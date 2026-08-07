"""Sampling contract for Elesa+Ganter GN 113.8 T-handle ball lock pins.

Thirty complete rows are transcribed from the manufacturer's 5/2026 GN 113.8
table.  catalog_index is the only independently sampled value; refine() copies
all geometry dimensions from the selected row so nonexistent combinations can
never be generated.
"""

from bench2 import Resample


SOURCE_URL = "https://www.elesa-ganter.com/siteassets/PDF/EN/GN%20113.8.pdf"

# designation, d1, l1, d2, d3, d4, l2, l3, m (all dimensions in millimetres)
CATALOG_ROWS = [
    dict(designation="GN 113.8-5-10", pin_d=5.0, grip_length=10.0, locked_envelope_d=5.5, handle_height=40.0, handle_neck_d=13.5, tip_to_ball_length=6.0, handle_length=25.0, handle_thickness=15.5),
    dict(designation="GN 113.8-5-20", pin_d=5.0, grip_length=20.0, locked_envelope_d=5.5, handle_height=40.0, handle_neck_d=13.5, tip_to_ball_length=6.0, handle_length=25.0, handle_thickness=15.5),
    dict(designation="GN 113.8-5-40", pin_d=5.0, grip_length=40.0, locked_envelope_d=5.5, handle_height=40.0, handle_neck_d=13.5, tip_to_ball_length=6.0, handle_length=25.0, handle_thickness=15.5),
    dict(designation="GN 113.8-5-80", pin_d=5.0, grip_length=80.0, locked_envelope_d=5.5, handle_height=40.0, handle_neck_d=13.5, tip_to_ball_length=6.0, handle_length=25.0, handle_thickness=15.5),
    dict(designation="GN 113.8-6-10", pin_d=6.0, grip_length=10.0, locked_envelope_d=7.0, handle_height=40.0, handle_neck_d=13.5, tip_to_ball_length=7.1, handle_length=25.0, handle_thickness=15.5),
    dict(designation="GN 113.8-6-20", pin_d=6.0, grip_length=20.0, locked_envelope_d=7.0, handle_height=40.0, handle_neck_d=13.5, tip_to_ball_length=7.1, handle_length=25.0, handle_thickness=15.5),
    dict(designation="GN 113.8-6-40", pin_d=6.0, grip_length=40.0, locked_envelope_d=7.0, handle_height=40.0, handle_neck_d=13.5, tip_to_ball_length=7.1, handle_length=25.0, handle_thickness=15.5),
    dict(designation="GN 113.8-6-80", pin_d=6.0, grip_length=80.0, locked_envelope_d=7.0, handle_height=40.0, handle_neck_d=13.5, tip_to_ball_length=7.1, handle_length=25.0, handle_thickness=15.5),
    dict(designation="GN 113.8-8-10", pin_d=8.0, grip_length=10.0, locked_envelope_d=9.5, handle_height=48.0, handle_neck_d=18.0, tip_to_ball_length=8.2, handle_length=31.0, handle_thickness=20.5),
    dict(designation="GN 113.8-8-20", pin_d=8.0, grip_length=20.0, locked_envelope_d=9.5, handle_height=48.0, handle_neck_d=18.0, tip_to_ball_length=8.2, handle_length=31.0, handle_thickness=20.5),
    dict(designation="GN 113.8-8-40", pin_d=8.0, grip_length=40.0, locked_envelope_d=9.5, handle_height=48.0, handle_neck_d=18.0, tip_to_ball_length=8.2, handle_length=31.0, handle_thickness=20.5),
    dict(designation="GN 113.8-8-70", pin_d=8.0, grip_length=70.0, locked_envelope_d=9.5, handle_height=48.0, handle_neck_d=18.0, tip_to_ball_length=8.2, handle_length=31.0, handle_thickness=20.5),
    dict(designation="GN 113.8-8-100", pin_d=8.0, grip_length=100.0, locked_envelope_d=9.5, handle_height=48.0, handle_neck_d=18.0, tip_to_ball_length=8.2, handle_length=31.0, handle_thickness=20.5),
    dict(designation="GN 113.8-10-15", pin_d=10.0, grip_length=15.0, locked_envelope_d=12.0, handle_height=48.0, handle_neck_d=18.0, tip_to_ball_length=9.6, handle_length=31.0, handle_thickness=20.5),
    dict(designation="GN 113.8-10-30", pin_d=10.0, grip_length=30.0, locked_envelope_d=12.0, handle_height=48.0, handle_neck_d=18.0, tip_to_ball_length=9.6, handle_length=31.0, handle_thickness=20.5),
    dict(designation="GN 113.8-10-50", pin_d=10.0, grip_length=50.0, locked_envelope_d=12.0, handle_height=48.0, handle_neck_d=18.0, tip_to_ball_length=9.6, handle_length=31.0, handle_thickness=20.5),
    dict(designation="GN 113.8-10-80", pin_d=10.0, grip_length=80.0, locked_envelope_d=12.0, handle_height=48.0, handle_neck_d=18.0, tip_to_ball_length=9.6, handle_length=31.0, handle_thickness=20.5),
    dict(designation="GN 113.8-10-120", pin_d=10.0, grip_length=120.0, locked_envelope_d=12.0, handle_height=48.0, handle_neck_d=18.0, tip_to_ball_length=9.6, handle_length=31.0, handle_thickness=20.5),
    dict(designation="GN 113.8-12-20", pin_d=12.0, grip_length=20.0, locked_envelope_d=14.5, handle_height=58.0, handle_neck_d=24.0, tip_to_ball_length=10.6, handle_length=36.5, handle_thickness=27.5),
    dict(designation="GN 113.8-12-50", pin_d=12.0, grip_length=50.0, locked_envelope_d=14.5, handle_height=58.0, handle_neck_d=24.0, tip_to_ball_length=10.6, handle_length=36.5, handle_thickness=27.5),
    dict(designation="GN 113.8-12-100", pin_d=12.0, grip_length=100.0, locked_envelope_d=14.5, handle_height=58.0, handle_neck_d=24.0, tip_to_ball_length=10.6, handle_length=36.5, handle_thickness=27.5),
    dict(designation="GN 113.8-12-120", pin_d=12.0, grip_length=120.0, locked_envelope_d=14.5, handle_height=58.0, handle_neck_d=24.0, tip_to_ball_length=10.6, handle_length=36.5, handle_thickness=27.5),
    dict(designation="GN 113.8-16-30", pin_d=16.0, grip_length=30.0, locked_envelope_d=19.0, handle_height=58.0, handle_neck_d=24.0, tip_to_ball_length=14.0, handle_length=36.5, handle_thickness=27.5),
    dict(designation="GN 113.8-16-80", pin_d=16.0, grip_length=80.0, locked_envelope_d=19.0, handle_height=58.0, handle_neck_d=24.0, tip_to_ball_length=14.0, handle_length=36.5, handle_thickness=27.5),
    dict(designation="GN 113.8-16-150", pin_d=16.0, grip_length=150.0, locked_envelope_d=19.0, handle_height=58.0, handle_neck_d=24.0, tip_to_ball_length=14.0, handle_length=36.5, handle_thickness=27.5),
    dict(designation="GN 113.8-20-50", pin_d=20.0, grip_length=50.0, locked_envelope_d=25.0, handle_height=80.0, handle_neck_d=34.0, tip_to_ball_length=20.5, handle_length=46.5, handle_thickness=38.0),
    dict(designation="GN 113.8-20-100", pin_d=20.0, grip_length=100.0, locked_envelope_d=25.0, handle_height=80.0, handle_neck_d=34.0, tip_to_ball_length=20.5, handle_length=46.5, handle_thickness=38.0),
    dict(designation="GN 113.8-20-150", pin_d=20.0, grip_length=150.0, locked_envelope_d=25.0, handle_height=80.0, handle_neck_d=34.0, tip_to_ball_length=20.5, handle_length=46.5, handle_thickness=38.0),
    dict(designation="GN 113.8-25-50", pin_d=25.0, grip_length=50.0, locked_envelope_d=30.8, handle_height=80.0, handle_neck_d=34.0, tip_to_ball_length=22.0, handle_length=46.5, handle_thickness=38.0),
    dict(designation="GN 113.8-25-150", pin_d=25.0, grip_length=150.0, locked_envelope_d=30.8, handle_height=80.0, handle_neck_d=34.0, tip_to_ball_length=22.0, handle_length=46.5, handle_thickness=38.0),
]

