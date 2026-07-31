# stop_bar_tailpiece — symbol map (Gotoh GE101Z sheet)

| Sheet symbol / callout | Parameter | Nominal | Verified against catalog |
|---|---|---|---|
| 102 (overall) | `overall_l` | 102 | GE101Z 102 / GE101A 101.5 / Faber 101.27 |
| 82 (stud span) | `stud_span` | 82 | Gotoh 82 (metric); StewMac/Gibson/Faber 3-1/4" = 82.55 |
| 18 (section, front-back) | `bar_w` | 18 | end view; string bores run through this depth |
| 12.75 (section, height) | `bar_h` | 12.75 | end view: flat bottom, domed top |
| 7 (end tab) | `tab_t` | 7 | GE101A 6.8 |
| R300 (crown) | `crown_r` | 300 | GE101A R250 |
| 51.5 (10.3 x 5) | `string_pitch` | 10.3 | span = 5 x pitch, printed on the sheet |
| phi5.1 / 4.5 (both faces) | `hole_d` (+ fixed 4.5 counterbore depth) | 5.1 | twin counterbores, one from each face |
| phi3 (web) | `web_d` | 3.0 | through-bore between the counterbores |
| 8 (stud slot) | `slot_w` | 8 | Faber 8.1 |
| (blend, undimensioned) | `ramp_len` | proportion | body-to-ear shoulder on the photo/plan |

Bore stack (invisible from outside; the reason `web_d` exists):
`face -> phi5.1 x 4.5 -> phi3 web -> phi5.1 x 4.5 -> face`, axis along the 18 mm depth.

Difficulty = range clustering (no feature toggle; the bore stack is always built):
easy replicates the GE101Z numbers, medium adds the GE101A / US-vendor spread,
hard widens to declared proportions (steep short shoulders, deeper crowns).

Deliberate deviations: studs/bushings are separate hardware (per the issue);
D-front is a circular-arc approximation of the die-cast dome; ruled loft with
dense stations stands in for the smooth blend (pinned-OCC limitation).
