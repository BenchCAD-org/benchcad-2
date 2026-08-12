# GN 490 implementation and assembly notes

This family implements the aluminum JW Winco GN 490 swivel clamp connector
joint proposed in Issue #57. It is a fixed-pose, seven-component `cq.Assembly`,
not a motion simulation.

## Sources

- Product page: <https://www.jwwinco.com/en-us/products/3.7-Connecting-assembling-with-clamping-and-connecting-elements/Tube-clamp-connectors/GN-490-Aluminum-Swivel-Clamp-Connector-Joints>
- Official metric dimension PDF: <https://live-catalog.jwwinco.com/pdf/winco/us/490.pdf?dispositiontype=attachment>
- Official engineering drawing: <https://live-catalog-cdn.jwwinco.com/svg/winco/2b652d595047898141ca5e84699bf940/GN-490-Aluminum-Swivel-Clamp-Connector-Joints-sketch.svg>
- Family proposal and reference images: <https://github.com/BenchCAD-org/benchcad-2/issues/57>

The source publishes eight equal-diameter rows, Types A/B, aluminum finishes
MT/SW, and the V-groove and pressure-spring functions. It identifies the body,
DIN 912 socket screw, DIN 934 hex nut, adjustable lever, pressure spring, and
insert/distance bushing. It does not publish a swivel-angle range, V-groove
detail, body-bore clearance, spring construction, bushing profile, or the
secondary Type A/Type B fastener dimensions.

## Datasheet symbols to parameters

| Datasheet | Build parameter | Treatment |
|---|---|---|
| `d1`, `d2` | `clamp_d` | One catalog key; only `d1=d2` rows are allowed |
| `d3` | `thread_d` | Exact selected-row lookup |
| `d4` | `body_d4` | Exact selected-row lookup |
| `l1` | `body_l1` | Exact selected-row lookup |
| `l2` | `lever_l2` | Exact selected-row lookup; Type B axial envelope |
| `l3` | `lever_l3` | Exact selected-row lookup; Type B radial envelope |
| `l4` | `jaw_l4` | Exact selected-row lookup; thickness of each complete body |
| `l5` | `gap_l5` | Exact selected-row lookup; separation between the bodies |
| `m` | `catalog_m` | Exact selected-row lookup; clamping-axis spacing |
| Type A/B | `actuator_type` | `0` = A, `1` = B |

`refine()` copies all eight dependent dimensions from one row selected by
`clamp_d`. It never interpolates, independently samples, or mixes rows.

## Table transcription and recomputation

| `clamp_d` | `d3` | `d4` | `l1` | `l2` | `l3` | `l4` | `l5` | `m` | `2*l4+l5` | `d1+l5` |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | 6 | 28 | 33 | 35 | 45 | 14 | 5 | 13 | 33 | 13 |
| 10 | 8 | 32 | 45 | 45 | 63 | 20 | 5 | 15 | 45 | 15 |
| 12 | 8 | 36 | 47 | 45 | 63 | 21 | 5 | 17 | 47 | 17 |
| 14 | 8 | 46 | 57 | 55 | 78 | 25.5 | 6 | 20 | 57 | 20 |
| 15 | 10 | 46 | 57 | 55 | 78 | 25.5 | 6 | 21 | 57 | 21 |
| 16 | 10 | 46 | 57 | 55 | 78 | 25.5 | 6 | 22 | 57 | 22 |
| 18 | 10 | 56 | 63 | 55 | 78 | 28.5 | 6 | 24 | 63 | 24 |
| 20 | 10 | 56 | 65 | 55 | 78 | 28.5 | 8 | 28 | 65 | 28 |

The two identities hold for every published equal-diameter row:

- `l1 = 2*l4 + l5`
- `m = d1 + l5`

The second identity places the implied clamped-rod centers one radius inside
the two faces adjacent to the central gap. No independent center-distance or
mixed row can be sampled.

## Assembly axes and component map

The central screw/stud axis is `Z`. The lower body occupies
`[-l1/2, -l5/2]`, and the upper body occupies `[+l5/2, +l1/2]`. The lower
V-groove axis is `X`; the upper body uses the same construction rotated 90
degrees, so its V-groove axis is `Y`. This is the reference pose shown by the
catalog application graphic, not a claimed angular limit.

`build()` returns a named `cq.Assembly` whose seven child names exactly match
`family.json.components`:

1. `lower_clamp_body`
2. `upper_clamp_body`
3. `actuator`
4. `hex_nut`
5. `distance_bushing`
6. `lower_compression_spring`
7. `upper_compression_spring`

Each child is produced by an independent `build_<component>()` function. The
two clamp bodies are complete physical cast bodies, not four artificial axial
jaw slices. `actuator` is either the Type A socket screw or the Type B
adjustable-lever/stud purchased component. The DIN 934-like nut is an external
part. Both clamp bodies have only a round central passage; their outer faces
have no counterbore or hexagonal recess.

The nut and actuator head/hub touch the two outer body faces without positive
volume overlap. The round stud passes through round proportional-clearance
bores. The stud extends through nearly the full nut thickness. One circular
`distance_bushing` is centered in `l5` and has only its central round stud
bore—there is no eccentric hole. Two separate helical pressure springs are
coaxial with the actuator, one below and one above that bushing.

