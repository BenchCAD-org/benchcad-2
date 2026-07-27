"""Sampling contract for the DIN 808 single-jointed EG universal joint."""


# JW Winco DIN 808 metric table:
# row: (outside d1, circular bore d2, square s, EG length l1, half length l3,
#       maximum shaft assembly depth t +1)
CATALOG_ROWS = {
    1: (16.0, 6.0, 6.0, 34.0, 17.0, 8.0),
    2: (16.0, 8.0, 8.0, 40.0, 20.0, 11.0),
    3: (16.0, 10.0, 8.0, 52.0, 26.0, 14.0),
    4: (22.0, 10.0, 10.0, 48.0, 24.0, 12.0),
    5: (22.0, 12.0, 10.0, 62.0, 31.0, 18.0),
    6: (25.0, 12.0, 12.0, 56.0, 28.0, 13.0),
    7: (25.0, 16.0, 12.0, 74.0, 37.0, 21.0),
    8: (28.0, 14.0, 14.0, 60.0, 30.0, 13.0),
    9: (32.0, 16.0, 16.0, 68.0, 34.0, 16.0),
    10: (32.0, 20.0, 16.0, 86.0, 43.0, 24.0),
    11: (36.0, 18.0, 18.0, 74.0, 37.0, 17.0),
    12: (42.0, 20.0, 20.0, 82.0, 41.0, 18.0),
    13: (42.0, 25.0, 20.0, 108.0, 54.0, 31.0),
    14: (45.0, 22.0, 22.0, 95.0, 47.5, 22.0),
    15: (50.0, 25.0, 25.0, 108.0, 54.0, 26.0),
    16: (50.0, 30.0, 25.0, 132.0, 66.0, 38.0),
    17: (58.0, 30.0, 30.0, 122.0, 61.0, 29.0),
    18: (58.0, 32.0, 30.0, 130.0, 65.0, 33.0),
    19: (70.0, 35.0, 35.0, 140.0, 70.0, 35.0),
}

ROWS_BY_DIFFICULTY = {
    "easy": [8, 9, 11, 12],
    "medium": list(range(4, 17)),
    "hard": list(range(1, 20)),
}

BORES_BY_DIFFICULTY = {
    "easy": [0],          # B: equal circular bores, no keyway
    "medium": [0, 1],     # B or K
    "hard": [0, 1, 2],    # B, K, or V
}

ANGLES_BY_DIFFICULTY = {
    "easy": [0, 10, 20],
    "medium": [0, 15, 30, 45],
    "hard": [0, 15, 30, 45],
}


def _row_range(column):
    return {
        difficulty: (
            min(CATALOG_ROWS[row][column] for row in rows),
            max(CATALOG_ROWS[row][column] for row in rows),
        )
        for difficulty, rows in ROWS_BY_DIFFICULTY.items()
    }


def _keyway_dimensions(d2):
    """Return DIN 6885-1 hub-keyway width b and radial depth t2."""
    if d2 <= 8.0:
        return 2.0, 1.0
    if d2 <= 10.0:
        return 3.0, 1.4
    if d2 <= 12.0:
        return 4.0, 1.8
    if d2 <= 16.0:
        return 5.0, 2.3
    if d2 <= 22.0:
        return 6.0, 2.8
    if d2 <= 30.0:
        return 8.0, 3.3
    return 10.0, 3.3


PARAM_SPEC = {
    "catalog_row": dict(
        desc="JW Winco DIN 808 metric catalog-row selector (1-19)",
        unit="",
        range={"easy": (8, 12), "medium": (4, 16), "hard": (1, 19)},
        choices=ROWS_BY_DIFFICULTY,
        integer=True,
        source="JW Winco DIN 808 metric table; one choice selects one complete row",
        askable=True,
    ),
    "bore_code": dict(
        desc="equal end-bore code: 0=B plain circular, 1=K keyed circular, 2=V square",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 2)},
        choices=BORES_BY_DIFFICULTY,
        integer=True,
        source="JW Winco DIN 808 bore-code table; equal code at both ends",
        feature=True,
    ),
    "joint_angle": dict(
        desc="static absolute inclination between the two shaft axes",
        unit="deg",
        range={"easy": (0, 20), "medium": (0, 45), "hard": (0, 45)},
        choices=ANGLES_BY_DIFFICULTY,
        integer=True,
        source="JW Winco DIN 808 EG engineering drawing, permissible pose shown as +/-45 degrees",
        askable=True,
    ),
    "d1": dict(
        desc="outside diameter d1",
        unit="mm",
        range=_row_range(0),
        refine=True,
        source="JW Winco DIN 808 metric table, selected row d1",
        askable=True,
    ),
    "d2": dict(
        desc="equal H7 circular bore diameter for B/K",
        unit="mm",
        range=_row_range(1),
        refine=True,
        source="JW Winco DIN 808 metric table, selected row d2 H7",
        askable=True,
    ),
    "square_s": dict(
        desc="equal H10 square size for V",
        unit="mm",
        range=_row_range(2),
        refine=True,
        source="JW Winco DIN 808 metric table, selected row s H10",
        askable=True,
    ),
    "l1": dict(
        desc="overall straight-pose length for single-jointed EG",
        unit="mm",
        range=_row_range(3),
        refine=True,
        source="JW Winco DIN 808 metric table, selected row l1 Type EG",
        askable=True,
    ),
    "l3": dict(
        desc="end face to trunnion-center half length",
        unit="mm",
        range=_row_range(4),
        refine=True,
        source="JW Winco DIN 808 metric table, selected row l3",
        askable=True,
    ),
    "shaft_depth": dict(
        desc="maximum shaft insertion envelope t (+1 tolerance not modeled)",
        unit="mm",
        range=_row_range(5),
        refine=True,
        source="JW Winco DIN 808 metric table, selected row t +1 max assembly length",
        askable=True,
    ),
    "keyway_width": dict(
        desc="DIN 6885-1 JS9 hub-keyway width b; zero when bore code is not K",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (0.0, 8.0), "hard": (0.0, 10.0)},
        refine=True,
        source="JW Winco DIN 6885-1 metric keyway table, JS9 hub-keyway column",
        askable=True,
    ),
    "keyway_depth": dict(
        desc="DIN 6885-1 hub-keyway radial depth t2; zero when bore code is not K",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (0.0, 3.3), "hard": (0.0, 3.3)},
        refine=True,
        source="JW Winco DIN 6885-1 metric keyway table, t2 column",
        askable=True,
    ),
}


