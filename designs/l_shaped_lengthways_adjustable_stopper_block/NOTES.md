# L-shaped lengthways-adjustable stopper block notes

## Source

MISUMI, *Threaded Stopper Blocks — L-Shaped, T-Shaped, Side Counterbored,
Two-Hole*, 2019 US catalog, p. 1700:

https://us.misumi-ec.com/pdf/fa/2019/2019_US_1700.pdf

The modeled product family is the L-shaped **Lengthways Adjustable Type**
(AJLTT/AJLTTM/AJLTTS coarse-thread and AJLSTT/AJLSTTM fine-thread series).
Material and finish variants are geometrically equivalent and are not sampled.

## Drawing-symbol mapping

| Drawing symbol | Parameter | Interpretation |
|---|---|---|
| M | `thread_nominal_d_M` | Nominal diameter of the horizontal threaded hole |
| H | `thread_axis_height_H` | Height from the base underside to the threaded-hole axis |
| H1 | `top_margin_H1` | Margin from the threaded-hole axis to the upright top |
| T1 | `transverse_width_T1` | Full transverse width of the body |
| W1 | `upright_length_W1` | Upright thickness along the base length |
| L1 | `base_length_L1` | Overall base length |
| S | `base_thickness_S` | Base thickness |
| P | `mount_hole_pitch_P` | Mounting-hole center distance |
| G1 | `first_hole_offset_G1` | Upright outer end to first mounting-hole center |
| d1 | `counterbore_diameter_d1` | Counterbore diameter |
| d2 | `through_hole_diameter_d2` | Mounting through-hole diameter |
| l | `counterbore_depth_l` | Counterbore depth from the base top |
| C | `top_chamfer_C` | Chamfer size; drawing callout is 2-C2 |
| R | `internal_fillet_R` | Internal upright/base junction radius |

The drawing dimensions H from the underside datum to the hole axis and H1
from the axis to the top. Therefore the modeled overall height is `H + H1`.

## Catalog grouping and coupling

The table merges M sizes into four geometric groups:

| Nominal M | Permitted H | H1 | T1 | W1 | L1 | S | P | G1 | d1 | d2 | l |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3, 4 | 15, 20 | 4 | 9 | 5 | 25 | 6 | 10 | 10 | 6.5 | 3.5 | 3.5 |
| 5, 6 | 15, 20 | 6 | 12 | 8 | 32 | 8 | 10 | 15 | 8 | 4.5 | 4.5 |
| 8, 10, 12 | 25, 30, 35 | 10 | 22 | 10 | 44 | 10 | 16 | 20 | 11 | 6.5 | 6.5 |
| 16, 20 | 35, 40 | 15 | 30 | 15 | 65 | 15 | 30 | 25 | 14 | 9 | 9 |

`spec.py` samples only nominal M. `refine()` then selects H from the values
permitted for that M group and copies every remaining dimension from the same
group. Dimensions are never independently mixed across catalog groups.

## Deliberate modeling conventions

- The catalog specifies a threaded M hole, but this family intentionally uses
  a cylindrical through bore of nominal diameter M. Coarse/fine pitch and
  explicit helical thread geometry are excluded from the family scope.
- The drawing calls out the internal corner as **R2 or less**, which is an
  upper bound rather than an exact radius. The model uses a fixed **R1.5 mm**
  convention, chosen within the manufacturer's R <= 2 mm bound. R1.5 is not
  claimed to be an exact catalog dimension.
- Both chamfers in the drawing callout **2-C2** are modeled at exactly 2 mm.
