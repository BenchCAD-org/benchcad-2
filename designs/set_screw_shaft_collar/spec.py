"""Benchmark spec for a GN 705 / DIN 705 style set screw shaft collar."""

from bench2 import Resample


CATALOG_ROWS = [
    # d1, d2, screw major diameter, screw length, b
    (5, 10, 3, 4, 6),
    (6, 12, 4, 5, 8),
    (8, 16, 4, 6, 8),
    (10, 20, 5, 8, 10),
    (12, 22, 6, 8, 12),
    (16, 28, 6, 8, 12),
    (20, 32, 6, 8, 14),
    (24, 40, 8, 12, 16),
    (30, 45, 8, 10, 16),
    (35, 56, 8, 12, 16),
    (40, 63, 10, 16, 18),
    (50, 80, 10, 16, 18),
    (60, 90, 10, 16, 20),
    (70, 100, 10, 20, 20),
    (80, 110, 12, 20, 22),
]

ROWS_BY_DIFF = {
    "easy": [row for row in CATALOG_ROWS if row[0] <= 16],
    "medium": [row for row in CATALOG_ROWS if 10 <= row[0] <= 40],
    "hard": CATALOG_ROWS,
}


PARAM_SPEC = {
    "bore_d": dict(
        desc="H8 inner bore diameter d1 for the shaft",
        unit="mm",
        range={"easy": (5, 16), "medium": (10, 40), "hard": (5, 80)},
        source="JW Winco GN 705 metric table, column d1 H8",
        choices={
            "easy": [row[0] for row in ROWS_BY_DIFF["easy"]],
            "medium": [row[0] for row in ROWS_BY_DIFF["medium"]],
            "hard": [row[0] for row in ROWS_BY_DIFF["hard"]],
        },
        integer=True,
        askable=True,
        coverage=[row[0] for row in CATALOG_ROWS],
    ),
    "outer_d": dict(
        desc="Outside diameter d2 of the collar",
        unit="mm",
        range={"easy": (10, 28), "medium": (20, 63), "hard": (10, 110)},
        source="JW Winco GN 705 metric table, column d2",
        refine=True,
        askable=True,
    ),
    "width": dict(
        desc="Axial collar width b js14",
        unit="mm",
        range={"easy": (6, 12), "medium": (10, 18), "hard": (6, 22)},
        source="JW Winco GN 705 metric table, column b js14",
        refine=True,
        askable=True,
    ),
    "screw_d": dict(
        desc="Set screw nominal thread major diameter d3",
        unit="mm",
        range={"easy": (3, 6), "medium": (5, 10), "hard": (3, 12)},
        source="JW Winco GN 705 metric table, column d3, M size converted to major diameter",
        refine=True,
        askable=True,
    ),
    "screw_len": dict(
        desc="Set screw nominal length from the catalog d3 entry",
        unit="mm",
        range={"easy": (4, 8), "medium": (8, 16), "hard": (4, 20)},
        source="JW Winco GN 705 metric table, column d3, length after x",
        refine=True,
        askable=True,
    ),
    "second_screw": dict(
        desc="Second set screw on the largest GN 705 table rows, placed at 135 degrees per drawing cue",
        unit="",
        range={"easy": (0, 0), "medium": (0, 0), "hard": (0, 1)},
        source="JW Winco GN 705 note: second grub screw for d1 > 70 mm",
        choices={"easy": [0], "medium": [0], "hard": [0, 1]},
        refine=True,
        feature=True,
    ),
}


def _row_for_bore(bore_d):
    for row in CATALOG_ROWS:
        if row[0] == int(round(bore_d)):
            return row
    raise Resample


def refine(p: dict, difficulty: str, rng) -> None:
    d1, d2, screw_d, screw_len, width = _row_for_bore(p["bore_d"])
    allowed = ROWS_BY_DIFF[difficulty]
    if (d1, d2, screw_d, screw_len, width) not in allowed:
        raise Resample
    p["outer_d"] = float(d2)
    p["screw_d"] = float(screw_d)
    p["screw_len"] = float(screw_len)
    p["width"] = float(width)
    p["second_screw"] = 1 if d1 > 70 else 0


def check(p: dict) -> list[str]:
    bad = []
    wall = (p["outer_d"] - p["bore_d"]) / 2.0
    if wall <= p["screw_d"] * 0.65:
        bad.append("wall <= 0.65*screw_d: collar needs material around the radial set screw")
    if p["width"] < p["screw_d"] * 1.45:
        bad.append("width < 1.45*screw_d: catalog proportions leave axial support for the tapped screw")
    if p["second_screw"] and p["bore_d"] <= 70:
        bad.append("second_screw set below d1 > 70: GN 705 large-size note limits the opposed second screw")
    if (not p["second_screw"]) and p["bore_d"] > 70:
        bad.append("second_screw missing above d1 > 70: GN 705 large-size note calls for an opposed second screw")
    return bad
