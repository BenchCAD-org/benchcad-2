"""Tests for the experimental B-Rep structural similarity (issue #196).

The cases are the ones the issue asks for: identical geometry, a topology
change (extra through-hole), a missing fillet, a groove-depth change, a
harmless B-Rep split, and enumeration-order invariance.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "framework"))

import cadquery as cq  # noqa: E402

from bench2.structural import (  # noqa: E402
    _ocp_hashcode_fix,
    brep_descriptor,
    count_similarity,
    spectrum_similarity,
    structural_similarity,
    topology_match,
)


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
        cq.Workplane("XY")
        .box(size, size, size)
        .faces(">Z")
        .workplane()
        .rect(size, 3.0)
        .cutBlind(-depth)
        .val()
    )


def _block_split(size=20.0):
    """Same solid as _block, but with its faces split along a seam.

    A plain ``union`` fuses the coincident faces back into one (measured: 6
    faces, i.e. no split at all), so the halves are glued instead: identical
    geometry, 10 faces instead of 6.
    """
    a = cq.Workplane("XY").box(size / 2.0, size, size).translate((-size / 4.0, 0, 0))
    b = cq.Workplane("XY").box(size / 2.0, size, size).translate((size / 4.0, 0, 0))
    return a.val().fuse(b.val(), glue=True)


class TestDescriptor(unittest.TestCase):
    def test_box_descriptor_is_the_textbook_one(self):
        d = brep_descriptor(_block())
        self.assertEqual((d.solids, d.shells), (1, 1))
        self.assertEqual((d.faces, d.edges, d.vertices), (6, 12, 8))
        self.assertEqual(d.euler, (2,))  # closed shell of genus 0
        self.assertAlmostEqual(sum(d.face_spectrum), 1.0, places=9)
        self.assertAlmostEqual(sum(d.edge_spectrum), 1.0, places=9)
        # a cube's six faces are equal sixths
        for v in d.face_spectrum:
            self.assertAlmostEqual(v, 1.0 / 6.0, places=9)

    def test_enumeration_order_invariance(self):
        """Same solid reached two ways gives a byte-identical descriptor."""
        one = brep_descriptor(_block())
        # rebuild via a different construction order; the B-Rep enumeration
        # order differs, the descriptor must not.
        other = brep_descriptor(
            cq.Workplane("XZ").box(20.0, 20.0, 20.0).val()
        )
        self.assertEqual(one.face_spectrum, other.face_spectrum)
        self.assertEqual(one.edge_spectrum, other.edge_spectrum)
        self.assertEqual(one.euler, other.euler)

    def test_euler_sees_genus_where_the_naive_form_cannot(self):
        """V - E + F is 2 for both shapes; the wire-corrected form is not."""
        plain = _block().Shells()[0]
        holed = _block_with_hole().Shells()[0]

        def naive(sh):
            return len(sh.Vertices()) - len(sh.Edges()) + len(sh.Faces())
        self.assertEqual(naive(plain), naive(holed))  # naive cannot tell them apart
        self.assertEqual(brep_descriptor(_block()).euler, (2,))
        self.assertEqual(brep_descriptor(_block_with_hole()).euler, (0,))

    def test_local_features_do_not_move_the_topology_term(self):
        for shape in (_block_with_groove(depth=1.0), _block_filleted(), _block_split()):
            self.assertEqual(brep_descriptor(shape).euler, (2,))

    def test_descriptor_is_deterministic(self):
        self.assertEqual(brep_descriptor(_block()), brep_descriptor(_block()))


class TestIdentical(unittest.TestCase):
    def test_identical_geometry_scores_one(self):
        s = structural_similarity(_block(), _block(), iou=1.0)
        self.assertTrue(s.topology_match)
        self.assertAlmostEqual(s.s_face, 1.0, places=9)
        self.assertAlmostEqual(s.s_edge, 1.0, places=9)
        self.assertAlmostEqual(s.s_count, 1.0, places=9)
        self.assertAlmostEqual(s.structural, 1.0, places=9)


class TestTopologyChange(unittest.TestCase):
    def test_through_hole_changes_euler_and_is_detected(self):
        plain, holed = _block(), _block_with_hole()
        self.assertFalse(topology_match(brep_descriptor(plain), brep_descriptor(holed)))
        # the added handle drops the Euler characteristic
        self.assertNotEqual(brep_descriptor(plain).euler, brep_descriptor(holed).euler)

    def test_soft_and_hard_treatments_differ(self):
        plain, holed = _block(), _block_with_hole()
        soft = structural_similarity(plain, holed, iou=0.97)
        hard = structural_similarity(plain, holed, iou=0.97, hard_gate=True)
        self.assertFalse(soft.topology_match)
        self.assertFalse(soft.hard_gated)
        self.assertGreater(soft.structural, 0.0)
        self.assertTrue(hard.hard_gated)
        self.assertEqual(hard.structural, 0.0)
        # components stay observable under the gate, for ablation
        self.assertEqual(soft.s_face, hard.s_face)

    def test_high_iou_still_loses_points_structurally(self):
        """The case the issue is about: IoU barely moves, structure does."""
        s = structural_similarity(_block(), _block_with_hole(), iou=0.99)
        self.assertLess(s.structural, 0.99)


class TestLocalFeatureChanges(unittest.TestCase):
    def test_missing_fillet_is_visible_in_the_components(self):
        sharp, filleted = _block(), _block_filleted()
        s = structural_similarity(sharp, filleted, iou=0.99)
        self.assertLess(s.s_count, 1.0)          # fillets add faces and edges
        self.assertLess(s.structural, 0.99)

    def test_groove_depth_change_is_visible(self):
        shallow = _block_with_groove(depth=0.5)
        deep = _block_with_groove(depth=3.0)
        same = structural_similarity(shallow, shallow, iou=1.0)
        diff = structural_similarity(shallow, deep, iou=0.98)
        self.assertAlmostEqual(same.s_face, 1.0, places=9)
        # a depth change is a size change, not a topology change: same shell,
        # same face and edge counts, only the spectra move.
        self.assertTrue(diff.topology_match)
        self.assertAlmostEqual(diff.s_count, 1.0, places=9)
        # and it must be a *partial* loss — asserting only "< same" would also
        # pass on a degenerate fixture that scores a flat zero.
        self.assertLess(diff.s_face, 0.999)
        self.assertGreater(diff.s_face, 0.5)


class TestHarmlessSplit(unittest.TestCase):
    def test_split_faces_are_only_lightly_penalized(self):
        whole, split = _block(), _block_split()
        d_whole, d_split = brep_descriptor(whole), brep_descriptor(split)
        self.assertGreater(d_split.faces, d_whole.faces)  # really is split
        s = structural_similarity(whole, split, iou=1.0)
        # the spectra are compared as cumulative curves, so a split costs
        # little; the count term is the one that notices, at weight 0.05
        self.assertGreater(s.s_face, 0.90)
        self.assertGreater(s.s_edge, 0.90)
        self.assertGreater(s.structural, 0.90)


class TestPrimitives(unittest.TestCase):
    def test_spectrum_similarity_bounds(self):
        self.assertEqual(spectrum_similarity((), ()), 1.0)
        self.assertEqual(spectrum_similarity((1.0,), ()), 0.0)
        self.assertAlmostEqual(spectrum_similarity((1.0,), (1.0,)), 1.0, places=9)
        s = spectrum_similarity((1.0,), (0.5, 0.5))
        self.assertGreaterEqual(s, 0.0)
        self.assertLessEqual(s, 1.0)

    def test_count_similarity_bounds(self):
        d = brep_descriptor(_block())
        self.assertAlmostEqual(count_similarity(d, d), 1.0, places=9)


if __name__ == "__main__":
    unittest.main()
