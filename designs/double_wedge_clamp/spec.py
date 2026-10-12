"""Sampling contract for the JW Winco GN 920.1 wedge-clamp family."""


CATALOG_ROWS = [
    dict(name="M8-21", d=8.0, b=21.0, h1=15.0, h2=4.5, h3=7.5,
         screw_projection=15.0, m=10.0, force_kn=15.0, torque_nm=25.0),
    dict(name="M8-25", d=8.0, b=25.0, h1=15.0, h2=4.5, h3=7.5,
         screw_projection=15.0, m=12.0, force_kn=15.0, torque_nm=25.0),
    dict(name="M8-32", d=8.0, b=32.0, h1=15.0, h2=4.5, h3=7.5,
         screw_projection=15.0, m=16.0, force_kn=15.0, torque_nm=25.0),
    dict(name="M8-40", d=8.0, b=40.0, h1=15.0, h2=4.5, h3=7.5,
         screw_projection=15.0, m=20.0, force_kn=15.0, torque_nm=25.0),
    dict(name="M8-50", d=8.0, b=50.0, h1=15.0, h2=4.5, h3=7.5,
         screw_projection=15.0, m=30.0, force_kn=15.0, torque_nm=25.0),
    dict(name="M12-40", d=12.0, b=40.0, h1=22.0, h2=4.5, h3=11.0,
         screw_projection=21.0, m=20.0, force_kn=30.0, torque_nm=85.0),
    dict(name="M12-50", d=12.0, b=50.0, h1=22.0, h2=4.5, h3=11.0,
         screw_projection=21.0, m=30.0, force_kn=30.0, torque_nm=85.0),
]

DIFFICULTY_ROWS = {
    "easy": [0, 1, 2, 3, 4],
    "medium": [0, 1, 2, 3, 4],
    "hard": [0, 1, 2, 3, 4, 5, 6],
}

DIFFICULTY_TYPES = {
    "easy": [0],
    "medium": [0, 1],
    "hard": [0, 1, 2],
}

ROW_FIELDS = (
    "d",
    "b",
    "h1",
    "h2",
    "screw_projection",
    "force_kn",
    "torque_nm",
)


def _row_range(name):
    return {
        difficulty: (
            min(CATALOG_ROWS[index][name] for index in rows),
            max(CATALOG_ROWS[index][name] for index in rows),
        )
        for difficulty, rows in DIFFICULTY_ROWS.items()
    }


def _selected_row(p):
    index = int(p["catalog_row"])
    if index < 0 or index >= len(CATALOG_ROWS):
        return None
    return CATALOG_ROWS[index]


PARAM_SPEC = {
    "catalog_row": dict(
        desc=(
            "complete GN 920.1 catalog row selector: 0=M8-21 through "
            "6=M12-50"
        ),
        unit="",
        range={"easy": (0, 4), "medium": (0, 4), "hard": (0, 6)},
        choices=DIFFICULTY_ROWS,
        coverage=list(range(7)),
        integer=True,
        source="JW Winco GN 920.1 metric table; one index selects one complete row",
    ),
    "jaw_type": dict(
        desc="catalog type: 0=GL smooth, 1=GA M4 attachment holes, 2=RF serrated",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 2)},
        choices=DIFFICULTY_TYPES,
        coverage=[0, 1, 2],
        integer=True,
        source="JW Winco GN 920.1 types GL, GA, and RF",
        feature=True,
    ),
    "d": dict(
        desc="central socket-head screw nominal thread diameter",
        unit="mm",
        range=_row_range("d"),
        source="JW Winco GN 920.1 metric table, selected row d",
        refine=True,
    ),
    "b": dict(
        desc="catalog clamp width perpendicular to jaw travel",
        unit="mm",
        range=_row_range("b"),
        source="JW Winco GN 920.1 metric table, selected row b",
        refine=True,
    ),
    "jaw_span": dict(
        desc="overall span a across the opposed outer clamping faces",
        unit="mm",
        range={"easy": (39.5, 44.5), "medium": (39.5, 44.5), "hard": (34.5, 45.5)},
        source="JW Winco GN 920.1 metric table, selected row and jaw type a min/max",
        refine=True,
    ),
    "h1": dict(
        desc="maximum jaw body height",
        unit="mm",
        range=_row_range("h1"),
        source="JW Winco GN 920.1 metric table, selected row h1 max",
        refine=True,
    ),
    "h2": dict(
        desc="center wedge height above the jaw top plane",
        unit="mm",
        range=_row_range("h2"),
        source="JW Winco GN 920.1 metric table, selected row h2",
        refine=True,
    ),
    "h3": dict(
        desc="GA M4-hole center height; 0 sentinel when the field is inapplicable",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (0.0, 7.5), "hard": (0.0, 11.0)},
        source="JW Winco GN 920.1 type GA drawing/table h3; not sampled for GL/RF",
        refine=True,
    ),
    "screw_projection": dict(
        desc="published maximum screw projection l below the clamp base",
        unit="mm",
        range=_row_range("screw_projection"),
        source="JW Winco GN 920.1 metric table, selected row length l max",
        refine=True,
    ),
    "m": dict(
        desc="GA spacing between the two M4 holes per jaw; 0 when inapplicable",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (0.0, 30.0), "hard": (0.0, 30.0)},
        source="JW Winco GN 920.1 type GA drawing/table m; not sampled for GL/RF",
        refine=True,
    ),
    "force_kn": dict(
        desc="catalog clamping force per jaw, metadata only",
        unit="kN",
        range=_row_range("force_kn"),
        source="JW Winco GN 920.1 metric table, selected row force per jaw",
        refine=True,
    ),
    "torque_nm": dict(
        desc="catalog maximum tightening torque, metadata only",
        unit="N m",
        range=_row_range("torque_nm"),
        source="JW Winco GN 920.1 metric table, selected row maximum torque",
        refine=True,
    ),
}


