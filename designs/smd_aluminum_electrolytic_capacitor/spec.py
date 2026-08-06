from bench2 import Resample


PARAM_SPEC = {
    "body_diameter": {
        "desc": "Overall capacitor body diameter",
        "unit": "mm",
        "range": {
            "easy": (6.0, 6.6),
            "medium": (5.8, 6.9),
            "hard": (5.6, 7.3),
        },
        "source": "user-provided STEP measurements; proportion",
        "askable": True,
    },
    "body_thickness": {
        "desc": "Axial thickness of the disc body",
        "unit": "mm",
        "range": {
            "easy": (2.2, 2.8),
            "medium": (2.0, 3.2),
            "hard": (1.9, 3.6),
        },
        "source": "user-provided STEP measurements; proportion",
        "askable": True,
    },
    "lead_spacing": {
        "desc": "Center-to-center spacing between the radial leads",
        "unit": "mm",
        "range": {
            "easy": (6.8, 7.8),
            "medium": (6.4, 8.2),
            "hard": (6.0, 8.6),
        },
        "source": "user-provided STEP measurements; proportion",
        "askable": True,
    },
    "lead_diameter": {
        "desc": "Diameter of each radial lead wire",
        "unit": "mm",
        "range": {
            "easy": (0.6, 0.8),
            "medium": (0.5, 0.9),
            "hard": (0.45, 1.0),
        },
        "source": "user-provided STEP measurements; proportion",
        "askable": True,
    },
    "lead_length": {
        "desc": "Free lead length below the body",
        "unit": "mm",
        "range": {
            "easy": (4.8, 5.8),
            "medium": (4.6, 6.6),
            "hard": (4.4, 7.0),
        },
        "source": "user-provided STEP measurements; proportion",
        "askable": True,
    },
    "lead_embed": {
        "desc": "How far each lead penetrates into the body for fusion",
        "unit": "mm",
        "range": {
            "easy": (0.35, 0.7),
            "medium": (0.3, 0.9),
            "hard": (0.25, 1.0),
        },
        "source": "proportion",
        "askable": False,
    },
}


def check(p):
    bad = []
    for name in PARAM_SPEC:
        if p[name] <= 0:
            bad.append(f"{name} must be positive")

    if p["lead_embed"] >= p["body_thickness"]:
        bad.append("lead_embed must be smaller than body_thickness so the leads exit the body")

    if p["lead_spacing"] <= p["lead_diameter"] * 1.5:
        bad.append("lead_spacing must comfortably exceed lead_diameter so the leads do not overlap")

    if p["lead_length"] <= p["lead_embed"]:
        bad.append("lead_length must exceed lead_embed so there is exposed lead below the body")

    if p["body_diameter"] <= p["lead_spacing"] * 0.65:
        bad.append("body_diameter must stay large enough to cover the radial lead roots")

    if p["lead_length"] < 3.5:
        bad.append("lead_length must preserve the long, radial lead look of a disc capacitor")

    return bad