ROWS_BY_DIFFICULTY = {
    "easy": list(range(0, 10)),
    "medium": list(range(10, 20)),
    # Keep all ten hard rows, with the true largest catalog instance at a
    # deterministic preview-extreme draw position.
    "hard": [20, 21, 22, 23, 24, 25, 26, 29, 27, 28],
}

ROW_KEYS = (
    "pin_d",
    "grip_length",
    "locked_envelope_d",
    "handle_height",
    "handle_neck_d",
    "tip_to_ball_length",
    "handle_length",
    "handle_thickness",
)


def _row_range(name):
    return {
        difficulty: (
            min(CATALOG_ROWS[index][name] for index in indices),
            max(CATALOG_ROWS[index][name] for index in indices),
        )
        for difficulty, indices in ROWS_BY_DIFFICULTY.items()
    }


PARAM_SPEC = {
    "catalog_index": dict(
        desc="GN 113.8 source-table row selector (0-29)",
        unit="",
        range={"easy": (0, 9), "medium": (10, 19), "hard": (20, 29)},
        choices=ROWS_BY_DIFFICULTY,
        coverage=list(range(30)),
        integer=True,
        source=f"Elesa+Ganter GN 113.8 datasheet table, 5/2026: {SOURCE_URL}",
    ),
    "pin_d": dict(
        desc="nominal stainless pin diameter d1",
        unit="mm",
        range=_row_range("pin_d"),
        refine=True,
        askable=True,
        source=f"GN 113.8 table column d1 (-0.04/-0.08 tolerance): {SOURCE_URL}",
    ),
    "grip_length": dict(
        desc="usable grip length l1 from locking-ball centreline to handle shoulder",
        unit="mm",
        range=_row_range("grip_length"),
        refine=True,
        askable=True,
        source=f"GN 113.8 table column l1 (+0.6 tolerance): {SOURCE_URL}",
    ),
    "locked_envelope_d": dict(
        desc="overall diameter d2 across the two balls in locking position",
        unit="mm",
        range=_row_range("locked_envelope_d"),
        refine=True,
        askable=True,
        source=f"GN 113.8 drawing and table column d2: {SOURCE_URL}",
    ),
    "handle_height": dict(
        desc="overall T-handle height d3",
        unit="mm",
        range=_row_range("handle_height"),
        refine=True,
        askable=True,
        source=f"GN 113.8 drawing and table column d3: {SOURCE_URL}",
    ),
    "handle_neck_d": dict(
        desc="round handle neck diameter d4",
        unit="mm",
        range=_row_range("handle_neck_d"),
        refine=True,
        askable=True,
        source=f"GN 113.8 drawing and table column d4: {SOURCE_URL}",
    ),
    "tip_to_ball_length": dict(
        desc="distance l2 from pin tip to locking-ball centreline",
        unit="mm",
        range=_row_range("tip_to_ball_length"),
        refine=True,
        askable=True,
        source=f"GN 113.8 drawing and table column l2 (+/-1 tolerance): {SOURCE_URL}",
    ),
    "handle_length": dict(
        desc="T-handle axial envelope length l3",
        unit="mm",
        range=_row_range("handle_length"),
        refine=True,
        askable=True,
        source=f"GN 113.8 drawing and table column l3: {SOURCE_URL}",
    ),
    "handle_thickness": dict(
        desc="T-handle thickness m in the end view",
        unit="mm",
        range=_row_range("handle_thickness"),
        refine=True,
        askable=True,
        source=f"GN 113.8 drawing and table column m: {SOURCE_URL}",
    ),
}


