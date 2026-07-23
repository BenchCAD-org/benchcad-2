"""Sampling specification for the Häfele Minifix 15 connector housing."""

# Häfele UK catalogue pp. 294--295 order-table rows.  These are nominal
# installation dimensions, not measurements of the die casting.
CATALOG_ROWS = (
    # min. panel t, bore Ø, rim?, nominal rim Ø, nominal rim h, A, depth X
    (12.0, 15.0, 1, 16.5, 1.0, 6.0, 9.5),
    (15.0, 15.0, 0, 0.0, 0.0, 7.5, 12.0),
    (16.0, 15.0, 1, 16.5, 1.0, 8.0, 12.5),
    # Baseline OEM CAD item 262.25.035: Minifix 15R for 19 mm wood.
    (19.0, 15.0, 1, 16.5, 1.0, 9.5, 14.5),
    (23.0, 15.0, 1, 16.5, 1.0, 11.5, 16.5),
    (29.0, 15.0, 0, 0.0, 0.0, 14.5, 19.5),
    (34.0, 15.0, 1, 16.5, 1.0, 17.0, 22.5),
)

TABLE_SOURCE = "Häfele UK catalogue 14CFC294.pdf and 14CFC295.pdf, pp. 294--295"
OEM_CAD_SOURCE = "Häfele US P-00861332, item 262.25.035 CAD data, STEP AP214 (retrieved 2026-07-23)"
PROPORTION = (
    "proportion: 262.25.035 OEM CAD anchors one 19 mm baseline; "
    "cross-SKU cage transforms are not dimensioned"
)


PARAM_SPEC = {
    "variant": dict(
        desc="Index of a real Häfele Minifix 15 catalogue row",
        unit="",
        range={"easy": (0, 6), "medium": (0, 6), "hard": (0, 6)},
        choices={
            "easy": [1],
            "medium": [0, 1, 2, 3, 4],
            "hard": [0, 1, 2, 3, 4, 5, 6],
        },
        integer=True,
        coverage=[0, 1, 2, 3, 4, 5, 6],
        source=TABLE_SOURCE,
    ),
    "body_diameter": dict(
        desc="Nominal required housing drill-hole diameter",
        unit="mm",
        range={
            "easy": (15.0, 15.0),
            "medium": (15.0, 15.0),
            "hard": (15.0, 15.0),
        },
        coverage=[15.0],
        refine=True,
        askable=True,
        source=TABLE_SOURCE,
    ),
    "min_wood_thickness": dict(
        desc="Minimum panel thickness for the selected order-table row",
        unit="mm",
        range={
            "easy": (12.0, 16.0),
            "medium": (12.0, 23.0),
            "hard": (12.0, 34.0),
        },
        refine=True,
        coverage=[12.0, 15.0, 16.0, 19.0, 23.0, 29.0, 34.0],
        source=TABLE_SOURCE,
    ),
    "has_rim": dict(
        desc="Whether the catalogue row has a seating rim",
        unit="",
        range={"easy": (0, 1), "medium": (0, 1), "hard": (0, 1)},
        refine=True,
        feature=True,
        coverage=[0, 1],
        source=TABLE_SOURCE,
    ),
    "rim_diameter": dict(
        desc="Nominal outside diameter of the optional seating rim",
        unit="mm",
        range={
            "easy": (0.0, 16.5),
            "medium": (0.0, 16.5),
            "hard": (0.0, 16.5),
        },
        refine=True,
        source=TABLE_SOURCE,
    ),
    "rim_height": dict(
        desc="Nominal height of the optional seating rim",
        unit="mm",
        range={
            "easy": (0.0, 1.0),
            "medium": (0.0, 1.0),
            "hard": (0.0, 1.0),
        },
        refine=True,
        source=TABLE_SOURCE,
    ),
    "bolt_axis_height": dict(
        desc="Dim. A, panel-face to connecting-bolt axis distance",
        unit="mm",
        range={
            "easy": (6.0, 8.0),
            "medium": (6.0, 11.5),
            "hard": (6.0, 17.0),
        },
        refine=True,
        askable=True,
        coverage=[6.0, 7.5, 8.0, 9.5, 11.5, 14.5, 17.0],
        source=TABLE_SOURCE,
    ),
    "housing_height": dict(
        desc="Nominal drilling depth X used to scale the axial envelope",
        unit="mm",
        range={
            "easy": (9.5, 12.5),
            "medium": (9.5, 16.5),
            "hard": (9.5, 22.5),
        },
        refine=True,
        askable=True,
        coverage=[9.5, 12.0, 12.5, 14.5, 16.5, 19.5, 22.5],
        source=TABLE_SOURCE + "; X-to-casting-envelope mapping is " + PROPORTION,
    ),
    "bolt_hole_diameter": dict(
        desc="Catalogue mating-panel edge drill-hole diameter",
        unit="mm",
        range={
            "easy": (7.0, 8.0),
            "medium": (7.0, 8.0),
            "hard": (7.0, 8.0),
        },
        choices={
            "easy": [7.0, 8.0],
            "medium": [7.0, 8.0],
            "hard": [7.0, 8.0],
        },
        coverage=[7.0, 8.0],
        askable=True,
        source=(
            TABLE_SOURCE
            + ": bolt drill hole Ø7 or Ø8 mm; capture-clearance scaling is "
            + PROPORTION
        ),
    ),
    "cam_web_thickness": dict(
        desc="Nominal reconstructed cage-wall and cam-web thickness",
        unit="mm",
        range={
            "easy": (0.99, 0.99),
            "medium": (0.77, 1.10),
            "hard": (0.77, 1.21),
        },
        refine=True,
        source=OEM_CAD_SOURCE + "; cross-SKU scaling is " + PROPORTION,
    ),
}


