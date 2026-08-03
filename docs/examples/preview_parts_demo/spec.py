PARAM_SPEC = {
    "block_w": {
        "desc": "block width",
        "unit": "mm",
        "range": {"easy": (40.0, 50.0), "medium": (40.0, 60.0), "hard": (40.0, 70.0)},
        "source": "proportion",
    },
    "block_t": {
        "desc": "block thickness",
        "unit": "mm",
        "range": {"easy": (10.0, 12.0), "medium": (10.0, 16.0), "hard": (10.0, 20.0)},
        "source": "proportion",
    },
    "bore_d": {
        "desc": "bushing bore seat diameter",
        "unit": "mm",
        "range": {"easy": (12.0, 14.0), "medium": (12.0, 18.0), "hard": (12.0, 22.0)},
        "source": "proportion",
    },
    "bolt_d": {
        "desc": "bolt shank diameter",
        "unit": "mm",
        "range": {"easy": (4.0, 5.0), "medium": (4.0, 6.0), "hard": (4.0, 8.0)},
        "source": "proportion",
    },
    "bolt_pitch": {
        "desc": "bolt center-to-center spacing",
        "unit": "mm",
        "range": {"easy": (26.0, 32.0), "medium": (26.0, 40.0), "hard": (26.0, 48.0)},
        "source": "proportion",
    },
}


def check(p):
    bad = []
    if p["bolt_pitch"] > p["block_w"] - 2.5 * p["bolt_d"]:
        bad.append("bolt_pitch too wide: counterbores must stay inside the block (proportion)")
    if p["bore_d"] + 6.0 + 1.9 * p["bolt_d"] > p["bolt_pitch"] * 1.6:
        bad.append("bore/flange crowds the bolt circle (proportion)")
    return bad
