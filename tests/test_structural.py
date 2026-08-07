"""Tests for the experimental B-Rep structural inspection tool (issue #196).

Covers the v1 regression cases (identical geometry, an extra through-hole, a
missing fillet, a groove-depth change, a harmless split, enumeration-order
invariance) plus the v2 properties: canonicalization, uniform-scale invariance,
zero-padding, the p_edge/p_face sensitivity split, and topology staying visible
independently of high spectral similarity.
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "framework"))

import cadquery as cq  # noqa: E402

from bench2.structural import (  # noqa: E402
    EDGE_TYPE_ORDER,
    _area,
    _length,
    NotSingleSolidError,
    _ocp_hashcode_fix,
    brep_descriptor,
    canonicalize,
    compare,
    shell_genera,
    spectrum_similarity,
    typed_spectrum_similarity,
    summed_chi,
    topology_similarity,
    total_genus,
    void_count,
)
from _topo_fixtures import hole_and_void, plain, with_holes, with_voids  # noqa: E402

# cadquery's own selectors dedup through Shape.hashCode(), so the shim has to
# be in place before any fixture runs — not merely before the first descriptor.
_ocp_hashcode_fix()


def _block(size=20.0):
    return cq.Workplane("XY").box(size, size, size).val()


def _block_with_hole(size=20.0, d=4.0):
    return cq.Workplane("XY").box(size, size, size).faces(">Z").workplane().hole(d).val()


def _block_filleted(size=20.0, r=1.5):
    return cq.Workplane("XY").box(size, size, size).edges("|Z").fillet(r).val()


def _block_with_groove(size=20.0, depth=1.0):
    return (
        cq.Workplane("XY").box(size, size, size)
        .faces(">Z").workplane().rect(size, 3.0).cutBlind(-depth).val()
    )


def _block_split(size=20.0):
    """Same solid as _block, faces split along a seam.

    A plain ``union`` fuses the coincident faces back into one (measured: 6
    faces, no split at all), so the halves are glued: identical geometry, 10
    faces instead of 6.
    """
    a = cq.Workplane("XY").box(size / 2.0, size, size).translate((-size / 4.0, 0, 0))
    b = cq.Workplane("XY").box(size / 2.0, size, size).translate((size / 4.0, 0, 0))
    return a.val().fuse(b.val(), glue=True)


class TestCanonicalization(unittest.TestCase):
    def test_split_reduces_to_the_unsplit_shape(self):
        split = brep_descriptor(_block_split(), canonical=False)
        self.assertEqual((split.faces, split.edges), (10, 20))
        canon = brep_descriptor(_block_split())
        plain = brep_descriptor(_block())
        self.assertEqual((canon.faces, canon.edges), (plain.faces, plain.edges))

    def test_real_features_survive_canonicalization(self):
        for shape, faces in ((_block_with_hole(), 7), (_block_filleted(), 10),
                             (_block_with_groove(), 10)):
            self.assertEqual(brep_descriptor(shape).faces, faces)

    def test_canonicalize_preserves_topology(self):
        for shape in (_block(), _block_with_hole(), _block_filleted(), _block_split()):
            before = brep_descriptor(shape, canonical=False).euler
            after = brep_descriptor(shape).euler
            self.assertEqual(before, after)


class TestDescriptor(unittest.TestCase):
    def test_box_descriptor_is_the_textbook_one(self):
        d = brep_descriptor(_block())
        self.assertEqual((d.solids, d.shells), (1, 1))
        self.assertEqual((d.faces, d.edges, d.vertices), (6, 12, 8))
        self.assertEqual(d.euler, (2,))
        self.assertAlmostEqual(sum(d.face_spectrum), 1.0, places=9)
        self.assertAlmostEqual(sum(d.edge_spectrum), 1.0, places=9)

    def test_enumeration_order_invariance(self):
        one = brep_descriptor(_block())
        other = brep_descriptor(cq.Workplane("XZ").box(20.0, 20.0, 20.0).val())
        self.assertEqual(one.face_spectrum, other.face_spectrum)
        self.assertEqual(one.edge_spectrum, other.edge_spectrum)
        self.assertEqual(one.euler, other.euler)

    def test_uniform_scale_invariance(self):
        """Normalizing by each shape's own total removes scale."""
        small, large = brep_descriptor(_block(10.0)), brep_descriptor(_block(250.0))
        for x, y in zip(small.face_spectrum, large.face_spectrum):
            self.assertAlmostEqual(x, y, places=9)
        for x, y in zip(small.edge_spectrum, large.edge_spectrum):
            self.assertAlmostEqual(x, y, places=9)
        c = compare(_block(10.0), _block(250.0))
        self.assertAlmostEqual(c.s_edge, 1.0, places=9)
        self.assertAlmostEqual(c.s_face, 1.0, places=9)
        self.assertAlmostEqual(c.structural, 1.0, places=9)

    def test_euler_sees_genus_where_the_naive_form_cannot(self):
        plain = _block().Shells()[0]
        holed = _block_with_hole().Shells()[0]

        def naive(sh):
            return len(sh.Vertices()) - len(sh.Edges()) + len(sh.Faces())

        self.assertEqual(naive(plain), naive(holed))
        self.assertEqual(brep_descriptor(_block()).euler, (2,))
        self.assertEqual(brep_descriptor(_block_with_hole()).euler, (0,))

    def test_descriptor_is_deterministic(self):
        self.assertEqual(brep_descriptor(_block()), brep_descriptor(_block()))