def _selected_row(p):
    index = int(p["catalog_index"])
    if index < 0 or index >= len(CATALOG_ROWS):
        return None
    return CATALOG_ROWS[index]


def refine(p, difficulty, rng):
    _ = rng
    index = int(p["catalog_index"])
    if index not in ROWS_BY_DIFFICULTY[difficulty]:
        raise Resample
    row = CATALOG_ROWS[index]
    for name in ROW_KEYS:
        p[name] = row[name]


def check(p):
    bad = []
    row = _selected_row(p)
    if row is None:
        return ["catalog_index does not select one of the 30 reviewed GN 113.8 rows"]

    for name in ROW_KEYS:
        if name not in p or abs(float(p[name]) - float(row[name])) > 1e-9:
            bad.append(f"{name} must match complete catalog row {row['designation']}")

    if p["locked_envelope_d"] <= p["pin_d"]:
        bad.append("d2 must exceed d1 so both locking balls protrude (GN 113.8 drawing)")
    if p["handle_neck_d"] <= p["locked_envelope_d"]:
        bad.append("d4 must exceed d2 to form the handle shoulder (GN 113.8 table)")
    if p["handle_height"] <= p["handle_neck_d"]:
        bad.append("d3 must exceed d4 for a recognizable T-handle (GN 113.8 drawing)")
    if p["handle_thickness"] <= p["handle_neck_d"]:
        bad.append("m must exceed d4 for the broad handle end view (GN 113.8 table)")
    if p["grip_length"] <= 0.0 or p["tip_to_ball_length"] <= 0.0:
        bad.append("l1 and l2 must be positive catalog dimensions")

    # The modeled pockets must leave a continuous pin core and remain clear of
    # the tip and shoulder.  Ball radius is the documented part.py proportion.
    protrusion = (p["locked_envelope_d"] - p["pin_d"]) / 2.0
    ball_r = max(0.16 * p["pin_d"], 1.15 * protrusion)
    ball_center_r = p["locked_envelope_d"] / 2.0 - ball_r
    if ball_r <= protrusion:
        bad.append("modeled ball radius must exceed visible protrusion (proportion)")
    if 1.03 * ball_r >= ball_center_r + p["pin_d"] / 2.0:
        bad.append("ball pocket would cut through the opposite pin wall (positive-core rule)")
    if ball_r >= min(p["tip_to_ball_length"], p["grip_length"]):
        bad.append("ball sphere would overrun the pin tip or handle shoulder (geometry)")
    return bad
