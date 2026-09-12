"""Sampling contract for two AmesburyTruth 17 Series window cam-lock rows."""

import math


PRODUCT_ROWS = {
    23: {
        "body_length": 65.9,
        "body_width": 28.6,
        "end_pad_h": 12.7,
        "body_h": 12.7,
        "deck_h": 13.5,
        "overall_h": 23.1,
        "hole_spacing": 52.4,
        "hole_d": 4.3,
        "hole_edge_offset": 11.1,
        "has_alignment_lugs": 0,
    },
    32: {
        "body_length": 65.9,
        "body_width": 26.2,
        "end_pad_h": 6.4,
        "body_h": 11.3,
        "deck_h": 12.5,
        "overall_h": 20.1,
        "hole_spacing": 52.4,
        "hole_d": 4.3,
        "hole_edge_offset": 11.1,
        "has_alignment_lugs": 1,
    },
}

ROW_KEYS = (
    "body_length",
    "body_width",
    "end_pad_h",
    "body_h",
    "deck_h",
    "overall_h",
    "hole_spacing",
    "hole_d",
    "hole_edge_offset",
    "has_alignment_lugs",
)

DIFFICULTY_ROWS = {
    "easy": [23],
    "medium": [23, 32],
    "hard": [32],
}


def _row_range(name):
    return {
        difficulty: (
            min(PRODUCT_ROWS[row][name] for row in rows),
            max(PRODUCT_ROWS[row][name] for row in rows),
        )
        for difficulty, rows in DIFFICULTY_ROWS.items()
    }


