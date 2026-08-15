# GN 866 pneumatic power clamp — catalog mapping and deviations

## Catalog symbol → code

`spec.py:OFFICIAL_ROWS` contains the three discrete Ganter rows (sizes 20,
32, and 40). `refine()` locks every sampled instance to the selected row;
only the published `l1` / `l2` minus tolerance varies within a row.

| Drawing/table symbol | Code parameter | Geometry use |
|---|---|---|
| size | `size` | selects the official 20 / 32 / 40 row; also sets small STEP-derived detail proportions |
| max. moment | `max_moment` | catalog metadata in N·m; no geometric effect |
| Fs / Fh | `fs`, `fh` | catalog force metadata in N; no geometric effect |
| a / b | `a`, `b` | paired gripper width and opening-position references |
| d1 | `d1` | pneumatic cylinder/body diameter and gripper bore depth reference |
| d2 / d3 | `d2`, `d3` | small and stepped transverse bores in the body and grippers |
| d4 | `d4` | lower stepped-bore diameter |
| d5 | `d5_major` | pneumatic-port thread major diameter; represented as a plain shallow bore |
| l1 | `l1` | body length before the shared minus tolerance |
| l2 | `l2` | complete assembly envelope before the shared minus tolerance |
| l3 | `l3` | cylinder length and gripper-span reference |
| l4 | `l4` | lower body-block length |
| l5 | `l5` | side-cover thickness/detail reference |
| l6 | `l6` | catalog head-span input; retained in the build contract while the outer head profile follows `l1 - l3` |
| m1 / m2 | `m1`, `m2` | two upper gripper-bore positions |
| m3 | `m3` | lower body-bore pitch |
| m4 | `m4` | upper body-window/bore-region reference; the size-20 table has no value and uses 0 |
| m5 | `m5` | transverse lower-bore offset |
| m6 | `m6` | pneumatic-port spacing |
| r | `r` | catalog force reference radius; metadata only because the mechanism is shown in one clamped pose |
| s1 / s2 | `s1`, `s2` | body width and overall depth |
| t | `t` | gripper/bridge plate thickness |
| w | `w` | catalog clamping-arm angle in degrees; pose metadata only in the fixed assembly representation |

## STEP-derived geometry

The supplied manufacturer STEP is used only as a visual and dimensional
reference. The submitted model is rebuilt with CadQuery primitives and does
not import STEP at build time. The size-20 shoulder stations, taper ratios,
side-cover placement, gripper outline points, small fillets, and hidden mating
clearances are STEP-derived. For sizes 32 and 40, dimensionless local ratios
are retained where the public catalog does not fully define a transition, but
principal envelope and bore dimensions come from their own official catalog
rows; the family does not uniformly scale the size-20 row.

The STEP separates into a main body and two mirrored grippers. `build()` keeps
three solids and removes only hidden mating overlap. At official size 20 the
pairwise intersection volumes are 0 mm³ and the visible envelope remains
approximately 32.2 × 160.0 × 37.3 mm versus the catalog 32 × 160 × 38 mm.

## Intentional simplifications

- `max_moment`, `fs`, `fh`, and `r` describe performance and therefore do not
  change solid geometry.
- The delivered family represents one fixed assembled/clamped pose. `w` is
  documented as pose metadata rather than rotating the grippers away from the
  STEP reference pose.
- `l6` is not used as an independent outer-envelope length because its catalog
  behavior is not consistent with that interpretation across the three rows;
  the visible head length is derived from `l1 - l3`, matching the STEP pose.
- Pneumatic threads, internal linkage, seals, fasteners, engraving, and very
  small edge breaks are omitted. Thread sizes are represented by plain bores.
- The shared `length_tolerance` applies the drawing's 0 / −0.5 mm allowance to
  `l1` and `l2` only.
