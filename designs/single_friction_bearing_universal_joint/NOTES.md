# DIN 808 EG modeling notes

## Scope and evidence

This family implements only the JW Winco DIN 808 steel, single-jointed,
friction-bearing form `EG`. It does not include the double-jointed `DG` form,
`l2`, `l4`, a second cross, unequal or inch bores, needle bearings, stainless
variants, shafts, or protective boots.

Primary sources:

- JW Winco DIN 808 official product page and official `808g.pdf`.
- The Issue #61 EG engineering drawing, product photo, and metric-table
  attachments, all checked against `808g.pdf`.
- JW Winco `DIN 6885-1 Keys and Keyways, Metric, High Type`, linked directly
  from the DIN 808 product page, for JS9 hub-keyway width `b` and depth `t2`.

The DIN 808 table contains 19 complete rows. `catalog_row` selects exactly one
row and `refine()` fills `d1`, `d2`, `s`, `l1`, `l3`, and `t` from that row.
Dimensions are never interpolated or mixed between rows.

## Source-symbol mapping

| Source | Code | Use |
|---|---|---|
| `d1` | `d1` | outside hub/fork-root diameter |
| `d2 H7` | `d2` | equal circular bore at both ends for B/K |
| `s H10` | `square_s` | equal square bore at both ends for V |
| `l1`, type EG | `l1` | straight-pose overall length |
| `l3` | `l3` | each end face to the single cross center |
| `t +1` | `shaft_depth` | nominal maximum shaft-insertion envelope; tolerance is not modeled |
| DIN 6885-1 `b JS9` | `keyway_width` | K hub-keyway width |
| DIN 6885-1 `t2` | `keyway_depth` | K hub-keyway radial depth |

The source drawing gives `l1 = 2*l3` for all 19 EG rows. Both ends always use
the same selected B, K, or V treatment.

## Static component model

`build()` returns a `cq.Assembly` with stable names:

- `input_yoke`
- `output_yoke`
- `cross`

Each component has its own builder. Both yokes are rigidly transformed
instances of the same yoke geometry, including the B/K/V bore treatment. The
cross contains two perpendicular arms centered at the shaft-axis intersection.
The input-yoke trunnion axis is global Z; the output-yoke instance is phased 90
degrees so its trunnion axis is global Y. Rotating the output yoke about Y
therefore changes the shaft inclination while leaving its cross axis centered
and perpendicular to the input cross axis. This is a static envelope, not a
kinematic mate, RPM rating, torque model, or clearance-class claim.

Hidden sleeves, pins, caps, retainers, and lubrication passages are omitted
because the reviewed drawing does not dimension them.

## Component and assembly preview

`preview_parts.png` uses one four-view row for the yoke part because
`input_yoke` and `output_yoke` are rigidly transformed instances of the same
geometry. A second four-view row shows the orthogonal cross. The assembly rows
then separate the adjacent/nested highlight groups:

- blue `input_yoke` and teal `output_yoke`, with the cross as a subdued spatial
  reference;
- orange `cross`, with both yokes transparent.

No exploded sequence or assembly arrows are shown. The public evidence does not
dimension the omitted pins, sleeves, caps, or retainers, so arrows would imply
an unsupported physical assembly method. The assembly graphic documents
component identity, position, and perpendicular trunnion axes only.

## Honest proportion boundary

DIN 808 does not dimension the fork ears, cross arms, or internal clearances in
the reviewed public drawing. The following are deliberate `proportion` rules,
chosen to preserve recognizable geometry, three separate solids, positive
clearance, and stable generation:

- full-diameter hub length: `t`; this keeps the published maximum shaft
  insertion envelope coupled to the cylindrical hub and leaves the remaining
  `l3 - t` length for the fork
- fork-eye radius: `0.21*d1`
- fork-eye center offset from the shaft axis: `0.37*d1`
- fork-ear thickness: `0.18*d1`
- cross-arm diameter: `0.16*d1`
- trunnion-hole diameter: `0.19*d1`
- cross end clearance inside each fork eye: `0.02*d1`
- fork/root overlap for a single yoke solid: `0.03*d1`

Fork-eye centers and radii are constrained so perpendicular yoke envelopes do
not overlap. The 0.03*d1 diametral trunnion clearance prevents a positive solid
intersection between the cross and either yoke. These values are not claimed
as DIN/manufacturer dimensions or performance clearances.

## Deliberate simplifications

- The published `t +1` tolerance is not varied; the table's nominal `t` is used.
- Bore H7/H10 and keyway JS9 tolerances are metadata, not geometric tolerance
  samples.
- Root blends, chamfers, shoulders, grease passages, sleeves, caps, and
  retainers are omitted rather than guessed.
- At nonzero `joint_angle`, each half retains its catalog `l3`; `l1` remains the
  official straight-pose boundary dimension.
- MOQ-marked rows remain valid hard-tier catalog choices; the asterisk is
  availability information, not a geometric difference.
