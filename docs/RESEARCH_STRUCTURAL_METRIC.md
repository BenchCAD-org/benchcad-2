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
[Open blockers](#open-blockers), which are the gate on large-scale
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
Global geometric / occupancy agreement. **Raw IoU**, from the canonical
benchmark evaluator — voxel IoU on a normalized 64^3 grid, STEP tessellated at a
fixed 0.05 linear deflection, each shape normalized isotropically (bbox centre
to 0.5, longest axis to 1), filled and dense-padded to 68^3.

The baseline-relative `norm_iou` is **not** the component. Any benchmark-level
baseline normalization happens *after* `Q_raw` exists, on the complete score:

```
Q_benchmark = clip((Q_raw - Q_baseline) / (1 - Q_baseline), 0, 1)
```

where `Q_baseline` is the complete metric score of the baseline model on that
case. That outer normalization is not part of the metric definition.

**Not computed in this repository** — supplied by the canonical evaluator.
Its `0.0`-on-failure behaviour is an infrastructure hazard, see
[Established limitations](#established-limitations) item 10.

### 2. Global topology
Both shapes canonicalized with `ShapeUpgrade_UnifySameDomain`, then reduced to
three counts:

- `C` — connected solid bodies,
- `G` — total genus, summed over every shell, from a **welded triangulation**,
- `V = shells - solids` — enclosed voids,

with `D_T = |dC| + |dG| + |dV|` and `S_topology = 1 / (1 + D_T)`.

No internal C/G/V weights. Because every term is a non-negative absolute
difference, `D_G <= D_GV <= D_CGV` holds structurally: adding a quantity can
only preserve or increase detected disagreement, never hide it.

Each quantity earned its place on a counterexample the simpler descriptor
misses: `G` on a missing through hole, `V` on a hollow part modelled solid
(invisible to `G`), `C` on a solid split into two bodies (invisible to `G` and
`V`). `C` survives despite a failed boolean fuse being caught decisively by the
spectra, because topology is the only **scale-independent** channel: a 0.5 mm
stray body in a 200 mm part holds `S_topology` at 0.5000 while `S_face` reaches
1.0000 and the volume difference falls ~50x below a single 1/64 voxel.

**Genus comes from a welded mesh, not from B-Rep element counts.** Each shell is
tessellated with `BRepMesh_IncrementalMesh`, triangulation nodes are welded
across faces, and `chi = V - E + F` is computed on the mesh complex, giving
`g = (2k - chi) / 2` for `k` connected components.

The retired formula reconstructed `chi` from B-Rep vertex/edge/wire counts. It
was withdrawn because:

- **the counts were representation-dependent** — cadquery's dedup and OCP's
  topological maps disagreed on 3 of 5 shells of one family, so the same shell
  yielded `chi = 2` or `chi = 0` depending on which API was asked;
- **it produced impossible values on valid geometry** — `chi > 2` on a closed,
  connected, manifold, OCC-valid shell, converted by floor division into a
  **negative genus** with no guard;
- **three of eight real families were wrong**;
- **one was silently wrong while looking entirely reasonable** —
  `three_jaw_scroll_chuck` reported `G = 72` against a true `21`. Nothing about
  72 is anomalous, so no validity guard would ever have caught it. That is why
  the formula was replaced rather than guarded.

Every seam correction tried fixed one control and broke another; the mesh route
was correct on all nine controls first time, because a welded triangulation is a
genuine combinatorial surface and seam/periodic bookkeeping cannot leak into it.

**Validity, all required per shell:** every face triangulated; watertight and
manifold (each mesh edge in exactly two triangles); `k >= 1`; `chi` even;
resulting `g >= 0`. Any failure makes topology **N/A** for the shape — never
clamped, rounded, `abs()`-ed, repaired, or fallen back to the old formula.

Tessellation deflection and weld tolerance are **implementation constants, not
hyperparameters**: genus was measured invariant across deflection 0.5 to 0.01
(50x) and weld tolerance 1e-2 to 1e-6 (10 000x), while triangle counts moved by
orders of magnitude.

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

- **Frozen convention:** each shape is mapped **independently**, from its own
  bounding box, **per-axis**, to the unit cube. Deliberately different from the
  canonical IoU's isotropic normalization — different components have different
  jobs and no artificial symmetry is forced between them. This is load-bearing: a frame shared between the two shapes destroys
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
zero the product; that represents an extreme mismatch and is not a defect.

**Strict N/A propagation.** If any required component is N/A then `Q_raw` is
N/A. Surviving weights are **not** renormalized. Renormalization was considered
and rejected on measurement: dropping a factor is not neutral, because a
component that usually scores 1.0 pulls the geometric mean *up*. With equal
weights and identical applicable scores (I .90, E .90, F .90), a single-solid
case whose topology scores 1.0 reaches **0.9240** while the same case with
topology N/A reaches **0.9000** — a systematic 0.0240 penalty that grows to
0.0487 at `w_T = 0.5`, and reverses into a reward when topology would have
scored badly. Scores across differing applicability sets were therefore not
comparable.

The distinction preserved is **0 (valid measurement, maximal disagreement)**
versus **N/A (cannot be validly computed)**. N/A must never be silently
converted to zero. Individual component scores and diagnostics are still
reported when `Q_raw` is N/A.

Assemblies are **in scope**. `C`, `G` and `V` are all defined over multiple
solids with no new parameter, and were verified on real assemblies — chuck
(9 solids, `G = 21`, `V = 0`), bearing (11 solids, `G = 4`, `V = 0`), T-handle
pin (5 solids, `G = 0`, `V = 0`). The earlier `shells - 1` definition of `V`
claimed 8, 10 and 4 voids on those same three. An assembly yields `Q_raw` = N/A
only when its topology genuinely cannot be computed, like any other shape.

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

10. **The canonical IoU reports failure as `0.0`.** A missing file, an
    unparseable STEP, an empty tessellation or degenerate geometry all return
    `0.0` from the evaluator, which is indistinguishable from a genuine total
    mismatch. Under the epsilon-free geometric mean that value annihilates the
    entire case: a pair that is geometrically perfect but failed to parse
    scores `Q_raw = 0.0000`, where the correct N/A treatment gives `1.0000`.
    This is an evaluator-side defect, not a metric-side one. The research row
    schema refuses to accept a failure as a score, but it cannot recover
    information already discarded upstream.

11. **The canonical IoU's tessellation tolerance is absolute, and it is
    measurably safe anyway.** The `0.05` linear deflection is applied to raw mm
    geometry before normalization, so mesh fidelity is scale-dependent: the
    same part tessellates to 1556 vertices at every scale from 4 mm to 40 m,
    but coarsens to 700 at 0.4 mm. Guardrail regression, identical geometry
    compared to itself and cross-scale across five orders of magnitude:

    | pair | 64^3 (production) | 128^3 | 256^3 |
    |---|---|---|---|
    | x0.01 vs x1 | **1.0000** | 0.9992 | 1.0000 |
    | x0.1 vs x1 | **1.0000** | 1.0000 | 1.0000 |
    | each scale vs itself, x0.01 to x1000 | **1.0000** | — | — |

    Maximum observed drift is 8e-4, against a 1/64 voxel discretization scale
    of ~1.6e-2 — more than an order of magnitude below the noise floor of the
    representation, and exactly 0 at the production resolution. **Retain the
    existing implementation.** The margin would need re-checking if voxel
    resolution were ever raised.

## Implementation status

| component | status |
|---|---|
| topology (`C`, `G`, `V`, `D_T`, `S_T`) | implemented, `framework/bench2/structural.py` |
| typed edge BSS | implemented |
| typed face BSS | implemented |
| three-way weighted combination | implemented (`DEFAULT_WEIGHTS`, topology/edge/face) |
| IoU | **not implemented in this repository** |
| four-component geometric mean | **not implemented** |
| spatial refinement | **not in production**; research module `research/bss_validation/spatial.py` |
| validation row + strict N/A | research module `research/bss_validation/row.py` |

Multiple solids are in scope. A shape whose topology cannot be validly computed
raises `TopologyUndefinedError`, which callers record as N/A, never as zero.

## Deliberately deferred

Not ambiguities — decisions that must be made **from validation data**, not
intuition.

1. **`p_edge` / `p_face`** — contract is `1 <= p <= 2`; operating point unset.
2. **`w_I, w_T, w_E, w_F`** — unset. The implemented default is a three-way
   0.50 / 0.25 / 0.25 over topology/edge/face, which predates the four-component
   architecture and is not a proposal.
3. **Spatial level schedule and maximum depth** — levels stay independent,
   min-aggregated, not assumed monotone, not required to nest. Candidate
   schedules are evaluated during validation.

## Open blockers

1. **The canonical IoU returns `0.0` on any failure** — missing file,
   unparseable STEP, empty tessellation, degenerate geometry. Under an
   epsilon-free geometric mean that fake zero annihilates the case, and it is
   indistinguishable from a genuine total mismatch. It needs a sentinel
   distinct from `0.0` before any calibration data is collected. The row schema
   here refuses to accept a failure as a score, but it cannot recover
   information the evaluator has already discarded.
2. **No human-judgment labels exist anywhere.** Severity against a geometry
   pair is not recorded in any accessible source, and the primary validation
   question needs it. See
   [`RESEARCH_VALIDATION_PROTOCOL.md`](RESEARCH_VALIDATION_PROTOCOL.md).
3. **Corpus access and contamination policy.** Real prediction/reference pairs
   exist outside this repository; using benchmark evaluation data for parameter
   fitting would be contamination. Split policy proposed in the protocol
   document, pending maintainer confirmation.
