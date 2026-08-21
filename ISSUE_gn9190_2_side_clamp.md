# [family-assembly] gn9190_2_side_clamp

Family: `gn9190_2_side_clamp`

Category: `cat:machine-hardware`

Anchor source: [Ganter GN 9190.2 side clamps with clamping thread and support](https://www.ganternorm.com/en/products/2.3-Tensioning-with-eccentric-cams-and-wedge-clamps/Side-Clamps/GN-9190.2-Side-Clamps-Steel-with-Clamping-Thread-and-Support)

Claim it: I can implement this family with CadQuery as a row-locked, five-component parametric assembly.

Done = a parametric family under `designs/gn9190_2_side_clamp/` covering the official 10, 14, and 18 mm GN 9190.2 rows, with E/P jaw variants, G/K operating variants, valid assembly previews, and zero pairwise component interference.

Start here: use the official GN 9190.2 drawing/table for catalog dimensions. The supplied `9190.2-10-M8-E-G.step` is geometry evidence for the housing, pivoted jaw, support block, clamping screw, operating end, holes, reliefs, and local edge treatment; it is not imported by the submitted model.

## Reference Images

| Current assembly preview | STEP-derived component reference |
|---|---|
| <img src="https://github.com/__OWNER__/__REPO__/blob/__BRANCH__/designs/gn9190_2_side_clamp/preview_assembly.png?raw=true" alt="GN 9190.2 parametric assembly preview" width="520"> | <img src="https://github.com/__OWNER__/__REPO__/blob/__BRANCH__/designs/gn9190_2_side_clamp/preview_step_solids.png?raw=true" alt="GN 9190.2 STEP-derived component reference" width="520"> |

| Current component preview | Official-row coverage |
|---|---|
| <img src="https://github.com/__OWNER__/__REPO__/blob/__BRANCH__/designs/gn9190_2_side_clamp/preview_parts.png?raw=true" alt="GN 9190.2 component preview" width="520"> | <img src="https://github.com/__OWNER__/__REPO__/blob/__BRANCH__/designs/gn9190_2_side_clamp/preview_row10.png?raw=true" alt="GN 9190.2 size 10 preview" width="260"><img src="https://github.com/__OWNER__/__REPO__/blob/__BRANCH__/designs/gn9190_2_side_clamp/preview_row14.png?raw=true" alt="GN 9190.2 size 14 preview" width="260"><img src="https://github.com/__OWNER__/__REPO__/blob/__BRANCH__/designs/gn9190_2_side_clamp/preview_row18.png?raw=true" alt="GN 9190.2 size 18 preview" width="260"> |

## Official catalog table

Catalog dimensions are in mm. The table values below are the row-locked dimensions used by the model; `d1`, `d2`, `d3`, `d4`, and `d5` follow the drawing symbols for body, pivot, and clamping features.

| Nominal size | d1 | fs | b1 | b2 | d2 | d3 | d4 | d5 | h1 | h2 | h3 | h4 | l1 | l2 | l3 | l4 | l5 | l6 | s | ma |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 8 | 7 | 32 | 12.1 | 8.4 | 8 | 8 | 4 | 26 | 44 | 28 | 15 | 52 | 28 | 30 | 72.5 | 38 | 63 | 3 | 3 |
| 14 | 12 | 15 | 48 | 16 | 13 | 12 | 12 | 4 | 26 | 53 | 27 | 15 | 72 | 40 | 44 | 100 | 55 | 78 | 4 | 9 |
| 18 | 16 | 21.5 | 68 | 18.8 | 17 | 16 | 16 | 4 | 26 | 72 | 38 | 20 | 86 | 41 | 56 | 126 | 63 | 108 | 7 | 20 |

## Parameter mapping

- `slot_width` selects one official catalog row: 10, 14, or 18 mm. There is no invented continuous size interpolation.
- `jaw_type` selects the E or P jaw geometry. E retains a serrated contact face; P cuts the plain angled contact relief.
- `stroke_coding` selects the G hex-head or K lever-style operating geometry.
- `serration_count` controls the number of contact reliefs on the E jaw.
- `jaw_angle` controls the P contact relief angle in degrees.
- `return_spring_gap` controls the body opening and internal clearance pocket.
- `lever_angle` rotates the pivoted jaw around its hinge datum.
- `body_chamfer`, `body_edge_radius`, `jaw_chamfer`, `jaw_edge_radius`, `support_chamfer`, and `screw_chamfer` control bounded manufacturing edge details and are clamped to local wall thickness.
- `d1` through `d5`, `h1` through `h4`, `l1` through `l6`, `s`, and `ma` are row-coupled catalog values used directly or through clearly documented derived features.

## Geometry and validation

- The result is a named `cq.Assembly` with five declared components: `steel_body`, `pivoted_jaw`, `support_block`, `clamping_screw`, and `operating_end`.
- The 10/E/G reference instance has the STEP envelope convention of approximately `72.5 x 48 x 32 mm` for the body and `52 x 22 x 32 mm` for the jaw.
- The 10/E/G component volumes are approximately 60.0k, 13.2k, and 3.9k mm3 for body, jaw, and support respectively, close to the supplied STEP evidence.
- All 10/14/18 rows and E/P plus G/K combinations produce valid non-degenerate components.
- Pairwise component intersection is `0 mm3` for the sampled rows and variants.

## Constraints

- `slot_width` must be exactly 10, 14, or 18 mm.
- `jaw_type` must be E or P and `stroke_coding` must be G or K.
- `serration_count` must be at least 3; `jaw_angle` is bounded to 30-120 degrees.
- All edge-detail parameters must be non-negative and remain below local wall-thickness limits.
- `lever_angle` is bounded to -35 to 35 degrees so the pivoted jaw remains a valid clearance-fit member.

## Caveats

- Threads, seals, springs, and hidden pneumatic internals are simplified; the visible clamping screw, ball end, pivot holes, support fork, reliefs, and edge treatments are parameterized.
- Fine STEP edge blends that are not dimensioned in the public drawing are documented as proportion-based details through the exposed chamfer/fillet parameters.
- The supplied STEP is used only as geometry evidence and measurement guidance; it is not imported by `part.py`.
