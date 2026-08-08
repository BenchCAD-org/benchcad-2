"""Regression tests for the welded-mesh topology (C, G, V).

These pin the correction that retired the B-Rep element-count reconstruction of
genus. That formula was representation-dependent and produced impossible values
on real geometry; the values pinned here for the three corrected families are
the reason it was replaced, so they must not drift back.
"""

from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "framework"))

import cadquery as cq  # noqa: E402
import numpy as np  # noqa: E402

from bench2.structural import (  # noqa: E402
    TopologyUndefinedError,
    _mesh_shell_complex,
    _mesh_shell_topology,
    _ocp_hashcode_fix,
    brep_descriptor,
    canonicalize,
    compare_topology,
    solid_count,
    topology_difference,
    total_genus,
    void_count,
)

_ocp_hashcode_fix()


def _cgv(shape):
    d = brep_descriptor(shape)
    return solid_count(d), total_genus(d), void_count(d)


def _box(size=20.0):
    return cq.Workplane("XY").box(size, size, size).val()


def _with_holes(n):
    xs = {1: [(0, 0)], 2: [(-6, 0), (6, 0)], 3: [(-7, 0), (0, 0), (7, 0)]}[n]
    r = {1: 3.0, 2: 2.5, 3: 2.0}[n]
    return (cq.Workplane("XY").box(20, 20, 20).faces(">Z").workplane()
            .pushPoints(xs).circle(r).cutThruAll().val())


def _with_cavities(n):
    solid = _box()
    if n == 1:
        return solid.cut(cq.Workplane("XY").sphere(4).val())
    return (solid.cut(cq.Workplane("XY").sphere(2.5).translate((6, 0, 0)).val())
                 .cut(cq.Workplane("XY").sphere(2.5).translate((-6, 0, 0)).val()))


class MeshGenusControlTest(unittest.TestCase):
    """Known topology, computed through the mesh."""

    def test_primitives(self):
        for name, shape, genus in (
            ("block", _box(10), 0),
            ("cylinder", cq.Solid.makeCylinder(5, 10), 0),
            ("sphere", cq.Solid.makeSphere(5), 0),
            ("torus", cq.Solid.makeTorus(10, 3), 1),
        ):
            with self.subTest(name):
                self.assertEqual(total_genus(brep_descriptor(shape)), genus)

    def test_through_holes_raise_genus_one_per_hole(self):
        for n in (1, 2, 3):
            with self.subTest(holes=n):
                self.assertEqual(_cgv(_with_holes(n)), (1, n, 0))

    def test_blind_hole_is_not_topology(self):
        blind = (cq.Workplane("XY").box(20, 20, 20).faces(">Z").workplane()
                 .circle(3).cutBlind(-10).val())
        self.assertEqual(_cgv(blind), (1, 0, 0))
        self.assertEqual(_cgv(_box()), (1, 0, 0))

    def test_enclosed_cavities_raise_V_one_per_cavity(self):
        for n in (1, 2):
            with self.subTest(cavities=n):
                self.assertEqual(_cgv(_with_cavities(n)), (1, 0, n))

    def test_through_hole_plus_cavity_moves_G_and_V(self):
        shape = _with_holes(1).cut(
            cq.Workplane("XY").sphere(2.5).translate((6, 6, 0)).val())
        self.assertEqual(_cgv(shape), (1, 1, 1))

    def test_two_disconnected_solids_move_C_only(self):
        two = cq.Compound.makeCompound([
            cq.Workplane("XY").box(8, 8, 8).val(),
            cq.Workplane("XY").box(8, 8, 8).translate((30, 0, 0)).val(),
        ])
        self.assertEqual(_cgv(two), (2, 0, 0))

    def test_cavity_with_inner_body_moves_C_and_V(self):
        shape = (_box().cut(cq.Workplane("XY").sphere(6).val())
                 .fuse(cq.Workplane("XY").sphere(3).val()))
        self.assertEqual(_cgv(shape), (2, 0, 1))

    def test_fillet_and_chamfer_do_not_change_topology(self):
        for name, shape in (
            ("fillet", cq.Workplane("XY").box(10, 10, 10).edges().fillet(1).val()),
            ("chamfer", cq.Workplane("XY").box(10, 10, 10).edges().chamfer(1).val()),
        ):
            with self.subTest(name):
                self.assertEqual(_cgv(shape), (1, 0, 0))


class ValidityGuardTest(unittest.TestCase):
    """N/A, never a manufactured genus."""

    @staticmethod
    def _open_shell():
        from OCP.BRep import BRep_Builder
        from OCP.TopoDS import TopoDS_Shell

        builder = BRep_Builder()
        shell = TopoDS_Shell()
        builder.MakeShell(shell)
        for face in _box(10).Faces()[:5]:      # five of six faces: not closed
            builder.Add(shell, face.wrapped)
        return shell

    def test_open_shell_is_na_not_a_number(self):
        shell = self._open_shell()
        _, _, _, _, watertight, _ = _mesh_shell_complex(shell)
        self.assertFalse(watertight)
        with self.assertRaises(TopologyUndefinedError) as ctx:
            _mesh_shell_topology(shell)
        self.assertIn("watertight", str(ctx.exception))

    def test_closed_shell_produces_a_value(self):
        shell = canonicalize(_box(10)).Shells()[0]
        chi, genus = _mesh_shell_topology(shell.wrapped)
        self.assertEqual((chi, genus), (2, 0))

    def test_guard_never_clamps_to_a_plausible_number(self):
        """A failure must surface, not become 0."""
        with self.assertRaises(TopologyUndefinedError):
            _mesh_shell_topology(self._open_shell())


