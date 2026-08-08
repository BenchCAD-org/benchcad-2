# vertical_latch_toggle_clamp Notes

Source family: Ganter / JW Winco GN 851.1 steel vertical latch-type toggle
clamps with horizontal mounting base.

The sampled entry parameters are `clamp_size` and `with_u_bolt`. The drawing
symbol dimensions are all refined from a real catalog row so the sampler does
not invent invalid size combinations.

Table-driven dimensions:

- `a1`, `a2`
- `b1`, `b2`, `b3`, `b4`, `b5`
- `d1`, `d2`
- `h1`, `h2`
- `l1`, `l2`
- `m1`, `m2`, `m3`, `m4`, `m5`
- `r`, `s`, `w1`, `w2`

Assembly split:

- The submitted CadQuery model is a five-solid static assembly, matching the
  main solid count observed in the GN 851.1-160-T3 STEP reference.
- The solids are the folded base/frame, U-bolt latch rod, lower C-shaped fork,
  adjuster block, and handle/linkage pack.

Simplifications:

- Small hardware details such as split pins, spring wire, exact stamped-bend
  radii, and thread forms are proportion-derived visual approximations.
- The current STEP-matched rebuild targets the T3 form. The `with_u_bolt`
  parameter remains in the function signature, but validation samples the
  supplied T3 arrangement rather than adding a non-STEP substitute for type T.
