"""Row-coupled sampling for STAUFF RB+RUK and RB+RUL assemblies."""

# D1,A,L1,H1,H2,G,RUK-H3,H4,RUL-H3,H4 from evidence 05 and 08.
RB_ROWS = {
    1: (25, 30, 40, 73.5, 41, 10, 30, 17.5, 30, 17.5),
    2: (26.9, 30, 40, 73.5, 41, 10, 30, 18.5, 30, 18.5),
    3: (30, 38, 48, 81, 48, 10, 30, 20, 30, 20),
    4: (33.7, 38, 48, 81, 48, 10, 30, 22, 30, 22),
    5: (38, 46, 56, 89, 48, 10, 30, 24, 30, 24),
    6: (42.4, 46, 56, 89, 48, 10, 30, 26.2, 30, 26.2),
    7: (44.5, 52, 62, 100, 55, 10, 35, 27.2, 35, 27.2),
    8: (48.3, 52, 62, 100, 55, 10, 35, 29, 35, 29),
    9: (57, 64, 76, 118, 63, 12, 39, 33.5, 39, 33.5),
    10: (60.3, 64, 76, 118, 63, 12, 39, 35.2, 39, 35.2),
    11: (76.1, 82, 94, 135, 77, 12, 39, 43, 39, 43),
    12: (88.9, 94, 106, 152, 82, 12, 41, 52.5, 39, 54.5),
    13: (108, 120, 136, 190, 105, 16, 49, 62, 47, 64),
    14: (114.3, 120, 136, 190, 105, 16, 49, 65, 47, 67),
    15: (133, 148, 164, 217, 105, 16, 49, 74.5, 47, 76.5),
    16: (139.7, 148, 164, 217, 105, 16, 49, 78, 47, 80),
    17: (159, 176, 192, 247, 105, 16, 51, 87.5, 47, 91.5),
    18: (168.3, 176, 192, 247, 105, 16, 51, 92, 47, 96),
    19: (193.7, 202, 218, 273, 105, 16, 51, 105, 47, 109),
    20: (216, 228, 248, 311, 125, 20, 59, 116, 55, 120),
    21: (219.1, 228, 248, 311, 125, 20, 59, 117.5, 55, 121.5),
    22: (267, 282, 303, 364, 125, 20, 59, 141.5, 55, 145.5),
    23: (273, 282, 302, 364, 125, 20, 59, 144.5, 55, 148.5),
    24: (318, 332, 352, 418, 125, 20, 62, 167, 55, 174),
    25: (323.9, 332, 352, 418, 125, 20, 62, 170, 55, 177),
    26: (355.6, 378, 402, 475, 145, 24, 70, 186, 63, 193),
    27: (368, 378, 402, 475, 145, 24, 70, 192, 63, 199),
    28: (406.4, 428, 452, 526, 145, 24, 70, 211, 63, 218),
    29: (419, 428, 452, 526, 145, 24, 70, 217.5, 63, 224.5),
    30: (508, 530, 554, 627, 145, 24, 70, 262, 63, 269),
    31: (521, 530, 554, 627, 145, 24, 70, 269, 63, 276),
}

# A:(L2,L3,B,H5,H6,H7,D2); evidence 11. RUL gets H7=0 below.
RUK_ROWS = {
    30: (35, 25, 24, 5, 8, 5, 8),
    38: (35, 25, 24, 5, 8, 5, 8),
    46: (35, 25, 24, 5, 8, 5, 8),
    52: (35, 25, 24, 5, 8, 5, 8),
    64: (38, 25, 50, 5, 10, 6, 10),
    82: (38, 25, 50, 5, 10, 6, 10),
    94: (75, 40, 70, 8, 17, 10, 15),
    120: (75, 40, 70, 8, 17, 10, 15),
    148: (75, 40, 70, 8, 17, 10, 15),
    176: (140, 90, 75, 8, 26, 10, 25),
    202: (140, 90, 75, 8, 26, 10, 25),
    228: (140, 90, 75, 8, 26, 10, 25),
    282: (140, 90, 75, 8, 26, 10, 25),
    332: (220, 150, 75, 8, 32, 10, 30),
    378: (220, 150, 75, 8, 32, 10, 30),
    428: (220, 150, 75, 8, 32, 10, 30),
    530: (220, 150, 75, 8, 32, 10, 30),
}
RUL_ROWS = {
    30: (75, 40, 30, 5, 12, 11),
    38: (80, 48, 30, 5, 12, 11),
    46: (90, 56, 30, 5, 12, 11),
    52: (95, 62, 35, 5, 15, 11),
    64: (110, 76, 35, 5, 15, 14),
    82: (135, 94, 35, 5, 15, 14),
    94: (145, 106, 40, 10, 20, 14),
    120: (190, 136, 40, 10, 20, 18),
    148: (220, 164, 40, 10, 20, 18),
    176: (250, 192, 50, 12, 25, 18),
    202: (270, 218, 50, 12, 25, 18),
    228: (315, 248, 50, 12, 25, 22),
    282: (370, 302, 50, 12, 25, 22),
    332: (420, 352, 60, 15, 30, 22),
    378: (480, 402, 60, 15, 30, 26),
    428: (540, 452, 60, 15, 30, 26),
    530: (640, 554, 60, 15, 30, 26),
}

ROWS_BY_DIFFICULTY = {
    "easy": [9, 10, 11, 12, 13, 14, 15, 16],
    "medium": list(range(3, 26)),
    "hard": list(range(1, 32)),
}
VARIANTS_BY_DIFFICULTY = {"easy": [0], "medium": [0, 1], "hard": [0, 1]}


