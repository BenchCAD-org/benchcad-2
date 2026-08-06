# DIN 71752 clevis fork head notes

## Sources and scope

- Primary source: [Ganter DIN 71752 Fork Heads, Steel, without Pin](https://www.ganternorm.com/en/products/3.6-Moving-Transferring-Connecting-with-Joints-Couplings-and-Gears/Fork-joints-Fork-heads/DIN-71752-Fork-heads-Steel).
- Source drawing: the dimensioned drawing on the primary source page.
- Source table: the `Article options / Table` section on the primary source page.
- Official CAD evidence: the primary page's `Download STEP-File` for
  `DIN 71752-4-8-M4`, downloaded 2026-07-27 (SHA-256
  `484D00DB511133380BDCD87B676816C8A1798173320C8B047955E0D635972018`).
- Issue scope: sizes `d1 = 4, 5, 6, 8, 10, 12, 14, 16 mm`, both catalog length variants, without pin or retaining hardware.
- `d1 = 20 mm` is excluded because the source explicitly says DIN 71752 does not foresee that size and its DIN length columns are blank.

Source values were transcribed and checked on 2026-07-26.

## Symbol mapping

| Source symbol | Code parameter | Use |
|---|---|---|
| d1 H9 | `d1` | transverse pin-hole diameter |
| l1 | `l1` | fork-slot root to pin center |
| d2 | `d2` | nominal internal thread diameter |
| a | `a` | outside fork-head width in both elevations |
| b | `b` | clear gap between fork arms |
| d3 | `d3` | threaded shank outside diameter |
| l2 | `l2` | shank end to pin center |
| l3 | `l3` | overall length |
| l4 | `l4` | cylindrical threaded-shank length |

`is_long=0` selects the first `l1/l2/l3` value in a source row;
`is_long=1` selects the second value. All remaining dimensions stay coupled to
that same `d1` row.

## Transcribed catalog rows

| d1 | l1 short/long | d2 | a | b | d3 | l2 short/long | l3 short/long | l4 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 8 / 16 | 4 | 8 | 4 | 8 | 16 / 24 | 21 / 29 | 6 |
| 5 | 10 / 20 | 5 | 10 | 5 | 9 | 20 / 30 | 26 / 36 | 7.5 |
| 6 | 12 / 24 | 6 | 12 | 6 | 10 | 24 / 36 | 31 / 43 | 9 |
| 8 | 16 / 32 | 8 | 16 | 8 | 14 | 32 / 48 | 42 / 58 | 12 |
| 10 | 20 / 40 | 10 | 20 | 10 | 18 | 40 / 60 | 52 / 72 | 15 |
| 12 | 24 / 48 | 12 | 24 | 12 | 20 | 48 / 72 | 62 / 86 | 18 |
| 14 | 28 / 56 | 14 | 28 | 14 | 24 | 56 / 85 | 72 / 101 | 22.5 |
| 16 | 32 / 64 | 16 | 32 | 16 | 26 | 64 / 96 | 83 / 115 | 24 |

## Independent source spot checks

- Small row: the source `d1=4` row shows `a=8`, `b=4`, `d3=8`, short
  `l1/l2/l3=8/16/21`, long `16/24/29`, and `l4=6`; these are the values in
  `DIN_ROWS[4]`.
- Large row: the source `d1=16` row shows `a=32`, `b=16`, `d3=26`, short
  `l1/l2/l3=32/64/83`, long `64/96/115`, and `l4=24`; these are the values in
  `DIN_ROWS[16]`.
- CAD geometry check: the modeled `d1=4` short exterior and the official STEP
  both have an `8 x 8 x 20.747055... mm` occupied bounding box and six faces
  on the same `R=8.033333... mm` sphere. After axis alignment, a boolean
  comparison also confirms that their exterior envelopes coincide.

## Geometry equations

- Fork-slot root height: `z_root = l2 - l1`, directly from the two source
  dimensions sharing the pin-hole center datum.
- Each fork-arm thickness: `(a - b) / 2`, from the symmetric source drawing.
- Pin-hole center: `(x, z) = (0, l2)`; the hole axis crosses both arms.
- Cylindrical shank: source diameter `d3` and source axial length `l4`.
- The forged envelope is a sphere clipped by the `a x a` square head width.
  Let `span = l3-l4` and `r = d3/2`. Requiring the sphere to pass through the
  shank circle `(r, l4)` and the theoretical axial apex `(0, l3)` gives
  `R = (span^2+r^2)/(2*span)` and center height `l3-R`. This relation was
  independently recovered from the official `DIN 71752-4-8-M4` STEP: it uses
  `R=8.033333... mm`, centered `12.966666... mm` from the shank end.
- Intersecting that sphere with the square envelope creates the round-to-square
  transition from `l4` upward. Cutting the fork slot at `l2-l1` then creates
  the official curved arm roots and central saddle.
- Threaded passage: use the ISO metric coarse pitch `P` for the selected `d2`
  and the common tap-drill shop approximation `d_core = d2-P`, rounded to the
  nearest `0.1 mm`. This gives `3.3 mm` for M4, exactly matching the official
  `DIN 71752-4-8-M4` STEP. That STEP also shows the passage breaking through at
  the fork-slot floor, so its modeled depth is `l2-l1` (with only a tiny
  boolean overlap into the already-open slot).
- Shank-end chamfers: the official `DIN 71752-4-8-M4` STEP has 45-degree outer
  and bore-entry chamfers with `0.4 mm` axial/radial legs. The drawing does not
  dimension them, so the family states the fitted proportion `c=0.1*d2` and
  applies the same `c` to both visible chamfers for every catalog size.
- The open fork slot has width `b` and a flat floor at `l2-l1`, matching the
  orthographic side view.
- The same clipped sphere crowns the fork-arm ends in both elevations. Because
  the central `b`-wide slot removes the sphere's axial apex, the highest
  remaining material lies slightly below the theoretical `l3` envelope, as in
  the official STEP model.

## Deliberate deviations

- The internal thread is represented by a smooth tap-drill/core-diameter
  cylindrical passage through to the fork-slot floor. Thread crests, flanks,
  and helical form are omitted as allowed by issue #51; the modeled scope is
  the standard right-hand variant.
- The pin, retaining clip, surface finish, tolerances, and minor unshown edge
  breaks are omitted. The two visible shank-end chamfers are included using
  the documented proportion above.
