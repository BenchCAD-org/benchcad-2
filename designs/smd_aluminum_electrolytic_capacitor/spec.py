PARAM_SPEC = {
    "body_diameter": {
        "desc": "Diameter of the vertical aluminum capacitor can",
        "unit": "mm",
        "range": {"easy": (6.1, 6.5), "medium": (5.8, 6.9), "hard": (5.5, 7.4)},
        "source": "STEP measurement; proportion",
        "askable": True,
    },
    "can_height": {
        "desc": "Height of the cylindrical can above the plastic SMD base",
        "unit": "mm",
        "range": {"easy": (7.3, 8.0), "medium": (6.9, 8.4), "hard": (6.4, 9.0)},
        "source": "STEP measurement; proportion",
        "askable": True,
    },
    "base_length": {
        "desc": "Overall length of the rectangular SMD base and terminal carrier",
        "unit": "mm",
        "range": {"easy": (8.4, 9.2), "medium": (8.0, 9.7), "hard": (7.5, 10.4)},
        "source": "STEP measurement; proportion",
        "askable": True,
    },
    "base_width": {
        "desc": "Overall width of the rectangular SMD base",
        "unit": "mm",
        "range": {"easy": (7.7, 8.5), "medium": (7.3, 8.9), "hard": (6.9, 9.5)},
        "source": "STEP measurement; proportion",
        "askable": True,
    },
    "base_thickness": {
        "desc": "Thickness of the plastic base below the capacitor can",
        "unit": "mm",
        "range": {"easy": (1.4, 1.8), "medium": (1.25, 2.0), "hard": (1.1, 2.25)},
        "source": "STEP measurement; proportion",
        "askable": True,
    },
    "terminal_span": {
        "desc": "Center-to-center span used to place the two SMD terminal pads",
        "unit": "mm",
        "range": {"easy": (6.9, 7.7), "medium": (6.5, 8.1), "hard": (6.0, 8.7)},
        "source": "STEP measurement; proportion",
        "askable": True,
    },
    "terminal_width": {
        "desc": "Width of each visible SMD terminal pad",
        "unit": "mm",
        "range": {"easy": (0.8, 1.1), "medium": (0.7, 1.3), "hard": (0.6, 1.5)},
        "source": "proportion",
        "askable": True,
    },
    "terminal_thickness": {
        "desc": "Thickness of the metal SMD terminal pads below the base",
        "unit": "mm",
        "range": {"easy": (0.18, 0.28), "medium": (0.14, 0.34), "hard": (0.1, 0.4)},
        "source": "proportion",
        "askable": False,
    },
    "rim_radius": {
        "desc": "Small radius used on the can rim and vertical can edges",
        "unit": "mm",
        "range": {"easy": (0.18, 0.32), "medium": (0.12, 0.42), "hard": (0.08, 0.55)},
        "source": "proportion",
        "askable": True,
    },
}


def check(p):
    bad = []
    for name in PARAM_SPEC:
        if p[name] <= 0:
            bad.append(f"{name} must be positive")

    if p["body_diameter"] >= min(p["base_length"], p["base_width"]) * 0.92:
        bad.append("body_diameter must leave visible plastic base around the can")
    if p["terminal_span"] >= p["base_length"]:
        bad.append("terminal_span must fit inside the base length")
    if p["terminal_span"] <= p["body_diameter"] * 0.82:
        bad.append("terminal_span must remain wide enough for opposite SMD terminals")
    if p["terminal_width"] >= p["base_length"] * 0.32:
        bad.append("terminal_width must stay smaller than the base end features")
    if p["terminal_thickness"] >= p["base_thickness"] * 0.45:
        bad.append("terminal_thickness must stay thinner than the plastic base")
    if p["rim_radius"] >= p["body_diameter"] * 0.12:
        bad.append("rim_radius must remain a small capacitor-can edge blend")
    if p["can_height"] <= p["base_thickness"] * 2.2:
        bad.append("can_height must dominate the SMD base thickness")

    return bad
