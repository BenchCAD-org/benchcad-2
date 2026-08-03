"""tilting_speaker_wall_bracket — the benchmark generator.

Anchored to the B-Tech BT77 technical drawing (issue #7): plate 67.9 x 260.4,
jaw width 132.4 -> 280.3, reach to 270.3, cradle pattern 91.5 x 45.8, max
tilt 10 (BT77) / 20 (BT332) as the catalog's discrete tilt classes. The wall
hole pattern (keyhole 6.5 at the 30 offset, holes at 76 / 127, slot 8.5 at
145) and the 10.5 pivot are drawing constants inside part.py.
"""

PARAM_SPEC = {
    "plate_w": {
        "desc": "wall plate width",
        "unit": "mm",
        "range": {"easy": (64.0, 70.0), "medium": (60.0, 74.0), "hard": (56.0, 78.0)},
        "source": "BT77 drawing: 67.9 over the 60 hole band",
    },
    "plate_h": {
        "desc": "wall plate height",
        "unit": "mm",
        "range": {"easy": (256.0, 262.0), "medium": (250.0, 268.0), "hard": (244.0, 274.0)},
        "source": "BT77 drawing: 260.4 (254 hole zone + rims)",
    },
    "plate_d": {
        "desc": "wall column depth off the wall",
        "unit": "mm",
        "range": {"easy": (27.0, 31.0), "medium": (25.0, 33.0), "hard": (23.0, 35.0)},
        "source": "BT77 side view: 29",
    },
    "plate_t": {
        "desc": "wall column face/wall thickness",
        "unit": "mm",
        "range": {"easy": (2.2, 3.0), "medium": (2.0, 3.4), "hard": (1.8, 3.8)},
        "source": "proportion (stamped steel plate of a 25 kg mount)",
    },
    "arm_reach": {
        "desc": "standoff arm length, plate face to knuckle root",
        "unit": "mm",
        "range": {"easy": (180.0, 240.0), "medium": (150.0, 262.0), "hard": (135.0, 270.3)},
        "source": "BT77 drawing: 270.3 max reach; BT77 adjustable band 135-280 (issue #7 table)",
    },
    "arm_h": {
        "desc": "wall-end upright height of the arm weldment",
        "unit": "mm",
        "range": {"easy": (104.0, 116.0), "medium": (98.0, 122.0), "hard": (92.0, 128.0)},
        "source": "BT77 drawing: 110.3",
    },
    "beam_w": {
        "desc": "arm beam square section",
        "unit": "mm",
        "range": {"easy": (20.0, 26.0), "medium": (18.0, 28.0), "hard": (16.0, 30.0)},
        "source": "proportion (25 kg cantilever)",
    },
    "knuckle_d": {
        "desc": "clamp knuckle disc diameter",
        "unit": "mm",
        "range": {"easy": (82.0, 96.0), "medium": (76.0, 102.0), "hard": (70.0, 108.0)},
        "source": "proportion read off the BT77 top view disc",
    },
    "knuckle_t": {
        "desc": "clamp knuckle disc height",
        "unit": "mm",
        "range": {"easy": (22.0, 28.0), "medium": (20.0, 30.0), "hard": (18.0, 32.0)},
        "source": "proportion (houses the two slide bars + pivot seat)",
    },
    "bar_d": {
        "desc": "jaw slide-bar square section",
        "unit": "mm",
        "range": {"easy": (9.0, 12.0), "medium": (8.0, 13.0), "hard": (7.0, 14.0)},
        "source": "proportion read off the BT77 top view bars",
    },
    "jaw_span": {
        "desc": "clamp opening, jaw grip face to jaw grip face",
        "unit": "mm",
        "range": {"easy": (160.0, 240.0), "medium": (140.0, 265.0), "hard": (132.4, 280.3)},
        "source": "BT77 drawing: min width 132.4, max width 280.3 (continuously adjustable)",
    },
    "jaw_h": {
        "desc": "jaw grip plate height",
        "unit": "mm",
        "range": {"easy": (100.0, 120.0), "medium": (92.0, 128.0), "hard": (84.0, 136.0)},
        "source": "proportion (grip plate on the cabinet side; no catalog number)",
    },
    "jaw_d": {
        "desc": "jaw grip plate depth (into the room)",
        "unit": "mm",
        "range": {"easy": (120.0, 140.0), "medium": (110.0, 150.0), "hard": (100.0, 160.0)},
        "source": "BT77 drawing: 140 over the jaw pair",
    },
    "cradle_w": {
        "desc": "cradle top plate width (wall direction)",
        "unit": "mm",
        "range": {"easy": (76.0, 84.0), "medium": (70.0, 90.0), "hard": (64.0, 96.0)},
        "source": "BT77 drawing: 80 cradle plate",
    },
    "cradle_l": {
        "desc": "cradle top plate length (across the jaws)",
        "unit": "mm",
        "range": {"easy": (120.0, 140.0), "medium": (110.0, 150.0), "hard": (104.0, 160.0)},
        "source": "proportion: carries the 91.5 hole span with a rim",
    },
    "max_tilt": {
        "desc": "tilt class, the +/- travel limit",
        "unit": "deg",
        "range": {"easy": (10.0, 10.0), "medium": (10.0, 20.0), "hard": (10.0, 20.0)},
        "choices": {"easy": [10.0], "medium": [10.0, 20.0], "hard": [10.0, 20.0]},
        "coverage": [10.0, 20.0],
        "source": "catalog: BT77 +/-10, BT332 +/-20 (issue #7 table)",
    },
    "tilt_pose": {
        "desc": "sampled operating tilt of the cradle",
        "unit": "deg",
        "range": {"easy": (-10.0, 10.0), "medium": (-20.0, 20.0), "hard": (-20.0, 20.0)},
        "refine": True,
        "source": "operating state within the max_tilt class",
    },
}


def check(p):
    bad = []
    if p["jaw_span"] < p["knuckle_d"] + 40.0:
        bad.append("jaws would ride onto the knuckle: jaw_span must exceed knuckle_d + 40 "
                   "(slide bars keep engagement)")
    if p["cradle_l"] > p["jaw_span"] - 18.0:
        bad.append("cradle plate would strike the jaw plates: cradle_l must stay under "
                   "jaw_span - 18 (speaker sits between the jaws)")
    if p["cradle_l"] < 104.0:
        bad.append("cradle too short for the 91.5 hole span plus rim (BT77 pattern)")
    if p["knuckle_t"] < p["bar_d"] + 8.0:
        bad.append("knuckle too thin for its slide bores: knuckle_t must exceed bar_d + 8")
    if p["knuckle_d"] < p["bar_d"] * 4.0:
        bad.append("knuckle disc too small for two offset slide bores (bar_off = 0.18*knuckle_d)")
    if p["plate_h"] < 230.0:
        bad.append("plate shorter than the 30 + 145 + slot hole pattern needs (BT77 layout)")
    if p["arm_h"] > p["plate_h"] * 0.55:
        bad.append("arm upright taller than half the plate: not a BT77 proportion")
    if p["jaw_h"] < 60.0:
        bad.append("jaw plate under 60 cannot steady a cabinet (proportion)")
    return bad


def refine(p, difficulty, rng):
    # the sampled pose lives inside this instance's tilt class
    p["tilt_pose"] = round(float(rng.uniform(-p["max_tilt"], p["max_tilt"])), 1)
