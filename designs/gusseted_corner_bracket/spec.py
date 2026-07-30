"""Benchmark spec for an independent gusseted 90-degree corner bracket."""

from bench2 import Resample


PARAM_SPEC = {
    "leg_length_1": dict(
        desc="first mounting wing length",
        unit="mm",
        range={"easy": (27.0, 29.5), "medium": (26.0, 34.0), "hard": (36.0, 44.0)},
        source="family requirement: small/default/large bracket envelope",
        askable=True,
    ),
    "leg_length_2": dict(
        desc="second mounting wing length",
        unit="mm",
        range={"easy": (34.0, 36.0), "medium": (26.0, 34.0), "hard": (36.0, 44.0)},
        source="family requirement: small/default/large bracket envelope",
        askable=True,
    ),
    "bracket_width": dict(
        desc="common edge width of the bracket",
        unit="mm",
        range={"easy": (11.0, 13.0), "medium": (24.0, 30.0), "hard": (30.0, 36.0)},
        source="family requirement: width centered across the common connection edge",
        askable=True,
    ),
    "plate_thickness": dict(
        desc="thickness of each mounting wing",
        unit="mm",
        range={"easy": (4.2, 4.8), "medium": (2.8, 3.4), "hard": (3.2, 4.0)},
        source="family requirement: conservative cast-like plate thickness range",
        askable=True,
    ),
    "gusset_thickness": dict(
        desc="triangular gusset thickness along the bracket width",
        unit="mm",
        range={"easy": (7.5, 8.5), "medium": (7.0, 9.0), "hard": (8.0, 11.0)},
        source="family requirement: centered gusset thickness",
        askable=True,
    ),
    "gusset_length_1": dict(
        desc="gusset reach along the first wing",
        unit="mm",
        range={"easy": (12.5, 13.5), "medium": (8.0, 13.0), "hard": (10.0, 17.0)},
        source="family requirement: gusset extends into wing 1 without reaching the slot",
        askable=True,
    ),
    "gusset_length_2": dict(
        desc="gusset reach along the second wing",
        unit="mm",
        range={"easy": (12.5, 13.5), "medium": (8.0, 13.0), "hard": (10.0, 17.0)},
        source="family requirement: gusset extends into wing 2 without reaching the slot",
        askable=True,
    ),
    "slot_width": dict(
        desc="slot width",
        unit="mm",
        range={"easy": (5.8, 6.2), "medium": (6.0, 6.8), "hard": (6.4, 7.2)},
        source="family requirement: elongated through-slot width",
        askable=True,
    ),
    "slot_length": dict(
        desc="slot total length",
        unit="mm",
        range={"easy": (13.0, 13.5), "medium": (11.5, 14.0), "hard": (13.5, 16.0)},
        source="family requirement: elongated through-slot length",
        askable=True,
    ),
    "slot_offset_1": dict(
        desc="slot center offset from the first corner edge along leg_length_1",
        unit="mm",
        range={"easy": (20.0, 22.0), "medium": (22.5, 26.0), "hard": (24.0, 32.0)},
        source="family requirement: independent slot placement on wing 1",
        askable=True,
    ),
    "slot_offset_2": dict(
        desc="slot center offset from the second corner edge along leg_length_2",
        unit="mm",
        range={"easy": (26.0, 28.0), "medium": (18.0, 24.0), "hard": (24.0, 32.0)},
        source="family requirement: independent slot placement on wing 2",
        askable=True,
    ),
    "edge_radius": dict(
        desc="outer edge radius",
        unit="mm",
        range={"easy": (0.8, 1.2), "medium": (0.8, 1.1), "hard": (0.9, 1.4)},
        source="conservative cast-like outer-edge rounding",
        askable=True,
    ),
    "gusset_radius": dict(
        desc="gusset root transition radius",
        unit="mm",
        range={"easy": (2.8, 3.2), "medium": (1.5, 2.3), "hard": (1.8, 2.8)},
        source="conservative gusset root rounding",
        askable=True,
    ),
}


DEFAULTS = {
    "leg_length_1": 28.0,
    "leg_length_2": 35.0,
    "bracket_width": 12.0,
    "plate_thickness": 4.5,
    "gusset_thickness": 8.0,
    "gusset_length_1": 13.5,
    "gusset_length_2": 13.5,
    "slot_width": 6.0,
    "slot_length": 13.5,
    "slot_offset_1": 20.0,
    "slot_offset_2": 27.0,
    "edge_radius": 1.0,
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

    if p["gusset_thickness"] <= p["plate_thickness"]:
        bad.append("gusset_thickness <= plate_thickness: gusset must read as a distinct strengthening rib")

    if p["gusset_thickness"] >= p["bracket_width"] - 2.0 * p["edge_radius"]:
        bad.append("gusset_thickness too large for the available bracket width")

    if p["gusset_length_1"] >= p["leg_length_1"] - p["plate_thickness"] - p["edge_radius"]:
        bad.append("gusset_length_1 reaches the free end of wing 1")
    if p["gusset_length_2"] >= p["leg_length_2"] - p["plate_thickness"] - p["edge_radius"]:
        bad.append("gusset_length_2 reaches the free end of wing 2")

    if p["gusset_length_1"] <= p["plate_thickness"] * 2.0:
        bad.append("gusset_length_1 too short: gusset must visibly engage wing 1")
    if p["gusset_length_2"] <= p["plate_thickness"] * 2.0:
        bad.append("gusset_length_2 too short: gusset must visibly engage wing 2")

    if p["slot_length"] <= p["slot_width"] + 2.0:
        bad.append("slot_length must exceed slot_width by enough margin to form a real long hole")

    slot1 = _leg_slot_limit(p["leg_length_1"], p["slot_length"], p["slot_offset_1"], p["plate_thickness"], p["edge_radius"])
    slot2 = _leg_slot_limit(p["leg_length_2"], p["slot_length"], p["slot_offset_2"], p["plate_thickness"], p["edge_radius"])
    if slot1:
        bad.append(slot1)
    if slot2:
        bad.append(slot2)

    if p["slot_offset_1"] <= p["gusset_length_1"] + p["slot_length"] * 0.15:
        bad.append("slot_offset_1 too near the corner: first wing slot would intersect the gusset")
    if p["slot_offset_2"] <= p["gusset_length_2"] + p["slot_length"] * 0.15:
        bad.append("slot_offset_2 too near the corner: second wing slot would intersect the gusset")

    if p["edge_radius"] <= 0 or p["gusset_radius"] <= 0:
        bad.append("radii must be positive")

    if p["edge_radius"] >= min(p["plate_thickness"], p["slot_width"]) * 0.65:
        bad.append("edge_radius too aggressive for the thin wings")

    if p["gusset_radius"] >= min(p["gusset_length_1"], p["gusset_length_2"]) * 0.35:
        bad.append("gusset_radius too aggressive for the gusset envelope")

    if p["plate_thickness"] + p["gusset_thickness"] >= min(p["leg_length_1"], p["leg_length_2"]):
        bad.append("combined thickness envelope exceeds the available leg lengths")

    return bad
