"""Strict N/A semantics of the research validation row.

These pin the two rules that have already been observed to fail in practice:
a failure must never arrive as a score, and an N/A component must never be
renormalized away.
"""

from __future__ import annotations

import unittest

from research.bss_validation.row import (
    REQUIRED_COMPONENTS,
    IouStatus,
    ValidationRow,
    applicability,
    applicability_class,
    classify_iou,
    combine,
    combine_penalty,
)

WEIGHTS = {"iou": 0.25, "topology": 0.25, "edge": 0.25, "face": 0.25}


def _row(**kwargs) -> ValidationRow:
    base = dict(
        case_id="c", family="f", source_type="synthetic_defect",
        reference_id="a", candidate_id="b",
    )
    base.update(kwargs)
    return ValidationRow(**base)


class CombineTest(unittest.TestCase):
    def test_all_components_applicable_combines(self):
        row = _row(iou_raw=1.0, iou_status=IouStatus.OK.value,
                   s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
        value, status = combine(row, WEIGHTS)
        self.assertEqual(status, "ok")
        self.assertAlmostEqual(value, 1.0, places=12)

    def test_genuine_zero_in_a_structural_component_still_zeroes(self):
        """0.0 is maximal disagreement, not an error. No epsilon, no floor."""
        row = _row(iou_raw=0.5, iou_status=IouStatus.OK.value,
                   s_topology=1.0, s_edge_global=0.0, s_face_global=1.0)
        value, status = combine(row, WEIGHTS)
        self.assertEqual(status, "ok")
        self.assertEqual(value, 0.0)

    def test_valid_iou_zero_is_na_but_not_a_failure(self):
        """Excluded from Q_raw, still visible and still distinct from failure."""
        row = _row(iou_raw=0.0, iou_status=IouStatus.VALID_ZERO.value,
                   s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
        value, status = combine(row, WEIGHTS)
        self.assertIsNone(value)
        self.assertEqual(status, "na:iou")
        self.assertEqual(row.iou_raw, 0.0)          # diagnostics keep the value
        self.assertNotEqual(row.iou_status, IouStatus.FAILED_PARSE.value)

    def test_classify_iou_separates_zero_from_failure(self):
        self.assertEqual(classify_iou(0.73), (0.73, IouStatus.OK.value))
        self.assertEqual(classify_iou(0.0), (0.0, IouStatus.VALID_ZERO.value))
        self.assertEqual(
            classify_iou(None, IouStatus.FAILED_PARSE.value),
            (None, IouStatus.FAILED_PARSE.value))
        self.assertEqual(classify_iou(None), (None, IouStatus.MISSING.value))

    def test_iou_failure_is_na_not_zero(self):
        """The canonical evaluator returns 0.0 on failure; that must not score."""
        for status in (IouStatus.FAILED_PARSE.value,
                       IouStatus.FAILED_TESSELLATE.value,
                       IouStatus.MISSING.value,
                       IouStatus.NOT_RUN.value):
            with self.subTest(status=status):
                row = _row(iou_raw=None, iou_status=status, s_topology=1.0,
                           s_edge_global=1.0, s_face_global=1.0)
                value, combined = combine(row, WEIGHTS)
                self.assertIsNone(value)
                self.assertEqual(combined, "na:iou")

    def test_failure_and_maximal_mismatch_are_distinguishable(self):
        failed = _row(iou_raw=None, iou_status=IouStatus.FAILED_PARSE.value,
                      s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
        mismatch = _row(iou_raw=0.0, iou_status=IouStatus.OK.value,
                        s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
        self.assertIsNone(combine(failed, WEIGHTS)[0])
        self.assertEqual(combine(mismatch, WEIGHTS)[0], 0.0)

    def test_na_topology_propagates_without_renormalizing(self):
        """An assembly yields Q_raw = N/A; surviving weights are not rescaled."""
        row = _row(iou_raw=0.9, iou_status=IouStatus.OK.value, s_topology=None,
                   s_edge_global=0.9, s_face_global=0.9, solids=2)
        value, status = combine(row, WEIGHTS)
        self.assertIsNone(value)
        self.assertEqual(status, "na:topology")

    def test_component_scores_survive_an_na_combination(self):
        row = _row(iou_raw=0.9, iou_status=IouStatus.OK.value, s_topology=None,
                   s_edge_global=0.9, s_face_global=0.8)
        row.q_raw, row.q_raw_status = combine(row, WEIGHTS)
        self.assertIsNone(row.q_raw)
        self.assertEqual(row.s_edge_global, 0.9)
        self.assertEqual(row.s_face_global, 0.8)

    def test_multiple_missing_components_are_all_named(self):
        row = _row(iou_raw=None, iou_status=IouStatus.MISSING.value,
                   s_topology=None, s_edge_global=1.0, s_face_global=1.0)
        value, status = combine(row, WEIGHTS)
        self.assertIsNone(value)
        self.assertEqual(status, "na:iou,topology")

    def test_weights_are_honoured(self):
        row = _row(iou_raw=0.5, iou_status=IouStatus.OK.value, s_topology=1.0,
                   s_edge_global=1.0, s_face_global=1.0)
        heavy, _ = combine(row, {"iou": 0.7, "topology": 0.1,
                                 "edge": 0.1, "face": 0.1})
        light, _ = combine(row, {"iou": 0.1, "topology": 0.3,
                                 "edge": 0.3, "face": 0.3})
        self.assertLess(heavy, light)


class PenaltyCompositionTest(unittest.TestCase):
    """Q_raw = IoU * (S_T^wT * S_E^wE * S_F^wF): structure may only subtract."""

    def test_structure_never_raises_the_geometric_score(self):
        for iou, topo, edge, face in ((1.0, 1.0, 1.0, 1.0),
                                      (0.946, 1.0, 0.725, 0.908),
                                      (0.005, 1.0, 0.9, 0.9),
                                      (0.474, 0.333, 0.788, 0.774),
                                      (0.02, 1.0, 0.98, 0.89)):
            row = _row(iou_raw=iou, iou_status=IouStatus.OK.value,
                       s_topology=topo, s_edge_global=edge, s_face_global=face)
            value, status = combine_penalty(row)
            with self.subTest(iou=iou):
                self.assertEqual(status, "ok")
                self.assertLessEqual(value, iou + 1e-12)
                self.assertGreaterEqual(value, 0.0)

    def test_perfect_structure_retains_the_iou_exactly(self):
        row = _row(iou_raw=0.63, iou_status=IouStatus.OK.value,
                   s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
        value, _ = combine_penalty(row)
        self.assertAlmostEqual(value, 0.63, places=12)

    def test_low_overlap_is_not_rescued_by_structure(self):
        """The failure mode this composition exists to remove."""
        row = _row(iou_raw=0.005, iou_status=IouStatus.OK.value,
                   s_topology=1.0, s_edge_global=0.9, s_face_global=0.9)
        flat, _ = combine(row, WEIGHTS)
        penalty, _ = combine_penalty(row)
        self.assertGreater(flat, 0.2)        # the flat mean rescued it
        self.assertLess(penalty, 0.006)      # this one does not

    def test_na_propagates_strictly(self):
        row = _row(iou_raw=0.0, iou_status=IouStatus.VALID_ZERO.value,
                   s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
        self.assertEqual(combine_penalty(row), (None, "na:iou"))
        row = _row(iou_raw=0.9, iou_status=IouStatus.OK.value, s_topology=None,
                   s_edge_global=1.0, s_face_global=1.0)
        self.assertEqual(combine_penalty(row), (None, "na:topology"))


class ApplicabilityTest(unittest.TestCase):
    def test_applicability_class_stratifies(self):
        full = _row(iou_raw=1.0, iou_status=IouStatus.OK.value, s_topology=1.0,
                    s_edge_global=1.0, s_face_global=1.0)
        assembly = _row(iou_raw=1.0, iou_status=IouStatus.OK.value,
                        s_topology=None, s_edge_global=1.0, s_face_global=1.0)
        self.assertEqual(applicability_class(applicability(full)),
                         "iou+topology+edge+face")
        self.assertEqual(applicability_class(applicability(assembly)),
                         "iou+edge+face")

    def test_required_components_are_the_four_frozen_ones(self):
        self.assertEqual(REQUIRED_COMPONENTS,
                         ("iou", "topology", "edge", "face"))

    def test_row_serializes(self):
        row = _row(iou_raw=0.5, iou_status=IouStatus.OK.value)
        self.assertIn('"case_id": "c"', row.to_json())


if __name__ == "__main__":
    unittest.main()
