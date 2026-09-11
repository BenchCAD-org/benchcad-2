"""Parameter spec for the generic gusseted corner bracket."""


PARAM_SPEC = {
    "overall_width": dict(
        desc="L, total bracket width across the two side panels",
        unit="mm",
        range={"easy": (27.8, 28.2), "medium": (26.0, 30.0), "hard": (24.0, 32.0)},
        source="validated benchmark geometry; adjustable engineering-proportion range",
        askable=True,
    ),
    "slot_width": dict(
        desc="W, central rounded opening and locator-tab width",
        unit="mm",
        range={"easy": (5.9, 6.1), "medium": (5.5, 6.4), "hard": (5.2, 6.4)},
        source="validated benchmark geometry; adjustable engineering-proportion range",
        askable=True,
    ),
    "side_step": dict(
        desc="W1, side-panel top step and lower step size",
        unit="mm",
        range={"easy": (7.4, 7.6), "medium": (7.0, 8.0), "hard": (6.6, 8.4)},
        source="validated benchmark geometry; adjustable engineering-proportion range",
        askable=True,
    ),
    "overall_height": dict(
        desc="H, total length/height of the side profile",
        unit="mm",
        range={"easy": (34.8, 35.2), "medium": (32.0, 38.0), "hard": (30.0, 40.0)},
        source="validated benchmark geometry; adjustable engineering-proportion range",
        askable=True,
    ),
    "opening_offset": dict(
        desc="A, lower datum for the paired rounded central openings",
        unit="mm",
        range={"easy": (13.4, 13.6), "medium": (12.5, 14.5), "hard": (12.0, 15.0)},
        source="validated benchmark geometry; adjustable engineering-proportion range",
        askable=True,
    ),
    "opening_spacing": dict(
        desc="B, spacing between the paired rounded central-opening centers",
        unit="mm",
        range={"easy": (7.9, 8.1), "medium": (7.0, 9.0), "hard": (6.5, 9.5)},
        source="validated benchmark geometry; adjustable engineering-proportion range",
        askable=True,
    ),
    "opening_radius": dict(
        desc="R, radius of the larger rounded central-opening arcs",
        unit="mm",
        range={"easy": (3.45, 3.55), "medium": (3.2, 3.8), "hard": (3.2, 4.0)},
        source="validated benchmark geometry; adjustable engineering-proportion range",
        askable=True,
    ),
    "plate_thickness": dict(
        desc="T, horizontal and vertical mounting-plate thickness",
        unit="mm",
        range={"easy": (4.4, 4.6), "medium": (4.1, 4.9), "hard": (3.8, 5.2)},
        source="validated benchmark geometry; adjustable engineering-proportion range",
        askable=True,
    ),
    "side_thickness": dict(
        desc="T1, thickness of each outer side panel along X",
        unit="mm",
        range={"easy": (2.9, 3.1), "medium": (2.6, 3.4), "hard": (2.4, 3.6)},
        source="validated benchmark geometry; adjustable engineering-proportion range",
        askable=True,
    ),
    "panel_mount_holes": dict(
        desc="optional pair of coaxial M5 tap-drill holes through the two side panels",
        unit="bool",
        range={"easy": (False, False), "medium": (True, True), "hard": (True, True)},
        choices={"easy": [False], "medium": [True], "hard": [True]},
        source="validated optional side-panel-hole benchmark variant; easy keeps the round24 no-hole baseline",
        askable=True,
        feature=True,
    ),
}


DEFAULTS = {
    "overall_width": 28.0,
    "slot_width": 6.0,
    "side_step": 7.5,
    "overall_height": 35.0,
    "opening_offset": 13.5,
    "opening_spacing": 8.0,
    "opening_radius": 3.5,
    "plate_thickness": 4.5,
    "side_thickness": 3.0,
    "panel_mount_holes": False,
}


def check(p: dict) -> list[str]:
    bad = []

    for key, value in DEFAULTS.items():
        if isinstance(value, bool):
            continue
        if p[key] <= 0:
            bad.append(f"{key} must be positive")

    if p["overall_width"] <= 2.0 * p["side_thickness"] + p["slot_width"] + 0.5:
        bad.append("overall_width must leave room for both side panels and the central opening")

    if p["side_thickness"] >= p["plate_thickness"]:
        bad.append("side_thickness must remain thinner than the main mounting plates")

    if p["slot_width"] >= 2.0 * p["opening_radius"]:
        bad.append("slot_width must be smaller than twice opening_radius so the rounded openings remain real")

    if p["side_step"] <= 2.0:
        bad.append("side_step must exceed the fixed side-panel corner radius")

    if p["overall_height"] <= 2.0 * p["side_step"] + 8.0:
        bad.append("overall_height must leave enough length for the stepped side-panel slope")

    if p["opening_offset"] + p["opening_spacing"] + p["opening_radius"] >= p["overall_height"] - 2.0:
        bad.append("central rounded openings must stay inside the side-profile envelope")

    if p["opening_offset"] - p["opening_radius"] <= p["plate_thickness"]:
        bad.append("central rounded openings must clear the mounting-plate corner thickness")

    if p["plate_thickness"] >= p["overall_height"] * 0.25:
        bad.append("plate_thickness too large for the available profile height")

    return bad
