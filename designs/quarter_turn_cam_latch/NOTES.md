# quarter_turn_cam_latch — sheet dimension → parameter → formula

Reference: `docs/assets/refs/quarter_turn_cam_latch_drawing.png` (Southco E5,
tool operated, short housing, fixed grip) and `..._photo.png`. Issue #32.

The E5 sheet labels its dimensions with values, not letters, so the "symbol"
column below is the value as it is printed on the drawing.

## Dimensioned on the sheet

| On the sheet | Parameter | Catalog value | Notes |
|---|---|---|---|
| `Ø 28 (1.10)` | `head_d` | 28 | head above the panel; mini 22 |
| `5 (.20)` | `head_h` | 5 | mini knob 12.2 |
| `Ø 22.5 +0.5/-0` | `body_d` | 22.5 | panel cutout circle; mini 16.3 |
| `□ 20.1 +0.1/-0` | `afl` | 20.1 | cutout across-flats; mini 14.1 |
| `27.2 (1.07)` | `body_l` | 27.2 | see "the 27.2 datum" below |
| `45 (1.77)` | `cam_l` | 45 | **centreline to cam tip**; mini 33 |
| `23 (.91)` | `tip_flat` | 23 | flat past the step |
| `19 (.75)` | `cam_w` | 19 | blade width, off the top view |
| `4 (.16)` | `cam_t` | 4 | **cam thickness** — the small dimension on the cam hub |
| `0.5 (.02)` | `WASHER_T` | 0.5 | compressed sealing washer, under the head |
| `1 (.04)` | `PANEL_T` | 1 | thinnest catalog panel, off the panel edge view |
| `Screw M6 thread` | `SCREW_D` | 6 | cam screw; head to ISO 4017 (A/F 10, k 4) |
| `Grip` | `grip` | 4–42 (2 mm steps) | head underside → cam clamping face |

## The 27.2 datum — why `body_l` is not the housing length

Both extension lines of the sheet's `27.2` were measured off the page against
the `Ø 28` head as the scale (5.71 px/mm):

| level | page y (px) | from the head underside |
|---|---|---|
| head underside | 392 | 0 |
| housing end | 490 | 17.2 |
| cam back face | 512 | 21.0 |
| back of the M6 screw head | 540 | 25.9 ≈ **27.2** |

So `27.2` is the **installed depth behind the head, covering housing + cam +
screw head**, not the housing alone. The model spends it the same way:

    housing_length(body_l, cam_t) = body_l - cam_t - CAM_JOINT - SCREW_HEAD_H

and the assembly's back face lands on `-body_l` exactly (measured: 0.0000 mm
error over the sampled sweep, all four housing lengths).

The same read gives the cam's Z-step: hub plane at 21.0 deep, clamping face
at 13.3 deep, i.e. a **4 mm step — one cam thickness** — hence

    cam_offset(body_l, cam_t, grip) = body_l - cam_t - SCREW_HEAD_H - grip

which returns 5.2 at the catalog row (`body_l` 27.2, `cam_t` 4, `grip` 14).
The 1.2 over the sheet's 4 is the screw head: ISO 4017 M6 is k = 4.0 and the
sheet's screw head scales to ≈ 5, so the housing here is 1 mm longer than the
real one and the step takes up the difference. The outer envelope is exact
either way.

## Scaled off the sheet, not dimensioned

| Feature | Value | How it was read |
|---|---|---|
| mounting nut A/F | `body_d + 4.8` (27.3 at Ø22.5) | silhouette width in the section |
| mounting nut height | 4.2 | 24 px in the section |
| cam step run | ≤ `(cam_l - tip_flat) - (body_d/2 + 0.6)` | the step only leaves the hub plane once it is outside the barrel |
| neck blend | ≈ 2.9 × `cam_w` | the top view's taper is still narrowing at x ≈ 21, outside the Ø28 head |

**The nut width is the one genuinely ambiguous read.** Its two inner lines sit
at ±50.6 % of the half-width, which is the signature of a hex sectioned across
*corners* — that reading gives A/F 23.6 over a Ø22.5 body, a 0.55 mm wall,
which is not a nut anyone makes. Taken as across-*flats* the wall is 2.4 mm.
The model uses the flats reading; if the corners reading is right, the nut is
some 3.7 mm narrower than modelled.

## Not modelled

- Threads (housing/nut and the M6). The mating pair is a real functional
  feature; it is left off here as it is across this family's siblings.
- The square drive between the housing end and the cam bore — it would be a
  hidden internal feature at every benchmark view angle.
- Offset and deep-offset cams, which is how the catalog reaches grips below
  the mounting nut. `check()` rejects those instead of pretending.
- Roller cams, the internal O-ring and spring, and the DIN-key head recesses
  (`slotted` stands in for the tool recess family).
