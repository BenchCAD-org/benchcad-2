# light_duty_swivel_plate_caster engineering notes

This family implements only the unbraked JW Winco EN 22870 Form L caster.
`catalog_size` selects one complete official row; dimensions are never mixed
across the 40, 50, 60, and 80 mm products.

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
| `mount_slot_w` | `d2` | diagonal mounting-slot width, not wheel axle diameter |
| `overall_h` | `h` | floor-to-plate-top height |
| `plate_l` | `l1`, Type L/LF | mounting-plate length |
| `plate_w` | `l2`, Type L/LF | mounting-plate width |
| `swivel_offset` | `l3`, Type L/R/G | axle-to-swivel-axis offset |
| `mount_pitch_x` | `m1`, Type L/LF | mounting-slot pitch |
| `mount_pitch_y` | `m2` | mounting-slot pitch |

| `catalog_size` | `d1` | `b` | `d2` slot width | `h` | `l1` | `l2` | `l3` | `m1` | `m2` |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 40 | 40 | 18 | 5 | 59 | 42 | 42 | 24 | 30 | 33 |
| 50 | 50 | 18 | 6 | 66 | 55 | 55 | 21 | 38.5 | 44 |
| 60 | 60 | 24 | 6 | 83 | 60 | 60 | 21 | 38.5 | 48 |
| 80 | 80 | 24 | 6 | 104 | 60 | 60 | 30 | 38.5 | 48 |

The shared sheet also contains rigid, braked, center-hole, and threaded-stud
forms. Those columns are excluded. The published `r` value belongs to the
braked LF view and does not drive this unbraked Form L geometry.

## Coordinate system and official dimensions

- XY is the horizontal mounting/floor plane; Z is vertical.
- Floor contact is `Z = 0`.
- The wheel axis is parallel to Y at
  `(X, Z) = (swivel_offset, wheel_d / 2)`.
- The swivel axis is the Z axis at `(X, Y) = (0, 0)`.
- The outside mounting-flange top is exactly `Z = overall_h`.
- Slot centers are at
  `(+-mount_pitch_x / 2, +-mount_pitch_y / 2)`.

## Proportion formulas

Every item below is explicitly `proportion`; none is presented as a JW Winco
production dimension.

- wheel axle/fastener nominal diameter:
  `max(4.0 mm, 0.25 * wheel_width)`
- plate thickness:
  `max(1.6 mm, 0.035 * min(plate_l, plate_w)) * sheet_scale`
- drawn-plate transition outer radius / central-platform radius:
  `0.46 * plate_min` / `0.30 * plate_min`
- platform sink depth: `max(1.0 mm, 0.85 * plate_t)`
- smooth transition curves: each surface uses one cubic spline with horizontal
  endpoint tangent directions; the lower curve is the upper curve shifted down
  by exactly `plate_t`
- upper race diameter / height:
  `0.46 * plate_min * race_scale` /
  `max(3.0 mm, 0.060 * overall_h) * race_scale`
- lower race diameter / height:
  `0.40 * plate_min * race_scale` /
  `max(2.6 mm, 0.050 * overall_h) * race_scale`
- axial gap between race envelopes: `0.25 mm`
- fork sheet thickness:
  `max(1.6 mm, 0.080 * wheel_width) * sheet_scale`
- wheel-to-fork side clearance per side: `0.8 mm + 0.010 * wheel_d`
- fork bridge thickness:
  `max(2.0 mm, 0.11 * wheel_width) * sheet_scale`
- slot length: `1.20 * d2 * slot_scale`; `d2` itself remains exact
- slots point radially toward the swivel axis
- wheel side-recess depth: `min(1.5 mm, 0.10 * wheel_width)`
- wheel recess outer radius / hub radius: `0.34 * wheel_d` / `0.18 * wheel_d`
- axle radial clearance in wheel, fork, and nut: `0.20 mm`
- axle-head/nut axial clearance outside each fork leg: `0.25 mm`
- bolt head across flats / height: `1.80 * axle_d` /
  `max(1.4 mm, 0.65 * axle_d)`
- nut across flats / height: `1.80 * axle_d` / `0.85 * axle_d`

`sheet_scale`, `race_scale`, and `slot_scale` equal 1.0 in easy, vary from
0.95 to 1.05 in medium, and from 0.90 to 1.10 in hard. They perturb only
catalog-unpublished construction; all EN 22870 row values remain exact.

## Components

The five component builders map one-to-one to stable `cq.Assembly` children
and `family.json.components`:

| Builder | Assembly child | Quantity |
|---|---|---:|
| `build_mounting_plate()` | `mounting_plate` | 1 |
| `build_swivel_fork()` | `swivel_fork` | 1 |
| `build_wheel()` | `wheel` | 1 |
| `build_axle_fastener()` | `axle_bolt` | 1 |
| `build_axle_nut()` | `axle_nut` | 1 |

The mounting plate is stationary. The fork and wheel move in the real product,
but this benchmark returns one deterministic assembled reference pose.

## Geometry and clearance rules

- Both fork plates are translated copies of one XZ side-profile master. They
  remain parallel, symmetric about Y=0, identical in shape, and coaxial.
- The master has a wide top, a near-vertical upper inner edge, and a smooth
  outer spline tangent to a round axle ear; its closed wire does not cross.
- The bridge remains above the wheel top for all four catalog rows.
- Wheel and both fork plates retain positive side clearance.
- Wheel and fork axle bores exceed the proportioned axle radius by `0.20 mm`.
- Axle head and nut remain `0.25 mm` outside the fork faces.
- Upper and lower swivel-race envelopes retain a `0.25 mm` axial gap.

## Deliberate deviations and omissions

- Natural-rubber tread and polypropylene core are one connected wheel envelope;
  their internal interface is not dimensioned.
- The wheel tread section, side recesses, hub, and shoulder crown are
  proportions; only catalog `d1` and `b` control the envelope dimensions.
- The dual bearing is represented only by separated upper/lower external race
  envelopes. Balls, raceways, grease, seals, and preload are omitted.
- The mounting plate is represented as a thin stamping: horizontal outer
  flange, broad smooth annular near-constant-gauge transition, and lower
  central platform. Both transition surfaces meet the horizontal regions
  tangentially and use the same control logic offset by `plate_t`.
  Its sink depth, transition radii, kingpin hole, and sheet gauge are
  proportions because the catalog does not publish them. No countersink or
  blind top-face recess is inferred.
- The catalog's `d2` is used only as mounting-slot width. Slot length is a
  proportion because it is not independently published.
- The real wheel axle diameter and hardware standard are not published. The
  axle, hex head, and nut are therefore proportioned envelopes, not ISO 4014,
  ISO 4032, or any other claimed standard size. Threads are omitted.
- Washers, wrench marks, coating, secondary fasteners, stamping ribs, bend
  radii, draft, and local blends are omitted.
- No brake, rigid bracket, center-hole mount, threaded stud, or animation is
  included.
