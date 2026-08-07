# truss_half_coupler_hook — source notes (datasheet → design mapping)

Anchor: Doughty T57000/T57010 (standard half coupler), T58080 (slimline),
T58100 (lightweight), T57200 (hook clamp) datasheets; cross-checked against
Riggatec / Global Truss / Kupo equivalents.

## Symbol mapping (Doughty drawing → code)

| Drawing | Meaning | Value / relation | code |
|---|---|---|---|
| Ø48-51 | barrel bore | universal truss/scaff tube | `bore_d` |
| 50 | body width along tube | 30 (slimline) - 51 | `body_w` |
| 55 | tube centre → base face | 40-55 across range | `base_drop` |
| Ø12.7 | VERTICAL fixing bore, base face up into the nut window (front-view hidden lines) | drawing | `hang_d` |
| 16 | depth of that bore, base face up to the window floor | `1.26 * hang_d` = 16.0 at Ø12.7 | derived |
| 19 | captive-nut window width ACROSS the clamp — and therefore the A/F of the M12 nut it traps | drawing | `tang_t` |
| 107 | overall width = left lobe + closure-tab tip | **106.77** measured on the anchor row; asserted by `check()` | derived |
| 116 | overall height = base face to the eyebolt tip, clamp shut | **116.51** measured on the anchor row | derived |

### Front view, measured off the sheet

`docs/assets/refs/truss_half_coupler_hook_drawing.png` was measured against its
own dimensions rather than eyeballed. Scale from the 107 dimension line: it
spans 386 px, i.e. **3.6075 px/mm**; the same scale reproduces the 55 (198.5 px)
and the Ø51 barrel ring, so it is not a one-dimension fit. Origin = the barrel
axis, +X toward the closure tab, +Z up. Readings, and what each drives:

| Feature | Measured (mm) | code |
|---|---|---|
| barrel outer circle | Ø51.0 | `bore_d` |
| body top face | z = **+2.9**, out to x = **±39.7** | `z_top = 0.113 r_i`, `x_sh = 1.557 r_i` |
| hinge / pivot pin centres | x = **-35.5 / +34.1**, z = **-12.0** | `x_pin = 1.337 r_i`, `z_pin = -0.471 r_i` |
| pin lobe (the corner is ROUND, not a fillet) | r ≈ **12.5** about the pin | `r_lobe = 0.490 r_i` |
| widest points of the body | x = **-47.1 / +46.6** at z ≈ -11 | `x_pin + r_lobe` = 46.6 |
| base face | z = **-55.4**, half width **≈ 25.5** | `base_drop`, `w_base = 1.00 r_i` |
| closure-tab tip | x = **+60.1**, nose r ≈ 3 | `x_tab = 2.36 r_i`, `r_nose = 0.11 r_i` |
| closure-tab faces | top z = **+28.6**, underside z = **+15.4** | `z_tab_hi = 1.122 r_i`, `lug_h` ≈ 13 |
| eyebolt shank | two straight lines at x = **+29.1 / +41.4**, i.e. Ø12.3 centred on the pivot | `closing_bolt_d` (M8/M10 declared) |
| captive-nut window | two straight lines at x = **±9.7**, z from **-23.5 to -39** | `tang_t` × `0.82 tang_t` |
| Ø12.7 hidden lines | x = **±6.35**, z from **-39** to the base face | `hang_d` |
| overall dark extent | x **-47.4 … +59.6** (= 107.0), z **-55.4 … +61.5** (= 116.9) | envelope |

Three facts from that table are what the earlier version of this part got
wrong, and they are why it read as a box rather than a clamp:

1. **The two widest points are the pin LOBES, and they sit BELOW the tube
   centre** (z ≈ -12, not 0). The 107 is measured from the left lobe across to
   the closure-tab tip — it is not symmetric about the barrel.
2. **The closure is a cantilevered flat TAB with open air under it**, reaching
   24 mm past the body's own silhouette. The earlier model put a
   30 × 50 × 20 rectangular block there, which is what filled the top of the
   envelope and made the silhouette square.
3. **The body's top face is at z ≈ +2.9**, so the jaw is a deep U open at the
   top and the strap is the only thing over the barrel — not two halves of a
   split ring meeting at z = 0.

The drawn wing nut is NOT orthographically consistent (its hex collar centres
on x ≈ +28.8 while the eyebolt it sits on is at +35.2), so it is treated as a
pictorial symbol and the nut is taken from DIN 315-D instead. The M10 row's
49.5 span ends at x = +58.8 on the anchor row, 1.4 mm inside the tab tip — which
is what makes M10, and not M12, the closure that fits the 107 outline.

