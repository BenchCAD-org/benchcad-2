"""Catalog coupling and engineering checks for JW Winco GN 586."""

from math import cos, pi

from part import _assembly_dimensions


CATALOG_ROWS = [
    dict(
        designation="1/2 x 13", thread_major_d=12.7, thread_tpi=13,
        d2=26.0, h1=85.0, h2=75.0, h3=37.0, h4=38.0,
        k1=10.0, k2=54.0, k3=34.0, k4=75.0, k5=45.0,
        l1=22.0, l2=32.0, r=32.0, wll_t=1.0,
        lashing_da_n=2000, tightening_torque_nm=100,
    ),
    dict(
        designation="5/8 x 11", thread_major_d=15.875, thread_tpi=11,
        d2=30.0, h1=99.0, h2=85.0, h3=38.0, h4=47.0,
        k1=13.5, k2=56.0, k3=36.0, k4=87.0, k5=47.0,
        l1=24.0, l2=33.0, r=38.0, wll_t=1.5,
        lashing_da_n=3000, tightening_torque_nm=150,
    ),
    dict(
        designation="3/4 x 10", thread_major_d=19.05, thread_tpi=10,
        d2=45.0, h1=127.0, h2=110.0, h3=54.0, h4=56.0,
        k1=16.5, k2=82.0, k3=54.0, k4=113.0, k5=64.0,
        l1=28.0, l2=50.0, r=48.0, wll_t=2.5,
        lashing_da_n=5000, tightening_torque_nm=250,
    ),
    dict(
        designation="7/8 x 9", thread_major_d=22.225, thread_tpi=9,
        d2=45.0, h1=127.0, h2=110.0, h3=52.0, h4=58.0,
        k1=16.5, k2=82.0, k3=54.0, k4=113.0, k5=64.0,
        l1=27.0, l2=50.0, r=48.0, wll_t=2.5,
        lashing_da_n=5000, tightening_torque_nm=300,
    ),
    dict(
        designation="1 x 8", thread_major_d=25.4, thread_tpi=8,
        d2=45.0, h1=143.0, h2=125.0, h3=64.0, h4=61.0,
        k1=16.5, k2=82.0, k3=54.0, k4=130.0, k5=78.0,
        l1=41.0, l2=50.0, r=48.0, wll_t=4.0,
        lashing_da_n=8000, tightening_torque_nm=400,
    ),
]

DIFFICULTY_ROWS = {
    "easy": [1, 2],
    "medium": [0, 1, 2, 3],
    "hard": [0, 1, 2, 3, 4],
}

ROW_KEYS = (
    "thread_major_d", "thread_tpi", "d2", "h1", "h2", "h3", "h4",
    "k1", "k2", "k3", "k4", "k5", "l1", "l2", "r", "wll_t",
    "lashing_da_n", "tightening_torque_nm",
)


def _row_range(name):
    return {
        difficulty: (
            min(CATALOG_ROWS[index][name] for index in indices),
            max(CATALOG_ROWS[index][name] for index in indices),
        )
        for difficulty, indices in DIFFICULTY_ROWS.items()
    }


def _selector_range():
    return {
        difficulty: (min(indices), max(indices))
        for difficulty, indices in DIFFICULTY_ROWS.items()
    }


def _entry(name, desc, unit="mm", askable=False, source=None):
    return dict(
        desc=desc,
        unit=unit,
        range=_row_range(name),
        source=source or "JW Winco GN 586 official inch table, selected row only",
        refine=True,
        askable=askable,
    )


PARAM_SPEC = {
    "catalog_row": dict(
        desc=(
            "complete GN 586 row: 0=1/2 x 13, 1=5/8 x 11, "
            "2=3/4 x 10, 3=7/8 x 9, 4=1 x 8"
        ),
        unit="",
        range=_selector_range(),
        choices=DIFFICULTY_ROWS,
        integer=True,
        coverage=[0, 1, 2, 3, 4],
        source="JW Winco GN 586 official inch table; one selector fills one complete row",
    ),
    "thread_major_d": _entry(
        "thread_major_d",
        "nominal thread major diameter converted from the printed inch designation",
        askable=True,
        source="GN 586 printed d1 designation; exact 25.4 mm per inch conversion",
    ),
    "thread_tpi": _entry(
        "thread_tpi",
        "catalog threads per inch controlling the modeled 60-degree helix",
        unit="1/in",
        askable=True,
    ),
    "d2": _entry("d2", "catalog dimension d2", askable=True),
    "h1": _entry("h1", "overall upright height h1", askable=True),
    "h2": _entry("h2", "inner opening top elevation h2"),
    "h3": _entry("h3", "inner opening height h3", askable=True),
    "h4": _entry("h4", "inner opening bottom elevation h4"),
    "k1": _entry("k1", "load-ring depth k1", askable=True),
    "k2": _entry("k2", "load-ring outside width k2", askable=True),
    "k3": _entry("k3", "load-ring inside width k3"),
    "k4": _entry("k4", "catalog swivel-envelope dimension k4; metadata only"),
    "k5": _entry("k5", "catalog swivel-envelope dimension k5; metadata only"),
    "l1": _entry("l1", "supplied bolt projection l1", askable=True),
    "l2": _entry("l2", "bracket plan dimension l2"),
    "r": _entry(
        "r",
        "catalog swept clearance radius r; metadata only, no invented motion",
    ),
    "wll_t": _entry(
        "wll_t",
        "catalog nominal WLL metadata; not calculated or certified by the CAD",
        unit="t",
        source="JW Winco GN 586 official load-capacity table, selected row only",
    ),
    "lashing_da_n": _entry(
        "lashing_da_n",
        "catalog maximum lashing-force metadata; not calculated or certified by the CAD",
        unit="daN",
        source="JW Winco GN 586 official load-capacity table, selected row only",
    ),
    "tightening_torque_nm": _entry(
        "tightening_torque_nm",
        "catalog maximum tightening-torque metadata; not a CAD control",
        unit="Nm",
        source="JW Winco GN 586 official assembly table, selected row only",
    ),
    "has_rfid": dict(
        desc="undimensioned representation of the catalog RFID transponder",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (1, 1)},
        choices={"easy": [0], "medium": [0, 1], "hard": [1]},
        integer=True,
        feature=True,
        source="JW Winco GN 586 specification confirms RFID; pocket size is proportion",
    ),
}


