"""Validation row: schema, strict N/A semantics, and pair evaluation.

Research only. Not imported by `framework/bench2`, not connected to grading.

Two rules from the frozen specification are enforced here rather than left to
the caller, because both have already been observed to fail in practice:

1. **A status is not a score.** ``iou_status`` is carried separately from
   ``iou_raw``. The canonical evaluator returns ``0.0`` on a missing file, an
   unparseable STEP or a degenerate tessellation, which is indistinguishable
   from a genuine total mismatch — and under an epsilon-free geometric mean
   that fake zero annihilates the whole case. A failure must arrive here as a
   status, never as a number.

2. **Strict N/A propagation.** If any required top-level component is N/A then
   ``q_raw`` is N/A. Surviving weights are *not* renormalized: dropping a
   factor is not neutral, because a component that usually scores 1.0 pulls the
   geometric mean up, so renormalizing systematically biases cases whose
   applicability sets differ. Every available component score and diagnostic is
   still reported.

IoU is supplied by the canonical evaluator, not recomputed here.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

REQUIRED_COMPONENTS = ("iou", "topology", "edge", "face")

SCHEMA_VERSION = "1.0.0"


class IouStatus(str, Enum):
    OK = "ok"
    FAILED_PARSE = "failed_parse"
    FAILED_TESSELLATE = "failed_tessellate"
    MISSING = "missing"
    NOT_RUN = "not_run"


class SourceType(str, Enum):
    SYNTHETIC_DEFECT = "synthetic_defect"
    REPO_REVISION = "repo_revision"
    AI_PREDICTION = "ai_prediction"
    HUMAN_CORRECTION = "human_correction"


@dataclass
class ValidationRow:
    case_id: str
    family: str
    source_type: str
    reference_id: str
    candidate_id: str

    defect_categories: tuple[str, ...] = ()
    severity: int | None = None

    iou_raw: float | None = None
    iou_status: str = IouStatus.NOT_RUN.value

    s_topology: float | None = None
    s_edge_global: float | None = None
    s_face_global: float | None = None

    s_edge_spatial: float | None = None
    s_face_spatial: float | None = None
    level_scores: dict[str, dict[str, float]] = field(default_factory=dict)
    worst_edge_cell: dict[str, Any] | None = None
    worst_face_cell: dict[str, Any] | None = None

    solids: int | None = None
    applicable: dict[str, bool] = field(default_factory=dict)
    applicability_class: str = ""
    q_raw: float | None = None
    q_raw_status: str = "not_computed"

    schema_version: str = SCHEMA_VERSION
    tool_version: str = ""
    ocp_version: str = ""
    run_id: str = ""
    notes: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


def applicability(row: ValidationRow) -> dict[str, bool]:
    return {
        "iou": row.iou_status == IouStatus.OK.value and row.iou_raw is not None,
        "topology": row.s_topology is not None,
        "edge": row.s_edge_global is not None,
        "face": row.s_face_global is not None,
    }


def applicability_class(applicable: dict[str, bool]) -> str:
    """Stratification key. Combined scores are comparable only within a class."""
    return "+".join(k for k in REQUIRED_COMPONENTS if applicable.get(k))


def combine(row: ValidationRow, weights: dict[str, float]) -> tuple[float | None, str]:
    """Weighted geometric mean under strict N/A propagation.

    Returns ``(q_raw, status)``. ``q_raw`` is ``None`` unless every required
    component is applicable. A genuine 0.0 is a valid measurement and is
    allowed to zero the product; there is no epsilon and no floor.
    """
    app = applicability(row)
    missing = [k for k in REQUIRED_COMPONENTS if not app.get(k)]
    if missing:
        return None, "na:" + ",".join(missing)

    total = sum(weights[k] for k in REQUIRED_COMPONENTS)
    if total <= 0.0:
        return None, "na:zero_weight"

    values = {
        "iou": row.iou_raw,
        "topology": row.s_topology,
        "edge": row.s_edge_global,
        "face": row.s_face_global,
    }
    product = 1.0
    for name in REQUIRED_COMPONENTS:
        value = float(values[name])
        if value <= 0.0:
            return 0.0, "ok"
        product *= value ** (weights[name] / total)
    return float(product), "ok"


def evaluate_pair(
    reference,
    candidate,
    *,
    case_id: str,
    family: str,
    source_type: str,
    reference_id: str,
    candidate_id: str,
    iou_raw: float | None = None,
    iou_status: str = IouStatus.NOT_RUN.value,
    p_edge: float = 1.0,
    p_face: float = 1.0,
    weights: dict[str, float] | None = None,
    spatial_levels: tuple[int, ...] | None = None,
    run_id: str = "",
) -> ValidationRow:
    """Score one reference/candidate pair into a validation row.

    ``weights`` is required only to populate ``q_raw``; omit it and the row
    still carries every component score. No default weights are supplied here
    on purpose — they are calibration variables and must not be set by
    intuition.
    """
    from bench2 import structural

    row = ValidationRow(
        case_id=case_id,
        family=family,
        source_type=source_type,
        reference_id=reference_id,
        candidate_id=candidate_id,
        iou_raw=iou_raw,
        iou_status=iou_status,
        run_id=run_id,
    )

    try:
        from OCP.OCP import __version__ as _ocp_version  # noqa: F401

        row.ocp_version = str(_ocp_version)
    except Exception:
        row.ocp_version = "unknown"
    row.tool_version = getattr(structural, "__version__", SCHEMA_VERSION)

    da = structural.brep_descriptor(reference)
    db = structural.brep_descriptor(candidate)
    row.solids = db.solids

    row.s_edge_global = structural.typed_spectrum_similarity(
        da.edge_by_type, db.edge_by_type, structural.EDGE_TYPE_ORDER, p=p_edge
    )
    row.s_face_global = structural.typed_spectrum_similarity(
        da.face_by_type, db.face_by_type, structural.FACE_TYPE_ORDER, p=p_face
    )

    # Topology is single-solid scope. Multi-solid is N/A, not zero, and under
    # strict propagation that makes the whole combined score N/A.
    try:
        topo = structural.compare_topology(da, db)
        row.s_topology = topo.topology_similarity
    except structural.NotSingleSolidError as exc:
        row.s_topology = None
        row.notes = f"topology N/A: {exc}"

    if spatial_levels:
        from .spatial import compare_spatial

        spatial = compare_spatial(
            reference, candidate,
            levels=spatial_levels, p_edge=p_edge, p_face=p_face,
        )
        row.s_edge_spatial = spatial.edge
        row.s_face_spatial = spatial.face
        row.level_scores = {
            str(n): {"edge": spatial.edge_by_level[n], "face": spatial.face_by_level[n]}
            for n in spatial.edge_by_level
        }
        if spatial.worst_edge_cell is not None:
            row.worst_edge_cell = asdict(spatial.worst_edge_cell)
        if spatial.worst_face_cell is not None:
            row.worst_face_cell = asdict(spatial.worst_face_cell)

    row.applicable = applicability(row)
    row.applicability_class = applicability_class(row.applicable)
    if weights is not None:
        row.q_raw, row.q_raw_status = combine(row, weights)
    return row
