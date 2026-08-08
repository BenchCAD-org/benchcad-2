# truss_half_coupler_hook — source notes (datasheet → design mapping)

Anchor: Doughty T57000/T57010 (standard half coupler), T58080 (slimline),
T58100 (lightweight), T57200 (hook clamp) datasheets; cross-checked against
Riggatec / Global Truss / Kupo equivalents.

## Symbol mapping (Doughty drawing → code)

| Drawing | Meaning | Value / relation | code |
|---|---|---|---|
| Ø48-51 | barrel bore | universal truss/scaff tube | `bore_d` |
| 50 | body width along tube | 30 (slimline) - 51 | `body_w` |
| 55 | tube centre → base face | 40-55 across range | `base_drop` |
| Ø12.7 | VERTICAL fixing bore, base face up into the nut window (front-view hidden lines) | drawing | `hang_d` |
| 16 | depth of that bore, base face up to the window floor | `1.26 * hang_d` = 16.0 at Ø12.7 | derived |
| 19 | captive-nut window width ACROSS the clamp — and therefore the A/F of the M12 nut it traps | drawing | `tang_t` |
| 107 | overall width = left lobe + closure-tab tip | **106.77** measured on the anchor row; asserted by `check()` | derived |
| 116 | overall height = base face to the TOP OF THE WING NUT, clamp shut | **116.84** on the anchor row (STEP: 115.97) | derived |

### The manufacturer's own 3D model is the primary source

Doughty publish a STEP model of this exact product code alongside the data
sheet: `T57000-T57010.step`, linked from
<https://doughty-engineering.co.uk/products/doughty-half-coupler/>. It is a
SolidWorks export and it is the primary source for the geometry below; the
front view is now only a cross-check. It is NOT redistributed in this repo —
only measurements taken from it are recorded here.

It contains **eight solids**, the same eight this family builds, and its
envelope is **107.09 x 50.00 x 115.97** against the sheet's 107 / 50 / 116.
Barrel bore is **r 25.400** (Ø50.8 = 2 in). Ratios below are its exact
dimensions divided by that radius, with the origin on the barrel axis:

| feature | STEP | ratio | code |
|---|---|---|---|
| pin centres | x = ±35.00, z = −13.18 | 1.3780 r_i | `x_pin`, `z_pin` |
| pin lobe | r = 12.00 | 0.4724 r_i | `r_lobe` |
| body top face | z = **−1.18** | = `z_pin + r_lobe` | `z_top` |
| body extremities | x = ±47.00 | = `x_pin + r_lobe` | — |
| base face | z = −56.40, x = ±25.00 | 0.9843 r_i | `w_base` |
| both joint slots | inboard end x = ±17.43, floor z = −29.77 | 0.6862 / −1.1720 r_i | `x_slot`, `z_slot` |
| hinge slot / strap tongue | 29.50 / 28.00 wide | 0.59 / 0.56 body_w | `pocket_w`, `tongue_w` |
| pivot slot / bolt eye | 14.00 / 12.00 wide | `bolt_d + 2` / `bolt_d` | `slot_w`, `eye_w` |
| bolt eye outer | r = 10.10 | 0.84 bolt_d | `r_eye` |
| spring pin | body bore Ø9.50, tongue bore Ø10.0, length 44.5 | 0.75 hang_d | `pin_d` |
| strap outer | r = 35.40 (10.0 thick) | 1.35 wall_t | `r_out` |
| tab tip / nose | x = 60.09, r = 4.00 | 2.3657 / 0.1575 r_i | `x_tab`, `r_nose` |
| tab top face | z = 26.73 | 1.0524 r_i | `z_tab_hi` |
| captive-nut window | x = ±9.62, z −37.40 up to the bore, through | `tang_t` | window |
| Ø12.7 fixing bore | z −56.40 → −37.40, i.e. **19.0 deep** | 1.5 hang_d | `hang_d` |
| washer / hex nut / wing nut | Ø24.0×2.3 / 18.3 A/F / 46.5 span × 20.6 tall | — | see below |

