"""Spatial typed BSS — research only, per `docs/RESEARCH_STRUCTURAL_METRIC.md`.

Nothing here is imported by `framework/bench2`. This is the deep-inspection
mode: expensive, opt-in, never wired into a default.

Convention frozen in the specification:

* each shape normalized **independently**, its own bbox mapped **per-axis** to
  ``[0, 1]^3``;
* descriptor buckets are ``(cell, type, normalized measure)``;
* mass is assigned **exactly** — a crossing entity distributes its measure
  across cells so ``sum_c L(e, c) == L(e)``, realized by clipping the entity
  against the cell and reading only the scalar measure. No generated section
  geometry enters the descriptor;
* levels are independent probes, aggregated by ``min``. Not nested, not
  assumed monotone.

Candidate-cell enumeration from the entity bounding box is load-bearing, not an
optimization: an entity lying exactly *in* a boundary plane is returned whole by
an intersection against both neighbours, and enumeration breaks that tie
deterministically. Clipping every cell unconditionally over-counted edge mass by
1.9 % on a real family.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from bench2.structural import (
    EDGE_TYPE_ORDER,
    FACE_TYPE_ORDER,
    _area,
    _curve_type,
    _length,
    _ocp_hashcode_fix,
    _surface_type,
    canonicalize,
)


def _gprop():
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps

    return BRepGProp, GProp_GProps


def _linear(shape) -> float:
    BRepGProp, GProp_GProps = _gprop()
    props = GProp_GProps()
    BRepGProp.LinearProperties_s(shape, props)
    return props.Mass()


def _surface(shape) -> float:
    BRepGProp, GProp_GProps = _gprop()
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, props)
    return props.Mass()


@dataclass
class CellScore:
    """One cell's local agreement, for diagnostics only."""

    level: int
    index: tuple[int, int, int]
    bbox_normalized: tuple[float, float, float, float, float, float]
    score: float
    dominant_type_deltas: tuple[tuple[str, float], ...]


@dataclass
class SpatialComparison:
    edge_by_level: dict[int, float] = field(default_factory=dict)
    face_by_level: dict[int, float] = field(default_factory=dict)
    worst_edge_cell: CellScore | None = None
    worst_face_cell: CellScore | None = None

    @property
    def edge(self) -> float | None:
        """min over levels — the frozen aggregation."""
        return min(self.edge_by_level.values()) if self.edge_by_level else None

    @property
    def face(self) -> float | None:
        return min(self.face_by_level.values()) if self.face_by_level else None


class SpatialDescriptor:
    """Entity geometry extracted once, reused across every level."""

    def __init__(self, shape):
        _ocp_hashcode_fix()
        solid = canonicalize(shape)
        box = solid.BoundingBox()
        self.lo = np.array([box.xmin, box.ymin, box.zmin])
        self.hi = np.array([box.xmax, box.ymax, box.zmax])
        # per-axis; a degenerate axis (a flat part) must not divide by zero
        self.span = np.maximum(self.hi - self.lo, 1e-12)

        self.entities: list[tuple] = []
        for face in solid.Faces():
            b = face.BoundingBox()
            self.entities.append(
                (face.wrapped, _area(face), _surface_type(face),
                 np.array([b.xmin, b.ymin, b.zmin]),
                 np.array([b.xmax, b.ymax, b.zmax]), True)
            )
        for edge in solid.Edges():
            b = edge.BoundingBox()
            self.entities.append(
                (edge.wrapped, _length(edge), _curve_type(edge),
                 np.array([b.xmin, b.ymin, b.zmin]),
                 np.array([b.xmax, b.ymax, b.zmax]), False)
            )
        self.total_area = sum(m for _, m, _, _, _, f in self.entities if f)
        self.total_length = sum(m for _, m, _, _, _, f in self.entities if not f)
        self._boxes: dict = {}

    def _cell(self, n: int, index):
        key = (n, index)
        cached = self._boxes.get(key)
        if cached is not None:
            return cached
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
        from OCP.gp import gp_Pnt

        step = self.span / n
        idx = np.array(index, dtype=float)
        c0 = self.lo + step * idx
        c1 = c0 + step
        # the outer shell of the grid is extended so nothing falls off the edge
        pad = self.span.max() * 4.0
        c0 = np.where(np.array(index) == 0, c0 - pad, c0)
        c1 = np.where(np.array(index) == n - 1, c1 + pad, c1)
        shape = BRepPrimAPI_MakeBox(gp_Pnt(*c0), gp_Pnt(*c1)).Shape()
        self._boxes[key] = shape
        return shape

    def buckets(self, n: int) -> tuple[dict, dict]:
        """Sparse ``{(cell, type): [normalized measures]}`` for edges and faces."""
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Common

        edges: dict = {}
        faces: dict = {}
        step = self.span / n
        for wrapped, measure, kind, blo, bhi, is_face in self.entities:
            if measure <= 0.0:
                continue
            total = self.total_area if is_face else self.total_length
            if total <= 0.0:
                continue
            target = faces if is_face else edges

            i0 = np.clip(np.floor((blo - self.lo) / step).astype(int), 0, n - 1)
            i1 = np.clip(np.ceil((bhi - self.lo) / step).astype(int) - 1, 0, n - 1)
            i1 = np.maximum(i1, i0)
            cells = [
                (i, j, k)
                for i in range(i0[0], i1[0] + 1)
                for j in range(i0[1], i1[1] + 1)
                for k in range(i0[2], i1[2] + 1)
            ]

            if len(cells) == 1:
                target.setdefault((cells[0], kind), []).append(measure / total)
                continue

            for index in cells:
                common = BRepAlgoAPI_Common(wrapped, self._cell(n, index)).Shape()
                part = _surface(common) if is_face else _linear(common)
                if part > 1e-12:
                    target.setdefault((index, kind), []).append(part / total)

        return (
            {k: tuple(sorted(v, reverse=True)) for k, v in edges.items()},
            {k: tuple(sorted(v, reverse=True)) for k, v in faces.items()},
        )


