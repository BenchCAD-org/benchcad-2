"""snatch_block_single_sheave — benchmark generator.

Two independent catalogue ladders drive one part: the sheave is sized by the
wire rope it carries, the fitting by the working load limit. The catalogue rows
pair them, so a row is drawn as a unit (`catalog_index`) and every published
dimension is filled from it in `refine()`; only the rope diameter inside the
row's range, the bearing option and the operating angle are drawn freely.

Source for every row: Crosby *Blocks* catalogue p.326, metric table —
https://kitocrosby.com/wp-content/uploads/2025/07/15_Blocks_MET_326.pdf
"""

import math

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
    "bar_deep_F": {
        "desc": "shackle bar depth through the crown, symbol F — the bow's other "
                "axis, and the one the overall height A closes on",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (32.0, 32.0), "medium": (13.0, 32.0), "hard": (13.0, 32.0)},
        "source": "catalogue dimension F",
    },
    "bow_width_G": {
        "desc": "shackle bow inside width, symbol G",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (76.0, 76.0), "medium": (34.0, 76.0), "hard": (34.0, 76.0)},
        "source": "catalogue dimension G",
    },
    "bow_height_H": {
        "desc": "shackle throat: clear opening under the bolt down to the inside of "
                "the bow crown, symbol H — same lower datum as D",
        "unit": "mm",
        "refine": True,
        "range": {"easy": (88.0, 88.0), "medium": (40.0, 88.0), "hard": (40.0, 88.0)},
        "source": "catalogue dimension H",
    },
    "swivel_angle": {
        "desc": "rotation of the shackle fitting about the block axis in the swivel; "
                "0 puts the bow in the plane of the side plates",
        "unit": "deg",
        "range": {"easy": (0.0, 0.0), "medium": (0.0, 90.0), "hard": (0.0, 180.0)},
        "source": "operating state; the fitting swivels freely (Crosby: forged steel "
                  "swivel tees and yokes, fitting-to-case clearance .031-.062 in) and "
                  "the catalogue photographs show it at every angle (proportion)",
    },
    "roller_count": {
        "desc": "bodies in the bearing: 1 bronze bushing, or the number of straight "
                "rollers in a full complement round the centre pin",
        "unit": "",
        "integer": True,
        "refine": True,
        "range": {"easy": (1, 40), "medium": (1, 40), "hard": (1, 40)},
        "source": "not published; a full complement is as many rollers as fit round "
                  "the pin at 0.6 mm apart, so this follows from the pin and race "
                  "(proportion) — the manual only says the roller option is a "
                  "straight, unsealed roller bearing",
    },
    "roller_bearing": {
        "desc": "0 = bronze bushing (catalogue code BB), 1 = roller bearing (code RB)",
        "unit": "",
        "integer": True,
        "feature": True,
        "range": {"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        "choices": {"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        "source": "catalogue column 'Bearing Code'; the manual (p.9, p.12) calls the "
                  "option a straight, unsealed roller bearing, so it is modelled as a "
                  "full complement of rollers running on the pin instead of a bronze "
                  "sleeve — the roller size and count are proportion",
    },
}

_ROW_KEYS = ("sheave_d", "head_w_B", "cheek_w_C", "pin_to_throat_D",
             "bar_thk_E", "bar_deep_F", "bow_width_G", "bow_height_H", "rope_d")

# Mirrored from part.py so check() constrains what build() actually draws.
_PLATE_SPAN = 0.549
_PLATE_T = 0.065
_SIDE_CLR = 2.0
_GROOVE_DEPTH_FACTOR = 1.5
_GROOVE_R_FACTOR = 0.53
_FLANK_ANGLE = 12.0
_BOLT_TO_CHEEK = 0.26
_BOSS_TO_BOLT = 0.95
_EYE_TO_BOLT = 1.05
_CASE_FOOT = 1.15
_NECK = 0.35
_PLATE_REACH = 0.36
_SHEAVE_GAP = 4.0
_BOLT_TO_BAR = 1.13
_TEE_TO_BOLT = 0.95
_EAR_SPAN = 0.73
_EAR_W = 1.4
_HEAD_R = 1.35
# ISO 261 first-choice coarse sizes with their ISO 272 / 4014 / 4032 hardware:
# nominal -> (across flats s, head height k, nut height m).  Mirrored from
# part.py so check() constrains the fasteners build() actually draws.
_ISO_HEX = {
    12: (18.0, 7.5, 10.8), 16: (24.0, 10.0, 14.8), 20: (30.0, 12.5, 18.0),
    24: (36.0, 15.0, 21.5), 30: (46.0, 18.7, 25.6), 36: (55.0, 22.5, 31.0),
    42: (65.0, 26.0, 34.0), 48: (75.0, 30.0, 38.0),
}


