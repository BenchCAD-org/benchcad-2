# Multidimensional Structural Evaluation for BenchCAD
## Technical Report — Preliminary Design and Validation

Status: research prototype. No production code changed. **No final weights selected. Spatial scoring not validated.**

---

## 1. Motivation

BenchCAD v1 scores a reconstruction with a single number: voxel IoU on a normalized 64³ grid, each shape independently normalized so its bounding box centre maps to 0.5 and its longest axis to 1, tessellated at a fixed 0.05 linear deflection, filled and dense-padded to 68³.

That number is genuinely useful and this work does not propose replacing it. It is, however, a single projection of a problem with several independent axes:

| axis | what varies | does normalized voxel IoU see it? |
|---|---|---|
| **rigid pose** | rotation, translation | **no** — v1 removes translation but performs no rotational alignment, so a correct part in a different orientation is penalised for nothing |
| **spatial feature location** | a correct feature in the wrong place | **yes**, and it is the only channel that does |
| **topology / connectivity** | holes, voids, disconnected bodies | weakly — a missing through hole moved IoU by ~0.05 in our controlled tests |
| **edge / detail structure** | chamfers, fillets, boundary detail | poorly — see the chamfer inversion in §5 |
| **face / surface structure** | surface type substitution, radius errors | partially |

The design goal is therefore **complementarity, not replacement**: keep IoU as the geometric base, add cheap structural channels that see what overlap cannot, and remove pose as a preprocessing step so it never masquerades as a modelling error.

---

## 2. DFCA — Dominant Face Correspondence Alignment

DFCA is **preprocessing, not a scoring dimension**. Its only job is to remove irrelevant rigid pose differences using the minimum structural information necessary. A local modelling error must not be converted into an alignment failure and then into a second, amplified penalty.

### 2.1 Frozen algorithm

**Primary correspondence.** For every face type present in both shapes, take each shape's largest face of that type by *normalized* area and compute

```
s_A(t) = min(A_ref(t), A_cand(t)) / max(A_ref(t), A_cand(t))
type*  = argmax_t s_A(t)
s_best = s_A(type*)
```

No face type has fixed priority — `Plane` is not preferred over `Cylinder`, `Cylinder` not over `BSpline`. The evidence chooses the type. With `τ = 0.70` fixed:

- `s_best ≥ τ` → anchor on `type*`'s dominant face pair (`mode = typed`);
- `s_best < τ` → relax the type constraint **on the primary anchor only** and pair the globally largest faces (`mode = degraded_cross_type`).

**Primary orientation** comes from the anchor face's intrinsic direction — plane normal (sign from face orientation), or cylinder/cone/torus axis. Faces without an intrinsic axis (sphere, BSpline) fall back to the centroid offset from the shape centre.

**Second direction, local.** Adjacent faces of the anchor are sorted by descending normalized area and scanned **sequentially**. The first one whose centroid offset has a non-degenerate component perpendicular to the primary axis fixes the roll. This is a scan that stops at the first usable face, not an enumeration. Face type is **not** required to match here — the second face is only a directional anchor.

**Second direction, global.** A locally axisymmetric one-ring does **not** prove the part is globally symmetric. If the local scan fails on either side, the primary faces are excluded and the same `s_A` evidence rule is applied over all remaining faces, selecting a *correspondence pair*; the first pair giving an independent direction on both sides wins.

**Canonical roll** is used **only** when both scans fail, i.e. when the missing rotational degree of freedom is genuinely unobservable from the geometry. Flagged `roll_unobservable = true`. This is not a failure and does not refuse.

Translation is removed by the **centre of mass**; scale by **volume^(1/3)**. Both are rotation-invariant — an earlier version used the bounding box, which is not, so a rotated copy of the same part normalized differently and could never align.

**Two independent directions determine a rigid orientation.** The anchor axis fixes two of three rotational degrees of freedom; one non-parallel second direction fixes the third. Nothing more is needed, and taking more would be pose search.

**Frame construction enforces `det(R) = +1`**, so reflection is structurally impossible rather than filtered afterwards. A mirrored chiral part scored 0.6271 against 1.0000 for the same part merely rotated.

**One input pair produces exactly one transform.** No PCA, no ICP, no IoU, no voxel or boolean overlap, no pose search, no rotation enumeration, no candidate set, no best-of-N inside DFCA. On the 60-pair real corpus: **60 of 60 produce a unique transform, zero refusals.**

