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

- Threads are represented as clean cylindrical holes; helical thread geometry is omitted.
- Small edge chamfers and shallow screw-side recesses are computed internally from catalog dimensions because the table does not publish separate values for these minor manufacturing details.
- The catalog note for d1 > 70 mm is represented by a second radial screw hole/recess at 135 degrees using the same d3 dimensions as the main screw.
- Material and finish variants are metadata-only; they do not alter geometry.
