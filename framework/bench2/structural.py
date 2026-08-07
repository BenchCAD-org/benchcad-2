"""Experimental B-Rep structural inspection tool (issue #196).

**Research-phase tooling, used on the data.** Per `CONTRIBUTING.md` this
repository is the data pipeline, not an evaluation or scoring pipeline: this
module grades no model and produces no leaderboard number. It exists to compare
two B-Reps — a generated instance against its reference, a step-wise case under
inspection, a family that looks wrong — and say *where* they differ
structurally. It is opt-in and wired into no default: importing it changes
nothing.

Three complementary signals, all permutation-invariant and all cheap. No face
correspondence, centroid matching, adjacency or assignment: the point of the
experiment is how far a very cheap descriptor goes.

1. **Topology** — both shapes are canonicalized with
   `ShapeUpgrade_UnifySameDomain`, then reduced to two counts: ``G``, the
   handles summed over the solid's shells, and ``V``, the enclosed voids.
   ``D = |dG| + |dV|`` and ``S = 1 / (1 + D)``. Summing the corrected Euler
   characteristic instead would cancel: a handle contributes -2 and a void +2,
   so a plain block and a block with one through hole *and* one void both sum
   to 2 — measured, and the reason the decomposition is kept. **Single-solid
   scope only**: out-of-scope input raises `NotSingleSolidError` rather than
   getting a silent multi-solid heuristic.
2. **Edge-length spectrum, type-aware** — canonical edge lengths, each
   normalized by that shape's total edge length, then bucketed by OCP curve
   type, sorted and zero-padded within each bucket. Length and area alone do
   not encode curve or surface type, so an R1 fillet and a chamfer sized to
   the same area were previously indistinguishable; bucketing keeps
   `Circle` from matching `Line`.
3. **Face-area spectrum, type-aware** — the same by total surface area, with
   `Cylinder` kept apart from `Plane`.

Each spectrum is compared with its own continuous ``L_p``, ``1 <= p <= 2``, and
the three signals combine under weights normalized to sum 1. Five parameters,
four degrees of freedom: ``p_edge``, ``p_face``, ``w_topology``, ``w_edge``,
``w_face``.

**Sweeping is free.** :meth:`StructuralComparison.rescore` recombines an
existing comparison under new parameters without touching OCP, so a parameter
sweep costs one descriptor extraction per pair, not one per grid point.

Two conventions the issue left open, chosen here and documented so a sweep is
readable:

* ``L_p`` is normalized by ``2 ** (1 / p)``, the largest distance possible
  between two vectors that each sum to 1 (two disjoint point masses). Without a
  p-dependent normalizer the similarity scale would shift with p and the sweep
  would compare unlike numbers.
* Topology similarity is ``1 / (1 + |delta chi|)`` — parameter-free,
  symmetric, and total. The relative-difference alternative is undefined at
  ``chi_a = chi_b = 0`` and saturates at a single through hole; see
  :func:`topology_similarity`. The exact match and the raw difference are kept
  alongside the score.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

DEFAULT_WEIGHTS = {"topology": 0.50, "edge": 0.25, "face": 0.25}

# Fixed type orders. A constant of the metric, like the 2**(1/p) divisor — not a
# tunable parameter, and no type carries a weight. Anything OCP reports that is
# not listed is appended in sorted order, so an unexpected type is still scored
# rather than silently merged.
EDGE_TYPE_ORDER = ("Line", "Circle", "Ellipse", "Hyperbola", "Parabola",
                   "BezierCurve", "BSplineCurve", "OffsetCurve", "OtherCurve")
FACE_TYPE_ORDER = ("Plane", "Cylinder", "Cone", "Sphere", "Torus",
                   "BezierSurface", "BSplineSurface", "SurfaceOfRevolution",
                   "SurfaceOfExtrusion", "OffsetSurface", "OtherSurface")
DEFAULT_P_EDGE = 1.0
DEFAULT_P_FACE = 1.0


class NotSingleSolidError(ValueError):
    """Raised when a shape is outside this experiment's single-solid scope.

    The topology signal is deliberately defined for one solid only. Rather than
    silently applying a multi-solid heuristic, out-of-scope input is reported.
    The spectra are unaffected and remain available through
    :func:`brep_descriptor` if you want them for a multi-solid shape.
    """


def _ocp_hashcode_fix():
    """Restore ``TopoDS_*.HashCode`` on the pinned cadquery 2.3 / OCP 7.9 pair.

    Delegates to OCP's own ``__hash__``, which is keyed on the underlying
    shape. The ``id(self)``-based variant used elsewhere in the framework is
    not equivalent — see #198.
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