### 2.2 A design mistake that is not part of DFCA

An earlier implementation built a **full neighbour matching matrix**: every neighbour of the reference anchor against every filtered neighbour of the candidate anchor, each surviving pairing kept as a separate correspondence. On `double_simplex_sprocket` — 5171 faces, an anchor plane with a several-hundred-tooth one-ring — this produced **760 pairings from a single anchor**, later deduplicated to 27 by structural signature, and then resolved by taking the **maximum IoU over the candidates**.

That was wrong on two counts: it was pose search under another name, and it let IoU participate in alignment. Cost followed: 760 exact booleans ≈ 6.8 minutes for one pair. **It is not part of the current algorithm** and is documented here only so it is not reintroduced.

### 2.3 Cost, and descriptor reuse

DFCA reads face type, normalized area, area ordering and adjacency — all of which the BSS layer already extracts. When those descriptors are shared rather than recomputed:

| part | total faces | shared preprocessing | **DFCA marginal** | exact IoU |
|---|---|---|---|---|
| prismatic plate | 44 | 13 ms | **0.14 ms** | 37 ms |
| `coil_spring` | 8 | 166 ms | **0.08 ms** | **4181 ms** |
| `double_simplex_sprocket` | 5171 | 1105 ms | **0.64 ms** | 587 ms |

**DFCA's marginal cost is 0.08–0.64 ms** — 0.64 ms against 1105 ms of preprocessing on a 5171-face part, about 0.06 % of total. Standalone (rebuilding its own descriptors) it costs 6–529 ms, essentially all of which is extraction it would otherwise share. Descriptor reuse saved **24 %** of total evaluator cost on the sprocket.

Stage scaling, measured: preprocessing `O(n)` (1.8 ms at 13 faces → 551 ms at 5171), primary anchor `O(n)` with a very small constant (0.46 ms at 5171 faces), local scan `O(local degree)` (0.20 ms on a 760-neighbour anchor), frame construction `O(1)`. **There is no pose-count term.**

Against a corrected PCA baseline on pure alignment: **22–61× faster** (median 51×), because PCA needs a tessellated point cloud while DFCA reads B-Rep metadata that already exists.

**We do not claim the algorithm is `O(1)`.** The defensible statement is that once shared B-Rep descriptors exist, the marginal cost of the structural alignment and scoring layer is negligible relative to descriptor extraction and exact IoU in the measured cases. Exact IoU dominated: **96 % of total evaluator time on `coil_spring`**.

---

## 3. BSS — Structural Scoring

### 3.1 Topology

```
D_T = |ΔC| + |ΔG| + |ΔV|
S_T = 1 / (1 + D_T)
```

with, in the implementation's exact terms:

- **C** = number of solid bodies (`descriptor.solids`);
- **G** = total genus, summed over every shell, from a **welded triangulation**: each shell is tessellated, triangulation nodes are welded across faces, `χ = V − E + F` is computed on the mesh complex, and `g = (2k − χ)/2` for `k` connected components;
- **V** = `shells − solids` — every solid contributes exactly one outer shell, so what remains encloses a void.

No internal C/G/V weights. Because every term is a non-negative absolute difference, `D_G ≤ D_GV ≤ D_CGV` holds structurally: adding a quantity can only preserve or increase detected disagreement.

**Why mesh genus rather than B-Rep element counts.** The previous formulation reconstructed χ from vertex/edge/wire counts. It was withdrawn because its inputs were representation-dependent — cadquery's dedup and OCP's topological maps disagreed on 3 of 5 shells of one family, so the same shell yielded χ = 2 or χ = 0 depending on which API was asked — and because it produced impossible values on valid geometry: χ > 2 on a closed, connected, manifold, OCC-valid shell, floor-divided into a **negative genus** with no guard. **Three of eight real families were wrong**, including one silently wrong while looking entirely plausible (`three_jaw_scroll_chuck`: reported G = 72, true value 21). No validity guard would have caught that, which is why the formula was replaced rather than guarded.

**Validity, all required per shell:** every face triangulated; watertight and manifold (each mesh edge in exactly two triangles); `k ≥ 1`; `χ` even; resulting `g ≥ 0`. Any failure makes topology **N/A** — never clamped, rounded, `abs()`-ed or repaired.

