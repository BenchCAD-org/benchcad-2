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
- The ring outer width is `k2`, upright top is `h1`, and depth is `k1`.
- The visible front-section width is `(k2 - k3) / 2`.
- `d2`, `l1`, and `l2` control the bracket footprint and supplied bolt
  projection shown in the fixed upright pose.
- `k4`, `k5`, and `r` describe the catalog swivel envelope. They remain coupled
  to the selected row and are checked as metadata; no swept body, angle, mate,
  or fictitious motion range is generated.

## Honest proportion choices

The source does not dimension forging draft/parting lines, ring-section
transitions, bracket-ear thickness and distribution, bushing wall and height,
bolt-head proportions, thread runout, retainers, grooves, RFID pocket, coating
thickness, or hidden contact surfaces. The model therefore uses:

- a filleted closed load ring built identically in all difficulties, with
  catalog `k1`, `k2`, `k3`, `h1`, `h2`, and `h4` controlling its depth and
  envelope; only after that closed solid is complete, hard subtracts a bottom
  gap whose width is exactly `k2 / 2` (`proportion`);
- the load ring passes through the clear space between the two clevis ears;
  its outer bottom is placed one quarter of the total clevis height above the
  clevis bottom (`proportion`, user-reviewed assembly placement);
- an elliptical swivel base and vertical annular bracket axis, without the
  rejected four prismatic ear bars;
- a separate obround-ended thin-steel clevis made as one continuous solid:
  the strip is folded 180 degrees into two horizontal parallel ears, their
  holes are coaxial with the vertical bracket axis, and only the negative-X
  return side is closed;
- no separate pin: the bracket annular axis passes through both clevis holes;
- a plain annular bushing around the nominal bolt cylinder;
- a simplified cylindrical thread envelope and enlarged hex head placed above
  the bracket post; its across-flats dimension exceeds the clevis-hole diameter;
- an optional fused RFID pad whose presence is source-backed but whose size is
  explicitly `proportion` (easy omits it, medium mixes it, hard shows it).

These details are shape-identification geometry only and are labeled
`proportion` in `spec.py`. The assembly contains no receiving
material, stress analysis, load path, safety factor calculation, or
certification.

## Assembly contract

`build()` returns a deterministic `cq.Assembly` with five stable child names:
`load_ring`, `bracket`, `bushing`, `bolt`, and `clevis`. Each physical
component has its own builder. `family.json` declares five solids and five
one-off components.

The family output remains one fixed upright pose. No numeric fold or swivel
angle is a family parameter or a GN 586 claim. A development-only sweep used
for an earlier open-ring revision no longer applies after the user requested
closed easy/medium rings; it is therefore not reported as final verification.

## Verification record

- All five catalog rows were built with both RFID states and both ring-gap
  states: twenty fixed assemblies, five non-degenerate solids each, and zero
  pairwise volumetric intersections. Easy/medium select the closed state;
  hard selects the post-build `k2 / 2` bottom subtraction.
- `preview_parts.png` gives four standard views for each of the five distinct
  physical components, followed by four assembly-overview views.
- `preview_assembly.png` keeps the complete reviewed assembly in place while
  sequentially highlighting each stable component across four standard views.
- Formal `bench2 validate` passed easy, medium, and hard at 4/4 seeds,
  covered all five declared catalog rows, produced 7/12 unique sampled
  geometries, and confirmed five non-degenerate solids per instance.
