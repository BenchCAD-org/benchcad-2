# gusseted_corner_bracket notes

This family models a generic self-contained 90-degree gusseted corner bracket
for aluminum-frame benchmark work. The default no-hole configuration matches
the validated round24 reference geometry; enabling `panel_mount_holes` matches
the validated round25 optional side-panel-hole configuration.

The model does not load STEP, BREP, round directories, preview images, or any
absolute-path geometry at build time.

## Coordinate convention

- `X` = overall width across the two outer side panels.
- `Y` = horizontal mounting-plate length direction.
- `Z` = vertical mounting-plate height direction.

## Constructed features

- central L-shaped body made from the horizontal and vertical mounting plates;
- left and right stepped side panels with the validated sloped profile and R2
  outer corner transitions;
- four small locator tabs on the bottom and rear mounting faces;
- paired analytic rounded central openings on the horizontal and vertical
  plates;
- optional coaxial M5 tap-drill holes through the two side panels only.

## Public parameters

The product identity is generic. The exposed dimensions default to the
validated benchmark geometry and use safe engineering-proportion ranges for
benchmark variation.

Background reference consulted during development:

- [commercial product page](https://www.misumi.com.cn/vona2/detail/110310404279/)

| Code parameter | Factory symbol | Default | Unit/type | Controls |
|---|---:|---:|---|---|
| `overall_width` | `L` | 28.0 | mm | total X width across both side panels |
| `slot_width` | `W` | 6.0 | mm | central rounded-opening width and locator-tab X width |
| `side_step` | `W1` | 7.5 | mm | side-panel top/lower step dimensions |
| `overall_height` | `H` | 35.0 | mm | side-profile Y/Z extent and mounting-plate length/height |
| `opening_offset` | `A` | 13.5 | mm | lower datum for the paired rounded central openings |
| `opening_spacing` | `B` | 8.0 | mm | spacing between paired rounded central-opening centers |
| `opening_radius` | `R` | 3.5 | mm | larger central-opening arc radius |
| `plate_thickness` | `T` | 4.5 | mm | horizontal and vertical mounting-plate thickness |
| `side_thickness` | `T1` | 3.0 | mm | thickness of each side panel along X |
| `panel_mount_holes` | optional machining | False | bool | toggles the pair of coaxial side-panel holes |

The optional side-panel holes use the validated round25 M5 tap-drill geometry:
diameter 4.2 mm, centers at the 12 mm by 12 mm side-panel location, and axes
parallel to X. Hole diameter and placement are intentionally not public
parameters because the task reference only confirmed the standard optional
machining location.

## Difficulty presets

- `easy`: near-default no-hole baseline (`panel_mount_holes=False`).
- `medium`: near-default part with the side-panel holes enabled.
- `hard`: side-panel holes enabled plus wider legal variation of the exposed
  dimensions.

All presets are expected to build as one valid, closed, non-degenerate solid.
