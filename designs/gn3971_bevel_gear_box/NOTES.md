# GN 3971 bevel gear box - sources and derivations

## Primary evidence

- Ganter GN 3971 product page: housing Aluminum, Types L/T, product photos.
- Ganter GN 3971 standard sheet, PDF page 1: orthographic/section drawings and
  the `b1` through `t2` dimension table.
- Ganter GN 3971 standard sheet, PDF page 2: mounting-interface drawings and
  the `d4` through `m5` table.
- Ganter GN 3971 standard sheet, PDF page 3: 1:1 ratio, `3 +/- 0.5 deg`
  circumferential backlash, and unrestricted shaft rotation direction.
- Ganter DIN 6885-1 keyway extract: parallel-key radial arrangement.  The GN
  3971 sheet explicitly marks the Type-L, `b1=24`, `b2=4` row as deviating
  from DIN 6885-1; the catalog value is retained verbatim.

GN 3971 source links:

- https://www.ganternorm.com/en/products/3.6-Moving-Transferring-Connecting-with-Joints-Couplings-and-Gears/Gears/GN-3971-Bevel-Gear-Boxes-Housing-Aluminum
- https://live-katalog.ganternorm.com/pdf/ganter/en/3971.pdf?dispositiontype=attachment
- https://live-katalog.ganternorm.com/pdf/ganter/en/6885-1.pdf?dispositiontype=attachment

## Drawing symbol to parameter

| Symbol | Parameter | Model use |
|---|---|---|
| b1 | `housing_size_b1` | square housing width/depth |
| d1 | `shaft_diameter_d1` | both shaft diameters and bearing bores |
| b2 | `key_width_b2` | installed rounded-end parallel-key width |
| d2 | `bearing_boss_diameter_d2` | visible boss/opening envelope; proportional simplified bearing OD |
| d3 | not a build parameter | theoretical usable hub diameter; N/A at b1=18 |
| h | `key_height_h` | key projection above shaft |
| l1 | `housing_length_l1` | Type-L body spans and Type-T output-axis body span |
| l2 | `shaft_projection_l2` | shaft projection beyond each housing face |
| l3 | `key_length_l3` | visible key length |
| l4 | `key_end_margin_l4` | key-to-shaft-end margin |
| m1 | `input_axis_height_m1` | apex to input face; also apex to Type-L top face |
| t1 | `bearing_inset_t1` | official outer bearing/shoulder inset |
| t2 | `shaft_reach_t2` | official inner shaft/bearing reach |
| d4 | `mounting_hole_diameter_d4` | side-view clearance holes |
| d5 | `mounting_thread_d5` | four-hole bearing-face patterns |
| d6 | `rear_thread_d6` | two-hole rear-face pattern |
| d7 | `shaft_end_thread_d7` | threaded shaft-end holes |
| m2/m3 | `lower_hole_offset_m2` / `upper_hole_offset_m3` | d4 side pattern |
| m4 | `face_hole_spacing_m4` | face/rear hole spacing |
| m5 | `rear_hole_height_m5` | Type-L rear-hole height above base; retained as catalog evidence for Type T |

`CATALOG_ROWS` keeps the official `d3` values as evidence, including `None`
for both `b1=18` rows.  Because d3 is a theoretical usable hub diameter and
the minimum rows have no value, it is deliberately not exposed to
`PARAM_SPEC` and never drives geometry.  No zero, interpolation, or invented
minimum is substituted.

## Catalog coupling and checked rows

`catalog_index` is the only catalog draw.  It covers all 14 combinations:
seven `b1` sizes times Types L/T.  `refine()` copies every exposed dimension
from that same row, and `check()` locks every value back to it.

Manual source checks:

| Row | Source values checked | Model relation |
|---|---|---|
| b1=18, Type L | d1=6, b2=2, d2=13, l1=32, l2=12, m1=23, d4=3.1 | l1-m1=9=b1/2 |
| b1=35, Type T | d1=12, b2=4, d2=30, l1=60, l2=16, m1=42.5, d4=4.1 | l1-m1=17.5=b1/2 |

## External housing and interfaces

The two shaft axes are +X and +Z and intersect at the origin.  The drawing
identity `l1-m1=b1/2` puts the rear face at `-b1/2` and the input face at
`+m1`.  Type L uses the same limits vertically (`-b1/2` to `+m1`).  Type T is
vertically symmetric about the input axis, so its housing limits are
`-l1/2` to `+l1/2` and both output ends project a further `l2`.

