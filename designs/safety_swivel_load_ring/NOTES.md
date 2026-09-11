# GN 586 modeling notes

## Evidence

- Anchor: JW Winco GN 586 product page and official `586.pdf` linked in Issue #62.
- The five printed inch-thread rows were transcribed as whole rows and
  spot-checked against the dimension-table and load/torque attachments.
- `d1` remains an exact printed designation through `catalog_row`,
  `thread_major_d`, and `thread_tpi`; the nominal major diameter uses the exact
  conversion 25.4 mm/in.
- WLL, lashing force, tightening torque, and the -40 to 100 deg C range are
  source metadata only. They are not geometry controls or certification claims.
- The official PDF says the 1.5 x d1 minimum screw-in-depth note applies at
  tensile strength >= 340 N/mm2. Issue #62 says 640 N/mm2. Receiving material
  and screw-in depth are excluded from this family, so neither value becomes a
  CAD constraint.

## Dimension reconstruction

- The printed chain is reproduced exactly: `h2 = h3 + h4`.
- The load-ring opening spans `k3` by `h3`, from elevation `h4` to `h2`.
- The ring outer width is `k2`, upright top is exactly `h1`, and depth is
  `k1`; no post-build Z translation is applied.
- The visible front-section width is `(k2 - k3) / 2`.
- `d2`, `l1`, and `l2` control the bracket footprint and supplied bolt
  projection shown in the fixed upright pose.
- `k4`, `k5`, and `r` describe the catalog swivel envelope. They remain coupled
  to the selected row and are checked as metadata, but are intentionally not
  `build()` inputs; no swept body, angle, mate, or fictitious motion range is
  generated.
- The printed inch designation supplies both nominal major diameter and TPI.
  The modeled external thread uses `P = 25.4 / TPI`, a 60-degree Unified
  profile and basic external radial depth `0.61343*P`. The visible triangular
  ridge uses an axial half-width of `0.30*P` and a small radial embed into the
  root cylinder; those two robust-boolean details are explicit `proportion`
  choices rather than tolerance-grade crest/root geometry.

## Honest proportion choices

The source does not dimension forging draft/parting lines, ring-section
transitions, bracket-ear thickness and distribution, bushing wall and height,
bolt-head proportions, thread runout, retainers, grooves, RFID pocket, coating
thickness, or hidden contact surfaces. The model therefore uses:

- a closed load ring built identically in all difficulties by drawing a YZ
  guide with long straight sides, large-radius shoulders, and a low single-peak
  tangent-continuous spline crown,
  drawing a circular `k1` section on XZ at the guide start, and sweeping that
  circle around the guide with a fixed planar normal;
- the load ring passes through the clear space between the two bracket ears;
  the bracket pocket is centered on the swept ring's lower path, derived from
  `h4`, `(k2-k3)/2`, and the circular `k1/2` section radius, and captures that
  section with only documented assembly clearance;
- an elliptical swivel base and vertical annular bracket axis, without the
  rejected four prismatic ear bars;
- a separate obround-ended U-shaped bracket made as one continuous solid:
  the strip is folded 180 degrees into two horizontal parallel ears, their
  holes are coaxial with the vertical bracket axis, and only the negative-X
  return side is closed;
- no separate pin: the bracket annular axis passes through both clevis holes;
- a plain annular bushing around the nominal bolt cylinder;
- a catalog-pitch helical external thread and enlarged hex head placed above
  the bracket post; its across-flats dimension exceeds the bracket-hole diameter,
  and its undimensioned blind hex socket uses documented proportions;
- an optional fused RFID pad whose presence is source-backed but whose size is
  explicitly `proportion` (easy omits it, medium mixes it, hard shows it).

These details are shape-identification geometry only and are labeled
`proportion` in `spec.py`. The assembly contains no receiving
material, stress analysis, load path, safety factor calculation, or
certification.

## Assembly contract

`build()` returns a deterministic `cq.Assembly` with five stable child names:
`load_ring`, `swivel_base`, `bearing_bushing`, `mounting_bolt`, and `bracket`.
The source-labeled U-shaped body is therefore named `bracket`; names of the
remaining construction pieces describe their role instead of fighting the
drawing. Each physical component has its own builder. `family.json` declares
five solids and five one-off components.

The family output remains one fixed upright pose. No numeric fold or swivel
angle is a family parameter or a GN 586 claim. A development-only sweep used
for an earlier open-ring revision no longer applies after the user requested
closed easy/medium rings; it is therefore not reported as final verification.

## Verification record

- The prior hard-only `k2/2` ring subtraction was unsupported and has been
  removed. All tiers now preserve the same closed load-ring topology.
- `preview_parts.png` must give four standard views for each of the five distinct
  physical components, one assembly overview, and five further rows that keep
  the complete assembly in place while sequentially highlighting each stable
  component across the same four views.
- Validation and preview evidence below must be regenerated after changes; no
  earlier pass or interference number is carried forward as current evidence.
