"""Catalog-row sampling contract for JW Winco EN 22870 Form L."""

import math

from part import _derived_geometry


_CATALOG_ROWS = {
    40: {
        "wheel_d": 40.0,
        "wheel_width": 18.0,
        "axle_d": 5.0,
        "overall_h": 59.0,
        "plate_l": 42.0,
        "plate_w": 42.0,
        "swivel_offset": 24.0,
        "mount_pitch_x": 30.0,
        "mount_pitch_y": 33.0,
    },
    50: {
        "wheel_d": 50.0,
        "wheel_width": 18.0,
        "axle_d": 6.0,
        "overall_h": 66.0,
        "plate_l": 55.0,
        "plate_w": 55.0,
        "swivel_offset": 21.0,
        "mount_pitch_x": 38.5,
        "mount_pitch_y": 44.0,
    },
    60: {
        "wheel_d": 60.0,
        "wheel_width": 24.0,
        "axle_d": 6.0,
        "overall_h": 83.0,
        "plate_l": 60.0,
        "plate_w": 60.0,
        "swivel_offset": 21.0,
        "mount_pitch_x": 38.5,
        "mount_pitch_y": 48.0,
    },
    80: {
        "wheel_d": 80.0,
        "wheel_width": 24.0,
        "axle_d": 6.0,
        "overall_h": 104.0,
        "plate_l": 60.0,
        "plate_w": 60.0,
        "swivel_offset": 30.0,
        "mount_pitch_x": 38.5,
        "mount_pitch_y": 48.0,
    },
}

_TABLE_SOURCE = (
    "JW Winco EN 22870 metric table, unbraked Form L rows "
    "EN 22870-{40|50|60|80}-G-L-L-ST"
)


PARAM_SPEC = {
    "catalog_size": dict(
        desc="EN 22870 wheel-size row selector",
        unit="mm",
        range={
            "easy": (50, 60),
            "medium": (40, 60),
            "hard": (40, 80),
        },
        choices={
            "easy": [50, 60],
            "medium": [40, 50, 60],
            "hard": [40, 50, 60, 80],
        },
        coverage=[40, 50, 60, 80],
        integer=True,
        source=_TABLE_SOURCE,
        askable=True,
    ),
    "wheel_d": dict(
        desc="Wheel diameter d1",
        unit="mm",
        range={
            "easy": (50.0, 60.0),
            "medium": (40.0, 60.0),
            "hard": (40.0, 80.0),
        },
        refine=True,
        source=_TABLE_SOURCE,
        askable=True,
    ),
    "wheel_width": dict(
        desc="Wheel width b",
        unit="mm",
        range={
            "easy": (18.0, 24.0),
            "medium": (18.0, 24.0),
            "hard": (18.0, 24.0),
        },
        refine=True,
        source=_TABLE_SOURCE,
        askable=True,
    ),
    "axle_d": dict(
        desc="Wheel axle diameter d2",
        unit="mm",
        range={
            "easy": (6.0, 6.0),
            "medium": (5.0, 6.0),
            "hard": (5.0, 6.0),
        },
        refine=True,
        source=_TABLE_SOURCE,
        askable=True,
    ),
    "overall_h": dict(
        desc="Overall caster height h",
        unit="mm",
        range={
            "easy": (66.0, 83.0),
            "medium": (59.0, 83.0),
            "hard": (59.0, 104.0),
        },
        refine=True,
        source=_TABLE_SOURCE,
        askable=True,
    ),
    "plate_l": dict(
        desc="Form L mounting-plate length l1",
        unit="mm",
        range={
            "easy": (55.0, 60.0),
            "medium": (42.0, 60.0),
            "hard": (42.0, 60.0),
        },
        refine=True,
        source=_TABLE_SOURCE,
        askable=True,
    ),
    "plate_w": dict(
        desc="Form L mounting-plate width l2",
        unit="mm",
        range={
            "easy": (55.0, 60.0),
            "medium": (42.0, 60.0),
            "hard": (42.0, 60.0),
        },
        refine=True,
        source=_TABLE_SOURCE,
        askable=True,
    ),
    "swivel_offset": dict(
        desc="Unbraked Form L axle-to-swivel-axis offset l3",
        unit="mm",
        range={
            "easy": (21.0, 21.0),
            "medium": (21.0, 24.0),
            "hard": (21.0, 30.0),
        },
        refine=True,
        source=_TABLE_SOURCE,
        askable=True,
    ),
    "mount_pitch_x": dict(
        desc="Form L mounting-slot pitch m1",
        unit="mm",
        range={
            "easy": (38.5, 38.5),
            "medium": (30.0, 38.5),
            "hard": (30.0, 38.5),
        },
        refine=True,
        source=_TABLE_SOURCE,
        askable=True,
    ),
    "mount_pitch_y": dict(
        desc="Form L mounting-slot pitch m2",
        unit="mm",
        range={
            "easy": (44.0, 48.0),
            "medium": (33.0, 48.0),
            "hard": (33.0, 48.0),
        },
        refine=True,
        source=_TABLE_SOURCE,
        askable=True,
    ),
    "sheet_scale": dict(
        desc="Scale factor for unpublished plate, fork, and bridge thicknesses",
        unit="",
        range={
            "easy": (1.0, 1.0),
            "medium": (0.95, 1.05),
            "hard": (0.90, 1.10),
        },
        source="proportion; benchmark perturbation of unpublished sheet gauge",
        askable=True,
    ),
    "race_scale": dict(
        desc="Scale factor for unpublished external swivel-race envelopes",
        unit="",
        range={
            "easy": (1.0, 1.0),
            "medium": (0.95, 1.05),
            "hard": (0.90, 1.10),
        },
        source="proportion; benchmark perturbation of unpublished race envelope",
        askable=True,
    ),
    "slot_scale": dict(
        desc="Scale factor for unpublished mounting-slot length and width",
        unit="",
        range={
            "easy": (1.0, 1.0),
            "medium": (0.95, 1.05),
            "hard": (0.90, 1.10),
        },
        source="proportion; benchmark perturbation of unpublished slot size",
        askable=True,
    ),
}