Tessellation deflection and weld tolerance are **implementation constants, not hyperparameters**: genus was measured invariant across deflection 0.5→0.01 (50×) and weld tolerance 1e-2→1e-6 (10 000×), while triangle counts moved by orders of magnitude.

### 3.2 Edge score `S_E`

Canonical edge lengths, each normalized by that shape's **total** edge length, bucketed by OCP curve type, then sorted and zero-padded within each bucket and compared with `L_p` (`p_edge = 1`).

Sorting replaces explicit correspondence: no face or edge matching, no assignment problem. Type bucketing prevents a `Circle` from cancelling against a `Line` — length alone does not encode curve type, so an R1 fillet and an area-matched chamfer were previously indistinguishable.

Normalization is **global, before bucketing**, which keeps the concatenated descriptor at unit mass and makes the `2^(1/p)` distance normalization valid.

### 3.3 Face score `S_F`

The same by total surface area, bucketed by OCP surface type, keeping `Cylinder` apart from `Plane`.

### 3.4 Representation handling

Both shapes are canonicalized with `ShapeUpgrade_UnifySameDomain` before any measurement. A harmless B-Rep face split is removed before it can be scored — verified: a part with its dominant face split into two, identical volume to 0.0000 and 22 faces on both sides, scores **1.0000 on all four components**.

### 3.5 Descriptors shared with DFCA

Face type, normalized face area, area ordering and face adjacency are extracted once and used by both layers. Edge type and normalized edge length are used by BSS and by DFCA's neighbour matching.

---

## 4. Aggregate and weight grid

```
Q = I · S_T^wT · S_E^wE · S_F^wF        wT + wE + wF = 1
```

IoU exponent fixed at **exactly 1**. This is deliberate: IoU is the geometric base and the structural channels are retention factors, so `0 ≤ Q ≤ I` holds by construction with no threshold, gate or exponent. The alternative — a flat four-way geometric mean — was tested and rejected: it allowed a candidate with almost no overlap to be *rescued* by structural similarity (measured on real predictions: IoU 0.005 reaching Q 0.212; IoU 0.019 reaching 0.348), inverting what the structural descriptors are for.

**Strict N/A propagation.** If any required component is N/A then `Q` is N/A; surviving weights are **not** renormalized. Renormalization was tested and rejected: dropping a factor is not neutral, because a component that usually scores 1.0 pulls the geometric mean *up*. With equal weights and identical applicable scores, a single-solid case with `S_T` = 1.0 reached 0.9240 while the same case with `S_T` N/A reached 0.9000 — a systematic 0.024 penalty growing to 0.049 at `wT` = 0.5, and reversing into a reward when topology would have scored badly.

A genuine 0.0 in a valid component is a valid measurement and zeroes the product; there is no epsilon and no floor. A *successful* IoU of exactly 0 is reported as `valid_zero` — kept in the diagnostics, excluded from `Q` — and distinguished from an infrastructure failure, which arrives as a status with `iou_raw = None`.

**Tested grid:** `wT ∈ {0.20, 0.30, 0.40, 0.50, 0.60}` × edge:face ∈ {1:1, 2:1, 3:1} = **15 settings**. `p_edge = p_face = 1` throughout.

**No final weight has been selected.** The pilot is not sufficient to determine one; see §16.

---

## 5. Controlled validation

Three reference parts (prismatic plate, rotational flange, multi-feature block), one property perturbed at a time. All self-comparisons score 1.0000 on all four components.

| family | perturbation | IoU | `S_T` | `S_E` | `S_F` |
|---|---|---|---|---|---|
| **pose** | rotation 37°, translation, both | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| **bulk** | thickness 12→14 / 12→20 | **0.8123 / 0.5247** | 1.0000 | 0.9802 / 0.9258 | 0.9605 / 0.8669 |
| **topology** | one hole missing / extra | 0.9492 / 0.9528 | **0.5000 / 0.5000** | 0.8992 / 0.9083 | 0.9572 / 0.9583 |
| **detail** | chamfer removed | 0.9889 | 1.0000 | **0.7732** | 0.9467 |
| detail | chamfer 1.0→0.5 / →2.0 | 0.9917 / 0.9702 | 1.0000 | 0.9849 / 0.9704 | 0.9730 / 0.9435 |
| **surface** | Plane → arched | 0.9503 | 1.0000 | **0.6206** | **0.6699** |
| **location** | hole 18→14 / 18→8 | **0.9470 / 0.9136** | **1.0000** | **1.0000** | **1.0000** |
| **representation** | dominant face split, geometry identical | **1.0000** | **1.0000** | **1.0000** | **1.0000** |

