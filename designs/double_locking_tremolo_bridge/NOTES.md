# double_locking_tremolo_bridge — frame, derivations, and what is proportion

References: Gotoh dimension sheets
[GE1996T](https://g-gotoh.com/images/pdf/GE1996T-Dim.pdf) and
[GE1996T-7](https://g-gotoh.com/images/pdf/GE1996T-7-Dim.pdf), plus the
[product page](https://g-gotoh.com/product/ge1996t/?lang=en).

**There is no dimensional standard for this part.** Guitar bridges are defined by
manufacturer systems, not by ISO/DIN/JIS. Everything the sheets dimension is
cited; everything else is declared `"proportion"` and listed at the bottom.

## Frame — and how it was pinned

Getting the long axis wrong is the easy mistake here, so it was settled from the
numbers before any geometry was written:

- **X is across the strings.** The 91.5 mm span, the 74 mm post spacing and the
  10.8 mm string pitch all lie on it.
- **Y runs along the strings** (36 mm depth).
- **Z is up**; the sustain block hangs −Z.

Three independent checks agree:

1. the elevation's stations **19 + 50 + 20 + 2.5 = 91.5**, so 91.5 is subdivided
   by the elevation and is therefore the width that view spans;
2. **54 < 74 < 91.5** — string span inside post spacing inside plate span. Only
   this assignment nests;
3. the 7-string sheet repeats the pattern at **64.8 < 84.8 < 102.3**, and prints
   its string span explicitly as `64.8 = 10.8 × 6`.

`base_plane` is `XY`.

## The two axes

| quantity | GE1996T (6) | GE1996T-7 (7) | in the model |
|---|---|---|---|
| plate span | 91.5 | 102.3 | `plate_span`, filled by string count |
| plate depth | 36 | 39 | `plate_depth`, filled by string count |
| post spacing | 74 | 84.8 | `post_spacing`, filled by string count |
| saddle radius | R350 | R430 | `saddle_radius`, filled by string count |
| string pitch | 10.8 | 10.8 | shared |
| plate thickness | 3.2 | 3.2 | shared |
| knife-edge height | 8.6 | 8.6 | shared |
| saddle | 10.8 × 32.3 | 10.8 × 32.3 | shared |
| post thread / length | M8, 30 long | same | shared |
| tremolo arm | ø5.5 (side view) | same | not modelled |
| insert bushing | ø11.3 × 30 | same | shared |
| sustain block height | 33 / 36 / 40 | 33 / 36 / 40 | `block_height`, independent ladder |

So the family varies on **string count** and **block height**, and holds the
whole hardware interface fixed. That is the real structure of the product line,
and it is why `n_strings` selects a size rather than the dimensions being drawn
independently — a 7-string plan on 74 mm posts is not a product.

## Derived, not tabulated

**Saddle heights.** The sheets give one saddle detail and one radius, not six
heights. The saddle tops lie on a cylinder of radius `saddle_radius`, so a
saddle at distance `x` from the centreline drops by

```
drop(x) = saddle_radius − sqrt(saddle_radius² − x²)
```

For the 6-string (R350, outer saddle at 27 mm) that is 1.04 mm; for the
7-string (R430, outer at 32.4 mm) 1.22 mm. `check()` rejects any combination
where the drop exceeds what the knife boss height allows, which is what would
happen if a tight radius were paired with a wide span.

**String span.** `string_pitch × (n_strings − 1)` — 54 and 64.8, the second
printed on the sheet as the identity itself.

## `pivot_angle` is a state, not a dimension

The plate rocks on two hardened knife edges bearing on the post heads. The
sheets draw the bridge level and do not dimension the travel, so `pivot_angle`
is declared `"proportion"` and treated the way `jaw_open_fraction` is in
`three_jaw_scroll_chuck`. **Only the plate and what it carries rotate** — the
posts and insert bushings are set into the guitar body and stay put. The
rotation axis is an X line through the knife-edge line at the plate underside.

## Proportions — everything the sheets do not publish

| quantity | value | basis |
|---|---|---|
| knife-edge line position | `0.14 × plate_depth` from the back edge | proportion, read off the plan view |
| saddle row position | `0.42 × plate_depth` from the front edge | proportion, read off the plan view |
| clamp block height | `0.34 × saddle height` | proportion |
| clamp screw diameter | `0.30 × string pitch` | proportion |
| sustain block width | `0.55 × plate_span` | proportion; `check()` also requires it to clear the bushings |
| sustain block depth | `0.62 × plate_depth` | proportion |
| post head diameter | `1.5 × post shaft` | proportion — the head is the bearing surface the knife edge rides |
| plate corner radius | `0.055 × plate_span` | proportion; the sheet marks R5 on a 91.5 plate, which is 0.055 |
| saddle width / slot | `0.86` / `0.30 × string pitch` | proportion |

## CadQuery notes for anyone editing this

`revolve` bit this family and its sibling `snatch_block_single_sheave` three
different ways. All three produce a *silently wrong* result rather than an
error at the call site:

1. **The axis is given in the workplane's LOCAL coordinates.** On a
   `Workplane("XZ")`, local z is the plane normal (world −Y), so passing
   `(0, 0, 1)` revolves about world −Y, not world Z. World Z is local
   `(0, 1, 0)` there. The wrong axis is perpendicular to the section plane and
   sweeps out a zero-volume face; the failure only surfaces later as a
   degenerate body.
2. **The section plane must contain the axis.** A radial/axial section drawn in
   XY cannot be revolved about Z — the axial coordinate gets swept around the
   axis and the result is a flat annulus.
3. **`.center()` before `.revolve()`** moves the local origin and drags the axis
   onto the section's own centre (`BRep_API: command not done`), and a section
   that already closes on itself must not be `.close()`d — the zero-length edge
   makes the revolve return empty. `cq.Solid.makeTorus` sidesteps both.

The knife-edge ridge is unioned into the plate with a half-thickness overlap
rather than butted at the plate underside: two coincident faces are the case OCC
unions least reliably.

## Reference images

`docs/assets/refs/double_locking_tremolo_bridge_drawing.png` — the GE1996T
(6-string) dimension sheet — is on main and is what the numbers below are
measured against.

The **GE1996T-7** sheet (`GE1996T-7-Dim.pdf`) is the source for the 7-string
row and is **not yet in the repo**. It cannot be added here: a family PR is
scoped to its own `designs/` directory, and reference assets land on main via
the family issue. Until it does, the 7-string figures (`plate_span` 102.3,
`plate_depth` 39, `post_spacing` 84.8, `saddle_radius` 430) are checkable only
against <https://g-gotoh.com/images/pdf/GE1996T-7-Dim.pdf>.

## The post: a mis-attributed callout, and an assembly that could not assemble

`post_shaft_d` was 5.5, sourced to "sheet callout ø5.5". **That callout is in
the SIDE view and belongs to the tremolo arm.** Blown up, the post detail
carries only **M8** and **30** — no ø5.5 anywhere near it — and a ø5.5 blank
cannot carry an M8 thread in the first place.

The consequence was not just a thin post. `_POST_HEAD` was 1.5, so the bearing
head came out **ø8.25** against a bushing bore of `5.5 × 1.12 =` **ø6.16**: the
post could not pass through the bushing it screws into. The detail draws the
head **narrower** than the M8 body — about ø6.8 on ø8, waisted under a small
domed tip — which is the opposite proportion.

Now: thread ø8 (M8), head 0.85 × thread, length 30 as dimensioned, bushing
bored `post + 0.4` (wall 1.45, against the real ~1.65 on a ø11.3 bushing).
