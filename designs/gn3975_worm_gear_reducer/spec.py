"""Benchmark specification for the Ganter GN 3975 worm reducer.

The public GN 3975 drawing gives a small, discrete table rather than an
independent range for each dimension.  ``catalog_index`` therefore selects a
complete row and ``refine`` copies that row into the named build parameters.
This prevents impossible combinations such as a 20-size housing with the
30-size mounting pattern while still exposing every catalog tuple to the
benchmark sampler.
"""

from bench2 import Resample


CATALOG_FIELDS = (
    "gearbox_type",
    "housing_size_m1",
    "gear_ratio_i",
    "housing_face_width_b1",
    "drive_shaft_diameter_d1",
    "drive_keyway_width_b2",
    "output_keyway_width_b3",
    "output_bore_diameter_d2",
    "output_hub_outer_diameter_d3",
    "secondary_interface_diameter_d4",
    "bearing_interface_diameter_d5",
    "keyway_depth_h",
    "housing_overall_length_l1",
    "drive_shaft_projection_l2",
    "output_interface_length_l3",
    "shaft_end_margin_l4",
    "axial_offset_t1",
    "keyway_length_t2",
    "radial_offset_t3",
    "shaft_end_length_t4",
    "mounting_thread_d6",
    "clearance_hole_d7",
    "shaft_end_thread_d8",
    "mounting_spacing_m2",
    "mounting_spacing_m3",
    "mounting_offset_m4",
    "mounting_offset_m5",
    "mounting_spacing_m6",
    "mounting_spacing_m7",
    "mounting_spacing_m8",
    "mounting_spacing_m9",
    "mounting_spacing_m10",
    "mounting_spacing_m11",
)


# GN 3975 drawing/table values.  The first eight rows are size m1=20 Type A,
# the next eight size m1=20 Type B, then the corresponding m1=30 rows.  Type A
# is the one-sided drive extension; Type B is the through-shaft arrangement.
_SIZE_20 = (
    35, 12, 4, 4, 12, 30, 20, 27.4, 1.5, 60, 16, 12, 3, 2, 13.8,
    1.6, 18.3, 4, 4.2, 5, 26, 50, 17.5, 1.5, 31, 26, 42.5, 22.5, 26, 33,
)
_SIZE_30 = (
    40, 12, 4, 5, 14, 30, 25, 27.4, 1.5, 80, 16, 12, 3, 4, 16.3,
    2.0, 20.5, 5, 5.5, 5, 40, 60, 20, 10, 15, 26, 57.5, 30, 30, 47,
)
_RATIOS_20 = (5, 13, 15, 18, 23, 30, 40, 65)
_RATIOS_30 = (5, 10, 17, 20, 25, 34, 45, 64)

CATALOG_ROWS = [
    (gearbox_type, 20, ratio, *_SIZE_20)
    for gearbox_type in (1, 2)
    for ratio in _RATIOS_20
] + [
    (gearbox_type, 30, ratio, *_SIZE_30)
    for gearbox_type in (1, 2)
    for ratio in _RATIOS_30
]

ROWS_BY_DIFF = {
    "easy": list(range(0, 16)),
    "medium": list(range(16, 32)),
    "hard": list(range(32)),
}


def _table_ranges(field_index: int) -> dict[str, tuple[float, float]]:
    """Ranges are the extrema of the rows allowed at each difficulty."""
    return {
        difficulty: (
            min(CATALOG_ROWS[i][field_index] for i in indices),
            max(CATALOG_ROWS[i][field_index] for i in indices),
        )
        for difficulty, indices in ROWS_BY_DIFF.items()
    }


def _catalog_param(field: str, desc: str, unit: str = "mm", *, integer=False,
                   feature=False) -> dict:
    index = CATALOG_FIELDS.index(field)
    entry = {
        "desc": desc,
        "unit": unit,
        "range": _table_ranges(index),
        "source": "Ganter GN 3975 drawing/table (issue #153)",
        "refine": True,
    }
    if integer:
        entry["integer"] = True
    if feature:
        entry["feature"] = True
    return entry


