# quarter_turn_cam_latch — sheet dimension → parameter → formula

## What the part is (and what an earlier revision got wrong)

The double-D body is keyed to the panel cutout, so it **cannot rotate**; the
tool recess obviously must. An earlier revision of this family unioned the
head and the double-D body into one rigid solid, which is a latch that cannot
be operated. The E5 is an actuator turning inside a fixed housing:

- the sheet's own detail bubble names an **Internal O-ring** and an
  **Internal spring**. What looked like thread hatching in the main section at
  the panel level is that spring — a coil, clearly drawn, in an annular
  cavity between two parts.
- **every head-style icon on p.154 is two circles**: an outer flange and an
  inner raised boss carrying the recess. Cutting the top view through its
  centre gives Ø28.0 (flange) / Ø18.1 / Ø15.9 (plug) / Ø8.5 (square recess).
  The Ø18.1 disc is the rotating actuator's face.
- Southco's patent for this family, **US 6,527,308**, describes exactly this:
  "a first body rotatably mounted within a second body, and a cam mounted to
  the first body".
- the catalog line for the series is "spring-loaded bodies for better **grip
  tolerance** and vibration resistance" — so the spring is an axial preload
  that lets one part number cover a grip band, not a rotary detent.

Reference: Southco E5 literature,
`media.southco.com/media/static/Literature/e5.en.pdf`. Issue #32 carries the
same table with page numbers. `docs/assets/refs/quarter_turn_cam_latch_drawing.png`
is **page 154 only** — zinc, tool operated, short housing, fixed grip.

The E5 sheet labels dimensions with values, not letters, so the "on the sheet"
column is the value as printed.

## Dimensioned on page 154 — the committed reference image

| On the sheet | Parameter | Value | Notes |
|---|---|---|---|
| `Ø 28 (1.10)` | `head_d` | 28 | the fixed flange above the panel |
| top view Ø18.1 | `PLUG_RATIO` | 0.646 × `head_d` | the rotating plug's face |
| top view Ø8.5 | (drive) | — | the tool recess; `drive_af` is the cam-side square |
| detail bubble | `spring`, `o_ring` | — | named, not dimensioned — proportions |
| `5 (.20)` | `head_h` | 5 | |
| `Ø 22.5 +0.5/-0` | `body_d` | 22.5 | panel cutout circle |
| `□ 20.1 +0.1/-0` | `afl` | 20.1 | cutout across-flats |
| `27.2 (1.07)` | `body_l` | 27.2 | see "the 27.2 datum" |
| `45 (1.77)` | `cam_l` | 45 | **centreline to cam tip** |
| `23 (.91)` | `tip_flat` | 23 | flat past the step |
| `19 (.75)` | `cam_w` | 19 | blade width, top view |
| `4 (.16)` | `cam_t` | 4 | see "the 4 (.16)" |
| `0.5 (.02)` | `WASHER_T` | 0.5 | compressed sealing washer |
| `1 (.04)` | `PANEL_T` | 1 | thinnest catalog panel |
| `Screw M6 thread` | `SCREW_D` | 6 | |
| head styles `00` / `23` | `slotted` | 1 / 0 | Slotted / Blank |
| `Grip` | `grip` | — | head underside → cam clamping face |

## NOT on the committed image

These come from other pages of the same PDF. A reviewer checking them needs
the PDF, not this PR's render.

| Value | Page | Parameter |
|---|---|---|
| long housings 45.5 / 58.2 / 68.2 | 155 | `body_l` |
| body thread M22×1.5 | 156 | (sets the nut's bore) |
| mini: head Ø22×12.2, cutout 14.1 / Ø16.3, cam 33 / 15 | 158 | lower ends of the ranges |
| grip 4–42 in 2 mm steps | 170 | `grip` |

## Scale

Everything below is measured on the committed PNG at **5.4222 px/mm**, taken
from the printed `45` dimension (extension lines at x = 1225 and x = 1469,
244 px). Cross-check: the head silhouette measures 151.5 px = **27.94** against
a printed Ø28, i.e. 0.2 %.

## The 27.2 datum — why `body_l` is not the housing length

Levels on a column just off the axis (x = 1245):

| level | page y | below the head underside |
|---|---|---|
| head underside | 393 | 0 |
| housing end | 491.5 | **18.17** |
| cam back face | 514 | **22.32** |
| back of the screw head | 541 | **27.30** |

`27.2` is therefore the **installed depth behind the head, covering housing +
cam + screw head**, not the housing alone — 18.17 + 4.15 + 4.98 = 27.30 against
a printed 27.2 (0.4 %). The model spends it the same way:

    housing_length(body_l, cam_t) = body_l - cam_t - CAM_JOINT - SCREW_HEAD_H

so the assembly's back face lands on `-body_l` exactly (measured: 0.0000 mm
error across the sampled sweep and 2300+ corner instances, all four lengths).

