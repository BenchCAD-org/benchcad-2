"""Benchmark spec for GN 866 pneumatic power clamp."""

PARAM_DESC = {
    "size": "main cylinder diameter / catalog size row",
    "max_moment": "maximum clamping moment at 6 bar",
    "fs": "clamping force at r and 6 bar",
    "fh": "holding capacity at r and 6 bar",
    "a": "clamp arm width reference",
    "b": "jaw gap / opening reference",
    "d1": "main slot / hole diameter",
    "d2": "small hole diameter",
    "d3": "side bore diameter",
    "d4": "lower pin / bore diameter",
    "d5_major": "air port thread major diameter",
    "l1": "overall body length",
    "l2": "overall envelope length",
    "l3": "clamp arm length",
    "l4": "lower block length",
    "l5": "front cover thickness",
    "l6": "head length / upper span",
    "m1": "upper stem bore pitch",
    "m2": "upper stem secondary bore pitch",
    "m3": "lower block bore pitch",
    "m4": "head bore pitch",
    "m5": "side offset / width pitch",
    "m6": "air port spacing",
    "r": "reference radius / motion envelope",
    "s1": "body thickness",
    "s2": "overall depth",
    "t": "bridge / plate thickness",
    "w": "clamping-arm angle",
    "length_tolerance": "shared catalog tolerance applied to l1 and l2",
}

OFFICIAL_20 = {
    "size": 20.0,
    "max_moment": 60.0,
    "fs": 630.0,
    "fh": 1150.0,
    "a": 21.0,
    "b": 10.0,
    "d1": 28.0,
    "d2": 5.0,
    "d3": 7.0,
    "d4": 4.1,
    "d5_major": 5.0,
    "l1": 138.0,
    "l2": 160.0,
    "l3": 57.5,
    "l4": 24.5,
    "l5": 5.0,
    "l6": 89.0,
    "m1": 12.0,
    "m2": 7.5,
    "m3": 17.0,
    "m4": 0.0,
    "m5": 22.0,
    "m6": 13.0,
    "r": 48.0,
    "s1": 32.0,
    "s2": 38.0,
    "t": 13.0,
    "w": 66.0,
    "length_tolerance": 0.0,
}

OFFICIAL_ROWS = {
    20.0: OFFICIAL_20,
    32.0: {
        "size": 32.0, "max_moment": 150.0, "fs": 1110.0, "fh": 1520.0,
        "a": 31.0, "b": 12.0, "d1": 40.0, "d2": 6.0, "d3": 9.0,
        "d4": 5.0, "d5_major": 8.0, "l1": 206.0, "l2": 237.0,
        "l3": 91.0, "l4": 31.0, "l5": 6.0, "l6": 72.5, "m1": 18.0,
        "m2": 10.0, "m3": 25.0, "m4": 51.0, "m5": 30.0, "m6": 22.0,
        "r": 67.5, "s1": 42.0, "s2": 42.0, "t": 15.0, "w": 14.0,
        "length_tolerance": 0.0,
    },
    40.0: {
        "size": 40.0, "max_moment": 300.0, "fs": 1800.0, "fh": 2000.0,
        "a": 37.0, "b": 16.0, "d1": 50.0, "d2": 8.0, "d3": 11.0,
        "d4": 6.8, "d5_major": 8.0, "l1": 244.0, "l2": 282.0,
        "l3": 104.0, "l4": 38.0, "l5": 7.5, "l6": 89.5, "m1": 22.0,
        "m2": 13.0, "m3": 30.0, "m4": 62.0, "m5": 37.0, "m6": 25.0,
        "r": 82.5, "s1": 52.0, "s2": 52.0, "t": 18.0, "w": 14.0,
        "length_tolerance": 0.0,
    },
}


def _scaled(value, lo, hi):
    return {
        "easy": (value, value),
        "medium": (round(value * lo, 2), round(value * hi, 2)),
        "hard": (round(value * 0.88, 2), round(value * 1.14, 2)),
    }


_UNITS = {"max_moment": "N·m", "fs": "N", "fh": "N", "w": "deg"}
_ROW_RANGES = {name: (min(row[name] for row in OFFICIAL_ROWS.values()), max(row[name] for row in OFFICIAL_ROWS.values())) for name in OFFICIAL_20}

PARAM_SPEC = {
    name: dict(
        desc=f"{PARAM_DESC[name]} ({name} in the GN 866 drawing/table)",
        unit=_UNITS.get(name, "mm"),
        range={"easy": _ROW_RANGES[name], "medium": _ROW_RANGES[name], "hard": _ROW_RANGES[name]},
        source="Ganter GN 866 official size-20, size-32, and size-40 catalog rows",
        refine=name != "size",
        askable=name == "size",
        **({"choices": {"easy": [20.0], "medium": [20.0, 32.0], "hard": [20.0, 32.0, 40.0]}} if name == "size" else {}),
    )
    for name in OFFICIAL_20
}

PARAM_SPEC["size"]["refine"] = False
PARAM_SPEC["size"]["coverage"] = [20.0, 32.0, 40.0]
PARAM_SPEC["length_tolerance"].update(
    refine=False,
    unit="mm",
    range={"easy": (0.0, 0.0), "medium": (-0.25, 0.0), "hard": (-0.5, 0.0)},
    source="Ganter GN 866 drawing: l1 and l2 are specified with -0.5 mm tolerance",
)


def refine(p: dict, difficulty: str, rng) -> None:
    row = OFFICIAL_ROWS[float(p["size"])]
    for name, value in row.items():
        if name not in {"size", "length_tolerance"}:
            p[name] = value


def check(p: dict) -> list[str]:
    bad = []
    if p["d2"] >= p["d1"]:
        bad.append("d2 must remain smaller than d1 (Ganter GN 866 catalog rows)")
    if p["m3"] <= 0 or p["m4"] < 0:
        bad.append("bore pitches must be non-negative (catalog drawing; m4 is blank for size 20)")
    if p["l2"] < p["l1"]:
        bad.append("l2 should not be smaller than l1 for the full envelope (catalog table)")
    if p["s2"] <= p["s1"] * 0.8:
        bad.append("s2 should stay comparable to s1 (proportion of the catalog section)")
    if p["l3"] <= p["d1"]:
        bad.append("l3 too small for the upper clamp arms (catalog table)")
    if not -0.5 <= p["length_tolerance"] <= 0.0:
        bad.append("length_tolerance must stay within the catalog l1/l2 -0.5 mm tolerance")
    return bad