class TestIdenticalAndSplit(unittest.TestCase):
    def test_identical_shapes_score_identically(self):
        c = compare(_block(), _block())
        self.assertTrue(c.topology_match)
        for v in (c.s_topology, c.s_edge, c.s_face, c.structural):
            self.assertAlmostEqual(v, 1.0, places=9)

    def test_harmless_split_is_exactly_invariant_after_canonicalization(self):
        c = compare(_block(), _block_split())
        self.assertTrue(c.topology_match)
        self.assertAlmostEqual(c.s_edge, 1.0, places=9)
        self.assertAlmostEqual(c.s_face, 1.0, places=9)
        self.assertAlmostEqual(c.structural, 1.0, places=9)
        # the raw descriptors still record that it was split
        self.assertEqual(c.raw_b.faces, 10)
        self.assertEqual(c.canonical_b.faces, 6)


class TestTopology(unittest.TestCase):
    def test_topology_error_visible_despite_high_spectral_similarity(self):
        c = compare(_block(), _block_with_hole())
        # the spectra barely notice — and, more to the point, both of them
        # rate this far more similar than the topology term does
        self.assertGreater(c.s_edge, 0.80)
        self.assertGreater(c.s_face, 0.80)
        self.assertFalse(c.topology_match)     # topology does notice
        # D = 1 (one handle), so S_topology = 1/2 — far below either spectrum
        self.assertAlmostEqual(c.s_topology, 0.5, places=9)
        self.assertGreater(c.s_edge, c.s_topology)
        self.assertGreater(c.s_face, c.s_topology)

    def test_local_features_do_not_move_topology(self):
        for shape in (_block_with_groove(), _block_filleted(), _block_split()):
            c = compare(_block(), shape)
            self.assertTrue(c.topology_match)
            self.assertEqual(c.topology.topology_difference, 0)

    def test_topology_quantities_are_exposed(self):
        c = compare(_block(), _block_with_hole())
        t = c.topology
        self.assertEqual((t.total_genus_reference, t.total_genus_candidate), (0, 1))
        self.assertEqual((t.void_count_reference, t.void_count_candidate), (0, 0))
        self.assertEqual(t.abs_genus_difference, 1)
        self.assertEqual(t.abs_void_difference, 0)
        self.assertEqual(t.topology_difference, 1)
        self.assertFalse(t.topology_exact_match)
        self.assertAlmostEqual(c.s_topology, 0.5, places=9)

    def test_topology_similarity_is_total_and_symmetric(self):
        self.assertAlmostEqual(topology_similarity(0), 1.0, places=9)
        self.assertAlmostEqual(topology_similarity(1), 0.5, places=9)
        self.assertAlmostEqual(topology_similarity(2), 1.0 / 3.0, places=9)


