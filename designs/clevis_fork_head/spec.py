"""DIN 71752 catalog-row sampling contract for clevis fork heads."""

from part import _thread_core_d


SOURCE_TABLE = (
    "Ganter DIN 71752 Fork Heads, Steel, without Pin, article options table: "
    "https://www.ganternorm.com/en/products/3.6-Moving-Transferring-Connecting-with-"
    "Joints-Couplings-and-Gears/Fork-joints-Fork-heads/DIN-71752-Fork-heads-Steel"
)

# Each tuple-valued dimension is (short, long). All dimensions are millimeters.
DIN_ROWS = {
    4: dict(l1=(8.0, 16.0), d2=4.0, a=8.0, b=4.0, d3=8.0,
            l2=(16.0, 24.0), l3=(21.0, 29.0), l4=6.0),
    5: dict(l1=(10.0, 20.0), d2=5.0, a=10.0, b=5.0, d3=9.0,
            l2=(20.0, 30.0), l3=(26.0, 36.0), l4=7.5),
    6: dict(l1=(12.0, 24.0), d2=6.0, a=12.0, b=6.0, d3=10.0,
            l2=(24.0, 36.0), l3=(31.0, 43.0), l4=9.0),
    8: dict(l1=(16.0, 32.0), d2=8.0, a=16.0, b=8.0, d3=14.0,
            l2=(32.0, 48.0), l3=(42.0, 58.0), l4=12.0),
    10: dict(l1=(20.0, 40.0), d2=10.0, a=20.0, b=10.0, d3=18.0,
             l2=(40.0, 60.0), l3=(52.0, 72.0), l4=15.0),
    12: dict(l1=(24.0, 48.0), d2=12.0, a=24.0, b=12.0, d3=20.0,
             l2=(48.0, 72.0), l3=(62.0, 86.0), l4=18.0),
    14: dict(l1=(28.0, 56.0), d2=14.0, a=28.0, b=14.0, d3=24.0,
             l2=(56.0, 85.0), l3=(72.0, 101.0), l4=22.5),
    16: dict(l1=(32.0, 64.0), d2=16.0, a=32.0, b=16.0, d3=26.0,
             l2=(64.0, 96.0), l3=(83.0, 115.0), l4=24.0),
}

DIFFICULTY_SIZES = {
    "easy": [4, 5, 6],
    "medium": [4, 5, 6, 8, 10, 12],
    "hard": [4, 5, 6, 8, 10, 12, 14, 16],
}

DIFFICULTY_VARIANTS = {
    "easy": [0],
    "medium": [0, 1],
    "hard": [0, 1],
}

REFINED_KEYS = ("l1", "d2", "a", "b", "d3", "l2", "l3", "l4")


def _selected_dimensions(p):
    size = int(p["d1"])
    variant = int(p["is_long"])
    row = DIN_ROWS.get(size)
    if row is None or variant not in (0, 1):
        return None
    return {
        "l1": row["l1"][variant],
        "d2": row["d2"],
        "a": row["a"],
        "b": row["b"],
        "d3": row["d3"],
        "l2": row["l2"][variant],
        "l3": row["l3"][variant],
        "l4": row["l4"],
    }


def _dimension_range(name):
    ranges = {}
    for difficulty, sizes in DIFFICULTY_SIZES.items():
        values = []
        for size in sizes:
            row = DIN_ROWS[size]
            value = row[name]
            if isinstance(value, tuple):
                values.extend(value[i] for i in DIFFICULTY_VARIANTS[difficulty])
            else:
                values.append(value)
        ranges[difficulty] = (min(values), max(values))
    return ranges


