# gusseted_corner_bracket notes

This family models the single `LBSBB 8-3030` right-angle corner bracket only:

- two perpendicular mounting wings;
- one centered triangular gusset;
- one elongated through-slot in each wing;
- an optional pair of mounting holes on the two triangular side panels.

The validated no-hole baseline matches `round24`, and the optional side-panel hole variant matches `round25`.

## Modeling convention

- `X` = width along the shared connection edge
- `Y` = first mounting wing length direction
- `Z` = second mounting wing length direction

The part is maintained as a single validated reference body with optional slot and side-panel-hole adjustments applied parametrically.

## Parameter intent

### Confirmed mapping

The drawing/table values used by this family are:

- `leg_length_1` -> `L = 28`
- `leg_length_2` -> `H = 35`
- `slot_width` -> `W = 6`
- `bracket_width` -> overall width span centered on `x = 0`, also `28` in this implementation
- `gusset_length_1` / `gusset_length_2` -> local gusset reach derived from `A = 13.5`
- `gusset_thickness` -> `T1 = 3`
- `edge_radius` -> `R = 3.5`
- `plate_thickness` -> `T = 4.5`
- `panel_mount_holes` -> optional on/off switch for the pair of side-panel installation holes

### Tentative mapping

The screenshot does not uniquely pin down every placement dimension, so these remain implementation choices constrained by the drawing and the validated geometry:

- `slot_length` -> long-hole total length, taken as `13.5`
- `slot_offset_1`, `slot_offset_2` -> slot center placements along each wing, chosen to keep both slots inside the wing outline and clear of the gusset
- `panel_hole_offset` -> shared placement control for the optional side-panel holes, chosen to keep both holes inside their faces and away from slots, fillets, and internal cavities

### Geometry notes

- `X` is the width direction and is symmetric about `x = 0`.
- `Y` is the first wing direction.
- `Z` is the second wing direction.
- The bracket is built from two fused rectangular wings plus one local triangular gusset prism.
- Each slot is cut in its own wing-local plane so the long axis follows that wing's direction.
- When `panel_mount_holes` is enabled, the two additional holes are standard 4.2 mm through-holes on the two triangular side panels; they are coordinated by the single `panel_hole_offset` parameter and must not intersect the long slots, gusset, or central cavities.
