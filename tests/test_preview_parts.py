"""Framework tests for `bench2 preview-parts` (issue #95).

Fixture families are written to temp dirs and executed through the REAL
pipeline — derive_program -> subprocess -> per-leaf STEP + manifest -> VTK —
so the acceptance criteria are exercised end to end: nested Assembly
locations, translation + rotation, repeated instances, grouped vs
--per-instance rows, metadata mismatches, and byte-deterministic output in
the pinned environment. Pure contract/classification logic is unit-tested
without geometry."""

import json
import math
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

import numpy as np

ASSEMBLY_PART = '''
import cadquery as cq


def build(base_w, pin_d):
    base = cq.Workplane("XY").box(base_w, base_w, 4)
    pin = cq.Workplane("XY").cylinder(10, pin_d / 2)
    result = cq.Assembly(name="fixture")
    result.add(base, name="base")
    rack = cq.Assembly(name="rack", loc=cq.Location((0, 0, 7)))
    rack.add(pin, name="pin_01", loc=cq.Location((-base_w / 4, 0, 0)))
    rack.add(pin, name="pin_02", loc=cq.Location((base_w / 4, 0, 0), (0, 0, 1), 30))
    result.add(rack)
    return result
'''

ASSEMBLY_SPEC = '''
PARAM_SPEC = {
    "base_w": {"desc": "base plate width", "unit": "mm", "source": "proportion",
               "range": {"easy": (20, 30), "medium": (20, 40), "hard": (20, 50)}},
    "pin_d": {"desc": "pin diameter", "unit": "mm", "source": "proportion",
              "range": {"easy": (4, 6), "medium": (4, 8), "hard": (4, 10)}},
}


def check(p):
    return []
'''

SINGLE_PART = '''
import cadquery as cq


def build(base_w):
    result = cq.Workplane("XY").box(base_w, base_w, 4)
    return result
'''

SINGLE_SPEC = '''
PARAM_SPEC = {
    "base_w": {"desc": "base plate width", "unit": "mm", "source": "proportion",
               "range": {"easy": (20, 30), "medium": (20, 40), "hard": (20, 50)}},
}


def check(p):
    return []
'''


def _meta(**overrides):
    meta = {
        "family": "fixture",
        "standard": None,
        "base_plane": "XY",
        "description": "test fixture",
        "source": "proportion",
        "contributor": "framework-tests",
    }
    meta.update(overrides)
    return meta


def _write_family(fam_dir: Path, part: str, spec: str, meta: dict) -> Path:
    fam_dir.mkdir(parents=True, exist_ok=True)
    (fam_dir / "part.py").write_text(part)
    (fam_dir / "spec.py").write_text(spec)
    (fam_dir / "family.json").write_text(json.dumps(meta))
    return fam_dir

ASSEMBLY_META = _meta(
    solids=3,
    components=[{"name": "base", "quantity": 1}, {"name": "pin", "quantity": 2}],
)

# compose_grid geometry: W = label_w + 4*(cell+pad) + pad, H = rows*(cell+pad) + pad
CELL, PAD, LABEL_W = 320, 10, 300
GRID_W = LABEL_W + 4 * (CELL + PAD) + PAD


def _grid_height(rows: int) -> int:
    return rows * (CELL + PAD) + PAD


