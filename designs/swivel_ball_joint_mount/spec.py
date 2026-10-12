"""Sampling contract for the JW Winco GN 784 swivel ball joint mount."""

from part import (
    _CATALOG_ROWS,
    _THREADS,
    _catalog_dimensions,
    _geometry_proportions,
    _valid_catalog_variants,
)


_ALL_ROWS = list(range(8))
_DIFFICULTY_ROWS = {
    # GN 784 Issue #60: d1 31/39, metric, Type A, identification 2.
    "easy": [2, 4],
    # Every printed row has at least one published metric A or B alternative.
    "medium": _ALL_ROWS,
    # All eight rows, with metric and inch alternatives.
    "hard": _ALL_ROWS,
}


PARAM_SPEC = {
    "catalog_row": dict(
        desc=(
            "complete GN 784 printed row: 0=23-M4/M5, 1=23-1/4, "
            "2=31-M5/M6, 3=31-M8, 4=39-M5/M6, 5=39-M8/3-8, "
            "6=49-M8/3-8, 7=49-M10"
        ),
        unit="",
        range={"easy": (2, 4), "medium": (0, 7), "hard": (0, 7)},
        choices=_DIFFICULTY_ROWS,
        integer=True,
        coverage=_ALL_ROWS,
        source=(
            "JW Winco GN 784 official metric table, eight printed rows; "
            "the selector carries the entire row without interpolating"
        ),
        askable=True,
    ),
    "ball_type": dict(
        desc="GN 784 ball type: 0=A internal thread, 1=B external thread",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        integer=True,
        refine=True,
        coverage=[0, 1],
        source="JW Winco GN 784 official drawing and Type table",
        askable=True,
    ),
    "thread_code": dict(
        desc=(
            "published thread: 0=M4, 1=M5, 2=M6, 3=M8, 4=M10, "
            "5=1/4-20, 6=3/8-16"
        ),
        unit="",
        range={"easy": (1, 2), "medium": (0, 4), "hard": (0, 6)},
        integer=True,
        refine=True,
        source=(
            "JW Winco GN 784 official d2/d3/d4 table; refine chooses only a "
            "nonblank thread field from the selected complete row and type"
        ),
        askable=True,
    ),
    "clamp_actuator": dict(
        desc="GN 784 identification: 1=adjustable lever, 2=hex-socket set screw",
        unit="",
        range={"easy": (2, 2), "medium": (1, 2), "hard": (1, 2)},
        choices={"easy": [2], "medium": [1, 2], "hard": [1, 2]},
        integer=True,
        coverage=[1, 2],
        source="JW Winco GN 784 official drawing and Identification table",
        askable=True,
    ),
    "swivel_angle": dict(
        desc="static ball pose from vertical (0) to horizontal (90)",
        unit="deg",
        range={"easy": (0, 0), "medium": (0, 30), "hard": (0, 90)},
        choices={"easy": [0], "medium": [0, 30], "hard": [0, 30, 90]},
        integer=True,
        coverage=[0, 30, 90],
        source=(
            "JW Winco GN 784 official swiveling-range drawing marks 30 and "
            "90 degrees; Issue #60 and human CQ-editor review confirm the "
            "vertical-to-horizontal 90 degree pose"
        ),
        askable=True,
    ),
}


def refine(p, difficulty, rng):
    variants = _valid_catalog_variants(p["catalog_row"], difficulty)
    if not variants:
        return
    selected = variants[int(rng.integers(len(variants)))]
    p["ball_type"], p["thread_code"] = selected