PARAM_SPEC = {
    "product_row": dict(
        desc="AmesburyTruth product row: 23=17.23.XX.200 EntryGard, 32=17.32.XX.200 Trimline",
        unit="",
        range={"easy": (23, 23), "medium": (23, 32), "hard": (32, 32)},
        choices=DIFFICULTY_ROWS,
        coverage=[23, 32],
        integer=True,
        feature=True,
        source="AmesburyTruth drawings 17.23.XX.200 and 17.32.XX.200; complete selected row",
        askable=True,
    ),
    "body_length": dict(
        desc="Official overall body length",
        unit="mm",
        range=_row_range("body_length"),
        refine=True,
        source="AmesburyTruth selected product-row drawing",
        askable=True,
    ),
    "body_width": dict(
        desc="Official overall body width",
        unit="mm",
        range=_row_range("body_width"),
        refine=True,
        source="AmesburyTruth selected product-row drawing",
        askable=True,
    ),
    "end_pad_h": dict(
        desc="Official height of the end mounting pad or foot",
        unit="mm",
        range=_row_range("end_pad_h"),
        refine=True,
        source="AmesburyTruth selected product-row drawing; 17.32 callout is 2X 6.4 mm",
        askable=True,
    ),
    "body_h": dict(
        desc="Official lower central-body height",
        unit="mm",
        range=_row_range("body_h"),
        refine=True,
        source="AmesburyTruth selected product-row drawing",
        askable=True,
    ),
    "deck_h": dict(
        desc="Official middle-deck top height",
        unit="mm",
        range=_row_range("deck_h"),
        refine=True,
        source="AmesburyTruth selected product-row drawing",
        askable=True,
    ),
    "overall_h": dict(
        desc="Official overall height through the pivot boss",
        unit="mm",
        range=_row_range("overall_h"),
        refine=True,
        source="AmesburyTruth selected product-row drawing",
        askable=True,
    ),
    "hole_spacing": dict(
        desc="Official center-to-center spacing of the two mounting holes",
        unit="mm",
        range=_row_range("hole_spacing"),
        refine=True,
        source="AmesburyTruth selected product-row drawing",
        askable=True,
    ),
    "hole_d": dict(
        desc="Official diameter of each mounting-hole through bore",
        unit="mm",
        range=_row_range("hole_d"),
        refine=True,
        source="AmesburyTruth selected product-row drawing",
        askable=True,
    ),
    "hole_edge_offset": dict(
        desc="Official mounting-hole center offset from the nearer long edge",
        unit="mm",
        range=_row_range("hole_edge_offset"),
        refine=True,
        source="AmesburyTruth selected product-row drawing",
        askable=True,
    ),
    "has_alignment_lugs": dict(
        desc="Selected row includes alignment lugs: 17.23=without, 17.32=with",
        unit="",
        range=_row_range("has_alignment_lugs"),
        refine=True,
        integer=True,
        feature=True,
        source="Truth SW07 table and AmesburyTruth 17.32 product resource name 'With LG'",
    ),
    "hole_csk_d": dict(
        desc="Modeled major diameter of each mounting-hole countersink",
        unit="mm",
        range={"easy": (8.0, 8.0), "medium": (8.0, 8.0), "hard": (8.0, 8.0)},
        choices=[8.0],
        source="proportion; deliberate approximation around the recommended #7 flat-head screw",
        askable=True,
    ),
    "hole_csk_angle": dict(
        desc="Included angle of the modeled inch-series flat-head countersink",
        unit="deg",
        range={"easy": (82.0, 82.0), "medium": (82.0, 82.0), "hard": (82.0, 82.0)},
        choices=[82.0],
        source="ASME inch flat-head convention used with the Truth #7 screw recommendation; not drawing-dimensioned",
        askable=True,
    ),
    "housing_length": dict(
        desc="Modeled length of the hollow central cam housing",
        unit="mm",
        range={"easy": (37.0, 37.0), "medium": (36.0, 38.0), "hard": (35.0, 39.0)},
        source="proportion from AmesburyTruth product image",
        askable=True,
    ),
    "cavity_h": dict(
        desc="Modeled height of the shallow underside cavity and its single open long side",
        unit="mm",
        range={"easy": (4.4, 4.4), "medium": (4.0, 4.8), "hard": (3.8, 5.2)},
        source="proportion from AmesburyTruth 17.32 side view; deliberately shallower than the 6.4 mm end feet",
        askable=True,
    ),
    "closed_wall_t": dict(
        desc="Modeled wall thickness at both short ends and the one closed long side",
        unit="mm",
        range={"easy": (2.4, 2.4), "medium": (2.2, 2.8), "hard": (2.0, 3.0)},
        source="proportion from AmesburyTruth isometric view: one long side open, opposite long side closed",
        askable=True,
    ),
    "lever_length": dict(
        desc="Modeled lever length from pivot to free end",
        unit="mm",
        range={"easy": (31.5, 31.5), "medium": (30.0, 33.0), "hard": (29.0, 34.0)},
        source="proportion from AmesburyTruth product image",
        askable=True,
    ),
    "lever_width": dict(
        desc="Modeled operating-lever neck width",
        unit="mm",
        range={"easy": (8.0, 8.0), "medium": (7.5, 8.8), "hard": (7.0, 9.2)},
        source="proportion from AmesburyTruth product image",
        askable=True,
    ),
    "lever_tip_width": dict(
        desc="Modeled widened operating-lever width at the free end",
        unit="mm",
        range={"easy": (11.5, 11.5), "medium": (10.8, 12.2), "hard": (10.4, 12.8)},
        source="proportion from AmesburyTruth product image",
        askable=True,
    ),
    "lever_t": dict(
        desc="Modeled maximum lever thickness at its two end steps",
        unit="mm",
        range={"easy": (3.2, 3.2), "medium": (3.0, 3.5), "hard": (2.8, 3.6)},
        source="proportion from AmesburyTruth product image",
        askable=True,
    ),
    "lever_angle": dict(
        desc="Displayed lever rotation about the cam pivot",
        unit="deg",
        range={"easy": (0, 0), "medium": (0, 90), "hard": (0, 90)},
        choices={"easy": [0], "medium": [0, 45, 90], "hard": [0, 30, 60, 90]},
        source="operational rotation accepted for this benchmark; modeled display range is 0 to 90 degrees",
    ),
}


def refine(p, difficulty, rng):
    row = PRODUCT_ROWS.get(int(p["product_row"]))
    if row is None:
        return
    for key in ROW_KEYS:
        p[key] = row[key]


