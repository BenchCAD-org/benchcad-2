import hashlib
import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

import cadquery as cq
import numpy as np

from bench2 import render
from bench2.assembly_preview import (
    _call_build,
    _component_contract,
    _highlight_groups,
    assembly_leaves,
)


class AssemblyPreviewTests(unittest.TestCase):
    def test_spec_only_parameters_do_not_need_to_be_build_arguments(self):
        class Part:
            @staticmethod
            def build(width):
                return width

        sampled = {"catalog_row": 4, "width": 12}
        self.assertEqual(_call_build(Part, sampled), 12)

    def test_nested_locations_and_repeated_component_grouping(self):
        root = cq.Assembly(name="root", loc=cq.Location((10, 0, 0)))
        nested = cq.Assembly(name="nested", loc=cq.Location((0, 20, 0)))
        nested.add(
            cq.Workplane("XY").box(2, 2, 2),
            name="bolt_01",
            loc=cq.Location((0, 0, 3)),
        )
        nested.add(
            cq.Workplane("XY").box(2, 4, 6),
            name="bolt_02",
            loc=cq.Location((0, 0, 6), (0, 0, 1), 90),
        )
        root.add(cq.Workplane("XY").box(4, 5, 6), name="body")
        root.add(nested)

        leaves = assembly_leaves(root, [("body", 1), ("bolt", 2)])

        self.assertEqual(
            [(leaf.instance_name, leaf.component_name) for leaf in leaves],
            [("body", "body"), ("bolt_01", "bolt"), ("bolt_02", "bolt")],
        )
        centers = {
            leaf.instance_name: leaf.world_shape.Center().toTuple()
            for leaf in leaves
        }
        self.assertAlmostEqual(centers["body"][0], 10.0)
        self.assertAlmostEqual(centers["bolt_01"][1], 20.0)
        self.assertAlmostEqual(centers["bolt_01"][2], 3.0)
        self.assertAlmostEqual(centers["bolt_02"][2], 6.0)
        rotated_box = next(
            leaf.world_shape.BoundingBox()
            for leaf in leaves
            if leaf.instance_name == "bolt_02"
        )
        self.assertAlmostEqual(rotated_box.xlen, 4.0)
        self.assertAlmostEqual(rotated_box.ylen, 2.0)

    def test_grouped_and_per_instance_highlights_follow_metadata_order(self):
        assembly = cq.Assembly(name="root")
        assembly.add(cq.Workplane("XY").box(1, 1, 1), name="bolt_01")
        assembly.add(cq.Workplane("XY").box(3, 3, 3), name="body")
        assembly.add(cq.Workplane("XY").box(1, 1, 1), name="bolt_02")
        contract = [("body", 1), ("bolt", 2)]
        leaves = assembly_leaves(assembly, contract)

        grouped = _highlight_groups(leaves, contract, per_instance=False)
        per_instance = _highlight_groups(leaves, contract, per_instance=True)

        self.assertEqual(
            [(name, instances) for name, instances, _, _ in grouped],
            [("body", {"body"}), ("bolt", {"bolt_01", "bolt_02"})],
        )
        self.assertEqual(
            [name for name, _, _, _ in per_instance],
            ["body", "bolt_01", "bolt_02"],
        )

    def test_semantically_distinct_equal_geometry_stays_separate(self):
        assembly = cq.Assembly(name="root")
        shape = cq.Workplane("XY").cylinder(2, 10)
        assembly.add(shape, name="left_pin")
        assembly.add(shape, name="right_pin", loc=cq.Location((20, 0, 0)))

        leaves = assembly_leaves(
            assembly,
            [("left_pin", 1), ("right_pin", 1)],
        )

        self.assertEqual(
            [leaf.component_name for leaf in leaves],
            ["left_pin", "right_pin"],
        )

    def test_longest_component_prefix_wins_for_numbered_instances(self):
        assembly = cq.Assembly(name="root")
        assembly.add(cq.Workplane("XY").box(1, 1, 1), name="bolt_01")
        assembly.add(cq.Workplane("XY").box(2, 2, 2), name="bolt_long_01")

        leaves = assembly_leaves(
            assembly,
            [("bolt", 1), ("bolt_long", 1)],
        )

        self.assertEqual(
            [leaf.component_name for leaf in leaves],
            ["bolt", "bolt_long"],
        )

    def test_quantity_mismatch_is_rejected(self):
        assembly = cq.Assembly(name="root")
        assembly.add(cq.Workplane("XY").box(1, 1, 1), name="bolt_01")
        with self.assertRaisesRegex(ValueError, "quantities do not match"):
            assembly_leaves(assembly, [("bolt", 2)])

    def test_unknown_instance_name_is_rejected(self):
        assembly = cq.Assembly(name="root")
        assembly.add(cq.Workplane("XY").box(1, 1, 1), name="mystery")
        with self.assertRaisesRegex(ValueError, "does not match"):
            assembly_leaves(assembly, [("body", 1)])

    def test_metadata_solids_must_match_component_quantities(self):
        with tempfile.TemporaryDirectory() as td:
            fam_dir = Path(td)
            (fam_dir / "family.json").write_text(
                json.dumps(
                    {
                        "solids": 2,
                        "components": [
                            {"name": "body", "quantity": 1},
                            {"name": "bolt", "quantity": 2},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "solids must equal"):
                _component_contract(fam_dir)

    def test_multi_actor_render_is_byte_deterministic(self):
        left = cq.Workplane("XY").box(4, 6, 8).val()
        right = cq.Workplane("XY").cylinder(3, 7).val().located(cq.Location((12, 0, 0)))

        def mesh(shape):
            vertices, triangles = shape.tessellate(0.05)
            return (
                np.array(
                    [[v.x, v.y, v.z] for v in vertices],
                    dtype=float,
                ),
                np.array(triangles, dtype=int),
            )

        raw = {"body": mesh(left), "pin": mesh(right)}
        all_vertices = np.concatenate(
            [vertices for vertices, _ in raw.values()],
            axis=0,
        )
        lo, hi = all_vertices.min(axis=0), all_vertices.max(axis=0)
        center, longest = (lo + hi) / 2.0, (hi - lo).max()
        meshes = {
            name: ((vertices - center) / longest + 0.5, triangles)
            for name, (vertices, triangles) in raw.items()
        }

        hashes = []
        for _ in range(2):
            image = render.render_multi_mesh(
                meshes,
                img_size=120,
                highlighted={"pin"},
            )
            payload = BytesIO()
            image.save(payload, format="PNG")
            hashes.append(hashlib.sha256(payload.getvalue()).hexdigest())

        self.assertEqual(hashes[0], hashes[1])


if __name__ == "__main__":
    unittest.main()