def canonicalize(shape):
    """Merge same-domain faces and edge chains.

    One OCC call covers coplanar faces, co-cylindrical and co-conical faces,
    and collinear or co-circular edge chains. Measured on the fixtures: a
    glued split block reduces to exactly the unsplit block (10 faces/20 edges
    to 6/12) while a through hole, a fillet and a groove are untouched; on four
    merged families the Euler signature is preserved exactly.
    """
    import cadquery as cq
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain

    _ocp_hashcode_fix()
    unifier = ShapeUpgrade_UnifySameDomain(shape.wrapped, True, True, False)
    unifier.Build()
    return cq.Shape(unifier.Shape())


@dataclass(frozen=True)
class BRepDescriptor:
    """Order-independent structural fingerprint of one shape."""

    solids: int
    shells: int
    faces: int
    edges: int
    vertices: int
    euler: tuple[int, ...]              # corrected chi per shell, sorted
    face_spectrum: tuple[float, ...]    # areas / total area, descending
    edge_spectrum: tuple[float, ...]    # lengths / total length, descending
    face_by_type: tuple = ()            # ((surface type, sorted shares), ...)
    edge_by_type: tuple = ()            # ((curve type, sorted shares), ...)

    def as_dict(self) -> dict:
        return {
            "solids": self.solids, "shells": self.shells,
            "faces": self.faces, "edges": self.edges,
            "vertices": self.vertices, "euler": list(self.euler),
            "face_spectrum": list(self.face_spectrum),
            "edge_spectrum": list(self.edge_spectrum),
            "face_by_type": {t: list(v) for t, v in self.face_by_type},
            "edge_by_type": {t: list(v) for t, v in self.edge_by_type},
        }


@dataclass(frozen=True)
class TopologyComparison:
    """Every topology quantity for one pair, cached for a later sweep."""

    shell_count_reference: int
    shell_count_candidate: int
    void_count_reference: int
    void_count_candidate: int
    per_shell_chi_reference: tuple
    per_shell_chi_candidate: tuple
    per_shell_genus_reference: tuple
    per_shell_genus_candidate: tuple
    total_genus_reference: int
    total_genus_candidate: int
    abs_genus_difference: int
    abs_void_difference: int
    topology_difference: int
    topology_exact_match: bool
    topology_similarity: float
    summed_chi_reference: int      # diagnostic only, see summed_chi()
    summed_chi_candidate: int      # diagnostic only

    def as_dict(self) -> dict:
        return {
            "shell_count_reference": self.shell_count_reference,
            "shell_count_candidate": self.shell_count_candidate,
            "void_count_reference": self.void_count_reference,
            "void_count_candidate": self.void_count_candidate,
            "per_shell_chi_reference": list(self.per_shell_chi_reference),
            "per_shell_chi_candidate": list(self.per_shell_chi_candidate),
            "per_shell_genus_reference": list(self.per_shell_genus_reference),
            "per_shell_genus_candidate": list(self.per_shell_genus_candidate),
            "total_genus_reference": self.total_genus_reference,
            "total_genus_candidate": self.total_genus_candidate,
            "abs_genus_difference": self.abs_genus_difference,
            "abs_void_difference": self.abs_void_difference,
            "topology_difference": self.topology_difference,
            "topology_exact_match": self.topology_exact_match,
            "topology_similarity": self.topology_similarity,
            "summed_chi_reference": self.summed_chi_reference,
            "summed_chi_candidate": self.summed_chi_candidate,
        }


def compare_topology(a: BRepDescriptor, b: BRepDescriptor) -> TopologyComparison:
    """Full topology comparison of two canonical single-solid descriptors."""
    ga, gb = shell_genera(a), shell_genera(b)
    Ga, Gb = int(sum(ga)), int(sum(gb))
    Va, Vb = void_count(a), void_count(b)
    d = abs(Ga - Gb) + abs(Va - Vb)
    return TopologyComparison(
        shell_count_reference=a.shells, shell_count_candidate=b.shells,
        void_count_reference=Va, void_count_candidate=Vb,
        per_shell_chi_reference=a.euler, per_shell_chi_candidate=b.euler,
        per_shell_genus_reference=ga, per_shell_genus_candidate=gb,
        total_genus_reference=Ga, total_genus_candidate=Gb,
        abs_genus_difference=abs(Ga - Gb), abs_void_difference=abs(Va - Vb),
        topology_difference=d, topology_exact_match=(d == 0),
        topology_similarity=topology_similarity(d),
        summed_chi_reference=summed_chi(a), summed_chi_candidate=summed_chi(b),
    )


