"""Benchmark specification for Ganter GN 1135 threaded lifting pins."""


CATALOG_ROWS = [
    # size, d1, l1, d2, d3, d4, d5, h1, h2, h3, h4, k1, k2, k3, l2, l3,
    # max torque, F1, F2, F3.  Dimensions mm, torque N m, loads kN.
    (8, 8, 12, 6.62, 20, 38, 33.5, 123.7, 54.9, 25.7, 42.5, 11, 68, 46, 17.8, 8, 2, 2.1, 0.9, 0.8),
    (10, 10, 14, 8.35, 20, 38, 33.5, 123.7, 54.9, 25.7, 42.5, 11, 68, 46, 20, 10, 2, 3.9, 1.5, 1.5),
    (12, 12, 17, 10.07, 20, 38, 33.5, 123.7, 54.9, 25.7, 42.5, 11, 68, 46, 24, 12, 2, 6.2, 2.5, 2.3),
    (16, 16, 17, 13.80, 20, 38, 33.5, 123.7, 54.9, 25.7, 42.5, 11, 68, 46, 24, 12, 2, 8.4, 4.5, 4.2),
    (20, 20, 22, 17.25, 35, 59, 50.0, 167.5, 73.7, 36.5, 55.6, 15.5, 102, 70, 30, 17, 3, 16.6, 7.7, 5.0),
]

FIELDS = (
    "catalog_size", "mounting_thread_d1", "thread_engagement_length_l1",
    "lower_pin_core_diameter_d2", "lower_body_diameter_d3",
    "rotating_head_diameter_d4", "button_guard_diameter_d5",
    "overall_height_h1", "body_height_h2", "pivot_axis_height_h3",
    "shackle_opening_height_h4", "shackle_thickness_k1",
    "shackle_outer_width_k2", "shackle_inner_width_k3",
    "lower_pin_projection_l2", "threaded_segment_length_l3",
    "max_torque_nm", "nominal_load_f1_kn", "nominal_load_f2_kn",
    "nominal_load_f3_kn",
)

ROWS_BY_DIFFICULTY = {
    "easy": [0, 1],
    "medium": [2, 3],
    "hard": [0, 1, 2, 3, 4],
}

TABLE_SOURCE = "Ganter GN 1135 dimensional table (issue #154)"


def _ranges(field):
    index = FIELDS.index(field)
    return {
        difficulty: (
            min(CATALOG_ROWS[row][index] for row in rows),
            max(CATALOG_ROWS[row][index] for row in rows),
        )
        for difficulty, rows in ROWS_BY_DIFFICULTY.items()
    }


def _catalog(field, desc, unit="mm", *, integer=False):
    item = {
        "desc": desc,
        "unit": unit,
        "range": _ranges(field),
        "source": TABLE_SOURCE,
        "refine": True,
    }
    if integer:
        item["integer"] = True
    return item


