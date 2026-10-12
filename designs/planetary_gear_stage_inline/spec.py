"""planetary_gear_stage_inline — benchmark generator.

Almost nothing here is a free number. The catalogue single-stage ratio fixes the
tooth-count ratio outright, coaxiality fixes the ring from the sun and planet, and
the assembly and neighbouring conditions decide which planet counts are admissible
at all. The output bearing and the shaft seal are *selected from standard tables*
by the output journal, never dimensioned; the housing diameter is then whatever it
has to be for the tie bolts to clear both the ring gear and the bearing seat.

`refine()` therefore does real work: it derives the tooth counts from the drawn
ratio, selects the standard hardware, and rejects a base draw that cannot be built
as a complete gearhead — rather than tabulating combinations.

Sources
  ISO 53 / DIN 867   basic rack: alpha 20 deg, addendum 1.0*m, dedendum 1.25*m
  ISO 54 / DIN 780   module series
  DIN 3960           parameter definitions
  ISO 15 / DIN 625-1 deep-groove ball bearings, series 60 (output bearings)
  DIN 3760 form A    radial shaft seals (output seal)
  DIN 471            retaining rings (planet pins)
  ISO 4762           socket head cap screws (case tie bolts)
  Neugart PLE        a widely published gearhead of this class; i = 3, 4 and 5 are
                     three of its single-stage ratios and the output shaft
                     dimensions below are its D3/L3 rows
                     https://www.neugart.com/fileadmin/user_upload/Downloads/Catalog_Chapters/Neugart_PLE_EN.pdf
"""

from bench2 import Resample
from part import (layout, housing_od_min, output_bearing, ball_count,
                  screw_size, clamp_length)

# ISO 54 / DIN 780 series I, the range that suits these frame sizes.
MODULES = [0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0]

