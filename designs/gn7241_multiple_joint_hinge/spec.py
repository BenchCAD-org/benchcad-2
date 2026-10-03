"""Benchmark spec for a GN 7241 multiple-joint hinge in the closed position."""


PARAM_DESC = {
    "l1": "first vertical mounting-seat length",
    "l2": "second mounting-seat pivot reference distance from the first seat",
    "l3": "second mounting-seat local mounting slot length",
    "l4": "second mounting-seat longitudinal length",
    "m1": "main slot pitch on the first mounting seat",
    "m2": "local lower pivot offset / small-hole pitch",
    "m3": "small round-hole pitch on the first mounting seat",
    "m4": "slot pitch on the second mounting seat",
    "m5": "small round-hole pitch on the second mounting seat",
    "h1": "overall mounting-seat width",
    "h2": "central link-pack width",
    "d1": "mounting slot diameter",
    "d2": "small mounting hole diameter",
    "s": "mounting plate thickness",
    "l5": "closed-position horizontal envelope",
    "l6": "closed-position vertical envelope",
    "x": "closed-position horizontal offset between mounting reference and linkage",
    "y": "closed-position vertical offset between mounting reference and linkage",
}


OFFICIAL_75 = {
    "l1": 75.0,
    "l2": 44.5,
    "l3": 30.0,
    "l4": 51.0,
    "m1": 61.0,
    "m2": 8.0,
    "m3": 40.0,
    "m4": 46.0,
    "m5": 28.0,
    "h1": 60.0,
    "h2": 30.0,
    "d1": 6.5,
    "d2": 4.0,
    "s": 7.0,
    "l5": 117.5,
    "l6": 96.7,
    "x": 52.0,
    "y": 29.0,
}


def _scaled(value, lo, hi):
    return {
        "easy": (value, value),
        "medium": (round(value * lo, 2), round(value * hi, 2)),
        "hard": (round(value * 0.88, 2), round(value * 1.14, 2)),
    }


def _source(name):
    return (
        f"GN 7241-AL-75-EL catalog drawing/table symbol {name}; "
        "medium/hard ranges are proportional variants around the official 75 row"
    )


PARAM_SPEC = {
    name: dict(
        desc=f"{PARAM_DESC[name]} ({name} in the GN 7241 drawing/table)",
        unit="mm",
        range=_scaled(value, 0.90, 1.12),
        source=_source(name),
        refine=name != "l1",
        askable=name in {"l1"},
    )
    for name, value in OFFICIAL_75.items()
}


def refine(p: dict, difficulty: str, rng) -> None:
    """Keep the closed hinge kinematic layout coherent while scaling size.

    GN 7241 publishes the official 75 row used here as the anchor.  The Python
    reconstruction depends on the relative positions of slots, pivots, and link
    ends staying synchronized, so non-anchor dimensions are refined from the
    same scale factor rather than sampled independently.
    """
    scale = p["l1"] / OFFICIAL_75["l1"]
    for name, value in OFFICIAL_75.items():
        if name == "l1":
            continue
        p[name] = round(value * scale, 2)


def check(p: dict) -> list[str]:
    bad = []
    if p["m1"] > p["l1"] - 2.0 * p["d1"]:
        bad.append("m1 too large for l1: first mounting slots need edge material")
    if p["m3"] > p["l1"] - 2.0 * p["d2"]:
        bad.append("m3 too large for l1: first small holes need edge material")
    if p["m4"] > p["h1"] - 2.0 * p["d1"]:
        bad.append("m4 too large for h1: second mounting slots need side material")
    if p["m5"] > p["h1"] - 2.0 * p["d2"]:
        bad.append("m5 too large for h1: second small holes need side material")
    if p["d2"] >= p["d1"]:
        bad.append("d2 >= d1: small round holes must remain smaller than obround slots")
    if p["h2"] >= p["h1"] * 0.75:
        bad.append("h2 too large for h1: central link pack must fit between mounting-seat outer bands")
    if p["h2"] <= p["d1"] * 3.0:
        bad.append("h2 too small for d1: linkage pack needs material around pivot collars")
    if p["s"] <= p["d2"]:
        bad.append("s <= d2: mounting plate thickness must stay plausible around small holes")
    if p["l3"] <= p["d1"] * 2.0:
        bad.append("l3 <= 2*d1: obround slots need visible straight length")
    if p["l2"] <= p["m5"]:
        bad.append("l2 <= m5: second mounting-seat pivot reference must exceed the local hole pitch")
    if p["x"] <= p["h2"]:
        bad.append("x <= h2: closed hinge horizontal offset must clear the link-pack width")
    if p["l5"] <= p["x"] + p["m5"]:
        bad.append("l5 <= x + m5: closed horizontal envelope must include the rear linkage")
    if p["l6"] <= p["l1"]:
        bad.append("l6 <= l1: vertical envelope must exceed the first mounting-seat length")
    if p["y"] <= p["m2"] + p["d1"]:
        bad.append("y too small: lower linkage reference would collide with the mounting features")
    return bad