The cam's Z-step follows from the same levels — tip top at y = 462, so
grip 12.73 and step 5.44:

    cam_offset(body_l, cam_t, grip) = body_l - cam_t - SCREW_HEAD_H - grip
    27.30 - 4.15 - 4.98 - 12.73 = 5.45   vs the measured step 5.44

The sheet's own grip, 12.73, is not on the catalog's 2 mm grid — page 154 is a
generic illustration, not a part number. At grip 12 the model's step is 6.2.

## The `4 (.16)`

Its extension lines sit at y = 491 and y = 512.5, i.e. across the cam plate
between the housing end (491.5) and the cam's back face (514) — it dimensions
the **cam's thickness**, 21.5 px = 3.97.

Issue #32's table records "cam arm cross-section (width/thickness) is not
dimensioned anywhere". That is wrong twice: the top view dimensions the blade
`19 (.75)` wide, and this `4 (.16)` gives the thickness. The reading is
corroborated by the 27.2 stack only closing if the cam is ≈ 4 thick.

## Scaled off page 154, not dimensioned

| Feature | Value | How it was read |
|---|---|---|
| mounting nut A/F | `body_d + 2.3` | see below |
| mounting nut height | 4.2 | 22.5 px |
| screw head height | 5.0 | 27 px — 1 over ISO 4017 M6 (k = 4), so washer-faced |
| screw head A/F | 10.0 | 13.1 silhouette read across corners = A/C 11.5 = ISO 4017 M6 |
| step's run and ≤ 60° slope | proportion | the sheet dimensions no bend angle |
| neck blend ≈ 2.9 × `cam_w` | proportion | the taper is still narrowing at x ≈ 20, outside the Ø28 head |

### The mounting nut — the one reading worth arguing about

The nut's silhouette measures **28.59**, and its two inner lines sit at
**±0.497** of the half-width. That ratio is the signature of a hex sectioned
across **corners** (the near and far vertices project to ±R/2), so:

    A/F = 28.59 × 0.866 = 24.76 = body_d + 2.26   →   1.4 wall over the M22×1.5 thread

Read the other way — silhouette = A/F — the corners would stand **5.1 proud of
the Ø28 head**. The section shows 0.3. So the corners reading is the right one
and this is a slim panel nut, not a structural one. The screw head in the same
section is cut the same way, and reads as a plain ISO 4017 M6 hex across
corners, which is a second point for that interpretation.

An earlier revision of this family read the silhouette as across-flats and
widened the nut to `body_d + 4.8`. That was wrong on both counts and is
reverted.

## The internals and view-reconstructability

The spring and O-ring live inside the housing bore and are **not visible from
any of the four benchmark view angles**. That is in tension with the repo's
rule against "solid outside, structure inside". They are modelled anyway
because without them the latch is not the part — the spring is what the
catalog sells the series on — and because `bench2 preview` emits both a
cutaway column and a per-component render, which is the escape the rule
itself allows. Flagging it rather than deciding it quietly.

The plug is a different case: its face **is** externally visible, as the inner
circle of every head-style icon and of the top view. Splitting housing from
plug costs nothing in reconstructability and is what makes the latch operable.

## Not modelled

- **Threads** — the M22×1.5 body/nut pair and the M6. The mating pair is a real
  functional feature; it is left off here as it is across this family's
  siblings. Without it neither the nut nor the screw actually retains anything.
- The tool recess is a plain slot (head style 00) or nothing (style 23); the
  square/triangle/double-bit/key-lock recesses are not modelled.
- Offset and deep-offset cams — how the catalog reaches grips below the
  mounting nut. `check()` rejects those rather than pretending.
- Roller cams, and the detent ramps some E5 variants carry.

## Standards: checked, and what does NOT apply

There is no dimensional standard for this latch. That is a checked result, not
an assumption, and it is recorded here so it does not get re-litigated:

- **DIN 43668** (quarter-turn locks for switchgear/control cabinets) is the
  standard this class of part is usually cited against, and it was checked
  first. **It does not apply.** Its insert cutout is a **32 x 20.1 rectangle**;
  the E5's is a **double-D, 20.1 across flats on a o22.5 circle**. The shared
  20.1 is a coincidence of the flats dimension, not a shared cutout. Writing
  DIN 43668 into `family.json` would be a fabricated citation, so `standard`
  stays "Southco E5 quarter-turn cam latch" — a product family, not a norm.
- What genuinely does apply, per feature rather than per part:
  | feature | standard |
  |---|---|
  | body thread M22x1.5 | ISO 261 fine-pitch series (ISO 965 tolerances) |
  | internal O-ring | ISO 3601-1 size series |
  | internal compression spring | EN 13906-1 / DIN 2098 |
  | sealed variants' ingress rating | IEC 60529 |
  These are cited for the feature class only. The E5 sheet does not give a
  size code for the O-ring or the spring, so their dimensions here remain
  proportion (see the table above) and are NOT claimed to be ISO 3601 rows.
- Architecture (rotating plug in a fixed body) follows Southco US 6,527,308.