class ContractTests(unittest.TestCase):
    def test_contract_preserves_declaration_order(self):
        from bench2.preview_parts import component_contract

        meta = _meta(solids=3, components=[
            {"name": "pin", "quantity": 2}, {"name": "base", "quantity": 1}])
        self.assertEqual(component_contract(meta), [("pin", 2), ("base", 1)])

    def test_contract_requires_components(self):
        from bench2.preview_parts import component_contract

        with self.assertRaisesRegex(ValueError, "must declare `components`"):
            component_contract(_meta(solids=2))

    def test_contract_rejects_solids_drift(self):
        from bench2.preview_parts import component_contract

        meta = _meta(solids=2, components=[
            {"name": "base", "quantity": 1}, {"name": "pin", "quantity": 2}])
        with self.assertRaisesRegex(ValueError, "`solids` must be declared and equal"):
            component_contract(meta)
        with self.assertRaisesRegex(ValueError, "`solids` must be declared and equal"):
            component_contract(_meta(components=[{"name": "base", "quantity": 1}]))

    def test_contract_rejects_malformed_entries(self):
        from bench2.preview_parts import component_contract

        with self.assertRaisesRegex(ValueError, "non-empty string `name`"):
            component_contract(_meta(solids=1, components=[{"quantity": 1}]))
        with self.assertRaisesRegex(ValueError, "positive integer `quantity`"):
            component_contract(_meta(solids=1, components=[{"name": "base", "quantity": 0}]))
        with self.assertRaisesRegex(ValueError, "duplicate component name"):
            component_contract(_meta(solids=2, components=[
                {"name": "base", "quantity": 1}, {"name": "base", "quantity": 1}]))


class ClassificationTests(unittest.TestCase):
    def test_exact_name_beats_suffix_stripping(self):
        from bench2.preview_parts import classify_instance

        self.assertEqual(classify_instance("plate_2", ["plate", "plate_2"]), "plate_2")
        self.assertEqual(classify_instance("plate_2_01", ["plate", "plate_2"]), "plate_2")

    def test_numbered_instances_map_to_their_component(self):
        from bench2.preview_parts import classify_instance

        self.assertEqual(classify_instance("bolt_01", ["body", "bolt"]), "bolt")
        self.assertEqual(classify_instance("bolt_long_01", ["bolt", "bolt_long"]), "bolt_long")

    def test_non_numeric_suffix_is_a_distinct_component(self):
        from bench2.preview_parts import classify_instance

        with self.assertRaisesRegex(ValueError, "matches no family.json component"):
            classify_instance("bolt_left", ["bolt"])

    def test_uuid_style_unnamed_node_fails_clearly(self):
        from bench2.preview_parts import classify_instance

        with self.assertRaisesRegex(ValueError, "matches no family.json component"):
            classify_instance("3efa2ed8-8ccc-11f1-8aba-e1bee9f8c9c9", ["base", "pin"])

    def test_semantically_distinct_identical_geometry_stays_separate(self):
        from bench2.preview_parts import group_instances

        groups = group_instances(
            [{"name": "left_pin"}, {"name": "right_pin"}],
            [("left_pin", 1), ("right_pin", 1)])
        self.assertEqual(groups, {"left_pin": [0], "right_pin": [1]})

    def test_quantity_drift_is_rejected(self):
        from bench2.preview_parts import group_instances

        with self.assertRaisesRegex(ValueError, "pin: declared 2, built 1"):
            group_instances([{"name": "base"}, {"name": "pin_01"}],
                            [("base", 1), ("pin", 2)])

    def test_duplicate_instance_names_are_rejected(self):
        from bench2.preview_parts import group_instances

        with self.assertRaisesRegex(ValueError, "not unique"):
            group_instances([{"name": "pin_01"}, {"name": "pin_01"}], [("pin", 2)])


