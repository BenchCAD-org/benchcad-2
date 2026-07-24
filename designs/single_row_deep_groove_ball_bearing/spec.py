"""Benchmark spec for 6000-6005 open single-row deep groove ball bearings.

Boundary dimensions d, D, and B are coupled catalog rows. Internal ball, pitch
circle, groove, and cage dimensions are not public ISO/SKF boundary dimensions
in the reviewed evidence, so they are explicitly treated as proportions.
"""

from bench2 import Resample


CATALOG_ROWS = {
    # designation: bore d, outside D, width B, Cr N, Cor N, mass kg
    6000: (10.0, 26.0, 8.0, 4160, 1780, 0.019),
    6001: (12.0, 28.0, 8.0, 5110, 2380, 0.022),
    6002: (15.0, 32.0, 9.0, 5590, 2840, 0.030),
    6003: (17.0, 35.0, 10.0, 6000, 3250, 0.039),
    6004: (20.0, 42.0, 12.0, 9390, 5020, 0.069),
    6005: (25.0, 47.0, 12.0, 10060, 5860, 0.080),
}

ROWS_BY_DIFF = {
    "easy": [6000, 6001],
    "medium": [6002, 6003],
    "hard": [6004, 6005],
}

# Internal construction values. Only the 6000 ball count, ball diameter, and
# pitch diameter are calibrated from the provided TraceParts 6000 reference PNGs.
# All raceway/cage values and all 6001-6005 internal values are proportions:
# separate per designation, mechanically spaced, but not claimed as SKF/ISO
# or manufacturer-measured internal data.
INTERNAL_ROWS = {
    # designation: ball_d, ball_count, pitch_d, groove_depth, cage_t, cage_width
    6000: (4.83, 7, 18.04, 1.43, 0.96, 1.18),
    6001: (4.90, 7, 19.40, 1.45, 0.98, 1.18),
    6002: (4.35, 8, 22.40, 1.32, 0.88, 1.15),
    6003: (4.70, 8, 24.60, 1.48, 0.95, 1.25),
    6004: (5.55, 8, 31.40, 1.65, 1.10, 1.55),
    6005: (5.70, 9, 36.40, 1.70, 1.15, 1.60),
}


