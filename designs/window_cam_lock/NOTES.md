# window_cam_lock engineering notes

This family contains two discrete AmesburyTruth catalog rows. Official row
dimensions are copied together by `refine()` and are never sampled
independently.

## Official references

- 17.23.XX.200 EntryGard drawing:
  <https://www.amesburytruth.com/downloads/products/AT%20WSH%2017.23.XX.200%2017%20Series%20Entrygard%20Locks.pdf>
- 17.32.XX.200 Trimline drawing:
  <https://www.amesburytruth.com/downloads/products/AT%20WSH%2017.32.XX.200%2017%20Series%20Trimline%20Locks.pdf>
- 17.23 product page:
  <https://www.amesburytruth.com/products/windows/hung/locks/cam-locks/zinc/cam-locks-17-series-entrygard>
- 17.32 product page:
  <https://www.amesburytruth.com/products/windows/hung/locks/cam-locks/zinc/cam-locks-17-series>

## Vertical-stack recalculation

### 17.23.XX.200

- lower tier / end pad: 12.7 mm
- middle-deck top: 13.5 mm
- overall boss top: 23.1 mm
- modeled deck rise: `13.5 - 12.7 = 0.8 mm`
- modeled boss rise: `23.1 - 13.5 = 9.6 mm`
- stack check: `12.7 + 0.8 + 9.6 = 23.1 mm`

### 17.32.XX.200

- two end mounting feet: `2X 6.4 mm`
- lower central body: 11.3 mm
- middle-deck top: 12.5 mm
- overall boss top: 20.1 mm
- modeled deck rise: `12.5 - 11.3 = 1.2 mm`
- modeled boss rise: `20.1 - 12.5 = 7.6 mm`
- central stack check: `11.3 + 1.2 + 7.6 = 20.1 mm`

The enlarged 17.32 drawing shows that the `2X .25 in [6.4 mm]` leader points
to the two end mounting feet. It does **not** dimension the alignment lugs.
No published lug height was found, so the lug geometry is explicitly
proportion-based.

## Mounting-hole and countersink recalculation

Both rows specify 65.9 mm overall length, 52.4 mm hole spacing, 4.3 mm through
bores, and an 11.1 mm hole-center offset from the nearer long edge.

The manufacturer drawing does not dimension a countersink major diameter or
angle. This model deliberately uses an 8.0 mm major diameter and a single 82
degree included angle, based on the legacy Truth recommendation for a #7
Phillips flat-head inch screw and the visible product proportions.

- end center land: `(65.9 - 52.4) / 2 = 6.75 mm`
- end countersink edge margin: `6.75 - 8.0 / 2 = 2.75 mm`
- near long-edge margin: `11.1 - 8.0 / 2 = 7.10 mm`
- 17.23 far long-edge margin: `28.6 - 11.1 - 8.0 / 2 = 13.50 mm`
- 17.32 far long-edge margin: `26.2 - 11.1 - 8.0 / 2 = 11.10 mm`
- 82 degree countersink depth:
  `(8.0 - 4.3) / (2 * tan(82 deg / 2)) = 2.13 mm`
- 17.23 residual end-pad thickness: `12.7 - 2.13 = 10.57 mm`
- 17.32 residual end-foot thickness: `6.4 - 2.13 = 4.27 mm`

The mounting-hole Y coordinate is
`-body_width / 2 + 11.1`, rather than being placed on the body centerline.

## Proportion formulas

Every formula below is labeled `proportion` in `spec.py`; none is presented as
an AmesburyTruth production dimension.

- clipped base-corner setback: `0.10 * body_width`
- central housing outside width: `0.82 * body_width`
- shallow cavity/opening height: sampled `cavity_h`; easy 4.4 mm,
  medium 4.0-4.8 mm, hard 3.8-5.2 mm
- central cavity length: `housing_length - 2 * closed_wall_t`
- asymmetric cavity width:
  `0.82 * body_width + 1.0 mm - closed_wall_t`
- asymmetric cavity Y center: `-(1.0 mm + closed_wall_t) / 2`
- the negative-Y long side is open; the positive-Y long side and both short
  ends retain `closed_wall_t`
