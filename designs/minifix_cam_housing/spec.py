"""Sampling specification for the Häfele Minifix 15 connector housing."""

# Häfele UK catalogue pp. 294--295 order-table rows.  The values are nominal;
# the tables describe the required bore geometry rather than the unlisted
# internal cam pocket.
CATALOG_ROWS = (
    # min. panel t, body Ø, rim?, rim Ø, rim h, A, drilling depth X
    (12.0, 15.0, 1, 16.5, 1.0, 6.0, 9.5),
    (15.0, 15.0, 0, 0.0, 0.0, 7.5, 12.0),
    (16.0, 15.0, 1, 16.5, 1.0, 8.0, 12.5),
    (19.0, 15.0, 1, 16.5, 1.0, 9.5, 14.5),
    (23.0, 15.0, 1, 16.5, 1.0, 11.5, 16.5),
    (29.0, 15.0, 0, 0.0, 0.0, 14.5, 19.5),
    (34.0, 15.0, 1, 16.5, 1.0, 17.0, 22.5),
)

TABLE_SOURCE = "Häfele UK catalogue 14CFC294.pdf and 14CFC295.pdf, pp. 294--295"
PROPORTION = "proportion: catalogue does not dimension casting internals or non-hex drive widths"


PARAM_SPEC = {
    "variant": dict(
        desc="Index of a real Häfele Minifix 15 catalogue row",
        unit="",
        range={"easy": (0, 6), "medium": (0, 6), "hard": (0, 6)},
        choices={"easy": [1], "medium": [0, 1, 2, 3, 4],
                 "hard": [0, 1, 2, 3, 4, 5, 6]},
        integer=True,
        coverage=[0, 1, 2, 3, 4, 5, 6],
        source=TABLE_SOURCE,
    ),
    "body_diameter": dict(
        desc="Press-fit housing body and mounting-bore diameter",
        unit="mm",
        range={"easy": (15.0, 15.0), "medium": (15.0, 15.0), "hard": (15.0, 15.0)},
        coverage=[15.0],
        refine=True,
        askable=True,
        source=TABLE_SOURCE,
    ),
    "min_wood_thickness": dict(
        desc="Minimum panel thickness for the selected order-table row",
        unit="mm",
        range={"easy": (12.0, 16.0), "medium": (12.0, 23.0), "hard": (12.0, 34.0)},
        refine=True,
        coverage=[12.0, 15.0, 16.0, 19.0, 23.0, 29.0, 34.0],
        source=TABLE_SOURCE,
    ),
    "has_rim": dict(
        desc="Whether the seating rim is present on the panel face",
        unit="",
        range={"easy": (0, 1), "medium": (0, 1), "hard": (0, 1)},
        refine=True,
        feature=True,
        coverage=[0, 1],
        source=TABLE_SOURCE,
    ),
    "rim_diameter": dict(
        desc="Outside diameter of the optional seating rim",
        unit="mm",
        range={"easy": (0.0, 16.5), "medium": (0.0, 16.5), "hard": (0.0, 16.5)},
        refine=True,
        source=TABLE_SOURCE,
    ),
    "rim_height": dict(
        desc="Height of the optional seating rim above the panel face",
        unit="mm",
        range={"easy": (0.0, 1.0), "medium": (0.0, 1.0), "hard": (0.0, 1.0)},
        refine=True,
        source=TABLE_SOURCE,
    ),
    "bolt_axis_height": dict(
        desc="Dim. A, panel-face to connecting-bolt axis distance",
        unit="mm",
        range={"easy": (6.0, 8.0), "medium": (6.0, 11.5), "hard": (6.0, 17.0)},
        refine=True,
        askable=True,
        coverage=[6.0, 7.5, 8.0, 9.5, 11.5, 14.5, 17.0],
        source=TABLE_SOURCE,
    ),
    "housing_height": dict(
        desc="Drilling depth X, used as the housing axial-envelope approximation",
        unit="mm",
        range={"easy": (9.5, 12.5), "medium": (9.5, 16.5), "hard": (9.5, 22.5)},
        refine=True,
        askable=True,
        coverage=[9.5, 12.0, 12.5, 14.5, 16.5, 19.5, 22.5],
        source=TABLE_SOURCE + "; using drilling depth X as the casting axial envelope is proportion",
    ),
    "bolt_hole_diameter": dict(
        desc="Mating panel edge-hole diameter, proportionally sizing the hook mouth",
        unit="mm",
        range={"easy": (7.0, 8.0), "medium": (7.0, 8.0), "hard": (7.0, 8.0)},
        choices={"easy": [7.0], "medium": [7.0, 8.0], "hard": [7.0, 8.0]},
        askable=True,
        source="Häfele UK catalogue pp. 294--295: bolt drill hole Ø7 or Ø8 mm; hook-mouth scaling is proportion",
    ),
    "cam_web_thickness": dict(
        desc="Thickness of the unlisted internal C-hook plate and sloped cam web",
        unit="mm",
        range={"easy": (0.9, 1.3), "medium": (0.9, 1.4), "hard": (0.9, 1.6)},
        refine=True,
        source=PROPORTION,
    ),
    "drive_style": dict(
        desc="Simplified top drive: 0 PZ cross, 1 flat-blade slot, 2 SW4 hex socket",
        unit="",
        range={"easy": (0, 2), "medium": (0, 2), "hard": (0, 2)},
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1, 2]},
        integer=True,
        feature=True,
        coverage=[0, 1, 2],
        source="Häfele UK catalogue pp. 294--295: PZ2/PZ3, flat blade, or SW4; cross outline is simplified proportion",
    ),
    "drive_size": dict(
        desc="PZ/flat recess width or SW4 hex width across flats",
        unit="mm",
        range={"easy": (1.7, 1.9), "medium": (1.7, 2.1), "hard": (1.7, 4.0)},
        refine=True,
        coverage=[4.0],
        source="Häfele pp. 294--295 specifies SW4; PZ/flat recess widths are proportion",
    ),
}