PARAM_SPEC = {
    "d1": dict(
        desc="nominal transverse clevis-pin hole diameter d1 (H9)",
        unit="mm",
        range={d: (min(v), max(v)) for d, v in DIFFICULTY_SIZES.items()},
        choices=DIFFICULTY_SIZES,
        coverage=list(DIN_ROWS),
        integer=True,
        source=f"{SOURCE_TABLE}; d1 H9 rows 4, 5, 6, 8, 10, 12, 14, and 16",
    ),
    "is_long": dict(
        desc="catalog length variant selector: 0=short l1/l2/l3 columns, 1=long columns",
        unit="",
        range={d: (min(v), max(v)) for d, v in DIFFICULTY_VARIANTS.items()},
        choices=DIFFICULTY_VARIANTS,
        coverage=[0, 1],
        integer=True,
        source=f"{SOURCE_TABLE}; paired short and long l1, l2, and l3 columns",
    ),
    "l1": dict(
        desc="distance l1 from fork-slot root to transverse pin-hole center",
        unit="mm",
        range=_dimension_range("l1"),
        source=f"{SOURCE_TABLE}; selected size and length variant",
        refine=True,
    ),
    "d2": dict(
        desc="nominal diameter d2 of the simplified right-hand internal thread",
        unit="mm",
        range=_dimension_range("d2"),
        source=f"{SOURCE_TABLE}; standard right-hand thread d2 column",
        refine=True,
    ),
    "a": dict(
        desc="overall fork-head width a in both drawing elevations",
        unit="mm",
        range=_dimension_range("a"),
        source=f"{SOURCE_TABLE}; dimension a",
        refine=True,
    ),
    "b": dict(
        desc="clear gap b between the two symmetric fork arms",
        unit="mm",
        range=_dimension_range("b"),
        source=f"{SOURCE_TABLE}; dimension b",
        refine=True,
    ),
    "d3": dict(
        desc="outside diameter d3 of the threaded cylindrical shank",
        unit="mm",
        range=_dimension_range("d3"),
        source=f"{SOURCE_TABLE}; dimension d3",
        refine=True,
    ),
    "l2": dict(
        desc="distance l2 from shank end to transverse pin-hole center",
        unit="mm",
        range=_dimension_range("l2"),
        source=f"{SOURCE_TABLE}; selected size and length variant",
        refine=True,
    ),
    "l3": dict(
        desc="overall fork-head length l3",
        unit="mm",
        range=_dimension_range("l3"),
        source=f"{SOURCE_TABLE}; selected size and length variant",
        refine=True,
    ),
    "l4": dict(
        desc="axial length l4 of the cylindrical threaded shank",
        unit="mm",
        range=_dimension_range("l4"),
        source=f"{SOURCE_TABLE}; dimension l4",
        refine=True,
    ),
}


def refine(p, difficulty, rng):
    selected = _selected_dimensions(p)
    if selected is None:
        return
    p.update(selected)


def check(p):
    selected = _selected_dimensions(p)
    if selected is None:
        return ["d1/is_long does not select a Ganter DIN 71752 catalog row"]

    bad = []
    for name in REFINED_KEYS:
        if name not in p or abs(float(p[name]) - float(selected[name])) > 1e-9:
            bad.append(f"{name} must match the selected Ganter DIN 71752 catalog row")

    if not p["b"] < p["a"]:
        bad.append("b must be smaller than a so both fork arms have positive thickness (DIN drawing)")
    if abs(p["a"] - 2.0 * p["b"]) > 1e-9:
        bad.append("a must equal 2*b for the selected DIN 71752 table row")
    if p["d1"] >= p["a"]:
        bad.append("d1 must be smaller than head width a to contain the pin hole (DIN drawing)")
    if p["l3"] - p["l2"] <= p["d1"] / 2.0:
        bad.append("l3-l2 must exceed d1/2 to leave material above the pin hole (geometry)")

    fork_root_z = p["l2"] - p["l1"]
    if fork_root_z <= 0.0:
        bad.append("l2-l1 must be positive to locate the fork root above the shank end (DIN drawing)")
    if p["l4"] >= fork_root_z:
        bad.append(
            "l4 must end below l2-l1 to leave the round-to-square shoulder shown in the "
            "DIN 71752 drawing"
        )
    if p["d2"] >= p["d3"]:
        bad.append("thread diameter d2 must be smaller than shank diameter d3 (DIN table)")
    end_chamfer = 0.1 * p["d2"]
    thread_core_d = _thread_core_d(p["d2"])
    if thread_core_d / 2.0 + end_chamfer >= p["d3"] / 2.0 - end_chamfer:
        bad.append(
            "metric coarse thread-core and 0.1*d2 end chamfers must leave a positive "
            "annular end face (tap-drill convention; documented proportion)"
        )
    return bad
