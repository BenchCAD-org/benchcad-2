"""Sampling contract for the issue #182 core planetary stage."""

def _constant(desc, unit, value, source, askable=False):
    return dict(
        desc=desc, unit=unit,
        range={"easy": (value, value), "medium": (value, value), "hard": (value, value)},
        choices=[value], source=source, askable=askable,
    )


PARAM_SPEC = {
    "module": dict(
        desc="spur gear module", unit="mm",
        range={"easy": (1.0, 1.0), "medium": (0.8, 1.0), "hard": (0.8, 1.25)},
        choices={"easy": [1.0], "medium": [0.8, 1.0], "hard": [0.8, 1.0, 1.25]},
        coverage=[0.8, 1.0, 1.25],
        source="ISO 54 / DIN 780 preferred module series", askable=True,
    ),
    "z_sun": _constant("sun tooth count", "", 12,
                       "chosen 4:1 stage; ratio relation is checked"),
    "z_planet": _constant("planet tooth count", "", 12,
                          "chosen 4:1 stage; coaxiality relation is checked"),
    "z_ring": _constant("internal ring tooth count", "", 36,
                        "chosen 4:1 stage; 1 + z_ring/z_sun = 4"),
    "n_planets": _constant("number of planet gears", "", 3,
                           "three-planet carrier; assembly and clearance are checked"),
    "face_width": dict(
        desc="gear face width", unit="mm",
        range={"easy": (10.0, 10.0), "medium": (8.0, 12.0), "hard": (8.0, 14.0)},
        choices={"easy": [10.0], "medium": [8.0, 10.0, 12.0],
                 "hard": [8.0, 10.0, 12.0, 14.0]},
        source="proportion: straight-cut planetary gears commonly use 3-16 modules",
        askable=True,
    ),
    "sun_shaft_d": _constant("input sun shaft diameter", "mm", 6.0,
                             "proportion: kept inside the sun root diameter", True),
    "sun_shaft_len": _constant("input shaft projection", "mm", 21.15,
                               "proportion: 0.45 times PLE060 housing length L2 = 47 mm"),
    "output_shaft_d": _constant("output shaft diameter D3 h7", "mm", 14.0,
                                "Neugart PLE060 table, output shaft D3 h7", True),
    "output_shaft_len": _constant("output shaft length L3", "mm", 35.0,
                                  "Neugart PLE060 table, output shaft L3", True),
    "shaft_collar_d": _constant("output shaft collar diameter D4", "mm", 17.0,
                                "Neugart PLE060 table, shaft collar D4", True),
    "key_w": _constant("feather key width B1", "mm", 5.0,
                       "Neugart PLE060 table and DIN 6885-1 A 5 x 5 x 25", True),
    "key_len": _constant("feather key length L5", "mm", 25.0,
                         "Neugart PLE060 table and DIN 6885-1 A 5 x 5 x 25"),
    "center_hole_d": _constant("output centre hole diameter C", "mm", 5.0,
                               "Neugart PLE060 table, DIN 332 type DR M5 x 12.5"),
    "center_hole_depth": _constant("output centre hole depth", "mm", 12.5,
                                   "Neugart PLE060 table, DIN 332 type DR M5 x 12.5"),
    "carrier_angle": dict(
        desc="carrier operating angle", unit="deg",
        range={"easy": (0.0, 0.0), "medium": (0.0, 30.0), "hard": (0.0, 90.0)},
        choices={"easy": [0.0], "medium": [0.0, 30.0], "hard": [0.0, 30.0, 90.0]},
        source="operating state; mesh phasing is derived from planetary kinematics",
        askable=True,
    ),
}


def check(p):
    import math

    bad = []
    zs, zp, zr, n = int(p["z_sun"]), int(p["z_planet"]), int(p["z_ring"]), int(p["n_planets"])
    if zr != zs + 2 * zp:
        bad.append("z_ring must equal z_sun + 2*z_planet (coaxiality)")
    if (zs + zr) % n:
        bad.append("(z_sun + z_ring) must divide by n_planets (equal planet pitch)")
    if (zs + zp) * math.sin(math.pi / n) <= zp + 2:
        bad.append("adjacent planet tip circles overlap")
    if abs((1.0 + zr / zs) - 4.0) > 1e-9:
        bad.append("tooth counts must form the selected single-stage 4:1 ratio")
    sun_root_d = p["module"] * zs - 2.0 * 1.25 * p["module"]
    if p["sun_shaft_d"] >= sun_root_d:
        bad.append("sun shaft reaches the sun root diameter")
    if not 3.0 * p["module"] <= p["face_width"] <= 16.0 * p["module"]:
        bad.append("face width must remain in the 3-16 module gear proportion band")
    if p["shaft_collar_d"] < p["output_shaft_d"]:
        bad.append("D4 collar cannot be smaller than D3 output shaft")
    if p["key_w"] >= p["output_shaft_d"]:
        bad.append("DIN 6885 key width must be smaller than output shaft diameter")
    if p["center_hole_depth"] >= p["output_shaft_len"]:
        bad.append("DIN 332 centre hole must remain blind")
    return bad

