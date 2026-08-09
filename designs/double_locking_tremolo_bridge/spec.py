"""double_locking_tremolo_bridge — benchmark generator.

The family varies on two axes and holds the hardware interface fixed. String
count drives the whole plan — span, post spacing and saddle radius all follow
it — so `n_strings` selects a published size and `refine()` fills them from it.
Sustain-block height is an independent three-value catalogue ladder. Plate
thickness, post, insert bushing and saddle block are shared across the product
line and are declared as the single values the sheets print.

Sources: Gotoh dimension sheets
https://g-gotoh.com/images/pdf/GE1996T-Dim.pdf (6-string) and
https://g-gotoh.com/images/pdf/GE1996T-7-Dim.pdf (7-string); product page
https://g-gotoh.com/product/ge1996t/?lang=en for finishes, block heights,
string spacing and saddle radius.
"""

import math

from bench2 import Resample

# n_strings -> (plate span, plate depth, post spacing, saddle radius), mm.
# Both rows are read off the dimension sheets. The 7-string sheet prints its
# string span as 64.8 = 10.8 x 6, which is what pins the pitch as shared.
SIZES = {
    6: (91.5, 36.0, 74.0, 350.0),
    7: (102.3, 39.0, 84.8, 430.0),
}

PARAM_SPEC = {
    "n_strings": {
        "desc": "number of strings; selects the published size",
        "unit": "",
        "integer": True,
        "range": {"easy": (6, 6), "medium": (6, 7), "hard": (6, 7)},
        "choices": {"easy": [6], "medium": [6, 7], "hard": [6, 7]},
        "coverage": [6, 7],
        "source": "GE1996T and GE1996T-7 dimension sheets",
    },
    "string_pitch": {
        "desc": "string spacing at the saddles",
        "unit": "mm",
        "range": {"easy": (10.8, 10.8), "medium": (10.8, 10.8), "hard": (10.8, 10.8)},
        "source": "both sheets and the product page state 10.8 mm; the 7-string "
                  "sheet prints the span as 64.8 = 10.8 x 6",
    },
    "plate_span": {
        "desc": "base plate overall span across the strings",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (91.5, 91.5), "medium": (91.5, 102.3), "hard": (91.5, 102.3)},
        "source": "sheet dimension 91.5 (6-string) / 102.3 (7-string)",
    },
    "plate_depth": {
        "desc": "base plate depth along the strings",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (36.0, 36.0), "medium": (36.0, 39.0), "hard": (36.0, 39.0)},
        "source": "sheet dimension 36 / 39",
    },
    "post_spacing": {
        "desc": "centre distance between the two mounting posts",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (74.0, 74.0), "medium": (74.0, 84.8), "hard": (74.0, 84.8)},
        "source": "sheet dimension 74 / 84.8",
    },
    "saddle_radius": {
        "desc": "radius of the cylinder the saddle tops lie on",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (350.0, 350.0), "medium": (350.0, 430.0), "hard": (350.0, 430.0)},
        "source": "sheet (R350) / (R430); product page 'saddle radius'",
    },
    "plate_t": {
        "desc": "base plate thickness",
        "unit": "mm",
        "range": {"easy": (3.2, 3.2), "medium": (3.2, 3.2), "hard": (3.2, 3.2)},
        "source": "sheet dimension 3.2, identical on both sizes",
    },
    "string_h": {
        "desc": "string height above the plate face — the saddle top sits on "
                "the fingerboard-radius cylinder at this height",
        "unit": "mm",
        "range": {"easy": (8.6, 8.6), "medium": (8.6, 8.6), "hard": (8.6, 8.6)},
        # Measured off the elevation at 7.97 px/mm (scaled from the plate's own
        # 3.2): the 8.6 runs from the plate face to the R350 arc through the
        # saddle notches. An earlier revision read it as the knife-edge height
        # and named the parameter knife_h; the sheet does not dimension the
        # knife at all, so its depth is a proportion of this (_KNIFE_DROP).
        "source": "sheet dimension 8.6 (plate face to the R350 string arc), "
                  "identical on both sizes",
    },
    "block_height": {
        "desc": "sustain block height below the plate",
        "unit": "mm",
        "integer": True,
        "range": {"easy": (33, 40), "medium": (33, 40), "hard": (33, 40)},
        "choices": {"easy": [33, 36, 40], "medium": [33, 36, 40], "hard": [33, 36, 40]},
        "coverage": [33, 36, 40],
        "source": "catalogue block heights 33 / 36 / 40 mm, offered on both sizes",
    },
    "saddle_len": {
        "desc": "saddle block length along the strings",
        "unit": "mm",
        "range": {"easy": (32.3, 32.3), "medium": (32.3, 32.3), "hard": (32.3, 32.3)},
        "source": "sheet saddle detail view, 32.3",
    },
    "post_shaft_d": {
        "desc": "post thread diameter (M8) where it screws into the insert bushing",
        "unit": "mm",
        "range": {"easy": (8.0, 8.0), "medium": (8.0, 8.0), "hard": (8.0, 8.0)},
        "source": "sheet post detail view: M8, 30 long. The sheet's o5.5 callout "
                  "is in the SIDE view and belongs to the tremolo arm - the post "
                  "detail carries no o5.5, and a o5.5 blank cannot carry an M8 "
                  "thread",
    },
    "bushing_d": {
        "desc": "insert bushing outside diameter",
        "unit": "mm",
        "range": {"easy": (11.3, 11.3), "medium": (11.3, 11.3), "hard": (11.3, 11.3)},
        "source": "sheet bushing detail view, o11.3",
    },
    "bushing_len": {
        "desc": "insert bushing length",
        "unit": "mm",
        "range": {"easy": (30.0, 30.0), "medium": (30.0, 30.0), "hard": (30.0, 30.0)},
        "source": "sheet bushing detail view, 30",
    },
    "pivot_angle": {
        "desc": "rock of the plate about the knife edges; 0 is level, negative "
                "dives, positive pulls up",
        "unit": "deg",
        "range": {"easy": (0.0, 0.0), "medium": (-8.0, 4.0), "hard": (-14.0, 8.0)},
        "source": "operating state, not a dimension: the sheet draws the bridge "
                  "level and does not dimension the travel (proportion)",
    },
}