PARAM_SPEC = {
    "catalog_index": {
        "desc": "complete GN 3975 catalog row and gearbox variant",
        "unit": "",
        "range": {"easy": (0, 15), "medium": (16, 31), "hard": (0, 31)},
        "source": "Ganter GN 3975 drawing/table (issue #153), row-locked catalog",
        "choices": {d: rows for d, rows in ROWS_BY_DIFF.items()},
        "integer": True,
        "coverage": list(range(32)),
    },
    "gearbox_type": _catalog_param(
        "gearbox_type", "drive arrangement: Type A one-sided or Type B through shaft", "",
        integer=True, feature=True,
    ),
    "housing_size_m1": _catalog_param("housing_size_m1", "worm/output axis centre distance m1", "", integer=True),
    "gear_ratio_i": _catalog_param("gear_ratio_i", "catalog worm reduction ratio i", "", integer=True),
    "housing_face_width_b1": _catalog_param("housing_face_width_b1", "housing face width b1"),
    "drive_shaft_diameter_d1": _catalog_param("drive_shaft_diameter_d1", "drive shaft diameter d1"),
    "drive_keyway_width_b2": _catalog_param("drive_keyway_width_b2", "drive shaft key width b2"),
    "output_keyway_width_b3": _catalog_param("output_keyway_width_b3", "output key width b3"),
    "output_bore_diameter_d2": _catalog_param("output_bore_diameter_d2", "output H7 bore diameter d2"),
    "output_hub_outer_diameter_d3": _catalog_param("output_hub_outer_diameter_d3", "output hub diameter d3"),
    "secondary_interface_diameter_d4": _catalog_param("secondary_interface_diameter_d4", "secondary interface diameter d4"),
    "bearing_interface_diameter_d5": _catalog_param("bearing_interface_diameter_d5", "bearing interface diameter d5"),
    "keyway_depth_h": _catalog_param("keyway_depth_h", "key depth h"),
    "housing_overall_length_l1": _catalog_param("housing_overall_length_l1", "housing overall length l1"),
    "drive_shaft_projection_l2": _catalog_param("drive_shaft_projection_l2", "drive shaft projection l2"),
    "output_interface_length_l3": _catalog_param("output_interface_length_l3", "drive key length l3 from the Type A/B view"),
    "shaft_end_margin_l4": _catalog_param("shaft_end_margin_l4", "shaft end margin l4"),
    "axial_offset_t1": _catalog_param("axial_offset_t1", "bearing axial offset t1"),
    "keyway_length_t2": _catalog_param("keyway_length_t2", "catalog sectional extent t2"),
    "radial_offset_t3": _catalog_param("radial_offset_t3", "housing wall/seat offset t3"),
    "shaft_end_length_t4": _catalog_param("shaft_end_length_t4", "drive-shaft axial extent t4"),
    "mounting_thread_d6": _catalog_param("mounting_thread_d6", "mounting thread nominal diameter d6", "", integer=True),
    "clearance_hole_d7": _catalog_param("clearance_hole_d7", "mounting clearance hole diameter d7"),
    "shaft_end_thread_d8": _catalog_param("shaft_end_thread_d8", "shaft-end thread nominal diameter d8", "", integer=True),
    "mounting_spacing_m2": _catalog_param("mounting_spacing_m2", "output-face square tapped-hole spacing m2"),
    "mounting_spacing_m3": _catalog_param("mounting_spacing_m3", "lower clearance-hole row spacing m3"),
    "mounting_offset_m4": _catalog_param("mounting_offset_m4", "lower clearance-hole row offset m4"),
    "mounting_offset_m5": _catalog_param("mounting_offset_m5", "middle clearance-hole row offset m5"),
    "mounting_spacing_m6": _catalog_param("mounting_spacing_m6", "upper clearance-hole row spacing m6"),
    "mounting_spacing_m7": _catalog_param("mounting_spacing_m7", "drive-end square tapped-hole spacing m7"),
    "mounting_spacing_m8": _catalog_param("mounting_spacing_m8", "drive-axis height from lower housing edge m8"),
    "mounting_spacing_m9": _catalog_param("mounting_spacing_m9", "broad-face horizontal tapped-hole spacing m9"),
    "mounting_spacing_m10": _catalog_param("mounting_spacing_m10", "broad-face vertical tapped-hole spacing m10"),
    "mounting_spacing_m11": _catalog_param("mounting_spacing_m11", "upper clearance-hole row offset m11"),
    "input_rotation_deg": {
        "desc": "deterministic input shaft pose for assembly visualization",
        "unit": "deg",
        "range": {"easy": (0.0, 0.0), "medium": (-90.0, 90.0), "hard": (-180.0, 180.0)},
        "source": "issue #153 assembly pose; proportion",
    },
}