PARAM_SPEC = {
    "designation": dict(
        desc="6000-series bearing designation; selects the coupled d/D/B catalog row",
        unit="",
        range={"easy": (6000, 6001), "medium": (6000, 6003), "hard": (6000, 6005)},
        source="6000-series boundary-dimension table, rows 6000-6005; ISO 15:2017 boundary-dimension family",
        choices={"easy": [6000, 6001], "medium": [6002, 6003], "hard": [6004, 6005]},
        coverage=[6000, 6001, 6002, 6003, 6004, 6005],
        integer=True,
        askable=True,
    ),
    "bore_d": dict(
        desc="bearing bore diameter d",
        unit="mm",
        range={"easy": (10.0, 12.0), "medium": (15.0, 17.0), "hard": (20.0, 25.0)},
        source="6000-series boundary-dimension table, column d; 6000 spot-checked against SKF PDF",
        refine=True,
        coverage=[10.0, 12.0, 15.0, 17.0, 20.0, 25.0],
        askable=True,
    ),
    "outer_d": dict(
        desc="bearing outside diameter D",
        unit="mm",
        range={"easy": (26.0, 28.0), "medium": (32.0, 35.0), "hard": (42.0, 47.0)},
        source="6000-series boundary-dimension table, column D; 6000 spot-checked against SKF PDF",
        refine=True,
        coverage=[26.0, 28.0, 32.0, 35.0, 42.0, 47.0],
        askable=True,
    ),
    "width": dict(
        desc="bearing width B",
        unit="mm",
        range={"easy": (8.0, 8.0), "medium": (9.0, 10.0), "hard": (12.0, 12.0)},
        source="6000-series boundary-dimension table, column B; 6000 spot-checked against SKF PDF",
        refine=True,
        coverage=[8.0, 9.0, 10.0, 12.0],
        askable=True,
    ),
    "ball_d": dict(
        desc="proportion-based rolling ball diameter",
        unit="mm",
        range={"easy": (4.75, 5.00), "medium": (4.30, 4.75), "hard": (5.45, 5.80)},
        source="proportion: 6000 baseline calibrated from TraceParts reference-image geometry; 6001-6005 are per-designation proportion estimates, not manufacturer-measured internal data",
        refine=True,
        askable=True,
    ),
    "ball_count": dict(
        desc="number of equally spaced balls in the single row",
        unit="",
        range={"easy": (7, 7), "medium": (8, 8), "hard": (8, 9)},
        source="6000 image-derived count from provided TraceParts seven-view PNGs; 6001-6005 are per-designation proportion estimates",
        integer=True,
        refine=True,
        askable=True,
    ),
    "pitch_d": dict(
        desc="ball pitch-circle diameter",
        unit="mm",
        range={"easy": (17.9, 19.6), "medium": (22.2, 24.8), "hard": (31.1, 36.7)},
        source="proportion: 6000 baseline calibrated from TraceParts reference-image geometry; 6001-6005 are per-designation proportion estimates, not manufacturer-measured internal data",
        refine=True,
        askable=True,
    ),
    "race_groove_depth": dict(
        desc="radial overlap of each ball into the simplified deep race grooves",
        unit="mm",
        range={"easy": (1.36, 1.52), "medium": (1.28, 1.52), "hard": (1.58, 1.76)},
        source="proportion: simplified raceway depth constrained by ring-wall continuity and ball-envelope clearance; not manufacturer-measured internal data",
        refine=True,
    ),
    "cage_t": dict(
        desc="radial thickness of the simplified cage band",
        unit="mm",
        range={"easy": (0.90, 1.06), "medium": (0.84, 1.04), "hard": (1.04, 1.22)},
        source="proportion: cage strip thickness/pocket details not public boundary data",
        refine=True,
    ),
    "cage_width": dict(
        desc="axial width of the simplified ball retainer cage",
        unit="mm",
        range={"easy": (1.10, 1.28), "medium": (1.08, 1.32), "hard": (1.46, 1.70)},
        source="proportion: cage width not public boundary data",
        refine=True,
    ),
}


def _row(designation):
    try:
        return CATALOG_ROWS[int(designation)]
    except KeyError as exc:
        raise Resample from exc


def refine(p: dict, difficulty: str, rng) -> None:
    designation = int(p["designation"])
    if designation not in ROWS_BY_DIFF[difficulty]:
        raise Resample

    bore_d, outer_d, width, _cr, _cor, _mass = _row(designation)
    p["bore_d"] = bore_d
    p["outer_d"] = outer_d
    p["width"] = width

    ball_d, ball_count, pitch_d, groove_depth, cage_t, cage_width = INTERNAL_ROWS[designation]
    # Small benchmark perturbations around the image-calibrated 6000 baseline
    # and the proportion rows for 6001-6005. They represent dataset variation,
    # not image-fit uncertainty or manufacturer tolerance.
    if designation == 6000:
        ball_jitter, pitch_jitter, groove_jitter = 0.04, 0.12, 0.03
        cage_jitter = 0.04
    else:
        ball_jitter, pitch_jitter, groove_jitter = 0.07, 0.18, 0.06
        cage_jitter = 0.08
    p["ball_d"] = round(ball_d + float(rng.uniform(-ball_jitter, ball_jitter)), 2)
    p["ball_count"] = ball_count
    p["pitch_d"] = round(pitch_d + float(rng.uniform(-pitch_jitter, pitch_jitter)), 2)
    p["race_groove_depth"] = round(groove_depth + float(rng.uniform(-groove_jitter, groove_jitter)), 2)
    p["cage_t"] = round(cage_t + float(rng.uniform(-cage_jitter, cage_jitter)), 2)
    p["cage_width"] = round(cage_width + float(rng.uniform(-cage_jitter, cage_jitter)), 2)