class TessellationStabilityTest(unittest.TestCase):
    """Triangle counts may move; the invariant may not."""

    def test_genus_invariant_across_deflection(self):
        import bench2.structural as st

        shapes = (("torus", cq.Solid.makeTorus(10, 3), 1),
                  ("2 holes", _with_holes(2), 2),
                  ("cavity", _with_cavities(1), 0))
        original = st._MESH_DEFLECTION
        try:
            for name, shape, expected in shapes:
                counts = set()
                for deflection in (0.5, 0.2, 0.1, 0.05, 0.02):
                    st._MESH_DEFLECTION = deflection
                    with self.subTest(name=name, deflection=deflection):
                        self.assertEqual(
                            total_genus(brep_descriptor(shape)), expected)
                    counts.add(sum(_mesh_shell_complex(s.wrapped)[2]
                                   for s in canonicalize(shape).Shells()))
                # the mesh really did change; the invariant did not.
                # (summed over every shell: a planar shell alone never moves)
                self.assertGreater(len(counts), 1, f"{name} mesh never changed")
        finally:
            st._MESH_DEFLECTION = original

    def test_genus_invariant_across_weld_tolerance(self):
        import bench2.structural as st

        original = st._WELD_RELATIVE
        try:
            for weld in (1e-2, 1e-3, 1e-4, 1e-5, 1e-6):
                st._WELD_RELATIVE = weld
                with self.subTest(weld=weld):
                    self.assertEqual(
                        total_genus(brep_descriptor(_with_holes(2))), 2)
        finally:
            st._WELD_RELATIVE = original


class RealFamilyTopologyTest(unittest.TestCase):
    """The corrections that motivated retiring the counting formula."""

    # family -> expected G. The three marked were wrong before the mesh route:
    # cable gland -2, T-handle pin -1, chuck 72 (silently wrong, looked fine).
    EXPECTED = {
        "clevis_fork_head": 3,
        "metric_plastic_cable_gland": 1,          # was -2
        "set_screw_shaft_collar": 2,
        "single_row_deep_groove_ball_bearing": 4,
        "slotted_din_rail": 4,
        "speaker_pole_mount_socket": 4,
        "t_handle_ball_lock_pin": 0,              # was -1
        "three_jaw_scroll_chuck": 21,             # was 72
    }

    @staticmethod
    def _build(name):
        from pathlib import Path

        from bench2.loader import load_family
        from bench2.sampling import sample

        directory = Path("designs") / name
        if not directory.exists():
            return None
        part, spec = load_family(directory)
        params = sample(spec, "easy", np.random.default_rng(0))
        accepted = set(inspect.signature(part.build).parameters)
        built = part.build(**{k: v for k, v in params.items() if k in accepted})
        if hasattr(built, "toCompound"):
            built = built.toCompound()
        if hasattr(built, "val"):
            built = built.val()
        return built if hasattr(built, "Faces") else cq.Shape(built.wrapped)

    def test_real_family_genus(self):
        for name, expected in self.EXPECTED.items():
            shape = self._build(name)
            if shape is None:
                self.skipTest(f"{name} not present")
            with self.subTest(name):
                self.assertEqual(total_genus(brep_descriptor(shape)), expected)

    def test_assemblies_score_topology_and_report_no_false_voids(self):
        for name in ("three_jaw_scroll_chuck",
                     "single_row_deep_groove_ball_bearing",
                     "t_handle_ball_lock_pin"):
            shape = self._build(name)
            if shape is None:
                self.skipTest(f"{name} not present")
            with self.subTest(name):
                d = brep_descriptor(shape)
                self.assertGreater(solid_count(d), 1)
                self.assertEqual(void_count(d), 0)   # shells - 1 claimed 8/10/4
                self.assertGreaterEqual(total_genus(d), 0)


class DifferenceTest(unittest.TestCase):
    def test_identical_topology_scores_one(self):
        a = brep_descriptor(_box())
        self.assertEqual(topology_difference(a, a), 0)
        self.assertEqual(compare_topology(a, a).topology_similarity, 1.0)

    def test_each_quantity_is_caught_by_exactly_its_own_defect(self):
        plain = brep_descriptor(_box())
        for shape, expected in ((_with_holes(1), 1),      # G
                                (_with_cavities(1), 1),   # V
                                ):
            with self.subTest():
                self.assertEqual(
                    topology_difference(plain, brep_descriptor(shape)), expected)

    def test_combined_defects_accumulate(self):
        plain = brep_descriptor(_box())
        both = brep_descriptor(_with_holes(1).cut(
            cq.Workplane("XY").sphere(2.5).translate((6, 6, 0)).val()))
        self.assertEqual(topology_difference(plain, both), 2)
        self.assertAlmostEqual(
            compare_topology(plain, both).topology_similarity, 1 / 3, places=9)

    def test_information_addition_is_one_way(self):
        """D_G <= D_GV <= D_CGV, structurally, on every controlled pair."""
        pairs = [(_box(), _with_holes(1)), (_box(), _with_cavities(1)),
                 (_box(), cq.Compound.makeCompound([
                     cq.Workplane("XY").box(8, 8, 8).val(),
                     cq.Workplane("XY").box(8, 8, 8).translate((30, 0, 0)).val()]))]
        for reference, candidate in pairs:
            a, b = brep_descriptor(reference), brep_descriptor(candidate)
            d_g = abs(total_genus(a) - total_genus(b))
            d_gv = d_g + abs(void_count(a) - void_count(b))
            d_cgv = d_gv + abs(solid_count(a) - solid_count(b))
            with self.subTest():
                self.assertLessEqual(d_g, d_gv)
                self.assertLessEqual(d_gv, d_cgv)
                self.assertEqual(d_cgv, topology_difference(a, b))


if __name__ == "__main__":
    unittest.main()
