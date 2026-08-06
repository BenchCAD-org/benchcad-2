# light_duty_swivel_plate_caster engineering notes

This family implements only the unbraked JW Winco EN 22870 Form L caster.
`catalog_size` selects one complete official row; no dimension is mixed across
the 40, 50, 60, and 80 mm products.

## Official references

- Product page:
  <https://www.jwwinco.com/en-us/products/3.10-Rolling-Transporting-with-Casters-and-Wheels/Light-Duty-Casters/EN-22870-Steel-Light-Duty-Casters-Rubber-Wheel-Tread-Polypropylene-Wheel-Core-Light-Version>
- Metric dimension PDF:
  <https://live-catalog.jwwinco.com/pdf/winco/us/22870_L.pdf?dispositiontype=attachment>
- Engineering drawing:
  <https://live-catalog-cdn.jwwinco.com/svg/winco/c8d15078a9076f8889ca5e930cc7f661/EN-22870-Steel-Light-Duty-Casters-Rubber-Wheel-Tread-Polypropylene-Wheel-Core-Light-Version-sketch.svg>

## Catalog mapping

| Code parameter | Catalog symbol | Meaning |
|---|---|---|
| `wheel_d` | `d1` | wheel diameter |
| `wheel_width` | `b` | wheel width |
| `axle_d` | `d2` | wheel axle diameter |
| `overall_h` | `h` | floor-to-plate-top height |
| `plate_l` | `l1`, Type L/LF | mounting-plate length |
| `plate_w` | `l2`, Type L/LF | mounting-plate width |
| `swivel_offset` | `l3`, Type L/R/G | axle-to-swivel-axis offset |
| `mount_pitch_x` | `m1`, Type L/LF | mounting-slot pitch |
| `mount_pitch_y` | `m2` | mounting-slot pitch |

| `catalog_size` | `d1` | `b` | `d2` | `h` | `l1` | `l2` | `l3` | `m1` | `m2` |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 40 | 40 | 18 | 5 | 59 | 42 | 42 | 24 | 30 | 33 |
| 50 | 50 | 18 | 6 | 66 | 55 | 55 | 21 | 38.5 | 44 |
| 60 | 60 | 24 | 6 | 83 | 60 | 60 | 21 | 38.5 | 48 |
| 80 | 80 | 24 | 6 | 104 | 60 | 60 | 30 | 38.5 | 48 |

The shared sheet also contains dimensions for rigid, braked, center-hole, and
threaded-stud forms. Those columns are deliberately excluded. The published
`r` value is drawn on the braked LF view, so it remains issue metadata and does
not drive unbraked Form L geometry.

## Coordinate system and official dimensions

- XY is the horizontal mounting/floor plane; Z is vertical.
- Floor contact is `Z = 0`.
- The wheel axis is parallel to Y, at
  `(X, Z) = (swivel_offset, wheel_d / 2)`.
- The swivel axis is the Z axis at `(X, Y) = (0, 0)`.
- The mounting-plate top is exactly `Z = overall_h`.
- Slot centers are at
  `(±mount_pitch_x / 2, ±mount_pitch_y / 2)`.

## Proportion formulas

Every formula in this section is explicitly `"proportion"` and is not
presented as a JW Winco production dimension.

- plate thickness:
  `max(1.6 mm, 0.035 * min(plate_l, plate_w)) * sheet_scale`
- mounting-plate corner radius:
  `min(2.0 mm, 0.04 * min(plate_l, plate_w))`
- upper race diameter / height:
  `0.46 * plate_min * race_scale` /
  `max(3.0 mm, 0.060 * overall_h) * race_scale`
- lower race diameter / height:
  `0.40 * plate_min * race_scale` /
  `max(2.6 mm, 0.050 * overall_h) * race_scale`
- axial gap between upper and lower race envelopes: `0.25 mm`
- fork sheet thickness:
  `max(1.6 mm, 0.080 * wheel_width) * sheet_scale`
- wheel-to-fork side clearance per side:
  `0.8 mm + 0.010 * wheel_d`
- fork bridge thickness:
  `max(2.0 mm, 0.11 * wheel_width) * sheet_scale`
- slot width / length:
  `max(3.0 mm, 0.55 * axle_d) * slot_scale` / `1.65 * slot_width`
- slots point radially toward the swivel axis
- wheel edge fillet:
  `min(0.08 * wheel_width, 0.04 * wheel_d)`
- wheel side-recess depth:
  `min(1.5 mm, 0.10 * wheel_width)`
- wheel recess outer radius / hub radius:
  `0.34 * wheel_d` / `0.18 * wheel_d`
- axle radial clearance in wheel and fork: `0.20 mm`
- axle-head axial clearance outside each fork leg: `0.25 mm`
- axle head thickness / diameter:
  `max(1.4 mm, 0.30 * axle_d)` / `1.80 * axle_d`

