"""duct_takeoff_starting_collar — the benchmark generator spec.

A round-duct takeoff / starting collar (tabbed, optional butterfly damper).
PARAM_SPEC declares each build() parameter; check() holds the engineering rules a
reviewer audits. Nothing is coupled, so there is no refine().
Spec: docs/DESIGN_SPEC.md

Sources:
- GreenSeam tabbed / spin-in start collar spec sheets + ECCO and M&M submittals:
  collar (branch) Ø 4-20 in (100-500 mm), cylindrical body ~6 in, crimp/bead
  1-5/8 in, base tabs ~1 in, ~16 trapezoidal tabs, damper axis 2 in below the
  bead. Galvanized steel ASTM A653, 26 ga std / 24 ga option.
- Only diameter varies per catalog row (lengths constant); tab count/width not
  dimensioned -> "proportion".
"""


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "collar_d": dict(
        desc="collar (branch-duct) nominal diameter",
        unit="mm",
        range={"easy": (150.0, 300.0), "medium": (100.0, 400.0), "hard": (100.0, 500.0)},
        source="GreenSeam/ECCO/M&M start-collar sizes 4-20 in (100-500 mm)",
        askable=True,
    ),
    "collar_h": dict(
        desc="cylindrical barrel height",
        unit="mm",
        range={"easy": (80.0, 120.0), "medium": (60.0, 150.0), "hard": (55.0, 160.0)},
        source="GreenSeam ~6 in body -> proportion",
        askable=True,
    ),
    "wall": dict(
        desc="sheet-metal wall thickness",
        unit="mm",
        range={"easy": (0.5, 0.7), "medium": (0.5, 0.85), "hard": (0.4, 0.9)},
        source="26 ga (0.55 mm) / 24 ga (0.7 mm) galvanized, ASTM A653",
        askable=True,
    ),
    "bead_proj": dict(
        desc="outward projection of the rolled top bead",
        unit="mm",
        range={"easy": (2.0, 4.0), "medium": (2.0, 5.0), "hard": (1.5, 6.0)},
        source="proportion (rolled stiffening bead)",
        askable=True,
    ),
    "tab_h": dict(
        desc="mounting-tab length (radial reach)",
        unit="mm",
        range={"easy": (20.0, 28.0), "medium": (15.0, 32.0), "hard": (12.0, 35.0)},
        source="GreenSeam tab ~1 in (25 mm)",
        askable=True,
    ),
    "tab_w": dict(
        desc="mounting-tab width",
        unit="mm",
        range={"easy": (12.0, 18.0), "medium": (10.0, 22.0), "hard": (8.0, 26.0)},
        source="proportion (tab width not dimensioned; ~16 tabs on the photo)",
        askable=True,
    ),
    "tab_count": dict(
        desc="number of base mounting tabs",
        unit="",
        range={"easy": (14, 18), "medium": (12, 20), "hard": (10, 24)},
        source="GreenSeam photo ~16 trapezoidal tabs -> proportion",
        integer=True,
        askable=True,
    ),
    "damper": dict(
        desc="integral butterfly damper (blade + shaft) fitted (1) vs none (0)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        source="GreenSeam/ECCO with-damper vs plain start-collar variants",
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        feature=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    import math

    bad = []

    # the tabs must fit around the base circumference with gaps between them
    if p["tab_count"] * p["tab_w"] > 0.9 * math.pi * p["collar_d"]:
        bad.append("tab_count*tab_w > 0.9*pi*D: tabs overlap around the base")

    # rolled sheet, not thick pipe
    if p["wall"] > p["collar_d"] / 60.0:
        bad.append("wall > D/60: collar is rolled sheet metal, not thick pipe")

    # the bead must be smaller than the mounting tabs
    if p["bead_proj"] > p["tab_h"]:
        bad.append("bead_proj > tab_h: bead should be a small rib, not larger than a tab")

    # a barrel, not a flat ring: body height must exceed the wall bead zone
    if p["collar_h"] < 6.0 * p["wall"] + 20.0:
        bad.append("collar_h too short: barrel must clear the bead zone with a real body")

    return bad