## Assembly (6 solids, contact-or-clearance only)

lower shell (the one-piece body: lobed pentagon plate, U-jaw, hinge/pivot
pockets, captive-nut window + Ø12.7 eye, or the M12 stud) · upper shell (the
closure strap: hinge tongue → band over the barrel → flat tab) · hinge pin ·
closing bolt (pivot eye + plain shank + ring thread) · pivot pin · wing nut.

Clearances: pins 0.15 radial; hinge tongue 0.3 a side in its pocket; eyebolt
0.7 a side in the tab slot and in the body's pivot slot; nut 0.3 over the tab.
The strap's left end BEARS on the body's shoulder — that face contact is the
hinge seat and is the only touching pair; every pair still measures zero
intersection volume. Verified across all 24 sampled rows (3 difficulties × 8
seeds): 0 interfering pairs.

## Hardware derivation (constants, not sampled)

- closing bolt nominal = `closing_bolt_d`, a parameter in its own right. It is
  NOT derived from `hang_d`: the datasheet lists the base fixing ("integral flat
  boss drilled Ø12.7 with a hex slot for a captive M10/M12 nut") and the closure
  ("a swing-away Grade 8.8 eyebolt and wing nut") as separate fasteners. The
  earlier `hang_d - 0.7` conflation sized the eyebolt M12 and, once a real
  DIN 315-D wing nut went on it, measured 114 mm across a 107 mm outline.
  M8/M10 only — see the spec note on why M12 is not a declared value.
- ISO 261 coarse pitch by nominal (M8 1.25, M10 1.5, M12 1.75).
- Thread = axisymmetric ring stacks (no helix): bolt rings root→crest
  `bolt_d/2 - 0.61 p → bolt_d/2`, width `0.4 p`, one per pitch; the nut's
  internal rings sit on the SAME z-grid offset half a pitch, radially nested
  0.25 p past the bolt crest — engaged, with 0.1 p axial gaps, so the pair
  measures zero intersection volume.
- pins Ø `max(5, 0.5 hang_d)`; bolt pivot-eye outer radius
  `pin_d/2 + 0.26 bolt_d + 1.4`, sized off the pin it swings on (the drawing's
  pivot circles read ~Ø11 over a Ø6.35 pin), not off the thread diameter.

### Wing nut — DIN 315 form D (symbol → code)

The datasheet's front view — the one carrying the 107 — shows the wings splayed
**in that plane** over a hex-to-round boss; the side view shows only a narrow
rib. So the wings lie in XZ, across the clamp, not along the tube axis.

| DIN 315-D | meaning | code |
|---|---|---|
| d1 | nominal thread | `closing_bolt_d` |
| d2 / d3 | boss Ø at the bearing face / at the top of the taper | `_din315d()` row |
| m | boss height | `m_boss` |
| e | span over the wing tips (M10: 48-51; drawing scales to ~47.7) | `e_span` |
| h | overall height, bearing face to the top of the wings | `h_nut` |
| g2 / g1 | wing thickness at the root / at the ear | `g2` / `g1` |
| r1 | ear (wing-tip lobe) radius | `ear_r1` |
| r4 | concave underside radius | `under_r4` |

Rows are the DIN 315-D mid-band, scaled linearly to the actual thread Ø so the
nut still fits a non-tabulated bolt.

## Deliberate deviations / simplifications

1. Drawn closed with the barrel absent. The sheet's own outline leaves the
   barrel exposed in two gaps — upper right, where the eyebolt crosses, and a
   narrow one upper left — so the strap is not modelled as closing onto the
   body anywhere except its hinge seat.
2. Ring thread substitutes the helix (framework-wide convention); run-out and
   chamfers on the bolt tip are not modelled.
3. Hinge/pivot pin retention (the drawing shows split roll pins) is not
   modelled; pins are plain cylinders 0.4 short of the body width so the ends
   sit flush inside the ears.
4. The body is modelled as a plane-faced extrusion. The real casting has
   chamfered outer edges and a relieved front face; neither is modelled.
5. The body outline scales with `bore_d`, so the 107 is reproduced at Ø51 and
   falls to ~100.5 at Ø48. The real clamp is one casting across the whole
   48-51 range; scaling it is a benchmark-variation choice, not a catalog
   claim, and `check()` bounds the result to 96-110.