def _values(variant, row):
    rb = RB_ROWS[row]
    a = rb[1]
    saddle = RUK_ROWS[a] if variant == 0 else RUL_ROWS[a][:5] + (0.0, RUL_ROWS[a][5])
    h3, h4 = rb[6:8] if variant == 0 else rb[8:10]
    return rb[:6] + (h3, h4) + saddle


def _range(index):
    out = {}
    for difficulty, rows in ROWS_BY_DIFFICULTY.items():
        values = [_values(v, r)[index] for v in VARIANTS_BY_DIFFICULTY[difficulty] for r in rows]
        out[difficulty] = (min(values), max(values))
    return out


def _derived(desc, index, source):
    return dict(desc=desc, unit="mm", range=_range(index), refine=True, source=source, askable=True)


PARAM_SPEC = {
    "saddle_variant": dict(
        desc="0=RUK short saddle, 1=RUL long saddle",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        choices=VARIANTS_BY_DIFFICULTY,
        integer=True,
        feature=True,
        coverage=[0, 1],
        source="STAUFF evidence 04-12 and 16-18: discrete product topologies",
    ),
    "catalog_row": dict(
        desc="complete RB D1 table-row selector",
        unit="",
        range={"easy": (9, 16), "medium": (3, 25), "hard": (1, 31)},
        choices=ROWS_BY_DIFFICULTY,
        integer=True,
        askable=True,
        source="STAUFF evidence 05/08 RB table",
    ),
    "d1": _derived("pipe outside diameter D1", 0, "STAUFF evidence 05/08"),
    "a": _derived("U-bolt leg center spacing A", 1, "STAUFF evidence 05/08"),
    "l1": _derived("U-bolt overall width L1", 2, "STAUFF evidence 05/08"),
    "h1": _derived("U-bolt overall height H1", 3, "STAUFF evidence 05/08"),
    "h2": _derived("U-bolt straight height H2", 4, "STAUFF evidence 05/08"),
    "thread_d": _derived("metric thread nominal diameter G", 5, "STAUFF evidence 05/08"),
    "h3": _derived("variant assembly height H3", 6, "STAUFF evidence 05/08 variant column"),
    "h4": _derived("variant assembly height H4", 7, "STAUFF evidence 05/08 variant column"),
    "l2": _derived("saddle overall length L2", 8, "STAUFF evidence 11 RUK / 17 RUL"),
    "l3": _derived("saddle center length L3", 9, "STAUFF evidence 11 RUK / 17 RUL"),
    "b": _derived("saddle width B", 10, "STAUFF evidence 11 RUK / 17 RUL"),
    "h5": _derived("saddle lower thickness H5", 11, "STAUFF evidence 11 RUK / 17 RUL"),
    "h6": _derived("saddle overall thickness H6", 12, "STAUFF evidence 11 RUK / 17 RUL"),
    "h7": _derived(
        "RUK bottom-boss projection H7; zero for RUL", 13, "STAUFF evidence 11 RUK; RUL has no H7"
    ),
    "auxiliary_d": _derived(
        "RUK boss diameter D2 or RUL through-hole diameter D4", 14, "STAUFF evidence 11 D2 / 17 D4"
    ),
}


def refine(p, difficulty, rng):
    del difficulty, rng
    keys = (
        "d1",
        "a",
        "l1",
        "h1",
        "h2",
        "thread_d",
        "h3",
        "h4",
        "l2",
        "l3",
        "b",
        "h5",
        "h6",
        "h7",
        "auxiliary_d",
    )
    for key, value in zip(keys, _values(int(p["saddle_variant"]), int(p["catalog_row"]))):
        p[key] = value


def check(p):
    row = int(p["catalog_row"])
    variant = int(p["saddle_variant"])
    bad = []
    if row not in RB_ROWS:
        return ["catalog_row must select one of 31 STAUFF RB rows"]
    if variant not in (0, 1):
        return ["saddle_variant must be RUK=0 or RUL=1"]
    keys = (
        "d1",
        "a",
        "l1",
        "h1",
        "h2",
        "thread_d",
        "h3",
        "h4",
        "l2",
        "l3",
        "b",
        "h5",
        "h6",
        "h7",
        "auxiliary_d",
    )
    if tuple(p[k] for k in keys) != _values(variant, row):
        bad.append("dimensions must remain one complete RB row joined to matching A saddle row")
    if p["a"] <= p["d1"]:
        bad.append("STAUFF table: A must exceed D1")
    if p["l1"] <= p["a"]:
        bad.append("STAUFF table: L1 must exceed A")
    if p["l2"] <= p["l3"]:
        bad.append("STAUFF saddle table: L2 must exceed L3")
    if p["h6"] <= p["h5"]:
        bad.append("STAUFF saddle table: H6 must exceed H5")
    if p["l1"] != p["a"] + p["thread_d"]:
        bad.append("STAUFF table: L1 leg-center spacing equals clear A plus rod G")
    if p["h4"] != p["h5"] + p["d1"] / 2:
        bad.append("STAUFF table: groove center H4 equals H5 plus D1/2")
    if variant == 0 and p["h7"] <= 0:
        bad.append("STAUFF RUK table: H7 bosses must project below baseline")
    if variant == 1 and p["h7"] != 0:
        bad.append("STAUFF RUL topology has no RUK H7 bosses")
    if p["h1"] <= p["h2"]:
        bad.append("STAUFF table: overall H1 must exceed straight-leg H2")
    return bad