The public drawing dimensions the shoulder endpoints but does not publish a
curve radius.  The Type-L inward shoulder is therefore a proportion: the
lower-left quadrant of a circle centered where the extended input and top
faces meet, with radius `m1-b1/2`.  The supplied Type-T STEP gives a more
specific profile: each shoulder is a short straight leg, a 45-degree arc of
radius `4 mm`, a short 45-degree tangent bridge, and a second 45-degree arc of
the same radius.  Its `b1=18` tangent bridge is `0.9 mm`; the implementation
scales these reference proportions as `r=(2/9)*b1` and `gap=0.05*b1`.  These
are analytic circular arcs, not polyline approximations, but the scaled values
remain proportions rather than unpublished manufacturing dimensions.  Type-L
side edges use a `0.04*b1` fillet (proportion); the Type-T reference has sharp
rear side corners.  Visible d2 openings use a small 45-degree entry chamfer
(proportion).

The page-2 projections are transcribed as follows:

- d5: four tapped holes on an m4 square around each bearing face;
- d6: two rear-face tapped holes spaced m4; Type L uses height m5 above the
  base, while the Type-T rear view places them on the input-axis centerline;
- d4: Type L side holes at `(-m2,-m2)` and `(+m3,+m3)`; Type T holes at
  `(+m3,+m3)` and `(+m3,-m3)` in the drawing's XZ coordinates.

The public sheet gives nominal M3/M4/M5 sizes, not thread pitch or minor
diameter.  Housing and shaft threads therefore use an explicitly simplified
`0.8*d` cylindrical core plus entry chamfer, not a false manufacturing thread.
The official minimum usable depths are retained exactly: `2*d5`, `2*d6`, and
`1.6*d7`.

## Shafts, keys, and operating state

The external obround elements shown on the shafts are modeled as installed
parallel keys and fused into their shaft solids to preserve the issue's fixed
nine-solid benchmark decomposition.  This interpretation is supported by the
GN drawing's exposed `h` dimension and its text that the parallel keys may take
any angular position.  It also agrees with DIN 6885-1: a 2 mm key on a 6 mm
shaft has 2 mm total height and 1.2 mm shaft-keyway depth, leaving the catalog
`h=0.8 mm` exposed; a 4 mm key on a 12 mm shaft similarly leaves
`4-2.5=1.5 mm`, matching the catalog.  Their exposed `b2/h/l3/l4` geometry is
official; a 0.08 mm hidden overlap is a Boolean-fusion proportion rather than
an asserted groove depth.  Rounded key ends are true slot arcs.  Type T is one
continuous output-shaft solid with top and bottom keyed/threaded ends.

`shaft_rotation_deg` rotates the +X input shaft and input gear together.  The
output shaft and gear rotate by the equal opposite angle, implementing the
documented 1:1 ratio.  Housing, bearings, dimensions, and body count do not
change with this pose parameter.

## Bevel gears

Exact tooth count, module, pitch cone details, and fits are unpublished.
The benchmark uses these declared proportions:

- 16 equal teeth on each gear;
- 45-degree pitch cones because equal gears meet at a 90-degree shaft angle;
- one shared pitch-cone apex at the shaft-axis intersection;
- mean module `m = 2*r_mean/16`;
- face limits `s_inner=max(0.24*b1, (d1/2+0.30)/ROOT_RATIO)` and
  `s_outer=min(0.38*b1, s_inner+0.12*b1)` measured from the apex.  The small
  end is set from the ROOT cone so the full-depth root still clears the shaft
  bore; the large end is capped so the full-depth tip still leaves a `b1` side
  wall on every catalog size.  Face width along the cone stays near `0.29` of
  the cone distance, the usual bevel proportion;
- a short `0.02*b1` hub; each shaft begins at the greater of the hub start
  and `d1/2+0.02*b1`, so perpendicular shafts cannot cross at the apex while
  both retain a positive cylindrical seat inside their gear bore;
- straight planar tooth flanks at 20 degrees, tapering over the WORKING depth
  (one addendum either side of the pitch line).  The remaining `0.25*m` of
  dedendum is root clearance at constant thickness: continuing the taper into
  it thickens the root past an involute-equivalent flank and eats the
  published backlash before the flanks reach contact;
- standard depth: addendum `1.00*m` and dedendum `1.25*m` measured
  PERPENDICULAR to the pitch cone (whole depth `2.25*m`).  The tooth sections
  are sketched at constant `z` and the tip/root cones run parallel to the
  45-degree pitch cone, so a perpendicular offset `a` becomes a radial offset
  `a/cos(45 deg)` — hence `TIP_RATIO = 1 + 2*1.4142/16` and
  `ROOT_RATIO = 1 - 2*1.7678/16`, both independent of size.  (Radial figures
  of `0.50*m`/`0.60*m` were used before that conversion was applied, which
  left only `0.78*m` of real tooth depth — about a third of standard.)  A
  `0.15*m` root overlap fuses every tooth to its gear core;
