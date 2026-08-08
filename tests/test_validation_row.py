"""Strict N/A semantics of the research validation row.

These pin the two rules that have already been observed to fail in practice:
a failure must never arrive as a score, and an N/A component must never be
renormalized away.
"""

from __future__ import annotations

import pytest

from research.bss_validation.row import (
    REQUIRED_COMPONENTS,
    IouStatus,
    ValidationRow,
    applicability,
    applicability_class,
    combine,
)

WEIGHTS = {"iou": 0.25, "topology": 0.25, "edge": 0.25, "face": 0.25}


def _row(**kwargs) -> ValidationRow:
    base = dict(
        case_id="c", family="f", source_type="synthetic_defect",
        reference_id="a", candidate_id="b",
    )
    base.update(kwargs)
    return ValidationRow(**base)


def test_all_components_applicable_combines():
    row = _row(iou_raw=1.0, iou_status=IouStatus.OK.value,
               s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
    value, status = combine(row, WEIGHTS)
    assert status == "ok"
    assert value == pytest.approx(1.0)


def test_genuine_zero_is_a_valid_measurement_and_zeroes_the_product():
    """0.0 is maximal disagreement, not an error. No epsilon, no floor."""
    row = _row(iou_raw=0.0, iou_status=IouStatus.OK.value,
               s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
    value, status = combine(row, WEIGHTS)
    assert status == "ok"
    assert value == 0.0


@pytest.mark.parametrize("status", [
    IouStatus.FAILED_PARSE.value,
    IouStatus.FAILED_TESSELLATE.value,
    IouStatus.MISSING.value,
    IouStatus.NOT_RUN.value,
])
def test_iou_failure_is_na_not_zero(status):
    """The canonical evaluator returns 0.0 on failure; that must never score."""
    row = _row(iou_raw=None, iou_status=status,
               s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
    value, combined_status = combine(row, WEIGHTS)
    assert value is None
    assert combined_status == "na:iou"


def test_failure_and_maximal_mismatch_are_distinguishable():
    failed = _row(iou_raw=None, iou_status=IouStatus.FAILED_PARSE.value,
                  s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
    mismatch = _row(iou_raw=0.0, iou_status=IouStatus.OK.value,
                    s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
    assert combine(failed, WEIGHTS)[0] is None
    assert combine(mismatch, WEIGHTS)[0] == 0.0


def test_na_topology_propagates_strictly_without_renormalizing():
    """An assembly yields Q_raw = N/A; surviving weights are not rescaled."""
    row = _row(iou_raw=0.9, iou_status=IouStatus.OK.value,
               s_topology=None, s_edge_global=0.9, s_face_global=0.9, solids=2)
    value, status = combine(row, WEIGHTS)
    assert value is None
    assert status == "na:topology"


def test_component_scores_survive_an_na_combination():
    row = _row(iou_raw=0.9, iou_status=IouStatus.OK.value,
               s_topology=None, s_edge_global=0.9, s_face_global=0.8)
    row.q_raw, row.q_raw_status = combine(row, WEIGHTS)
    assert row.q_raw is None
    assert row.s_edge_global == 0.9
    assert row.s_face_global == 0.8


def test_applicability_class_stratifies():
    full = _row(iou_raw=1.0, iou_status=IouStatus.OK.value,
                s_topology=1.0, s_edge_global=1.0, s_face_global=1.0)
    assembly = _row(iou_raw=1.0, iou_status=IouStatus.OK.value,
                    s_topology=None, s_edge_global=1.0, s_face_global=1.0)
    assert applicability_class(applicability(full)) == "iou+topology+edge+face"
    assert applicability_class(applicability(assembly)) == "iou+edge+face"


def test_multiple_missing_components_are_all_named():
    row = _row(iou_raw=None, iou_status=IouStatus.MISSING.value, s_topology=None,
               s_edge_global=1.0, s_face_global=1.0)
    value, status = combine(row, WEIGHTS)
    assert value is None
    assert status == "na:iou,topology"


def test_required_components_are_the_four_frozen_ones():
    assert REQUIRED_COMPONENTS == ("iou", "topology", "edge", "face")


def test_row_serializes():
    row = _row(iou_raw=0.5, iou_status=IouStatus.OK.value)
    assert '"case_id": "c"' in row.to_json()
