"""snatch_block_single_sheave — benchmark generator.

Two independent catalogue ladders drive one part: the sheave is sized by the
wire rope it carries, the fitting by the working load limit. The catalogue rows
pair them, so a row is drawn as a unit (`catalog_index`) and every published
dimension is filled from it in `refine()`; only the rope diameter inside the
row's range, the bearing option and the operating angle are drawn freely.

Source for every row: Crosby *Blocks* catalogue p.326, metric table —
https://kitocrosby.com/wp-content/uploads/2025/07/15_Blocks_MET_326.pdf
"""

from bench2 import Resample

# One entry per geometrically distinct catalogue row:
# (WLL t, rope lo, rope hi, sheave dia, A, B, C, D, E, F, G, H) — mm.
# Bronze-bushing and roller-bearing rows are identical in every dimension, so the
# bearing is a feature parameter rather than a row of its own. The 419 w/Eye row
# (stock 109037) is excluded: it carries a swivel eye instead of a shackle, which
# is a different fitting, not another size of this one.
CATALOG = (
    (2, 8, 10, 76, 235, 76, 67, 185, 13, 13, 34, 40),
    (4, 10, 13, 114, 340, 108, 79, 268, 16, 18, 43, 51),
    (5, 10, 13, 102, 353, 114, 75, 278, 16, 18, 43, 51),
    (6, 10, 13, 127, 351, 130, 94, 268, 16, 18, 43, 51),
    (8, 16, 19, 152, 481, 152, 106, 373, 32, 32, 76, 88),
    (8, 16, 19, 203, 533, 206, 106, 398, 32, 32, 76, 88),
    (8, 16, 19, 254, 586, 257, 106, 425, 32, 32, 76, 88),
    (8, 16, 19, 305, 657, 308, 106, 471, 32, 32, 76, 88),
    (8, 16, 19, 356, 695, 359, 106, 484, 32, 32, 76, 88),
    (12, 16, 19, 146, 483, 152, 106, 375, 32, 32, 76, 88),
    (12, 19, 22, 152, 481, 152, 106, 373, 32, 32, 76, 88),
    (12, 19, 22, 203, 533, 206, 106, 398, 32, 32, 76, 88),
    (12, 19, 22, 254, 586, 257, 106, 425, 32, 32, 76, 88),
)

_ALL = list(range(len(CATALOG)))
_MID = [0, 1, 2, 3, 4, 5, 6, 10, 11]

PARAM_SPEC = {
    "catalog_index": {
        "desc": "row of the Crosby p.326 size table this instance reproduces",
        "unit": "",
        "integer": True,
        "range": {"easy": (4, 6), "medium": (0, 11), "hard": (0, 12)},
        "choices": {"easy": [4, 5, 6], "medium": _MID, "hard": _ALL},
        "coverage": _ALL,
        "source": "Crosby Blocks catalogue p.326 metric table, 13 distinct rows",
    },
    "sheave_d": {
        "desc": "sheave outside diameter",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (152.0, 254.0), "medium": (76.0, 356.0), "hard": (76.0, 356.0)},
        "source": "catalogue column 'Sheave Diameter'",
    },
    "rope_d": {
        "desc": "nominal wire rope diameter the groove is cut for",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (16.0, 19.0), "medium": (8.0, 22.0), "hard": (8.0, 22.0)},
        "source": "catalogue column 'Wire Rope Diameter', which gives a range per row",
    },
    "head_w_B": {
        "desc": "side plate head width, symbol B — the plate crown diameter",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (152.0, 257.0), "medium": (76.0, 359.0), "hard": (76.0, 359.0)},
        "source": "catalogue dimension B",
    },
    "cheek_w_C": {
        "desc": "overall width across the cheeks, symbol C",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (106.0, 106.0), "medium": (67.0, 106.0), "hard": (67.0, 106.0)},
        "source": "catalogue dimension C",
    },
    "pin_to_throat_D": {
        "desc": "centre pin down to the bottom of the shackle throat, symbol D",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (373.0, 425.0), "medium": (185.0, 484.0), "hard": (185.0, 484.0)},
        "source": "catalogue dimension D",
    },
    "bar_thk_E": {
        "desc": "shackle bar / fitting thickness, symbol E",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (32.0, 32.0), "medium": (13.0, 32.0), "hard": (13.0, 32.0)},
        "source": "catalogue dimension E",
    },
    "bow_width_G": {
        "desc": "shackle bow inside width, symbol G",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (76.0, 76.0), "medium": (34.0, 76.0), "hard": (34.0, 76.0)},
        "source": "catalogue dimension G",
    },
    "bow_height_H": {
        "desc": "shackle bow height, pin axis to the outside of the crown, symbol H",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (88.0, 88.0), "medium": (40.0, 88.0), "hard": (40.0, 88.0)},
        "source": "catalogue dimension H",
    },
    "open_angle": {
        "desc": "swing of the opening side plate about the centre pin; 0 is closed",
        "unit": "deg",
        "range": {"easy": (0.0, 0.0), "medium": (0.0, 30.0), "hard": (0.0, 75.0)},
        "source": "operating state; the catalogue states the opening feature admits "
                  "rope without reeving but does not dimension the swing (proportion)",
    },
    "roller_bearing": {
        "desc": "0 = bronze bushing (catalogue code BB), 1 = roller bearing (code RB)",
        "unit": "",
        "integer": True,
        "feature": True,
        "range": {"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        "choices": {"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        "source": "catalogue column 'Bearing Code'; the roller option runs a thicker "
                  "race, modelled as a larger sheave bore (proportion)",
    },
}