class ManifestTests(unittest.TestCase):
    """The derived program exports every leaf with its true world transform."""

    def test_nested_locations_translation_and_rotation(self):
        from bench2.derive import derive_program
        from bench2.execute import execute_cq_to_parts
        from bench2.loader import load_family
        from bench2.sampling import sample as sample_params

        with tempfile.TemporaryDirectory() as td:
            fam_dir = _write_family(Path(td) / "fam", ASSEMBLY_PART, ASSEMBLY_SPEC,
                                    ASSEMBLY_META)
            part, spec = load_family(fam_dir)
            p = sample_params(spec, "hard", np.random.default_rng(0))
            manifest = execute_cq_to_parts(derive_program(part, p), Path(td) / "out")

            self.assertTrue(manifest["is_assembly"])
            self.assertEqual([leaf["name"] for leaf in manifest["leaves"]],
                             ["base", "pin_01", "pin_02"])
            transforms = {leaf["name"]: np.array(leaf["world_transform"])
                          for leaf in manifest["leaves"]}
            w = p["base_w"]
            # pin_01: nested rack loc (0,0,7) * pin loc (-w/4,0,0), no rotation
            np.testing.assert_allclose(transforms["pin_01"][:, 3], [-w / 4, 0.0, 7.0],
                                       atol=1e-9)
            np.testing.assert_allclose(transforms["pin_01"][:, :3], np.eye(3), atol=1e-9)
            # pin_02: same nesting plus a 30 deg rotation about Z
            np.testing.assert_allclose(transforms["pin_02"][:, 3], [w / 4, 0.0, 7.0],
                                       atol=1e-9)
            self.assertAlmostEqual(transforms["pin_02"][0, 0], math.cos(math.radians(30)))
            self.assertAlmostEqual(transforms["pin_02"][1, 0], math.sin(math.radians(30)))

    def test_single_solid_result_reports_not_assembly(self):
        from bench2.derive import derive_program
        from bench2.execute import execute_cq_to_parts
        from bench2.loader import load_family
        from bench2.sampling import sample as sample_params

        with tempfile.TemporaryDirectory() as td:
            fam_dir = _write_family(Path(td) / "fam", SINGLE_PART, SINGLE_SPEC,
                                    _meta())
            part, spec = load_family(fam_dir)
            p = sample_params(spec, "hard", np.random.default_rng(0))
            manifest = execute_cq_to_parts(derive_program(part, p), Path(td) / "out")
            self.assertFalse(manifest["is_assembly"])
            self.assertEqual(manifest["leaves"], [])


class PreviewPartsEndToEndTests(unittest.TestCase):
    def test_grouped_default_is_deterministic_and_correctly_shaped(self):
        from PIL import Image

        from bench2.preview_parts import build_preview_parts

        with tempfile.TemporaryDirectory() as td:
            fam_dir = _write_family(Path(td) / "fam", ASSEMBLY_PART, ASSEMBLY_SPEC,
                                    ASSEMBLY_META)
            out = build_preview_parts(fam_dir)
            self.assertEqual(out, fam_dir / "preview_parts.png")
            first = out.read_bytes()
            # 2 component rows + 1 assembly overview + 2 grouped highlight rows
            self.assertEqual(Image.open(BytesIO(first)).size, (GRID_W, _grid_height(5)))
            # image bytes are deterministic in the pinned environment
            build_preview_parts(fam_dir)
            self.assertEqual(first, out.read_bytes())

    def test_per_instance_adds_one_row_per_repeated_instance(self):
        from PIL import Image

        from bench2.preview_parts import build_preview_parts

        with tempfile.TemporaryDirectory() as td:
            fam_dir = _write_family(Path(td) / "fam", ASSEMBLY_PART, ASSEMBLY_SPEC,
                                    ASSEMBLY_META)
            out = build_preview_parts(fam_dir, per_instance=True)
            # 2 component rows + 1 assembly overview + 3 per-instance highlight rows
            with Image.open(out) as image:
                self.assertEqual(image.size, (GRID_W, _grid_height(6)))

    def test_single_part_family_skips_or_fails_clearly(self):
        from bench2.preview_parts import build_preview_parts

        with tempfile.TemporaryDirectory() as td:
            fam_dir = _write_family(Path(td) / "fam", SINGLE_PART, SINGLE_SPEC,
                                    _meta())
            # `bench2 preview` auto-detect path: not an assembly -> no artifact
            self.assertIsNone(build_preview_parts(fam_dir, required=False))
            self.assertFalse((fam_dir / "preview_parts.png").exists())
            # explicit `bench2 preview-parts` on a single part -> clear failure
            with self.assertRaisesRegex(ValueError, "not a named cq.Assembly"):
                build_preview_parts(fam_dir)

    def test_metadata_mismatch_fails_before_rendering(self):
        from bench2.preview_parts import build_preview_parts

        with tempfile.TemporaryDirectory() as td:
            fam_dir = _write_family(
                Path(td) / "fam", ASSEMBLY_PART, ASSEMBLY_SPEC,
                _meta(solids=3, components=[{"name": "base", "quantity": 1},
                                            {"name": "peg", "quantity": 2}]))
            with self.assertRaisesRegex(ValueError, "matches no family.json component"):
                build_preview_parts(fam_dir)
            self.assertFalse((fam_dir / "preview_parts.png").exists())


