"""Single-model spec for LBSBB 8-3030 gusseted corner bracket."""


PARAM_SPEC = {
    "leg_length_1": dict(
        desc="L, first wing length from the shared inner corner",
        unit="mm",
        range={"easy": (28.0, 28.0), "medium": (28.0, 28.0), "hard": (28.0, 28.0)},
        source="LBSBB 8-3030 table row",
        askable=True,
    ),
    "leg_length_2": dict(
        desc="H, second wing length from the shared inner corner",
        unit="mm",
        range={"easy": (35.0, 35.0), "medium": (35.0, 35.0), "hard": (35.0, 35.0)},
        source="LBSBB 8-3030 table row",
        askable=True,
    ),
    "bracket_width": dict(
        desc="overall width span centered on x=0",
        unit="mm",
        range={"easy": (28.0, 28.0), "medium": (28.0, 28.0), "hard": (28.0, 28.0)},
        source="derived from the L dimension in the 8-3030 drawing",
        askable=True,
    ),
    "plate_thickness": dict(
        desc="T, thickness of each mounting wing",
        unit="mm",
        range={"easy": (4.5, 4.5), "medium": (4.5, 4.5), "hard": (4.5, 4.5)},
        source="LBSBB 8-3030 table row",
        askable=True,
    ),
    "gusset_thickness": dict(
        desc="T1, local gusset thickness along x",
        unit="mm",
        range={"easy": (3.0, 3.0), "medium": (3.0, 3.0), "hard": (3.0, 3.0)},
        source="LBSBB 8-3030 table row",
        askable=True,
    ),
    "gusset_length_1": dict(
        desc="A, gusset reach along wing 1",
        unit="mm",
        range={"easy": (13.5, 13.5), "medium": (13.5, 13.5), "hard": (13.5, 13.5)},
        source="LBSBB 8-3030 table row (used as local gusset reach)",
        askable=True,
    ),
    "gusset_length_2": dict(
        desc="A, gusset reach along wing 2",
        unit="mm",
        range={"easy": (13.5, 13.5), "medium": (13.5, 13.5), "hard": (13.5, 13.5)},
        source="LBSBB 8-3030 table row (used as local gusset reach)",
        askable=True,
    ),
    "slot_width": dict(
        desc="W, slot width",
        unit="mm",
        range={"easy": (6.0, 6.0), "medium": (6.0, 6.0), "hard": (6.0, 6.0)},
        source="LBSBB 8-3030 table row",
        askable=True,
    ),
    "slot_length": dict(
        desc="A, slot total length",
        unit="mm",
        range={"easy": (13.5, 13.5), "medium": (13.5, 13.5), "hard": (13.5, 13.5)},
        source="LBSBB 8-3030 table row (used as the slot major axis)",
        askable=True,
    ),
    "slot_offset_1": dict(
        desc="slot center offset along wing 1",
        unit="mm",
        range={"easy": (15.0, 15.2), "medium": (15.2, 15.4), "hard": (15.4, 15.6)},
        source="LBSBB 8-3030 table row, interpreted as a safe slot center placement",
        askable=True,
    ),
    "slot_offset_2": dict(
        desc="slot center offset along wing 2",
        unit="mm",
        range={"easy": (15.0, 15.2), "medium": (15.2, 15.4), "hard": (15.4, 15.6)},
        source="LBSBB 8-3030 table row, interpreted as a safe slot center placement",
        askable=True,
    ),
    "panel_mount_holes": dict(
        desc="optional M5 through-holes on the two triangular side panels",
        unit="bool",
        range={"easy": (False, True), "medium": (False, True), "hard": (False, True)},
        choices={"easy": [False, True], "medium": [False, True], "hard": [False, True]},
        source="optional side-panel hole variant validated against the round25 reference geometry",
        askable=True,
        feature=True,
    ),
    "panel_hole_offset": dict(
        desc="shared in-plane offset for the optional side-panel holes",
        unit="mm",
        range={"easy": (7.0, 12.0), "medium": (7.0, 12.0), "hard": (7.0, 12.0)},
        source="shared placement control for the optional round25 side-panel holes",
        askable=True,
        feature=True,
    ),
    "edge_radius": dict(
        desc="R, outer edge radius",
        unit="mm",
        range={"easy": (3.5, 3.5), "medium": (3.5, 3.5), "hard": (3.5, 3.5)},
        source="LBSBB 8-3030 table row",
        askable=True,
    ),
    "gusset_radius": dict(
        desc="R, gusset root transition radius",
        unit="mm",
        range={"easy": (3.5, 3.5), "medium": (3.5, 3.5), "hard": (3.5, 3.5)},
        source="LBSBB 8-3030 table row, used conservatively for the gusset root transition",
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

    if p["plate_thickness"] + p["gusset_thickness"] >= min(p["leg_length_1"], p["leg_length_2"]):
        bad.append("combined thickness envelope exceeds the available leg lengths")

    return bad