_ROW_KEYS = ("sheave_d", "head_w_B", "cheek_w_C", "pin_to_throat_D",
             "bar_thk_E", "bow_width_G", "bow_height_H", "rope_d")

# Mirrored from part.py so check() constrains what build() actually draws.
_PLATE_T = 0.10
_SIDE_CLR = 2.0
_GROOVE_DEPTH_FACTOR = 1.5
_TANG_FRACTION = 0.55


def refine(p, difficulty, rng):
    row = CATALOG[int(p["catalog_index"])]
    _wll, rope_lo, rope_hi, sheave_d, _a, b, c, d, e, _f, g, h = row
    p["sheave_d"] = float(sheave_d)
    p["head_w_B"] = float(b)
    p["cheek_w_C"] = float(c)
    p["pin_to_throat_D"] = float(d)
    p["bar_thk_E"] = float(e)
    p["bow_width_G"] = float(g)
    p["bow_height_H"] = float(h)
    # The row gives the rope range the groove may be cut for; pick inside it.
    p["rope_d"] = round(float(rng.uniform(rope_lo, rope_hi)), 1)
    for key in _ROW_KEYS:
        lo, hi = PARAM_SPEC[key]["range"][difficulty]
        if not (lo - 1e-6 <= p[key] <= hi + 1e-6):
            raise Resample


def check(p):
    bad = []
    row = CATALOG[int(p["catalog_index"])]

    # The catalogue is internally consistent: A = B/2 + D + E holds on every row,
    # so the published overall height is not a free number — it falls out of the
    # stack, and a row that violates it would be a transcription error.
    a_model = p["head_w_B"] / 2.0 + p["pin_to_throat_D"] + p["bar_thk_E"]
    if abs(a_model - row[4]) > 2.5:
        bad.append("B/2 + D + E = %.1f but the catalogue prints A = %d "
                   "(Crosby p.326 rows are consistent to 2 mm)" % (a_model, row[4]))

    # The plate crown tracks the sheave, but not by covering it: on the 4 t row
    # (sheave 114, B 108) the sheave rim stands proud of the plate, and on the
    # 5 t row (sheave 102, B 114) the plate overhangs. Across all 13 rows the
    # ratio stays inside a narrow band, which is the real constraint.
    ratio = p["head_w_B"] / p["sheave_d"]
    if not 0.94 <= ratio <= 1.13:
        bad.append("head_w_B / sheave_d = %.3f is outside the 0.94-1.13 band the "
                   "catalogue holds on all 13 rows (Crosby p.326)" % ratio)

    # The bow needs straight leg between the pin and the crown.
    if p["bow_height_H"] <= p["bow_width_G"] / 2.0 + p["bar_thk_E"]:
        bad.append("bow_height_H <= G/2 + E: no straight leg left between the shackle "
                   "pin and the bow crown (anchor shackle proportion)")

    # Metal has to remain under the groove, over the bore.
    tread_d = p["sheave_d"] - 2.0 * _GROOVE_DEPTH_FACTOR * p["rope_d"]
    if tread_d <= p["bar_thk_E"] + 12.0:
        bad.append("groove bottom reaches the bore: tread diameter %.1f leaves no rim "
                   "over a %.1f pin (sheave practice, groove depth 1.5 d)"
                   % (tread_d, p["bar_thk_E"]))

    # Two plates plus running clearance have to fit inside C, leaving a sheave
    # wide enough to hold the groove.
    sheave_w = p["cheek_w_C"] * (1.0 - 2.0 * _PLATE_T) - 2.0 * _SIDE_CLR
    if sheave_w <= 2.0 * p["rope_d"]:
        bad.append("sheave width %.1f is under two rope diameters: the groove will not "
                   "fit inside cheek width C (sheave practice)" % sheave_w)

    # The yoke tang drops between the shackle ears.
    if _TANG_FRACTION * p["bow_width_G"] >= p["bow_width_G"] - 2.0:
        bad.append("yoke tang does not clear the shackle bow opening G")

    return bad