**The lobe is externally tangent to the barrel bore.** On the STEP model
`x_pin² + z_pin² = (r_i + r_lobe)²` holds to four decimals, and the tangency
point (−23.77, −8.95) is an actual vertex of both the bore face and the lobe
face. That is not a coincidence of one row — it is the design relation that
makes strap and body finish flush. `part.py` therefore derives `z_pin` from it
rather than carrying an independent ratio, and `z_top` from `z_pin + r_lobe`.

**Three things this corrected**, all of them functional rather than cosmetic:

1. **Both joints are full-depth clevises**, milled straight in from the outside
   face down to z = −29.77 and open through the top — not the small closed
   pockets this part had. On the hinge side that is what lets the strap's
   knuckle be a FULL disc of radius `r_lobe` about the pin, flush with the
   body's own lobe at x = −47.00, instead of a 7.75-radius stub buried 4 mm
   inside the silhouette with nothing to carry load on. On the pivot side it is
   what lets the eyebolt swing right out of the casting; the old pocket stopped
   at x = 39.7 while the lobe ran to 46.6, so the bolt jammed on the body's own
   lobe after about 20°, and the clamp could not be opened.
2. **The captive-nut window runs all the way up into the jaw** — its top edge
   lies exactly on the barrel bore (at x = ±9.62 the bore is at z = −23.51,
   and the window's walls end at −23.50). The old version left a 1.5 mm floor
   between window and jaw, which closes the pocket the nut is dropped into.
3. **The Ø12.7 fixing bore is 19.0 deep**, = 1.5 × Ø12.7, not the 16 the sheet
   dimensions. The sheet and the STEP disagree here by 3 mm; every other
   dimension they share agrees, so this is recorded as a conflict rather than
   averaged, and the code follows the STEP.

### Front view, measured off the sheet

`docs/assets/refs/truss_half_coupler_hook_drawing.png` was measured against its
own dimensions rather than eyeballed. Scale from the 107 dimension line: it
spans 386 px, i.e. **3.6075 px/mm**; the same scale reproduces the 55 (198.5 px)
and the Ø51 barrel ring, so it is not a one-dimension fit. Origin = the barrel
axis, +X toward the closure tab, +Z up. Readings, and what each drives:

| Feature | Measured (mm) | code |
|---|---|---|
| barrel outer circle | Ø51.0 | `bore_d` |
| body top face | z = **+2.9**, out to x = **±39.7** | `z_top = 0.113 r_i`, `x_sh = 1.557 r_i` |
| hinge / pivot pin centres | x = **-35.5 / +34.1**, z = **-12.0** | `x_pin = 1.337 r_i`, `z_pin = -0.471 r_i` |
| pin lobe (the corner is ROUND, not a fillet) | r ≈ **12.5** about the pin | `r_lobe = 0.490 r_i` |
| widest points of the body | x = **-47.1 / +46.6** at z ≈ -11 | `x_pin + r_lobe` = 46.6 |
| base face | z = **-55.4**, half width **≈ 25.5** | `base_drop`, `w_base = 1.00 r_i` |
| closure-tab tip | x = **+60.1**, nose r ≈ 3 | `x_tab = 2.36 r_i`, `r_nose = 0.11 r_i` |
| closure-tab faces | top z = **+28.6**, underside z = **+15.4** | `z_tab_hi = 1.122 r_i`, `lug_h` ≈ 13 |
| eyebolt shank | two straight lines at x = **+29.1 / +41.4**, i.e. Ø12.3 centred on the pivot | `closing_bolt_d` (M8/M10 declared) |
| captive-nut window | two straight lines at x = **±9.7**, z from **-23.5 to -39** | `tang_t` × `0.82 tang_t` |
| Ø12.7 hidden lines | x = **±6.35**, z from **-39** to the base face | `hang_d` |
| overall dark extent | x **-47.4 … +59.6** (= 107.0), z **-55.4 … +61.5** (= 116.9) | envelope |

Three facts from that table are what the earlier version of this part got
wrong, and they are why it read as a box rather than a clamp:

1. **The two widest points are the pin LOBES, and they sit BELOW the tube
   centre** (z ≈ -12, not 0). The 107 is measured from the left lobe across to
   the closure-tab tip — it is not symmetric about the barrel.
2. **The closure is a cantilevered flat TAB with open air under it**, reaching
   24 mm past the body's own silhouette. The earlier model put a
   30 × 50 × 20 rectangular block there, which is what filled the top of the
   envelope and made the silhouette square.
3. **The body's top face is at z ≈ +2.9**, so the jaw is a deep U open at the
   top and the strap is the only thing over the barrel — not two halves of a
   split ring meeting at z = 0.

The drawn wing nut is NOT orthographically consistent (its hex collar centres
on x ≈ +28.8 while the eyebolt it sits on is at +35.2), so it is treated as a
pictorial symbol and the nut is taken from DIN 315-D instead. The M10 row's
49.5 span ends at x = +58.8 on the anchor row, 1.4 mm inside the tab tip — which
is what makes M10, and not M12, the closure that fits the 107 outline.

## Assembly (8 solids, contact-or-clearance only)

lower shell (the one-piece body: lobed pentagon plate, U-jaw, hinge/pivot
pockets, captive-nut window + Ø12.7 eye, or the M12 stud) · upper shell (the
closure strap: hinge tongue → band over the barrel → flat tab) · hinge pin ·
closing bolt (pivot eye + plain shank + ring thread) · pivot pin · **washer ·
hex nut** · wing nut.

The sheet draws **three** parts on the eyebolt above the tab, not one — an
ISO 7089 plain washer, an ISO 4032 hexagon nut on it, and the wing nut on top
of that. The washer is not decoration: the tab slot is open at +X, so without
it the hex nut would bear on two thin slot edges.

Clearances: pins 0.15 radial; hinge tongue 0.3 a side in its pocket; eyebolt
0.7 a side in the tab slot and in the body's pivot slot; 0.2 at each step of
the washer / hex nut / wing nut stack. The strap's left end BEARS on the body's
shoulder — that face contact is the hinge seat and is the only touching pair;
every pair still measures zero intersection volume. Verified across all 24
sampled rows (3 difficulties × 8 seeds): 0 interfering pairs.

## Hardware derivation (constants, not sampled)

- closing bolt nominal = `closing_bolt_d`, a parameter in its own right. It is
  NOT derived from `hang_d`: the datasheet lists the base fixing ("integral flat
  boss drilled Ø12.7 with a hex slot for a captive M10/M12 nut") and the closure
  ("a swing-away Grade 8.8 eyebolt and wing nut") as separate fasteners. The
  earlier `hang_d - 0.7` conflation sized the eyebolt M12 and, once a real
  DIN 315-D wing nut went on it, measured 114 mm across a 107 mm outline.
  M8/M10 only — see the spec note on why M12 is not a declared value.
- ISO 261 coarse pitch by nominal (M8 1.25, M10 1.5, M12 1.75).
- Thread = axisymmetric ring stacks (no helix): bolt rings root→crest
  `bolt_d/2 - 0.61 p → bolt_d/2`, width `0.4 p`, one per pitch; the nut's
  internal rings sit on the SAME z-grid offset half a pitch, radially nested
  0.25 p past the bolt crest — engaged, with 0.1 p axial gaps, so the pair
  measures zero intersection volume.
- pins Ø `max(5, 0.5 hang_d)`, hollow (see deviation 3); bolt pivot-eye outer radius
  `pin_d/2 + 0.26 bolt_d + 1.4`, sized off the pin it swings on (the drawing's
  pivot circles read ~Ø11 over a Ø6.35 pin), not off the thread diameter.

### The nut stack, measured off the sheet

| part | measured on the drawing | nearest standard row | code |
|---|---|---|---|
| plain washer | Ø **24.5** × **2.2** thick | **ISO 7089 M12**: d2 24, h 2.5 | `_ISO7089` |
| hexagon nut | **18.2** across × **10.7** tall | **ISO 4032 M12**: s 18, m 10.8 | `_ISO4032` |
| eyebolt shank | Ø **12.3** | M12 | — |

So the sheet's eyebolt hardware is unambiguously **M12** — three independent
dimensions land on the M12 row. Its *wing nut*, however, measures only ~42
across and ~19.6 tall, which is nowhere near DIN 315-D M12 (63.5 / 32.2) and is
closer to the M8 row. That is the same inconsistency the hex collar's off-centre
position shows: the wing nut on the sheet is a pictorial symbol, the rest of the
stack is to scale.

This model therefore runs **M8/M10**, because a DIN 315-D M12 wing nut spans
63.5 and puts the envelope at 112.4 — outside the 107 outline. The consequence
is recorded rather than hidden: with a standard-conformant stack the anchor row
stands **116.8 mm** tall against the catalog's **116**. The STEP model settles the
wing-nut question: its wing nut is **46.5 across x 20.6 tall**, which is not
any DIN 315-D row — so Doughty's closure nut is simply not a DIN 315 part, and
the M8/M10 restriction here is a modelling compromise, not a catalog fact.

ISO 4032 s/m and ISO 7089 d1/d2/h were read off
[fasteners.eu](https://www.fasteners.eu/standards/iso/4032/) and
[fasteners.eu](https://www.fasteners.eu/standards/iso/7089/), not iso.org,
which returns HTTP 403 to automated fetches.

The sheet's 116 is measured to the **top of the wing nut** (front view dark
extent ends at z = +61.5, which is the nut, not a protruding thread), so with
the clamp shut the eyebolt is cut to end inside the nut's threaded boss.

### Wing nut — DIN 315 form D (symbol → code)

The datasheet's front view — the one carrying the 107 — shows the wings splayed
**in that plane** over a hex-to-round boss; the side view shows only a narrow
rib. So the wings lie in XZ, across the clamp, not along the tube axis.

| DIN 315-D | meaning | code |
|---|---|---|
| d1 | nominal thread | `closing_bolt_d` |
| d2 / d3 | boss Ø at the bearing face / at the top of the taper | `_din315d()` row |
| m | boss height | `m_boss` |
| e | span over the wing tips (M10: 48-51; drawing scales to ~47.7) | `e_span` |
| h | overall height, bearing face to the top of the wings | `h_nut` |
| g2 / g1 | wing thickness at the root / at the ear | `g2` / `g1` |
| r1 | ear (wing-tip lobe) radius | `ear_r1` |
| r4 | concave underside radius | `under_r4` |

Rows are the DIN 315-D mid-band, scaled linearly to the actual thread Ø so the
nut still fits a non-tabulated bolt.

## Deliberate deviations / simplifications

1. Drawn closed with the barrel absent. The sheet's own outline leaves the
   barrel exposed in two gaps — upper right, where the eyebolt crosses, and a
   narrow one upper left — so the strap is not modelled as closing onto the
   body anywhere except its hinge seat.
2. Ring thread substitutes the helix (framework-wide convention); run-out and
   chamfers on the bolt tip are not modelled.
3. Both pins are hollow **ISO 8752 / DIN 1481 slotted spring pins**, which is
   what the sheet draws — its pin circles are two concentric circles broken by
   a slot, not a solid dowel. Modelled as a C-section tube with the wall
   thickness taken from the standard's table by nominal Ø (Ø3 → 0.6, Ø4 → 0.8,
   Ø5 → 1.0, Ø6 → 1.25, Ø8 → 1.5, Ø10 → 2.0, Ø12 → 2.5; `_ISO8752_S`, scaled
   to a non-tabulated Ø), slot opening downward. The
   free-state slot width is NOT tabulated (it closes as the pin is driven), so
   0.20 d is a proportion. The s column was read off
   [fasteners.eu/standards/iso/8752](https://www.fasteners.eu/standards/iso/8752/),
   not from iso.org, which returns HTTP 403 to automated fetches; anyone
   relying on it should confirm against the ISO catalogue.
   The standard's chamfered lead-in is not modelled and
   pins are 0.4 short of the body width so the ends sit flush inside the ears.
4. The body is modelled as a plane-faced extrusion. The real casting has
   chamfered outer edges and a relieved front face; neither is modelled.
5. The body outline scales with `bore_d`, so the 107 is reproduced at Ø51 and
   falls to ~100.5 at Ø48. The real clamp is one casting across the whole
   48-51 range; scaling it is a benchmark-variation choice, not a catalog
   claim, and `check()` bounds the result to 96-110.
