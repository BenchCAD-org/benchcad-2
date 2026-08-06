# guitar_tuning_machine_head — gear-train notes

The tuning machine is a crossed-axis worm drive: a single-start WORM on the
key shaft (button axis, along Y) drives a WORM WHEEL pressed on the string
post (along Z). One button turn advances the post by 1/z2 turn; the drive
self-locks so string tension cannot back-drive the button.

## Symbols → parameters → formulas

| symbol | meaning | formula in `part._gear` | source |
|---|---|---|---|
| z2 | wheel tooth count | `gear_ratio` (14 or 16) | Grover 102 series 14:1 (grotro.com); Gotoh SG381 1:16 (g-gotoh.com). Single-start worm ⇒ ratio = z2 |
| d_t2 | wheel tip diameter | `2*min(0.41*housing_h - 1.7, housing_d/2 - 2.1)` | proportion: wheel fills the chamber the casting allows |
| m | module | `d_t2 / (z2 + 2)` | standard tip relation d_t = m(z+2) |
| r2 | wheel pitch radius | `m*z2/2` | standard |
| px | axial pitch | `pi*m` | wheel circular pitch = worm axial pitch (crossed 90°) |
| d1 | worm pitch diameter | `key_shaft_d + 1.4*m` | proportion: worm cut on the key shaft blank |
| a | centre distance | `(d1 + m*z2)/2` | standard worm-drive relation |
| λ | lead angle | `atan(px / (pi*d1)) = atan(m/d1)` | single-start; `check()` bounds λ ≤ 7° for self-locking (machinery handbook rule of thumb: self-locking below ~6-8° with steel/zinc friction) |
| b | wheel face width | `min(7.5*m, 0.26*housing_h)` | proportion |

Verified against catalog: Gotoh SG381 (27.1 envelope row) draws z2 = 16 ⇒
one button turn = 1/16 post turn, matching the published 1:16 ratio; the
Grover rows draw z2 = 14 (102 series 14:1).

## Deliberate deviations

- Wheel teeth are straight trapezoidal-gap teeth (flanks 20°), not hobbed
  involute/globoid; the worm thread is a trapezoidal single-start thread.
  Flank clearance (thread 0.34·px vs gap 0.66·px + 0.06 absolute floor) is
  the working backlash; probes verify zero interpenetration through the full
  coupled rotation and real drive contact when the wheel is held.
- The worm thread is generated as 12 straight prism segments per turn
  (sagitta ≤ 0.1 mm, absorbed by the backlash): the pinned OCC 7.9 booleans
  silently no-op against helical swept solids, so a swept groove cannot be
  used in this environment.
- Wheel dimensions derive from the casting envelope (module is not a
  catalog column — vendors do not publish the internal gear data), with the
  RATIO row-locked to the catalog model.
- Thread run-out at the worm ends is a plain chamfered blank end (the worm
  ends inside the closed housing barrel).
