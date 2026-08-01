"""Single-model spec for LBSBB 8-3030 gusseted corner bracket."""


PARAM_SPEC = {
    "leg_length_1": dict(
        desc="L, first wing length from the shared inner corner",
        unit="mm",
        range={"easy": (27.8, 28.2), "medium": (26.0, 30.0), "hard": (24.0, 32.0)},
        source="LBSBB 8-3030 table row; benchmark-adjustable geometry parameter",
        askable=True,
    ),
    "leg_length_2": dict(
        desc="H, second wing length from the shared inner corner",
        unit="mm",
        range={"easy": (34.8, 35.2), "medium": (32.0, 38.0), "hard": (30.0, 42.0)},
        source="LBSBB 8-3030 table row; benchmark-adjustable geometry parameter",
        askable=True,
    ),
    "bracket_width": dict(
        desc="overall width span centered on x=0",
        unit="mm",
        range={"easy": (27.8, 28.2), "medium": (26.0, 30.0), "hard": (24.0, 32.0)},
        source="derived from the L dimension in the 8-3030 drawing; adjustable family geometry parameter",
        askable=True,
    ),
    "plate_thickness": dict(
        desc="T, thickness of each mounting wing",
        unit="mm",
        range={"easy": (4.4, 4.6), "medium": (4.1, 4.9), "hard": (3.9, 5.1)},
        source="LBSBB 8-3030 table row; adjustable family geometry parameter",
        askable=True,
    ),
    "gusset_thickness": dict(
        desc="T1, local gusset thickness along x",
        unit="mm",
        range={"easy": (2.9, 3.1), "medium": (2.6, 3.4), "hard": (2.4, 3.6)},
        source="LBSBB 8-3030 table row; adjustable family geometry parameter",
        askable=True,
    ),
    "gusset_length_1": dict(
        desc="A, gusset reach along wing 1",
        unit="mm",
        range={"easy": (13.4, 13.6), "medium": (12.0, 15.0), "hard": (11.5, 15.5)},
        source="LBSBB 8-3030 merged table cell; adjustable family geometry parameter",
        askable=True,
    ),
    "gusset_length_2": dict(
        desc="A, gusset reach along wing 2",
        unit="mm",
        range={"easy": (13.4, 13.6), "medium": (12.0, 15.0), "hard": (11.5, 15.5)},
        source="LBSBB 8-3030 merged table cell; adjustable family geometry parameter",
        askable=True,
    ),
    "slot_width": dict(
        desc="W, slot width",
        unit="mm",
        range={"easy": (5.9, 6.1), "medium": (5.5, 6.5), "hard": (5.0, 7.0)},
        source="LBSBB 8-3030 table row; adjustable family geometry parameter",
        askable=True,
    ),
    "slot_length": dict(
        desc="A, slot total length",
        unit="mm",
        range={"easy": (13.4, 13.6), "medium": (12.5, 14.5), "hard": (12.0, 15.0)},
        source="LBSBB 8-3030 table row; adjustable family geometry parameter",
        askable=True,
    ),
    "slot_offset_1": dict(
        desc="slot center offset along wing 1",
        unit="mm",
        range={"easy": (14.9, 15.1), "medium": (14.5, 15.5), "hard": (14.0, 16.0)},
        source="benchmark placement rule documented in NOTES.md; adjustable family geometry parameter",
        askable=True,
    ),
    "slot_offset_2": dict(
        desc="slot center offset along wing 2",
        unit="mm",
        range={"easy": (14.9, 15.1), "medium": (14.5, 15.5), "hard": (14.0, 16.0)},
        source="benchmark placement rule documented in NOTES.md; adjustable family geometry parameter",
        askable=True,
    ),
    "panel_mount_holes": dict(
        desc="optional M5 through-holes on the two triangular side panels",
        unit="bool",
        range={"easy": (False, False), "medium": (True, True), "hard": (True, True)},
        choices={"easy": [False], "medium": [True], "hard": [True]},
        source="derived optional feature for the benchmark family; easy keeps the default no-hole model",
        askable=True,
        feature=True,
    ),
    "panel_hole_offset": dict(
        desc="shared in-plane offset for the optional side-panel holes",
        unit="mm",
        range={"easy": (11.8, 12.0), "medium": (8.0, 12.0), "hard": (7.0, 12.0)},
        source="benchmark placement rule for the optional M5 side-panel holes",
        askable=True,
        feature=True,
    ),
    "panel_hole_diameter": dict(
        desc="diameter of each optional side-panel M5 clearance hole",
        unit="mm",
        range={"easy": (4.15, 4.25), "medium": (4.1, 4.3), "hard": (4.0, 4.5)},
        source="M5 clearance-hole benchmark default with adjustable family parameterization",
        askable=True,
        feature=True,
    ),
    "edge_radius": dict(
        desc="R, outer edge radius",
        unit="mm",
        range={"easy": (3.45, 3.55), "medium": (3.2, 3.8), "hard": (3.0, 4.2)},
        source="LBSBB 8-3030 table row; adjustable family geometry parameter",
        askable=True,
    ),
    "gusset_radius": dict(
        desc="R, gusset root transition radius",
        unit="mm",
        range={"easy": (2.95, 3.05), "medium": (2.5, 3.5), "hard": (2.2, 3.8)},
        source="LBSBB 8-3030 table row; adjustable family geometry parameter",
        askable=True,
    ),
}


