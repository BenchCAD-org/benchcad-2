# GN 3975 worm-gear reducer

This family is a catalog-row reconstruction of Ganter GN 3975 from issue
#153. `CATALOG_ROWS` locks all public dimensional values to the 32 requested
tuples: eight ratios for each combination of `m1 = 20/30` and Type A/B.
`catalog_index` ordering is:

| rows | housing | drive arrangement |
| --- | --- | --- |
| 0–7 | m1=20 | Type A, one-sided drive |
| 8–15 | m1=20 | Type B, through drive |
| 16–23 | m1=30 | Type A, one-sided drive |
| 24–31 | m1=30 | Type B, through drive |

The ratio is the catalog output/input speed ratio.  The rendered wheel uses a
bounded visual tooth count only to keep previews light; it is not a claim that
the catalog ratio equals a tooth count.  The worm is shown with
`WORM_STARTS = 2` as a proportion assumption, not as an official claim that
GN 3975 uses a two-start worm.

The official STEP supplied with the issue was used only for visual/envelope
evidence (square aluminium housing, top output hub, drive key, and mounting
patterns).  It is deliberately not imported or committed.  The public drawing
does not specify the internal worm tooth profile, wheel tooth form, bearing
raceways, seals, or cavity clearances; those portions are documented as
`proportion` simplifications.  The assembly is nevertheless split into the
fixed seven benchmark solids required by the issue: one housing, one
drive-shaft/worm, one worm-wheel/output hub, two drive bearings, and two output
bearings.

For the supplied size-20 Type B reference, read-only B-rep inspection was used
to reconstruct the external interfaces explicitly: a 92 x 60 x 35 mm envelope;
output-axis face radii 15, 14.5, 11.5, and 6 mm; drive-face radii 15, 13.7, and
6 mm; six d7 through-hole centres; four M-size blind holes on each output face;
four blind holes on the positive Y face; and four blind holes on each drive-end
face. These external cues are rebuilt parametrically from catalog dimensions
and documented proportions; `build()` never loads the supplied STEP geometry.

The manufacturer drawing fixes the mounting semantics used in `part.py`:
`m1` is the worm/output centre distance; `m8` locates the drive axis from the
lower housing edge; `m2` sets the square blind-hole pattern around the output;
`m7` sets the drive-end pattern; `m9`/`m10` set the broad-side pattern; and
`m3`/`m6` set the two through-hole row widths. The Type A/B view also identifies
`l3` as the parallel-key length and `l4` as its shaft-end margin.

Key and thread checks cite DIN 6885-1 or the issue's usable-depth rule.  The
mounting-hole checks ensure the published `m`/`d` rectangles stay inside the
corresponding housing envelope.
