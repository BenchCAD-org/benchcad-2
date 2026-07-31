"""Benchmark specification for the RÖHM DURO-M three-jaw scroll chuck.

``catalog_index`` selects one complete DIN 6350 cylindrical-centre-mount row
from the official DURO-M catalogue.  ``jaw_open_fraction`` is an operating
state within that row's published A1 external-chucking range; it is not a new
catalogue model and never creates arbitrary size combinations.

Parameter names carry the drawing symbol (physical-quantity + symbol, repo
convention): chuck table symbols A/B/C/D/E/F/G/K from catalogue p.3048, jaw BB
table symbols A/B/C/D/E/F/G/H from p.3060, chucking range A1 from p.3044.
"""


CATALOG_ROWS = [
    # chuck: size(A), item, B, C, D, E, F, G, holes; jaw BB: A/B/C/D/E/F/G/H;
    # key square K; A1 chucking range min/max
    dict(size=74, item=185299, B=56, C=2.5, D=32.5, E=15, F=63, G=6, holes=3,
         jA=32, jB=10, jC=23, jD=4.7, jE=4.0, jF=10, jG=21, jH=5, K=6,
         amin=2, amax=24),
    dict(size=80, item=185300, B=56, C=3, D=39.5, E=19, F=67, G=6, holes=3,
         jA=37, jB=12, jC=26, jD=4.8, jE=4.5, jF=12, jG=24.5, jH=6, K=6,
         amin=2, amax=30),
    dict(size=100, item=185301, B=70, C=3, D=50, E=20, F=83, G=8, holes=3,
         jA=48, jB=14, jC=33.5, jD=6.3, jE=6.0, jF=15, jG=31, jH=6, K=8,
         amin=3, amax=38),
    dict(size=125, item=185302, B=95, C=4, D=56, E=32, F=108, G=8, holes=3,
         jA=52, jB=18, jC=41.5, jD=7.3, jE=7.0, jF=17, jG=35, jH=8, K=9,
         amin=3, amax=53),
    dict(size=140, item=185585, B=105, C=4, D=60, E=40, F=120, G=8, holes=3,
         jA=61, jB=18, jC=41.5, jD=8.3, jE=7.0, jF=18, jG=40, jH=8, K=9,
         amin=3, amax=53),
    dict(size=160, item=185303, B=125, C=4, D=65, E=42, F=140, G=10, holes=3,
         jA=61, jB=18, jC=47.5, jD=8.3, jE=7.0, jF=18, jG=40, jH=10, K=10,
         amin=4, amax=72),
    dict(size=200, item=185304, B=160, C=4, D=73.5, E=55, F=176, G=10, holes=3,
         jA=69, jB=20, jC=53.5, jD=8.3, jE=8.0, jF=20, jG=44, jH=10, K=11,
         amin=4, amax=100),
    dict(size=250, item=185305, B=200, C=5, D=82, E=76, F=224, G=12, holes=3,
         jA=90, jB=24, jC=67.5, jD=10.3, jE=10.0, jF=27, jG=57, jH=14, K=12,
         amin=5, amax=122),
    dict(size=315, item=185306, B=260, C=5, D=95, E=103, F=286, G=16, holes=3,
         jA=130, jB=34, jC=79.5, jD=11.3, jE=15.0, jF=41.5, jG=86.5, jH=15,
         K=14, amin=6, amax=135),
    dict(size=400, item=185307, B=330, C=5, D=105, E=136, F=362, G=16, holes=3,
         jA=130, jB=34, jC=79.5, jD=11.3, jE=15.0, jF=41.5, jG=86.5, jH=15,
         K=17, amin=20, amax=200),
    dict(size=500, item=185308, B=420, C=5, D=120, E=190, F=458, G=16, holes=6,
         jA=190, jB=42, jC=95, jD=14.9, jE=15.0, jF=50, jG=120, jH=20, K=19,
         amin=35, amax=260),
    dict(size=630, item=185309, B=545, C=7, D=135, E=240, F=586, G=16, holes=6,
         jA=190, jB=42, jC=95, jD=14.9, jE=15.0, jF=50, jG=120, jH=20, K=19,
         amin=50, amax=350),
]


DIFFICULTY_INDICES = {
    "easy": [0, 1, 2, 3],
    "medium": [4, 5, 6, 7],
    "hard": [8, 9, 10, 11],
}


def _catalog_range(key, difficulty):
    vals = [CATALOG_ROWS[i][key] for i in DIFFICULTY_INDICES[difficulty]]
    return (min(vals), max(vals))


def _ranges(key):
    return {d: _catalog_range(key, d) for d in ("easy", "medium", "hard")}


