# simpson_gear_set

Two ordinary planetary stages on ONE common sun, with the stage-1 carrier bolted
to the stage-2 ring.

## Why this is not two copies of `planetary_gear_stage_inline`

Both stages are ordinary planetaries, and that is exactly the point of separating
them: the #182 admissibility conditions carry over **unchanged and per stage**,
unlike the compound trains (#186 stepped planet, #187 dual ring) where they do
not. What is new is one coupling, and it buys a ratio ladder out of a single
gearset:

| gear | driven | held | ratio | at z_s 30, z_r1 = z_r2 = 72 |
|---|---|---|---|---|
| 1st | ring 1 | carrier 2 | `(z_r1 + z_r2 + z_s) / z_r1` | 29/12 = 2.417 |
| 2nd | ring 1 | sun | `1 + z_s / z_r1` | 17/12 = 1.417 |
| 3rd | ring 1 **and** sun | — | 1 (direct) | 1 |
| rev | sun | carrier 2 | `-z_r2 / z_s` | −12/5 = −2.400 |

All four were solved from a 5-equation Willis system in exact rational arithmetic
on three tooth sets before being written down. Note 2nd is `1 + z_s/z_r1`, **not**
`1 + z_r1/z_s`: the ring is the input here, not the carrier, and writing that
relation the familiar way round is the easiest mistake in this family.

3rd gear is an **overdetermined check** and worth keeping: pin both the sun and
ring 1 to 1 and every member — planets included — must come out at exactly 1. It
exercises all five equations at once and catches a sign error anywhere.

## The coupling is computed, not drawn

`carrier1_ring2_output` is ONE solid: the stage-1 carrier plate, its planet pins,
the stage-2 ring teeth cut into the inside of a drum, and the output flange. They
never move relative to one another, so they are one body — and modelling it that
way makes the family's defining feature visible as a single component in
`preview_parts.png`.

`member_angles()` then solves every member's absolute angle from the OUTPUT angle
through the 1st-gear mesh relations:

```
a_sun = -a_out * z_r2 / z_sun                    stage 2, carrier 2 held
a_p2  =  a_out * z_r2 / z_p2
a_p1  =  a_out - (z_sun/z_p1) * (a_sun - a_out)  stage 1, carrier 1 = output
a_r1  =  a_out + (z_p1/z_r1) * (a_p1 - a_out)
```

and `a_r1 / a_out` comes out equal to the closed form `(z_r1+z_r2+z_s)/z_r1`
exactly, on every tooth set checked. So `output_angle` is a real operating state:
turn it and the whole set moves consistently, rather than the members being posed.

## Tooth phase

`mesh_phase()` is carried over from #182 / PR #185 unchanged. `_gear_profile` puts
a tooth centre at angle 0 for both the external and the internal form, so a planet
on the +X axis needs a space facing the sun (local 180°) **and** a space facing
its ring (local 0°) — both are space centres only when `z_planet` is EVEN. For an
odd planet the RING takes a half-pitch shift instead:

```
z_planet even :  ring_phase = 0            planet_phase = 180 − 180/z_planet
z_planet odd  :  ring_phase = 180/z_ring   planet_phase = 0
```

**The shared sun costs nothing here.** The rule is derived against a sun with a
tooth at 0, and each stage has its own ring, so stage 2 picks its phases
independently of stage 1. The proposal issue flagged this as a possible extra
constraint; it is not one, and that is worth recording because it is the obvious
thing to worry about.

## Root radius

Carried over from PR #185, and it is the one thing that must not be "simplified"
back: the external root runs to the TRUE dedendum circle, not to the base circle.
Below 17 teeth at 20° the base circle sits **above** the dedendum circle, so
clamping the root there leaves the tooth space too shallow and drives every mating
tip into solid metal. It reads as a tolerance problem and is not one.

## Interference is measured, not assumed

Every pair of solids is intersected and the common volume measured, at
`output_angle` 0 and 37°: **zero overlap on every pair, both states**. `validate`
cannot catch this — two solids in the same place are individually valid — so it is
checked here rather than trusted.

## Members and where they leave

The sun and ring 1 leave to −Z (axis and rim); the output flange and the carrier-2
hub leave to +Z (rim and axis). Nothing can collide. A real Simpson gearbox routes
all four through concentric drums nested inside one another — that is a gearbox,
and this family is the gear set.

## Proportions the standard does not fix

| quantity | value | basis |
|---|---|---|
| involute samples per flank | 14 | measured in PR #185: 22 or 30 changes mesh interference by ~0.001 mm³ |
| circumferential backlash | `0.08 × module`, off the externals | real gears are cut with backlash (DIN 3967); zero-backlash is not a manufacturable condition |
| planet pin diameter | `0.34 × m·z_planet` | proportion |
| carrier plate thickness | `0.55 × face_width` | proportion |
| drum rim over the ring root | `0.16 × m·z_ring` | proportion |
| running clearance | 0.25 mm | proportion |
| axial member clearance | 0.35 mm | proportion |
| face width band | drawn, then clamped to 4–13 × module | shop practice; `check()` enforces the wider 3–16 × |

`face_width` is drawn and then brought into the band rather than resampled — a
freely drawn face width rejects almost every small-module draw, and the symptom
surfaces as a COVERAGE failure on `module`, not as an error about face width.

## Ratio band

`refine()` rejects tooth sets whose 1st gear falls outside 2.0–3.2 or whose 2nd
falls outside 1.2–1.8, and `check()` additionally requires 2nd < 1st. A Simpson
set exists to give a usable ladder; a tooth set that does not is the wrong
topology rather than a hard sample.