class ValidateGateTests(unittest.TestCase):
    def test_validate_checks_components_metadata(self):
        from bench2.validate import validate_family

        with tempfile.TemporaryDirectory() as td:
            fam_dir = _write_family(Path(td) / "fam", ASSEMBLY_PART, ASSEMBLY_SPEC,
                                    ASSEMBLY_META)
            passed, log = validate_family(fam_dir, seeds=1, geometry=False)
            self.assertTrue(passed, msg=str(log))
            self.assertTrue(any("components: 2 component type(s)" in msg
                                for okay, msg in log if okay), msg=str(log))

    def test_validate_fails_on_components_solids_drift(self):
        from bench2.validate import validate_family

        with tempfile.TemporaryDirectory() as td:
            fam_dir = _write_family(
                Path(td) / "fam", ASSEMBLY_PART, ASSEMBLY_SPEC,
                _meta(solids=2, components=[{"name": "base", "quantity": 1},
                                            {"name": "pin", "quantity": 2}]))
            passed, log = validate_family(fam_dir, seeds=1, geometry=False)
            self.assertFalse(passed)
            self.assertTrue(any("`solids` must be declared and equal" in msg
                                for okay, msg in log if not okay), msg=str(log))


class DocsExampleTests(unittest.TestCase):
    """The committed docs example keeps working as the framework evolves."""

    def test_docs_example_stays_runnable(self):
        from PIL import Image

        from bench2.preview_parts import build_preview_parts

        demo = Path(__file__).resolve().parent.parent / "docs" / "examples" / "preview_parts_demo"
        with tempfile.TemporaryDirectory() as td:
            fam_dir = Path(td) / "demo"
            fam_dir.mkdir()
            for name in ("part.py", "spec.py", "family.json"):
                (fam_dir / name).write_text((demo / name).read_text())
            out = build_preview_parts(fam_dir)
            # 3 component rows + 1 assembly overview + 3 grouped highlight rows
            with Image.open(out) as image:
                self.assertEqual(image.size, (GRID_W, _grid_height(7)))


class RenderRegressionTests(unittest.TestCase):
    """The multi-actor refactor keeps single-part rendering deterministic."""

    @staticmethod
    def _tetra():
        verts = np.array([[0.2, 0.2, 0.2], [0.8, 0.25, 0.3],
                          [0.5, 0.8, 0.25], [0.45, 0.5, 0.8]], dtype=np.float64)
        tris = np.array([[0, 1, 2], [0, 1, 3], [1, 2, 3], [0, 2, 3]], dtype=np.int64)
        return verts, tris

    @staticmethod
    def _png_bytes(image):
        buf = BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()

    def test_render_iso_is_deterministic(self):
        from bench2 import render

        verts, tris = self._tetra()
        a = self._png_bytes(render.render_iso(verts, tris, img_size=120))
        b = self._png_bytes(render.render_iso(verts, tris, img_size=120))
        self.assertEqual(a, b)

    def test_highlight_styles_change_the_pixels(self):
        from bench2 import render

        verts, tris = self._tetra()
        shifted = verts + np.array([0.15, 0.0, 0.0])
        teal = self._png_bytes(render.render_actors(
            [(verts, tris, render.TEAL_STYLE), (shifted, tris, render.TEAL_STYLE)],
            img_size=120))
        highlighted = self._png_bytes(render.render_actors(
            [(verts, tris, render.HIGHLIGHT_STYLE), (shifted, tris, render.DIMMED_STYLE)],
            img_size=120))
        self.assertNotEqual(teal, highlighted)


if __name__ == "__main__":
    unittest.main()