**Pose.** DFCA restores pose-only cases to exactly 1.0000 on every component. Pose is not treated as a modelling error.

**Location — why IoU remains necessary.** For pure feature displacement, `S_T`, `S_E` and `S_F` are **exactly 1.0000**, not approximately. Moving a hole changes no area, no length, no type and no topology, so measure-normalized multiset descriptors are *structurally incapable* of seeing it. IoU is the only channel that responds. Without IoU the evaluator would be blind to position errors entirely.

**Chamfer — where IoU alone gets the order wrong.** IoU ranks a *removed* chamfer (0.9889) **above** an oversized one (0.9702), because doubling the chamfer removes more material. `S_E` orders the severity correctly (0.9849 > 0.9704 > 0.7732). **All 15 weight settings restore the correct order**, with the margin roughly doubling from edge:face 1:1 to 3:1.

**Topology.** A missing or extra through hole moves IoU by ~0.04 while `S_T` drops categorically to 0.5000 — a difference IoU cannot distinguish from a removed chamfer (0.9889).

**Representation.** Canonicalization removes a harmless face split before measurement; no false penalty.

**Penalty localization** is clean: pose → nothing responds; bulk → IoU primarily; topology → `S_T`; chamfer → `S_E`; surface substitution → `S_E` and `S_F`; location → IoU only. **No double-penalty case was found**: on `Plane → arched`, where the dominant face type changes, DFCA stayed `typed` with `s_best` = 0.966 and IoU 0.9503 — the face-type error is charged to `S_E`/`S_F` and does not propagate into alignment failure.

Two honest negatives from the same suite: the chamfer ladder is **non-monotone under IoU**, and missing-hole versus extra-hole is **indistinguishable to every component** (the system sees that topology changed, not in which direction).

---

## 6. Computational cost

Covered quantitatively in §2.3. Headline: **DFCA marginal ≈ 0.08–0.64 ms** after shared descriptors exist; BSS component costs are 0.00–0.54 ms each; exact IoU dominates, reaching 96 % of evaluator time on `coil_spring`; descriptor reuse saved 24 % on the largest part.

---

## 7. Human-blinded pilot design

**4 reference parts × 5 candidate reconstructions each = 20 candidates.**

Candidates are **real model outputs** taken from two independent benchmark runs, selected by run identity and round position only — never by any metric value. Every candidate was verified scorable by both BenchCAD v1 and the frozen new evaluator before inclusion.

**Ranking is within each reference only.** Different parts are never ranked against one another; comparing an imperfect washer with an imperfect spring is ill-posed. An earlier flat 12-part set was built and discarded for this reason.

Presentation: reference and candidates rendered under one camera convention, four matched oblique views each, candidates anonymised A–E in a per-group random order. No case name, metric value, DFCA field, source identity or descriptive text was shown.

The human ranking was **frozen before** any v1 or new-evaluator value was revealed, and has not been revised since. The rater also recorded qualitative confidence per judgment (clearly distinguishable / moderate / weak preference / nearly indistinguishable), which later proved more informative than the rankings alone.

---

## 8. Raw overall result

Reported first and without qualification:

| | pairwise, all 4 groups | mean Spearman | mean Kendall |
|---|---|---|---|
| BenchCAD v1 | **32/40** | +0.725 | +0.600 |
| best tested new setting | **33/40** | +0.725 | +0.650 |

**On binary ordering across all four groups the two are approximately tied.** One pairwise comparison out of forty, with identical mean Spearman, is not evidence of superiority and should not be presented as such. §§9–14 explain what this number was hiding in both directions.

---

## 9. Groups 2–4 — the clean human-comparable subset

Group 1 was subsequently shown to contain a structural defect invisible in render-only inspection (§13), so the human ranking there was formed without decisive information. Analysing the remaining three groups — 30 pairwise comparisons:

| | pairwise /30 | mean Spearman | mean Kendall | HIGH+VHIGH direction | confidence↔margin ρ |
|---|---|---|---|---|---|
| **BenchCAD v1** | 24/30 | +0.7000 | +0.6000 | 14/16 | +0.2584 |
| **new evaluator** | **27/30** | **+0.8667** | **+0.8000** | **16/16** | **+0.48 … +0.58** |

