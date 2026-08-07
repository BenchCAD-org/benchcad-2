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
   `ShapeUpgrade_UnifySameDomain`, which merges same-domain faces and edge
   chains, then reduced to one corrected Euler characteristic. **Defined for a
   single-solid instance only**: out-of-scope input raises
   `NotSingleSolidError` rather than getting a silent multi-solid heuristic.
2. **Edge-length spectrum** — canonical edge lengths, each normalized by that
   shape's total edge length, sorted, zero-padded to the longer.
3. **Face-area spectrum** — the same by total surface area.

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

    def as_dict(self) -> dict:
        return {
            "solids": self.solids, "shells": self.shells,
            "faces": self.faces, "edges": self.edges,
            "vertices": self.vertices, "euler": list(self.euler),
            "face_spectrum": list(self.face_spectrum),
            "edge_spectrum": list(self.edge_spectrum),
        }


@dataclass
class StructuralComparison:
    """Everything one comparison produced, so a sweep never recomputes it."""

    raw_a: BRepDescriptor
    raw_b: BRepDescriptor
    canonical_a: BRepDescriptor
    canonical_b: BRepDescriptor
    chi_reference: int
    chi_candidate: int
    abs_chi_difference: int
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
        s_edge = spectrum_similarity(
            self.canonical_a.edge_spectrum, self.canonical_b.edge_spectrum, p=pe)
        s_face = spectrum_similarity(
            self.canonical_a.face_spectrum, self.canonical_b.face_spectrum, p=pf)
        return StructuralComparison(
            raw_a=self.raw_a, raw_b=self.raw_b,
            canonical_a=self.canonical_a, canonical_b=self.canonical_b,
            chi_reference=self.chi_reference, chi_candidate=self.chi_candidate,
            abs_chi_difference=self.abs_chi_difference,
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
            "chi_reference": self.chi_reference,
            "chi_candidate": self.chi_candidate,
            "abs_chi_difference": self.abs_chi_difference,
            "s_topology": self.s_topology,
            "topology_exact_match": self.topology_match,
            "s_edge": self.s_edge, "s_face": self.s_face,
            "p_edge": self.p_edge, "p_face": self.p_face,
            "weights": dict(self.weights),
            "structural": self.structural,
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
    return BRepDescriptor(
        solids=len(shape.Solids()), shells=len(shells),
        faces=len(faces), edges=len(edges), vertices=len(shape.Vertices()),
        euler=tuple(sorted(euler)),
        face_spectrum=_normalized_spectrum(_area(f) for f in faces),
        edge_spectrum=_normalized_spectrum(_length(e) for e in edges),
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


def corrected_euler(descriptor: BRepDescriptor) -> int:
    """The single scalar chi for a one-solid instance.

    Summed over the solid's shells, so a solid carrying an internal void is
    still one number. Raises :class:`NotSingleSolidError` outside scope.
    """
    if descriptor.solids != 1:
        raise NotSingleSolidError(
            f"topology is defined for a single solid in this experiment; "
            f"this shape has {descriptor.solids} solids "
            f"({descriptor.shells} shells). The spectra are still available "
            f"via brep_descriptor()."
        )
    return int(sum(descriptor.euler))


def topology_similarity(chi_a: int, chi_b: int) -> float:
    """Parameter-free symmetric map from |delta chi| to [0, 1].

    ``1 / (1 + |chi_a - chi_b|)``. The relative-difference form
    ``1 - |d| / (|chi_a| + |chi_b|)`` was considered and rejected: it is
    **undefined at chi_a = chi_b = 0** (two genus-1 parts, 0/0), it saturates
    to 0.0 for a single through hole (chi 2 vs 0) so one hole already reads as
    maximally different, and it is inconsistent in |d| — chi 2 vs 0 gives 0.0
    while 2 vs 4 gives 0.667 for the same difference of 2. This form is total,
    symmetric, monotone in |delta chi|, depends on nothing else, and has no
    tunable parameter: 1, 1/2, 1/3, ...
    """
    return float(1.0 / (1.0 + abs(int(chi_a) - int(chi_b))))


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

    chi_a, chi_b = corrected_euler(can_a), corrected_euler(can_b)
    d_chi = abs(chi_a - chi_b)
    s_top = topology_similarity(chi_a, chi_b)
    s_edge = spectrum_similarity(can_a.edge_spectrum, can_b.edge_spectrum, p=p_edge)
    s_face = spectrum_similarity(can_a.face_spectrum, can_b.face_spectrum, p=p_face)

    return StructuralComparison(
        raw_a=raw_a, raw_b=raw_b, canonical_a=can_a, canonical_b=can_b,
        chi_reference=chi_a, chi_candidate=chi_b, abs_chi_difference=d_chi,
        s_topology=s_top, topology_match=(d_chi == 0),
        s_edge=s_edge, s_face=s_face, p_edge=p_edge, p_face=p_face, weights=w,
        structural=(w["topology"] * s_top + w["edge"] * s_edge + w["face"] * s_face),
    )
