"""Benchmark spec for a GN 851.1 vertical latch toggle clamp."""

from bench2 import Resample


# GN 851.1 vertical latch-type toggle clamps with horizontal mounting base.
# The JW Winco page exposes the table in inch units; values below are converted
# to millimetres (x25.4) except d1, which is M4/M6/M8 nominal diameter.
# The T variant omits the U-bolt latch; T3 includes the U-bolt latch with catch.
#
# size, variant, a1, a2, b1, b2, b3, b4, b5, d1, d2, h1, h2, l1, l2, m1, m2,
# m3, m4, m5, r, s, w1, w2
CATALOG_ROWS = [
    (160, 0, 5.1, 24.9, 25.9, 35.1, 21.1, 25.4, 14.0, 4.0, 4.3, 37.1, 9.9, 68.1, 4.6, 22.1, 6.6, 13.0, 6.6, 14.2, 52.1, 2.0, 32.0, 9.9),
    (160, 1, 5.1, 24.9, 25.9, 35.1, 21.1, 25.4, 14.0, 4.0, 4.3, 37.1, 9.9, 68.1, 4.6, 22.1, 6.6, 13.0, 6.6, 14.2, 52.1, 2.0, 32.0, 9.9),
    (320, 0, 7.9, 37.1, 36.1, 43.9, 32.0, 37.1, 22.1, 6.0, 6.6, 54.1, 15.0, 105.9, 6.1, 25.4, 8.4, 19.1, 10.4, 20.6, 78.0, 3.0, 53.1, 21.1),
    (320, 1, 7.9, 37.1, 36.1, 43.9, 32.0, 37.1, 22.1, 6.0, 6.6, 54.1, 15.0, 105.9, 6.1, 25.4, 8.4, 19.1, 10.4, 20.6, 78.0, 3.0, 53.1, 21.1),
    (700, 0, 13.0, 45.0, 52.1, 54.1, 38.1, 48.5, 25.9, 8.0, 8.4, 67.1, 23.1, 147.1, 7.9, 36.6, 9.9, 32.0, 13.5, 26.9, 102.1, 3.6, 64.0, 24.9),
    (700, 1, 13.0, 45.0, 52.1, 54.1, 38.1, 48.5, 25.9, 8.0, 8.4, 67.1, 23.1, 147.1, 7.9, 36.6, 9.9, 32.0, 13.5, 26.9, 102.1, 3.6, 64.0, 24.9),
]

ROWS_BY_KEY = {(row[0], row[1]): row for row in CATALOG_ROWS}
SYMBOLS = (
    "a1", "a2", "b1", "b2", "b3", "b4", "b5", "d1", "d2", "h1", "h2",
    "l1", "l2", "m1", "m2", "m3", "m4", "m5", "r", "s", "w1", "w2",
)
SYMBOL_DESC = {
    "a1": "side-view offset from the latch rod centerline to the lower catch side",
    "a2": "side-view vertical height from the base datum to the underside of the handle bracket",
    "b1": "top-view mounting base length",
    "b2": "top-view overall base / handle envelope width",
    "b3": "front-view outside fork/base width",
    "b4": "front-view lower adjuster plate height",
    "b5": "front-view lower adjuster plate / inside fork width",
    "d1": "U-bolt latch rod nominal diameter",
    "d2": "mounting hole diameter in the base and lower adjuster plate",
    "h1": "side-view upper latch pivot height",
    "h2": "side-view lower catch offset from the U-bolt centerline",
    "l1": "top-view overall handle length",
    "l2": "small front catch tab length",
    "m1": "top-view transverse mounting-hole spacing",
    "m2": "top-view secondary table offset near the mounting holes",
    "m3": "top-view longitudinal mounting-hole spacing",
    "m4": "front-view lower adjuster hole height from the lower datum",
    "m5": "front-view vertical spacing between lower and upper adjuster hole centers",
    "r": "side-view adjustable range with w2 set to zero",
    "s": "sheet/base plate thickness",
    "w1": "clamp stroke",
    "w2": "adjustable end range at the lower U-bolt/catch",
}


def _symbol_values(symbol):
    idx = SYMBOLS.index(symbol) + 2
    return [row[idx] for row in CATALOG_ROWS[::2]]