@dataclass
class StructuralComparison:
    """Everything one comparison produced, so a sweep never recomputes it."""

    raw_a: BRepDescriptor
    raw_b: BRepDescriptor
    canonical_a: BRepDescriptor
    canonical_b: BRepDescriptor
    topology: TopologyComparison
    s_topology: float
    topology_match: bool
    s_edge: float
    s_face: float
    p_edge: float
    p_face: float
    weights: dict = field(default_factory=dict)
    structural: float = 0.0

    def rescore(self, *, p_edge=None, p_face=None, weights=None) -> "StructuralComparison":
        """Recombine under new parameters. No OCP, no descriptor extraction."""
        pe = self.p_edge if p_edge is None else p_edge
        pf = self.p_face if p_face is None else p_face
        w = _normalize_weights(self.weights if weights is None else weights)
        s_edge = typed_spectrum_similarity(
            self.canonical_a.edge_by_type, self.canonical_b.edge_by_type,
            EDGE_TYPE_ORDER, p=pe)
        s_face = typed_spectrum_similarity(
            self.canonical_a.face_by_type, self.canonical_b.face_by_type,
            FACE_TYPE_ORDER, p=pf)
        return StructuralComparison(
            raw_a=self.raw_a, raw_b=self.raw_b,
            canonical_a=self.canonical_a, canonical_b=self.canonical_b,
            topology=self.topology,
            s_topology=self.s_topology, topology_match=self.topology_match,
            s_edge=s_edge, s_face=s_face, p_edge=pe, p_face=pf, weights=w,
            structural=(w["topology"] * self.s_topology
                        + w["edge"] * s_edge + w["face"] * s_face),
        )

    def as_dict(self) -> dict:
        """Flat, JSON-safe export for caching a sweep."""
        return {
            "raw": {"a": self.raw_a.as_dict(), "b": self.raw_b.as_dict()},
            "canonical": {"a": self.canonical_a.as_dict(),
                          "b": self.canonical_b.as_dict()},
            **self.topology.as_dict(),
            "s_topology": self.s_topology,
            "s_edge": self.s_edge, "s_face": self.s_face,
            "p_edge": self.p_edge, "p_face": self.p_face,
            "weights": dict(self.weights),
            "structural": self.structural,
        }


def _curve_type(edge) -> str:
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GeomAbs import GeomAbs_CurveType

    t = BRepAdaptor_Curve(edge.wrapped).GetType()
    for name in dir(GeomAbs_CurveType):
        if name.startswith("GeomAbs_") and getattr(GeomAbs_CurveType, name) == t:
            return name.replace("GeomAbs_", "")
    return "OtherCurve"


def _surface_type(face) -> str:
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_SurfaceType

    t = BRepAdaptor_Surface(face.wrapped).GetType()
    for name in dir(GeomAbs_SurfaceType):
        if name.startswith("GeomAbs_") and getattr(GeomAbs_SurfaceType, name) == t:
            return name.replace("GeomAbs_", "")
    return "OtherSurface"


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


def _typed_spectrum(pairs, order) -> tuple:
    """``((type, sorted normalized values), ...)`` in the fixed type order.

    Normalization is by the shape's TOTAL measure, taken **before** bucketing:
    each entry keeps the share of the whole shape it represents, so geometry
    changing type transfers mass between buckets instead of vanishing. Per
    bucket normalization would hide exactly that.
    """
    vals = [(t, float(v)) for t, v in pairs if v > 0.0]
    total = sum(v for _, v in vals)
    if not vals or total <= 0.0:
        return ()
    buckets = {}
    for t, v in vals:
        buckets.setdefault(t, []).append(v / total)
    known = [t for t in order if t in buckets]
    extra = sorted(t for t in buckets if t not in order)
    return tuple((t, tuple(sorted(buckets[t], reverse=True))) for t in known + extra)


def _normalized_spectrum(values) -> tuple[float, ...]:
    """Sorted-descending values normalized to sum 1.

    Dividing by the shape's own total makes the spectrum invariant to uniform
    scaling: lengths scale linearly and areas quadratically, and each is
    divided by its own total.
    """
    vals = np.asarray([v for v in values if v > 0.0], dtype=float)
    total = float(vals.sum())
    if vals.size == 0 or total <= 0.0:
        return ()
    return tuple(np.sort(vals / total)[::-1].tolist())


