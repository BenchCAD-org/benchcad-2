# GN 1135 self-locking threaded lifting pin

This family locks every dimensional and load parameter to one of the five
official Ganter GN 1135 rows: M8, M10, M12, M16, or M20. Values from different
sizes are never recombined. Loads and maximum torque remain row metadata and do
not change the CAD geometry.

The public drawing supplies `d1`–`d5`, `h1`–`h4`, `k1`–`k3`, and `l1`–`l3`.
The supplied `1135-M8-12-ST.step` was inspected read-only for external evidence:
the M8 reference has a 68.0 x 141.617 x 38.0 mm upright envelope, a d38 rotating
head, d20 lower body, d6.62 lower pin core, a pivot axis at h3=25.7, and the
catalog shackle outline. Its center section was sampled to reconstruct the
forged outer eye, 46 x 42.5 opening, lower waist, rounded k1 section, and pivot
bosses. The guard was reconstructed as the observed d5 cylinder clipped by six
flats, with conical end transitions. The STEP is not imported by `build()` and
is not committed.

The pivot bore uses the measured approximately 10.3 mm clearance and a stepped
counterbore at each outer land for the larger pivot heads. The stationary post,
spring pocket, button cap, and interrupted thread slots include small running
clearances so the nine scored solids remain separate. On the M20 row the eye
cheek is scaled with a proportioned lower-neck offset and a short local relief
at the d59 head envelope; this is an explicit fit adjustment, not an additional
catalog dimension. The lower boss shoulder is a rounded square prism with
planar end cheeks, while the measured pivot bore, boss barrel, and outer land
remain cylindrical; this distinction follows the official section rather than
rounding the complete ear into one cylinder.

The benchmark uses a fixed nine-solid mechanism:

1. main stationary pin body;
2. rotating collar;
3. shackle;
4. transverse shackle pivot;
5. push button and central actuator as one solid;
6. return spring;
7. six-flat safety guard around the button;
8. two opposed retracting threaded segments.

`lock_state=0` is locked: the button and actuator are raised, the spring is at
its free modeled height, and both segment lands reach the nominal `d1`
envelope. `lock_state=1` is released: one deterministic button travel lowers
the actuator, compresses the spring by the same travel, and retracts both
segments inside the `d2` envelope. This coupling is ordinary deterministic
geometry, not independently sampled motion.

The exact wedge/cam surfaces, segment count, segment thread form, button travel,
spring wire diameter and turns, bearing construction, fits, and minor fillets
are not published. Their dimensions are therefore explicit `proportion`
approximations. The four straight segment lands are a visual interrupted-thread
cue, not a claim that the production thread is non-helical.

The shackle swivels about its transverse pivot over the documented 180 degrees.
The collar, guard, pivot, and shackle rotate together through a complete turn
around the stationary threaded-pin axis, so this motion cannot unscrew the pin.

Assembly linkage is represented by deterministic transforms rather than hidden
CAD constraints: `main_pin_body` is stationary; `rotating_collar`,
`safety_guard`, `shackle`, and `shackle_pivot` share the axial rotation; the
shackle additionally swivels about its transverse pivot axis. The button,
return spring, and opposed threaded segments remain coaxial with the stationary
body. Button travel, spring compression, and segment retraction are coupled by
the same `lock_state` input, while the exact production cam/bearing mates remain
unpublished proportions.
