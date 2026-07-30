# gusseted_corner_bracket notes

This family models an independent right-angle corner bracket with:

- two perpendicular mounting wings;
- one centered triangular gusset;
- one elongated through-slot in each wing;
- conservative edge rounding / chamfering attempts that never replace the body if a roundover fails.

## Modeling convention

- `X` = width along the common connection edge
- `Y` = first wing length direction
- `Z` = second wing length direction

The part is built as one fused solid from:

- a wing in the `XY` plane;
- a wing in the `XZ` plane;
- a triangular gusset prism centered in `X`.

The slots are cut after fusion so the final body stays single-piece.

## Parameter intent

### Determined mapping

These mappings are taken directly from the `LBSBB8-3030` table row:

- `leg_length_1` -> `L = 28`
- `leg_length_2` -> `H = 35`
- `slot_width` -> `W = 6`
- `bracket_width` -> `W1 = 7.5`
- `gusset_length_1` / `gusset_length_2` -> `A = 13.5` as a shared gusset reach envelope in this implementation
- `gusset_thickness` -> `B = 8`
- `edge_radius` -> `R = 3.5`
- `plate_thickness` -> `T = 4.5`
- `gusset_radius` -> `T1 = 3`

### Tentative mapping

The following are geometric placements that are not uniquely defined by the screenshot/table alone:

- `slot_length`: long-hole total length, chosen to preserve a visible long slot without colliding with the gusset
- `slot_offset_1`, `slot_offset_2`: slot center placements along each wing, chosen so the holes remain inside the wing envelope and outside the gusset

### Notes on geometry

- `leg_length_1` is the horizontal wing extent.
- `leg_length_2` is the vertical wing extent.
- `bracket_width` is kept as the width-direction envelope used by this family implementation.
- The two slots are oriented along their own wing axes: the horizontal wing slot runs along the horizontal wing direction, and the vertical wing slot runs along the vertical wing direction.