def refine(p: dict, difficulty: str, rng) -> None:
    """Expand one real catalogue row into its coupled nominal dimensions."""
    del difficulty, rng
    row = CATALOG_ROWS[int(p["variant"])]
    (
        p["min_wood_thickness"],
        p["body_diameter"],
        p["has_rim"],
        p["rim_diameter"],
        p["rim_height"],
        p["bolt_axis_height"],
        p["housing_height"],
    ) = row
    p["cam_web_thickness"] = round(0.22 * (p["housing_height"] - p["bolt_axis_height"]), 2)


def check(p: dict) -> list[str]:
    """Return engineering violations; each statement names its evidence."""
    bad = []
    expected = CATALOG_ROWS[int(p["variant"])]
    actual = (
        p["min_wood_thickness"],
        p["body_diameter"],
        p["has_rim"],
        p["rim_diameter"],
        p["rim_height"],
        p["bolt_axis_height"],
        p["housing_height"],
    )
    if actual != expected:
        bad.append("variant dimensions do not match its exact Häfele catalogue row")
    if p["body_diameter"] != 15.0:
        bad.append("body_diameter != 15: catalogue pp. 294--295 specifies a Ø15 bore")
    if abs(p["bolt_axis_height"] - p["min_wood_thickness"] / 2.0) > 1e-9:
        bad.append("A != t/2: catalogue rows keep the bolt axis on the panel mid-plane")
    if p["housing_height"] > p["min_wood_thickness"] - 2.0:
        bad.append("X > t-2: catalogue bore must retain at least a 2 mm panel floor")
    hook_depth = p["housing_height"] - p["bolt_axis_height"]
    if not 3.5 <= hook_depth <= 5.5:
        bad.append("X-A outside 3.5..5.5 mm: catalogue rows bound the body past the bolt axis")
    if p["has_rim"]:
        if (p["rim_diameter"], p["rim_height"]) != (16.5, 1.0):
            bad.append("rim dimensions differ from nominal Ø16.5 × 1 mm: catalogue p. 295")
        if p["rim_diameter"] <= p["body_diameter"]:
            bad.append("rim_diameter <= body_diameter: rim must overhang the Ø15 bore")
    elif p["rim_diameter"] != 0.0 or p["rim_height"] != 0.0:
        bad.append("unrimmed order rows have no seating rim: catalogue p. 294")
    if p["bolt_hole_diameter"] not in (7.0, 8.0):
        bad.append("bolt drill hole is not Ø7 or Ø8 mm: catalogue pp. 294--295")
    expected_web = round(0.22 * hook_depth, 2)
    if p["cam_web_thickness"] != expected_web:
        bad.append("cage wall does not follow the declared OEM-calibrated proportion")
    if not 0 < p["cam_web_thickness"] < 0.10 * p["body_diameter"]:
        bad.append("cage wall is not a thin die-cast web (OEM CAD/proportion)")
    return bad
