# single_row_deep_groove_ball_bearing notes

This family is table-driven and equation-heavy, so the mapping below is included
for human review under `REVIEWING.md`.

## Source categories

- **standard:** ISO 15:2017 radial bearing boundary-dimension family, represented
  here by the real 6000-series catalog rows.
- **catalog table:** the provided 6000-series table supplies `d`, `D`, and `B`
  for 6000-6005.
- **reference-image calibrated:** only the 6000 rolling-element count, ball
  diameter baseline, and pitch-circle baseline are calibrated from the supplied
  TraceParts 6000 PNG views.
- **proportion:** all unverified internal values, including raceway depth, cage
  dimensions, and all 6001-6005 internal rolling-element layouts.
- **benchmark perturbation:** small deterministic sample variation added in
  `refine()` around the 6000 image-calibrated baseline and around the
  proportion rows. These perturbations represent dataset variation, not
  image-fit uncertainty or manufacturer tolerance.

## ISO / catalog symbol mapping

| Source symbol | Code parameter | Meaning |
|---|---|---|
| `d` | `bore_d` | bearing bore diameter |
| `D` | `outer_d` | bearing outside diameter |
| `B` | `width` | bearing width |
| 6000-6005 row | `designation` | selector for the coupled `d/D/B` catalog row |

The table rows are coupled in `spec.py`: `designation` selects `bore_d`,
`outer_d`, and `width`. The sampler must not produce mixed rows such as a 6000
bore with a 6005 outside diameter.

## 6000 image-calibrated ball geometry

The supplied 6000 axial reference PNG was used for a circle fit of the seven
visible rolling balls. The outer bearing diameter is known from the table:
`D = 26 mm`.

Measured pixel anchors:

- outer diameter: `P_D = 1228 px`
- mean fitted ball diameter: `P_ball = 228.31 px`
- mean pitch radius: `R_pitch = 426.10 px`
- fitted ball count: `7`

Manual recomputation for the 6000 row:

- `ball_d = 26 x 228.31 / 1228 ~= 4.83 mm`
- `pitch_d = 2 x 26 x 426.10 / 1228 ~= 18.04 mm`

Only these 6000 ball layout values are reference-image calibrated. They are not
claimed to be universal SKF internal dimensions for every 6000-series bearing.

## 6001-6005 internal values

No reliable model-specific CAD section or manufacturer table was available for
the internal ball, raceway, and cage geometry of 6001-6005. Their internal rows
therefore remain `proportion` values chosen to fit inside their real `d/D/B`
envelopes, keep clearance between bodies, and provide meaningful benchmark
variation. They must not be described as SKF, TraceParts, or manufacturer
measured internal dimensions.

## Derived ring and raceway construction

The code keeps the inner and outer rings as continuous solids:

- `span = outer_d - bore_d`
- `inner_shoulder_d = bore_d + 0.30 * span`
- `outer_race_d = outer_d - (3.4 / 16.0) * span`

For the 6000 row, these normalize the SKF-style section anchors:

- `inner_shoulder_d = 10 + 0.30 * 16 = 14.8 mm`
- `outer_race_d = 26 - (3.4 / 16) * 16 = 22.6 mm`

These shoulder relationships are then reused as proportions for 6001-6005. The
raceways are simplified toroidal cuts on the facing ring surfaces:

- `race_clearance = ball_d * 0.04`
- `groove_r = ball_d / 2 + race_clearance + race_groove_depth * 0.04`

`race_groove_depth` is not image-derived. It is a proportion constrained by
ring-wall continuity and ball-envelope clearance.

## Cage construction

The cage is a simplified one-piece retainer:

- radial band limits: `pitch_d - cage_t` to `pitch_d + cage_t`
- pocket clearance: `cage_clearance = ball_d * 0.10`
- two narrow side rails are joined by bridge ribs between adjacent balls
- each ball pocket is cut by an oversized sphere centered on the ball center

This is a benchmark-readable simplification of an open bearing cage. It keeps
the cage as one solid, preserves visible ball pockets, and avoids positive
intersection with balls or rings. It does not model exact stamped-cage pocket
geometry.

## Deliberate deviations and limitations

- Internal rolling-element, raceway, and cage dimensions are not ISO 15 boundary
  dimensions.
- 6001-6005 internal values are proportion estimates.
- Raceway curvature and cage pocket details are simplified for stable CadQuery
  generation and visual recognizability.
- Edge chamfers from the 6000 reference are recorded as evidence but are not
  modeled as a separate parameter in this first version.
- `da`, `Da`, and `ra` are mounting/abutment recommendations and are not part of
  the modeled bearing body.
- There is currently no reliable DWG parser or true CAD section-measurement
  chain in this local workflow; the only internal calibration used here is the
  6000 PNG circle-fit baseline described above.