CATALOG_SOURCE = (
    "RÖHM lathe-chuck catalogue, DURO-M cylindrical centre mount DIN 6350 "
    "table p.3048 (PDF p.26)"
)
JAW_SOURCE = (
    "RÖHM lathe-chuck catalogue, DURO-M outward stepped jaw BB table "
    "p.3060 (PDF p.32)"
)
RANGE_SOURCE = (
    "RÖHM lathe-chuck catalogue, DURO-M chucking ranges A1 table p.3044 "
    "(PDF p.22)"
)


PARAM_SPEC = {
    "catalog_index": dict(
        desc="Index of one complete official DURO-M DIN 6350 catalogue row",
        unit="row",
        range={"easy": (0, 3), "medium": (4, 7), "hard": (8, 11)},
        choices=DIFFICULTY_INDICES,
        coverage=list(range(12)),
        integer=True,
        source=CATALOG_SOURCE,
        askable=True,
    ),
    "catalog_item": dict(desc="RÖHM three-jaw chuck item number", unit="item",
        range=_ranges("item"), refine=True, integer=True, source=CATALOG_SOURCE),
    "outer_dia_A": dict(desc="Chuck outside diameter, catalogue size A", unit="mm",
        range=_ranges("size"), refine=True, source=CATALOG_SOURCE, askable=True),
    "register_dia_B": dict(desc="Rear H6 centering recess diameter B", unit="mm",
        range=_ranges("B"), refine=True, source=CATALOG_SOURCE, askable=True),
    "register_depth_C": dict(desc="Rear centering recess depth C", unit="mm",
        range=_ranges("C"), refine=True, source=CATALOG_SOURCE),
    "height_D": dict(desc="Chuck axial body height D", unit="mm",
        range=_ranges("D"), refine=True, source=CATALOG_SOURCE, askable=True),
    "bore_E": dict(desc="Through-hole diameter E", unit="mm",
        range=_ranges("E"), refine=True, source=CATALOG_SOURCE, askable=True),
    "bolt_circle_F": dict(desc="Rear mounting bolt-circle diameter F", unit="mm",
        range=_ranges("F"), refine=True, source=CATALOG_SOURCE),
    "mount_thread_G": dict(desc="Nominal mounting thread diameter G", unit="mm",
        range=_ranges("G"), refine=True, source=CATALOG_SOURCE),
    "mount_hole_count": dict(desc="Number of catalogued mounting holes", unit="count",
        range=_ranges("holes"), refine=True, integer=True, source=CATALOG_SOURCE),
    "jaw_length_A": dict(desc="Outward stepped jaw BB length A", unit="mm",
        range=_ranges("jA"), refine=True, source=JAW_SOURCE, askable=True),
    "jaw_width_B": dict(desc="Outward stepped jaw BB width B", unit="mm",
        range=_ranges("jB"), refine=True, source=JAW_SOURCE),
    "jaw_height_C": dict(desc="Outward stepped jaw BB height C", unit="mm",
        range=_ranges("jC"), refine=True, source=JAW_SOURCE, askable=True),
    "jaw_serration_D": dict(
        desc="Jaw BB underside serration dimension D; drives the scroll "
             "thread pitch",
        unit="mm",
        range=_ranges("jD"), refine=True, source=JAW_SOURCE),
    "jaw_tongue_E": dict(
        desc="Jaw BB guide-tongue band dimension E; drives the T-flange "
             "height",
        unit="mm",
        range=_ranges("jE"), refine=True, source=JAW_SOURCE),
    "jaw_step_F": dict(desc="Outward stepped jaw BB dimension F", unit="mm",
        range=_ranges("jF"), refine=True, source=JAW_SOURCE),
    "jaw_step_G": dict(desc="Outward stepped jaw BB dimension G", unit="mm",
        range=_ranges("jG"), refine=True, source=JAW_SOURCE),
    "jaw_step_H": dict(desc="Outward stepped jaw BB dimension H", unit="mm",
        range=_ranges("jH"), refine=True, source=JAW_SOURCE),
    "key_square_K": dict(desc="Chuck-key square K", unit="mm",
        range=_ranges("K"), refine=True, source=CATALOG_SOURCE, askable=True),
    "grip_min_A1": dict(desc="Minimum published A1 external chucking diameter",
        unit="mm", range=_ranges("amin"), refine=True, source=RANGE_SOURCE),
    "grip_max_A1": dict(desc="Maximum published A1 external chucking diameter",
        unit="mm", range=_ranges("amax"), refine=True, source=RANGE_SOURCE),
    "jaw_open_fraction": dict(
        desc="Operating position inside the official A1 chucking range; not a SKU",
        unit="fraction",
        range={"easy": (0.25, 0.55), "medium": (0.12, 0.82), "hard": (0.0, 1.0)},
        source="operating-state fraction within the published A1 range",
        askable=True,
    ),
    "clamp_d": dict(
        desc="Current external gripping diameter derived from A1 range",
        unit="mm",
        range={"easy": (2, 53), "medium": (3, 122), "hard": (6, 350)},
        refine=True,
        source="grip_min_A1 + jaw_open_fraction * (grip_max_A1 - grip_min_A1)",
        askable=True,
    ),
    "has_scallops": dict(
        desc="Characteristic outer-body scallops present below size 400",
        unit="bool",
        range={"easy": (1, 1), "medium": (1, 1), "hard": (0, 1)},
        refine=True,
        integer=True,
        feature=True,
        source="RÖHM catalogue p.3041: from size 400 no scallops due to design",
    ),
}