**All 15 tested weight settings produce identically 27/30, Spearman +0.8667, Kendall +0.8000, and 16/16 on high-confidence direction.** Not one is worse than v1 on any metric. This is a broad stable region over the tested grid.

---

## 10. Confidence and discrimination

A metric should represent not only *which* candidate is better but *how obvious* the difference is. Using only confidence labels frozen before the new scores were seen (27 labelled comparisons):

| | VHIGH median margin | HIGH median | MED median | LOW median | HIGH direction | confidence↔margin ρ |
|---|---|---|---|---|---|---|
| **BenchCAD v1** | 0.5694 | 0.5349 | 0.3893 | 0.0971 | **12/14** | **+0.2619** |
| new `wT`=0.20 1:1 | 0.6641 | 0.4446 | 0.5180 | **0.0730** | **14/14** | **+0.5812** |
| new `wT`=0.40 3:1 | 0.6420 | 0.4677 | 0.4200 | 0.0701 | 12/14 | **+0.6197** |

(margins normalized by within-group score range)

On Groups 2–4, low-confidence median normalized margin: **v1 = 0.1408**, new = **0.099–0.113**. The new evaluator treats hard-to-distinguish candidates as more similar.

**Pathological cases** — low confidence with a huge margin, or high confidence with a near-zero one:

| | LOW confidence, margin > 0.5 | HIGH confidence, margin < 0.05 |
|---|---|---|
| **v1** | **Group 4 D vs C: normalized margin 0.9933, wrong direction** | none |
| new, all settings | **none** | **none** |

v1 spends the entire score range of a group asserting a difference the human marked LOW/MEDIUM, backwards. No new setting produces any pathological case.

One case where v1 is better: Group 1 A vs B, where v1's margin of **0.0003** matches "nearly indistinguishable" more closely than the new evaluator's 0.0734 — though §13 shows those two candidates were not in fact near-identical.

**This calibration result is arguably more informative than 32/40 versus 33/40**, because it measures the dimension on which the two methods differ rather than the one on which they agree.

---

## 11. Case study — Group 2, discrimination

Human judgment: **{A,B,C} >> D > E**, with the tier boundary marked VERY HIGH confidence and the internal A/B/C ordering marked LOW.

| measure | min{A,B,C} | max{D,E} | **tier margin** |
|---|---|---|---|
| BenchCAD v1 | 0.2095 | 0.2058 | **+0.0037** |
| new IoU alone | 0.6350 | 0.6531 | **−0.0181** (tiers inverted) |
| representative aggregate | 0.5234 | 0.4145 | **+0.1089** |

Approximately **29× the v1 tier margin**. Note the middle row: **the new IoU alone actually inverts the tiers.** The separation is restored by the **edge channel** — `S_E` ≈ 0.78 for {A,B,C} against 0.54–0.56 for {D,E}. This improvement does not come from better alignment or a better IoU; it comes from BSS.

For context, all five v1 scores in this group lie between 0.1877 and 0.2145 — a spread of 0.027 across candidates a human separated into two clearly distinct tiers with very high confidence. Ranking agreement and score usefulness are not the same thing.

---

## 12. Case study — Group 4, alignment

BenchCAD v1 scored candidate D at **0.0342** — effectively zero, below every other candidate. After DFCA, IoU(D) = **0.3428**, in the same range as the rest of the group.

The near-zero score was an **alignment artifact**, and DFCA repaired it. That is precisely what DFCA was built for.

**The ranking was not fully repaired.** D still places 4th where the human placed it 2nd. Two high-confidence human judgments *were* recovered: **A best** (v1 placed C first) and **B > E**. So the group improves on the judgments the rater was most confident about while still missing D's exact position.

---

## 13. Case study — Group 1, forensic

The most important qualitative result.

Render-only human inspection placed A and B first and second and described them as "extremely difficult to distinguish". The topology channel instead reported `S_T`(A) = `S_T`(B) = **0.5000** against 1.0000 for C, D and E.

Forensic CAD inspection showed the topology channel was correct.

