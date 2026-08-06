# planetary_gear_stage_inline — derivations, and what is proportion

## What the standard fixes

Unusually for this benchmark, the tooth geometry is **fully determined by
published standards**, so most of this family is derived rather than tabulated.

| quantity | value | source |
|---|---|---|
| pressure angle α | 20° | DIN 867 / ISO 53 basic rack |
| addendum hₐ | 1.0 · m | DIN 867 |
| dedendum h_f | 1.25 · m | DIN 867 |
| module series | 0.5 / 0.6 / 0.8 / 1.0 / 1.25 / 1.5 / 2.0 | ISO 54 / DIN 780 |
| pitch diameter | d = m·z | DIN 3960 |
| base diameter | d_b = d·cos α | DIN 3960 |
| tip diameter, external | d + 2·hₐ·m | DIN 867 |
| tip diameter, internal | d − 2·hₐ·m | DIN 867 |

## The involute, and why the ring is generated as a space

A point on the involute at radius `r` lies at an angle from the tooth centreline of

```
half(r) = π/(2z) + inv(α) − inv(α_r),      inv(x) = tan x − x,  cos α_r = r_b / r
```

At `r = d/2` this collapses to `π/(2z)`, which is exactly what makes the tooth
thickness `π·m/2` at the pitch circle — the property that lets two gears of the
same module mesh at all.

**The ring gear is not "an external gear turned inside out."** An internal gear's
*tooth space* is congruent to an external tooth, so the internal tooth half-angle
is `π/z − half(r)`, and the profile runs from the root (which is the *outer*
radius here) inward to the tip. `_gear_profile(..., internal=True)` returns that
boundary and `_housing` cuts it from the housing cylinder. Generating the ring
any other way produces something that looks toothed but cannot mesh.

Both profiles are emitted as **one closed polyline for all z teeth** — leading
flank, tip land, trailing flank, then straight on to the next tooth — and
extruded once. Building tooth-by-tooth and unioning z solids is the obvious
alternative and it is much slower and much more fragile in OCC.

## Tooth counts are derived, not drawn

The catalogue offers single-stage ratios **i = 3, 4, 5** only. With
`i = 1 + z_ring/z_sun` and coaxiality `z_ring = z_sun + 2·z_planet`:

```
z_planet = z_sun·(i − 2)/2        z_ring = z_sun + 2·z_planet
```

| i | z_planet / z_sun | needs |
|---|---|---|
| 3 | 0.5 | z_sun even |
| 4 | 1 | — |
| 5 | 1.5 | z_sun even |

`refine()` computes both and raises `Resample` when the division is not whole,
when a planet would come out under 4 teeth, or when either of the two
admissibility conditions fails:

```
(z_sun + z_ring) mod n_planets == 0                     planets at equal pitch
(z_sun + z_planet)·sin(π/n_planets) > z_planet + 2      adjacent planets clear
```

Neither is a preference. The first decides whether the planets can be placed at
all; the second whether their tip circles foul. A stage that violates either
cannot be built, which is why they are in `check()` as well.

## Verification against an independent model

The envelope was cross-checked against **`punkfab/robot-actuators`** (MIT), an
independently authored, parametrically generated planetary set. Measured with
`bench2 anchor` and compared at the matching configuration (m = 0.9, z 12/12/36,
3 planets, i = 4):

| | this family | reference | Δ |
|---|---|---|---|
| sun tip envelope | 12.60 × 12.60 | 12.60 | 0 |
| planet | 12.60 × 12.60 × 4.00 | 12.60 × 12.60 × 4.00 | 0 |
| housing OD | 45.65 | 45.65 | 0 |

The tip diameters land exactly because both derive them the same way from the
same standard — `m(z + 2)` = 0.9 × 14 = 12.6. Volumes differ (planet 309.8 vs
275.6) because bore sizes and shaft lengths are proportions, not standard
values, and the two models chose differently. That is the expected outcome: the
standard-fixed geometry agrees to the digit, the unpublished proportions do not.

The reference was read as a measuring instrument only. No geometry was converted
from it and the file is not in this repository.

## Proportions — everything the standard does not fix

| quantity | value | basis |
|---|---|---|
| involute samples per flank | 14 | enough that the flank error is well under a render pixel at these sizes |
| housing rim | `0.16 × m·z_ring` over the ring root | proportion |
| planet pin diameter | `0.42 × m·z_planet` | proportion — a pin that fits under the planet root with a bearing seat |
| planet bore clearance | `0.12 × pin` | proportion |
| carrier disc thickness | `0.55 × face_width` | proportion |
| carrier hub diameter | `1.9 × pin` | proportion |
| sun shaft diameter | `0.62 ×` sun root diameter | proportion; `check()` also forbids it reaching the root circle |
| face width band | 3–16 × module | shop practice; this class runs about 6–12 × |

`carrier_angle` is an operating state, not a dimension. Each planet is counter-
rotated by `−angle · z_sun/z_planet` as the carrier turns so the teeth stay
meshed — without that the planets would slide through the sun in the preview.

## Body decomposition

Per the category rule (#178), bodies that never move relative to each other are
one solid:

- `housing_ring_gear` — the ring is machined into the bore, not pressed in
- `sun_shaft` — sun cut on the input shaft
- `carrier_output` — two discs, the planet pins and the output shaft
- `planet_gear` × `n_planets` — the only parts with a degree of freedom

Bearings are omitted. Four component types, `3 + n_planets` bodies.