- tooth thickness fraction 0.43 of circular pitch.  For two equal gears this
  gives `(1-2*0.43)*360/16 = 3.15 deg` circumferential backlash, within the
  official `3 +/- 0.5 deg` range;
- a half-pitch initial phase places an input tooth in an output gap.

The gears have equal d1 bores and contact their shafts on coincident cylindrical
fit surfaces without sharing volume.  The housing cavity follows the two gear
envelopes and retains a positive side wall.

Additional unpublished construction dimensions are explicit proportions:

- diametral shaft-tunnel clearance `max(0.12, 0.008*d1)`;
- gear-cavity radial clearance `max(0.25, 0.015*b1)`;
- hollow housing wall `max(1.4, 0.08*b1)`: the full XZ casting outline is
  inset by this amount and removed between two broad side plates, while local
  annular sleeves/posts retain the bearings and every mounting/thread hole;
  the large front/side face therefore remains a closed thin wall, not a new
  through opening.
- bearing-opening chamfer `min(0.65, 0.045*d2)`;
- shaft-end chamfer `min(0.50, 0.06*d1)`;
- tapped-hole core diameter `0.8*d` and entry-chamfer depth `0.18*d`;
- bearing edge chamfer `min(0.35, 0.12*w, 0.18*(d2-d1)/2)`;
- gear-hub radius `max(d1/2+0.18*m, 0.65*r_root_inner)` and hidden hub overlap
  `0.20*m`;
- small 0.05-0.2 mm Boolean overtravel at hidden pockets and holes, used only
  to avoid coincident cutting faces and never to set an external dimension.

## Bearings and benchmark topology

The public sheet specifies sealed steel ball bearings (2RS) but no bearing
model or dimensions.  Each simplified bearing is one connected chamfered ring
with the official `d1` shaft interface, a proportional OD equal to the visible
`d2` boss/opening envelope, and proportion width `max(1.5, 0.12*d2)`.  It is
deliberately not split into races and balls; `d2` is not claimed as a published
bearing-model OD.
Bearing axes are concentric with their shafts.  Type L uses two bearings near
each positive shaft face; Type T keeps two input bearings and places one output
bearing at each vertical housing end.  The Type-T output bearings are mirrored,
with each outer bearing face inset by the selected row's `t1`; their inner
faces remain clear of the gear envelope over all seven sizes.  The use of
`t1/t2` to locate the simplified bearing stack follows the official section
drawing, while the unpublished bearing width remains a proportion.

The fixed nine solids are a benchmark modeling decision, not a Ganter BOM:
housing, two shafts, two bevel gears, and four simplified bearings.

## Verification record

A local mechanical audit supplements `bench2 validate`, which does not test
assembly-body intersections.  The audit rebuilt all 14 catalog rows at zero
rotation and rows 0, 6, and 13 at seven additional poses spanning one complete
22.5-degree tooth pitch (35 instances total):

- all 36 body pairs per instance had maximum intersection volume
  `0.000000000 mm^3`;
- gear-to-gear clearances stayed between approximately 0.049 and 0.106 mm;
- every shaft/gear, shaft/bearing, and bearing/housing interface had zero
  separation without positive-volume overlap;
- each catalog row exported to STEP and imported back as exactly nine solids;
- absolute bounding-box limits, not only lengths, matched the drawing: Type L
  uses X/Z `[-b1/2, m1+l2]`, while Type T uses the same X limits and symmetric
  Z limits `[-l1/2-l2, +l1/2+l2]`; both use Y `[-b1/2, +b1/2]`.

The final validator run covered 23 parameters, all 14 catalog indices, and 12
sampled builds: all were non-degenerate nine-solid assemblies, with 12/12
unique geometry hashes and no sampling, constraint, execution, or determinism
failure.

## Deliberate deviations

- No manufacturer STEP is imported or committed.
- Housing shoulder curves, gear tooth count/flank form, bearing OD/width,
  cavity wall, fits, minor fillets, seals, lubrication, internal shoulders,
  and hidden retention details are proportions because the public sheet does
  not specify them.
- Tapped holes are cylindrical core approximations; helical thread geometry
  and exact ISO minor diameters are not asserted.
- Parallel keys are fused to the shaft solids instead of separate bodies so
  the fixed nine-solid topology remains deterministic.
- The single-piece bearing rings convey location and envelope, not a literal
  rolling-element construction.
