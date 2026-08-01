# gusseted_corner_bracket notes

This family models the single `LBSBB 8-3030` right-angle corner bracket only:

- two perpendicular mounting wings;
- one centered triangular gusset;
- one elongated through-slot in each wing;
- an optional pair of mounting holes on the two triangular side panels.

The implementation is fully self-contained CadQuery geometry. It does not load
or depend on any STEP, BREP, round directory, or local absolute path at build
time.

## Modeling convention

- `X` = width along the shared connection edge
- `Y` = first mounting wing length direction
- `Z` = second mounting wing length direction

The part is built as one fused solid from a wing in the `XY` plane, a wing in the `XZ` plane, and a centered triangular gusset prism. The slots are cut after fusion so the final body stays single-piece.

## Parameter intent

### Fixed product identity

The family targets the single product line `LBSBB 8-3030`:

- `Type = LBSBB`
- `No. = 8-3030`
- `3030` profile size

These fields identify the product family. The geometric dimensions below are exposed as adjustable parameters with the listed defaults and safe ranges.

### Geometry mapping

The drawing/table values used by this family are:

- `leg_length_1` -> `L = 28` (adjustable family parameter)
- `leg_length_2` -> `H = 35` (adjustable family parameter)
- `bracket_width` -> overall width span centered on `x = 0` (adjustable family parameter)
- `plate_thickness` -> `T = 4.5` (adjustable family parameter)
- `gusset_thickness` -> `T1 = 3` (adjustable family parameter)
- `gusset_length_1` / `gusset_length_2` -> local gusset reach derived from `A = 13.5` (adjustable family parameters)
- `slot_width` -> `W = 6` (adjustable family parameter)
- `slot_length` -> `A = 13.5` (adjustable family parameter)
- `slot_offset_1` / `slot_offset_2` -> `B`-related slot placement controls (adjustable family parameters)
- `edge_radius` -> `R = 3.5` (adjustable family parameter)
- `panel_mount_holes` -> optional on/off switch for the pair of side-panel installation holes
- `panel_hole_offset` -> shared placement control for the optional side-panel holes
- `panel_hole_diameter` -> optional side-panel hole diameter, defaulting to the M5 clearance size

### Tentative mapping

The screenshot does not uniquely pin down every placement dimension, so these remain implementation choices constrained by the drawing and the validated geometry:

- `slot_length` -> long-hole total length, defaulting to `13.5`
- `slot_offset_1`, `slot_offset_2` -> slot center placements along each wing, chosen to keep both slots inside the wing outline and clear of the gusset
- `panel_hole_offset` -> shared placement control for the optional panel holes, chosen to keep both holes inside their faces and away from slots, fillets, and internal cavities
- `panel_hole_diameter` -> M5-style clearance hole diameter, defaulting to `4.2`

### Geometry notes

- `X` is the width direction and is symmetric about `x = 0`.
- `Y` is the first wing direction.
- `Z` is the second wing direction.
- The bracket is built from two fused rectangular wings plus one local triangular gusset prism.
- Each slot is cut in its own wing-local plane so the long axis follows that wing's direction.
- When `panel_mount_holes` is enabled, the two additional holes are standard M5 clearance through-holes on the two triangular side panels; they are coordinated by `panel_hole_offset` and `panel_hole_diameter`, and must not intersect the long slots, gusset, or central cavities.
