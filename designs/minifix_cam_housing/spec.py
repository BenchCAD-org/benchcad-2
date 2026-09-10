"""Catalog installation rows plus explicit reference-based casting proportions."""

# Panel t, bolt axis A, bore depth X, rim, catalogue example order number.
# Rows 0..6 retain issue #25's identity; row 7 anchors the supplied 18 mm model.
CATALOG_ROWS = (
    (12.0, 6.0, 9.5, 1, "262.25.070"),
    (15.0, 7.5, 12.0, 0, "262.26.032"),
    (16.0, 8.0, 12.5, 1, "262.25.212"),
    (19.0, 9.5, 14.5, 1, "262.25.221"),
    (23.0, 11.5, 16.5, 1, "262.25.669"),
    (29.0, 14.5, 19.5, 0, "262.26.291"),
    (34.0, 17.0, 22.5, 1, "262.25.081"),
    (18.0, 9.0, 13.5, 0, "262.26.034"),
)
TABLE_SOURCE = (
    "Hafele UK catalogue 2014, pp. 294-295: "
    "https://files.hafele.co.uk/catalogfiles/www/14CFC294.pdf ; "
    "https://files.hafele.co.uk/catalogfiles/www/14CFC295.pdf"
)
REFERENCE = (
    "proportion: user-supplied minifiks kilidi.SLDPRT, measured 2026-09-10; "
    "third-party reference https://grabcad.com/library/minifix-lock-1 ; "
    "SKU identity unverified; see NOTES.md"
)

PARAM_SPEC = {
    "variant": dict(
        desc="Index of a verified installation row; 7 is the 18 mm baseline",
        unit="",
        integer=True,
        range={"easy": (0, 7), "medium": (0, 7), "hard": (0, 7)},
        choices={"easy": [7], "medium": [1, 2, 3, 4, 7], "hard": list(range(8))},
        coverage=list(range(8)),
        source=TABLE_SOURCE,
    ),
    "min_wood_thickness": dict(
        desc="Minimum panel thickness t, installation metadata",
        unit="mm",
        refine=True,
        range={"easy": (18, 18), "medium": (15, 23), "hard": (12, 34)},
        coverage=[12, 15, 16, 18, 19, 23, 29, 34],
        source=TABLE_SOURCE,
    ),
    "housing_bore_diameter": dict(
        desc="Required panel bore; distinct from the smaller casting outside diameter",
        unit="mm",
        refine=True,
        range={d: (15.0, 15.0) for d in ("easy", "medium", "hard")},
        source=TABLE_SOURCE,
    ),
    "body_diameter": dict(
        desc="Actual casting diameter, 14.8 mm measured from the reference",
        unit="mm",
        refine=True,
        range={d: (14.8, 14.8) for d in ("easy", "medium", "hard")},
        source=REFERENCE,
    ),
    "housing_height": dict(
        desc="Casting depth below seating face, modeled at nominal bore depth X",
        unit="mm",
        refine=True,
        range={"easy": (13.5, 13.5), "medium": (12, 16.5), "hard": (9.5, 22.5)},
        coverage=[9.5, 12, 12.5, 13.5, 14.5, 16.5, 19.5, 22.5],
        source=TABLE_SOURCE + "; X-to-casting equality is " + REFERENCE,
    ),
    "bolt_axis_height": dict(
        desc="A: distance below panel seating face to the radial bolt axis",
        unit="mm",
        refine=True,
        range={"easy": (9, 9), "medium": (7.5, 11.5), "hard": (6, 17)},
        coverage=[6, 7.5, 8, 9, 9.5, 11.5, 14.5, 17],
        source=TABLE_SOURCE,
    ),
    "has_rim": dict(
        desc="Catalogue row has a seating flange above the panel face",
        unit="",
        refine=True,
        integer=True,
        feature=True,
        range={d: (0, 1) for d in ("easy", "medium", "hard")},
        coverage=[0, 1],
        source=TABLE_SOURCE,
    ),
    "rim_diameter": dict(
        desc="Nominal flange outside diameter, or zero without flange",
        unit="mm",
        refine=True,
        range={d: (0, 16.5) for d in ("easy", "medium", "hard")},
        source=TABLE_SOURCE,
    ),
    "rim_height": dict(
        desc="Flange projection above the seating face, or zero without flange",
        unit="mm",
        refine=True,
        range={d: (0, 1) for d in ("easy", "medium", "hard")},
        source=TABLE_SOURCE,
    ),
    "web_thickness": dict(
        desc="Thickness of the X-directed support web at y=-thickness..0; reference is 1 mm",
        unit="mm",
        range={"easy": (1, 1), "medium": (0.95, 1.05), "hard": (0.85, 1.15)},
        source=REFERENCE + "; +/-0.15 mm exploratory web variation is proportion",
    ),
    "neck_slot_width": dict(
        desc="Radial cam slot width around bolt neck; reference rounded end is R1.5",
        unit="mm",
        range={"easy": (3, 3), "medium": (2.9, 3.1), "hard": (2.8, 3.2)},
        source=REFERENCE + "; +/-0.2 mm exploratory neck variation is proportion",
    ),
    "has_markings": dict(
        desc="Recessed rotation arrow and direction triangle on the top face",
        unit="",
        integer=True,
        feature=True,
        range={d: (0, 1) for d in ("easy", "medium", "hard")},
        choices={"easy": [0], "medium": [1], "hard": [1]},
        coverage=[0, 1],
        source=REFERENCE + "; marks are 0.2 mm deep",
    ),
}