`sheet_scale`, `race_scale`, and `slot_scale` are 1.0 in easy, 0.95-1.05 in
medium, and 0.90-1.10 in hard. They perturb only catalog-unpublished details;
all EN 22870 row dimensions remain exact.

## Components

The four component builders map one-to-one to stable `cq.Assembly` children
and `family.json.components`:

| Builder | Assembly child | Quantity |
|---|---|---:|
| `build_mounting_plate()` | `mounting_plate` | 1 |
| `build_swivel_fork()` | `swivel_fork` | 1 |
| `build_wheel()` | `wheel` | 1 |
| `build_axle_fastener()` | `axle_fastener` | 1 |

The mounting plate is the stationary reference. The fork rotates about the
vertical swivel axis in the real product, and the wheel rotates about the
axle, but this benchmark returns one deterministic assembled reference pose.

## Interference and clearance rules

- wheel and both fork legs have a positive side gap
- the bridge remains above the wheel top for every catalog row
- wheel and fork axle bores are `0.20 mm` larger in radius than the axle
- axle head/nut envelopes remain `0.25 mm` outside the fork faces
- upper and lower swivel-race envelopes have a `0.25 mm` axial gap
- all four components must remain non-degenerate and pairwise
  non-intersecting in every sampled row

## Deliberate deviations and omissions

- Natural-rubber tread and polypropylene core are one connected wheel
  envelope; their internal interface is not dimensioned.
- The dual grease-lubricated ball bearing is represented only by separated
  upper/lower external race envelopes. Balls, grooves, grease, seals, and
  preload are omitted.
- Fork stamping bends are represented by connected straight-sided sheet
  envelopes. Production bend radii, draft, ribs, and local blends are omitted.
- Plate mounting slots are proportioned capsules because the catalog publishes
  their pitch but not their length or width.
- The tread section is a proportion. `d1` and `b` are catalog values, the
  profile is not, so the tread holds `d1` across the middle of the band and
  rolls off tangentially to the shoulders — the rubber-tyre section on the
  product photo. It is built as the full-diameter cylinder intersected with a
  sphere of radius `sqrt((d1/2 - drop)^2 + (b/2)^2)` on the wheel centre, with
  `drop = min(0.045*d1, 0.75*drop_max)` and `drop_max = d1/2 - sqrt((d1/2)^2 -
  (b/2)^2)`, the drop at which that sphere degenerates to the wheel radius.
  Measured: Ø60x24 holds 60.000 to y = ±6.7 and reaches 56.598 at the
  shoulder; Ø80x24 holds 80.000 and reaches 77.495.
- The plate is drawn, not flat: a circular seat around the swivel axis with the
  kingpin hole through its floor, both proportions (`0.92 * upper_race_d`,
  `min(0.45*t, 0.9)` deep, hole `max(3, 0.30 * upper_race_d)`). The seat is
  pressed downward so the plate top stays exactly at the catalog `h`.
- Each fork leg closes on a round lug of radius `0.95 * d2` concentric with the
  axle rather than a square corner below the bore — the pressed leg end on the
  photo. Still a proportion; the catalog dimensions no part of the leg.
- The axle is a **standard part, not a proportion**. The product photo shows a
  hex head bearing on the fork leg, and the catalog publishes its nominal size
  as `d2`, so it is modelled as an ISO 4014 hex-head bolt with an ISO 4032 hex
  nut at ISO 261 coarse pitch:

  | `d2` | rows | ISO 4014 `s` | ISO 4014 `k` | ISO 4032 `m` | pitch |
  |---:|---|---:|---:|---:|---:|
  | 5 | 40 | 8 | 3.5 | 4.7 | 0.8 |
  | 6 | 50 / 60 / 80 | 10 | 4 | 5.2 | 1.0 |

  Measured on the built solids, all four rows: head and nut across flats
  8.000 / 10.000 and nut height 4.700 / 5.200 — the table values exactly.
  Only these two sizes are tabulated; any other `d2` would fall back to
  declared proportions rather than invent a standard row.
- Thread form is the repo's axisymmetric ring stack, not a helix: one ring of
  axial width `0.4*pitch` every pitch, because `makeHelix` silently no-ops on
  scattered size/geometry combinations in the pinned cadquery/OCP. A thin
  annulus between the minor and major radii measures **40 % fill on every
  catalog size**, which is the ring duty cycle — the crests are present, not
  silently missing. The core is turned down to the minor diameter over the
  threaded length, as a cut thread is; the nut's internal rings sit on the
  same axial grid offset half a pitch, so the pair reads engaged and measures
  0.0000 mm³ of intersection.
- Thread run length, and where the thread starts along the shank, are
  proportions — ISO 4014 tabulates them but the caster catalog does not say
  which bolt length is fitted.
- Washers, wrench marks, thread coating and secondary fasteners are omitted.
- Surface finish, tread hardness, temperature range, load rating, molded
  lettering, and thread-guard material are provenance metadata, not geometry.
- No rigid bracket, brake, center hole, threaded stud, swivel animation, wheel
  animation, or undocumented assembly angle is included.