def refine(p, difficulty, rng):
    """Copy one complete EN 22870 Form L row into the sampled parameters."""
    _ = difficulty, rng
    row = _CATALOG_ROWS[int(p["catalog_size"])]
    for name, value in row.items():
        p[name] = value


def check(p: dict) -> list[str]:
    bad = []
    row = _CATALOG_ROWS.get(int(p["catalog_size"]))
    if row is None:
        return ["catalog_size is not a published EN 22870 Form L row"]

    for name, expected in row.items():
        if abs(float(p[name]) - expected) > 1e-9:
            bad.append(
                f"{name} must equal {expected} for catalog row "
                f"{int(p['catalog_size'])} (JW Winco EN 22870 table)"
            )

    if not 0.0 < p["mount_pitch_x"] < p["plate_l"]:
        bad.append("m1 must lie inside plate length l1 (EN 22870 geometry)")
    if not 0.0 < p["mount_pitch_y"] < p["plate_w"]:
        bad.append("m2 must lie inside plate width l2 (EN 22870 geometry)")
    if not 0.0 < p["axle_d"] < p["wheel_width"] < p["wheel_d"]:
        bad.append("d2 < b < d1 is required by the EN 22870 wheel geometry")
    if p["overall_h"] <= p["wheel_d"] / 2.0:
        bad.append("overall height h must exceed the wheel radius (geometry)")

    g = _derived_geometry(
        p["wheel_d"],
        p["wheel_width"],
        p["axle_d"],
        p["overall_h"],
        p["plate_l"],
        p["plate_w"],
        p["sheet_scale"],
        p["race_scale"],
        p["slot_scale"],
    )
    angle = math.atan2(p["mount_pitch_y"], p["mount_pitch_x"])
    slot_extent_x = (
        abs(math.cos(angle)) * g["slot_l"] / 2.0
        + abs(math.sin(angle)) * g["slot_w"] / 2.0
    )
    slot_extent_y = (
        abs(math.sin(angle)) * g["slot_l"] / 2.0
        + abs(math.cos(angle)) * g["slot_w"] / 2.0
    )
    slot_margin_x = (
        p["plate_l"] / 2.0
        - p["mount_pitch_x"] / 2.0
        - slot_extent_x
    )
    slot_margin_y = (
        p["plate_w"] / 2.0
        - p["mount_pitch_y"] / 2.0
        - slot_extent_y
    )
    if min(slot_margin_x, slot_margin_y) <= 0.75 * g["plate_t"]:
        bad.append(
            "proportioned mounting slots must retain 0.75 plate thickness "
            "to every outside edge"
        )

    lower_race_bottom = (
        p["overall_h"]
        - g["plate_t"]
        - g["upper_race_h"]
        - 0.25
        - g["lower_race_h"]
    )
    bridge_bottom = lower_race_bottom - g["bridge_t"] + 0.30
    if bridge_bottom <= p["wheel_d"]:
        bad.append(
            "fork bridge must clear the wheel top "
            "(proportion and non-interference)"
        )
    if g["side_clearance"] <= 0.0:
        bad.append("fork side clearance must remain positive (proportion)")
    return bad
