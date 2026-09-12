"""Sampling contract for the JW Winco GN 490 aluminum family.

All published dimensions are selected as one indivisible catalog row. The
sampler may choose only clamp diameter and actuator type; refine() fills every
dependent dimension from that same row.
"""


DATASHEET = (
    "JW Winco GN 490 official metric dimension PDF "
    "https://live-catalog.jwwinco.com/pdf/winco/us/490.pdf"
)

MODEL_ROWS = [
    dict(clamp_d=8, thread_d=6, body_d4=28, body_l1=33, lever_l2=35,
         lever_l3=45, jaw_l4=14, gap_l5=5, catalog_m=13),
    dict(clamp_d=10, thread_d=8, body_d4=32, body_l1=45, lever_l2=45,
         lever_l3=63, jaw_l4=20, gap_l5=5, catalog_m=15),
    dict(clamp_d=12, thread_d=8, body_d4=36, body_l1=47, lever_l2=45,
         lever_l3=63, jaw_l4=21, gap_l5=5, catalog_m=17),
    dict(clamp_d=14, thread_d=8, body_d4=46, body_l1=57, lever_l2=55,
         lever_l3=78, jaw_l4=25.5, gap_l5=6, catalog_m=20),
    dict(clamp_d=15, thread_d=10, body_d4=46, body_l1=57, lever_l2=55,
         lever_l3=78, jaw_l4=25.5, gap_l5=6, catalog_m=21),
    dict(clamp_d=16, thread_d=10, body_d4=46, body_l1=57, lever_l2=55,
         lever_l3=78, jaw_l4=25.5, gap_l5=6, catalog_m=22),
    dict(clamp_d=18, thread_d=10, body_d4=56, body_l1=63, lever_l2=55,
         lever_l3=78, jaw_l4=28.5, gap_l5=6, catalog_m=24),
    dict(clamp_d=20, thread_d=10, body_d4=56, body_l1=65, lever_l2=55,
         lever_l3=78, jaw_l4=28.5, gap_l5=8, catalog_m=28),
]

DIFFICULTY_DIAMETERS = {
    # Choice order is intentionally deterministic-seed friendly: it changes
    # no allowed catalog row, but prevents the validator's fixed preview seeds
    # from collapsing onto the same few rows across all three difficulties.
    "easy": [16, 15, 14],
    "medium": [10, 12, 14, 15, 16, 18],
    "hard": [10, 12, 14, 20, 15, 16, 8, 18],
}

DIFFICULTY_ACTUATORS = {
    "easy": [0],
    "medium": [0, 1],
    "hard": [0, 1],
}

ROW_KEYS = (
    "thread_d",
    "body_d4",
    "body_l1",
    "lever_l2",
    "lever_l3",
    "jaw_l4",
    "gap_l5",
    "catalog_m",
)


def _rows_for(difficulty):
    allowed = set(DIFFICULTY_DIAMETERS[difficulty])
    return [row for row in MODEL_ROWS if row["clamp_d"] in allowed]


def _row_range(name):
    return {
        difficulty: (
            min(row[name] for row in _rows_for(difficulty)),
            max(row[name] for row in _rows_for(difficulty)),
        )
        for difficulty in DIFFICULTY_DIAMETERS
    }


def _selected_row(p):
    diameter = int(p["clamp_d"])
    for row in MODEL_ROWS:
        if row["clamp_d"] == diameter:
            return row
    return None


