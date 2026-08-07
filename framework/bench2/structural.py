"""Experimental B-Rep structural similarity (issue #196).

Voxel IoU measures how much two shapes overlap. It is insensitive to local
B-Rep structure: a missing fillet, a shallow groove or an extra through-hole
can move IoU very little while changing the CAD substantially. This module
adds a lightweight descriptor of the B-Rep itself — topology, the distribution
of face areas, the distribution of edge lengths, and raw face/edge counts —
and a similarity built from them.

It is **experimental and opt-in**. Nothing here is wired into `bench2
validate`, `bench2 preview`, STATUS.md or any leaderboard path; importing this
module has no effect on existing behaviour.

One assumption in #196 does not hold in this repository, and the design here
adapts rather than forces it: **there is no IoU or scoring pipeline in
`framework/bench2/`.** The CLI exposes `new`, `preview`, `status` and
`validate` only, and the sole `iou` reference on main is `status.py` reading a
`frontier_iou` field out of pre-existing data it does not compute. So there is
no default to leave unchanged and nothing to voxelize against. `iou` is
therefore an *input* to :func:`structural_similarity` — supplied by whichever
pipeline owns scoring — instead of something this module invents. Every
component score is returned alongside the combination so the weighting can be
ablated later, and the components are usable on their own without any IoU.

Deterministic: descriptors are sorted, so the result never depends on B-Rep
enumeration order. No dependencies beyond numpy and the pinned cadquery/OCP.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# Weights from the #196 proposal. Kept as a module constant so an ablation can
# override them without editing the function.
WEIGHTS = {"iou": 0.60, "face": 0.20, "edge": 0.15, "count": 0.05}

_SPECTRUM_SAMPLES = 256


def _ocp_hashcode_fix():
    """Restore ``TopoDS_*.HashCode`` on the pinned cadquery 2.3 / OCP 7.9 pair.

    Delegates to OCP's own ``__hash__``, which is keyed on the underlying
    shape. The ``id(self)``-based variant used elsewhere in the framework is
    not equivalent: two wrappers around the same face get different ids, so
    the same face enumerated twice hashes differently and any dedup keyed on
    HashCode silently fails. Reported separately; this module does not depend
    on that one being fixed.
    """
    from OCP.TopoDS import (
        TopoDS_Compound,
        TopoDS_CompSolid,
        TopoDS_Edge,
        TopoDS_Face,
        TopoDS_Shape,
        TopoDS_Shell,
        TopoDS_Solid,
        TopoDS_Vertex,
        TopoDS_Wire,
    )

    for _cls in (TopoDS_Shape, TopoDS_Face, TopoDS_Edge, TopoDS_Vertex,
                 TopoDS_Wire, TopoDS_Shell, TopoDS_Solid, TopoDS_Compound,
                 TopoDS_CompSolid):
        if not hasattr(_cls, "HashCode"):
            _cls.HashCode = lambda self, ub=2147483647: hash(self) % ub


@dataclass(frozen=True)
class BRepDescriptor:
    """Order-independent structural fingerprint of one shape."""

    solids: int
    shells: int
    faces: int
    edges: int
    vertices: int
    euler: tuple[int, ...]              # V - E + F per shell, sorted
    face_spectrum: tuple[float, ...]    # face areas / total area, descending
    edge_spectrum: tuple[float, ...]    # edge lengths / total length, descending

    def as_dict(self) -> dict:
        return {
            "solids": self.solids,
            "shells": self.shells,
            "faces": self.faces,
            "edges": self.edges,
            "vertices": self.vertices,
            "euler": list(self.euler),
        }


@dataclass
class StructuralScore:
    """Combined score plus every component, so ablations need no re-run."""

    iou: float
    s_face: float
    s_edge: float
    s_count: float
    topology_match: bool
    structural: float
    hard_gated: bool = False
    descriptors: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "structural": self.structural,
            "iou": self.iou,
            "s_face": self.s_face,
            "s_edge": self.s_edge,
            "s_count": self.s_count,
            "topology_match": self.topology_match,
            "hard_gated": self.hard_gated,
        }


def _area(face) -> float:
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps

    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(face.wrapped, props)
    return float(props.Mass())


def _length(edge) -> float:
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps

    props = GProp_GProps()
    BRepGProp.LinearProperties_s(edge.wrapped, props)
    return float(props.Mass())


def _normalized_spectrum(values) -> tuple[float, ...]:
    """Sorted-descending values normalized to sum 1. Order-independent."""
    vals = np.asarray([v for v in values if v > 0.0], dtype=float)
    total = float(vals.sum())
    if vals.size == 0 or total <= 0.0:
        return ()
    return tuple(np.sort(vals / total)[::-1].tolist())


def brep_descriptor(shape) -> BRepDescriptor:
    """Extract the structural descriptor of a cadquery Shape."""
    _ocp_hashcode_fix()

    shells = shape.Shells()
    euler = []
    for shell in shells:
        # chi = V - E + sum_f (2 - wires_f), NOT the naive V - E + F. A B-Rep
        # face carrying w boundary wires is a disk with w-1 holes and has its
        # own characteristic 2 - w, and periodic faces add seam edges. Measured
        # on the pinned OCP, naive V - E + F is 2 for a plain block AND for a
        # block with a through hole — it cannot see genus at all; the corrected
        # form gives 2 and 0. It is also invariant to the changes that should
        # not count as topology: a blind pocket, a fillet and a glued face
        # split all stay at 2.
        chi = (
            len(shell.Vertices())
            - len(shell.Edges())
            + sum(2 - len(f.Wires()) for f in shell.Faces())
        )
        euler.append(int(chi))

    faces, edges = shape.Faces(), shape.Edges()
    return BRepDescriptor(
        solids=len(shape.Solids()),
        shells=len(shells),
        faces=len(faces),
        edges=len(edges),
        vertices=len(shape.Vertices()),
        euler=tuple(sorted(euler)),
        face_spectrum=_normalized_spectrum(_area(f) for f in faces),
        edge_spectrum=_normalized_spectrum(_length(e) for e in edges),
    )


def spectrum_similarity(a: tuple, b: tuple, samples: int = _SPECTRUM_SAMPLES) -> float:
    """Similarity of two normalized spectra, in [0, 1].

    Both spectra are turned into cumulative curves over their own normalized
    rank axis and resampled onto a shared grid, so spectra of different length
    are directly comparable and splitting one face into two moves the curve
    only by the width of that face's step rather than by its whole area. The
    score is ``1 - mean |C_a - C_b|``.
    """
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0

    def curve(spec):
        cum = np.concatenate(([0.0], np.cumsum(np.asarray(spec, dtype=float))))
        x = np.linspace(0.0, 1.0, cum.size)
        return np.interp(np.linspace(0.0, 1.0, samples), x, cum)

    return float(1.0 - np.mean(np.abs(curve(a) - curve(b))))


def count_similarity(a: BRepDescriptor, b: BRepDescriptor) -> float:
    """Low-weight face/edge count agreement, in [0, 1]."""
    parts = []
    for x, y in ((a.faces, b.faces), (a.edges, b.edges)):
        hi = max(x, y)
        parts.append(1.0 if hi == 0 else 1.0 - abs(x - y) / hi)
    return float(np.mean(parts))


def topology_match(a: BRepDescriptor, b: BRepDescriptor) -> bool:
    """Same solid/shell structure and the same Euler characteristics."""
    return (a.solids, a.shells, a.euler) == (b.solids, b.shells, b.euler)


def structural_similarity(
    shape_a,
    shape_b,
    iou: float,
    *,
    hard_gate: bool = False,
    weights: dict | None = None,
) -> StructuralScore:
    """Combine IoU with the B-Rep components of #196.

    ``iou`` is supplied by the caller — see the module docstring: this
    repository has no IoU implementation to call. ``hard_gate=True`` forces the
    combined score to 0 on a topology mismatch; the default reports the
    mismatch as a diagnostic and leaves the components untouched, so both
    treatments can be compared on the same run.
    """
    w = dict(WEIGHTS if weights is None else weights)
    da, db = brep_descriptor(shape_a), brep_descriptor(shape_b)

    s_face = spectrum_similarity(da.face_spectrum, db.face_spectrum)
    s_edge = spectrum_similarity(da.edge_spectrum, db.edge_spectrum)
    s_count = count_similarity(da, db)
    matched = topology_match(da, db)

    combined = (
        w["iou"] * float(iou)
        + w["face"] * s_face
        + w["edge"] * s_edge
        + w["count"] * s_count
    )
    gated = bool(hard_gate and not matched)
    if gated:
        combined = 0.0

    return StructuralScore(
        iou=float(iou),
        s_face=s_face,
        s_edge=s_edge,
        s_count=s_count,
        topology_match=matched,
        structural=combined,
        hard_gated=gated,
        descriptors={"a": da.as_dict(), "b": db.as_dict()},
    )