- retained material above the cavity: `deck_h - cavity_h`
- pivot X offset from body center: `0.10 * body_length`
- pivot boss diameter: `0.48 * body_width`
- simplified spindle diameter: `0.16 * body_width`
- spindle radial clearance: 0.20 mm
- rotating-cap axial clearance above the deck: 0.20 mm
- lever middle thickness: `0.48 * lever_t`
- lever root-plan transition: `-0.18 * lever_length`
- lever free-end step starts at: `-0.76 * lever_length`
- lever shoulder half-width at that transition:
  `0.42 * lever_tip_width`
- lever root thick-step length: `0.22 * lever_length`
- lever free-end thick step uses the exact upper-plan boundary from
  `-0.76 * lever_length` to `-lever_length`; it is the same tapered/widened
  outline extruded downward by `lever_t - 0.48 * lever_t`
- 17.32 lug length: `0.11 * body_length`
- 17.32 lug width: `0.055 * body_width`
- 17.32 lug height above the mounting plane: `0.28 * end_pad_h`
- 17.32 lug longitudinal centers: `+/- 0.28 * body_length`; both lugs are
  located on the same long edge, matching the official top view

## Components and visual assembly

`family.json` declares two physical components, and their names exactly match
the stable child names returned by `cq.Assembly`:

| Component builder | Assembly child | Quantity |
|---|---|---:|
| `build_fixed_body()` | `fixed_body` | 1 |
| `build_rotating_body()` | `rotating_body` | 1 |

The image-first assembly sequence is committed as `preview_parts.png`.
Successive panels highlight each component in the assembled context, then show
the rotating body exploded in `+Z` and inserted back along `-Z`, followed by
the final two-color assembly. The spindle and fixed-body pivot bore share the
axis at `X = 0.10 * body_length`, `Y = 0`. Final seating preserves 0.20 mm
radial clearance around the spindle and 0.20 mm axial clearance between the
fixed deck and rotating cap.

## Engineering constraints

- Every official dimension and the lug state must equal the complete selected
  product row.
- The 8.0 mm countersink must retain at least 2.5 mm of material to all outside
  edges and at least 0.75 mm to the central housing envelope.
- Countersink depth must leave at least 1.5 mm of mounting-pad floor.
- `cavity_h` is independent of `closed_wall_t`; changing a wall thickness cannot
  deepen the opening or pierce the roof.
- The shallow cavity must stop at least 1.0 mm below the selected row's end-foot
  top and retain at least 6.5 mm to the official deck top.
- Both short-end walls and the opposite long-side wall must remain closed.
- `deck_h > body_h` and `overall_h > deck_h`.
- The lever free end must be wider than the neck.
- The downward lever tip step must clear the middle deck by at least 0.75 mm.
- The handle is allowed to overhang the body during its modeled 0-90 degree
  travel; vertical clearance prevents contact with the fixed deck and feet.
- The fixed housing and rotating handle/spindle are exactly two non-intersecting
  solids separated by 0.20 mm axial/radial bearing clearances.

## Deliberate deviations and omissions

- EntryGard 17.23 and Trimline 17.32 share one benchmark family because their
  external architecture and official hole pattern are the same; `product_row`
  preserves their distinct dimension stacks and lug state.
- The model captures the external die-cast envelope, a shallow one-side-open
  mechanism bay, the opposite closed long wall, closed short ends, three height
  tiers, and stepped lever.
- It is a two-body assembly: one fixed housing and one rotating
  lever/cap/spindle body.
- The alignment-lug location and dimensions are proportional because the
  official 17.32 drawing/product resource confirms the feature but does not
  publish its dimensions. Lugs start at `Z=0`; they do not project below the
  flat mounting plane.
- The 8.0 mm countersink major diameter is a deliberate approximation. The
  official 4.3 mm through bore remains exact.
- The production lever's fillets, draft, texture, and local curvature are
  simplified into a continuous planform with abrupt lower root/tip steps.
- A simplified cylindrical spindle is included only to establish the second
  rotating body. Internal cam profile, spring, snap-back, fasteners, stops, and
  production wall ribs are omitted because no manufacturing dimensions were
  published.
- Casting draft, small rounds, embossed marks, and finish variants are omitted.
