"""slotted_din_rail_th35_7_5 benchmark spec."""


MODEL_ROWS = [
    # AutomationDirect DN-R35S precut slotted rail, every catalogue length.
    # Slot count is length / 25 on every row, and 375 is genuinely absent from
    # the table (it steps 350 -> 400).
    dict(model="DN-R35S-050-4", rail_length=50.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=2,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-075-4", rail_length=75.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=3,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-100-4", rail_length=100.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=4,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-125-4", rail_length=125.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=5,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-150-4", rail_length=150.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=6,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-175-4", rail_length=175.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=7,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-200-4", rail_length=200.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=8,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-225-4", rail_length=225.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=9,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-250-4", rail_length=250.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=10,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-275-4", rail_length=275.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=11,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-300-4", rail_length=300.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=12,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-325-4", rail_length=325.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=13,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-350-4", rail_length=350.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=14,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-400-4", rail_length=400.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=16,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-450-4", rail_length=450.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=18,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-500-4", rail_length=500.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=20,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-550-4", rail_length=550.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=22,
         profile_inner_width=27.0, slot_pitch=25.0),
    dict(model="DN-R35S-600-4", rail_length=600.0, rail_width=35.0, rail_height=7.5,
         rail_thickness=1.0, slot_width=6.3, slot_length=18.0, slot_count=24,
         profile_inner_width=27.0, slot_pitch=25.0),
]

DIFFICULTY_ROWS = {
    "easy": list(range(0, 6)),     # 50 - 175 mm
    "medium": list(range(0, 12)),  # 50 - 325 mm
    "hard": list(range(0, 18)),    # 50 - 600 mm, the whole table
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
        desc=(
            "source table row selector: 0=DN-R35S-050-4, 1=DN-R35S-100-4, "
            "2=DN-R35S-300-4, 3=DN-R35S-600-4"
        ),
        unit="",
        range=_index_range(),
        choices=DIFFICULTY_ROWS,
        integer=True,
        source=(
            "AutomationDirect DN-R35S precut slotted rail table; each draw "
            "selects one complete catalog row"
        ),
    ),
    "rail_length": dict(
        desc="precut rail segment length",
        unit="mm",
        range=_row_range("rail_length"),
        source="AutomationDirect DN-R35S precut length table, selected row only",
        refine=True,
    ),
    "rail_width": dict(
        desc="TH35 rail outside width",
        unit="mm",
        range=_row_range("rail_width"),
        source="AutomationDirect DN-R35S drawing, 35 mm",
        refine=True,
    ),
    "rail_height": dict(
        desc="TH35 rail profile height",
        unit="mm",
        range=_row_range("rail_height"),
        source="AutomationDirect DN-R35S drawing, 7.5 mm",
        refine=True,
    ),
    "rail_thickness": dict(
        desc="steel rail material thickness",
        unit="mm",
        range=_row_range("rail_thickness"),
        source="AutomationDirect DIN rail drawing, 1.0 mm",
        refine=True,
    ),
    "slot_width": dict(
        desc="mounting slot width",
        unit="mm",
        range=_row_range("slot_width"),
        source="AutomationDirect DN-R35S drawing, 6.3 mm",
        refine=True,
    ),
    "slot_length": dict(
        desc="mounting slot length",
        unit="mm",
        range=_row_range("slot_length"),
        source="AutomationDirect DN-R35S drawing, 18.0 mm",
        refine=True,
    ),
    "slot_count": dict(
        desc="number of mounting slots",
        unit="",
        range=_row_range("slot_count"),
        source="AutomationDirect DN-R35S precut table, selected row only",
        integer=True,
        refine=True,
    ),
    "profile_inner_width": dict(
        desc="inside span between TH35 side returns",
        unit="mm",
        range=_row_range("profile_inner_width"),
        source="AutomationDirect DN-R35S steel precut rail cross-section drawing, 27.0 mm",
        refine=True,
    ),
    "slot_pitch": dict(
        desc="center-to-center pitch between repeated mounting slots",
        unit="mm",
        range=_row_range("slot_pitch"),
        source=(
            "AutomationDirect DN-R35S precut length table: slot count scales "
            "one slot per 25 mm segment"
        ),
        refine=True,
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
    "profile_inner_width",
    "slot_pitch",
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
    side_return = (p["rail_width"] - p["profile_inner_width"]) / 2.0
    if abs(side_return - 4.0) > 1e-9:
        bad.append("side return must be 4.0 mm symmetric: DN-R35S cross-section drawing")
    if p["profile_inner_width"] <= p["slot_width"]:
        bad.append("slot_width exceeds center web: DN-R35S slot must fit within 27.0 mm web")
    if p["rail_thickness"] * 2.0 >= p["rail_height"]:
        bad.append("rail_thickness too large: 1.0 mm sheet must fit inside 7.5 mm TH35 height")
    if abs(p["rail_length"] - p["slot_count"] * p["slot_pitch"]) > 1e-9:
        bad.append("rail_length must equal slot_count * 25 mm pitch: DN-R35S table")
    if p["slot_count"] > 1:
        if p["slot_pitch"] <= p["slot_length"]:
            bad.append("slot_pitch leaves no web between slots: DN-R35S repeated M-slot layout")
    end_land = (p["rail_length"] - (p["slot_count"] - 1) * p["slot_pitch"]
                - p["slot_length"]) / 2.0
    if end_land < 0.0:
        bad.append("slot pattern overruns rail end: DN-R35S centered repeated slots")
    return bad