class TestTopologyDecomposition(unittest.TestCase):
    def test_plain_vs_plain(self):
        c = compare(plain(), plain())
        self.assertEqual(c.topology.topology_difference, 0)
        self.assertAlmostEqual(c.s_topology, 1.0, places=9)

    def test_one_through_hole(self):
        d = brep_descriptor(with_holes(1))
        self.assertEqual((total_genus(d), void_count(d)), (1, 0))
        self.assertEqual(compare(plain(), with_holes(1)).topology.topology_difference, 1)

    def test_multiple_through_holes(self):
        for n in (2, 3, 5):
            d = brep_descriptor(with_holes(n))
            self.assertEqual(total_genus(d), n)
            self.assertEqual(void_count(d), 0)
        self.assertEqual(compare(with_holes(5), with_holes(4)).topology.topology_difference, 1)

    def test_one_internal_void(self):
        d = brep_descriptor(with_voids(1))
        self.assertEqual((total_genus(d), void_count(d)), (0, 1))
        self.assertEqual(d.shells, 2)
        self.assertEqual(compare(plain(), with_voids(1)).topology.topology_difference, 1)

    def test_multiple_internal_voids(self):
        d = brep_descriptor(with_voids(2))
        self.assertEqual((total_genus(d), void_count(d)), (0, 2))
        self.assertEqual(compare(plain(), with_voids(2)).topology.topology_difference, 2)

    def test_hole_plus_void_is_no_longer_cancelled(self):
        """The regression this change exists for."""
        d = brep_descriptor(hole_and_void())
        # summed chi still cancels — that is why it is diagnostic only
        self.assertEqual(summed_chi(d), summed_chi(brep_descriptor(plain())))
        # the decomposition does not
        self.assertEqual((total_genus(d), void_count(d)), (1, 1))
        c = compare(plain(), hole_and_void())
        self.assertEqual(c.topology.topology_difference, 2)
        self.assertFalse(c.topology_match)
        self.assertAlmostEqual(c.s_topology, 1.0 / 3.0, places=9)

    def test_handle_and_void_mismatch_weigh_the_same(self):
        """Deliberate: no separate handle/void weights."""
        handle = compare(plain(), with_holes(1))
        void = compare(plain(), with_voids(1))
        self.assertEqual(handle.topology.topology_difference,
                         void.topology.topology_difference)
        self.assertAlmostEqual(handle.s_topology, void.s_topology, places=12)

    def test_shell_genera_are_per_shell(self):
        self.assertEqual(shell_genera(brep_descriptor(plain())), (0,))
        self.assertEqual(shell_genera(brep_descriptor(with_holes(3))), (3,))
        self.assertEqual(shell_genera(brep_descriptor(with_voids(1))), (0, 0))
        self.assertEqual(shell_genera(brep_descriptor(hole_and_void())), (0, 1))


class TestSingleSolidScope(unittest.TestCase):
    def _two_solids(self):
        a = cq.Workplane("XY").box(10, 10, 10).translate((-30, 0, 0)).val()
        b = cq.Workplane("XY").box(10, 10, 10).translate((30, 0, 0)).val()
        return cq.Compound.makeCompound([a, b])

    def test_multi_solid_input_is_reported_not_guessed(self):
        two = self._two_solids()
        self.assertEqual(brep_descriptor(two).solids, 2)
        with self.assertRaises(NotSingleSolidError) as ctx:
            total_genus(brep_descriptor(two))
        self.assertIn("2 solids", str(ctx.exception))
        with self.assertRaises(NotSingleSolidError):
            compare(_block(), two)

    def test_spectra_remain_available_out_of_scope(self):
        d = brep_descriptor(self._two_solids())
        self.assertAlmostEqual(sum(d.face_spectrum), 1.0, places=9)
        self.assertAlmostEqual(sum(d.edge_spectrum), 1.0, places=9)

    def test_void_carrying_solid_is_still_in_scope(self):
        d = brep_descriptor(with_voids(1))
        self.assertEqual(d.solids, 1)
        self.assertEqual(void_count(d), 1)      # in scope, not rejected


