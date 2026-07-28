"""stop_bar_tailpiece — the benchmark generator spec.

Gibson-style stop bar tailpiece, bar only (Gotoh GE101Z class). PARAM_SPEC
declares each build() parameter; check() holds the engineering rules a reviewer
audits. Nothing is coupled, so there is no refine(). Spec: docs/DESIGN_SPEC.md

Sources:
- Gotoh official 2D drawings GE101Z / GE101A / GE101Z-T (GE101Z-Dim.pdf et al):
  overall 101.5-102, stud span 82, section 12.3-12.75 x 17.8-18, end tab
  6.8-7, crown R250-R300, string pitch 10.3 (span 51.5), stepped string bores
  phi5.1 -> phi3, stud slot 8.
- Cross-vendor (StewMac Gotoh/Gibson, Faber TP-59, Allparts): stud span
  3-1/4 in = 82.55, overall 101.27, slot 8.1 — the open slots absorb the
  metric/imperial 0.55 mm difference.
"""


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "overall_l": dict(
        desc="overall bar length",
        unit="mm",
        range={"easy": (101.0, 102.5), "medium": (99.0, 104.0), "hard": (96.0, 106.0)},
        source="Gotoh 101.5-102 / Faber 101.27; hard widened as proportion",
        askable=True,
    ),
    "stud_span": dict(
        desc="stud centre-to-centre span (the Gibson mounting standard)",
        unit="mm",
        range={"easy": (82.0, 82.55), "medium": (81.5, 83.0), "hard": (81.5, 83.0)},
        source="Gotoh 82 (metric) vs Gibson/StewMac/Faber 82.55 (3-1/4 in)",
        askable=True,
    ),
    "bar_w": dict(
        desc="bar section width (front-back)",
        unit="mm",
        range={"easy": (12.3, 12.75), "medium": (12.0, 13.2), "hard": (11.5, 13.8)},
        source="GE101Z 12.75 / GE101A 12.3; proportion at hard",
        askable=True,
    ),
    "bar_h": dict(
        desc="bar section height at the crown crest",
        unit="mm",
        range={"easy": (17.8, 18.0), "medium": (16.5, 18.5), "hard": (15.5, 19.0)},
        source="GE101Z 18 / GE101A 17.8; proportion at hard",
        askable=True,
    ),
    "tab_t": dict(
        desc="end-tab (ear) thickness",
        unit="mm",
        range={"easy": (6.8, 7.0), "medium": (6.0, 7.6), "hard": (5.5, 8.0)},
        source="GE101Z 7 / GE101A 6.8; proportion at hard",
        askable=True,
    ),
    "crown_r": dict(
        desc="crown radius along the bar top",
        unit="mm",
        range={"easy": (250.0, 300.0), "medium": (240.0, 320.0), "hard": (220.0, 340.0)},
        source="GE101Z R300 / GE101A R250; proportion at hard",
        askable=True,
    ),
    "ramp_len": dict(
        desc="blend length from the crowned body down into each ear",
        unit="mm",
        range={"easy": (8.0, 11.0), "medium": (6.0, 13.0), "hard": (5.0, 15.0)},
        source="proportion (smooth body-to-ear transition on the GE101Z photo/drawing)",
        askable=True,
    ),
    "string_pitch": dict(
        desc="string-hole pitch (span = 5x pitch)",
        unit="mm",
        range={"easy": (10.3, 10.3), "medium": (10.0, 10.6), "hard": (9.8, 10.8)},
        source="Gotoh 10.3 (51.5 span); slight vendor spread as proportion",
        askable=True,
    ),
    "hole_d": dict(
        desc="string-hole entry diameter",
        unit="mm",
        range={"easy": (5.0, 5.2), "medium": (4.8, 5.5), "hard": (4.5, 5.8)},
        source="GE101Z phi5.1 entry (exit phi3 when stepped)",
        askable=True,
    ),
    "slot_w": dict(
        desc="open stud-slot width in the ears",
        unit="mm",
        range={"easy": (8.0, 8.1), "medium": (7.8, 8.4), "hard": (7.5, 8.6)},
        source="Gotoh 8 / Faber 8.1",
        askable=True,
    ),
    "stepped_holes": dict(
        desc="stepped string bores phi entry -> ~0.6x exit (1) vs plain through (0)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        source="GE101Z section shows phi5.1 -> phi3 stepped bore",
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        feature=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    bad = []

    # the ears must close around the open stud slots with material past them
    if p["overall_l"] < p["stud_span"] + 2.0 * p["slot_w"] + 4.0:
        bad.append("overall_l < stud_span + 2*slot_w + 4: ears cannot close around the stud slots")

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
    crown_at_r0 = p["bar_h"] - x_r0 * x_r0 / (2.0 * p["crown_r"])
    if crown_at_r0 < p["tab_t"] + 2.0:
        bad.append("crown drops below tab_t+2 before the blend starts: crown too deep for the body (GE101Z crown is shallow)")

    # the slot needs side walls in the bar width
    if p["slot_w"] > p["bar_w"] - 3.5:
        bad.append("slot_w > bar_w - 3.5: stud slot leaves <1.75 mm ear wall each side")

    # string holes must sit inside the body above the tab
    if p["hole_d"] > (p["bar_h"] - p["tab_t"]) - 3.0:
        bad.append("hole_d > bar_h - tab_t - 3: string bore does not fit the raised body")

    return bad