PARAM_SPEC = {
    "catalog_index": {
        "desc": "index selecting one complete official GN 1135 catalog row",
        "unit": "row",
        "range": {"easy": (0, 1), "medium": (2, 3), "hard": (0, 4)},
        "source": TABLE_SOURCE,
        "choices": ROWS_BY_DIFFICULTY,
        "integer": True,
        "coverage": list(range(5)),
    },
    "catalog_size": _catalog("catalog_size", "nominal metric catalog size", "M", integer=True),
    "mounting_thread_d1": _catalog("mounting_thread_d1", "nominal mounting thread diameter d1"),
    "thread_engagement_length_l1": _catalog("thread_engagement_length_l1", "thread engagement length l1"),
    "lower_pin_core_diameter_d2": _catalog("lower_pin_core_diameter_d2", "retracted lower pin core diameter d2"),
    "lower_body_diameter_d3": _catalog("lower_body_diameter_d3", "lower body diameter d3"),
    "rotating_head_diameter_d4": _catalog("rotating_head_diameter_d4", "rotating head diameter d4"),
    "button_guard_diameter_d5": _catalog("button_guard_diameter_d5", "button guard diameter d5"),
    "overall_height_h1": _catalog("overall_height_h1", "upright height above mounting face h1"),
    "body_height_h2": _catalog("body_height_h2", "body and guard height h2"),
    "pivot_axis_height_h3": _catalog("pivot_axis_height_h3", "shackle pivot-axis height h3"),
    "shackle_opening_height_h4": _catalog("shackle_opening_height_h4", "shackle clear opening height h4"),
    "shackle_thickness_k1": _catalog("shackle_thickness_k1", "shackle section thickness k1"),
    "shackle_outer_width_k2": _catalog("shackle_outer_width_k2", "shackle outer width k2"),
    "shackle_inner_width_k3": _catalog("shackle_inner_width_k3", "shackle clear inner width k3"),
    "lower_pin_projection_l2": _catalog("lower_pin_projection_l2", "lower pin projection l2"),
    "threaded_segment_length_l3": _catalog("threaded_segment_length_l3", "retracting threaded-segment length l3"),
    "max_torque_nm": _catalog("max_torque_nm", "maximum catalog tightening torque", "N m"),
    "nominal_load_f1_kn": _catalog("nominal_load_f1_kn", "catalog axial nominal load F1", "kN"),
    "nominal_load_f2_kn": _catalog("nominal_load_f2_kn", "catalog 45-degree nominal load F2", "kN"),
    "nominal_load_f3_kn": _catalog("nominal_load_f3_kn", "catalog transverse nominal load F3", "kN"),
    "lock_state": {
        "desc": "coupled mechanism state: 0 locked, 1 button-depressed/released",
        "unit": "state",
        "range": {"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        "source": "Ganter GN 1135 operating principle (issue #154)",
        "choices": {"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        "integer": True,
        "feature": True,
        "coverage": [0, 1],
    },
    "shackle_swivel_angle_deg": {
        "desc": "shackle swivel about its transverse pivot",
        "unit": "deg",
        "range": {"easy": (0.0, 45.0), "medium": (0.0, 120.0), "hard": (0.0, 180.0)},
        "source": "Ganter GN 1135 drawing: documented 180-degree swivel",
    },
    "shackle_rotation_deg": {
        "desc": "shackle and collar rotation around the stationary pin axis",
        "unit": "deg",
        "range": {"easy": (0.0, 90.0), "medium": (0.0, 270.0), "hard": (0.0, 360.0)},
        "source": "Ganter GN 1135 product description: complete axial rotation",
    },
}


def refine(p: dict, difficulty: str, rng) -> None:
    del rng
    index = int(p["catalog_index"])
    if index not in ROWS_BY_DIFFICULTY[difficulty]:
        from bench2 import Resample
        raise Resample
    for name, value in zip(FIELDS, CATALOG_ROWS[index]):
        p[name] = value


def check(p: dict) -> list[str]:
    bad = []
    index = int(p["catalog_index"])
    if not 0 <= index < len(CATALOG_ROWS):
        return ["catalog_index must select one of the five official GN 1135 rows"]
    for name, expected in zip(FIELDS, CATALOG_ROWS[index]):
        if abs(float(p.get(name, -1)) - float(expected)) > 1e-6:
            bad.append(f"{name} differs from GN 1135 catalog row {index}")

    if not p["lower_pin_core_diameter_d2"] < p["mounting_thread_d1"] <= p["lower_body_diameter_d3"]:
        bad.append("d2 < d1 <= d3 required by the GN 1135 released/locked thread envelope")
    if not p["threaded_segment_length_l3"] <= p["thread_engagement_length_l1"] <= p["lower_pin_projection_l2"]:
        bad.append("l3 <= l1 <= l2 required by the GN 1135 lower-pin drawing")
    if p["button_guard_diameter_d5"] >= p["rotating_head_diameter_d4"]:
        bad.append("d5 >= d4: button guard must fit inside rotating-head envelope (GN 1135 drawing)")
    if p["shackle_inner_width_k3"] + 2.0 * p["shackle_thickness_k1"] > p["shackle_outer_width_k2"]:
        bad.append("k3 + 2*k1 > k2: shackle section exceeds official outer width")
    if not p["pivot_axis_height_h3"] < p["body_height_h2"] < p["overall_height_h1"]:
        bad.append("h3 < h2 < h1 required by the GN 1135 upright drawing")
    if p["body_height_h2"] + p["shackle_opening_height_h4"] >= p["overall_height_h1"]:
        bad.append("h2 + h4 >= h1: shackle opening leaves no upper section (GN 1135 drawing)")
    if p["lock_state"] not in (0, 1):
        bad.append("lock_state must be locked=0 or released=1 (GN 1135 operating principle)")
    if not 0.0 <= p["shackle_swivel_angle_deg"] <= 180.0:
        bad.append("shackle swivel must stay within the documented 180-degree range")
    if not 0.0 <= p["shackle_rotation_deg"] <= 360.0:
        bad.append("shackle rotation must stay within the documented complete turn")
    if min(p["nominal_load_f1_kn"], p["nominal_load_f2_kn"], p["nominal_load_f3_kn"]) <= 0.0:
        bad.append("F1/F2/F3 must be positive catalog nominal loads (GN 1135 table)")
    return bad