def refine(p: dict, difficulty: str, rng) -> None:
    """Lock all geometry values to one complete official catalog tuple."""
    del rng  # row selection is the sampler's catalog_index choice
    index = int(p["catalog_index"])
    if index not in ROWS_BY_DIFF[difficulty]:
        raise Resample
    row = CATALOG_ROWS[index]
    for name, value in zip(CATALOG_FIELDS, row):
        p[name] = value


def check(p: dict) -> list[str]:
    """Engineering constraints for the catalog row and simplified internals."""
    bad = []
    index = int(p["catalog_index"])
    if not 0 <= index < len(CATALOG_ROWS):
        return ["catalog_index outside the 32-row GN 3975 table"]

    # A sampled instance must remain an unmodified manufacturer tuple.
    row = CATALOG_ROWS[index]
    for name, expected in zip(CATALOG_FIELDS, row):
        actual = p.get(name)
        if actual is None or abs(float(actual) - float(expected)) > 1e-6:
            bad.append(f"{name} differs from GN 3975 table row {index}")

    # Interface and key proportions are true for both published housing sizes.
    if p["output_bore_diameter_d2"] >= p["output_hub_outer_diameter_d3"]:
        bad.append("d2 >= d3: the output hub must retain a radial wall (GN 3975 drawing)")
    if p["bearing_interface_diameter_d5"] >= p["output_hub_outer_diameter_d3"]:
        bad.append("d5 >= d3: bearing register must fit inside the output hub (GN 3975 drawing)")
    if p["drive_keyway_width_b2"] > p["drive_shaft_diameter_d1"] / 2.0:
        bad.append("b2 > d1/2: key width must leave shaft material (DIN 6885-1 proportion)")
    if p["output_keyway_width_b3"] > p["output_bore_diameter_d2"] / 2.0:
        bad.append("b3 > d2/2: output key must leave a bore wall (DIN 6885-1 proportion)")
    if p["shaft_end_thread_d8"] >= p["drive_shaft_diameter_d1"]:
        bad.append("d8 >= d1: shaft-end thread cannot fit the drive shaft (proportion)")
    if p["shaft_end_length_t4"] < 1.6 * p["shaft_end_thread_d8"]:
        bad.append("t4 < 1.6*d8: tapped end lacks the issue's usable thread depth")
    # Mounting-hole rectangles must stay inside the corresponding housing
    # envelope; these inequalities are direct checks of the published m/d rows.
    if p["mounting_spacing_m3"] + 2.0 * p["clearance_hole_d7"] > p["housing_overall_length_l1"]:
        bad.append("m3 + 2*d7 > l1: top clearance holes leave the housing envelope")
    if p["mounting_spacing_m9"] + 2.0 * p["mounting_thread_d6"] > p["housing_overall_length_l1"]:
        bad.append("m9 + 2*d6 > l1: broad-face tapped holes leave the housing envelope")
    if p["mounting_spacing_m7"] + 2.0 * p["mounting_thread_d6"] > p["housing_face_width_b1"]:
        bad.append("m7 + 2*d6 > b1: drive-end tapped holes leave the housing envelope")
    if p["mounting_spacing_m10"] + 2.0 * p["mounting_thread_d6"] > p["housing_face_width_b1"]:
        bad.append("m10 + 2*d6 > b1: broad-face tapped holes leave the housing envelope")
    output_from_lower_edge = p["mounting_spacing_m8"] - p["housing_size_m1"]
    if not 0.0 < output_from_lower_edge < p["housing_overall_length_l1"]:
        bad.append("m8-m1 outside l1: output axis must remain inside the housing (GN 3975 drawing)")
    if p["mounting_spacing_m8"] + p["output_hub_outer_diameter_d3"] / 2.0 > p["housing_overall_length_l1"]:
        bad.append("m8+d3/2 > l1: drive register leaves the upper housing edge (GN 3975 drawing)")

    # The catalog ratios are output/input speed ratios.  The two-start worm,
    # wheel tooth form, and bearing section are intentionally proportioned
    # approximations because those internal manufacturing details are not in
    # the public GN 3975 table.
    if p["gear_ratio_i"] < 2:
        bad.append("gear_ratio_i < 2: reduction must exceed the two-start worm proportion")
    if p["gearbox_type"] not in (1, 2):
        bad.append("gearbox_type must be Type A=1 or Type B=2 (issue #153)")
    return bad
