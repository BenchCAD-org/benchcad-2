"""Benchmark spec for GN 866 pneumatic power clamp."""

PARAM_DESC = {
    "size": "main cylinder diameter / catalog size row",
    "max_moment": "maximum moment rating",
    "fs": "clamping force",
    "fh": "holding force",
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
    "w": "auxiliary width reference",
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
}


def _scaled(value, lo, hi):
    return {
        "easy": (value, value),
        "medium": (round(value * lo, 2), round(value * hi, 2)),
        "hard": (round(value * 0.88, 2), round(value * 1.14, 2)),
    }


PARAM_SPEC = {
    name: dict(
        desc=f"{PARAM_DESC[name]} ({name} in the GN 866 drawing/table)",
        unit="mm",
        range=_scaled(value, 0.90, 1.12),
        source="Ganter / JW Winco GN 866 catalog drawing and STEP reference; proportional ranges around the official 20 row",
        refine=name not in {"size", "max_moment", "fs", "fh"},
        askable=name in {"size"},
        feature=name in {"d1", "d2", "d3", "d4", "d5_major", "m1", "m2", "m3", "m4", "m5", "m6"},
    )
    for name, value in OFFICIAL_20.items()
}


def refine(p: dict, difficulty: str, rng) -> None:
    scale = p["size"] / OFFICIAL_20["size"]
    for name, value in OFFICIAL_20.items():
        if name == "size":
            continue
        if name in {"max_moment", "fs", "fh"}:
            continue
        p[name] = round(value * scale, 2)


def check(p: dict) -> list[str]:
    bad = []
    if p["d2"] >= p["d1"]:
        bad.append("d2 must remain smaller than d1")
    if p["m3"] <= 0 or p["m4"] < 0:
        bad.append("bore pitches must be non-negative")
    if p["l2"] < p["l1"]:
        bad.append("l2 should not be smaller than l1 for the full envelope")
    if p["s2"] <= p["s1"] * 0.8:
        bad.append("s2 should stay comparable to the body depth")
    if p["l3"] <= p["d1"]:
        bad.append("l3 too small for the upper clamp arms")
    return bad