def _describe(shape) -> BRepDescriptor:
    _ocp_hashcode_fix()
    shells = shape.Shells()
    euler = []
    for shell in shells:
        # chi = V - E + sum_f (2 - wires_f), NOT the naive V - E + F. A face
        # with w boundary wires is a disk with w-1 holes (chi 2 - w), and
        # periodic faces add seam edges. Measured on the pinned OCP the naive
        # form is 2 for a plain block AND for a block with a through hole — it
        # cannot see genus; the corrected form gives 2 and 0, and stays at 2
        # for a pocket, a fillet and a glued split.
        euler.append(int(
            len(shell.Vertices()) - len(shell.Edges())
            + sum(2 - len(f.Wires()) for f in shell.Faces())
        ))
    faces, edges = shape.Faces(), shape.Edges()
    face_pairs = [(_surface_type(f), _area(f)) for f in faces]
    edge_pairs = [(_curve_type(e), _length(e)) for e in edges]
    return BRepDescriptor(
        solids=len(shape.Solids()), shells=len(shells),
        faces=len(faces), edges=len(edges), vertices=len(shape.Vertices()),
        euler=tuple(sorted(euler)),
        face_spectrum=_normalized_spectrum(v for _, v in face_pairs),
        edge_spectrum=_normalized_spectrum(v for _, v in edge_pairs),
        face_by_type=_typed_spectrum(face_pairs, FACE_TYPE_ORDER),
        edge_by_type=_typed_spectrum(edge_pairs, EDGE_TYPE_ORDER),
    )


def brep_descriptor(shape, *, canonical: bool = True) -> BRepDescriptor:
    """Descriptor of ``shape``, canonicalized first unless told otherwise."""
    return _describe(canonicalize(shape) if canonical else shape)


def spectrum_similarity(a: tuple, b: tuple, p: float = 1.0) -> float:
    """Zero-padded ``L_p`` similarity of two normalized spectra, in [0, 1].

    The shorter spectrum is zero-padded to the longer, so a fine model compared
    against a coarse one carries the padded tail as residual — inherent to a
    permutation-invariant sorted descriptor, and a systematic penalty on
    differing counts worth remembering when reading a sweep.

    Normalized by ``2 ** (1 / p)``: both spectra sum to 1, so that is the
    largest distance two of them can have (disjoint point masses). Every p
    therefore lands on the same scale.
    """
    if not 1.0 <= p <= 2.0:
        raise ValueError(f"p must be in [1, 2], got {p}")
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    n = max(len(a), len(b))
    va = np.zeros(n)
    vb = np.zeros(n)
    va[: len(a)] = a
    vb[: len(b)] = b
    distance = float(np.sum(np.abs(va - vb) ** p) ** (1.0 / p))
    return float(max(0.0, 1.0 - distance / (2.0 ** (1.0 / p))))


def _require_single_solid(descriptor: BRepDescriptor) -> None:
    if descriptor.solids != 1:
        raise NotSingleSolidError(
            f"topology is defined for a single solid in this experiment; "
            f"this shape has {descriptor.solids} solids "
            f"({descriptor.shells} shells). The spectra are still available "
            f"via brep_descriptor()."
        )


