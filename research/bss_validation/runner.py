"""Score reference/candidate STEP pairs side by side. Research only.

Reads a manifest of **opaque handles** — no corpus path or private identifier
is embedded here — and emits one :class:`ValidationRow` per pair as JSON lines.

    uv run python -m research.bss_validation.runner manifest.jsonl out.jsonl

Manifest, one JSON object per line:

    {"case_id": "...", "family": "...", "source_type": "ai_prediction",
     "reference_id": "...", "candidate_id": "...",
     "reference_path": "...", "candidate_path": "...",
     "run_id": "..."}

The purpose of the first pass is **human inspection**, not calibration: put raw
IoU next to the structural components and look at where they disagree.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .row import IouStatus, classify_iou, evaluate_pair

# IoU reimplements the canonical evaluator's definition (64^3 voxels, STEP
# tessellated at 0.05, isotropic per-shape normalization, filled, padded to
# 68^3) so this runner can work standalone. It differs in exactly one way, which
# is the point: a failure is returned as a status instead of as 0.0. The
# canonical evaluator itself is not modified here.
IOU_RESOLUTION = 64
IOU_DEFLECTION = 0.05


def _normalized_mesh(step_path: Path):
    import cadquery as cq
    import numpy as np
    import trimesh

    shape = cq.importers.importStep(str(step_path))
    solid = shape.val()
    if solid is None:
        solids = shape.solids().vals()
        if not solids:
            raise ValueError("no solids")
        solid = solids[0]
    raw_vertices, raw_triangles = solid.tessellate(IOU_DEFLECTION)
    vertices = np.array([[p.x, p.y, p.z] for p in raw_vertices], dtype=float)
    triangles = np.array([[a, b, c] for a, b, c in raw_triangles], dtype=np.int64)
    if not len(vertices) or not len(triangles):
        raise ValueError("empty tessellation")
    lo, hi = vertices.min(axis=0), vertices.max(axis=0)
    longest = (hi - lo).max()
    if longest < 1e-9:
        raise ValueError("degenerate geometry")
    vertices = (vertices - (lo + hi) / 2.0) / longest + 0.5
    return trimesh.Trimesh(vertices=vertices, faces=triangles, process=False)


def _dense(voxels, size: int):
    import numpy as np

    matrix = voxels.matrix.astype(bool)
    out = np.zeros((size, size, size), dtype=bool)
    shape = np.array(matrix.shape)
    lo = ((size - shape) // 2).clip(0)
    hi = (lo + shape).clip(max=size)
    out[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]] = matrix[
        : hi[0] - lo[0], : hi[1] - lo[1], : hi[2] - lo[2]
    ]
    return out


def raw_iou(reference: Path, candidate: Path) -> tuple[float | None, str]:
    """-> ``(iou_raw, iou_status)``. A failure is a status, never a 0.0."""
    import numpy as np

    for path in (reference, candidate):
        if not Path(path).exists():
            return classify_iou(None, IouStatus.MISSING.value)
    try:
        meshes = [_normalized_mesh(Path(p)) for p in (reference, candidate)]
    except Exception:
        return classify_iou(None, IouStatus.FAILED_PARSE.value)
    try:
        grids = [
            _dense(m.voxelized(pitch=1.0 / IOU_RESOLUTION).fill(),
                   IOU_RESOLUTION + 4)
            for m in meshes
        ]
    except Exception:
        return classify_iou(None, IouStatus.FAILED_TESSELLATE.value)
    union = np.logical_or(*grids).sum()
    if not union:
        return classify_iou(None, IouStatus.FAILED_TESSELLATE.value)
    return classify_iou(float(np.logical_and(*grids).sum() / union))


def _load_step(path: Path):
    import cadquery as cq

    shape = cq.importers.importStep(str(path))
    solid = shape.val()
    if solid is None:
        solids = shape.solids().vals()
        if not solids:
            raise ValueError(f"no solids in {path}")
        solid = cq.Compound.makeCompound(solids)
    return solid


def score_pair(entry: dict, *, weights=None, p_edge=1.0, p_face=1.0,
               spatial_levels=None):
    """One manifest entry -> one :class:`ValidationRow`."""
    from bench2.structural import _ocp_hashcode_fix

    _ocp_hashcode_fix()
    iou_value, iou_status = raw_iou(Path(entry["reference_path"]),
                                    Path(entry["candidate_path"]))
    common = dict(
        case_id=entry["case_id"], family=entry.get("family", ""),
        source_type=entry.get("source_type", "ai_prediction"),
        reference_id=entry.get("reference_id", ""),
        candidate_id=entry.get("candidate_id", ""),
        iou_raw=iou_value, iou_status=iou_status,
        run_id=entry.get("run_id", ""),
    )
    try:
        reference = _load_step(Path(entry["reference_path"]))
        candidate = _load_step(Path(entry["candidate_path"]))
    except Exception as exc:
        from .row import ValidationRow

        row = ValidationRow(**common)
        row.notes = f"geometry load failed: {exc}"
        return row

    return evaluate_pair(
        reference, candidate,
        weights=weights, p_edge=p_edge, p_face=p_face,
        spatial_levels=spatial_levels, **common,
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--spatial-levels", default="",
                        help="e.g. 2,3,4 — temporary inspection schedule")
    parser.add_argument("--p-edge", type=float, default=1.0)
    parser.add_argument("--p-face", type=float, default=1.0)
    parser.add_argument("--weights", default="",
                        help="iou,topology,edge,face — PROVISIONAL, not calibrated")
    args = parser.parse_args(argv)

    levels = tuple(int(x) for x in args.spatial_levels.split(",") if x.strip())
    weights = None
    if args.weights:
        parts = [float(x) for x in args.weights.split(",")]
        weights = dict(zip(("iou", "topology", "edge", "face"), parts))

    written = 0
    with args.output.open("w") as sink:
        for line in args.manifest.read_text().splitlines():
            if not line.strip():
                continue
            row = score_pair(json.loads(line), weights=weights,
                             p_edge=args.p_edge, p_face=args.p_face,
                             spatial_levels=levels or None)
            sink.write(row.to_json() + "\n")
            written += 1
    print(f"{written} rows -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
