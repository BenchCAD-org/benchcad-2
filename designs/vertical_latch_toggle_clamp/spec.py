"""Benchmark spec for a static GN 851.1-T3 vertical latch toggle clamp."""

from bench2 import Resample


# JW Winco GN 851.1 catalog values, converted from inch to millimetres and
# rounded to 0.1 mm. The submitted assembly is explicitly the five-part T3
# configuration represented by the supplied 851.1-160-T3 STEP reference.
#
# size, a1, a2, b1, b2, b3, b4, b5, d1, d2, h1, h2, l1, l2,
# m1, m2, m3, m4, m5, s
CATALOG_ROWS = [
    (160, 5.1, 24.9, 25.9, 35.1, 21.1, 25.4, 14.0, 4.0, 4.3, 37.1, 9.9, 68.1, 4.6, 22.1, 6.6, 13.0, 6.6, 14.2, 2.0),
    (320, 7.9, 37.1, 36.1, 43.9, 32.0, 37.1, 22.1, 6.0, 6.6, 54.1, 15.0, 105.9, 6.1, 25.4, 8.4, 19.1, 10.4, 20.6, 3.0),
    (700, 13.0, 45.0, 52.1, 54.1, 38.1, 48.5, 25.9, 8.0, 8.4, 67.1, 23.1, 147.1, 7.9, 36.6, 9.9, 32.0, 13.5, 26.9, 3.6),
]

ROWS_BY_SIZE = {row[0]: row for row in CATALOG_ROWS}
SYMBOLS = (
    "a1", "a2", "b1", "b2", "b3", "b4", "b5", "d1", "d2", "h1", "h2",
    "l1", "l2", "m1", "m2", "m3", "m4", "m5", "s",
)
SYMBOL_DESC = {
    "a1": "side-view latch-axis offset",
    "a2": "side-view height to the handle bracket",
    "b1": "mounting base length",
    "b2": "overall base / handle envelope width",
    "b3": "outside fork width",
    "b4": "lower fork-block height",
    "b5": "inside U-bolt / fork spacing",
    "d1": "U-bolt nominal rod diameter",
    "d2": "mounting and adjuster hole diameter",
    "h1": "upper latch pivot height",
    "h2": "lower adjuster datum height",
    "l1": "overall handle length",
    "l2": "small front catch-tab length",
    "m1": "transverse mounting-hole spacing",
    "m2": "mounting-hole edge offset",
    "m3": "longitudinal mounting-hole spacing",
    "m4": "lower fork-hole height",
    "m5": "fork-hole vertical spacing",
    "s": "sheet thickness",
}


def _values(symbol):
    index = SYMBOLS.index(symbol) + 1
    return [row[index] for row in CATALOG_ROWS]


def _ranges(symbol):
    values = _values(symbol)
    return {
        "easy": (values[0], values[0]),
        "medium": (min(values[:2]), max(values[:2])),
        "hard": (min(values), max(values)),
    }


def _source(symbol):
    suffix = "M4 / M6 / M8 nominal diameter" if symbol == "d1" else "inch values converted to mm"
    return f"JW Winco GN 851.1 standard sheet, column {symbol}; {suffix}"


PARAM_SPEC = {
    "clamp_size": dict(
        desc="GN 851.1 catalog size identifier for the static T3 assembly",
        unit="",
        range={"easy": (160, 160), "medium": (160, 320), "hard": (160, 700)},
        source="JW Winco GN 851.1 standard sheet, size identifiers 160 / 320 / 700",
        choices={"easy": [160], "medium": [160, 320], "hard": [160, 320, 700]},
        integer=True,
        coverage=[160, 320, 700],
    ),
    "fit_clearance": dict(
        desc="hidden mating-relief clearance between static assembly components",
        unit="mm",
        range={"easy": (0.08, 0.12), "medium": (0.06, 0.16), "hard": (0.05, 0.20)},
        source="proportion / assembly-fit assumption for undimensioned internal reliefs",
    ),
}

PARAM_SPEC.update(
    {
        symbol: dict(
            desc=f"{SYMBOL_DESC[symbol]} ({symbol} in the GN 851.1 drawing)",
            unit="mm",
            range=_ranges(symbol),
            source=_source(symbol),
            refine=True,
        )
        for symbol in SYMBOLS
    }
)


def _row_for(size):
    try:
        return ROWS_BY_SIZE[int(round(size))]
    except KeyError as exc:
        raise Resample from exc


def refine(p: dict, difficulty: str, rng) -> None:
    row = _row_for(p["clamp_size"])
    for symbol, value in zip(SYMBOLS, row[1:]):
        p[symbol] = float(value)


def check(p: dict) -> list[str]:
    """Drawing-fit relationships used by all three published catalog rows."""
    bad = []
    if p["m3"] > p["b1"] - 2.0 * p["d2"]:
        bad.append("GN 851.1 drawing fit: m3 leaves insufficient base edge material")
    if p["m1"] > p["b2"] - 2.0 * p["d2"]:
        bad.append("GN 851.1 drawing fit: m1 leaves insufficient transverse edge material")
    if p["h1"] <= p["h2"]:
        bad.append("GN 851.1 drawing relation: h1 must remain above h2")
    if p["m4"] <= p["d2"]:
        bad.append("GN 851.1 drawing fit: m4 must leave material below the lower fork hole")
    if p["m4"] + p["m5"] + p["d2"] * 0.5 >= p["b4"]:
        bad.append("GN 851.1 drawing fit: m4/m5 holes do not fit within b4")
    if p["l1"] < p["b1"]:
        bad.append("GN 851.1 drawing relation: l1 must exceed the b1 base length")
    if p["d1"] >= p["d2"]:
        bad.append("T3 fit: d1 must remain smaller than the coaxial d2 guide holes")
    if p["b5"] >= p["b3"]:
        bad.append("GN 851.1 drawing relation: b5 must remain inside b3")
    return bad