DEFAULTS = {
    "leg_length_1": 28.0,
    "leg_length_2": 35.0,
    "bracket_width": 28.0,
    "plate_thickness": 4.5,
    "gusset_thickness": 3.0,
    "gusset_length_1": 13.5,
    "gusset_length_2": 13.5,
    "slot_width": 6.0,
    "slot_length": 13.5,
    "slot_offset_1": 15.0,
    "slot_offset_2": 15.0,
    "panel_mount_holes": False,
    "panel_hole_offset": 12.0,
    "panel_hole_diameter": 4.2,
    "edge_radius": 3.5,
    "gusset_radius": 3.0,
}


def _leg_slot_limit(leg_length, slot_length, slot_offset, plate_thickness, edge_radius):
    half = slot_length / 2.0
    if slot_offset - half <= plate_thickness + edge_radius:
        return "slot too close to the corner: slot must clear the gusset and the inner intersection"
    if slot_offset + half >= leg_length - edge_radius:
        return "slot too close to the free end: slot must remain inside the wing outline"
    return None


def check(p: dict) -> list[str]:
    bad = []

    for key, value in DEFAULTS.items():
        if isinstance(value, bool):
            continue
        if p[key] <= 0:
            bad.append(f"{key} must be positive")

    if p["bracket_width"] <= p["slot_width"] + 0.25:
        bad.append("bracket_width must be wider than the slot itself")

    if p["gusset_thickness"] >= p["plate_thickness"]:
        bad.append("gusset_thickness must stay thinner than the mounting wings so it reads as a local rib")

    if p["gusset_thickness"] >= p["bracket_width"] - 2.0 * p["edge_radius"]:
        bad.append("gusset_thickness too large for the available bracket width")

    if p["slot_length"] <= p["slot_width"] + 2.0:
        bad.append("slot_length must exceed slot_width by enough margin to form a real long hole")

    slot1 = _leg_slot_limit(p["leg_length_1"], p["slot_length"], p["slot_offset_1"], p["plate_thickness"], p["edge_radius"])
    slot2 = _leg_slot_limit(p["leg_length_2"], p["slot_length"], p["slot_offset_2"], p["plate_thickness"], p["edge_radius"])
    if slot1:
        bad.append(slot1)
    if slot2:
        bad.append(slot2)

    if p["edge_radius"] <= 0 or p["gusset_radius"] <= 0:
        bad.append("radii must be positive")

    if p["edge_radius"] >= min(p["plate_thickness"], p["slot_width"]) * 0.95:
        bad.append("edge_radius too aggressive for the thin wings")

    if p["gusset_radius"] >= min(p["gusset_length_1"], p["gusset_length_2"]) * 0.35:
        bad.append("gusset_radius too aggressive for the gusset envelope")

    if p["panel_hole_offset"] <= 0:
        bad.append("panel_hole_offset must be positive")
    if p["panel_hole_offset"] < 7.0:
        bad.append("panel_hole_offset too close to the corner for the optional side-panel holes")
    if p["panel_hole_offset"] > 12.0:
        bad.append("panel_hole_offset too far from the corner for the optional side-panel holes")
    if p["panel_hole_diameter"] <= 0:
        bad.append("panel_hole_diameter must be positive")
    if p["panel_hole_diameter"] < 4.0 or p["panel_hole_diameter"] > 4.5:
        bad.append("panel_hole_diameter must remain within the M5 clearance-hole envelope")

    if p["plate_thickness"] + p["gusset_thickness"] >= min(p["leg_length_1"], p["leg_length_2"]):
        bad.append("combined thickness envelope exceeds the available leg lengths")

    return bad
