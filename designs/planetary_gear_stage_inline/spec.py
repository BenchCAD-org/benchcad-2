"""planetary_gear_stage_inline — benchmark generator.

Almost nothing here is a free number. The single-stage ratio the catalogue
offers fixes the tooth-count ratio outright, coaxiality fixes the ring from the
sun and planet, and the assembly and neighbouring conditions decide which planet
counts are admissible at all. `refine()` therefore does real work: it derives
the tooth counts from the drawn ratio and rejects a base draw that cannot be
built, rather than tabulating combinations.

Sources
  ISO 53 / DIN 867   basic rack: alpha 20 deg, addendum 1.0*m, dedendum 1.25*m
  ISO 54 / DIN 780   module series
  DIN 3960           parameter definitions
  Neugart PLE        single-stage ratios i = 3, 4, 5; frame sizes 040-160
                     https://www.neugart.com/fileadmin/user_upload/Downloads/Catalog_Chapters/Neugart_PLE_EN.pdf
"""

from bench2 import Resample

# ISO 54 / DIN 780 series I, the range that suits these frame sizes.
MODULES = [0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0]

# Neugart PLE publishes exactly these three single-stage ratios.
RATIOS = [3, 4, 5]

_ADDENDUM = 1.0
_DEDENDUM = 1.25
_RIM = 0.16

PARAM_SPEC = {
    "ratio": {
        "desc": "nominal single-stage reduction, carrier output with the ring fixed",
        "unit": "",
        "integer": True,
        "range": {"easy": (3, 5), "medium": (3, 5), "hard": (3, 5)},
        "choices": {"easy": [4], "medium": RATIOS, "hard": RATIOS},
        "coverage": RATIOS,
        "source": "Neugart PLE single-stage ratios i = 3, 4, 5",
    },
    "module": {
        "desc": "gear module, shared by sun, planets and ring",
        "unit": "mm",
        "range": {"easy": (0.8, 1.25), "medium": (0.5, 2.0), "hard": (0.5, 2.0)},
        "choices": {"easy": [0.8, 1.0, 1.25], "medium": MODULES, "hard": MODULES},
        "coverage": MODULES,
        "source": "ISO 54 / DIN 780 module series",
    },
    "z_sun": {
        "desc": "sun tooth count",
        "unit": "",
        "integer": True,
        "range": {"easy": (12, 20), "medium": (10, 28), "hard": (10, 32)},
        "source": "shop practice: below about 10 teeth a 20 deg involute undercuts",
    },
    "z_planet": {
        "desc": "planet tooth count",
        "unit": "",
        "integer": True,
        "refine": True,
        "range": {"easy": (5, 30), "medium": (4, 48), "hard": (4, 48)},
        "source": "derived: z_planet = z_sun*(i-2)/2 from the ratio and coaxiality",
    },
    "z_ring": {
        "desc": "ring tooth count, internal",
        "unit": "",
        "integer": True,
        "refine": True,
        "range": {"easy": (24, 80), "medium": (20, 128), "hard": (20, 128)},
        "source": "derived: z_ring = z_sun + 2*z_planet (coaxiality)",
    },
    "n_planets": {
        "desc": "number of planets",
        "unit": "",
        "integer": True,
        "range": {"easy": (3, 3), "medium": (3, 5), "hard": (3, 6)},
        "choices": {"easy": [3], "medium": [3, 4, 5], "hard": [3, 4, 5, 6]},
        "source": "PLE-class gearheads run 3 planets; 4-6 appear on higher-torque "
                  "frames. Admissibility is decided by the assembly and neighbouring "
                  "conditions, not by preference",
    },
    "face_width": {
        "desc": "gear face width",
        "unit": "mm",
        "range": {"easy": (4.0, 10.0), "medium": (3.0, 20.0), "hard": (3.0, 28.0)},
        "source": "proportion; face width runs roughly 6-12x module in this class",
    },
    "housing_od": {
        "desc": "housing outside diameter",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (30.0, 120.0), "medium": (24.0, 240.0), "hard": (24.0, 300.0)},
        "source": "derived: ring root diameter plus a proportional rim",
    },
    "housing_face_t": {
        "desc": "housing end-face thickness behind the gears",
        "unit": "mm",
        "range": {"easy": (3.0, 6.0), "medium": (2.0, 10.0), "hard": (2.0, 14.0)},
        "source": "proportion",
    },
    "sun_shaft_d": {
        "desc": "sun input shaft diameter",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (4.0, 20.0), "medium": (3.0, 40.0), "hard": (3.0, 50.0)},
        "source": "derived: sized under the sun root circle so the shaft does not "
                  "break through the tooth roots",
    },
    "sun_shaft_len": {
        "desc": "sun shaft length projecting from the gear",
        "unit": "mm",
        "range": {"easy": (6.0, 14.0), "medium": (4.0, 30.0), "hard": (4.0, 40.0)},
        "source": "proportion",
    },
    "output_shaft_d": {
        "desc": "carrier output shaft diameter, h7 in the catalogue",
        "unit": "mm",
        "range": {"easy": (6.0, 14.0), "medium": (5.0, 30.0), "hard": (5.0, 40.0)},
        "source": "Neugart PLE 'Shaft diameter output D3 h7': 10 / 14 / 20 / 25 / 40 "
                  "across frames 040-160",
    },
    "output_shaft_len": {
        "desc": "carrier output shaft length from the carrier face",
        "unit": "mm",
        "range": {"easy": (10.0, 26.0), "medium": (8.0, 60.0), "hard": (8.0, 90.0)},
        "source": "Neugart PLE 'Shaft length output L3': 26 / 35 / 40 / 55 / 87",
    },
    "carrier_angle": {
        "desc": "carrier rotation; the operating state, planets stay meshed as it turns",
        "unit": "deg",
        "range": {"easy": (0.0, 0.0), "medium": (0.0, 90.0), "hard": (0.0, 240.0)},
        "source": "operating state, not a dimension (proportion)",
    },
}