def _row_consistency_errors(p):
    row = PRODUCT_ROWS.get(int(p["product_row"]))
    if row is None:
        return ["product_row must select 17.23 or 17.32"]
    bad = []
    for key in ROW_KEYS:
        if key in p and abs(float(p[key]) - float(row[key])) > 1e-9:
            bad.append(f"{key} must match complete AmesburyTruth row 17.{int(p['product_row']):02d}")
    return bad


def check(p: dict) -> list[str]:
    bad = _row_consistency_errors(p)
    end_center_margin = (p["body_length"] - p["hole_spacing"]) / 2.0
    csk_r = p["hole_csk_d"] / 2.0
    near_long_margin = p["hole_edge_offset"] - csk_r
    far_long_margin = p["body_width"] - p["hole_edge_offset"] - csk_r
    csk_depth = (p["hole_csk_d"] - p["hole_d"]) / (
        2.0 * math.tan(math.radians(p["hole_csk_angle"] / 2.0))
    )
    housing_to_csk = p["hole_spacing"] / 2.0 - csk_r - p["housing_length"] / 2.0
    boss_r = 0.24 * p["body_width"]
    cavity_length = p["housing_length"] - 2.0 * p["closed_wall_t"]
    roof_above_cavity = p["deck_h"] - p["cavity_h"]
    lever_mid_t = 0.48 * p["lever_t"]
    lever_tip_bottom = p["overall_h"] - p["lever_t"]

    if p["hole_csk_d"] <= p["hole_d"]:
        bad.append("countersink major diameter must exceed the official 4.3 mm through bore")
    if abs(p["hole_csk_angle"] - 82.0) > 1e-9:
        bad.append("modeled countersink must use one consistent 82 degree included angle")
    if end_center_margin - csk_r < 2.5:
        bad.append("countersink must retain at least 2.5 mm material to each body end")
    if near_long_margin < 2.5 or far_long_margin < 2.5:
        bad.append("countersink must retain at least 2.5 mm material to both long edges")
    if csk_depth >= p["end_pad_h"] - 1.5:
        bad.append("countersink depth must leave at least 1.5 mm mounting-pad floor")
    if housing_to_csk < 0.75:
        bad.append("central housing must clear each countersink envelope by at least 0.75 mm")
    if cavity_length <= 0.45 * p["housing_length"]:
        bad.append("closed short-end walls must leave a non-degenerate central opening")
    if p["closed_wall_t"] < 1.8 or p["closed_wall_t"] > 0.12 * p["housing_length"]:
        bad.append("closed short/long-side wall thickness must remain a plausible die-cast proportion")
    if p["cavity_h"] >= p["end_pad_h"] - 1.0:
        bad.append("underside cavity must stop at least 1.0 mm below the end-foot top")
    if roof_above_cavity < 6.5:
        bad.append("shallow cavity must retain at least 6.5 mm to the official deck top")
    if p["deck_h"] <= p["body_h"]:
        bad.append("middle deck must stand above the lower central body per selected drawing")
    if p["overall_h"] <= p["deck_h"]:
        bad.append("pivot boss top must stand above the middle deck per selected drawing")
    if p["lever_tip_width"] <= p["lever_width"]:
        bad.append("lever free end must be wider than its neck per product image")
    if p["lever_tip_width"] >= 0.55 * p["body_width"]:
        bad.append("lever free end must remain within the modeled housing-width envelope")
    if p["lever_length"] >= 0.56 * p["body_length"]:
        bad.append("lever length must remain below the documented body-length proportion")
    if lever_mid_t >= p["lever_t"]:
        bad.append("lever middle must be thinner than its two abrupt end steps")
    if lever_tip_bottom <= p["deck_h"] + 0.75:
        bad.append("downward free-end step must clear the middle deck by at least 0.75 mm")
    if boss_r <= p["lever_width"] / 2.0 + 1.0:
        bad.append("pivot boss must retain material around the lever root")
    if p["lever_angle"] < 0.0 or p["lever_angle"] > 90.0:
        bad.append("displayed lever rotation must remain within the modeled 0 to 90 degree travel")
    return bad
