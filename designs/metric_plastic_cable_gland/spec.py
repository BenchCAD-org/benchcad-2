"""Sampling contract for the metric plastic cable gland family."""


# LAPP SKINTOP ST-M, DB53111000EN v17 (2023-06-20), dimensions in mm:
# index: M, SW, A, C_min, C_max, D, clamp_min, clamp_max, O-ring.
SIZE_ROWS = [
    (12.0, 15.0, 16.6, 26.5, 30.0, 8.0, 3.5, 7.0, 0),
    (16.0, 19.0, 21.1, 29.0, 34.0, 8.0, 4.0, 10.0, 0),
    (20.0, 25.0, 27.6, 34.0, 37.0, 9.0, 6.0, 13.0, 0),
    (25.0, 30.0, 33.6, 35.0, 40.0, 10.0, 8.0, 17.0, 0),
    (32.0, 36.0, 40.3, 39.0, 47.0, 10.0, 9.0, 21.0, 0),
    (40.0, 46.0, 51.6, 43.0, 52.0, 10.0, 16.0, 28.0, 1),
    (50.0, 55.0, 61.6, 54.0, 62.0, 12.0, 27.0, 34.0, 1),
    (63.0, 66.0, 73.9, 59.0, 71.0, 12.0, 34.0, 45.0, 1),
]


PARAM_SPEC = {
    "size_index": dict(
        desc="Index of the coupled LAPP SKINTOP ST-M catalog row",
        unit="",
        range={"easy": (0, 1), "medium": (2, 4), "hard": (5, 7)},
        choices={"easy": [0, 1], "medium": [2, 3, 4], "hard": [5, 6, 7]},
        integer=True,
        coverage=list(range(8)),
        source="LAPP DB53111000EN v17 dimension table, M12 through M63 rows",
        askable=True,
    ),
    "thread_d": dict(
        desc="Nominal metric male connection thread diameter",
        unit="mm",
        range={"easy": (12.0, 16.0), "medium": (20.0, 32.0), "hard": (40.0, 63.0)},
        source="LAPP DB53111000EN v17 and EN 60423, pitch fixed at 1.5 mm",
        refine=True,
        askable=True,
    ),
    "sw": dict(
        desc="Hexagonal body wrench size across flats",
        unit="mm",
        range={"easy": (15.0, 19.0), "medium": (25.0, 36.0), "hard": (46.0, 66.0)},
        source="LAPP DB53111000EN v17, SW column",
        refine=True,
        askable=True,
    ),
    "outer_dia_a": dict(
        desc="Maximum outside diameter A of the fluted cap",
        unit="mm",
        range={"easy": (16.6, 21.1), "medium": (27.6, 40.3), "hard": (51.6, 73.9)},
        source="LAPP DB53111000EN v17, diameter A column",
        refine=True,
        askable=True,
    ),
    "overall_len": dict(
        desc="Overall gland length C in relaxed or tightened state",
        unit="mm",
        range={"easy": (26.5, 34.0), "medium": (34.0, 47.0), "hard": (43.0, 71.0)},
        source="LAPP DB53111000EN v17, C minimum and maximum columns",
        refine=True,
        askable=True,
    ),
    "thread_len": dict(
        desc="Male connection thread length D",
        unit="mm",
        range={"easy": (8.0, 8.0), "medium": (9.0, 10.0), "hard": (10.0, 12.0)},
        source="LAPP DB53111000EN v17, D column",
        refine=True,
        askable=True,
    ),
    "clamp_min": dict(
        desc="Minimum cable diameter in the published clamping range",
        unit="mm",
        range={"easy": (3.5, 4.0), "medium": (6.0, 9.0), "hard": (16.0, 34.0)},
        source="LAPP DB53111000EN v17, clamping range F lower bound",
        refine=True,
        askable=True,
    ),
    "clamp_max": dict(
        desc="Maximum cable diameter in the published clamping range",
        unit="mm",
        range={"easy": (7.0, 10.0), "medium": (13.0, 21.0), "hard": (28.0, 45.0)},
        source="LAPP DB53111000EN v17, clamping range F upper bound",
        refine=True,
        askable=True,
    ),
    "o_ring": dict(
        desc="Whether the catalog row includes the M40+ NBR shoulder O-ring",
        unit="",
        range={"easy": (0, 0), "medium": (0, 0), "hard": (1, 1)},
        source="LAPP DB53111000EN v17: 36x2, 46x2, and 57x2 O-rings for M40/M50/M63",
        refine=True,
        feature=True,
    ),
    "tightened": dict(
        desc="Cap position: relaxed C maximum or fully tightened C minimum",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        integer=True,
        feature=True,
        source="LAPP DB53111000EN v17, difference between C maximum and C minimum",
    ),
}


def refine(p: dict, difficulty: str, rng) -> None:
    row = SIZE_ROWS[p["size_index"]]
    (
        p["thread_d"],
        p["sw"],
        p["outer_dia_a"],
        c_min,
        c_max,
        p["thread_len"],
        p["clamp_min"],
        p["clamp_max"],
        p["o_ring"],
    ) = row
    p["overall_len"] = c_min if p["tightened"] else c_max


def check(p: dict) -> list[str]:
    bad = []
    row = SIZE_ROWS[p["size_index"]]
    expected = (
        p["thread_d"],
        p["sw"],
        p["outer_dia_a"],
        p["thread_len"],
        p["clamp_min"],
        p["clamp_max"],
        p["o_ring"],
    )
    catalog = (row[0], row[1], row[2], row[5], row[6], row[7], row[8])
    if expected != catalog:
        bad.append("all dimensions must remain coupled to one DB53111000EN v17 catalog row")
    expected_len = row[3] if p["tightened"] else row[4]
    if p["overall_len"] != expected_len:
        bad.append("overall length must equal the selected row's C min/max for tightened/relaxed state")
    if not p["clamp_max"] < p["thread_d"] - 1.2 * 1.5:
        bad.append("clamp maximum must pass the connection-thread minor bore (issue #31 engineering rule)")
    if not p["sw"] > p["thread_d"]:
        bad.append("SW must exceed nominal thread diameter (DB53111000EN v17 table)")
    if not p["sw"] < p["outer_dia_a"] < 1.1547 * p["sw"]:
        bad.append("cap diameter A must lie between hex flats and corners (issue #31 geometry rule)")
    if row[4] - row[3] < 3.0 or row[4] - row[3] > 12.0:
        bad.append("seal compression travel Cmax-Cmin must remain 3 to 12 mm (DB53111000EN v17)")
    if row[3] < p["thread_len"] + 18.0:
        bad.append("tightened length must leave at least 18 mm above thread D (issue #31 rule)")
    if p["o_ring"] != int(p["thread_d"] >= 40.0):
        bad.append("O-ring is present only on M40 and larger catalog rows")
    return bad
