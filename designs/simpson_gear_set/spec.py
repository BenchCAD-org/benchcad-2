"""simpson_gear_set — benchmark generator.

Two ordinary planetary stages on ONE sun, with the stage-1 carrier bolted to the
stage-2 ring. Each stage is an ordinary planetary, so the #182 admissibility
conditions carry over unchanged and apply per stage — unlike the compound trains
(#186, #187), where they do not.

What the coupling buys is the ratio ladder: the same gearset gives four ratios
depending on which member is driven and which is held.

    1st  ring1 in, carrier2 held :  i = (z_r1 + z_r2 + z_s) / z_r1
    2nd  ring1 in, sun held      :  i = 1 + z_s / z_r1
    3rd  ring1 and sun both in   :  i = 1  (direct)
    rev  sun in,   carrier2 held :  i = -z_r2 / z_s

All four were solved from a 5-equation Willis system in exact rational arithmetic
on three tooth sets before being written down; the 3rd-gear case is an
overdetermined check — pin both sun and ring1 to 1 and every member, planets
included, must come out at exactly 1, and it does.

Sources
  ISO 53 / DIN 867   basic rack: alpha 20 deg, addendum 1.0*m, dedendum 1.25*m
  ISO 54 / DIN 780   module series
  DIN 3960           parameter definitions
  Topology: the Simpson set, the layout that defined the 3-speed automatic.
  Ratios are a property of the tooth counts, not of any one product's table.
"""

import math

from bench2 import Resample

MODULES = [0.8, 1.0, 1.25, 1.5, 2.0, 2.5]

PARAM_SPEC = {
    "module": {
        "desc": "gear module, shared by both stages",
        "unit": "mm",
        "range": {"easy": (1.0, 2.0), "medium": (0.8, 2.5), "hard": (0.8, 2.5)},
        "choices": {"easy": [1.0, 1.25, 1.5], "medium": MODULES, "hard": MODULES},
        "coverage": MODULES,
        "source": "ISO 54 / DIN 780 module series",
    },
    "z_sun": {
        "desc": "common sun tooth count, shared by both stages",
        "unit": "",
        "integer": True,
        "range": {"easy": (24, 30), "medium": (18, 36), "hard": (16, 40)},
        "source": "shop practice: a 20 deg full-depth involute undercuts below "
                  "about 17 teeth without profile shift",
    },
    "z_planet1": {
        "desc": "stage-1 planet tooth count",
        "unit": "",
        "integer": True,
        "range": {"easy": (18, 24), "medium": (14, 30), "hard": (12, 34)},
        "source": "free: with the sun fixed it sets z_ring1 and so the 1st/2nd "
                  "gear ratios",
    },
    "z_planet2": {
        "desc": "stage-2 planet tooth count",
        "unit": "",
        "integer": True,
        "range": {"easy": (18, 24), "medium": (14, 30), "hard": (12, 34)},
        "source": "free: with the sun fixed it sets z_ring2 and so 1st and reverse",
    },
    "z_ring1": {
        "desc": "stage-1 ring tooth count, internal",
        "unit": "",
        "integer": True,
        "refine": True,
        "range": {"easy": (60, 78), "medium": (46, 96), "hard": (40, 108)},
        "source": "derived: z_ring1 = z_sun + 2*z_planet1 (coaxiality)",
    },
    "z_ring2": {
        "desc": "stage-2 ring tooth count, internal",
        "unit": "",
        "integer": True,
        "refine": True,
        "range": {"easy": (60, 78), "medium": (46, 96), "hard": (40, 108)},
        "source": "derived: z_ring2 = z_sun + 2*z_planet2 (coaxiality)",
    },
    "n_planets1": {
        "desc": "number of stage-1 planets",
        "unit": "",
        "integer": True,
        "range": {"easy": (3, 3), "medium": (3, 4), "hard": (3, 5)},
        "choices": {"easy": [3], "medium": [3, 4], "hard": [3, 4, 5]},
        "source": "three is the usual count; more is admissible only when the "
                  "assembly and neighbouring conditions allow it",
    },
    "n_planets2": {
        "desc": "number of stage-2 planets",
        "unit": "",
        "integer": True,
        "range": {"easy": (3, 3), "medium": (3, 4), "hard": (3, 5)},
        "choices": {"easy": [3], "medium": [3, 4], "hard": [3, 4, 5]},
        "source": "set independently of stage 1; the two stages share only the sun",
    },
    "face_width": {
        "desc": "gear face width, same on both stages",
        "unit": "mm",
        "range": {"easy": (8.0, 18.0), "medium": (5.0, 26.0), "hard": (5.0, 32.0)},
        "source": "proportion; brought into the 4-13x module band in refine()",
    },
    "stage_gap": {
        "desc": "axial clearance between the carrier-1 plate and stage 2",
        "unit": "mm",
        "range": {"easy": (2.0, 5.0), "medium": (1.5, 8.0), "hard": (1.5, 10.0)},
        "source": "proportion",
    },
    "input_len": {
        "desc": "length of the ring-1 input drum ahead of stage 1",
        "unit": "mm",
        "range": {"easy": (8.0, 16.0), "medium": (6.0, 26.0), "hard": (6.0, 34.0)},
        "source": "proportion",
    },
    "output_len": {
        "desc": "length of the output hub beyond the flange",
        "unit": "mm",
        "range": {"easy": (10.0, 20.0), "medium": (8.0, 34.0), "hard": (8.0, 44.0)},
        "source": "proportion",
    },
    "output_angle": {
        "desc": "operating state: output rotation in 1st gear; every other "
                "member's angle is solved from it",
        "unit": "deg",
        "range": {"easy": (0.0, 0.0), "medium": (0.0, 60.0), "hard": (0.0, 120.0)},
        "source": "operating state, not a dimension (proportion)",
    },
}


