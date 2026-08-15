import importlib.util
import unittest
from pathlib import Path

from bench2.derive import derive_program
from bench2.geomlib import (
    REGISTRY,
    iso_metric_fastener_dimensions,
    make_iso_hex_bolt,
    make_iso_tapped_hole_cutter,
)
from bench2.render import _ocp_hashcode_fix


class StandardComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Repository compatibility shim for cadquery 2.3 + OCP 7.9.3.
        _ocp_hashcode_fix()

    def test_m6_dimensions(self):
        data = iso_metric_fastener_dimensions(6)
        self.assertEqual(data["pitch"], 1.0)
        self.assertEqual(data["across_flats"], 10.0)
        self.assertEqual(data["head_h"], 4.0)
        self.assertAlmostEqual(data["internal_minor_d"], 4.917468)

    def test_registry(self):
        self.assertIs(REGISTRY["make_iso_hex_bolt"], make_iso_hex_bolt)
        self.assertIs(
            REGISTRY["make_iso_tapped_hole_cutter"],
            make_iso_tapped_hole_cutter,
        )

    def test_envelope_bolt_and_tapped_cutter_are_single_solids(self):
        bolt = make_iso_hex_bolt(6, 24, 18, modeled_thread=0).val()
        cutter = make_iso_tapped_hole_cutter(6, 12).val()
        self.assertEqual(len(bolt.Solids()), 1)
        self.assertEqual(len(cutter.Solids()), 1)
        self.assertAlmostEqual(bolt.BoundingBox().zmin, -24.0, places=6)
        self.assertAlmostEqual(bolt.BoundingBox().zmax, 4.0, places=6)

    def test_modeled_thread_bolt_is_one_solid(self):
        bolt = make_iso_hex_bolt(6, 12, 6, modeled_thread=1).val()
        self.assertEqual(len(bolt.Solids()), 1)
        self.assertGreater(len(bolt.Faces()), 10)

    def test_derived_program_inlines_cross_module_dependencies(self):
        fixture = Path(__file__).with_name("standard_component_fixture.py")
        spec = importlib.util.spec_from_file_location("standard_component_fixture", fixture)
        part = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(part)
        program = derive_program(
            part,
            {"nominal_d": 6.0, "length": 24.0, "thread_length": 18.0},
        )
        self.assertIn("def make_iso_hex_bolt(", program)
        self.assertIn("def iso_metric_fastener_dimensions(", program)
        self.assertIn("def _modeled_external_metric_thread(", program)
        self.assertNotIn("from bench2.geomlib", program)
        self.assertIn("import cadquery as cq", program)
        namespace = {}
        exec(program, namespace)
        self.assertEqual(len(namespace["result"].val().Solids()), 1)


if __name__ == "__main__":
    unittest.main()
