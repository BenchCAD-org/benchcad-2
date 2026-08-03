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
| 107 | overall width incl. pin bosses | emerges from `x_h = r_out + max(2.2 k_r, r_eye + 1.5)` | derived |
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

- closing bolt nominal = `hang_d - 0.7` (clearance-bore convention: Ø12.7 → M12,
  Ø10.5 → M10); ISO 261 coarse pitch (1.75 above Ø11, else 1.5).
- Thread = axisymmetric ring stacks (no helix): bolt rings root→crest
  `bolt_d/2 - 0.61 p → bolt_d/2`, width `0.4 p`, one per pitch; the nut's
  internal rings sit on the SAME z-grid offset half a pitch, radially nested
  0.25 p past the bolt crest — engaged, with 0.1 p axial gaps, so the pair
  measures zero intersection volume.
- pins Ø `max(5, 0.5 hang_d)`; wing nut DIN 315 proportions (hub 1.8 d,
  wings ~4.5 d span, height ~2 d) — shape anchor, dimensions `proportion`.

## Deliberate deviations / simplifications

1. Drawn closed with the barrel absent, so the shells stand 0.6 mm apart at
   the split; on a real barrel they close metal-to-metal.
2. Ring thread substitutes the helix (framework-wide convention); run-out and
   chamfers on the bolt tip are not modelled.
3. Hinge/pivot pin retention (peening/circlips) is not modelled; pins are
   0.4 short of the body width so the ends sit flush inside the ears.