def refine(p, difficulty, rng):
    row = _selected_row(p)
    if row is None:
        return

    for field in ROW_FIELDS:
        p[field] = row[field]

    if int(p["jaw_type"]) == 1:
        p["h3"] = row["h3"]
        p["m"] = row["m"]
    else:
        p["h3"] = 0.0
        p["m"] = 0.0

    if int(p["jaw_type"]) == 2 and row["d"] == 8.0:
        a_min, a_max = 34.5, 39.5
    elif row["d"] == 8.0:
        a_min, a_max = 39.5, 44.5
    else:
        a_min, a_max = 40.0, 45.5
    p["jaw_span"] = round(float(rng.uniform(a_min, a_max)), 2)


def _row_consistency_errors(p):
    row = _selected_row(p)
    if row is None:
        return ["catalog_row does not select one of the seven GN 920.1 rows"]

    bad = []
    for field in ROW_FIELDS:
        if field in p and abs(float(p[field]) - float(row[field])) > 1e-9:
            bad.append(f"{field} must match complete catalog row {row['name']}")

    if int(p["jaw_type"]) == 1:
        if abs(float(p["h3"]) - row["h3"]) > 1e-9:
            bad.append(f"h3 must match type GA catalog row {row['name']}")
        if abs(float(p["m"]) - row["m"]) > 1e-9:
            bad.append(f"m must match type GA catalog row {row['name']}")
    elif abs(float(p["h3"])) > 1e-9 or abs(float(p["m"])) > 1e-9:
        bad.append("h3 and m must be 0 sentinels for GL/RF, where GA fields do not apply")
    return bad


def check(p):
    bad = _row_consistency_errors(p)
    row = _selected_row(p)
    if row is None:
        return bad

    if int(p["jaw_type"]) == 2 and row["d"] == 8.0:
        a_min, a_max = 34.5, 39.5
    elif row["d"] == 8.0:
        a_min, a_max = 39.5, 44.5
    else:
        a_min, a_max = 40.0, 45.5
    if not a_min <= p["jaw_span"] <= a_max:
        bad.append("jaw_span must remain inside the selected row/type catalog a interval")

    jaw_width = 0.90 * p["d"]
    clearance = max(0.25, 0.025 * p["d"])
    center_gap = p["jaw_span"] - 2.0 * jaw_width
    wedge_top_width = center_gap - 2.0 * clearance
    wedge_bottom_width = max(0.38 * wedge_top_width, 1.30 * p["d"])
    lower_z = 0.14 * p["h1"]
    head_d = 1.35 * p["d"]

    if jaw_width <= 5.0 + 0.20 * p["d"]:
        bad.append("jaw wall behind each 5 mm GA blind hole must remain positive (proportion)")
    if wedge_top_width <= head_d + 2.0 * clearance:
        bad.append("center wedge is too narrow for the screw-head recess and side clearance (proportion)")
    if wedge_top_width <= wedge_bottom_width + 2.0 * clearance:
        bad.append("center wedge must retain a positive outward taper after side clearance (proportion)")
    if p["b"] - 2.0 * clearance <= head_d + 2.0 * clearance:
        bad.append("center wedge depth is too small for screw-head edge material (proportion)")
    if p["h1"] <= p["h2"] + 0.45 * p["d"]:
        bad.append("jaw height must exceed raised wedge height plus low-head screw height (proportion)")

    contact_dx = (wedge_top_width - wedge_bottom_width) / 2.0
    contact_dz = p["h1"] - lower_z
    contact_length = (contact_dx * contact_dx + contact_dz * contact_dz) ** 0.5
    normal_gap = clearance * contact_length / contact_dz
    rail_protrusion = 1.30
    slot_fit = 0.15
    rail_head_width = max(5.00, 0.18 * p["b"])
    slot_y_width = rail_head_width + 2.0 * slot_fit
    if rail_protrusion <= normal_gap + slot_fit:
        bad.append("interlocking rail does not reach through the jaw/wedge face gap (proportion)")
    if slot_y_width >= p["b"] - 2.0 * clearance:
        bad.append("continuous guide slot is too wide in Y for the jaw contact face (proportion)")

    if int(p["jaw_type"]) == 1:
        hole_r = 2.0
        if p["m"] / 2.0 + hole_r >= p["b"] / 2.0:
            bad.append("GA M4 holes must retain positive side edge material within b (proportion)")
        if p["h3"] - hole_r <= 0.0 or p["h3"] + hole_r >= p["h1"]:
            bad.append("GA M4 holes must retain positive top/bottom material within h1 (proportion)")
    return bad
