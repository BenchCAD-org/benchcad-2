# set_screw_shaft_collar Notes

## Sources

- JW Winco, "GN 705 Set Screw Shaft Collars, Steel / Stainless Steel, Metric":
  https://www.jwwinco.com/en-us/products/3.2-Mounting-Positioning-Leveling-with-Retaining-Cables-Screws-Clamping-and-Supporting-Elements/Shaft-Collars/GN-705-Steel-Set-Collars-Zinc-Plated
- Downloaded standard sheet:
  `gn705_standard_sheet.pdf`
- Downloaded engineering drawing:
  `gn705_engineering_drawing.svg`
- Downloaded product photo:
  `gn705_product_photo.jpg`

## Symbol Mapping

| Source symbol | Model parameter | Meaning |
|---|---|---|
| d1 H8 | `bore_d` | Shaft bore diameter |
| d2 | `outer_d` | Outside collar diameter |
| d3 | `screw_d`, `screw_len` | Set screw nominal thread and length |
| b js14 | `width` | Axial collar width |
| catalog note | `second_screw` | Second set screw at 135 degrees for d1 > 70 mm |

## Catalog Rows Used

The spec uses discrete catalog rows so generated dimensions remain table-based.

| d1 | d2 | d3 | b |
|---:|---:|---:|---:|
| 5 | 10 | M3 x 4 | 6 |
| 6 | 12 | M4 x 5 | 8 |
| 8 | 16 | M4 x 6 | 8 |
| 10 | 20 | M5 x 8 | 10 |
| 12 | 22 | M6 x 8 | 12 |
| 16 | 28 | M6 x 8 | 12 |
| 20 | 32 | M6 x 8 | 14 |
| 24 | 40 | M8 x 12 | 16 |
| 30 | 45 | M8 x 10 | 16 |
| 35 | 56 | M8 x 12 | 16 |
| 40 | 63 | M10 x 16 | 18 |
| 50 | 80 | M10 x 16 | 18 |
| 60 | 90 | M10 x 16 | 20 |
| 70 | 100 | M10 x 20 | 20 |
| 80 | 110 | M12 x 20 | 22 |

## Deliberate Deviations

- The set screw hole carries a MODELLED internal metric thread: drilled to the ISO
  internal-thread minor diameter (d - 1.0825*P) and threaded out to the major
  diameter with 60-degree V-rings of the ISO 261 coarse pitch — crest flat P/4 at
  the minor Ø, root flat P/8 at the major Ø, depth 0.5413*P. `screw_d` runs M3
  through M12 over the catalog rows (P = 0.5 to 1.75 mm), so the thread is the
  family's functional feature, not a cosmetic one.
- BOTH mouths are countersunk at 45 degrees out to the major Ø plus a tenth of a
  pitch. A tapped hole needs the lead-in to start the screw, and without it the
  first turn of thread is left as a knife edge on the face it breaks — here the
  OD, where the screw enters, and the bore, where the hole breaks into the shaft
  seat. Full threads run between the two countersinks: 3 turns on the M3 row up
  to 8 on the M10 rows.
- Those are revolved RINGS, not a swept helix, and they differ from a real thread
  only in lead: each turn closes on itself instead of advancing by P. A helix was
  tried first and its boolean cut silently no-ops below M10 — on the ten rows from
  M3 to M8 the groove solid comes out correct (right radius, right length, sane
  volume) and the cut removes 0.0 mm³, leaving a smooth hole that still passes
  every gate. `knurled_thumb_screw_din464` records the same failure on its M6 and
  M8 rows and takes the same way out.
- Small edge chamfers are computed internally from catalog dimensions because the
  table does not publish separate values for them.
- There is NO spotface on the outside diameter. GN 705 dimensions exactly four
  things — d1, d2, d3 and b — and d3 is the set screw itself (e.g. "M8 x 12").
  Both catalog types take a HEADLESS screw (Type A slotted cone-point ISO 7434,
  Type E hex socket cone-point DIN 914) which seats entirely inside the tapped
  hole, so there is nothing for a recess in the OD to clear. An earlier revision
  sank one anyway, `screw_d * 1.45` across and
  `min(1.2, max(0.35, screw_len * 0.12))` deep — both invented.
- The catalog note for d1 > 70 mm is represented by a second radial tapped hole at
  135 degrees using the same d3 dimensions as the main screw.
- Material and finish variants are metadata-only; they do not alter geometry.