def refine(p, difficulty, rng):
    del rng
    row = int(p["catalog_row"])
    d1, d2, square_s, l1, l3, shaft_depth = CATALOG_ROWS[row]
    p["d1"] = d1
    p["d2"] = d2
    p["square_s"] = square_s
    p["l1"] = l1
    p["l3"] = l3
    p["shaft_depth"] = shaft_depth

    if int(p["bore_code"]) == 1:
        p["keyway_width"], p["keyway_depth"] = _keyway_dimensions(d2)
    else:
        p["keyway_width"] = 0.0
        p["keyway_depth"] = 0.0


def check(p):
    bad = []
    row_number = int(p["catalog_row"])
    if row_number not in CATALOG_ROWS:
        return ["catalog_row must select one of the 19 JW Winco DIN 808 metric rows"]

    expected = CATALOG_ROWS[row_number]
    actual = (
        p["d1"],
        p["d2"],
        p["square_s"],
        p["l1"],
        p["l3"],
        p["shaft_depth"],
    )
    if actual != expected:
        bad.append("d1/d2/s/l1/l3/t must remain coupled to one complete DIN 808 table row")

    if abs(p["l1"] - 2.0 * p["l3"]) > 1e-9:
        bad.append("l1 must equal 2*l3 for the symmetric single-jointed EG drawing")
    if p["d2"] >= p["d1"]:
        bad.append("d2 must be smaller than d1 to preserve a positive circular-bore hub wall")
    if p["square_s"] >= p["d1"]:
        bad.append("square s must be smaller than d1 to preserve a positive square-bore hub wall")
    if p["shaft_depth"] <= 0.0 or p["shaft_depth"] >= p["l3"]:
        bad.append("shaft insertion depth t must remain positive and stop before the joint center")
    if not 0.0 <= p["joint_angle"] <= 45.0:
        bad.append("joint_angle must remain inside the DIN 808 drawing's absolute 0-45 degree pose")

    bore_code = int(p["bore_code"])
    if bore_code not in (0, 1, 2):
        bad.append("bore_code must be B, K, or V (encoded 0, 1, or 2)")
    expected_key = _keyway_dimensions(p["d2"]) if bore_code == 1 else (0.0, 0.0)
    if (p["keyway_width"], p["keyway_depth"]) != expected_key:
        bad.append("K keyway b/t2 must match DIN 6885-1 for selected d2; B/V must have no keyway")

    # The following construction checks enforce the explicitly documented
    # proportion envelope used for uncited fork and cross details.
    hub_length = p["shaft_depth"]
    ear_radius = 0.21 * p["d1"]
    ear_offset = 0.37 * p["d1"]
    ear_thickness = 0.18 * p["d1"]
    trunnion_d = 0.16 * p["d1"]
    trunnion_hole_d = 0.19 * p["d1"]
    if hub_length >= p["l3"] - 0.21 * p["d1"]:
        bad.append("proportion: hub must leave enough axial length for a non-degenerate fork eye")
    if ear_offset + ear_thickness / 2.0 >= p["d1"] / 2.0:
        bad.append("proportion: fork ears must remain inside the d1 root envelope")
    if 2.0 * ear_radius >= 2.0**0.5 * ear_offset:
        bad.append("proportion: perpendicular input/output fork-eye envelopes must remain disjoint")
    if trunnion_hole_d <= trunnion_d:
        bad.append("proportion: trunnion hole must exceed cross-arm diameter for positive clearance")
    return bad