# Single-stage ratios offered in this gearhead class.
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
        "source": "single-stage ratios offered in this gearhead class (Neugart PLE "
                  "lists 3, 4 and 5 among them)",
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
        "source": "gearheads of this class run 3 planets; 4-6 appear on "
                  "higher-torque frames. Admissibility is decided by the assembly "
                  "and neighbouring conditions, not by preference",
    },
    "face_width": {
        "desc": "gear face width",
        "unit": "mm",
        "range": {"easy": (4.0, 10.0), "medium": (3.0, 20.0), "hard": (3.0, 28.0)},
        "source": "proportion; drawn, then brought into the 4-13x module band that "
                  "this class runs (check() enforces the wider 3-16x)",
    },
    "housing_od": {
        "desc": "housing outside diameter",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (30.0, 140.0), "medium": (24.0, 260.0), "hard": (24.0, 320.0)},
        "source": "derived: whichever is larger of the ring root plus a rim, and the "
                  "diameter the tie bolts need to clear the ring gear and the "
                  "bearing seat with a wall on both sides",
    },
    "housing_face_t": {
        "desc": "housing rear wall thickness behind the gears",
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
        "desc": "sun shaft length projecting from the gear into the motor adapter",
        "unit": "mm",
        "range": {"easy": (8.0, 18.0), "medium": (6.0, 30.0), "hard": (6.0, 40.0)},
        "source": "proportion, drawn then raised if needed so the shaft reaches "
                  "past the rear wall far enough for the clamping hub to grip it",
    },
    "output_shaft_d": {
        "desc": "carrier output shaft diameter, h7 in the catalogue",
        "unit": "mm",
        "range": {"easy": (6.0, 14.0), "medium": (5.0, 30.0), "hard": (5.0, 40.0)},
        "source": "Neugart PLE 'Shaft diameter output D3 h7': 10 / 14 / 20 / 25 / 40 "
                  "across frames 040-160",
    },
    "output_shaft_len": {
        "desc": "carrier output shaft length beyond the bearing head face",
        "unit": "mm",
        "range": {"easy": (10.0, 26.0), "medium": (8.0, 60.0), "hard": (8.0, 90.0)},
        "source": "Neugart PLE 'Shaft length output L3': 26 / 35 / 40 / 55 / 87",
    },
    "n_case_screws": {
        "desc": "tie bolts clamping bearing head, housing and motor adapter together",
        "unit": "",
        "integer": True,
        "range": {"easy": (4, 4), "medium": (4, 6), "hard": (4, 8)},
        "choices": {"easy": [4], "medium": [4, 6], "hard": [4, 6, 8]},
        "source": "ISO 4762 socket head cap screws; 4 on small frames, 6-8 on large "
                  "ones. The thread size itself is derived from the ring diameter",
    },
    "n_output_balls": {
        "desc": "total balls in the two output bearings (2x the per-bearing complement)",
        "unit": "",
        "integer": True,
        "refine": True,
        "range": {"easy": (14, 20), "medium": (14, 20), "hard": (14, 20)},
        "source": "derived: the complement that fits on the pitch circle of the "
                  "selected ISO 15 series-60 bearing, twice over",
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

    # face width is a proportion of the module, so draw it and then bring it into
    # the band rather than resampling: a free face_width in a wide range rejects
    # almost every small-module draw, and the symptom is a COVERAGE failure on
    # `module`, not an error about face width.
    lo_f, hi_f = PARAM_SPEC["face_width"]["range"][difficulty]
    p["face_width"] = round(min(max(p["face_width"], max(4.0 * m, lo_f)),
                                min(13.0 * m, hi_f)), 2)

    # likewise: the sun has to reach past the rear wall far enough to be clamped.
    # Solve L >= housing_face_t + max(4, 0.35*L) + 1.2 for L.
    lo_s, hi_s = PARAM_SPEC["sun_shaft_len"]["range"][difficulty]
    sd = screw_size(m * zr)
    need_len = p["sun_shaft_len"]
    for _ in range(6):                      # clamp_length is monotone in the length
        need_len = p["housing_face_t"] + clamp_length(need_len, sd) + 1.0
    if need_len > hi_s:
        raise Resample                      # rear wall too thick for any shaft here
    p["sun_shaft_len"] = round(min(max(p["sun_shaft_len"], need_len), hi_s), 2)
    # keep the shaft inside the sun root circle with a wall left over
    p["sun_shaft_d"] = round(max(3.0, 0.62 * (m * zs - 2.0 * _DEDENDUM * m)), 2)

    # The housing is the larger of the old rim proportion and what the tie bolts
    # actually need. `housing_od_min` lives in part.py and is the same function
    # the build uses, so the two cannot disagree about the wall.
    need = housing_od_min(m, zr, p["output_shaft_d"])
    if need is None:
        raise Resample                      # output shaft off the top of ISO 15/60
    rim_od = m * zr + 2.0 * _DEDENDUM * m + 2.0 * _RIM * m * zr
    p["housing_od"] = round(max(rim_od, need + 0.6), 2)

    bearing = output_bearing(p["output_shaft_d"])
    p["n_output_balls"] = 2 * ball_count(bearing[0], bearing[1])

    for k in ("z_planet", "z_ring", "housing_od", "sun_shaft_d", "n_output_balls"):
        lo, hi = PARAM_SPEC[k]["range"][difficulty]
        if not (lo - 1e-6 <= p[k] <= hi + 1e-6):
            raise Resample

    # Final gate: the single source of truth for whether these numbers describe a
    # gearhead that can be bored, assembled and bolted together. Duplicating its
    # conditions here is how the two drift apart, so it is called, not copied.
    if _layout(p) is None:
        raise Resample


def _layout(p):
    return layout(p["module"], int(p["z_sun"]), int(p["z_planet"]), int(p["z_ring"]),
                  int(p["n_planets"]), p["face_width"], p["housing_od"],
                  p["housing_face_t"], p["sun_shaft_d"], p["sun_shaft_len"],
                  p["output_shaft_d"], p["output_shaft_len"])


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

    # face width against module: too narrow and the teeth are foil, too wide and
    # a straight-cut stage cannot hold contact across the face
    if not 3.0 * m <= p["face_width"] <= 16.0 * m:
        bad.append("face_width %.2f outside 3-16x module (%.2f-%.2f): spur planetary "
                   "stages in this class run about 6-12x (shop practice)"
                   % (p["face_width"], 3.0 * m, 16.0 * m))

    # --- the gearhead hardware, not just the gear set -----------------------
    bearing = output_bearing(p["output_shaft_d"])
    if bearing is None:
        bad.append("output_shaft_d %.2f is off the top of ISO 15 / DIN 625-1 series "
                   "60 (largest bore tabulated is 40): the output bearing would have "
                   "to be invented rather than selected"
                   % p["output_shaft_d"])
    else:
        need = housing_od_min(m, zr, p["output_shaft_d"])
        if p["housing_od"] < need:
            bad.append("housing_od %.2f < %.2f: the tie bolts cannot clear both the "
                       "ring root and the %d mm bearing seat with a wall on each "
                       "side, so the case cannot be bolted together"
                       % (p["housing_od"], need, bearing[1]))
        if 2 * ball_count(bearing[0], bearing[1]) != int(p["n_output_balls"]):
            bad.append("n_output_balls %d does not match the complement the selected "
                       "%dx%dx%d bearing holds (%d per bearing, two bearings)"
                       % (int(p["n_output_balls"]), bearing[0], bearing[1], bearing[2],
                          ball_count(bearing[0], bearing[1])))

    # the sun has to reach far enough back to be gripped by the clamping hub
    clamp_len = clamp_length(p["sun_shaft_len"], screw_size(m * zr))
    if p["sun_shaft_len"] < p["housing_face_t"] + clamp_len + 1.0:
        bad.append("sun_shaft_len %.2f leaves nothing past the %.2f rear wall for the "
                   "%.2f clamping hub: the sun would have no drive connection and no "
                   "support at all (it is deliberately not carried on its own bearing)"
                   % (p["sun_shaft_len"], p["housing_face_t"], clamp_len))

    # catch-all: anything layout() rejects that is not named above
    if not bad and _layout(p) is None:
        bad.append("the derived layout is not buildable (bore steps not monotonic, "
                   "planet bore breaks into the tooth roots, or the carrier plate "
                   "does not clear the bearing head bore)")

    return bad