def refine(p, difficulty, rng):
    """Expand one actual catalogue row without mixing unrelated row dimensions."""
    t, a, x, rim, _ = CATALOG_ROWS[int(p["variant"])]
    p.update(
        min_wood_thickness=t,
        bolt_axis_height=a,
        housing_height=x,
        has_rim=rim,
        rim_diameter=16.5 if rim else 0.0,
        rim_height=float(rim),
        housing_bore_diameter=15.0,
        body_diameter=14.8,
    )


def check(p):
    """Installation truth and material / tool-clearance constraints."""
    bad = []
    index = p["variant"]
    if index != int(index) or not 0 <= index < len(CATALOG_ROWS):
        return ["variant must identify an actual catalogue row (pp. 294-295)"]
    t, a, x, rim, _ = CATALOG_ROWS[int(index)]
    actual = (p["min_wood_thickness"], p["bolt_axis_height"], p["housing_height"], p["has_rim"])
    if actual != (t, a, x, rim):
        bad.append("installation dimensions must belong to one catalogue row (pp. 294-295)")
    if p["bolt_axis_height"] != p["min_wood_thickness"] / 2:
        bad.append("A must equal t/2: bolt axis is on panel mid-plane (catalogue rows)")
    if p["housing_height"] > p["min_wood_thickness"] - 2:
        bad.append("retain >=2 mm panel floor below bore X (catalogue row envelope)")
    if p["housing_bore_diameter"] != 15 or p["body_diameter"] != 14.8:
        bad.append("use the catalogue 15 mm bore and reference 14.8 mm casting (proportion)")
    expected_rim = (16.5, 1.0) if rim else (0.0, 0.0)
    if (p["rim_diameter"], p["rim_height"]) != expected_rim:
        bad.append("flange must match optional nominal diameter 16.5 x 1 mm (p. 295)")
    if rim and p["rim_diameter"] <= p["housing_bore_diameter"]:
        bad.append("seating flange must overhang the housing bore (catalogue drawing)")
    below_axis = p["housing_height"] - p["bolt_axis_height"]
    if not 3.5 <= below_axis <= 5.5:
        bad.append("X-A must retain the catalogue 3.5..5.5 mm space below bolt axis")
    if not 2.8 <= p["neck_slot_width"] <= 3.2:
        bad.append("neck slot exceeds reference R1.5 end +/-0.1 mm (proportion)")
    if not 0.85 <= p["web_thickness"] <= 1.15:
        bad.append("web must retain reference 1 mm thickness +/-0.15 mm (proportion)")
    if below_axis - p["neck_slot_width"] / 2 < 1.8:
        bad.append("retain at least 1.8 mm lower jaw beneath slot (reference proportion)")
    if p["bolt_axis_height"] - 3.383 < 2.5:
        bad.append("retain at least 2.5 mm support between cam roof and cap (proportion)")
    if p["has_markings"] not in (0, 1):
        bad.append("direction markings are an on/off reference feature (proportion)")
    return bad
