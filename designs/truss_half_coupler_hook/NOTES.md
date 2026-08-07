# truss_half_coupler_hook — source notes (datasheet → design mapping)

Anchor: Doughty T57000/T57010 (standard half coupler), T58080 (slimline),
T58100 (lightweight), T57200 (hook clamp) datasheets; cross-checked against
Riggatec / Global Truss / Kupo equivalents.

## Symbol mapping (Doughty drawing → code)

| Drawing | Meaning | Value / relation | code |
|---|---|---|---|
| Ø48-51 | barrel bore | universal truss/scaff tube | `bore_d` |
| 50 | body width along tube | 30 (slimline) - 51 | `body_w` |
| 55 | tube centre → base | 40-55 across range | `base_drop` |
| Ø12.7 | VERTICAL fixing bore, tang base up into the nut window (front-view hidden lines) | drawing | `hang_d` |
| 19 | tang width across the clamp AND the captive-nut window A/F (17 for M10) | drawing-anchored | `tang_t` / window in build |
| 107 | overall width incl. pin bosses and wing-nut ear | `2 x_h + k_r + e/2` = **106.98** on the anchor; asserted by `check()` | derived |
| ±35.8 | pivot / hinge centres about the bore | measured off the T57000 front view (107 spans 381 px at 3.561 px/mm) | `x_h` |
| 116 / 91 | overall / body height | emerges from ring + lug + nut stack | derived |
| 16 | eye height above base | `1.2 * hang_d` proportion | `z_eye` |

## Assembly (6 solids, contact-or-clearance only)

lower shell (half ring + hinge ears + pivot ears + tang, eye or stud) ·
upper shell (half ring + centre knuckle + slotted crown lug) · hinge pin ·
closing bolt (pivot eye + shank + ring thread) · pivot pin · wing nut.
Clearances: pins 0.15 radial; bolt-slot 0.6 a side; split plane 0.6 a side
(the shells clamp shut on the barrel, which is not part of the family);
nut hovers 0.3 over the lug.

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
- pins Ø `max(5, 0.5 hang_d)`; bolt pivot-eye outer radius `pin_d/2 + 2.4`,
  sized off the pin it swings on (the drawing's pivot circles read ~Ø11 over a
  Ø6.35 pin), not off the thread diameter.

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

1. Drawn closed with the barrel absent, so the shells stand 0.6 mm apart at
   the split; on a real barrel they close metal-to-metal.
2. Ring thread substitutes the helix (framework-wide convention); run-out and
   chamfers on the bolt tip are not modelled.
3. Hinge/pivot pin retention (peening/circlips) is not modelled; pins are
   0.4 short of the body width so the ends sit flush inside the ears.