def _iso_size(target):
    fits = [d for d in sorted(_ISO_HEX) if d <= target]
    return fits[-1] if fits else min(_ISO_HEX)


def _iso_fits_width(plate_span, overall):
    fits = [d for d in sorted(_ISO_HEX)
            if plate_span + _ISO_HEX[d][1] + _ISO_HEX[d][2] <= overall]
    return fits[-1] if fits else min(_ISO_HEX)
_RACE_BB = 0.12
_ROLLER = 0.22
_ROLL_GAP = 0.6
_ISO_SPLIT = (2.0, 2.5, 3.2, 4.0, 5.0, 6.3, 8.0, 10.0, 13.0, 16.0, 20.0)
_FIT = 0.5


def _bearing(p):
    """Pin, race depth and roller pitch circle -- mirrored from part.py."""
    pin_d = float(_iso_fits_width(_PLATE_SPAN * p["cheek_w_C"], p["cheek_w_C"]))
    race_t = max(2.0, (_ROLLER if p["roller_bearing"] else _RACE_BB) * pin_d)
    return pin_d, race_t, 0.5 * pin_d + _FIT + 0.5 * race_t


def _stack(p):
    """The fitting stack part.py builds, so check() can constrain it.

    Returns (hook bolt axis, shackle bolt axis, case foot centre) as z below the
    centre pin, all negative.
    """
    bolt_d = float(_iso_size(_BOLT_TO_CHEEK * p["cheek_w_C"]))
    tail_r = _BOSS_TO_BOLT * bolt_d
    eye_r = _EYE_TO_BOLT * bolt_d
    z_bolt = -max(_PLATE_REACH * p["pin_to_throat_D"],
                  0.5 * p["sheave_d"] + max(tail_r, eye_r) + _SHEAVE_GAP)
    sb_r = 0.5 * float(_iso_size(_BOLT_TO_BAR * p["bar_thk_E"]))
    z_sb = -p["pin_to_throat_D"] + p["bow_height_H"] + sb_r
    tee_r = _TEE_TO_BOLT * 2.0 * sb_r
    z_foot = z_sb + tee_r + _NECK * bolt_d + _CASE_FOOT * bolt_d
    return z_bolt, z_sb, z_foot