def refine(p: dict, difficulty: str, rng) -> None:
    """Expand one real catalogue row into its coupled bore dimensions."""
    row = CATALOG_ROWS[int(p["variant"])]
    (p["min_wood_thickness"], p["body_diameter"], p["has_rim"],
     p["rim_diameter"], p["rim_height"], p["bolt_axis_height"],
     p["housing_height"]) = row
    p["cam_web_thickness"] = round(
        0.28 * (p["housing_height"] - p["bolt_axis_height"]), 2
    )
    if p["drive_style"] == 2:
        p["drive_size"] = 4.0
    else:
        drive_hi = {"easy": 1.9, "medium": 2.1, "hard": 2.3}[difficulty]
        p["drive_size"] = round(float(rng.uniform(1.7, drive_hi)), 2)


def check(p: dict) -> list[str]:
    """Return engineering violations; each statement names its evidence."""
    bad = []
    expected = CATALOG_ROWS[int(p["variant"])]
    actual = (
        p["min_wood_thickness"], p["body_diameter"], p["has_rim"],
        p["rim_diameter"], p["rim_height"], p["bolt_axis_height"],
        p["housing_height"],
    )
    if actual != expected:
        bad.append("variant dimensions do not match its exact Häfele catalogue row")
    if p["body_diameter"] != 15.0:
        bad.append("body_diameter != 15: catalogue pp. 294--295 specifies a Ø15 housing bore")
    if abs(p["bolt_axis_height"] - p["min_wood_thickness"] / 2.0) > 1e-9:
        bad.append("A != t/2: catalogue order rows keep the bolt axis on the panel mid-plane")
    if p["housing_height"] > p["min_wood_thickness"] - 2.0:
        bad.append("X > t-2: catalogue bore must retain at least a 2 mm panel floor")
    hook_depth = p["housing_height"] - p["bolt_axis_height"]
    if not 3.5 <= hook_depth <= 5.5:
        bad.append("X-A outside 3.5..5.5 mm: catalogue rows bound the cam hook path below the bolt axis")
    if p["has_rim"]:
        if (p["rim_diameter"], p["rim_height"]) != (16.5, 1.0):
            bad.append("rim dimensions differ from Ø16.5 × 1 mm: catalogue p. 295")
        if p["rim_diameter"] <= p["body_diameter"]:
            bad.append("rim_diameter <= body_diameter: seating rim must overhang the Ø15 bore")
    elif p["rim_diameter"] != 0.0 or p["rim_height"] != 0.0:
        bad.append("unrimmed order rows have no seating rim: catalogue p. 294")
    if not 0 < p["cam_web_thickness"] < 0.15 * p["body_diameter"]:
        bad.append("cam web is not a thin internal casting feature (proportion)")
    if p["drive_style"] == 2 and p["drive_size"] != 4.0:
        bad.append("SW4 drive is not 4 mm across flats: Häfele catalogue pp. 294--295")
    return bad