## Published Type B envelope

The drawing defines two orthogonal outer projections:

- `l2`: axial reach from the actuator-side body face to the handle's furthest
  axial edge;
- `l3`: radial reach from the central fastener axis to the handle's furthest
  radial edge.

The handle centerline is inclined in the axial/radial plane. Its rounded end is
backed off by the end radius so the finished solid, rather than only its
centerline, reaches the published `l2` and `l3` limits. The direction follows
the Type B drawing and product image. Local hub, shoulder, taper, thickness,
rounding, and the requested top-button hexagonal recess remain proportions.

## Proportion formulas

The following values are not published GN 490 dimensions:

| Detail | Formula | Purpose |
|---|---|---|
| Body passage radius | `0.60*d3` | Clear the nominal round stud |
| V-groove radial center | `-(0.50*d1 + 0.60*d3 + 0.02*d1)` | Clear the central stud passage while keeping the rod inside `d4` |
| V-groove depth | `(0.50 + 1/sqrt(2))*d1 + 0.02*d1` | 90-degree V tangent geometry plus proportional clearance |
| V-groove mouth | `2*groove_depth` | Contain the full nominal rod proxy at the inner face |
| Body end fillet | `min(0.035*d4, 0.18*l4)` | Approximate the rounded casting edge |
| Type A shaft/head | shaft radius `0.50*d3`; external-hex circumdiameter `1.60*d3`; head height `0.85*d3` | Review-requested visible hex head; undocumented envelope is `proportion` |
| Type A socket | hex circumdiameter `0.55*d3`; depth `0.45*head_h` | Visible socket only |
| Nut | height `0.80*d3`; circumdiameter `1.80*d3`; bore radius `0.54*d3` | Simplified separate DIN 934 envelope |
| Distance bushing | radius `0.46*d4`; height `0.24*l5` | Single visible circular middle separator |
| Distance-plate stud bore | `0.50*d3 + max(0.10, 0.02*d3)` | Clear the round stud |
| Each spring height | `0.30*l5` | Fit one spring on each side of the bushing |
| Spring mean/wire radius | `0.72*d3`; `min(0.045*d3, 0.035*l5)` | Clear the actuator and remain non-degenerate |
| Spring pitch | `spring_h/2.5` | 2.5-turn helical sweep without self-intersection |
| Spring/bushing/body clearance | `0.04*l5` | Separate all three central components |
| Type B handle thickness | `max(0.70*d3, 0.14*d4)` | Flat die-cast lever section |
| Type B handle width | `1.40*handle_t` | Simplified die-cast section |
| Type B profile thickness | `1.18*handle_t` at hub, `0.92*handle_t` at end | Simplified taper |
| Type B hub | height `1.35*d3`; radius derived from stud/handle width | Connect stud and handle |

Each pressure spring is a genuine CadQuery helix sweep. All 16 legal
catalog/actuator combinations produce two valid, non-degenerate spring solids
in the pinned CadQuery/OCP environment.

## Geometry and interference acceptance

Local acceptance must cover every one of the 16 allowed catalog/actuator
combinations (eight rows times Types A/B):

- Assembly root and seven semantic child names are stable.
- Every component contains exactly one non-degenerate solid.
- `family.json.solids == len(family.json.components) == 7`.
- Every pair of physical components has zero positive intersection volume.
- Round stud, body passage, nut bore, and bushing bore retain their documented
  proportional clearances.
- The central distance bushing and both coaxial springs are mutually separated
  by their modeled axial clearances.
- Both clamp bodies retain positive material behind the V-groove and around
  the central passage.
- A full-diameter nominal rod proxy at each published axis has zero positive
  intersection volume with its clamp body, the stud passage, and the middle
  distance plate.
- Type B actuator bounding boxes reproduce the published `l2`/`l3` envelopes.

`bench2 validate` is still the required final machine gate, but it does not
validate Assembly child names or pairwise collision volume. Those checks are
therefore included in the local acceptance report.

## Deliberate deviations and unresolved source detail

- Casting draft, texture, local ribs, small blends, chamfers, and parting lines
  are omitted.
- The V-groove angle, tip radius, depth, radial offset, and mouth are not
  dimensioned; the model records them as `proportion`.
- Threads, thread runout, exact DIN fastener tolerances, lever ratchet internals,
  and surface finishes are omitted.
- Type A retains the catalog's central fastener role and hex socket, but its
  outer head is deliberately modeled as the requested six-sided review shape
  rather than claiming an exact DIN 912 cylindrical-head reproduction.
- The single circular middle separator is a visual/proportional interpretation
  of the catalog image and the listed insert/distance-bushing item; its local
  profile is not dimensioned. It has no eccentric opening.
- The two pressure springs' exact wire, turn count, pitch, and end treatment are
  not published. Their coaxial helical geometry is proportional.
- MT/SW finish and the excluded stainless-steel NI material do not change CAD.
- Context rods/tubes are omitted from the seven delivered components.
- No swivel motion, allowable angle, load rating, fit class, or tolerance is
  invented.

The two-body topology, plain outer body faces, one central distance bushing,
and two coaxial springs supersede the earlier local
four-jaw/one-offset-spring approximation. This is a user-authorized visual
correction made during local acceptance and must be called out in the eventual
PR.