def shell_genera(descriptor: BRepDescriptor) -> tuple[int, ...]:
    """Genus of each closed shell, ``g = (2 - chi) / 2``, sorted."""
    _require_single_solid(descriptor)
    return tuple(sorted((2 - int(c)) // 2 for c in descriptor.euler))


def total_genus(descriptor: BRepDescriptor) -> int:
    """``G`` — independent handles summed over the solid's shells."""
    return int(sum(shell_genera(descriptor)))


def void_count(descriptor: BRepDescriptor) -> int:
    """``V`` — enclosed internal voids, i.e. every shell past the outer one."""
    _require_single_solid(descriptor)
    return int(descriptor.shells - 1)


def summed_chi(descriptor: BRepDescriptor) -> int:
    """Diagnostic only. **Do not compare on this.**

    A handle contributes -2 and a void +2, so they cancel exactly: measured, a
    plain block and a block carrying one through hole *and* one internal void
    both sum to 2. That cancellation is why the topology signal is built from
    ``(G, V)`` instead.
    """
    _require_single_solid(descriptor)
    return int(sum(descriptor.euler))


def topology_difference(a: BRepDescriptor, b: BRepDescriptor) -> int:
    """``D = |G_a - G_b| + |V_a - V_b|`` — how many independent topological
    structures differ.

    One handle mismatch and one void mismatch each count as one unit. That is
    deliberate: no separate handle/void weights and no tunable parameter until
    benchmark evidence says the distinction needs one.
    """
    return (abs(total_genus(a) - total_genus(b))
            + abs(void_count(a) - void_count(b)))


def topology_similarity(difference: int) -> float:
    """``1 / (1 + D)`` — total, symmetric, monotone, parameter-free.

    The relative-difference form ``1 - |d| / (|x_a| + |x_b|)`` was considered
    and rejected: undefined when both are 0, saturating at 0.0 for a single
    missing handle, and inconsistent in ``|d|``.
    """
    return float(1.0 / (1.0 + abs(int(difference))))


def _normalize_weights(weights) -> dict:
    w = dict(DEFAULT_WEIGHTS if weights is None else weights)
    missing = set(DEFAULT_WEIGHTS) - set(w)
    if missing:
        raise ValueError(f"weights must define {sorted(DEFAULT_WEIGHTS)}, missing {sorted(missing)}")
    if any(v < 0 for v in w.values()):
        raise ValueError(f"weights must be non-negative, got {w}")
    total = float(sum(w.values()))
    if total <= 0.0:
        raise ValueError("weights must not sum to zero")
    return {k: float(v) / total for k, v in w.items()}


def typed_spectrum_similarity(a: tuple, b: tuple, order, p: float = 1.0) -> float:
    """Zero-padded ``L_p`` similarity of two **typed** spectra, in [0, 1].

    Each type bucket is zero-padded against its counterpart and the buckets are
    concatenated in the fixed order, so measurements of different geometric
    type can never match each other — a cylindrical face and a planar face of
    the same area no longer cancel. A type present in one shape and absent in
    the other pads against zeros, which is how a type change registers.

    Because normalization happened globally before bucketing, the concatenated
    vector still sums to 1 and ``2 ** (1 / p)`` is still the largest distance
    two of them can have. Adds no weight and no tunable parameter.
    """
    if not 1.0 <= p <= 2.0:
        raise ValueError(f"p must be in [1, 2], got {p}")
    da, db = dict(a), dict(b)
    if not da and not db:
        return 1.0
    if not da or not db:
        return 0.0
    va, vb = [], []
    known = [t for t in order if t in da or t in db]
    extra = sorted((set(da) | set(db)) - set(order))
    for t in known + extra:
        xa, xb = list(da.get(t, ())), list(db.get(t, ()))
        n = max(len(xa), len(xb))
        va += xa + [0.0] * (n - len(xa))
        vb += xb + [0.0] * (n - len(xb))
    distance = float(np.sum(np.abs(np.array(va) - np.array(vb)) ** p) ** (1.0 / p))
    return float(max(0.0, 1.0 - distance / (2.0 ** (1.0 / p))))


def compare(
    shape_a,
    shape_b,
    *,
    p_edge: float = DEFAULT_P_EDGE,
    p_face: float = DEFAULT_P_FACE,
    weights: dict | None = None,
) -> StructuralComparison:
    """Compare two B-Reps. Descriptors are extracted once; see ``rescore``."""
    w = _normalize_weights(weights)
    raw_a, raw_b = _describe(shape_a), _describe(shape_b)
    can_a, can_b = brep_descriptor(shape_a), brep_descriptor(shape_b)

    topo = compare_topology(can_a, can_b)
    s_top = topo.topology_similarity
    s_edge = typed_spectrum_similarity(
        can_a.edge_by_type, can_b.edge_by_type, EDGE_TYPE_ORDER, p=p_edge)
    s_face = typed_spectrum_similarity(
        can_a.face_by_type, can_b.face_by_type, FACE_TYPE_ORDER, p=p_face)

    return StructuralComparison(
        raw_a=raw_a, raw_b=raw_b, canonical_a=can_a, canonical_b=can_b,
        topology=topo, s_topology=s_top,
        topology_match=topo.topology_exact_match,
        s_edge=s_edge, s_face=s_face, p_edge=p_edge, p_face=p_face, weights=w,
        structural=(w["topology"] * s_top + w["edge"] * s_edge + w["face"] * s_face),
    )
