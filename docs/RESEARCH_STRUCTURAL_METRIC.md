# Structural comparison — frozen research specification

**Status: frozen architecture, research phase.** This document fixes the design
of the B-Rep structural comparison explored in issue #196 / PR #197 so that
large-scale validation can start against a stable target.

**Scope.** Per [`CONTRIBUTING.md`](../CONTRIBUTING.md) this repository is the
AI-plus-expert data pipeline, not an evaluation or scoring pipeline. What is
specified here is *research-phase tooling used on the data*: comparing a
generated instance against its reference, inspecting a step-wise case, triaging
a family that looks wrong. It grades no model and produces no leaderboard
number. `framework/bench2/structural.py` is opt-in and wired into no default.

The freeze covers the *architecture*. It is not a claim that every component is
implemented here — see [Implementation status](#implementation-status) and
[Open ambiguities](#open-ambiguities), which are the gate on large-scale
validation.

## Design principle

> **Maximize use of existing B-Rep information rather than create new degrees of
> freedom.**

Every discrimination gained so far came from *stopping information loss*, not
from adding rules. The progression is:

```
measure  ->  (type, measure)  ->  (cell, type, measure)
```

with the comparison underneath unchanged throughout:
**normalize -> bucket -> sort -> zero-pad -> L_p**.

Frozen consequence: no new scoring dimension, penalty, feature-specific rule,
orientation channel, adjacency term, or learned component is to be added unless
large-scale validation reveals a *realistic systematic* failure. A construction
that defeats the descriptor while preserving type, mass, topology and IoU is a
theoretical collision, not grounds to complicate the metric.

## Frozen architecture

### 1. IoU
Global geometric / occupancy agreement. **Not computed in this repository** —
see [Open ambiguities](#open-ambiguities).

### 2. Global topology
Both shapes canonicalized with `ShapeUpgrade_UnifySameDomain`, then reduced to

- `G` — handles summed over the solid's shells,
- `V` — enclosed voids,

with `D = |dG| + |dV|` and `S_topology = 1 / (1 + D)`.

Summed Euler characteristic is **diagnostic only** and must not be scored: a
handle contributes -2 and a void +2, so a plain block and a block with one
through hole *and* one void both sum to 2. Measured; it is why the
decomposition is kept.

Topology is **global only** at every spatial level. It is never computed
per cell.

### 3. Edge BSS
Canonical edge lengths, each normalized by that shape's **total** edge length,
bucketed by OCP curve type, then sorted and zero-padded within each bucket and
compared with `L_p`. `p_edge` retained as a tunable.

### 4. Face BSS
The same by total surface area, bucketed by OCP surface type. `p_face` retained.

Normalization is **global, before bucketing**. This is what keeps the combined
descriptor at unit mass, which is what makes the `2 ** (1 / p)` distance
normalization valid.

### 5. Optional spatial refinement (deep inspection)

- Each shape is mapped **independently, from its own bounding box, to the unit
  cube**. This is load-bearing: a frame shared between the two shapes destroys
  uniform-scale invariance (measured: scale x25 scored **0.0000** at levels
  >= 2 under a shared frame, **1.0000** under per-shape frames).
- Buckets become `(cell, type, normalized measure)`.
- **Exact fractional mass assignment is the reference formulation**: a crossing
  entity distributes its measure across cells, `sum_c L(e,c) = L(e)` and
  `sum_c A(f,c) = A(f)`. Realized by clipping the *entity* against the cell and
  reading only the scalar measure; no generated section geometry ever enters
  the descriptor.
- Spatial resolutions are **independent probes**. They are not required to be
  nested, monotone, or individually meaningful.
- Levels aggregate as `S_edge = min_m S_edge^(m)`, `S_face = min_m S_face^(m)`.
  Not averaged, not finest-only, not weighted.
- Worst-cell score, its normalized bbox, and dominant type-mass deltas may be
  exported as **diagnostics**, carrying an alignment caveat (the worst cell
  depends on the chosen resolution).
- **First-detected level is not a general-purpose error-scale diagnostic** — see
  [Established limitations](#established-limitations).

### 6. Final combined evaluation

IoU + topology + edge BSS + face BSS under a **weighted geometric mean**, four
weights summing to 1.

No epsilon and no score floor. A genuine zero in a valid component is allowed to
zero the product; that represents an extreme mismatch and is not a defect. The
distinction that must be preserved is **0 (maximally different)** versus
**N/A (not applicable)** — N/A must never be silently converted to zero.

### Degrees of freedom

Exactly **5** continuous tunable DoF:

| | |
|---|---|
| `p_edge`, `p_face` | 2 |
| top-level weights `w_I, w_T, w_E, w_F`, sum 1 | 3 independent |

Type bucketing, min-over-level, the spatial cell descriptor and all diagnostics
add **zero**. Spatial depth and level schedule are an inspection specification,
not a fitted continuous parameter.

## Established invariances

Measured on synthetic fixtures, exact fractional assignment, per-shape frames,
across levels 1^3 / 2^3 / 3^3 / 4^3 and 1,2,4,8:

| property | result |
|---|---|
| identical shapes | 1.0000 at every level |
| uniform scale x25 | 1.0000 at every level |
| harmless face split (`glue=True` fuse) | 1.0000 at every level |
| canonicalization | `ShapeUpgrade_UnifySameDomain` removes the split before comparison |

Mass conservation of the exact assignment, summing all cells against 1:

| shape class | edges | faces |
|---|---|---|
| planar synthetic | 1e-16 | 1e-16 |
| real planar family (`slotted_din_rail`) | 1e-15 | 1e-15 |
| real curved family (`metric_plastic_cable_gland`) | 1e-15 | **~1e-7** |
| complex real family (`three_jaw_scroll_chuck`), 16^3 | — | 4.3e-10 |

The ~1e-7 on curved faces is OCC's area-integration tolerance on a clipped
trimmed surface, not a defect; scores here resolve at 1e-4.

## Established limitations

These are measured, not argued, and are part of the frozen record.

1. **Spatial refinement is not monotone.** `S^(m+1) <= S^(m)` does not hold.
   Two mechanisms: the comparison is sort-then-pair, so splitting a bucket
   changes which elements pair with which (missing fillet: 0.9060 at 1^3 rising
   to 0.9137 at 2^3); and grid alignment can recreate a coarse blind spot at a
   finer level. Min-over-level therefore has real aggregation meaning and is
   **not** equivalent to taking the finest level.

2. **Nesting buys nothing.** A dyadic schedule (1,2,4,8) was measurably *more*
   non-monotone than linear (1,2,3,4) — 4 of 8 cases versus 2 of 8. With
   cross-level fragment reuse rejected (below), nesting has no performance
   argument either. The schedule may be chosen on coverage grounds alone.

3. **First-detected level is conditional.** For **extent** defects (orientation,
   size) it tracks feature scale cleanly: a slot at 0.60 / 0.25 / 0.12 of the
   part is first detected at 4^3 / 8^3 / 16^3. For **permutation** defects
   (a fillet/chamfer swap) it does not: separations of 4 mm and 40 mm on the
   same 60 mm bar both first appear at 2^3, and 3^3 can score exactly 1.0000
   where 2^3 sees the error, because detection depends on whether a cell
   boundary happens to fall between the two features. Since the defect class is
   not known in advance, first-detected level is **not reported** as an
   error-scale diagnostic.

4. **Orientation needs no channel.** A slot rotated 90 deg in place has
   identical type masses, so global typed BSS is exactly 1.0000; spatial
   refinement alone recovers it (S_edge 0.9016 / 0.8197 / 0.7787 at
   4^3 / 8^3 / 16^3 for a slot 0.60 of the part). Edge BSS is markedly more
   sensitive than face BSS here.

5. **Boundary coincidence is a real hazard.** An entity lying exactly *in* a
   cell boundary plane is returned whole by an intersection against both
   adjacent cells. Canonicalized parts are bbox-aligned and often symmetric, so
   this is common rather than rare. Candidate-cell enumeration from the entity
   bounding box breaks the tie deterministically and must be retained; a
   formulation that clips against all cells unconditionally over-counted edge
   mass by **1.9%**.

6. **Two accelerations are rejected on invariant grounds.** Cross-level
   fragment reuse is 10.4x faster per child clip in isolation but only
   ~1.4x end-to-end and loses mass conservation (1.9e-2); last-cell-by-
   subtraction saves 2-10% and degrades mass error from 4.3e-10 to 2.2e-6.
   Neither cost difference is overwhelming, so neither is taken.

7. **Cost is dominated by faces.** Profiled at 8^3 on a 3469-entity family:
   faces are 94% of runtime at 4.25 ms per clip, edges 6% at 0.33 ms. Analytic
   handling of Line/Circle edges addresses at most 6% of runtime. Measured
   totals for that family, with bbox rejection, candidate-cell enumeration,
   full-containment shortcut, sparse storage and cached extraction all in
   place: **9.0 s at 4^3, 28.5 s at 8^3, 92.9 s at 16^3**. Cell-box caching
   gave zero. Spatial inspection is affordable per case; it is not affordable
   as an always-on component, which is why it is optional and the baseline
   stays global.

8. **Known residual, realistic:** a wall thinned by offsetting inner and outer
   faces the same way changes areas, edge lengths and types very little while
   `G`/`V` are unchanged. IoU has to carry it. This is a practical argument for
   keeping `w_I` non-trivial.

9. **Known residual, adversarial:** geometry rearranged inside every finest
   cell while preserving type, mass, topology and IoU defeats any descriptor
   without full entity correspondence. Classified as a theoretical collision;
   no action.

## Implementation status

| component | status |
|---|---|
| topology (`G`, `V`, `D`, `S`) | implemented, `framework/bench2/structural.py` |
| typed edge BSS | implemented |
| typed face BSS | implemented |
| three-way weighted combination | implemented (`DEFAULT_WEIGHTS`, topology/edge/face) |
| IoU | **not implemented in this repository** |
| four-component geometric mean | **not implemented** |
| spatial refinement | **not implemented in production**; isolated experiments only |

Input scope is a **single solid**; anything else raises `NotSingleSolidError`
rather than falling back to a silent multi-solid heuristic.

## Open ambiguities

These block moving to large-scale validation and are not resolved by this
freeze.

1. **IoU has no home here.** The frozen architecture combines four components,
   but this repository computes no IoU and `docs/STATUS.md`'s `frontier_iou` is
   a value reported from elsewhere. Where IoU is computed, at what
   voxelization/resolution, and in what frame, must be settled before any
   four-component number can be produced or validated.
2. **Weight values are unset.** The implemented default is a three-way
   0.50 / 0.25 / 0.25 over topology/edge/face. No `w_I, w_T, w_E, w_F` are
   fixed.
3. **`p_edge` / `p_face` values are unset.** The contract is `1 <= p <= 2`; the
   operating point is not chosen.
4. **N/A propagation through the geometric mean is unspecified.** Topology is
   N/A for multi-solid input, which is a large share of real families
   (assemblies). The rule for a geometric mean with an N/A factor — renormalize
   the remaining weights, or decline to produce a combined number — must be
   fixed before validation, and must not collapse to zero.
5. **Level schedule and maximum depth are unset**, and whether the unit-cube
   mapping is per-axis (anisotropic, adapts to aspect ratio) or isotropic is
   not stated. All experiments to date used per-axis.
6. **Validation data does not exist in this repository.** There are no geometry
   files and no IoU values in `main` or its history; the only comparable pairs
   are adjacent `part.py` revisions across merged families, of which few are
   single-solid. Large-scale validation needs a corpus from wherever the
   scoring pipeline lives.
