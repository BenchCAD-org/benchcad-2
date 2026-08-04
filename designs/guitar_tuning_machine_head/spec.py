"""guitar_tuning_machine_head — the benchmark generator.

Anchored to the Grover Rotomatic 102 drawing (issue #9) with the catalog
spread of the 102 / Super / Mini and Gotoh SG381 lines. Catalog-discrete
values (post diameter, bushing class, housing width) are drawn from choices
with coverage so every real size appears; everything else is a documented
proportion around the 102 drawing.
"""

PARAM_SPEC = {
    "plate_w": {
        "desc": "baseplate (gear lobe) width, coupled to the housing envelope",
        "unit": "mm",
        "range": {"easy": (22.9, 25.0), "medium": (19.0, 25.0), "hard": (19.0, 25.0)},
        "refine": True,
        "source": "Grover 102 drawing: 23.85 face on the 27.05 envelope (ratio 0.88)",
    },
    "plate_t": {
        "desc": "baseplate thickness",
        "unit": "mm",
        "range": {"easy": (2.2, 2.8), "medium": (2.0, 3.0), "hard": (1.8, 3.2)},
        "source": "proportion (die-cast flange of a 27 mm housing)",
    },
    "housing_w": {
        "desc": "gear housing width across the cover face",
        "unit": "mm",
        "range": {"easy": (27.0, 27.1), "medium": (22.4, 27.1), "hard": (22.4, 27.1)},
        "choices": {"easy": [27.05], "medium": [27.05, 27.1], "hard": [22.4, 27.05, 27.1]},
        "coverage": [22.4, 27.05, 27.1],
        "source": "catalog: Grover 102 27.05, Gotoh SG381 27.1, SG381 mini 22.4 (issue #9 table)",
    },
    "housing_h": {
        "desc": "gear drum diameter (the drawing's 18 housing height)",
        "unit": "mm",
        "range": {"easy": (13.0, 19.0), "medium": (13.0, 19.0), "hard": (13.0, 19.0)},
        "refine": True,
        "source": "coupled 0.60-0.68 of the envelope (drawing: 18 on the 27.05 body)",
    },
    "housing_d": {
        "desc": "gear housing depth (cover face to back)",
        "unit": "mm",
        "range": {"easy": (13.0, 15.0), "medium": (12.0, 16.0), "hard": (11.0, 17.0)},
        "source": "Grover 102 drawing: 28.2-23 span behind the plate; proportion band",
    },
    "post_d": {
        "desc": "string post diameter (string section)",
        "unit": "mm",
        "range": {"easy": (6.0, 6.3), "medium": (6.0, 6.3), "hard": (6.0, 6.3)},
        "refine": True,
        "coverage": [6.0, 6.3],
        "source": "catalog row-locked to housing_w: Grover 102/Gotoh 6.0, Grover Super 6.3 (issue #9)",
    },
    "barrel_d": {
        "desc": "post lower-barrel diameter, journalled in the housing",
        "unit": "mm",
        "range": {"easy": (9.7, 10.1), "medium": (9.4, 10.4), "hard": (9.1, 10.7)},
        "source": "Grover 102 drawing: Ø9.9 [.39]",
    },
    "post_h": {
        "desc": "exposed post height, baseplate to under the tip cap",
        "unit": "mm",
        "range": {"easy": (19.0, 22.0), "medium": (17.5, 23.5), "hard": (16.0, 25.0)},
        "source": "Grover 102 drawing: 43 overall minus 18 housing; ~27 post over plate (issue #9)",
    },
    "bushing_od": {
        "desc": "peghole bushing body diameter (press-in collar or hex ferrule)",
        "unit": "mm",
        "range": {"easy": (7.8, 14.0), "medium": (7.8, 14.0), "hard": (7.8, 14.0)},
        "refine": True,
        "coverage": [7.8, 14.0],
        "source": "catalog row-locked to housing_w: Grover 7.8 collar, Gotoh 14.0 hex (issue #9)",
    },
    "string_hole_d": {
        "desc": "transverse string hole diameter through the post",
        "unit": "mm",
        "range": {"easy": (2.1, 2.3), "medium": (2.0, 2.5), "hard": (1.9, 2.7)},
        "source": "Grover 102 drawing: string hole 2.2 [.087]",
    },
    "screw_d": {
        "desc": "locating wood-screw hole diameter in the baseplate ear",
        "unit": "mm",
        "range": {"easy": (2.5, 2.7), "medium": (2.3, 3.0), "hard": (2.2, 3.2)},
        "source": "Grover 102 drawing: screw hole 2.6 [.102]",
    },
    "key_shaft_d": {
        "desc": "worm/key shaft diameter out the housing side",
        "unit": "mm",
        "range": {"easy": (4.2, 4.8), "medium": (4.0, 5.2), "hard": (3.8, 5.6)},
        "source": "proportion (shaft under the 8 mm button stem)",
    },
    "button_w": {
        "desc": "tuning button width across the pear profile",
        "unit": "mm",
        "range": {"easy": (23.0, 24.5), "medium": (21.5, 26.0), "hard": (20.0, 27.5)},
        "source": "Grover 102 drawing: 23.85 [.939]",
    },
    "button_h": {
        "desc": "tuning button height, shaft axis to crown",
        "unit": "mm",
        "range": {"easy": (16.5, 17.5), "medium": (15.5, 19.0), "hard": (14.5, 20.5)},
        "source": "Grover 102 drawing: 17 [.669]",
    },
    "button_t": {
        "desc": "tuning button thickness",
        "unit": "mm",
        "range": {"easy": (7.6, 8.4), "medium": (7.0, 9.0), "hard": (6.5, 9.5)},
        "source": "Grover 102 drawing: 8 [.315]",
    },
}


