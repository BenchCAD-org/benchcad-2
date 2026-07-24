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

Simplifications:

- The part is modeled as one connected solid for deterministic validation, not
  as a moving assembly of separate stamped and pinned pieces.
- Small hardware details such as nuts, grip ribs, split pins, spring wire, bend
  radii, and thread forms are proportion-derived visual approximations.
- Type T is represented by a hook/catch feature without the U-bolt; type T3
  includes the U-bolt latch and catch.