def check(p: dict) -> list[str]:
    bad = []

    designation = int(p["designation"])
    if designation not in CATALOG_ROWS:
        bad.append("designation is not one of the real 6000-6005 catalog rows")
        return bad

    bore_d, outer_d, width, _cr, _cor, _mass = _row(designation)
    if (p["bore_d"], p["outer_d"], p["width"]) != (bore_d, outer_d, width):
        bad.append("d/D/B must stay coupled to the selected 6000-6005 table row, not independently mixed")

    if p["bore_d"] >= p["outer_d"]:
        bad.append("bore_d >= outer_d: bearing must have a positive annular envelope")

    span = p["outer_d"] - p["bore_d"]
    inner_shoulder_d = p["bore_d"] + 0.30 * span
    outer_race_d = p["outer_d"] - (3.4 / 16.0) * span
    race_clearance = p["ball_d"] * 0.04
    inner_shoulder_r = inner_shoulder_d / 2.0
    outer_race_r = outer_race_d / 2.0
    pitch_r = p["pitch_d"] / 2.0
    ball_r = p["ball_d"] / 2.0
    inner_wall = (inner_shoulder_d - p["bore_d"]) / 2.0
    outer_wall = (p["outer_d"] - outer_race_d) / 2.0

    if inner_wall <= 0.9:
        bad.append("inner ring wall <= 0.9 mm after groove: ring would be too thin (positive wall requirement)")
    if outer_wall <= 0.9:
        bad.append("outer ring wall <= 0.9 mm after groove: ring would be too thin (positive wall requirement)")
    if p["race_groove_depth"] >= inner_wall - 0.25:
        bad.append("race_groove_depth nearly cuts through inner ring wall: inner ring must remain one continuous body")
    if p["race_groove_depth"] >= outer_wall - 0.25:
        bad.append("race_groove_depth nearly cuts through outer ring wall: outer ring outside surface must remain continuous")
    if not (p["bore_d"] < inner_shoulder_d < p["pitch_d"] < outer_race_d < p["outer_d"]):
        bad.append("raceway ordering invalid: bore < inner shoulder < pitch < outer race diameter < outside diameter must hold")
    if inner_shoulder_r - p["race_groove_depth"] > pitch_r - ball_r - race_clearance:
        bad.append("inner groove too shallow: ball would remain hidden behind the inner-ring shoulder")
    if outer_race_r + p["race_groove_depth"] < pitch_r + ball_r + race_clearance:
        bad.append("outer groove too shallow: ball would not fit the outer raceway opening")

    if p["ball_d"] >= p["width"] * 0.84:
        bad.append("ball_d >= 0.84*width: balls would protrude beyond open bearing end faces")
    if p["cage_width"] >= p["width"] * 0.45:
        bad.append("cage_width >= 0.45*width: cage would dominate the open bearing width")
    if p["cage_t"] >= p["ball_d"] * 0.42:
        bad.append("cage_t >= 0.42*ball_d: cage band would hide the rolling balls")
    if p["cage_t"] <= 0.18 * p["ball_d"]:
        bad.append("cage_t <= 0.18*ball_d: cage band would be too thin to read in preview")
    if p["cage_t"] >= p["ball_d"] + 2.0 * race_clearance:
        bad.append("cage_t reaches the ring raceway clearance envelope: cage must stay between inner and outer rings")
    if p["race_groove_depth"] <= 0 or p["race_groove_depth"] >= p["ball_d"] * 0.32:
        bad.append("race_groove_depth outside plausible proportion: grooves should cradle but not swallow the balls")

    circumference = 3.14159 * p["pitch_d"]
    if p["ball_count"] * p["ball_d"] >= circumference * 0.86:
        bad.append("balls too crowded on pitch circle: need cage clearance between rolling elements")

    return bad