_ROW_KEYS = ("plate_span", "plate_depth", "post_spacing", "saddle_radius")

# Mirrored from part.py so check() constrains what build() actually draws.
_BLOCK_W = 0.55
_SADDLE_ROW = 0.50
_KNIFE_INSET = 0.14  # kept for reference; the saddle-row check no longer uses it


def refine(p, difficulty, rng):
    n = int(p["n_strings"])
    if n not in SIZES:
        raise Resample
    span, depth, posts, radius = SIZES[n]
    p["plate_span"] = span
    p["plate_depth"] = depth
    p["post_spacing"] = posts
    p["saddle_radius"] = radius
    for key in _ROW_KEYS:
        lo, hi = PARAM_SPEC[key]["range"][difficulty]
        if not (lo - 1e-6 <= p[key] <= hi + 1e-6):
            raise Resample


def check(p):
    bad = []
    n = int(p["n_strings"])
    string_span = p["string_pitch"] * (n - 1)

    # Strings inside the posts, posts inside the plate. Both sheets hold it:
    # 54 < 74 < 91.5 and 64.8 < 84.8 < 102.3.
    if not string_span < p["post_spacing"] < p["plate_span"]:
        bad.append("string span %.1f, post spacing %.1f and plate span %.1f are not "
                   "nested: the strings land inside the posts and the posts inside "
                   "the plate (both Gotoh sheets)"
                   % (string_span, p["post_spacing"], p["plate_span"]))

    # Saddle tops lie on the fingerboard-radius cylinder. If the outer saddles
    # drop past what the knife boss gives, the radius is too tight for the span.
    drop = p["saddle_radius"] - (p["saddle_radius"] ** 2 - (string_span / 2.0) ** 2) ** 0.5
    if drop >= p["string_h"]:
        bad.append("saddle radius %.0f drops the outer saddles %.2f mm over a %.1f mm "
                   "span, past the %.2f mm of string height there is: too tight a radius "
                   "for this string count (sheet R350 / R430)"
                   % (p["saddle_radius"], drop, string_span, p["string_h"]))

    # The tremolo arm collet lives outboard of the last saddle, in what the
    # plate leaves past it. Too little room and there is nowhere to put it.
    _lean = p["string_h"] * 1.35 * math.sin(math.radians(12.0))   # _ARM_TILT
    _room = (p["plate_span"] / 2.0
             - (string_span / 2.0 + p["string_pitch"] * 0.43 + 0.8) - _lean)
    if _room < 5.0:
        bad.append("only %.1f mm of plate outboard of the last saddle once the "
                   "arm collet's rake is counted: nowhere to put it (the sheet "
                   "leaves ~11 at 91.5 span / 54 string span)" % _room)

    # The knife ridges sit at the post centres and have to stay on the plate.
    if p["plate_span"] - p["post_spacing"] < 8.0:
        bad.append("posts at %.1f centres on a %.1f plate leave under 8 mm for "
                   "the knife ridges to bear on"
                   % (p["post_spacing"], p["plate_span"]))

    # The sustain block hangs in the body cavity between the posts.
    if _BLOCK_W * p["plate_span"] >= p["post_spacing"] - 2.0 * p["bushing_d"]:
        bad.append("sustain block %.1f wide fouls the insert bushings at %.1f centres: "
                   "it has to hang between the posts"
                   % (_BLOCK_W * p["plate_span"], p["post_spacing"]))

    # The saddle has to sit on the plate. It very nearly fills the depth —
    # 32.3 on a 36 mm plate — so it does cross the knife-edge line in plan, and
    # an earlier version of this check that forbade that rejected the whole
    # 6-string size. What is actually required is only that it fits.
    if p["saddle_len"] >= p["plate_depth"]:
        bad.append("saddle_len %.1f does not fit a %.1f mm deep plate: the saddle "
                   "would overhang both edges (sheet plan view)"
                   % (p["saddle_len"], p["plate_depth"]))

    # A plate as deep as its block would be a hardtail, not a tremolo.
    if p["plate_t"] >= p["block_height"] / 4.0:
        bad.append("plate_t %.1f is not plate-like against a %d mm sustain block "
                   "(sheet: 3.2 mm plate on a 33-40 mm block)"
                   % (p["plate_t"], int(p["block_height"])))

    return bad
