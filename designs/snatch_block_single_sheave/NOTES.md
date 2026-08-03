# snatch_block_single_sheave — symbol map, derivations, and what is proportion

Reference: Crosby *Blocks* catalogue p.326, "Snatch Block with Shackle Fitting,
Single Sheave, 2–12 t" —
[imperial](https://kitocrosby.com/wp-content/uploads/2025/07/15_Blocks_326.pdf) ·
[metric](https://kitocrosby.com/wp-content/uploads/2025/07/15_Blocks_MET_326.pdf).
Standard cited by the catalogue: **ASME B30.26** (rigging hardware — construction
and marking requirements; it does not dimension the block).

## Frame

The centre pin is the origin, because every catalogue dimension is anchored to
it. The sheave axis is **Y**, the block hangs down **−Z**, the side plates lie in
**XZ**, and the shackle bow is a semicircle in that same plane with its pin along
**X**. `base_plane` is `XZ`.

## Symbol map

| symbol | catalogue meaning | in the model |
|---|---|---|
| A | overall height | not a parameter — see the identity below |
| B | side plate head width | `head_w_B`, the plate crown diameter; the pin sits `B/2` under the crown |
| C | width across the cheeks | `cheek_w_C`; sets plate thickness and sheave width |
| D | centre pin to the bottom of the shackle throat | `pin_to_throat_D` |
| E | shackle bar / fitting thickness | `bar_thk_E`; also the pin diameter |
| F | fitting thickness at the bottom of the front view | not modelled separately — equal to E on every row of this table |
| G | shackle bow inside width | `bow_width_G` |
| H | shackle bow height, pin axis to the outside of the crown | `bow_height_H` |

## The A = B/2 + D + E identity

The catalogue prints A, B, D and E independently, but they are not independent:

```
A  =  B/2  +  D  +  E
```

The pin sits `B/2` below the plate crown (the crown is a circle centred on the
pin), the shackle throat bottom is `D` below the pin, and the bow bar is `E`
thick under the throat.

Checked against all 13 distinct rows — exact on the large rows, within 2 mm on
the small ones where the printed values are rounded:

| row | B/2 | D | E | sum | printed A | Δ |
|---|---|---|---|---|---|---|
| 2 t, sheave 76 | 38 | 185 | 13 | 236 | 235 | +1 |
| 4 t, sheave 114 | 54 | 268 | 16 | 338 | 340 | −2 |
| 5 t, sheave 102 | 57 | 278 | 16 | 351 | 353 | −2 |
| 6 t, sheave 127 | 65 | 268 | 16 | 349 | 351 | −2 |
| 8 t, sheave 152 | 76 | 373 | 32 | 481 | 481 | 0 |
| 8 t, sheave 203 | 103 | 398 | 32 | 533 | 533 | 0 |
| 8 t, sheave 254 | 128.5 | 425 | 32 | 585.5 | 586 | −0.5 |
| 8 t, sheave 305 | 154 | 471 | 32 | 657 | 657 | 0 |
| 8 t, sheave 356 | 179.5 | 484 | 32 | 695.5 | 695 | +0.5 |

So **A is reproduced, not tabulated**: the model builds the stack and the overall
height falls out. `check()` asserts the identity to 2.5 mm, which would catch a
mistyped row. The three rows spot-checked in the PR body come out at 481.0,
236.0 and 695.5 mm against printed 481, 235 and 695.

## The two ladders

The sheave is sized by the rope, the fitting by the working load limit, and the
catalogue rows pair them:

- `C`, `E`, `F`, `G`, `H` are **constant within a capacity group** — every 8 t and
  12 t row shares 106 / 32 / 32 / 76 / 88.
- `B` and `D` **move with the sheave** inside a group.

That is why `catalog_index` draws a whole row: picking the dimensions
independently would produce blocks that do not exist.

`B/sheave_d` stays inside **0.94–1.13** across all 13 rows, and it goes both ways
— on the 4 t row (sheave 114, B 108) the sheave rim stands proud of the plate; on
the 5 t row (sheave 102, B 114) the plate overhangs the sheave. An earlier
version of `check()` asserted `B ≥ sheave_d` and rejected the 4 t row, which the
coverage gate caught. The band is the constraint the catalogue actually holds.

## Excluded row

Stock 109037 (2 t, 419 w/Eye) is **not** in the table. It is fitted with a 32 mm
ID swivel eye instead of a shackle — a different fitting, not another size of
this one, and its G and H would not describe a bow.

## Proportions — everything the catalogue does not publish

The catalogue dimensions the envelope and the shackle. It does not publish the
groove profile, the plate thickness, the sheave width, or the yoke, so these are
declared `"proportion"` and listed here for review:

| quantity | value | basis |
|---|---|---|
| groove bottom radius | `0.53 × rope_d` | wire-rope sheave practice: the groove is cut a little over half the rope diameter so the rope beds without pinching |
| groove depth | `1.5 × rope_d` | sheave practice: deep enough to hold the rope in the groove |
| groove flank flare | 20° off radial | shop practice, so the rope enters without catching the lip |
| plate thickness | `0.10 × C` | proportion — splits C into two plates, the sheave, and running clearance |
| running clearance | 2 mm each side | proportion |
| sheave width | `C(1 − 2×0.10) − 4` | falls out of the two above |
| plate tail radius | `0.16 × B` | proportion, read off the drawing's teardrop |
| yoke length |  `1.8 × H` | proportion, set so the plate takes ~60% of the overall height A, matching the catalogue drawing |
| yoke tang thickness | `0.55 × G` | proportion — the tang must drop between the shackle ears |
| pin head diameter | `1.6 × pin diameter` | ordinary headed-pin proportion |
| sheave bore | pin + 1.5 mm (bushing) or + 2.5 mm (roller) | proportion; the catalogue gives only the BB/RB code, not race dimensions |

`open_angle` is an operating state, not a dimension: the catalogue says the
opening feature "permits easy insertion of rope without reeving", but does not
dimension the swing. It is the block's equivalent of `jaw_open_fraction` in
`three_jaw_scroll_chuck`.

## CadQuery notes for anyone editing this

Two traps cost a rebuild here and are worth knowing:

- **`.center()` before `.revolve()`** moves the workplane origin, which drags
  revolve's local axis onto the section's own centre and degenerates the
  revolve (`BRep_API: command not done`). Write the section with `moveTo`
  instead, or use `cq.Solid.makeTorus` as `_shackle_bow` does.
- **A section that already closes on itself must not be `.close()`d** — the
  extra zero-length edge makes the revolve return an empty solid, which then
  fails much later as `Bnd_Box is void`. But `revolve` needs a pending wire, so
  dropping `.close()` is not the fix either; `makeTorus` avoids both.

The sheave is one revolve of its complete section (bore, side face, flank, arc
bottom, flank, side face) rather than a cylinder with a groove cut out, so the
groove needs no boolean at all.
