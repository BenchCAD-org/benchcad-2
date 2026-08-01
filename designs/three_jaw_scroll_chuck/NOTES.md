# three_jaw_scroll_chuck — datasheet mapping and derivations

## Catalog symbol → parameter

| Table | Symbol | Parameter | Used as |
|---|---|---|---|
| chuck p.3048 (DIN 6350) | A | `outer_dia_A` | body OD |
| | B | `register_dia_B` | rear centering recess diameter (cut into the back, per the section view) |
| | C | `register_depth_C` | recess depth |
| | D | `height_D` | axial body height (z ∈ [−D, 0]) |
| | E | `bore_E` | through-hole |
| | F | `bolt_circle_F` | rear mounting bolt circle |
| | G | `mount_thread_G` | mounting hole ⌀, blind from the back, × `mount_hole_count` |
| | K | `key_square_K` | pinion square socket |
| jaw BB p.3060 | A/B/C | `jaw_length_A` / `jaw_width_B` / `jaw_height_C` | jaw envelope (C spans foot underside → top) |
| | D | `jaw_serration_D` | underside serration band → **scroll thread pitch** |
| | E | `jaw_tongue_E` | guide-tongue band → **T-flange height** |
| | F/G/H | `jaw_step_F/G/H` | outward step profile; the drawing labels EACH riser height H, so the profile drops H at F and another H at G (capped by 0.22·C / 0.38·C at the largest rows) |
| ranges p.3044 | A1 | `grip_min_A1`..`grip_max_A1` | `clamp_d = A1min + f·(A1max − A1min)` |

The BB side view labels D on the serrated band and E on the tongue band; the
catalogue does not dimension the serrations further, so D is taken as the
serration pitch (= the scroll pitch it must match) and E as the flange height.
This interpretation is documented, not manufacturer-certified.

## Drive train (RÖHM p.3035 cutaway: key → bevel pinion → crown ring on the
## scroll back → Archimedean spiral → jaw underside teeth)

All internals derive in `part.py:_layout` from catalog values; the same
formulas are mirrored in `spec.py:check`. Proportions (documented, not
catalogued): thread height 0.55·pitch, ridge width 0.42·pitch, jaw tooth
width 0.34·pitch, ring face width 0.10·A, pinion teeth Z_p = 12, flank
half-angle 20°, universal running clearance clr = max(0.2, 0.004·D) mm.

- **Scroll thread**: one Archimedean band r(θ) = r_start + pitch·θ/2π swept
  over the annulus between the body sleeve and 0.345·A, standing 0.55·pitch
  proud of the scroll face. Spline-sampled at 36 pts/turn (no polyline facets).
- **Jaw teeth**: concentric arc segments on the jaw foot at the spiral's
  *gap* radii evaluated at that jaw's meridian (0°/120°/240°), i.e. radii
  r_start + pitch·((θ_jaw − α)/360) + (k+½)·pitch. Jaws 1/2/3 therefore carry
  the real ⅓-pitch stagger and interleave the spiral with clr axial clearance.
  The arc-vs-spiral radial deviation over the jaw width is covered by the
  0.24·pitch side gap (verified per size).
- **Key position α** (`part._scroll_phase`, mirrored in `check()`): the
  scroll is rotated by a whole number of crown pitches k·360/Z_w — which
  leaves the bevel mesh phase untouched — choosing the k that seats the most
  arc teeth on the worst-off jaw. This is the real degree of freedom the
  operator's key provides, made deterministic; with it every catalog row
  keeps ≥ 2 engaged teeth per jaw over the entire published A1 range
  (verified on a 51-point f grid × 12 rows).
- **Bevel pair**: straight planar-flank teeth, shaft angle 90°, shared pitch
  apex on the chuck axis at the pinion axis height: tan δ_wheel = Z_w/Z_p,
  pinion pitch radius r_pp = R_ring·Z_p/Z_w = axial offset between ring pitch
  point and pinion axis. Z_w solves the axial budget (pocket bottom ≥ cover
  pocket + 1 mm) and is rounded up to a multiple of 3 so all three pinion
  meridians see a tooth centre; each pinion's tooth array is phased with a
  gap toward the ring. Addendum 0.75·m, dedendum 1.25·m, thickness 0.34·π·m
  → backlash ≈ 0.2–0.4·m and 0.5·m radial clearance (measured 0.18–1.6 mm
  across sizes, zero interpenetration on all 36 body pairs at every size).
  Module m = 2·R_ring/Z_w; δ_wheel ranges ≈ 75–82° (crown-like, as in the
  cutaway), Z_w 45–84 across the 12 rows.
- **Guideways**: two-tier T-slots (neck 0.60·B_jaw wide, flange tier jaw-width
  wide, flange height = jaw E), open at the OD; the tier-2 floor is the scroll
  cavity ceiling, so the jaw feet engage the spiral through the floor opening
  — the slots are open on the face as on the product.
- **Pinion seating**: stepped radial bore (head pocket ⌀ + journal ⌀ =
  1.7·K or 0.9·pinion pitch ⌀, 0.15 mm bore clearance); the head enters via
  the cavity, the journal seats outward; square K socket in the outer face,
  recessed 0.015·A below the OD (inside a scallop where present).
- **Retention**: the scroll is sandwiched between the cavity ceiling and
  bottom with clr axial float; jaw flanges ride the tier-2 floor; `check()`
  bounds nose collision (clamp_d ≥ 0.16·jaw_width_B, from the 0.26·B nose at
  120° spacing), tongue engagement (≥ 30 % of jaw length in the guideway) and
  spiral engagement (≥ 2 pitches) — all 12 catalog rows stay feasible over
  the full published A1 range, and at A1 max the jaws overhang the body OD,
  which the catalogue's own ranges imply.

## Mounting holes

The body is tapped: holes cut at the thread minor diameter (0.85·G), blind
from the back (depth min(2.5·G, 0.45·D)); the cover carries clearance holes
(G + max(0.4, 0.05·G)). No false helical detail. Jaw gripping serrations are
two shallow grooves on each vertical gripping face (nose and both risers),
as the BB drawing marks them; groove pitch/depth are proportions.

## Not modelled (visible simplifications)

Involute/octoid flank curvature (planar flanks + backlash instead), thread
flank angle (rectangular section), jaw serration chamfers, cover screws,
pinion retaining details, edge breaks/fillets smaller than the catalogue
resolves.