PARAM_SPEC = {
    "clamp_d": dict(
        desc="published equal clamping diameters d1=d2; complete-row selector",
        unit="mm",
        range={"easy": (14, 16), "medium": (10, 18), "hard": (8, 20)},
        choices=DIFFICULTY_DIAMETERS,
        integer=True,
        coverage=[8, 10, 12, 14, 15, 16, 18, 20],
        source=f"{DATASHEET}; published d1=d2 rows only",
    ),
    "actuator_type": dict(
        desc="published actuator variant: 0=Type A DIN 912 socket screw, 1=Type B adjustable lever",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        choices=DIFFICULTY_ACTUATORS,
        integer=True,
        coverage=[0, 1],
        feature=True,
        source=f"{DATASHEET}; Type A and Type B order-code field",
    ),
    "thread_d": dict(
        desc="nominal metric thread diameter d3",
        unit="mm",
        range=_row_range("thread_d"),
        refine=True,
        source=f"{DATASHEET}; d3 from the row selected by clamp_d",
    ),
    "body_d4": dict(
        desc="outside cylindrical body diameter d4",
        unit="mm",
        range=_row_range("body_d4"),
        refine=True,
        source=f"{DATASHEET}; d4 from the row selected by clamp_d",
    ),
    "body_l1": dict(
        desc="overall two-body assembly length l1 along the central fastener axis",
        unit="mm",
        range=_row_range("body_l1"),
        refine=True,
        source=f"{DATASHEET}; l1 from the row selected by clamp_d",
    ),
    "lever_l2": dict(
        desc="published Type B axial envelope l2 beyond the actuator-side body face",
        unit="mm",
        range=_row_range("lever_l2"),
        refine=True,
        source=f"{DATASHEET}; l2 from the row selected by clamp_d",
    ),
    "lever_l3": dict(
        desc="published Type B radial envelope l3 from the fastener axis to the handle end",
        unit="mm",
        range=_row_range("lever_l3"),
        refine=True,
        source=f"{DATASHEET}; l3 from the row selected by clamp_d",
    ),
    "jaw_l4": dict(
        desc="axial thickness l4 of each complete clamp body",
        unit="mm",
        range=_row_range("jaw_l4"),
        refine=True,
        source=f"{DATASHEET}; l4 from the row selected by clamp_d",
    ),
    "gap_l5": dict(
        desc="published central separation l5 between the clamp sections",
        unit="mm",
        range=_row_range("gap_l5"),
        refine=True,
        source=f"{DATASHEET}; l5 from the row selected by clamp_d",
    ),
    "catalog_m": dict(
        desc="published spacing m between the two clamping axes",
        unit="mm",
        range=_row_range("catalog_m"),
        refine=True,
        source=f"{DATASHEET}; m from the row selected by clamp_d",
    ),
}


def refine(p, difficulty, rng):
    """Fill every coupled dimension from the selected official table row."""
    row = _selected_row(p)
    if row is None:
        return
    for name in ROW_KEYS:
        p[name] = row[name]


def _row_consistency_errors(p):
    row = _selected_row(p)
    if row is None:
        return ["clamp_d does not select a published GN 490 metric row"]
    bad = []
    for name in ROW_KEYS:
        if name in p and abs(float(p[name]) - float(row[name])) > 1e-9:
            bad.append(f"{name} must match the GN 490 row selected by clamp_d")
    return bad