# catalog model rows: housing envelope -> (post_d, bushing_od) pairs that
# actually ship together (issue #9 table)
MODEL_ROWS = {
    22.4: [(6.0, 7.8)],                  # mini
    27.05: [(6.0, 7.8), (6.3, 7.8)],     # Grover 102 / Super
    27.1: [(6.0, 14.0)],                 # Gotoh SG381
}


def check(p):
    bad = []
    # the screw ear must sit OUTBOARD of the sealed gear box (box width is
    # 0.68*plate_w in build): the ear hole's inner edge must clear the box
    # half-width plus a cast-web margin, so the screw can never bore the
    # gearbox — the drawing's ear hole sits 10.5 from centre vs the ~8.5 cavity
    if (p["housing_w"] / 2.0 - 1.15 * p["screw_d"] - p["screw_d"] / 2.0
            < 0.34 * p["plate_w"] + 0.4):
        bad.append("screw hole would enter the sealed gear box: housing_w/2 - 1.65*screw_d "
                   "must clear 0.34*plate_w + 0.4 (ear outboard of the cavity)")
    if p["barrel_d"] <= p["post_d"] + 2.0:
        bad.append("barrel_d must step >=2 mm over post_d (drawing: 9.9 barrel under 6 post)")
    if p["bushing_od"] < 10.0 and p["bushing_od"] <= p["post_d"] + 1.2:
        bad.append("press-in bushing wall too thin: bushing_od must exceed post_d + 1.2")
    # the locating screw drops vertically at the ear; its line must clear the
    # drum surface (3D line-to-axis distance vs drum radius)
    if (p["housing_w"] / 2.0 - 1.15 * p["screw_d"] - p["screw_d"] / 2.0
            < p["housing_h"] / 2.0 + 0.2):
        bad.append("screw line would graze the gear drum: housing_w/2 - 1.65*screw_d "
                   "must clear housing_h/2 + 0.2 (ear outboard of the drum)")
    if p["button_h"] < p["key_shaft_d"] * 2.5:
        bad.append("button too small to grip: button_h >= 2.5*key_shaft_d (ergonomic rule)")
    if p["string_hole_d"] >= p["post_d"] * 0.5:
        bad.append("string hole >= half the post: post section would be gutted (strength rule)")
    return bad


def refine(p, difficulty, rng):
    # the plate lobe scales with the casting envelope (drawing: 23.85/27.05)
    p["plate_w"] = round(p["housing_w"] * float(rng.uniform(0.85, 0.92)), 1)
    # post/bushing come from the same catalog MODEL ROW as the housing —
    # no 22.4 mini with a 6.3 Super post or a Gotoh hex ferrule
    rows = MODEL_ROWS[p["housing_w"]]
    p["post_d"], p["bushing_od"] = rows[int(rng.integers(len(rows)))]
    # the drum diameter scales with the casting envelope (drawing: 18/27.05)
    p["housing_h"] = round(p["housing_w"] * float(rng.uniform(0.60, 0.68)), 1)