def _selected_row(p):
    index = int(p["catalog_row"])
    if index < 0 or index >= len(CATALOG_ROWS):
        return None
    return CATALOG_ROWS[index]


def refine(p, difficulty, rng):
    row = _selected_row(p)
    if row is None:
        return
    for key in ROW_KEYS:
        p[key] = row[key]


def _row_consistency_errors(p):
    row = _selected_row(p)
    if row is None:
        return ["catalog_row does not select one of the five GN 586 rows"]
    bad = []
    for key in ROW_KEYS:
        if key in p and abs(float(p[key]) - float(row[key])) > 1e-9:
            bad.append(
                f"{key} must match complete GN 586 row {row['designation']}"
            )
    return bad


def check(p):
    bad = _row_consistency_errors(p)
    if bad:
        return bad

    # These identities are directly readable from every printed GN 586 row.
    if abs(p["h2"] - p["h3"] - p["h4"]) > 1e-9:
        bad.append("h2 must equal h3 + h4: GN 586 dimension chain")
    if p["k2"] <= p["k3"]:
        bad.append("k2 must exceed k3: GN 586 load ring needs positive section")
    if p["h1"] <= p["h2"]:
        bad.append("h1 must exceed h2: GN 586 load ring needs positive crown")

    # Undimensioned geometry is checked only against declared proportions.
    assembly_clearance = max(0.6, 0.045 * p["k1"])
    if p["d2"] <= 1.25 * p["thread_major_d"] + 2.0 * assembly_clearance:
        bad.append("d2 leaves no positive bracket/bushing clearance (proportion)")
    if p["l2"] <= p["k1"] + 2.0 * assembly_clearance:
        bad.append("l2 leaves no positive ring-to-bracket side clearance (proportion)")
    if p["h1"] - p["h3"] <= 0.38 * p["thread_major_d"]:
        bad.append("bolt head cannot fit above the mounting plane (proportion)")
    if 1.32 * p["thread_major_d"] >= p["k3"]:
        bad.append("proportioned bolt head does not clear the GN 586 ring opening")
    if p["l1"] <= 0.5 * p["thread_major_d"]:
        bad.append("supplied bolt projection is non-physical for this model (proportion)")
    if p["has_rfid"] not in (0, 1):
        bad.append("has_rfid must be a binary documented feature (proportion)")
    pitch = 25.4 / p["thread_tpi"]
    thread_root_d = p["thread_major_d"] - 2.0 * 0.61343 * pitch
    if thread_root_d <= 0.0:
        bad.append("Unified 60-degree thread profile leaves no positive root diameter")
    if p["l1"] < 2.0 * pitch:
        bad.append("threaded projection must contain at least two catalog-pitch turns")

    dims = _assembly_dimensions(
        p["thread_major_d"],
        p["d2"],
        p["h1"],
        p["h2"],
        p["h3"],
        p["h4"],
        p["k1"],
        p["k2"],
        p["k3"],
    )
    plate_wall = (dims["plate_width"] - dims["hole_d"]) / 2.0
    if plate_wall < 1.0:
        bad.append("clevis hole leaves less than 1 mm plate wall (proportion)")
    if dims["axis_d"] <= dims["bore_d"]:
        bad.append("bracket annular post has no positive wall (proportion)")
    if dims["hole_d"] <= dims["axis_d"]:
        bad.append("clevis hole needs positive bracket running clearance")
    # The ring is now a true circular section of diameter k1, so the clevis
    # opening only needs to exceed that diameter rather than the diagonal of
    # the former rectangular extrusion.
    if dims["inside_gap"] <= p["k1"]:
        bad.append("clevis gap does not clear the circular ring section")
    if dims["clevis_z"] != p["h4"]:
        bad.append("rounded bracket pocket must use catalog h4 as its vertical datum")
    open_side_clearance = (
        -dims["axis_d"] / 2.0
        - (dims["ring_x"] + p["k1"] / 2.0)
    )
    if open_side_clearance <= 0.0:
        bad.append("load ring does not clear the vertical bracket axis")
    closed_side_clearance = (
        dims["ring_x"]
        - p["k1"] / 2.0
        - dims["straight_tangent_x"]
    )
    if closed_side_clearance <= 0.0:
        bad.append("load ring does not clear the closed clevis return")
    if dims["bolt_head_base"] <= dims["post_top"]:
        bad.append("bolt head must sit above the bracket post")
    expected_across_flats = (
        dims["bolt_head_corner_d"] * cos(pi / 6.0)
    )
    if abs(expected_across_flats - dims["bolt_head_across_flats"]) > 1e-9:
        bad.append("bolt-head across-flats derivation is inconsistent")
    if dims["bolt_head_across_flats"] <= dims["hole_d"]:
        bad.append("bolt hex across-flats must exceed the bracket hole diameter")
    return bad