def _ratios(zs, zp1, zp2):
    zr1, zr2 = zs + 2 * zp1, zs + 2 * zp2
    return zr1, zr2, (zr1 + zr2 + zs) / zr1, 1.0 + zs / zr1, -zr2 / zs


def refine(p, difficulty, rng):
    zs = int(p["z_sun"])
    zp1, zp2 = int(p["z_planet1"]), int(p["z_planet2"])
    n1, n2 = int(p["n_planets1"]), int(p["n_planets2"])
    m = p["module"]

    zr1, zr2, i1, i2, irev = _ratios(zs, zp1, zp2)
    p["z_ring1"], p["z_ring2"] = zr1, zr2

    for zp in (zp1, zp2):
        if zp < 10:
            raise Resample                 # undercut floor
    # each stage is an ordinary planetary: the #182 conditions apply per stage
    for zr, zp, n in ((zr1, zp1, n1), (zr2, zp2, n2)):
        if (zs + zr) % n:
            raise Resample                 # planets cannot sit at equal pitch
        if (zs + zp) * math.sin(math.pi / n) <= zp + 2:
            raise Resample                 # adjacent planet tips foul

    # a Simpson set that does not produce a usable ladder is not the topology
    if not (2.0 <= i1 <= 3.2):
        raise Resample
    if not (1.2 <= i2 <= 1.8):
        raise Resample

    lo_f, hi_f = PARAM_SPEC["face_width"]["range"][difficulty]
    p["face_width"] = round(min(max(p["face_width"], max(4.0 * m, lo_f)),
                                min(13.0 * m, hi_f)), 2)

    for k in ("z_ring1", "z_ring2"):
        lo, hi = PARAM_SPEC[k]["range"][difficulty]
        if not (lo <= p[k] <= hi):
            raise Resample


def check(p):
    bad = []
    zs = int(p["z_sun"])
    zp1, zp2 = int(p["z_planet1"]), int(p["z_planet2"])
    zr1, zr2 = int(p["z_ring1"]), int(p["z_ring2"])
    n1, n2 = int(p["n_planets1"]), int(p["n_planets2"])
    m = p["module"]

    for tag, zs_, zp, zr in (("1", zs, zp1, zr1), ("2", zs, zp2, zr2)):
        if zr != zs_ + 2 * zp:
            bad.append("z_ring%s != z_sun + 2*z_planet%s: stage %s is not coaxial "
                       "and cannot be assembled" % (tag, tag, tag))

    for tag, zr, zp, n in (("1", zr1, zp1, n1), ("2", zr2, zp2, n2)):
        if (zs + zr) % n:
            bad.append("(z_sun + z_ring%s) mod n_planets%s != 0: stage %s planets "
                       "cannot sit at equal angular pitch and still mesh "
                       "(assembly condition)" % (tag, tag, tag))
        if (zs + zp) * math.sin(math.pi / n) <= zp + 2:
            bad.append("(z_sun+z_planet%s)*sin(pi/n_planets%s) <= z_planet%s+2: "
                       "adjacent stage-%s planet tips foul each other "
                       "(neighbouring condition)" % (tag, tag, tag, tag))

    for name, z in (("z_sun", zs), ("z_planet1", zp1), ("z_planet2", zp2)):
        if z < 10:
            bad.append("%s = %d: a 20 deg full-depth involute undercuts badly "
                       "below 10 teeth (DIN 867, no profile shift declared)"
                       % (name, z))

    _, _, i1, i2, irev = _ratios(zs, zp1, zp2)
    if not (2.0 <= i1 <= 3.2):
        bad.append("1st gear (z_r1+z_r2+z_sun)/z_r1 = %.3f outside 2.0-3.2: a "
                   "Simpson set exists to give a usable ladder" % i1)
    if not (1.2 <= i2 <= 1.8):
        bad.append("2nd gear 1 + z_sun/z_r1 = %.3f outside 1.2-1.8" % i2)
    if i2 >= i1:
        bad.append("2nd gear %.3f is not below 1st %.3f: the ladder is not "
                   "monotonic and the set would not shift" % (i2, i1))

    if not 3.0 * m <= p["face_width"] <= 16.0 * m:
        bad.append("face_width %.2f outside 3-16x module (%.2f-%.2f)"
                   % (p["face_width"], 3.0 * m, 16.0 * m))

    return bad
