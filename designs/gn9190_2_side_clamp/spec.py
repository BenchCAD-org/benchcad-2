"""Benchmark contract for the Ganter GN 9190.2 side clamp."""

_ROWS = (10.0, 14.0, 18.0)


def _entry(desc, unit, lo, hi, source, **extra):
    entry = {
        "desc": desc,
        "unit": unit,
        "range": {
            "easy": (lo, lo),
            "medium": (lo, hi),
            "hard": (lo, hi),
        },
        "source": source,
    }
    entry.update(extra)
    return entry


PARAM_SPEC = {
    "slot_width": {
        "desc": "catalog size row a",
        "unit": "mm",
        "range": {"easy": (10.0, 10.0), "medium": (10.0, 14.0), "hard": (10.0, 18.0)},
        "choices": {"easy": [10.0], "medium": [10.0, 14.0], "hard": list(_ROWS)},
        "source": "Ganter GN 9190.2 official dimension table, a rows",
        "askable": True,
    },
    "jaw_type": {
        "desc": "jaw contact coding E or P",
        "unit": "choice",
        "range": {"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        "choices": {"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        "source": "Ganter GN 9190.2 coding drawing",
        "askable": True,
    },
    "stroke_coding": {
        "desc": "operating-end coding G or K",
        "unit": "choice",
        "range": {"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        "choices": {"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        "source": "Ganter GN 9190.2 coding drawing",
        "askable": True,
    },
    "serration_count": _entry(
        "number of optional E jaw contact serrations", "count", 9, 13,
        "Ganter GN 9190.2 E contact detail; added teeth are a declared design variation",
        integer=True, askable=True),
    "jaw_angle": _entry(
        "P jaw relief angle", "deg", 60.0, 110.0,
        "Ganter GN 9190.2 P contact drawing; bounded proportion for the relief",
        askable=True),
    "return_spring_gap": _entry(
        "jaw return clearance", "mm", 0.6, 1.6,
        "proportion of the GN 9190.2 pivot clearance",
        askable=True),
    "lever_angle": _entry(
        "K operating lever angle", "deg", -20.0, 20.0,
        "Ganter GN 9190.2 K operating coding; motion range is a declared proportion",
        askable=True),
    "body_chamfer": _entry(
        "housing edge chamfer", "mm", 0.6, 1.8,
        "Ganter GN 9190.2 drawing edge treatment; bounded proportion",
        askable=True),
    "body_edge_radius": _entry(
        "housing edge radius", "mm", 0.2, 1.0,
        "Ganter GN 9190.2 drawing edge treatment; bounded proportion",
        askable=True),
    "jaw_chamfer": _entry(
        "jaw free-end chamfer", "mm", 0.2, 1.2,
        "Ganter GN 9190.2 pivoted jaw detail; bounded proportion",
        askable=True),
    "jaw_edge_radius": _entry(
        "jaw edge radius", "mm", 0.15, 0.8,
        "Ganter GN 9190.2 pivoted jaw detail; bounded proportion",
        askable=True),
    "support_chamfer": _entry(
        "support front chamfer", "mm", 0.2, 1.0,
        "Ganter GN 9190.2 support detail; bounded proportion",
        askable=True),
    "screw_chamfer": _entry(
        "clamping screw nose and socket chamfer", "mm", 0.15, 0.8,
        "Ganter GN 9190.2 clamping screw detail; bounded proportion",
        askable=True),
}


def check(p: dict) -> list[str]:
    bad = []
    if p["slot_width"] not in _ROWS:
        bad.append("slot_width must be one of the official 10, 14, or 18 mm rows")
    if p["jaw_type"] not in (0, 1, "E", "P"):
        bad.append("jaw_type must encode E or P (Ganter coding drawing)")
    if p["stroke_coding"] not in (0, 1, "G", "K"):
        bad.append("stroke_coding must encode G or K (Ganter coding drawing)")
    if not 3 <= int(p["serration_count"]):
        bad.append("serration_count must leave a positive E contact pitch")
    if not 30.0 <= float(p["jaw_angle"]) <= 120.0:
        bad.append("jaw_angle must remain inside the P relief range")
    if float(p["return_spring_gap"]) <= 0.0:
        bad.append("return_spring_gap must be positive for a pivot clearance")
    if not -35.0 <= float(p["lever_angle"]) <= 35.0:
        bad.append("lever_angle must remain inside the K lever motion range")
    for name in ("body_chamfer", "body_edge_radius", "jaw_chamfer", "jaw_edge_radius",
                 "support_chamfer", "screw_chamfer"):
        if float(p[name]) < 0.0:
            bad.append(name + " must be non-negative")
    return bad
