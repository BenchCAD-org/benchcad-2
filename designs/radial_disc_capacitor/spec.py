from bench2 import Resample


PARAM_SPEC = {
    "body_diameter": {
        "desc": "Overall capacitor body diameter",
        "unit": "mm",
        "range": {
            "easy": (7.0, 7.6),
            "medium": (6.8, 8.0),
            "hard": (6.6, 8.4),
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
            "hard": (1.8, 3.6),
        },
        "source": "user-provided STEP measurements; proportion",
        "askable": True,
    },
    "lead_spacing": {
        "desc": "Center-to-center spacing between the radial leads",
        "unit": "mm",
        "range": {
            "easy": (4.8, 5.4),
            "medium": (4.6, 5.8),
            "hard": (4.4, 6.0),
        },
        "source": "user-provided STEP measurements; proportion",
        "askable": True,
    },
    "lead_diameter": {
        "desc": "Diameter of each radial lead wire",
        "unit": "mm",
        "range": {
            "easy": (0.5, 0.7),
            "medium": (0.45, 0.8),
            "hard": (0.4, 0.9),
        },
        "source": "user-provided STEP measurements; proportion",
        "askable": True,
    },
    "lead_length": {
        "desc": "Free lead length below the body",
        "unit": "mm",
        "range": {
            "easy": (5.0, 6.0),
            "medium": (4.8, 6.8),
            "hard": (4.5, 7.2),
        },
        "source": "user-provided STEP measurements; proportion",
        "askable": True,
    },
    "lead_embed": {
        "desc": "How far each lead penetrates into the body for fusion",
        "unit": "mm",
        "range": {
            "easy": (0.5, 0.8),
            "medium": (0.45, 0.95),
            "hard": (0.4, 1.1),
        },
        "source": "proportion",
        "askable": False,
    },
}


def check(p):
    bad = []
    if p["body_diameter"] <= 0:
        bad.append("body_diameter must be positive")
    if p["body_thickness"] <= 0:
        bad.append("body_thickness must be positive")
    if p["lead_spacing"] <= 0:
        bad.append("lead_spacing must be positive")
    if p["lead_diameter"] <= 0:
        bad.append("lead_diameter must be positive")
    if p["lead_length"] <= 0:
        bad.append("lead_length must be positive")
    if p["lead_embed"] <= 0:
        bad.append("lead_embed must be positive")

    if p["lead_embed"] >= p["body_thickness"]:
        bad.append("lead_embed must be smaller than body_thickness so the leads exit the body")

    if p["lead_spacing"] + p["lead_diameter"] >= p["body_diameter"]:
        bad.append(
            "lead_spacing + lead_diameter must be smaller than body_diameter so both leads stay within the disc footprint"
        )

    if p["lead_spacing"] <= p["lead_diameter"] * 3:
        bad.append("lead_spacing must be several wire diameters so the leads remain distinct")

    return bad
