"""cabinet_bar_pull_handle — the benchmark generator spec.

A cabinet/drawer bar pull (round bar on two standoff posts). PARAM_SPEC declares
each build() parameter; check() holds the engineering rules a reviewer audits.
Nothing is coupled, so there is no refine(). Spec: docs/DESIGN_SPEC.md

Sources:
- Berenson SS hollow bar-pull series (7068-7072) + Richelieu BP305 line: bar
  Ø12 mm, post Ø10 mm, projection 32.5-35 mm, center-to-center 76-638 mm, mount
  tapped 8-32 / M4. Overall length = C-C + ~2*overhang.
- Bar Ø / post Ø / projection cross-checked constant across Berenson, Amerock,
  Hickory; C-C is the catalog ladder (96/128/160/192/224/320 mm). Within one
  line only C-C + length vary, so bar Ø / post Ø / projection are "proportion".
"""


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "center_to_center": dict(
        desc="center-to-center spacing of the two mounting posts",
        unit="mm",
        range={"easy": (96.0, 192.0), "medium": (76.0, 320.0), "hard": (76.0, 638.0)},
        source="Berenson 7068-7072 / Richelieu BP305 C-C ladder (76-638 mm)",
        askable=True,
    ),
    "overhang": dict(
        desc="bar overhang past each post (overall length = C-C + 2*overhang)",
        unit="mm",
        range={"easy": (24.0, 40.0), "medium": (20.0, 50.0), "hard": (18.0, 60.0)},
        source="Richelieu overhang ~40 mm; Berenson ~24 mm -> proportion",
        askable=True,
    ),
    "projection": dict(
        desc="standoff height (how far the bar stands off the cabinet face)",
        unit="mm",
        range={"easy": (32.0, 35.0), "medium": (28.0, 38.0), "hard": (25.0, 42.0)},
        source="Berenson 32.5 mm / Amerock 35 mm / Hickory 32 mm",
        askable=True,
    ),
    "bar_d": dict(
        desc="handle bar diameter",
        unit="mm",
        range={"easy": (11.0, 13.0), "medium": (10.0, 16.0), "hard": (9.0, 16.0)},
        source="Berenson/Amerock/Hickory Ø12 mm (1/2 in) -> proportion across lines",
        askable=True,
    ),
    "post_d": dict(
        desc="standoff-post diameter",
        unit="mm",
        range={"easy": (9.0, 11.0), "medium": (8.0, 12.0), "hard": (7.0, 13.0)},
        source="Berenson Ø10 mm / Amerock 3/8 in (9.5 mm) -> proportion",
        askable=True,
    ),
    "tap_d": dict(
        desc="mounting-screw tap hole diameter (in the post base)",
        unit="mm",
        range={"easy": (3.2, 3.6), "medium": (3.0, 4.5), "hard": (2.5, 5.0)},
        source="8-32 / M4 tap (Berenson M4; Richelieu 8-32)",
        askable=True,
    ),
    "tap_depth": dict(
        desc="tap-hole depth into the post",
        unit="mm",
        range={"easy": (5.0, 7.0), "medium": (4.0, 10.0), "hard": (4.0, 12.0)},
        source="Richelieu 8-32 x 6 mm deep -> proportion",
        askable=True,
    ),
    "chamfer_ends": dict(
        desc="bar ends chamfered (1) vs square (0)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        source="Richelieu bar ends C1.2x45 chamfer",
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        feature=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    bad = []

    # finger clearance under the bar (projection is to the bar's outer face, so
    # the clear gap below the bar is projection - bar_d)
    if p["projection"] - p["bar_d"] < 8.0:
        bad.append("projection - bar_d < 8: too little finger clearance under the bar")

    # the mounting tap must fit within the post (post rises to z = projection - bar_d/2)
    if p["tap_depth"] > p["projection"] - p["bar_d"] / 2.0 - 2.0:
        bad.append("tap_depth exceeds the post height (projection - bar_d/2 - 2): tap would break through")

    # the tap hole must leave a post wall
    if p["tap_d"] > p["post_d"] - 2.5:
        bad.append("tap_d > post_d-2.5: tap leaves <1.25 mm post wall")

    # posts must be clearly separated
    if p["center_to_center"] < p["post_d"] + 8.0:
        bad.append("center_to_center < post_d+8: posts too close / overlapping")

    # the bar must actually overhang the posts
    if p["overhang"] < p["bar_d"]:
        bad.append("overhang < bar_d: bar ends barely clear the posts")

    return bad