| shape | **C** solids | **G** | **V** | `D_T` | `S_T` |
|---|---|---|---|---|---|
| REFERENCE | **1** | 1 | 0 | — | — |
| A | **2** | 1 | 0 | 1 | **0.5000** |
| B | **2** | 1 | 0 | 1 | **0.5000** |
| C / D / E | 1 | 1 | 0 | 0 | 1.0000 |

The penalty comes **entirely from the solid count**; genus and voids match exactly.

| candidate | body 1 | body 2 | intersection volume | **minimum separation** |
|---|---|---|---|---|
| A | 33561.61 mm³ (79.2 %) | 8796.46 mm³ (**20.8 %**) | **0.000000** | **1.000000 mm** |
| B | 8796.46 mm³ (20.8 %) | 33561.68 mm³ (79.2 %) | **0.000000** | **1.000000 mm** |

Zero intersection, exactly 1.000 mm of separation. **A and B are each a part in two physically disconnected pieces**, with a detached body carrying a fifth of the volume. This is **not** a B-Rep face split, a seam, a failed canonicalization or tolerance noise — the bodies do not touch.

**Why render-only inspection missed it.** The reference has a **groove at the same location**. The candidates convert that groove into a complete gap. A 1 mm separation on a 40 mm part is 2.5 % of the length; the two bodies remain coaxial and flush, so no silhouette in any of the four views distinguishes "deeper groove" from "cut in two". The defect is visible only by separating the bodies or querying the solid count.

**This is not a claim that the algorithm is better than humans.** It is a demonstration that CAD-ground-truth information exists which ordinary rendered inspection does not convey.

---

## 14. Correct interpretation of Group 1

Once the forensic facts are known, the meaningful question is **not A versus B** — they share the same major defect and their internal ordering is low-value near-tie information. The meaningful distinction is:

```
{C, D, E}  >  {A, B}
```

i.e. connected candidates above candidates split into two solids.

Applying that single verified CAD constraint, preserving the A/B near-tie and the human's D > C > E ordering within {C,D,E}, gives the minimally corrected ground truth **D > C > E > B > A**:

| | before correction | **after correction** |
|---|---|---|
| **BenchCAD v1** | 8/10 | **2/10** |
| new evaluator, `wT` ≥ 0.30 | 2–3/10 | **7–8/10** |

**This is a post-hoc CAD-ground-truth adjudication, not an independent new human ranking**, and should be weighted accordingly.

The interpretation is: **v1 appeared strong on Group 1 only because it agreed with an incomplete render-only judgment.** The topology-aware evaluator disagreed because it had detected a real hidden structural defect. The direction of the `wT` effect flips with the correction — higher topology weight hurt against the uninformed ranking and helps against the verified one, which is what should happen if the channel measures something real.

---

## 15. Group 1 component complementarity

A post-blind impression that A/B used curved rather than cylindrical side surfaces was checked against the B-Rep and **is not confirmed**.

| shape | face types | largest face | type | radius |
|---|---|---|---|---|
| REFERENCE | Plane 4, Cylinder 4 | #1 | **Cylinder** | **32.660** |
| A / B | Cylinder 4, Plane **5** | — | **Cylinder** | **20.000** |
| C / D | Cylinder 4, **Cone 2**, Plane 4 | — | Cylinder | 5.000 |
| E | Cylinder 4, Plane 4 | — | Cylinder | 15.000 |

A and B use cylindrical side surfaces, the same type as the reference. What differs is the **radius** (20.000 against 32.660) and **one extra planar face** — the newly exposed face created by the separation. Group 1 therefore contains **one real defect, not two**.

Separately: **C and D introduce two `Cone` faces that neither the reference nor A/B/E have** — a genuine surface-type error, in the candidates ranked 3rd and 4th rather than in A/B.

Component responses to the three distinct defect classes in this one group:

| defect | detected by | value |
|---|---|---|
| disconnection (A, B) | **`S_T`** | 0.5000 — invisible to IoU (0.72, mid-range) |
| radius error (A, B) | **`S_F`** | 0.7663 — lowest face score in the group |
| Cone substitution (C, D) | **`S_E`** | 0.7919 / 0.7917 — lowest edge scores in the group |

Different structural channels respond to different real defect classes within a single AI-generated example. This is the complementarity the architecture was designed for, observed rather than argued.

---

## 16. Weight sensitivity — corrected conclusion

**This section supersedes an earlier conclusion that no broad stable region exists.**

