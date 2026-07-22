"""slotted_din_rail_th35_7_5 benchmark spec."""


MODEL_ROWS = [
    dict(model="DN-R35S-050-4", rail_length=50.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=2),
    dict(model="DN-R35S-100-4", rail_length=100.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=4),
    dict(model="DN-R35S-300-4", rail_length=300.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=12),
    dict(model="DN-R35S-600-4", rail_length=600.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=24),
]

DIFFICULTY_ROWS = {
    "easy": [0, 1],
    "medium": [0, 1, 2],
    "hard": [0, 1, 2, 3],
}


def _row_range(name):
    return {
        diff: (
            min(MODEL_ROWS[i][name] for i in rows),
            max(MODEL_ROWS[i][name] for i in rows),
        )
        for diff, rows in DIFFICULTY_ROWS.items()
    }


def _index_range():
    return {diff: (min(rows), max(rows)) for diff, rows in DIFFICULTY_ROWS.items()}


def _selected_row(p):
    idx = int(p["model_index"])
    if idx < 0 or idx >= len(MODEL_ROWS):
        return None
    return MODEL_ROWS[idx]


PARAM_SPEC = {
    "model_index": dict(
        desc="source table row selector: 0=DN-R35S-050-4, 1=DN-R35S-100-4, 2=DN-R35S-300-4, 3=DN-R35S-600-4",
        unit="",
        range=_index_range(),
        choices=DIFFICULTY_ROWS,
        integer=True,
        source="AutomationDirect DN-R35S precut slotted rail table; each draw selects one complete catalog row",
        askable=True,
    ),
    "rail_length": dict(
        desc="precut rail segment length",
        unit="mm",
        range=_row_range("rail_length"),
        source="AutomationDirect DN-R35S precut length table, selected row only",
        refine=True,
        askable=True,
    ),
    "rail_width": dict(
        desc="TH35 rail outside width",
        unit="mm",
        range=_row_range("rail_width"),
        source="AutomationDirect DN-R35S drawing, 35 mm",
        refine=True,
        askable=True,
    ),
    "rail_height": dict(
        desc="TH35 rail profile height",
        unit="mm",
        range=_row_range("rail_height"),
        source="AutomationDirect DN-R35S drawing, 7.5 mm",
        refine=True,
        askable=True,
    ),
    "rail_thickness": dict(
        desc="steel rail material thickness",
        unit="mm",
        range=_row_range("rail_thickness"),
        source="AutomationDirect DIN rail drawing, 1.0 mm",
        refine=True,
        askable=True,
    ),
    "slot_width": dict(
        desc="mounting slot width",
        unit="mm",
        range=_row_range("slot_width"),
        source="AutomationDirect DN-R35S drawing, 6.3 mm",
        refine=True,
        askable=True,
    ),
    "slot_length": dict(
        desc="mounting slot length",
        unit="mm",
        range=_row_range("slot_length"),
        source="AutomationDirect DN-R35S drawing, 18.0 mm",
        refine=True,
        askable=True,
    ),
    "slot_count": dict(
        desc="number of mounting slots",
        unit="",
        range=_row_range("slot_count"),
        source="AutomationDirect DN-R35S precut table, selected row only",
        integer=True,
        refine=True,
        askable=True,
    ),
    "lip_height": dict(
        desc="raised DIN rail lip/profile height used in the simplified TH35 section",
        unit="mm",
        range={"easy": (3.0, 4.0), "medium": (2.5, 4.5), "hard": (2.0, 5.0)},
        source="modeling proportion inside the sourced 7.5 mm TH35 envelope; not a catalog row dimension",
    ),
    "side_relief": dict(
        desc="visible side relief grooves between center hat and edge lips",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (1, 1)},
        source="visual relief from the DN-R35S top-hat drawing",
        choices={"easy": [0], "medium": [0, 1], "hard": [1]},
        feature=True,
    ),
}


SOURCE_ROW_KEYS = (
    "rail_length",
    "rail_width",
    "rail_height",
    "rail_thickness",
    "slot_width",
    "slot_length",
    "slot_count",
)


def refine(p, difficulty, rng):
    row = _selected_row(p)
    if row is None:
        return
    for key in SOURCE_ROW_KEYS:
        p[key] = row[key]


def _row_consistency_errors(p):
    row = _selected_row(p)
    if row is None:
        return ["model_index does not select a DN-R35S source row"]
    bad = []
    for key in SOURCE_ROW_KEYS:
        if key in p and abs(float(p[key]) - float(row[key])) > 1e-9:
            bad.append(f"{key} must match selected source row {row['model']}")
    return bad


def check(p):
    bad = _row_consistency_errors(p)
    if p["slot_length"] >= p["rail_length"] * 0.55:
        bad.append("slot_length too large for short rail: slot must leave end material")
    pitch = (p["rail_length"] - p["slot_length"]) / (p["slot_count"] + 1)
    if pitch < p["slot_length"] * 0.45:
        bad.append("slot pitch too tight: DN-R35S repeated slots need web between slots")
    if p["slot_width"] >= p["rail_width"] * 0.4:
        bad.append("slot_width too wide: slot must remain a center mounting slot")
    if p["lip_height"] >= p["rail_height"]:
        bad.append("lip_height >= rail_height: lip cannot exceed TH35 profile height")
    return bad