class TestSpectrumPrimitives(unittest.TestCase):
    def test_zero_padding_when_lengths_differ(self):
        # one face carrying everything vs two carrying half each
        s = spectrum_similarity((1.0,), (0.5, 0.5), p=1.0)
        self.assertAlmostEqual(s, 1.0 - 1.0 / 2.0, places=9)  # d_1 = 1.0, / 2**1
        self.assertGreaterEqual(s, 0.0)
        self.assertLessEqual(s, 1.0)

    def test_bounds_and_degenerate_inputs(self):
        self.assertEqual(spectrum_similarity((), ()), 1.0)
        self.assertEqual(spectrum_similarity((1.0,), ()), 0.0)
        self.assertAlmostEqual(spectrum_similarity((1.0,), (1.0,)), 1.0, places=9)
        # disjoint point masses are the worst case at every p
        for p in (1.0, 1.5, 2.0):
            self.assertAlmostEqual(spectrum_similarity((1.0, 0.0), (0.0, 1.0), p=p),
                                   0.0, places=9)

    def test_p_out_of_range_rejected(self):
        for p in (0.5, 2.5):
            with self.assertRaises(ValueError):
                spectrum_similarity((1.0,), (1.0,), p=p)

    def test_p_shifts_sensitivity_between_concentrated_and_distributed(self):
        """Raising p should favour distributed error over concentrated error."""
        base = tuple([0.25] * 4)
        concentrated = (0.35, 0.25, 0.25, 0.15)          # 0.10 moved once
        distributed = (0.30, 0.30, 0.20, 0.20)           # 0.05 moved twice
        l1_conc = sum(abs(a - b) for a, b in zip(base, concentrated))
        l1_dist = sum(abs(a - b) for a, b in zip(base, distributed))
        self.assertAlmostEqual(l1_conc, l1_dist, places=9)  # equal at p=1
        self.assertAlmostEqual(spectrum_similarity(base, concentrated, p=1.0),
                               spectrum_similarity(base, distributed, p=1.0), places=9)
        # at p=2 the concentrated error is penalized more
        self.assertLess(spectrum_similarity(base, concentrated, p=2.0),
                        spectrum_similarity(base, distributed, p=2.0))


class TestParameterisation(unittest.TestCase):
    def test_weights_are_normalized(self):
        c = compare(_block(), _block_with_hole(),
                    weights={"topology": 2.0, "edge": 1.0, "face": 1.0})
        self.assertAlmostEqual(sum(c.weights.values()), 1.0, places=9)
        self.assertAlmostEqual(c.weights["topology"], 0.5, places=9)

    def test_bad_weights_rejected(self):
        for bad in ({"topology": 1.0}, {"topology": -1.0, "edge": 1.0, "face": 1.0},
                    {"topology": 0.0, "edge": 0.0, "face": 0.0}):
            with self.assertRaises(ValueError):
                compare(_block(), _block(), weights=bad)

    def test_rescore_matches_a_fresh_compare(self):
        """A sweep must not need to recompute descriptors."""
        a, b = _block(), _block_with_hole()
        base = compare(a, b)
        for pe, pf, w in ((2.0, 1.0, {"topology": 1.0, "edge": 1.0, "face": 1.0}),
                          (1.0, 2.0, {"topology": 3.0, "edge": 1.0, "face": 1.0}),
                          (1.5, 1.5, None)):
            again = compare(a, b, p_edge=pe, p_face=pf, weights=w)
            cheap = base.rescore(p_edge=pe, p_face=pf, weights=w)
            self.assertAlmostEqual(cheap.s_edge, again.s_edge, places=12)
            self.assertAlmostEqual(cheap.s_face, again.s_face, places=12)
            self.assertAlmostEqual(cheap.structural, again.structural, places=12)

    def test_export_round_trips_as_json(self):
        import json

        d = compare(_block(), _block_with_hole()).as_dict()
        json.dumps(d)  # must not raise
        for key in ("raw", "canonical", "shell_count_reference",
                    "void_count_reference", "per_shell_chi_reference",
                    "per_shell_genus_reference", "total_genus_reference",
                    "total_genus_candidate", "abs_genus_difference",
                    "abs_void_difference", "topology_difference",
                    "topology_exact_match", "topology_similarity",
                    "summed_chi_reference", "s_topology",
                    "s_edge", "s_face", "p_edge", "p_face", "weights", "structural"):
            self.assertIn(key, d)