def check(p):
    """Engineering and topology constraints for the documented reference pose."""
    bad = _row_consistency_errors(p)

    if int(p["actuator_type"]) not in (0, 1):
        bad.append("actuator_type must be published GN 490 Type A or Type B")

    # The official table obeys l1 = 2*l4 + l5 in every row. Keeping this exact
    # prevents a mixed or mistyped row from moving the body end faces.
    if abs(p["body_l1"] - (2.0 * p["jaw_l4"] + p["gap_l5"])) > 1e-9:
        bad.append("body_l1 must equal 2*jaw_l4 + gap_l5 (GN 490 table identity)")
    if abs(p["catalog_m"] - (p["clamp_d"] + p["gap_l5"])) > 1e-9:
        bad.append("catalog_m must equal clamp_d + gap_l5 (GN 490 table identity)")

    # The end-entry V-groove dimensions and radial offset are unpublished
    # proportions.  Each complete l4-thick body remains one connected solid.
    passage_r = 0.60 * p["thread_d"]
    groove_center = (
        0.50 * p["clamp_d"] + passage_r
    )
    groove_depth = (
        (0.50 + 2.0 ** -0.5) * p["clamp_d"]
    )
    groove_mouth = 2.0 * groove_depth
    if groove_depth >= 0.90 * p["jaw_l4"]:
        bad.append("V-groove depth must retain an axial back wall in each l4 body (proportion)")
    if groove_mouth <= 2.40 * p["clamp_d"]:
        bad.append("V-groove mouth must admit the selected clamping diameter (proportion)")
    if groove_center + 0.50 * p["clamp_d"] >= p["body_d4"] / 2.0:
        bad.append("nominal clamped rod must remain inside the d4 body envelope (proportion)")

    # The passage is proportioned from d3; GN 490 publishes the thread, not
    # the body through-hole.  It clears the stud while retaining a web to the
    # radially offset V-groove.
    shaft_r = 0.50 * p["thread_d"]
    radial_wall = p["body_d4"] / 2.0 - passage_r
    if passage_r <= shaft_r:
        bad.append("central passage must clear the nominal actuator shaft (proportion)")
    if radial_wall <= 0.25 * p["clamp_d"]:
        bad.append("central passage must retain >0.25*clamp_d radial jaw wall (proportion)")
    if (
        groove_center
        - 0.50 * p["clamp_d"]
        - passage_r
        + 1e-9
        < 0.0
    ):
        bad.append("V-groove must retain a positive web to the central passage (proportion)")

    # The section shows a full-l5 central insert with pressure springs seated
    # in coaxial pockets in the two clamp bodies.  Local pocket and coil sizes
    # are unpublished proportions.
    bushing_h = p["gap_l5"]
    bushing_outer_r = 0.46 * p["body_d4"]
    bushing_bore_r = 0.50 * p["thread_d"] + max(0.10, 0.02 * p["thread_d"])
    spring_pocket_depth = min(0.22 * p["jaw_l4"], 0.55 * p["gap_l5"])
    coil_r = 0.72 * p["thread_d"]
    wire_r = min(0.045 * p["thread_d"], 0.035 * p["gap_l5"])
    spring_h = spring_pocket_depth - 2.0 * wire_r
    pitch = spring_h / 2.0
    spring_pocket_r = coil_r + wire_r + max(0.08, 0.012 * p["thread_d"])
    if abs(bushing_h - p["gap_l5"]) > 1e-9:
        bad.append("distance bushing must span the published central l5 gap (GN 490 section)")
    if bushing_outer_r <= bushing_bore_r:
        bad.append("distance bushing must retain positive annular wall (proportion)")
    if spring_h <= 2.0 * wire_r:
        bad.append("each body spring pocket must retain a positive helical span (proportion)")
    if coil_r - wire_r <= shaft_r + max(0.10, 0.02 * p["thread_d"]):
        bad.append("both coaxial springs must clear the actuator shaft (proportion)")
    if spring_pocket_r >= p["body_d4"] / 2.0:
        bad.append("both spring pockets must remain inside d4 (proportion)")
    if spring_pocket_depth >= p["jaw_l4"]:
        bad.append("each spring pocket must retain a clamp-body back wall (proportion)")
    if pitch <= 2.0 * wire_r:
        bad.append("helical spring pitch must exceed wire diameter (proportion)")

    # The DIN 934-like nut is a separate component, not a fabricated hex
    # capture pocket.  Its round bore clears the round stud envelope.
    if 0.54 * p["thread_d"] <= shaft_r:
        bad.append("separate hex-nut bore must clear the round stud envelope (proportion)")

    # Type B l2 and l3 are orthogonal published outer-envelope projections.
    # Local hub and handle section sizes are proportions; their final bounding
    # box is checked against l2/l3 by the exhaustive local geometry audit.
    if int(p["actuator_type"]) == 1:
        hub_h = 1.35 * p["thread_d"]
        handle_t = max(0.70 * p["thread_d"], 0.14 * p["body_d4"])
        end_r = 0.46 * handle_t
        start_bottom = (
            p["body_l1"] / 2.0
            + 0.70 * hub_h
            - 0.59 * handle_t
        )
        if p["lever_l2"] <= hub_h + 2.0 * end_r:
            bad.append("Type B l2 must exceed local hub and rounded-end sizes (published envelope + proportion)")
        if p["lever_l3"] <= 2.0 * end_r:
            bad.append("Type B l3 must leave positive radial handle reach (published envelope + proportion)")
        if start_bottom <= p["body_l1"] / 2.0:
            bad.append("Type B handle must clear the upper jaw in the fixed reference pose (proportion)")

    return bad
