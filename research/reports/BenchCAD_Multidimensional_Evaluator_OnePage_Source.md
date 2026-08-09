# Multidimensional Structural Evaluation for BenchCAD
### Preliminary Design & Validation Summary

## 1. Problem

BenchCAD v1 scores a reconstruction with a single normalized voxel IoU. That number is useful and we do not propose replacing it — but it cannot independently represent five distinct axes of CAD correctness: **rigid pose**, **topology / connectivity**, **local edge detail**, **face / surface geometry**, and **spatial feature placement**. v1 performs no rotational alignment at all, so a correctly-shaped part in a different orientation is penalised for nothing.

## 2. Proposed framework

```
        B-Rep descriptors (extracted once, shared)
                        ↓
                      DFCA                    one deterministic transform
                        ↓
        ┌───────────────┴───────────────┐
       IoU                             BSS
                                ┌───────┼───────┐
                               S_T     S_E     S_F
                                └───────┴───────┘
                        ↓
              Q = I · S_T^wT · S_E^wE · S_F^wF        (wT + wE + wF = 1)
```

- **DFCA** — removes rigid pose from B-Rep structure alone: dominant same-type face correspondence, then one adjacent face for roll. One pair → one transform. No pose search, no IoU, no PCA in the selection.
- **IoU** — bulk geometric agreement; exponent fixed at 1, so structure can only subtract.
- **S_T** — topology: `1/(1 + |ΔC| + |ΔG| + |ΔV|)` over solid count, genus and enclosed voids.
- **S_E** — typed, normalized edge-length spectra, sorted and compared without explicit correspondence.
- **S_F** — the same for face areas by surface type.

## 3. Controlled validation

| perturbation | responds |
|---|---|
| rotation / translation only | **nothing** — all four components return exactly 1.0000 |
| feature moved, nothing else | **IoU only** — S_T, S_E, S_F all exactly 1.0000 |
| through-hole missing | **S_T = 0.50** while IoU moves only 0.05 |
| chamfer removed vs oversized | **S_E** orders correctly; **IoU orders it backwards** (0.9889 vs 0.9702) |
| harmless B-Rep face split | **nothing** — canonicalized before scoring, 1.0000 throughout |

The location result is why IoU stays: the structural descriptors are *measure-normalized*, so a displaced feature changes no area, length or type. They are structurally incapable of seeing it.

## 4. Blinded pilot

4 reference parts × 5 real model-generated candidates each. Ranking is **within** each reference; candidates were selected by run and round only, never by a metric. The human ranking and per-judgment confidence were frozen before any score was revealed.

| Groups 2–4 (30 pairwise) | BenchCAD v1 | New evaluator |
|---|---|---|
| pairwise agreement | 24/30 | **27/30** |
| Spearman | 0.700 | **0.867** |
| Kendall τ | 0.600 | **0.800** |
| HIGH / VERY-HIGH direction | 14/16 | **16/16** |
| confidence↔margin ρ | 0.258 | **0.48 – 0.58** |

**All 15 tested weight settings** (`wT` 0.20–0.60 × edge:face 1:1–3:1) produce identically 27/30, ρ_s 0.867, τ 0.800 — a broad stable region, not a tuned point.

Across all four groups the raw count is v1 32/40 against a best new 33/40 — **effectively tied**. The difference lies in *calibration*, not direction: v1 has one pathological case (a LOW-confidence pair given 0.993 of the group's score range, in the wrong direction); the new evaluator has none, at any setting.

## 5. Two key case studies

**A — discrimination.** A human separated {A,B,C} from {D,E} with very high confidence. Tier margin: **v1 = +0.0037**, new aggregate = **+0.1089** — roughly **29×**. The new IoU alone gives **−0.0181**, i.e. it inverts the tiers; the separation is restored by the **edge channel**.

**B — hidden topology.** Render-only inspection ranked two candidates first and second, calling them "extremely difficult to distinguish". The topology channel gave both **S_T = 0.50** against 1.00 for the rest. Forensic CAD inspection then showed each was **split into two physically disconnected solids**, separated by exactly **1.000 mm**, zero intersection, with the detached body carrying **20.8 %** of the volume. The reference has a groove at the same location, so from four rendered views the gap reads as a deeper groove.

The meaningful distinction is not A versus B — both share the defect — but **{connected} > {two-piece}**. Applying that single verified CAD fact, v1 falls from 8/10 to **2/10** on that group while the new evaluator rises to **7–8/10**.

## 6. Computational cost

DFCA's **marginal** cost, once shared B-Rep descriptors exist, is **0.08–0.64 ms** (0.64 ms against 1105 ms of preprocessing on a 5171-face part). Structural scoring is 0.00–0.54 ms per component. Exact IoU dominates — up to **96 %** of total evaluator time. Descriptor reuse saved **24 %** on the largest part. We do not claim the algorithm is O(1).

## 7. Current conclusion

The pilot does **not** establish statistical superiority or a final weighting: 4 reference parts, 20 candidates, 40 pairwise comparisons, one rater. Within those limits, the multidimensional evaluator gives **stable ranking improvement on the clean human-comparable subset**, **substantially better confidence-to-score-margin calibration**, and **detects verified CAD structural defects that both render-only human inspection and IoU missed**.

## 8. Next

Expand the blind study (more parts, more candidates per part, multiple independent raters, five-level pairwise confidence); add deliberately **human-hard / CAD-obvious** cases — disconnected solids, hidden voids, failed fuses; validate **spatial localization**, which has had **no systematic validation** and supports none of the results above; adjudicate against CAD ground truth whenever human and structural judgments strongly disagree. Select final weights only after that larger study.
