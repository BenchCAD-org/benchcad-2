# Minifix cam housing: reference-based reconstruction

## Evidence and identity

This revision replaces the stored contour stack with analytic CadQuery features.
It addresses [issue #25](https://github.com/BenchCAD-org/benchcad-2/issues/25),
which was previously closed through PR #34 and subsequently patched in PR #223.

The geometry reference was supplied by the user as `minifiks kilidi.SLDPRT`.
Its SHA-256 is
`1dc6a51a00041a4bc87b38df3100b314283cc55bad1f359ca402a4d8329f3e37`.
The preceding search identified the same filename on
[GrabCAD: minifix lock](https://grabcad.com/library/minifix-lock-1).
The file's manufacturer and catalogue SKU are **not verified**. It is not
described here as original Hafele CAD. The original family credit is retained.

The reference was inspected in SOLIDWORKS 2023 SP5 (31.5.0) on 2026-09-10.
It contains an imported base body and a subsequent 0.2 mm marking cut;
there is no recoverable feature history for its main body. A STEP copy was
exported with the original native path unchanged. The exported solid has
318 faces, one valid solid and volume 707.428651 mm3. No source BREP, STEP,
SLDPRT, mesh or sampled contour data is embedded in `part.py`.

Installation dimensions were rechecked against the actual PDF pages:

- [Hafele UK 2014 catalogue p. 294, unrimmed](https://files.hafele.co.uk/catalogfiles/www/14CFC294.pdf)
- [Hafele UK 2014 catalogue p. 295, rimmed](https://files.hafele.co.uk/catalogfiles/www/14CFC295.pdf)
- [Original issue's product anchor](https://www.hafele.com/us/en/product/connector-housing-minifix-15/P-00861332/)

## Catalogue rows and units

All lengths below are millimetres. X is the panel **bore depth**, not a binding
casting dimension. The table specifies a 15 mm housing bore for every row.
The edge bore for a mating bolt is 7 or 8 mm according to the selected bolt.
That panel hole is not the diameter of the head or neck inside the cam.
Consequently it does not drive an arbitrary cut through this part.

| Index | Example article | Panel t | Axis A | Bore X | Rim diameter x height |
|---|---|---:|---:|---:|---|
| 0 | 262.25.070 | 12 | 6 | 9.5 | 16.5 x 1 |
| 1 | 262.26.032 | 15 | 7.5 | 12 | none |
| 2 | 262.25.212 | 16 | 8 | 12.5 | 16.5 x 1 |
| 3 | 262.25.221 | 19 | 9.5 | 14.5 | 16.5 x 1 |
| 4 | 262.25.669 | 23 | 11.5 | 16.5 | 16.5 x 1 |
| 5 | 262.26.291 | 29 | 14.5 | 19.5 | none |
| 6 | 262.25.081 | 34 | 17 | 22.5 | 16.5 x 1 |
| 7 | 262.26.034 | 18 | 9 | 13.5 | none |

Rows 0-6 retain the issue's indices. Row 7 is added because the supplied
unrimmed model has casting height 13.5 and top-to-slot-axis distance 9.0.
Those dimensions match this **installation row**; they do not establish its SKU.
The page-295 prose mentions 29 mm in one heading while its order table lists
23 mm; this family follows the explicit 23 / 11.5 / 16.5 order-table row.

Two independent endpoint spot-checks: row 0 has `A=12/2=6`, `t-X=2.5`,
`X-A=3.5`; row 6 has `A=34/2=17`, `t-X=11.5`, `X-A=5.5`.
The source specifies X +/-0.2 on row 0 and X +0.5 on the other selected rows.
The catalogue calls its dimensions non-binding nominal data.

## Datum and feature mapping

The output seating face is z=0. The casting occupies `-housing_height..0`;
an optional rim occupies `0..rim_height`. The bolt axis is at
`z=-bolt_axis_height`. The reference's original bottom datum was z=0 with
its top at z=13.5; subtract 13.5 from its Z coordinates to compare the two.

Inside `build()`, features are constructed from the bottom up and translated
to the seating datum once at the end. Let `H=housing_height`, `A=bolt_axis_height`
and `c=H-A`:

| Physical feature | Reference / formula in the build | Evidence |
|---|---|---|
| Casting outside diameter | 14.8; R7.4 cylindrical surface | native measurement |
| Model height H | nominal bore X | proportion anchored by reference H=13.5=X |
| Cam slot centre | c; 4.5 at baseline | reference R1.5 cylinder at z=4.5 |
| Closed end of radial slot | x=2.1, radius `neck_slot_width/2` | reference cylindrical face |
| Bolt-head bowl | sphere R3 at (0,0,c), reduced to c-0.7 for shortest row | spherical fit / proportion |
| Upper jaw / rib start | c+2.583 | reference plane z=7.082962 |
| Top cap underside | H-0.8 | reference plane z=12.7 |
| X-directed straight web | y=-1..0; 1 mm nominal thickness | reference y=-1 and y=0 planes |
| Y-directed straight web | x=3.705..4.4; thickness 0.695 | measured reference planes |
| Drive cup start | c+3.2 | reference front underside z=7.7 |
| Drive cup outline | R2.8 core, full Y arm and front half of X arm; 2.8-wide arms reaching 4.4, end radii 1 | cylindrical/planar face census and XY section at z=9 |
| Blind cross drive | R2 core, 1.2-wide arms reaching 3.6 | reference R2 and y=+/-0.6 walls |
| Cast edge / root blends | R0.25 at jaw edges, cage windows, web ends, cup underside, drive mouth and floor | reference cylindrical blend faces, e.g. 13-27, 121-125, 172-193, 194-214 and 256-264 |
| Jaw-tip inner flanks | right x=5.4785+0.491y; left x=-5.1517-0.109y, clipped by R7.4 | rounded measurements from reference planes 235 and 130/223 |
| Drive floor | 0.8 above cup start; depth A-4 | reference floor z=8.5; cross-row proportion |
| Direction markings | clockwise from +Z; R6.5 / R5.38 arcs, 0.6 shoulders, 140-degree tail; recessed 0.2 | exact native Sketch1 / Cut-Extrude1 pocket boundaries |
| Optional flange | supplied rim diameter / height | catalogue p. 295; absent from native reference |

The two support ribs follow the Cartesian X and Y directions. The Y rib is
offset to x=3.7053369..4.4; neither rib is generated by a polar pattern or aimed
at the cylinder centre. Straight web solids define the material retained between
window cutters; the cylinder trims their ends. Rounding the window cutters gives
continuous R0.25 roots at both the jaw roof and cap. Exposed web ends, cap
underside and cup underside are then filleted by their geometric locations.
The back of the X web meets the R2.8 cup directly, with R0.25 junctions;
the horizontal cup arm does not project behind the web's y=-thickness face.

The left jaw-tip slot edges follow `c +/- neck_slot_width/2`, keeping them
flush with the slot through the exploratory width range. At baseline the lower
tip starts at c-2.5 and the upper tip extends to the modeled roof. The right tip
is 1.5 high. Jaw tips are merged before edge filleting to avoid artificial seams.
Drive-mouth and drive-floor blends are R0.25; the top external circle and the
0.2-deep markings retain their reference sharp boundaries. An optional catalogue
rim has no supplied shape reference and is modeled with sharp outer edges.

`rim_diameter` and `rim_height` now both affect actual geometry.
`body_diameter` now means casting diameter; `housing_bore_diameter` separately
records the required 15 mm panel bore. The 0.2 mm diametral difference is a
reference observation, not a prescribed production tolerance.

## Variation and constraints

Easy uses the measured 18 mm baseline with no markings. Medium varies five
installation rows and adds markings; hard includes all eight rows and the
12 / 34 mm panel extremes. `web_thickness` varies 0.85-1.15 and
`neck_slot_width` varies 2.8-3.2 in hard. Those are explicitly labelled
exploratory proportions around measured 1.0 / 3.0 values, not catalogue options.

`check()` enforces complete catalogue rows, A=t/2, a minimum 2 mm panel floor,
the X-A envelope 3.5-5.5, flange overhang, reference-based web/slot bounds,
at least 1.8 mm lower jaw below the slot and at least 2.5 mm cage support
between the jaw roof and the cap. These geometric margins are proportions;
they are not presented as a load-rating standard. The blind-drive floor remains
0.8 mm even on the tallest row. The result must always contain exactly one solid.

The build has no I/O, random numbers, exception suppression, skipped faces,
substitute boxes, face census, polygon fitting or topology reconstruction.
Helpers only construct ordinary analytic features from the named parameters.

## Deliberate approximations

- Cross-SKU internal shapes are reference-based extrapolations. Only the
  supplied unrimmed 18 mm installation baseline has a measured shape reference.
- The jaw-tip inner flanks use measured planes and a cylindrical outer envelope;
  the small draft slopes and spline transitions remain simplified. The upper
  tip ends at the common modeled roof c+2.583 rather than the reference's c+2.5
  front plane. Main cast blends are now R0.25, including the web roots, exposed
  edges and blind-drive mouth/floor; these do not reproduce every imported
  spline patch of the source.
- The bolt-head bowl is a spherical approximation to the reference spline
  surface. The cross drive is a measured geometric approximation, not a certified
  ISO PZ2/PZ3 or SW4 tool profile. A separate SW4 hex socket is not claimed.
- The marking outline is reconstructed analytically from the exact reference
  pocket edges, including the right-hand clockwise tip and the separate
  negative-Y pointer. Markings are omitted only in the easy tier.
- The catalogue's installation tolerances and mechanical locking forces are
  not simulated. Geometry validity and reference agreement do not establish
  production interchangeability or a load rating.

## Verification record

Local verification compares all eight catalogue rows at the four combinations
of hard web/slot limits, checks one valid solid and exact seating/envelope datums,
and checks that deliberately wrong catalogue/geometry inputs are rejected.
The normal `bench2 validate` and `bench2 preview` commands supply the repository
gates and the four preview artifacts. Reference checks compare arrow/pointer
pocket outlines, X/Y rib planes, blend radii, mass properties and side-by-side
views in the same coordinate frame. Mass difference is not geometric overlap.
Boolean intersection with the imported spline body did not provide a reliable
valid common solid, so no 3D overlap percentage is claimed.

The 2026-09-10 local checks passed all 32 row/web/slot boundary combinations,
including exact Z envelopes and one valid solid, and rejected nine deliberately
incorrect inputs. Arrow and pointer planar symmetric differences were both
0 mm2 (maximum matched-vertex distance below 4e-14 mm). Four source/rebuilt
web-plane checks confirmed the X/Y directions. Seven blend zones contained
measured R0.25 cylinders in both models. The marked 18 mm baseline has volume
716.909336 mm3 versus reference 707.428651 mm3 (+1.340%); remaining differences
include the spherical seat approximation and the simplified cast draft/tips.
The user approved proceeding to PR publication after the local preview review.
The family package contains the four standard previews. Additional source
overlays and explicit 12 / 34 mm catalogue endpoint views were used for local
review and retained outside the submitted package, as the repository requires.

The standard preview command's aggregate extrema select rows 1 and 6; local
checks additionally cover the actual shortest row 0. The shared hard-zoom preset
labelled "top" looks from -Z for this part; arrow direction was checked from +Z
using the measured pocket outlines and a separate local top view. No shared
renderer changes are included in this family revision.
