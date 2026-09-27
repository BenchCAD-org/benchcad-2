"""Sampling contract for BenchCAD issue #186 compound stepped planet stage."""

_ROWS = {
    18: (22, 14, 54, 3),  # i = 40/7
    20: (20, 16, 56, 4),  # i = 9/2
    24: (18, 12, 54, 3),  # i = 35/8
    28: (20, 18, 66, 2),  # i = 20/3
}


def _constant(desc, unit, value, source):
    return {
        "desc": desc,
        "unit": unit,
        "range": {"easy": (value, value), "medium": (value, value), "hard": (value, value)},
        "choices": [value],
        "source": source,
    }


PARAM_SPEC = {
    "module": {
        "desc": "spur gear module", "unit": "mm",
        "range": {"easy": (2.0, 2.0), "medium": (1.5, 2.0), "hard": (1.0, 2.5)},
        "choices": {"easy": [2.0], "medium": [1.5, 2.0], "hard": [1.0, 1.5, 2.0, 2.5]},
        "coverage": [1.0, 1.5, 2.0, 2.5],
        "source": "ISO 54 / DIN 780 preferred module series",
        "askable": True,
    },
    "z_sun": {
        "desc": "sun tooth count", "unit": "",
        "range": {"easy": (18, 18), "medium": (18, 24), "hard": (18, 28)},
        "choices": {"easy": [18], "medium": [18, 20, 24], "hard": [18, 20, 24, 28]},
        "coverage": [18, 20, 24, 28],
        "integer": True,
        "source": "issue #186 tooth-count ladder",
        "askable": True,
    },
    "z_step_a": {
        "desc": "compound planet step-A tooth count", "unit": "",
        "range": {"easy": (18, 22), "medium": (18, 22), "hard": (18, 22)},
        "integer": True, "refine": True,
        "source": "issue #186 tooth-count ladder; coupled to z_sun",
    },
    "z_step_b": {
        "desc": "compound planet step-B tooth count", "unit": "",
        "range": {"easy": (12, 14), "medium": (12, 16), "hard": (12, 18)},
        "integer": True, "refine": True,
        "source": "issue #186 tooth-count ladder; coupled to z_sun",
    },
    "z_ring": {
        "desc": "held internal ring tooth count", "unit": "",
        "range": {"easy": (54, 54), "medium": (54, 56), "hard": (54, 66)},
        "integer": True, "refine": True,
        "source": "issue #186 tooth-count ladder; coupled to z_sun",
    },
    "n_planets": {
        "desc": "number of identical compound planets", "unit": "",
        "range": {"easy": (3, 3), "medium": (3, 4), "hard": (2, 4)},
        "integer": True, "refine": True,
        "source": "phase-timing admissibility checked from issue #186 mesh rule",
    },
    "tooth_width": {
        "desc": "axial face width of each toothed step", "unit": "mm",
        "range": {"easy": (7.0, 7.0), "medium": (5.0, 7.0), "hard": (3.5, 8.0)},
        "choices": {"easy": [7.0], "medium": [5.0, 7.0], "hard": [3.5, 5.0, 7.0, 8.0]},
        "coverage": [3.5, 5.0, 7.0, 8.0],
        "source": "proportion: 3-16 module face-width band for straight-cut gearing",
        "askable": True,
    },
    "interstep_gap": {
        "desc": "axial gap between the two rigid planet gear steps", "unit": "mm",
        "range": {"easy": (2.5, 2.5), "medium": (1.5, 2.5), "hard": (1.0, 3.0)},
        "choices": {"easy": [2.5], "medium": [1.5, 2.5], "hard": [1.0, 1.5, 2.5, 3.0]},
        "coverage": [1.0, 1.5, 2.5, 3.0],
        "source": "proportion: distinct toothed stations need a visible axial separator",
        "askable": True,
    },
    "carrier_angle": _constant(
        "static carrier angle", "deg", 0.0,
        "reference pose: all timed meshes shown at the issue drawing datum",
    ),
}


def refine(p, difficulty, rng):
    del difficulty, rng
    p["z_step_a"], p["z_step_b"], p["z_ring"], p["n_planets"] = _ROWS[int(p["z_sun"])]


def check(p):
    bad = []
    zs = int(p["z_sun"])
    za = int(p["z_step_a"])
    zb = int(p["z_step_b"])
    zr = int(p["z_ring"])
    n = int(p["n_planets"])
    if (za, zb, zr, n) != _ROWS.get(zs):
        bad.append("tooth counts must be one issue #186 coupled table row")
    if zs + za != zr - zb:
        bad.append("z_sun + z_step_a must equal z_ring - z_step_b (coaxiality)")
    ratio = 1.0 + (za * zr) / float(zs * zb)
    if ratio <= 1.0:
        bad.append("ring-fixed carrier ratio must be a speed reduction")
    if not 3.0 * p["module"] <= p["tooth_width"] <= 8.0 * p["module"]:
        bad.append("tooth_width must remain in the 3-8 module face-width proportion band")
    if not 0.5 * p["module"] <= p["interstep_gap"] <= 3.0 * p["module"]:
        bad.append("interstep_gap must remain in the 0.5-3 module separator band")
    if n < 2:
        bad.append("compound planet carrier needs at least two planets")
    return bad