class TestTypeAwareSpectra(unittest.TestCase):
    """The fillet/chamfer blind spot the typed descriptor exists to close."""

    SEL = "|Y and >Z and >X"

    def _cube(self):
        return cq.Workplane("XY").box(10, 10, 10)

    def _fillet(self):
        return self._cube().edges(self.SEL).fillet(1.0).val()

    def _chamfer(self, d=1.0):
        return self._cube().edges(self.SEL).chamfer(d).val()

    def _matched_chamfer(self):
        # face area 10*d*sqrt(2) equal to the fillet's 10*pi/2, so the untyped
        # descriptor sees identical entries: same new-face area, same end-edge
        # length. Only the type differs.
        return self._chamfer(d=(math.pi / 2) / math.sqrt(2))

    def test_the_types_are_what_distinguishes_them(self):
        f = brep_descriptor(self._fillet())
        c = brep_descriptor(self._chamfer())
        self.assertIn("Circle", dict(f.edge_by_type))
        self.assertIn("Cylinder", dict(f.face_by_type))
        self.assertNotIn("Circle", dict(c.edge_by_type))     # chamfer is all lines
        self.assertNotIn("Cylinder", dict(c.face_by_type))   # and all planes

    def test_fillet_vs_chamfer_is_detected(self):
        c = compare(self._fillet(), self._chamfer())
        self.assertTrue(c.topology_match)          # topologically identical
        self.assertLess(c.s_edge, 0.98)
        self.assertLess(c.s_face, 0.98)

    def test_matched_size_chamfer_is_still_detected(self):
        """Untyped, these are literally identical entries; typed, they are not."""
        fillet, chamfer = self._fillet(), self._matched_chamfer()
        # the RAW blend measures are equal by construction - 15.7080 of area and
        # 1.5708 of end edge on both - so the untyped descriptor has nothing to
        # separate them by except second-order neighbour trimming. (The
        # normalized shares differ very slightly because the two shapes end up
        # with different totals; that is the second-order term.)
        fc = canonicalize(fillet)
        cc = canonicalize(chamfer)
        self.assertAlmostEqual(min(_area(f) for f in fc.Faces()),
                               min(_area(f) for f in cc.Faces()), places=6)
        self.assertAlmostEqual(min(_length(e) for e in fc.Edges()),
                               min(_length(e) for e in cc.Edges()), places=6)
        c = compare(fillet, chamfer)
        self.assertLess(c.s_edge, 0.98)
        self.assertLess(c.s_face, 0.98)

    def test_deficit_is_dominated_by_the_transferred_mass_at_p1(self):
        """At p = 1 the deficit is the mass that changed type, plus a little.

        Not an exact identity: the two operations also trim their neighbouring
        faces differently (99.7854 vs 99.5), so a second-order term rides along.
        Measured, the transferred mass accounts for well over 99% of it.
        """
        fd = brep_descriptor(self._fillet())
        circle_mass = sum(dict(fd.edge_by_type)["Circle"])
        cylinder_mass = sum(dict(fd.face_by_type)["Cylinder"])
        c = compare(self._fillet(), self._chamfer(), p_edge=1.0, p_face=1.0)
        for deficit, transferred in ((1.0 - c.s_edge, circle_mass),
                                     (1.0 - c.s_face, cylinder_mass)):
            self.assertGreaterEqual(deficit, transferred * 0.99)
            self.assertLessEqual(deficit, transferred * 1.05)

    def test_typed_similarity_keeps_the_invariances(self):
        for a, b in ((_block(), _block()), (_block(), _block_split()),
                     (_block(10.0), _block(250.0))):
            c = compare(a, b)
            self.assertAlmostEqual(c.s_edge, 1.0, places=9)
            self.assertAlmostEqual(c.s_face, 1.0, places=9)

    def test_p_range_still_enforced(self):
        f = brep_descriptor(self._fillet())
        for p in (0.5, 2.5):
            with self.assertRaises(ValueError):
                typed_spectrum_similarity(f.edge_by_type, f.edge_by_type,
                                          EDGE_TYPE_ORDER, p=p)

    def test_type_buckets_are_exported(self):
        d = compare(self._fillet(), self._chamfer()).as_dict()
        self.assertIn("edge_by_type", d["canonical"]["a"])
        self.assertIn("face_by_type", d["canonical"]["a"])
        self.assertIn("Cylinder", d["canonical"]["a"]["face_by_type"])


class TestLocalFeatureChanges(unittest.TestCase):
    def test_missing_fillet_is_visible(self):
        c = compare(_block_filleted(), _block())
        self.assertTrue(c.topology_match)      # fillets are not a topology change
        self.assertLess(c.s_face, 1.0)
        self.assertLess(c.structural, 1.0)

    def test_groove_depth_change_is_a_partial_loss(self):
        c = compare(_block_with_groove(depth=0.5), _block_with_groove(depth=3.0))
        self.assertTrue(c.topology_match)
        self.assertLess(c.s_face, 0.999)
        self.assertGreater(c.s_face, 0.5)


if __name__ == "__main__":
    unittest.main()
