"""stop_bar_tailpiece — the benchmark generator spec.

Difficulty is expressed by range CLUSTERING, not a feature toggle (the stepped
bore stack is on the drawing for every variant, so it is always built):
easy   = the GE101Z catalog numbers (a render is a replica of the sheet);
medium = adds the GE101A / US-vendor spread (R250 crown, 82.55 span, 8.1 slot);
hard   = proportion extremes (short steep shoulders, deep crowns, 96-106 length).

Gibson-style stop bar tailpiece, bar only (Gotoh GE101Z class). PARAM_SPEC
declares each build() parameter; check() holds the engineering rules a reviewer
audits. Nothing is coupled, so there is no refine(). Spec: docs/DESIGN_SPEC.md

Sources:
- Gotoh official 2D drawings GE101Z / GE101A / GE101Z-T (GE101Z-Dim.pdf et al):
  overall 101.5-102, stud span 82, section 12.3-12.75 high x 17.8-18 wide, end tab
  6.8-7, crown R250-R300, string pitch 10.3 (span 51.5), stepped string bores
  phi5.1 -> phi3, stud slot 8.
- Cross-vendor (StewMac Gotoh/Gibson, Faber TP-59, Allparts): stud span
  3-1/4 in = 82.55, overall 101.27, slot 8.1 — the open slots absorb the
  metric/imperial 0.55 mm difference.
"""

import math

from part import _string_z


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "overall_l": dict(
        desc="overall bar length",
        unit="mm",
        range={"easy": (101.8, 102.2), "medium": (101.2, 102.5), "hard": (96.0, 106.0)},
        source="Gotoh 101.5-102 / Faber 101.27; hard widened as proportion",
        askable=True,
    ),
    "stud_span": dict(
        desc="stud centre-to-centre span (the Gibson mounting standard)",
        unit="mm",
        range={"easy": (81.95, 82.05), "medium": (81.9, 82.6), "hard": (81.5, 83.0)},
        source="Gotoh 82 (metric) vs Gibson/StewMac/Faber 82.55 (3-1/4 in)",
        askable=True,
    ),
    "bar_w": dict(
        desc="bar section width (front-back)",
        unit="mm",
        range={"easy": (17.9, 18.1), "medium": (17.6, 18.4), "hard": (15.5, 19.0)},
        source="GE101Z 18 / GE101A 17.8; proportion at hard",
        askable=True,
    ),
    "bar_h": dict(
        desc="bar section height at the crown crest",
        unit="mm",
        range={"easy": (12.65, 12.85), "medium": (12.3, 13.0), "hard": (11.5, 13.8)},
        source="GE101Z 12.75 / GE101A 12.3; proportion at hard",
        askable=True,
    ),
    "tab_t": dict(
        desc="end-tab (ear) thickness",
        unit="mm",
        range={"easy": (6.9, 7.1), "medium": (6.7, 7.2), "hard": (5.5, 8.0)},
        source="GE101Z 7 / GE101A 6.8; proportion at hard",
        askable=True,
    ),
    "crown_r": dict(
        desc="crown radius along the bar top",
        unit="mm",
        range={"easy": (290.0, 310.0), "medium": (245.0, 320.0), "hard": (220.0, 340.0)},
        source="GE101Z R300 / GE101A R250; proportion at hard",
        askable=True,
    ),
    "ramp_len": dict(
        desc="blend length from the crowned body down into each ear",
        unit="mm",
        range={"easy": (8.0, 10.0), "medium": (6.0, 13.0), "hard": (5.0, 15.0)},
        source="proportion (smooth body-to-ear transition on the GE101Z photo/drawing)",
        askable=True,
    ),
    "string_pitch": dict(
        desc="string-hole pitch (span = 5x pitch)",
        unit="mm",
        range={"easy": (10.28, 10.32), "medium": (10.25, 10.4), "hard": (9.8, 10.8)},
        source="Gotoh 10.3 (51.5 span); slight vendor spread as proportion",
        askable=True,
    ),
    "hole_d": dict(
        desc="string-hole entry diameter",
        unit="mm",
        range={"easy": (5.05, 5.15), "medium": (4.9, 5.3), "hard": (4.5, 5.8)},
        source="GE101Z phi5.1 entry (exit phi3 when stepped)",
        askable=True,
    ),
    "slot_w": dict(
        desc="open stud-slot width in the ears",
        unit="mm",
        range={"easy": (7.95, 8.05), "medium": (7.8, 8.15), "hard": (7.5, 8.6)},
        source="Gotoh 8 / Faber 8.1",
        askable=True,
    ),
    "web_d": dict(
        desc="through-web bore diameter between the twin counterbores",
        unit="mm",
        range={"easy": (2.95, 3.05), "medium": (2.85, 3.15), "hard": (2.6, 3.4)},
        source="GE101Z section: phi3 web between the phi5.1 x 4.5 counterbores",
        askable=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    bad = []

    # In plan the lobe is centred on the stud, reaches the overall dimension,
    # and is clipped by the +/-width/2 faces. It must still lie outboard of the
    # slot corner there, or the drawing's short curled nose disappears.
    lobe_r = (p["overall_l"] - p["stud_span"]) / 2.0
    mouth_corner_r = math.sqrt((p["bar_w"] / 2.0) ** 2 + (p["slot_w"] / 2.0 + 0.05) ** 2)
    if lobe_r <= mouth_corner_r:
        bad.append("ear lobe does not enclose the front outboard slot corner: curled hook tip would be open (GE101Z plan view; 0.05 mm clearance is proportion)")

    # the six-string span must clear both stud slots inside the raised body
    if 5.0 * p["string_pitch"] + p["hole_d"] > p["stud_span"] - p["slot_w"] - 6.0:
        bad.append("string span + hole_d > body between stud slots: outer holes break into the slots")

    # the blend must start past the string holes, and the crown must still stand
    # proud of the ear where the blend begins
    x_r0 = p["stud_span"] / 2.0 - p["slot_w"] / 2.0 - p["ramp_len"]
    # on the real part the outer bores sit right at the blend start, so only the
    # early (still-tall) third of the blend may overlap them
    if x_r0 + 0.35 * p["ramp_len"] < 2.5 * p["string_pitch"] + p["hole_d"] / 2.0 + 1.0:
        bad.append("blend drops too early: outer string bore would break out of the descending top (GE101Z outer bores sit at the blend start)")
    crown_at_r0 = p["bar_h"] - (p["crown_r"] - math.sqrt(p["crown_r"] ** 2 - x_r0 ** 2))
    if crown_at_r0 < p["tab_t"] + 2.0:
        bad.append("crown drops below tab_t+2 before the blend starts: crown too deep for the body (GE101Z crown is shallow)")

    # the U-slot's round closed end needs a real back wall in the plan width
    if p["slot_w"] > p["bar_w"] - 3.5:
        bad.append("slot_w > bar_w - 3.5: stud slot leaves <1.75 mm at its closed-end back wall")

    # the low bores shown in elevation retain a web above the base; their large
    # front entries still break through the D-section crown in plan
    z_hole = _string_z(p["tab_t"], p["hole_d"])
    if z_hole - p["hole_d"] / 2.0 < 0.8:
        bad.append("string bore leaves <0.8 mm above the base: GE101Z elevation shows a lower retaining web")

    # the web must remain a genuine step under the counterbores (drawing: 5.1 -> 3)
    if p["web_d"] > p["hole_d"] - 1.5:
        bad.append("web_d > hole_d - 1.5: no real counterbore step left (GE101Z bores are 5.1 entries over a 3 web)")

    return bad