def check(p):
    bad = []
    for name in (
        "catalog_row",
        "ball_type",
        "thread_code",
        "clamp_actuator",
        "swivel_angle",
    ):
        if name not in p or int(p[name]) != p[name]:
            bad.append(f"{name} must be an exact integer catalog selector")
            return bad

    d = _catalog_dimensions(
        p["catalog_row"], p["ball_type"], p["thread_code"]
    )
    if d is None:
        bad.append(
            "catalog_row/ball_type/thread_code selects a blank GN 784 table field"
        )
        return bad
    if int(p["clamp_actuator"]) not in (1, 2):
        bad.append("clamp_actuator must be GN 784 identification 1 or 2")
        return bad
    if not 0 <= p["swivel_angle"] <= 90:
        bad.append(
            "swivel_angle must stay in the published vertical-to-horizontal "
            "0-90 degree range"
        )
        return bad

    g = _geometry_proportions(d)
    ball_r = d["d6"] / 2.0
    housing_r = d["d1"] / 2.0

    if housing_r - (ball_r + g["cavity_clearance"]) <= 1.0:
        bad.append(
            "housing wall around ball cavity must exceed 1 mm "
            "(GN 784 dimensions plus proportion clearance)"
        )
    if g["opening_r"] >= ball_r - g["cavity_clearance"]:
        bad.append(
            "socket opening must remain smaller than captured ball "
            "(GN 784 captured-ball function; proportion opening)"
        )
    if g["lower_neck_length"] <= g["housing_wall"]:
        bad.append(
            "lower thin ball neck must be longer than the housing wall "
            "(human CQ-editor review; documented proportion)"
        )
    slot_d = g["lower_neck_d"] + 2.0 * g["slot_clearance"]
    if slot_d >= d["d7"]:
        bad.append(
            "90-degree sweep slot must clear the lower thin neck but remain "
            "narrower than the d7 middle collar (human CQ-editor review)"
        )
    if slot_d / 2.0 >= housing_r:
        bad.append(
            "lower-neck 90-degree sweep slot must retain housing side material "
            "(proportion running clearance)"
        )
    neck_top_radius = g["neck_embed"] + g["lower_neck_length"]
    if neck_top_radius <= housing_r:
        bad.append(
            "lower thin neck must extend beyond the housing outer radius so "
            "the d7 middle collar cannot strike the housing at 90 degrees "
            "(human CQ-editor review)"
        )

    base_r = g["base_d"] / 2.0
    anti_rotation_edge = d["m"] + d["d8"] / 2.0
    if base_r - anti_rotation_edge <= 0.5:
        bad.append(
            "d8 anti-rotation hole must retain positive base edge material "
            "(GN 784 d8 and m; proportion base diameter)"
        )
    if d["m"] - (d["d5"] + d["d8"]) / 2.0 <= 0.5:
        bad.append(
            "d5 base thread and d8 anti-rotation hole must retain a web "
            "(GN 784 d5, d8 and m)"
        )
    if housing_r - (base_r + g["base_clearance"]) <= 1.0:
        bad.append(
            "base pocket must leave a positive housing annulus "
            "(proportion pocket clearance)"
        )

    actuator_top = (
        d["h3"] + g["screw_d"] / 2.0 + g["actuator_clearance"]
    )
    ball_bottom = d["h2"] - ball_r
    if actuator_top >= ball_bottom:
        bad.append(
            "external actuator bore must clear the ball envelope in the fixed "
            "catalog pose (GN 784 h2, h3 and d6; proportion screw diameter)"
        )

    if d["ball_type"] == 0:
        available_thread_height = d["r_ball"] - ball_r
        if d["thread_depth"] + 0.8 >= available_thread_height:
            bad.append(
                "published usable internal thread depth must leave material "
                "above the ball (GN 784 1.5D metric / 1.2D inch rule)"
            )
    elif d["stud_length"] <= 0.0:
        bad.append("Type B must use the selected row's positive published l1")

    if p["clamp_actuator"] == 1:
        if d["k"] <= housing_r + g["actuator_clearance"]:
            bad.append(
                "identification 1 lever envelope k must extend outside housing "
                "(GN 784 k)"
            )
        if d["l2"] <= g["screw_d"]:
            bad.append(
                "identification 1 lever length l2 must exceed pivot diameter "
                "(GN 784 l2; proportion pivot diameter)"
            )

    return bad
