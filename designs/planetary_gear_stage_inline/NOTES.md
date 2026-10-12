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
| involute samples per flank | 14 | measured: raising it to 22 or 30 changes the mesh interference by 0.001 mm³, so 14 is not the limiting error |
| circumferential backlash | `0.08 × module`, taken off the external members | real gears are cut with backlash (DIN 3967 tolerance series). Measured contribution to mesh clearance is small; it is here because zero-backlash is not a manufacturable condition, not because it fixes anything |
| planet pin diameter | `0.34 × m·z_planet` | proportion — a pin that fits under the planet root with a bushing wall over it |
| bushing wall | `0.18 × pin`, floor 0.35 mm | proportion |
| carrier disc thickness | `0.55 × face_width` | proportion |
| carrier plate radius | pin circle + pin/2 + `max(0.4, 0.10 × pin)` | proportion, and the margin is load-bearing: making the plate tangent to the pins leaves a knife edge OCC cannot tessellate |
| planet end float | `max(0.15, 0.03 × face_width)` | proportion; it also keeps the carrier plate from sharing a face with the planets, which turns a contact into a boolean sliver |
| sun shaft diameter | `0.62 ×` sun root diameter | proportion; `check()` also forbids it reaching the root circle |
| face width band | 3–16 × module | shop practice; this class runs about 6–12 × |
| clamp hub OD | `1.85 × sun_shaft_d` | proportion |
| minimum wall over a bolt or bearing seat | 1.5 mm | proportion |

**`housing_od` is no longer a proportion.** It is now the larger of the old rim
formula and `housing_od_min()` — the diameter at which the tie bolts clear both
the ring root and the output bearing seat with a wall on each side. That function
lives in `part.py` and is called by `spec.refine()`, `spec.check()` and the build,
so the three cannot disagree about the wall.

**The bearings, the seal, the retaining rings and the screws are selected, not
proportioned.** `_BEARING_60` is ISO 15 / DIN 625-1 series 60, `_SEAL_A` is
DIN 3760 form A, `_SHCS` is ISO 4762. The output journal picks the smallest row
that accepts it; if the shaft runs off the top of the table the draw is rejected
rather than a bearing invented for it.

## Tooth phase and the rolling ratio — derived, then measured

Two things here were wrong in the first revision and are worth writing down,
because neither is visible in any rendered view.

**The planets were on the wrong rolling ratio.** The old code spun each planet by
`−angle · z_sun/z_planet`. That is the planet's speed *relative to the carrier*.
With the ring held, the absolute planet rotation is

```
w_planet / w_carrier = 1 − z_ring/z_planet = −(z_sun + z_planet)/z_planet
```

**And the sun was never rotated at all.** With the ring held, a carrier at
`carrier_angle` implies a sun at `(1 + z_ring/z_sun) · carrier_angle`. Leaving it
still is not a still picture of the mechanism; it is a picture of the sun's teeth
driven through the planets'.

**The tooth phases have to satisfy two meshes at once.** `_gear_profile` puts a
tooth centre at angle 0 for both the external and the internal form. A planet on
the +X axis needs a tooth space facing the sun (local 180°) and, against a ring
with a tooth at 0°, a space facing the ring too (local 0°). Both are space centres
only when 180° is a whole number of space pitches — that is, only when
`z_planet` is **even**. For an odd planet the ring takes a half-pitch shift
instead and the planet presents a tooth to the ring, a space to the sun:

```
z_planet even :  ring_phase = 0          planet_phase = 180 − 180/z_planet
z_planet odd  :  ring_phase = 180/z_ring planet_phase = 0
```

This was checked rather than assumed: sweeping the planet phase ±half a tooth
about the derived value, the mesh interference volume is a symmetric minimum
exactly at it, in both the even and the odd branch.

## The undercut that made every mesh interfere

The first revision clamped the external root radius to the **base** circle:
`r_root = max(r_pitch − 1.25m, r_base)`. Below 17 teeth at 20° the base circle
sits *above* the dedendum circle, so that clamp leaves the tooth space too
shallow and the mating tip drives into solid metal. Every sun/planet and
planet/ring pair interfered, by 2–15 mm³ each.

It looked like a tolerance problem and it is not one — tripling the backlash
moved it by 25% and doubling the flank sampling moved it by 0.05%. The flank now
runs to the true dedendum circle; `_half_angle` clamps `r` to `r_base`, so below
the base circle the profile continues as a radial line, the usual stand-in for
the trochoid. Mesh interference then measures **exactly zero**.

## Three ways one small part fell apart

The input clamping hub is a C-ring with a slit and a screw across it, and it took
three separate fixes to stay a single body. All three showed up in `validate` only
as "produced 59 solid(s) but the family declares 57":

1. **The clamp screw was drilled down the axis.** It has to pass through a boss
   beside the slit, not through the bore.
2. **The screw envelope reached back inside the tube wall**, which cuts a slot
   through the wall for its whole length and severs the ring. The boss is now
   placed so the hole clears the outside diameter.
3. **The boss was shorter than the screw diameter**, so its own hole cut it in
   half and the two ears fell off. `clamp_boss_h()` now sizes the boss from the
   screw and `clamp_length()` sizes the hub from the boss.

A fourth, found by the interference check rather than the solid count: **the boss
is a box, so its corners sweep further than its radial extent**, and the adapter
cavity has to clear `hypot(boss_r, boss_w/2)` rather than `boss_r`.

## Interference is checked, not assumed

Every pair of solids in the assembly is intersected and the common volume
measured, at both the smallest and the largest instance. The result is 0 for
every pair. This is worth doing because `bench2 validate` cannot catch it: it
checks solid count and non-degeneracy, and two solids occupying the same space
are individually perfectly valid. The first revision shipped a carrier with
**31% of its volume inside the housing** and passed 12/12.

## Body decomposition

Per the category rule (#178), bodies that never move relative to each other are
one solid:

- `housing_ring_gear` — the ring is machined into the bore, not pressed in; the
  rear wall and the tie-bolt holes are the same body
- `sun_shaft` — sun cut on the input shaft
- `carrier_output` — the plate, the planet pins, the bearing journal and the
  output shaft. There is deliberately **no hub on the gear side**: the sun
  occupies that axis
- `output_bearing_head` — bearing seats, seal seat and the machine mounting
  flange are one casting
- `motor_adapter`, `input_clamp_hub`, `output_shaft_seal`
- `planet_gear`, `planet_bushing`, `planet_retaining_ring` × `n_planets`
- `output_bearing_inner`, `output_bearing_outer` × 2, `output_bearing_ball`
- `case_screw` × `n_case_screws`

Fourteen component types. The body count runs 38 to 57 across the difficulty
range — `bench2 validate --seeds 2` measured 38, 40, 44, 47, 48 and 57. The
largest is six planets with eight tie bolts and a twenty-ball bearing pair:
1 housing + 1 sun + 1 adapter + 1 clamp hub + 1 head + 1 seal + 1 carrier
+ 6 planets + 6 bushings + 6 rings + 2 + 2 races + 20 balls + 8 screws = 57.

**The sun is deliberately not carried on its own bearing.** A floating sun is how
this class shares load between the planets — the clamping hub and the motor shaft
are its only support. That is why the hub is modelled: it is what makes the
floating sun an explicit design decision rather than a missing part.

**The planet bushing is flanged** rather than a plain sleeve plus two loose thrust
washers. Both are real constructions; the flanged one is one body per planet
instead of three, and it puts the thrust face where the load actually is.