On Groups 2–4, all 15 tested settings give identical ranking statistics: **27/30, Spearman +0.8667, Kendall +0.8000, 16/16 high-confidence direction**. The tested aggregate is broadly stable to weight choice on the clean human-comparable subset.

Across all four groups raw pairwise agreement varies 29–33/40, but that variation is dominated by Group 1, where the original ranking lacked structural information. After CAD-ground-truth adjudication, increasing topology weight becomes beneficial rather than harmful.

**Do not choose a final `wT` from this pilot.** Edge:face 2:1 and 3:1 were consistently equal or better than 1:1 in both controlled and human data, but the evidence does not distinguish 2:1 from 3:1. More independent data are required.

---

## 17. Current evidence levels

**Strongly supported**

- deterministic DFCA removes tested pose and alignment artifacts (pose-only cases score exactly 1.0000 on all components);
- DFCA marginal cost is very small after descriptor reuse (0.08–0.64 ms);
- IoU and the structural channels carry complementary information;
- IoU remains necessary for feature-location differences, where BSS is exactly blind;
- topology detects real connectivity errors overlap alone can miss (Group 1, verified against the B-Rep);
- the edge channel repairs the chamfer severity inversion IoU alone produces;
- the aggregate is stable across the full tested weight grid on Groups 2–4;
- the new evaluator matches all high and very-high confidence judgments in Groups 2–4 (16/16);
- confidence-to-margin calibration is substantially stronger in this pilot (ρ ≈ 0.48–0.62 vs 0.26), with zero pathological cases against v1's one;
- Group 1 topology detection was verified directly against the CAD B-Rep.

**Promising but requires more data**

- overall superiority over BenchCAD v1;
- the final topology weight;
- edge weighted above face;
- general confidence calibration beyond this pilot.

**Not yet validated**

- **Spatial / localization scoring — no systematic validation has been performed**;
- generalization to the full benchmark;
- multiple independent human raters;
- statistical significance (4 groups, 20 candidates, 40 pairwise comparisons);
- robustness across additional model families.

---

## 18. Spatial status and the next experiment

Spatial refinement exists as a research module — per-shape bbox mapped per-axis to the unit cube, `(cell, type, measure)` buckets, exact fractional mass assignment, independent levels aggregated by minimum — and its invariances and limitations have been measured. **It has not been validated against human judgment and is not part of any result in this report.**

Proposed next-stage experiment: for the **same** candidate/reference pairs, ask human raters to mark the region containing the largest error, then compare those regions with the evaluator's worst-cell localization. One human study would then evaluate overall ranking, confidence calibration, individual dimensions and spatial localization together.

---

## 19. Next steps

- more reference parts and more candidates per reference;
- multiple independent human raters, with inter-rater agreement measured;
- a five-level pairwise confidence scale;
- deliberately constructed **human-hard / CAD-obvious** cases: disconnected solids, hidden voids, failed fuses, internal topology defects;
- spatial localization validation (§18);
- CAD-ground-truth adjudication whenever human judgment and structural metrics strongly disagree — Group 1 shows this is not a formality;
- **final weight selection only after that larger study.**

---

## 20. Conclusion

**What was built.** A multidimensional CAD evaluator: shared B-Rep descriptor extraction, a deterministic structural alignment step producing exactly one transform, then IoU alongside three structural channels — topology, edge and face — combined multiplicatively with IoU as the geometric base.

**Why it is better motivated than IoU alone.** CAD correctness is not one-dimensional. Measured on controlled perturbations, IoU is the *only* channel that sees feature location, and the structural channels are the only ones that see topology changes, chamfer severity ordering, and surface-type substitution. Neither is sufficient alone; that is a measurement, not a design preference.

**Strongest quantitative evidence.** On the clean human-comparable subset, all 15 weight settings give 27/30 pairwise against v1's 24/30, Spearman +0.867 against +0.700, and 16/16 high-confidence directions against 14/16 — with confidence-to-margin calibration roughly doubled and no pathological cases.

**Strongest qualitative evidence.** Group 1: the topology channel flagged two candidates that render-only inspection ranked highest, and forensic CAD inspection confirmed both were split into two physically disconnected solids with a measured 1.000 mm gap.

**What remains unknown.** Whether the advantage generalizes beyond 4 reference parts and one rater; the correct weights; whether spatial localization works at all against human judgment. The pilot establishes no statistical significance and selects no final weighting.
