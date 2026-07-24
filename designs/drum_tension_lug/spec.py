"""drum_tension_lug — the benchmark generator spec.

A drum-shell tension lug. PARAM_SPEC declares each build() parameter; check()
holds the engineering rules a reviewer audits. Nothing is coupled, so there is
no refine(). Spec: docs/DESIGN_SPEC.md

Sources:
- SD Sparedrum L-series lug catalogue: body ~42 x 27 x 23 mm (L20BD), mounting
  hole spacing faceted 25-70 mm, mounting hole Ø 6 / 8 mm, rod thread #12-24
  (7/32", ~5.5 mm). Single-ended lugs and double-ended tube lugs.
- Pearl spare-parts catalogue (rod threads #12-24 / M5 / M6); body scale
  cross-checked against US8759653B2 (~20.6 mm width).
"""


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "body_len": dict(
        desc="lug body length along the drum axis (rod direction)",
        unit="mm",
        range={"easy": (40.0, 55.0), "medium": (40.0, 90.0), "hard": (38.0, 150.0)},
        source="SD Sparedrum L20 (42 mm) up to full-length tube lugs (Pearl CL/STL)",
        askable=True,
    ),
    "body_h": dict(
        desc="lug body height standing off the shell (radial)",
        unit="mm",
        range={"easy": (23.0, 29.0), "medium": (20.0, 34.0), "hard": (18.0, 40.0)},
        source="SD Sparedrum L20BD 27 mm -> proportion",
        askable=True,
    ),
    "body_w": dict(
        desc="lug body width tangent to the shell",
        unit="mm",
        range={"easy": (22.0, 25.0), "medium": (20.0, 29.0), "hard": (18.0, 33.0)},
        source="SD Sparedrum L20 23 mm; US8759653B2 ~20.6 mm cross-check",
        askable=True,
    ),
    "hole_spacing": dict(
        desc="centre-to-centre spacing of the two mounting screws",
        unit="mm",
        range={"easy": (24.0, 30.0), "medium": (24.0, 50.0), "hard": (24.0, 70.0)},
        source="SD Sparedrum mounting-hole facet 25-70 mm",
        askable=True,
    ),
    "mount_hole_d": dict(
        desc="mounting screw hole diameter",
        unit="mm",
        range={"easy": (5.5, 6.5), "medium": (5.0, 8.0), "hard": (5.0, 9.0)},
        source="SD Sparedrum mounting hole Ø 6 / 8 mm",
        askable=True,
    ),
    "rod_bore": dict(
        desc="tension-rod thread insert bore diameter",
        unit="mm",
        range={"easy": (5.0, 6.0), "medium": (4.5, 6.5), "hard": (4.5, 7.0)},
        source="rod thread #12-24 (7/32 ~5.5 mm) / M5 / M6 (Pearl, vintagedrumreference)",
        askable=True,
    ),
    "fillet_r": dict(
        desc="radius on the vertical body corners (cast look)",
        unit="mm",
        range={"easy": (2.0, 4.0), "medium": (2.0, 5.0), "hard": (1.0, 6.0)},
        source="proportion (die-cast lug corner radius)",
        askable=True,
    ),
    "double_ended": dict(
        desc="tube lug with a rod bore at BOTH ends (1) vs single-ended (0)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        source="SD Sparedrum single-ended lug vs double-ended tube lug",
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        feature=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    bad = []

    # mounting holes must sit on the body with edge material at both ends
    if p["hole_spacing"] > p["body_len"] - 12.0:
        bad.append("hole_spacing > body_len-12: mounting holes need >=6 mm edge to each end")

    # the two mounting holes must not merge into one
    if p["hole_spacing"] < p["mount_hole_d"] + 4.0:
        bad.append("hole_spacing < mount_hole_d+4: the two mounting holes would break through")

    # corner radius must be under half the smaller footprint dimension
    if p["fillet_r"] > 0.4 * min(p["body_w"], p["body_len"]):
        bad.append("fillet_r > 0.4*min(body_w,body_len): corner radius too large for the footprint")

    # mounting hole leaves body wall across the width
    if p["mount_hole_d"] > p["body_w"] - 6.0:
        bad.append("mount_hole_d > body_w-6: <3 mm wall beside the mounting hole")

    # rod bore leaves body wall through the height
    if p["rod_bore"] > p["body_h"] - 6.0:
        bad.append("rod_bore > body_h-6: <3 mm wall around the rod insert")

    return bad