def _ranges(symbol):
    values = _symbol_values(symbol)
    return {
        "easy": (values[0], values[0]),
        "medium": (min(values[:2]), max(values[:2])),
        "hard": (min(values), max(values)),
    }


def _source(symbol):
    if symbol == "d1":
        return "GN 851.1 catalog table, column d1 (M4 / M6 / M8 nominal diameter)"
    return f"GN 851.1 catalog table, column {symbol}, inch values converted to mm"


PARAM_SPEC = {
    "clamp_size": dict(
        desc="GN 851.1 catalog size / holding-capacity class",
        unit="N",
        range={"easy": (160, 160), "medium": (160, 320), "hard": (160, 700)},
        source="GN 851.1 catalog table, size rows 160 / 320 / 700",
        choices={"easy": [160], "medium": [160, 320], "hard": [160, 320, 700]},
        integer=True,
        askable=True,
        coverage=[160, 320, 700],
    ),
    "with_u_bolt": dict(
        desc="variant flag retained from GN 851.1: current STEP-matched rebuild samples type T3 with U-bolt latch and catch",
        unit="",
        range={"easy": (1, 1), "medium": (1, 1), "hard": (1, 1)},
        source="GN 851.1 type table: T3 with U-bolt latch and catch; matched to supplied 851.1-160-T3 STEP",
        choices={"easy": [1], "medium": [1], "hard": [1]},
        feature=True,
        coverage=[1],
    ),
    "handle_angle": dict(
        desc="operating handle angle about the upper latch pivot",
        unit="deg",
        range={"easy": (-4.0, 4.0), "medium": (-10.0, 12.0), "hard": (-18.0, 18.0)},
        source="GN 851.1 drawing operating-principle view; numeric angle is a bounded visual proportion",
        askable=False,
    ),
}

PARAM_SPEC.update(
    {
        symbol: dict(
            desc=f"{SYMBOL_DESC[symbol]} ({symbol} in the GN 851.1 table)",
            unit="mm",
            range=_ranges(symbol),
            source=_source(symbol),
            refine=True,
            askable=symbol in {"b1", "b2", "b3", "d1", "d2", "h1", "h2", "l1", "m2", "m3", "m4", "m5", "r", "s", "w1"},
        )
        for symbol in SYMBOLS
    }
)


def _row_for(size, variant):
    key = (int(round(size)), int(round(variant)))
    try:
        return ROWS_BY_KEY[key]
    except KeyError as exc:
        raise Resample from exc


def refine(p: dict, difficulty: str, rng) -> None:
    row = _row_for(p["clamp_size"], p["with_u_bolt"])
    for symbol, value in zip(SYMBOLS, row[2:]):
        p[symbol] = float(value)


def check(p: dict) -> list[str]:
    bad = []
    if p["m3"] > p["b1"] - 2.0 * p["d2"]:
        bad.append("m3 too large for b1: catalog mounting holes need edge material on the base")
    if p["m1"] > p["b2"] - 2.0 * p["d2"]:
        bad.append("m1 too large for b2: catalog mounting holes need side-wall material")
    if p["h1"] <= p["h2"]:
        bad.append("h1 <= h2: upper latch pivot must sit above catch height in the GN 851.1 drawing")
    if p["m4"] <= p["d2"]:
        bad.append("m4 <= d2: lower catch/adjuster hole needs visible material below its center")
    if p["m4"] + p["m5"] + p["d2"] * 0.5 >= p["b4"]:
        bad.append("m4 + m5 too tall for b4: the two lower adjuster holes must fit inside the lower plate")
    if p["l1"] < p["b1"]:
        bad.append("l1 < b1: handle must extend beyond the base footprint per the catalog proportions")
    if p["d1"] > p["b3"] * 0.25:
        bad.append("d1 too large for b3: latch rod would not fit inside the fork/catch width")
    if p["s"] < p["d2"] * 0.30:
        bad.append("s too thin for d2: base plate thickness must remain plausible around mounting holes")
    if p["a1"] >= p["a2"]:
        bad.append("a1 >= a2: U-bolt offset must stay inside the side-view adjustable width")
    if p["b5"] >= p["b3"]:
        bad.append("b5 >= b3: inner fork width must stay below the outside fork/base width")
    if abs(p["handle_angle"]) > 20.0:
        bad.append("handle_angle outside GN 851.1 operating-principle envelope used for the benchmark")
    return bad