def refine(p, difficulty, rng):
    i, zs, n = int(p["ratio"]), int(p["z_sun"]), int(p["n_planets"])
    m = p["module"]

    # ratio and coaxiality together fix the tooth counts
    num = zs * (i - 2)
    if num % 2:
        raise Resample                      # z_planet would not be a whole tooth
    zp = num // 2
    zr = zs + 2 * zp
    if zp < 4:
        raise Resample                      # too few teeth to cut a usable planet
    if (zs + zr) % n:
        raise Resample                      # planets cannot sit at equal pitch
    # neighbouring: adjacent planets must clear each other
    import math as _m
    if (zs + zp) * _m.sin(_m.pi / n) <= zp + 2:
        raise Resample

    p["z_planet"], p["z_ring"] = zp, zr
    p["housing_od"] = round(m * zr + 2.0 * _DEDENDUM * m + 2.0 * _RIM * m * zr, 2)
    # keep the shaft inside the sun root circle with a wall left over
    p["sun_shaft_d"] = round(max(3.0, 0.62 * (m * zs - 2.0 * _DEDENDUM * m)), 2)

    for k in ("z_planet", "z_ring", "housing_od", "sun_shaft_d"):
        lo, hi = PARAM_SPEC[k]["range"][difficulty]
        if not (lo - 1e-6 <= p[k] <= hi + 1e-6):
            raise Resample


def check(p):
    import math
    bad = []
    m, zs, zp, zr = p["module"], int(p["z_sun"]), int(p["z_planet"]), int(p["z_ring"])
    n = int(p["n_planets"])

    if zr != zs + 2 * zp:
        bad.append("z_ring != z_sun + 2*z_planet: the sun, planets and ring are not "
                   "coaxial and the stage cannot be assembled (planetary kinematics)")

    if (zs + zr) % n:
        bad.append("(z_sun + z_ring) mod n_planets != 0: the planets cannot sit at "
                   "equal angular pitch and still mesh (assembly condition)")

    if (zs + zp) * math.sin(math.pi / n) <= zp + 2:
        bad.append("(z_sun+z_planet)*sin(pi/n_planets) <= z_planet+2: adjacent planet "
                   "tip circles foul each other (neighbouring condition)")

    if abs((1.0 + zr / zs) - p["ratio"]) > 1e-6:
        bad.append("1 + z_ring/z_sun != ratio: the tooth counts do not produce the "
                   "nominal reduction (carrier output, ring fixed)")

    # 20 deg full-depth involute undercuts below 17 teeth without profile shift;
    # 10 is the practical floor with the tip relief this class uses.
    for name, z in (("z_sun", zs), ("z_planet", zp)):
        if z < 10:
            bad.append("%s = %d: a 20 deg full-depth involute undercuts badly below "
                       "10 teeth (DIN 867 basic rack, no profile shift declared)"
                       % (name, z))

    # the input shaft must stay inside the sun root circle
    root_d = m * zs - 2.0 * _DEDENDUM * m
    if p["sun_shaft_d"] >= root_d:
        bad.append("sun_shaft_d %.2f reaches the sun root circle %.2f: the shaft would "
                   "break through the tooth roots" % (p["sun_shaft_d"], root_d))

    # the ring must be inside the housing with a rim left
    ring_root_d = m * zr + 2.0 * _DEDENDUM * m
    if p["housing_od"] <= ring_root_d + 2.0:
        bad.append("housing_od %.2f leaves no rim over the ring root %.2f (a ring gear "
                   "cut into the bore needs wall behind it)"
                   % (p["housing_od"], ring_root_d))

    # face width against module: too narrow and the teeth are foil, too wide and
    # a straight-cut stage cannot hold contact across the face
    if not 3.0 * m <= p["face_width"] <= 16.0 * m:
        bad.append("face_width %.2f outside 3-16x module (%.2f-%.2f): spur planetary "
                   "stages in this class run about 6-12x (shop practice)"
                   % (p["face_width"], 3.0 * m, 16.0 * m))

    return bad
