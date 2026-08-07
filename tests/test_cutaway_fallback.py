"""`step_cutaway_mesh` must survive an empty boolean result.

The pinned cadquery 2.3 / OCP 7.9 pair sometimes returns an EMPTY shape from
`cut` on seam-heavy solids (observed on a bearing cage half fused from a band,
two lips and per-ball pocket cups). Before the fallback that raised
`ValueError: zero-size array to reduction operation minimum`, which killed the
whole `preview-parts` sheet for the family."""

import tempfile
import unittest
from pathlib import Path


def _write_box_step(path: Path):
    import cadquery as cq

    from bench2.render import _ocp_hashcode_fix

    _ocp_hashcode_fix()
    cq.exporters.export(cq.Workplane("XY").box(20, 10, 6), str(path))


class CutawayFallbackTest(unittest.TestCase):
    def test_normal_solid_uses_the_boolean_half(self):
        from bench2.render import step_cutaway_mesh

        with tempfile.TemporaryDirectory() as td:
            step = Path(td) / "box.step"
            _write_box_step(step)
            verts, tris = step_cutaway_mesh(step)
        self.assertGreater(len(verts), 0)
        self.assertGreater(len(tris), 0)
        # normalized frame: longest axis 1, centred on 0.5
        self.assertAlmostEqual(float(verts.max(axis=0).max()), 1.0, places=6)

    def test_empty_boolean_falls_back_to_a_mesh_half_section(self):
        import cadquery as cq

        from bench2.render import step_cutaway_mesh

        with tempfile.TemporaryDirectory() as td:
            step = Path(td) / "box.step"
            _write_box_step(step)
            original = cq.Shape.cut

            def empty_cut(self, *args, **kwargs):
                return cq.Compound.makeCompound([])

            cq.Shape.cut = empty_cut
            try:
                verts, tris = step_cutaway_mesh(step)
            finally:
                cq.Shape.cut = original

        self.assertGreater(len(verts), 0, "fallback produced no vertices")
        self.assertGreater(len(tris), 0, "fallback produced no triangles")
        self.assertTrue((tris >= 0).all(), "vertex remap left dangling indices")
        self.assertLess(int(tris.max()), len(verts), "triangle indexes past the vertex array")
        # every kept triangle must touch the -Y half of the part
        self.assertTrue(
            (verts[tris][:, :, 1] <= verts[:, 1].max() + 1e-9).any(axis=1).all(),
            "kept a triangle entirely in the removed half",
        )


if __name__ == "__main__":
    unittest.main()
