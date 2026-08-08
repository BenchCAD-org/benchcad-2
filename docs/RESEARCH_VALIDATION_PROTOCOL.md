# Structural comparison — validation protocol

Companion to [`RESEARCH_STRUCTURAL_METRIC.md`](RESEARCH_STRUCTURAL_METRIC.md).
Research phase, opt-in, connected to no grading path.

**Scope note.** Per [`CONTRIBUTING.md`](../CONTRIBUTING.md), this repository is
the data pipeline. What lives here is the *tooling and specification*: the pair
evaluator, the row schema, the annotation rubric, and the comparison plan.
Running a calibration campaign against benchmark model predictions is scoring
pipeline work and belongs wherever that pipeline lives. This document is written
so it can be handed there intact.

## What the validation answers

Not "does the metric separate synthetic examples" — it already does. The
question is:

> Which metric ordering agrees best with human engineering judgment on real
> AI-generated CAD?

## Human annotation

The reviewer is never asked to invent a similarity number. They assign one
ordinal severity, and optionally one or more defect labels.

### Severity rubric

Judge the **candidate against the reference as an engineering deliverable**. Ask
"if this came back from a supplier, what would I do?" — not "how different do
the numbers look".

| | label | meaning | reviewer test |
|---|---|---|---|
| **0** | equivalent | essentially correct; any difference is a legitimate alternative construction or below what matters | you would accept it without comment |
| **1** | minor defect | real but cosmetic or trivially fixable; function and fit unaffected | you would accept it with a note |
| **2** | meaningful defect | affects fit, manufacture, or a stated dimension; the part is wrong but recognizably the right part | you would send it back for correction |
| **3** | major defect | structurally or functionally wrong; wrong topology, wrong part, or unusable | you would reject and re-specify |

Rules for the annotator:

- Judge the **geometry**, not the code that produced it.
- A different but valid construction of the same shape is **0**, not a defect.
- If two defects are present, score the **worst** one, and apply both labels.
- If you cannot tell without measuring, that is evidence for **0 or 1**, not
  higher — see the scope principle in the metric specification.
- If the candidate fails to load or is empty, mark the case **unusable** rather
  than 3; that is an infrastructure outcome, not a judgment.

Four levels is deliberate: it is coarse enough to be reproducible across
reviewers and fine enough to rank methods. Inter-annotator agreement should be
measured on a shared subset before any calibration uses the labels.

### Defect taxonomy

Analysis only. **These labels never enter the metric** and must not be used to
weight, penalize, or gate anything. They exist to answer "where does each method
succeed and fail".

| label | covers |
|---|---|
| `missing_feature` | a feature present in the reference is absent |
| `extra_feature` | a feature not in the reference is present |
| `wrong_feature_type` | fillet vs chamfer, hole vs pocket, analytic vs spline |
| `wrong_feature_size` | right feature, wrong dimension |
| `wrong_feature_position` | right feature, wrong location |
| `wrong_orientation` | right feature, rotated |
| `topology_error` | hole, void, handle, or connectivity error |
| `wall_thickness_error` | continuous-geometry error at preserved surface type |
| `global_proportion_error` | overall dimension or aspect error |
| `multiple_errors` | several independent defects |
| `equivalent_construction` | different modelling route, same resulting shape |

Multiple labels are allowed and expected.

## Comparison plan

Every comparison is run on the same rows, stratified by `applicability_class`,
and scored by agreement with human severity (rank correlation against the
ordinal label, plus pairwise ordering accuracy).

**Primary**

| | method |
|---|---|
| A | raw IoU alone |
| B | BSS alone (topology + typed edge + typed face) |
| C | raw IoU + BSS, the full frozen combination |

**Ablations**, each removing exactly one source of information:

| ablation | isolates |
|---|---|
| C without topology | marginal value of `G`/`V` |
| C with untyped spectra | marginal value of type bucketing |
| C with global BSS only vs with spatial refinement | marginal value of spatial |
| spatial with level schedule variants | the deferred schedule choice |

**Known high-IoU false positives** — these must be shown to improve, and they
are the reason the descriptor was extended:

- fillet → chamfer
- matched-size fillet/chamfer substitution
- spatial feature permutation
- 90° feature orientation change
- local small-feature error

**Surface-focused controlled cases**, added for this round:

- correct surface type, wrong parameters
- wrong analytic surface type
- analytic surface replaced by a BSpline approximation
- similar-area surfaces of different geometric type

All of the above are **validation cases, not grounds for new descriptors**.

## Corpus handling

Sources are kept separate and never pooled silently:

| `source_type` | origin |
|---|---|
| `synthetic_defect` | controlled defects built in-repo; fully shareable |
| `repo_revision` | adjacent `part.py` revisions of merged families |
| `ai_prediction` | real model-generated CAD, supplied by the maintainer |
| `human_correction` | reviewer-corrected geometry |

### Contamination risk — flagged explicitly

Some available prediction corpora are **benchmark evaluation data**. Calibrating
metric parameters on benchmark evaluation data would tune the metric to the
cases it is later used to score. That is contamination, and it is not mitigated
by the metric having few parameters.

Proposed split policy, to be confirmed by a maintainer:

1. Parameters (`p_edge`, `p_face`, weights, schedule) are fitted **only** on
   `synthetic_defect` + `repo_revision` + any prediction set explicitly released
   for calibration.
2. Benchmark evaluation predictions are held out and used **once**, for
   reporting, after parameters are frozen.
3. If a case appears in both, it belongs to the held-out set.
4. The split is recorded per row and travels with the data.

### External manifest

No private repository names, paths, or geometry locations appear in this
repository. A maintainer supplies a manifest of safe identifiers and geometry
handles; the framework resolves geometry through that manifest and never
embeds a location.

```
{"case_id": "...", "family": "...", "source_type": "ai_prediction",
 "reference_id": "...", "candidate_id": "...",
 "reference_handle": "<opaque>", "candidate_handle": "<opaque>",
 "iou_raw": 0.0, "iou_status": "ok",
 "split": "calibration" | "heldout"}
```

## Row schema

Defined in `research/bss_validation/row.py`. Two properties are enforced in code
rather than by convention:

- **`iou_status` is separate from `iou_raw`.** The canonical evaluator returns
  `0.0` on any failure; that value must never reach a row as a score. A failure
  arrives as a status and the row's IoU is `None`.
- **Strict N/A propagation.** If any required component is N/A, `q_raw` is
  `None` with a status naming the missing component. Weights are not
  renormalized. Every component score and diagnostic is still recorded.

Assemblies are in scope. Topology is defined over multiple solids as
`C = solids`, `G` = total welded-mesh genus, `V = shells - solids`, so the four
assemblies among the nine merged families enter combined-score comparisons like
any other case. A row is N/A only when topology genuinely cannot be computed —
a shell that is not watertight, an untriangulable face, or an Euler result
inconsistent with a closed orientable surface.
