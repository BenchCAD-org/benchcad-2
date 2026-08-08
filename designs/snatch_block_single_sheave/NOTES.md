# snatch_block_single_sheave — symbol map, derivations, and what is proportion

Reference: Crosby *Blocks* catalogue p.326, "Snatch Block with Shackle Fitting,
Single Sheave, 2–12 t" —
[imperial](https://kitocrosby.com/wp-content/uploads/2025/07/15_Blocks_326.pdf) ·
[metric](https://kitocrosby.com/wp-content/uploads/2025/07/15_Blocks_MET_326.pdf).
Construction, part names and the disassembly order come from the McKissick
[*Snatch Blocks* manual](https://www.thecrosbygroup.com/wp-content/uploads/2019/07/9999362_Snatch_Blocks_web.pdf)
— parts reference p.2, disassembly views pp.10–11, disassembly instructions p.12,
inspection diagram p.13. Standard cited by the catalogue: **ASME B30.26**
(rigging hardware — construction and marking requirements; it does not dimension
the block).

## The load path — what actually connects to what

A block is a chain of pinned joints, and the catalogue sheet does not show it;
the manual does. Reading its disassembly order backwards:

```
wire rope
  └ sheave ── bushing OR roller complement ── centre pin ─┐
                                                          ├── both SIDE PLATES
  shackle bow ── shackle bolt ── swivel TEE               │
       (cotter)        └ SWIVEL ── swivel CASE ── HOOK BOLT ┘
                                                    (retention nut + hitch pin)
```

Every arrow above is a bore-and-pin pair in `part.py`, with 0.5 mm radial
clearance. Two members carry the whole fitting load and both are easy to leave
out, because nothing in the catalogue table names them:

- **hook bolt** (the manual's "upper bolt", parts ref. LS4/SS2). Runs side plate
  → case → side plate. It is the *only* thing holding the two plates apart at
  the fitting end, and the only path from the shackle into the block. Manual
  p.12: a snap ring on its end stops it pulling through the plate, a round
  retention nut is staked with three stakes, and a hairpin ("hitch pin") keeps
  the nut from backing off.
- **swivel case** (Crosby's "yoke"; LS8 is a *Tee and Yoke Assembly*). The lug
  the hook bolt passes through. Its underside is counterbored, and the tee's
  headed stem stands in that counterbore — that is the swivel, and it is why the
  shackle turns freely under a loaded block. The manual's maintenance sheet sets
  fitting-to-swivel-case clearance at **.031–.062 in** at the factory, which is
  where the model's 1 mm end float comes from.

The **tee** is a tee: a cross barrel pierced by the shackle bolt, with a vertical
stem rising into the case. The hook version of the same block (McKissick 418)
deletes the tee and puts the hook's own shank in the same case — which is why
Crosby sells the hook and the shackle each *with* a yoke.

The **retention nut is staked into the swing plate**, not carried on the bolt
(US6481695 puts the threaded nut on the swing plate; the manual says to check it
is "properly staked with 3 stakes"). That is not a detail — it is what makes the
block openable at all. A bolt carrying its own nut cannot be unscrewed: backing
it out of the plate drives the nut straight into the swivel case, which is
exactly what the probe reported (1410 mm³) on the first attempt at this.

Opening the block, manual p.12 step 2, verbatim: *"Remove hitch pin and unscrew
the upper bolt allowing the side plate to rotate on the center pin and swing out
of the way."* So `open_angle` is a rotation about the **centre pin**, and the
hook bolt is modelled as withdrawn from the swing plate whenever `open_angle > 0`
— the plate cannot turn while the bolt is through it.

## Frame

The centre pin is the origin, because every catalogue dimension is anchored to
it. The sheave axis is **Y**, the block hangs down **−Z**, the side plates lie in
**XZ**, and at `swivel_angle = 0` the shackle bow is a semicircle in that same
plane with its bolt along **X**. `base_plane` is `XZ`.

## Symbol map

| symbol | catalogue meaning | in the model |
|---|---|---|
| A | overall height | not a parameter — see the identity below |
| B | side plate head width | `head_w_B`, the plate crown diameter; the pin sits `B/2` under the crown |
| C | width across the cheeks | `cheek_w_C`; sets plate thickness, sheave width, **and every load-carrying pin** |
| D | centre pin to the bottom of the shackle throat | `pin_to_throat_D` |
| E | shackle bar / fitting thickness | `bar_thk_E`, the bow bar diameter |
| F | fitting thickness at the bottom of the front view | not modelled separately — equal to E on every row of this table |
| G | shackle bow inside width | `bow_width_G` |
| H | shackle throat: clear opening under the bolt, down to the inside of the crown | `bow_height_H` |

H and D share a lower datum. On the catalogue sheet both dimension lines land on
the same extension line at the inside of the bow crown, and H's upper arrow lands
on the underside of the shackle bolt — so the bolt axis is `H + one bolt radius`
above the throat, not `H` above the crown.

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
mistyped row.

Measured bounding-box heights land on the identity to 0.0 mm on twelve of the
thirteen rows. The exception is the 4 t row, and it is not an error: there the
sheave radius (57) is larger than `B/2` (54), so the **sheave rim** is the top of
the bounding box, not the plate crown, and the model measures 341.0. The printed
A is 340 — between the identity's 338 and the rim's 341. It is the same row that
broke the old `B ≥ sheave_d` check.

## The two ladders

The sheave is sized by the rope, the fitting by the working load limit, and the
catalogue rows pair them:

- `C`, `E`, `F`, `G`, `H` are **constant within a capacity group** — every 8 t and
  12 t row shares 106 / 32 / 32 / 76 / 88.
- `B` and `D` **move with the sheave** inside a group.

That is why `catalog_index` draws a whole row: picking the dimensions
independently would produce blocks that do not exist. It is also why the centre
pin and the hook bolt are scaled off **C** and not off the sheave — they are
load-carrying parts, so they belong to the WLL ladder. The scale is calibrated on
the 8 t block, where `0.30 × C = 31.8 mm` against a real 1¼ in centre pin and
`0.26 × C = 27.6 mm` against a real 1⅛ in hook bolt.

`B/sheave_d` stays inside **0.94–1.13** across all 13 rows, and it goes both ways
— on the 4 t row (sheave 114, B 108) the sheave rim stands proud of the plate; on
the 5 t row (sheave 102, B 114) the plate overhangs the sheave. An earlier
version of `check()` asserted `B ≥ sheave_d` and rejected the 4 t row, which the
coverage gate caught. The band is the constraint the catalogue actually holds.

### Where the fitting hangs, and why the big rows differ

The plates reach `0.36 × D` below the pin — the proportion the catalogue sheet
draws — **except** that the plate's tail boss and the swivel case both sit beside
the sheave, so on the large-sheave rows the rim pushes the whole fitting further
down and `0.36 D` stops governing:

| row | 0.36 D | sheave rim + case eye + 4 mm | hook bolt sits at |
|---|---|---|---|
| 8 t, sheave 152 | 134.3 | 109.0 | −134.3 (D governs) |
| 8 t, sheave 203 | 143.3 | 134.5 | −143.3 (D governs) |
| 8 t, sheave 254 | 153.0 | 160.0 | −160.0 (sheave governs) |
| 8 t, sheave 305 | 169.6 | 185.5 | −185.5 (sheave governs) |
| 8 t, sheave 356 | 174.2 | 211.0 | −211.0 (sheave governs) |

The consequence is visible in the renders: on the biggest block the plate is
nearly circular and the case is long, while on the small ones the plate is a
long teardrop. `check()` asserts both bounds.

## A caution about the catalogue sheet

The p.326 two-view is **topologically right and dimensionally not to scale.**
Measured off the raster at full resolution, against B taken as the plate crown
width: the sheet draws H/B = 0.485 and D/B = 2.12, where the table's own rows run
0.53–0.58 and 2.43–2.45, and it draws the crown 0.87 × (B/2) above the pin where
its own A identity requires exactly B/2. Use the sheet for *what connects to
what* and for the relative placement of parts within it; use the table for
numbers.

## Excluded row

Stock 109037 (2 t, 419 w/Eye) is **not** in the table. It is fitted with a 32 mm
ID swivel eye instead of a shackle — a different fitting, not another size of
this one, and its G and H would not describe a bow.

## Proportions — everything the catalogue does not publish

The catalogue dimensions the envelope and the shackle. It names the fitting parts
but dimensions none of them, so these are declared `"proportion"` and listed here
for review. `d` below is the hook bolt diameter, `p` the shackle bolt diameter.

| quantity | value | basis |
|---|---|---|
| groove bottom radius | `0.53 × rope_d` | wire-rope sheave practice: cut a little over half the rope diameter so the rope beds without pinching |
| groove depth | `1.5 × rope_d` | sheave practice: deep enough to hold the rope in the groove |
| groove flank flare | 20° off radial | shop practice, so the rope enters without catching the lip |
| plate thickness | `0.10 × C` | proportion — splits C into two plates, the sheave, and running clearance |
| running clearance | 2 mm each side of the sheave | proportion |
| sheave width | `C(1 − 2×0.10) − 4` | falls out of the two above |
| centre pin diameter | `0.30 × C` | load-sized part, so it scales with the WLL ladder; calibrated on the 8 t block (31.8 mm vs a real 1¼ in pin) |
| hook bolt diameter `d` | `0.26 × C` | same reasoning; 27.6 mm vs a real 1⅛ in bolt |
| plate tail boss radius | `0.95 d` | lug practice — edge distance about one bolt diameter |
| hook bolt axis | `max(0.36 D, sheave_r + max(boss, eye) + 4 mm)` below the pin | the first term is read off the sheet, the second is the sheave clearance that governs the big rows |
| swivel case eye radius | `1.05 d` | lug practice — outside diameter about twice the hole |
| swivel case foot radius | `1.15 d` | has to house the swivel counterbore |
| swivel case thickness | plate gap − 1 mm | the case IS the spacer between the plates, so it fills the gap |
| swivel end float | 1.0 mm | manual, maintenance item 7: fitting-to-swivel-case clearance .031–.062 in |
| tee stem diameter | `0.85 d` | carries the same load as the bolt, in tension |
| tee stem head diameter | `1.35 ×` stem | the shoulder that stands in the counterbore |
| exposed stem length | `0.35 d` | proportion, read off the sheet's neck between the case and the tee |
| shackle bolt diameter `p` | `1.13 × E` | anchor-shackle practice: Crosby G-2130 runs the bolt one size over the bow (8.5 t: bow 28.7, bolt 32) |
| tee barrel radius | `0.95 p` | proportion — the barrel stands proud of the shackle ears, as the product photographs show |
| shackle ear boss radius | `0.72 p` | ordinary shackle-eye proportion |
| shackle ear inside spacing | `0.73 × G` | measured off the sheet; it is why the bow is a pear and not a dee, and Crosby's own G-2130 anchor-shackle table has the same A < B relation |
| shackle ear width along the bolt | `1.4 × E` | the ear is upset wider than the bar so the bolt head bears on it **clear of the flaring leg** — see below |
| bolt head radius | `1.35 ×` shank radius | ordinary headed-bolt proportion |
| retention nut | OD `2.4 ×` bolt radius, length `0.9 ×` | round staked nut (manual p.12) |
| retaining wire diameter | `0.14 ×` its bolt's diameter | proportion |
| straight roller diameter | `0.22 ×` centre pin diameter, `0.6` mm apart | proportion; sets `roller_count` |
| head / nut diameter | `1.6 ×` shank, hex A/F `1.55 ×` shank | ordinary headed-pin proportions |
| bushing wall / roller race depth | `0.12 ×` pin (BB) or `0.22 ×` pin (RB), min 2 mm | proportion; the catalogue gives only the BB/RB code, not race dimensions |
| every pin-in-bore clearance | 0.5 mm radial | proportion |

### The bearing changes the body count

BB and RB are the same **component**, so the body count follows `roller_count`
rather than a fixed `solids`: 1 bronze bushing, or 15–16 straight rollers. The
manual (p.9, p.12) describes the option as a *straight, unsealed* roller
bearing, which is a full complement running directly on the pin — there is no
race to model, and "not sealed … not recommended for higher speeds" is what a
full complement behaves like. `family.json` therefore declares no `solids` and
names `roller_count` as the quantity; `bench2 validate` resolves it per instance.

### Retaining wire

The hitch pin and the shackle cotter are Crosby's own line items (LS5/SS3
*Hairpin for Hook Bolt*, LS14/SS6 *Cotter Pin Only*) and both are visible in the
sheet and the photographs, so both are modelled: the hairpin is swept along a
tangent-continuous path (line, semicircle, line) so it comes out as one solid
with no booleans, and the swept volume equals `π r² L` exactly — which is the
check that the sweep did not quietly return something else. The centre pin gets
neither: the manual retains it with a prevailing-torque lock nut and a **roll
pin** driven into it, which is not a visible clip.

`open_angle` and `swivel_angle` are operating states, not dimensions. The
manual gives the motion for both and dimensions neither.

## CadQuery notes for anyone editing this

Three traps cost a rebuild here and are worth knowing:

- **`.center()` before `.revolve()`** moves the workplane origin, which drags
  revolve's local axis onto the section's own centre and degenerates the
  revolve (`BRep_API: command not done`). Write the section with `moveTo`
  instead, or use `cq.Solid.makeTorus` as `_shackle_bow` does.
- **A section that already closes on itself must not be `.close()`d** — the
  extra zero-length edge makes the revolve return an empty solid, which then
  fails much later as `Bnd_Box is void`. But `revolve` needs a pending wire, so
  dropping `.close()` is not the fix either; `makeTorus` avoids both.
- **`Workplane("XZ")` extrudes toward −Y and `Workplane("YZ")` toward +X.**
  Every helper here places its result by the face the extrusion *ends* on, and
  says so; getting this backwards puts a cutter entirely outside its target and
  the cut silently does nothing.

The sheave is one revolve of its complete section (bore, side face, flank, arc
bottom, flank, side face) rather than a cylinder with a groove cut out, so the
groove needs no boolean at all.

## Probe

`bench2 validate` cannot see interpenetration, and it cannot see a part that is
attached to nothing — an assembly of free-floating solids passes every gate. So
this family is checked with an explicit pairwise probe over all 13 rows × {bronze
bushing closed, roller closed, roller open} = 39 instances: every pair's
intersection volume must be 0, and every joint in the load path above must have a
minimum distance no larger than the fit it is built with.

Current result: **0 mm³ overlap and 0.55 mm worst joint clearance, on all 39
instances.** Two joints are expected to open once `open_angle > 0` and are
excluded there: `side_plate_02 | hook_bolt` and `hook_bolt | retention_nut`,
because the bolt has been unscrewed out of the plate and the nut has swung away
with it — the state the manual describes.

Three defects were found by this probe and by nothing else, all of them while
adding the retaining hardware:

| what the probe said | cause |
|---|---|
| `shackle_bow \| shackle_bolt` 591 mm³ | the bolt head bears on the ear's outer face, but the bow's leg flares outboard below it and the head hung into that flare. Fixed by upsetting the ear to `1.4 E`; `check()` now computes the leg's outboard reach at the head's rim and rejects the row if it fouls |
| `hook_bolt \| swivel_case` 1410 mm³, open only | a bolt carrying its own nut cannot be withdrawn — the nut travels inboard into the case. Fixed by staking the nut into the swing plate, which is what the real one does |
| `shackle_bolt \| shackle_cotter` 58 mm³ | the cotter's eye reached back over the nut it locks. Fixed by parking the cotter clear of the nut face |

None of the three moved `bench2 validate` off PASS.