def _order_index(order) -> dict:
    return {name: i for i, name in enumerate(order)}


def bucket_similarity(a: dict, b: dict, order, p: float = 1.0) -> float:
    """normalize -> bucket -> sort -> zero-pad -> L_p, over the union of keys."""
    rank = _order_index(order)
    keys = sorted(
        set(a) | set(b),
        key=lambda k: (k[0], rank.get(k[1], len(rank)), k[1]),
    )
    left: list[float] = []
    right: list[float] = []
    for key in keys:
        x = list(a.get(key, ()))
        y = list(b.get(key, ()))
        width = max(len(x), len(y))
        left.extend(x + [0.0] * (width - len(x)))
        right.extend(y + [0.0] * (width - len(y)))
    if not left:
        return 1.0
    diff = np.abs(np.asarray(left) - np.asarray(right)) ** p
    distance = float(diff.sum() ** (1.0 / p))
    return float(max(0.0, 1.0 - distance / (2.0 ** (1.0 / p))))


def _worst_cell(a: dict, b: dict, order, level: int, p: float) -> CellScore | None:
    """Local agreement per cell. Diagnostic only; never enters a score."""
    cells = {k[0] for k in a} | {k[0] for k in b}
    worst: CellScore | None = None
    for cell in cells:
        sub_a = {k: v for k, v in a.items() if k[0] == cell}
        sub_b = {k: v for k, v in b.items() if k[0] == cell}
        score = bucket_similarity(sub_a, sub_b, order, p)
        if worst is not None and score >= worst.score:
            continue
        deltas: dict[str, float] = {}
        for key in set(sub_a) | set(sub_b):
            mass = abs(sum(sub_a.get(key, ())) - sum(sub_b.get(key, ())))
            deltas[key[1]] = deltas.get(key[1], 0.0) + mass
        top = tuple(sorted(deltas.items(), key=lambda kv: -kv[1])[:3])
        n = level
        step = 1.0 / n
        c0 = tuple(i * step for i in cell)
        worst = CellScore(
            level=n,
            index=cell,
            bbox_normalized=(c0[0], c0[1], c0[2],
                             c0[0] + step, c0[1] + step, c0[2] + step),
            score=score,
            dominant_type_deltas=top,
        )
    return worst


def compare_spatial(
    shape_a,
    shape_b,
    *,
    levels=(2, 3, 4),
    p_edge: float = 1.0,
    p_face: float = 1.0,
) -> SpatialComparison:
    """Typed spatial BSS across independent levels, aggregated by min.

    ``levels`` is an inspection specification, deliberately not frozen.
    """
    da = SpatialDescriptor(shape_a)
    db = SpatialDescriptor(shape_b)
    result = SpatialComparison()
    for n in levels:
        ea, fa = da.buckets(n)
        eb, fb = db.buckets(n)
        result.edge_by_level[n] = bucket_similarity(ea, eb, EDGE_TYPE_ORDER, p_edge)
        result.face_by_level[n] = bucket_similarity(fa, fb, FACE_TYPE_ORDER, p_face)

        cell_e = _worst_cell(ea, eb, EDGE_TYPE_ORDER, n, p_edge)
        if cell_e is not None and (
            result.worst_edge_cell is None
            or cell_e.score < result.worst_edge_cell.score
        ):
            result.worst_edge_cell = cell_e
        cell_f = _worst_cell(fa, fb, FACE_TYPE_ORDER, n, p_face)
        if cell_f is not None and (
            result.worst_face_cell is None
            or cell_f.score < result.worst_face_cell.score
        ):
            result.worst_face_cell = cell_f
    return result