def refine(p, difficulty, rng):
    row = CATALOG[int(p["catalog_index"])]
    _wll, rope_lo, rope_hi, sheave_d, _a, b, c, d, e, _f, g, h = row
    p["sheave_d"] = float(sheave_d)
    p["head_w_B"] = float(b)
    p["cheek_w_C"] = float(c)
    p["pin_to_throat_D"] = float(d)
    p["bar_thk_E"] = float(e)
    p["bar_deep_F"] = float(_f)
    p["bow_width_G"] = float(g)
    p["bow_height_H"] = float(h)
    # The row gives the rope range the groove may be cut for; pick inside it.
    p["rope_d"] = round(float(rng.uniform(rope_lo, rope_hi)), 1)
    # A bronze bushing is one body; a roller bearing is as many rollers as fit
    # round the pin.  Either way it is the same component, so the body count
    # follows this number and family.json declares no fixed `solids`.
    if p["roller_bearing"]:
        _pin_d, race_t, pitch_r = _bearing(p)
        p["roller_count"] = int(2.0 * math.pi * pitch_r // (race_t + _ROLL_GAP))
    else:
        p["roller_count"] = 1
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
    a_model = p["head_w_B"] / 2.0 + p["pin_to_throat_D"] + p["bar_deep_F"]
    if abs(a_model - row[4]) > 1.5:
        bad.append("B/2 + D + F = %.1f but the catalogue prints A = %d — the height "
                   "stack closes on F, the bow's depth through the crown, not on E "
                   "(Crosby p.326: exact on 9 of 13 rows, the rest B/2 rounding)"
                   % (a_model, row[4]))

    # The plate crown tracks the sheave, but not by covering it: on the 4 t row
    # (sheave 114, B 108) the sheave rim stands proud of the plate, and on the
    # 5 t row (sheave 102, B 114) the plate overhangs. Across all 13 rows the
    # ratio stays inside a narrow band, which is the real constraint.
    ratio = p["head_w_B"] / p["sheave_d"]
    if not 0.94 <= ratio <= 1.13:
        bad.append("head_w_B / sheave_d = %.3f is outside the 0.94-1.13 band the "
                   "catalogue holds on all 13 rows (Crosby p.326)" % ratio)

    # The bow needs straight leg between the pin and the crown.
    if p["bow_height_H"] <= p["bow_width_G"] / 2.0 + p["bar_deep_F"]:
        bad.append("bow_height_H <= G/2 + E: no straight leg left between the shackle "
                   "pin and the bow crown (anchor shackle proportion)")

    # Metal has to remain under the groove, over the bore.  The bore is set by
    # the centre pin, which is a load-sized part and so scales with C.
    pin_d = float(_iso_fits_width(_PLATE_SPAN * p["cheek_w_C"], p["cheek_w_C"]))
    bore_d = pin_d + 2.0 * max(2.0, _RACE_BB * pin_d)
    tread_d = p["sheave_d"] - 2.0 * _GROOVE_DEPTH_FACTOR * p["rope_d"]
    if tread_d <= bore_d + 12.0:
        bad.append("groove bottom reaches the bore: tread diameter %.1f leaves no rim "
                   "over a %.1f bore (sheave practice, groove depth 1.5 d)"
                   % (tread_d, bore_d))

    # Two plates plus running clearance have to fit inside C, leaving a sheave
    # wide enough to hold the groove.
    sheave_w = p["cheek_w_C"] * (_PLATE_SPAN - 2.0 * _PLATE_T) - 2.0 * _SIDE_CLR
    if sheave_w <= 1.7 * p["rope_d"]:
        bad.append("sheave width %.1f is under 1.7 rope diameters: the groove will not "
                   "fit inside the plate span C sets (sheave practice)" % sheave_w)
    # and the groove itself has to leave a flange: solve the flared flank the way
    # part.py draws it and require real rim on both sides.  This is the check the
    # C correction actually needed -- at the old 20 deg flare the 22 mm rope
    # opened the groove across the whole 40.4 mm face.
    gr = _GROOVE_R_FACTOR * p["rope_d"]
    tread_r = 0.5 * p["sheave_d"] - _GROOVE_DEPTH_FACTOR * p["rope_d"]
    arc_end_r = tread_r + gr - gr * math.cos(math.radians(60.0))
    lip = (gr * math.sin(math.radians(60.0))
           + math.tan(math.radians(_FLANK_ANGLE)) * (0.5 * p["sheave_d"] - arc_end_r))
    if sheave_w - 2.0 * lip < 2.0:
        bad.append("the groove opens to %.1f mm across a %.1f mm face: under 1 mm of "
                   "flange each side, the rope would not stay in (sheave practice)"
                   % (2.0 * lip, sheave_w))

    # ---- the fitting stack has to close -------------------------------------
    # These three are what an assembly family owes the reader: every joint in
    # the load path (bow -> shackle bolt -> tee -> swivel -> case -> hook bolt
    # -> plates) has to have room to exist, or the fitting is not attached to
    # the block at all.
    bolt_d = float(_iso_size(_BOLT_TO_CHEEK * p["cheek_w_C"]))
    z_bolt, z_sb, z_foot = _stack(p)

    # 1. the swivel case has to be long enough to hold the bolt eye above the
    #    counterbore its stem head stands in.
    case_len = z_bolt - z_foot
    if case_len < 0.725 * bolt_d + 4.0:
        bad.append("swivel case is %.1f mm between the hook bolt and its foot, under "
                   "the %.1f mm the bolt eye plus the swivel counterbore need "
                   "(fitting proportion, NOTES.md)"
                   % (case_len, 0.725 * bolt_d + 4.0))

    # 2. the hook bolt and the case eye run beside the sheave, so the tail of
    #    the plate has to clear the rim.  On the big-sheave rows this is what
    #    pushes the whole fitting down, not D.
    clear = -z_bolt - 0.5 * p["sheave_d"] - _EYE_TO_BOLT * bolt_d
    if clear < _SHEAVE_GAP - 1e-6:
        bad.append("hook bolt sits %.1f mm from the sheave rim, under the %.1f mm the "
                   "case eye needs to clear it (fitting proportion, NOTES.md)"
                   % (clear, _SHEAVE_GAP))

    # 3. the tee barrel hangs inside the shackle throat, between the ears.
    sb_d = float(_iso_size(_BOLT_TO_BAR * p["bar_thk_E"]))
    sb_r = 0.5 * sb_d
    tee_r = _TEE_TO_BOLT * 2.0 * sb_r
    if z_sb - tee_r <= -p["pin_to_throat_D"] + p["bar_deep_F"]:
        bad.append("swivel tee barrel r=%.1f reaches the shackle crown: the throat is "
                   "only H = %.0f mm deep under the bolt (anchor shackle proportion)"
                   % (tee_r, p["bow_height_H"]))

    # 4. a full complement has to fit: the rollers must not touch each other.
    if p["roller_bearing"]:
        _pin_d, race_t, pitch_r = _bearing(p)
        n = int(p["roller_count"])
        chord = 2.0 * pitch_r * math.sin(math.pi / max(2, n))
        if chord < race_t + 0.2:
            bad.append("%d rollers of %.1f mm on a %.1f mm pitch circle leave only "
                       "%.2f mm centre to centre: a full complement of that many does "
                       "not fit round the pin (proportion, NOTES.md)"
                       % (n, race_t, 2.0 * pitch_r, chord))

    # 5. the bow's legs are the crown circle's tangents, so the ears have to
    #    stand outside that circle or there is no pear shape to draw.
    bar_r = 0.5 * p["bar_deep_F"]
    major_r = 0.5 * p["bow_width_G"] + bar_r
    ear_w = _EAR_W * p["bar_thk_E"]
    ear_x = 0.5 * _EAR_SPAN * p["bow_width_G"] + 0.5 * ear_w
    reach = p["bow_height_H"] + sb_r - 0.5 * p["bow_width_G"]
    span = math.hypot(ear_x, reach)
    if span <= major_r * 1.02:
        bad.append("the shackle ears at x=%.1f sit inside the bow crown circle "
                   "R=%.1f: no tangent leg exists (anchor shackle proportion)"
                   % (ear_x, major_r))
    else:
        # 6. the bolt head bears on the ear's outer face, and the bow's leg
        #    flares outboard below it.  The head has to clear that leg or the
        #    shackle cannot be assembled -- caught by probe on the first draft.
        phi = math.atan2(reach, ear_x) - math.acos(major_r / span)
        t_x, t_z = major_r * math.cos(phi), -reach + major_r * math.sin(phi)
        head_r = _ISO_HEX[int(sb_d)][0] / math.sqrt(3.0)   # hex circumradius
        lean = (t_x - ear_x) / max(1e-6, -t_z)
        leg_out = ear_x + lean * head_r + bar_r * math.hypot(1.0, lean)
        if leg_out > ear_x + 0.5 * ear_w - 0.5:
            bad.append("the bow leg reaches x=%.1f at the rim of a %.1f mm bolt head "
                       "but the ear face is only at x=%.1f: the head would foul the "
                       "leg (anchor shackle proportion, NOTES.md)"
                       % (leg_out, 2.0 * head_r, ear_x + 0.5 * ear_w))

    # 7. every pin is snapped DOWN to an ISO size, so a row whose load-derived
    #    diameter lands just above a step would otherwise get a pin much smaller
    #    than the load asks for.  Reject anything that loses more than a fifth.
    span = _PLATE_SPAN * p["cheek_w_C"]
    _s, k, m = _ISO_HEX[int(pin_d)]
    across = span + k + m + 0.10 * pin_d          # head face to thread end
    if across > p["cheek_w_C"] + 1e-6:
        bad.append("plate span %.1f + head %.1f + nut %.1f + thread = %.1f exceeds the "
                   "printed C = %.0f: C is the OVERALL width, measured over the centre "
                   "pin's head and nut (Crosby p.326 side view)"
                   % (span, k, m, across, p["cheek_w_C"]))
    for label, target, chosen in (
            ("hook bolt", _BOLT_TO_CHEEK * p["cheek_w_C"], bolt_d),
            ("shackle bolt", _BOLT_TO_BAR * p["bar_thk_E"], sb_d)):
        if chosen < 0.80 * target:
            bad.append("%s: the load-derived %.1f mm snaps down to M%d, losing %.0f%% "
                       "of the section (ISO 261 first-choice ladder, NOTES.md)"
                       % (label, target, int(chosen), 100.0 * (1.0 - chosen / target)))

    # 8. no dead thread: the shackle bolt ends just past the split pin that locks
    #    its nut.  A long tail is not merely ugly -- it throws the whole fitting
    #    off-centre against the bow, which is how this was caught.
    cot_nom = 0.0
    for nom in _ISO_SPLIT:
        if nom <= 0.20 * sb_d:
            cot_nom = nom
    ear_w2 = _EAR_W * p["bar_thk_E"]
    x_nut2 = 0.5 * _EAR_SPAN * p["bow_width_G"] + ear_w2
    nut_face = x_nut2 + _ISO_HEX[int(sb_d)][2]
    bolt_end = x_nut2 + _ISO_HEX[int(sb_d)][2] + 1.03 * cot_nom + 1.5 + 1.1 * cot_nom
    if bolt_end - nut_face > 2.2 * cot_nom + 2.0:
        bad.append("the shackle bolt runs %.1f mm past its nut face for a %.1f mm "
                   "split pin: that is dead thread, and it throws the fitting "
                   "off-centre against the bow (shackle practice): the pin needs "
                   "%.1f mm to clear the nut and %.1f mm of bolt behind it"
                   % (bolt_end - nut_face, cot_nom, 1.03 * cot_nom + 1.5,
                      1.1 * cot_nom))

    return bad
