# GN 784 modeling notes

## Evidence boundary

- Anchor: JW Winco GN 784 official product page and US catalog PDF
  (`https://www.jwwinco.com/en-us/products/3.6-Moving-Transferring-Connecting-with-Joints-Couplings-and-Gears/ball-joints/GN-784-Aluminum-Mounting-Clamps-with-Swivel-Ball-Joint`
  and `https://live-catalog.jwwinco.com/pdf/winco/us/784.pdf`).
- The eight entries in `_CATALOG_ROWS` reproduce the eight printed table rows.
  Each row carries `d1`, the nonblank `d2`/`d3`/`d4` alternatives, applicable
  `r1` or `r2`, `l1`, and the complete common row (`d5` through torque).
- Type A maps only to a published `d2` or `d3` field. Type B maps only to a
  published `d4` field. A blank field returns no catalog combination.
- Internal usable thread depth follows the catalog footnote: `1.5D` for metric
  `d2`/`d3` and `1.2D` for inch `d3`. Type B uses the printed external-stud
  length `l1`.
- Finish is fixed to ELS metadata and is not sampled. Clamp and stop torques
  remain source metadata; they are not converted into performance claims.

## Difficulty and coupling

- `catalog_row` selects a complete printed row; dimensions never interpolate.
- `refine()` jointly chooses `ball_type` and `thread_code` from that row's
  nonblank alternatives.
- Easy: rows `31-M5/M6` and `39-M5/M6`, metric Type A, identification 2.
- Medium: metric alternatives from all eight rows, Type A/B, identification
  1/2, with 0 or 30 degree ball poses.
- Hard: every published metric or inch alternative from all eight rows,
  Type A/B, identification 1/2, with 0, 30, or 90 degree ball poses.

## Explicit proportion rules

The drawing does not dimension the hidden socket seat, base-seat fit, split,
clamp screw body, lever body, socket recess, small steps, fillets, chamfers,
thread helices, casting draft, or surface texture. They are deliberately
simplified and sourced as `proportion`:

- spherical seat radial clearance:
  `max(0.20 mm, 0.012*d6)`;
- base seat diametral member: `base_d = 0.80*d1`;
- base seat radial clearance:
  `max(0.15 mm, 0.008*d1)`;
- base thickness: `0.28*h3`;
- top opening radius:
  `max(0.44*d6, d7/2 + spherical_seat_clearance)`;
- clamp screw diameter: `0.18*d1`;
- clamp screw radial clearance:
  `max(0.20 mm, 0.012*d1)`;
- 90 degree stem-sweep slot: lower thin-neck diameter plus radial running
  clearance `max(0.25 mm, 0.010*d1)`; the resulting slot remains narrower
  than the `d7` middle collar;
- lower thin ball-neck diameter: `0.55*d7`;
- lower thin ball-neck length: from its `0.58*(d6/2)` sphere overlap to beyond
  the housing outside radius by `max(0.60 mm, 0.030*d1)`; this is also longer
  than the housing radial wall thickness;
- lever handle width: `0.20*l2`;
- lever handle thickness: `0.17*d1`;
- identification 2 head length: `0.16*d1`.

Threads are represented by nominal cylindrical holes/studs, not helices.
Small edge treatments and casting draft are omitted for deterministic,
reviewable geometry.

## Static assembly and deliberate deviations

- The result is a four-solid `cq.Assembly` named `housing`, `ball`, `base`, and
  `clamp_actuator`. It encodes no mates or joints; `swivel_angle` selects a
  deterministic static pose from vertical (0 degrees) to horizontal
  (90 degrees).
- The housing slot clears the complete 0-90 degree sweep of only the lower
  thin neck toward the side opposite the clamp actuator. The neck reaches
  beyond the housing outside surface before the `d7` middle collar begins, so
  the middle collar stays outside and the slot can remain narrower than it.
  The drawing's separate 360-degree annotation is not exposed as an
  unsupported second motion axis.
- The ball stem is modeled as a lower thin neck, a thick `d7` middle collar,
  and a thin upper threaded member. Type A cuts the sourced internal usable
  thread depth down the upper member; Type B keeps the upper stud solid.
- The ball is separated from its spherical seat by the documented proportion
  clearance while the opening remains smaller than `d6`, preserving capture.
- The base plate sits in a clearance pocket. The `d5` thread and offset `d8`
  anti-rotation hole are plain cylindrical cuts.
- Hidden clamping wedges, pins, retainers, screw tips, lever reindexing
  mechanism, hand-knob option, GN 784.1 flange, payload hardware, and surface
  texture are excluded as required by Issue #60.