_ROW_KEYS = {
    "catalog_item": "item",
    "outer_dia_A": "size",
    "register_dia_B": "B",
    "register_depth_C": "C",
    "height_D": "D",
    "bore_E": "E",
    "bolt_circle_F": "F",
    "mount_thread_G": "G",
    "mount_hole_count": "holes",
    "jaw_length_A": "jA",
    "jaw_width_B": "jB",
    "jaw_height_C": "jC",
    "jaw_serration_D": "jD",
    "jaw_tongue_E": "jE",
    "jaw_step_F": "jF",
    "jaw_step_G": "jG",
    "jaw_step_H": "jH",
    "key_square_K": "K",
    "grip_min_A1": "amin",
    "grip_max_A1": "amax",
}


def refine(p: dict, difficulty: str, rng) -> None:
    del difficulty, rng
    row = CATALOG_ROWS[int(p["catalog_index"])]
    for param, key in _ROW_KEYS.items():
        p[param] = row[key]
    p["clamp_d"] = round(
        p["grip_min_A1"]
        + p["jaw_open_fraction"] * (p["grip_max_A1"] - p["grip_min_A1"]),
        3,
    )
    p["has_scallops"] = 1 if p["outer_dia_A"] < 400 else 0


def check(p: dict) -> list[str]:
    bad = []
    idx = int(p["catalog_index"])
    if idx < 0 or idx >= len(CATALOG_ROWS):
        return ["catalog_index must select one of the 12 official DIN 6350 rows"]
    row = CATALOG_ROWS[idx]
    for param, key in _ROW_KEYS.items():
        if p[param] != row[key]:
            bad.append(f"{param} must equal the selected official catalog row")
    if not 0.0 <= p["jaw_open_fraction"] <= 1.0:
        bad.append("jaw_open_fraction must stay within the published A1 range")
    expected_clamp = p["grip_min_A1"] + p["jaw_open_fraction"] * (
        p["grip_max_A1"] - p["grip_min_A1"]
    )
    if abs(p["clamp_d"] - expected_clamp) > 0.002:
        bad.append("clamp_d must be derived from the official A1 limits")
    expected_scallops = 1 if p["outer_dia_A"] < 400 else 0
    if p["has_scallops"] != expected_scallops:
        bad.append("RÖHM catalog: sizes 400 and above have no characteristic scallops")
    if p["bore_E"] >= p["register_dia_B"]:
        bad.append("catalog row requires through-hole E smaller than register B")
    if p["bolt_circle_F"] >= p["outer_dia_A"]:
        bad.append("catalog mounting circle F must lie inside chuck diameter A")

    # geometric validity of the modelled scroll drive (formulas mirror
    # part.py _layout; keep the two in sync)
    A = p["outer_dia_A"]
    x0 = p["clamp_d"] / 2.0
    jA = p["jaw_length_A"]
    if p["clamp_d"] < 0.16 * p["jaw_width_B"]:
        bad.append(
            "clamp_d below 0.16*jaw_width_B: the three 0.26*B-wide jaw noses "
            "would interpenetrate at 120 deg spacing (tip half-width 0.13*B "
            "needs clamp radius > 0.13*B/tan60)")
    sleeve_od = max(p["bore_E"] + 0.06 * A, 0.20 * A)
    guide_inner = max(p["bore_E"] / 2.0 + 0.04 * A, 0.11 * A, sleeve_od / 2.0)
    engaged = min(x0 + jA, 0.5 * A) - max(x0, guide_inner)
    if engaged < 0.30 * jA:
        bad.append(
            "jaw guide engagement below 0.30*jaw_length_A: the T-tongue must "
            "keep at least 30% of the jaw length inside its guideway")
    scroll_id = sleeve_od + 2.0 * max(0.3, 0.0025 * A)
    ridge_w = 0.42 * p["jaw_serration_D"]
    r_si = scroll_id / 2.0 + 0.55 * ridge_w + 0.3
    r_so = 0.36 * A - 0.02 * A
    overlap = min(x0 + jA, r_so) - max(x0, r_si)
    if overlap < 2.0 * p["jaw_serration_D"]:
        bad.append(
            "scroll engagement below two thread pitches: the jaw underside "
            "must overlap the spiral band [r_si, r_so] by >= 2*jaw_serration_D")
    return bad
