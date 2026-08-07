"""Benchmark specification for Ganter GN 3971 bevel gear boxes.

``catalog_index`` selects one complete official size/type row.  Every drawing
dimension is refined from that row; L/T types and dimensions are never mixed.
``shaft_rotation_deg`` is an operating pose only and changes no catalog value.
"""

from part import _layout


CATALOG_ROWS = [
    # type: 0=L, 1=T. d3 is retained as evidence only; None is the official
    # unavailable value for b1=18 and never drives PARAM_SPEC or geometry.
    dict(type=0, b1=18, d1=6, b2=2, d2=13, d3=None, h=0.8, l1=32, l2=12,
         l3=8, l4=2, m1=23, t1=2.1, t2=15.4, d4=3.1, d5=3, d6=3, d7=3,
         m2=6, m3=8.5, m4=13, m5=11),
    dict(type=1, b1=18, d1=6, b2=2, d2=13, d3=None, h=0.8, l1=32, l2=12,
         l3=8, l4=2, m1=23, t1=3.1, t2=15.1, d4=3.1, d5=3, d6=3, d7=3,
         m2=6, m3=8.5, m4=13, m5=11),
    dict(type=0, b1=20, d1=8, b2=2, d2=16, d3=9.2, h=0.8, l1=35, l2=12,
         l3=8, l4=2, m1=25, t1=1.95, t2=15.3, d4=3.1, d5=3, d6=3, d7=3,
         m2=7, m3=10, m4=15, m5=10),
    dict(type=1, b1=20, d1=6, b2=2, d2=16, d3=9.2, h=0.8, l1=35, l2=12,
         l3=8, l4=2, m1=25, t1=2.25, t2=14.25, d4=3.1, d5=3, d6=3, d7=3,
         m2=7, m3=10, m4=15, m5=10),
    dict(type=0, b1=24, d1=10, b2=4, d2=19, d3=11.8, h=1.5, l1=42, l2=16,
         l3=12, l4=3, m1=30, t1=2, t2=18, d4=4.1, d5=4, d6=4, d7=4,
         m2=8, m3=12, m4=18, m5=16),
    dict(type=1, b1=24, d1=8, b2=3, d2=19, d3=11.8, h=1.2, l1=42, l2=16,
         l3=10, l4=3, m1=30, t1=2, t2=18, d4=4.1, d5=4, d6=4, d7=4,
         m2=8, m3=12, m4=18, m5=16),
    dict(type=0, b1=26, d1=12, b2=4, d2=21, d3=13.6, h=1.5, l1=46, l2=16,
         l3=12, l4=3, m1=33, t1=2, t2=19.5, d4=4.1, d5=4, d6=4, d7=5,
         m2=9, m3=13, m4=20, m5=16),
    dict(type=1, b1=26, d1=8, b2=3, d2=21, d3=13.6, h=1.2, l1=46, l2=16,
         l3=10, l4=3, m1=33, t1=2, t2=18, d4=4.1, d5=4, d6=4, d7=4,
         m2=9, m3=13, m4=20, m5=16),
    dict(type=0, b1=30, d1=12, b2=4, d2=24, d3=16.4, h=1.5, l1=53, l2=16,
         l3=12, l4=3, m1=38, t1=2.1, t2=18.3, d4=4.1, d5=4, d6=4, d7=5,
         m2=11, m3=15, m4=22, m5=16),
    dict(type=1, b1=30, d1=8, b2=3, d2=24, d3=16.4, h=1.2, l1=53, l2=16,
         l3=10, l4=3, m1=38, t1=2.3, t2=18.3, d4=4.1, d5=4, d6=4, d7=4,
         m2=11, m3=15, m4=22, m5=16),
    dict(type=0, b1=32, d1=12, b2=4, d2=28, d3=19.8, h=1.5, l1=56, l2=16,
         l3=12, l4=3, m1=40, t1=2.1, t2=18.3, d4=4.1, d5=4, d6=4, d7=5,
         m2=12, m3=17, m4=24, m5=16),
    dict(type=1, b1=32, d1=10, b2=3, d2=28, d3=19.8, h=1.2, l1=56, l2=16,
         l3=10, l4=3, m1=40, t1=2.8, t2=18.8, d4=4.1, d5=4, d6=4, d7=4,
         m2=12, m3=17, m4=24, m5=16),
    dict(type=0, b1=35, d1=12, b2=4, d2=30, d3=20.4, h=1.5, l1=60, l2=16,
         l3=12, l4=3, m1=42.5, t1=2.1, t2=18.3, d4=4.1, d5=4, d6=4, d7=5,
         m2=13.5, m3=17.5, m4=26, m5=16),
    dict(type=1, b1=35, d1=12, b2=4, d2=30, d3=20.4, h=1.5, l1=60, l2=16,
         l3=12, l4=3, m1=42.5, t1=3.2, t2=19.2, d4=4.1, d5=4, d6=4, d7=5,
         m2=13.5, m3=17.5, m4=26, m5=16),
]


DIFFICULTY_INDICES = {
    "easy": [0, 1, 2, 3],
    "medium": [4, 5, 6, 7, 8, 9],
    "hard": [10, 11, 12, 13],
}


def _catalog_range(key, difficulty):
    values = [CATALOG_ROWS[i][key] for i in DIFFICULTY_INDICES[difficulty]]
    return (min(values), max(values))


def _ranges(key):
    return {d: _catalog_range(key, d) for d in ("easy", "medium", "hard")}


GN_PAGE_1 = (
    "Ganter GN 3971 standard sheet, PDF page 1: dimensional drawing and "
    "b1/d1/b2/d2/h/l1/l2/l3/l4/m1/t1/t2 table"
)
GN_PAGE_2 = (
    "Ganter GN 3971 standard sheet, PDF page 2: d4/d5/d6/d7/m2/m3/m4/m5 "
    "mounting-interface table"
)


PARAM_SPEC = {
    "catalog_index": dict(
        desc="Index selecting one complete official GN 3971 size/type row",
        unit="row",
        range={"easy": (0, 3), "medium": (4, 9), "hard": (10, 13)},
        choices=DIFFICULTY_INDICES,
        coverage=list(range(14)),
        integer=True,
        source=f"{GN_PAGE_1}; {GN_PAGE_2}",
    ),
    "gearbox_type": dict(
        desc="Official gearbox type code, 0 for L and 1 for T",
        unit="code",
        range=_ranges("type"), refine=True, integer=True, feature=True,
        source="Ganter GN 3971 type definitions: L=90-degree, T=two output ends",
    ),
    "housing_size_b1": dict(
        desc="Square housing size b1", unit="mm", range=_ranges("b1"),
        refine=True, source=GN_PAGE_1),
    "shaft_diameter_d1": dict(
        desc="External shaft diameter d1", unit="mm", range=_ranges("d1"),
        refine=True, source=GN_PAGE_1),
    "key_width_b2": dict(
        desc="Installed parallel-key width b2", unit="mm", range=_ranges("b2"),
        refine=True, source=f"{GN_PAGE_1}; keyway DIN 6885-1"),
    "bearing_boss_diameter_d2": dict(
        desc="Visible bearing-seat and shaft-boss envelope diameter d2", unit="mm",
        range=_ranges("d2"), refine=True, source=GN_PAGE_1),
    "key_height_h": dict(
        desc="Parallel-key projection above the shaft, h", unit="mm",
        range=_ranges("h"), refine=True, source=GN_PAGE_1),
    "housing_length_l1": dict(
        desc="Overall housing length/height l1", unit="mm", range=_ranges("l1"),
        refine=True, source=GN_PAGE_1),
    "shaft_projection_l2": dict(
        desc="Shaft projection beyond the housing face, l2", unit="mm",
        range=_ranges("l2"), refine=True, source=GN_PAGE_1),
    "key_length_l3": dict(
        desc="Installed parallel-key length l3", unit="mm", range=_ranges("l3"),
        refine=True, source=GN_PAGE_1),
    "key_end_margin_l4": dict(
        desc="Shaft-end margin beyond the parallel key, l4", unit="mm",
        range=_ranges("l4"), refine=True, source=GN_PAGE_1),
    "input_axis_height_m1": dict(
        desc="Distance m1 from the shaft intersection to the input housing face",
        unit="mm", range=_ranges("m1"), refine=True, source=GN_PAGE_1),
    "bearing_inset_t1": dict(
        desc="Official axial bearing/shoulder inset t1", unit="mm",
        range=_ranges("t1"), refine=True, source=GN_PAGE_1),
    "shaft_reach_t2": dict(
        desc="Official internal shaft/bearing reach t2 from the bearing face",
        unit="mm", range=_ranges("t2"), refine=True, source=GN_PAGE_1),
    "mounting_hole_diameter_d4": dict(
        desc="Side-view clearance-hole diameter d4", unit="mm",
        range=_ranges("d4"), refine=True, source=GN_PAGE_2),
    "mounting_thread_d5": dict(
        desc="Bearing-face mounting-thread nominal diameter d5", unit="mm",
        range=_ranges("d5"), refine=True, source=GN_PAGE_2),
    "rear_thread_d6": dict(
        desc="Rear-face mounting-thread nominal diameter d6", unit="mm",
        range=_ranges("d6"), refine=True, source=GN_PAGE_2),
    "shaft_end_thread_d7": dict(
        desc="Shaft-end internal-thread nominal diameter d7", unit="mm",
        range=_ranges("d7"), refine=True, source=GN_PAGE_2),
    "lower_hole_offset_m2": dict(
        desc="Lower side clearance-hole diagonal offset m2", unit="mm",
        range=_ranges("m2"), refine=True, source=GN_PAGE_2),
    "upper_hole_offset_m3": dict(
        desc="Upper side clearance-hole diagonal offset m3", unit="mm",
        range=_ranges("m3"), refine=True, source=GN_PAGE_2),
    "face_hole_spacing_m4": dict(
        desc="Bearing-face and rear-hole center spacing m4", unit="mm",
        range=_ranges("m4"), refine=True, source=GN_PAGE_2),
    "rear_hole_height_m5": dict(
        desc="Type-L rear threaded-hole height m5 above the housing base",
        unit="mm",
        range=_ranges("m5"), refine=True, source=GN_PAGE_2),
    "shaft_rotation_deg": dict(
        desc="Input-shaft operating angle; output angle has equal opposite magnitude",
        unit="deg",
        range={"easy": (-30.0, 30.0), "medium": (-90.0, 90.0),
               "hard": (-180.0, 180.0)},
        source=("proportion: canonical full-cycle motion-state sweep; GN 3971 "
                "page 3 specifies 1:1 ratio, 3 +/- 0.5 deg backlash, and any "
                "shaft rotation direction"),
    ),
}


_ROW_KEYS = {
    "gearbox_type": "type",
    "housing_size_b1": "b1",
    "shaft_diameter_d1": "d1",
    "key_width_b2": "b2",
    "bearing_boss_diameter_d2": "d2",
    "key_height_h": "h",
    "housing_length_l1": "l1",
    "shaft_projection_l2": "l2",
    "key_length_l3": "l3",
    "key_end_margin_l4": "l4",
    "input_axis_height_m1": "m1",
    "bearing_inset_t1": "t1",
    "shaft_reach_t2": "t2",
    "mounting_hole_diameter_d4": "d4",
    "mounting_thread_d5": "d5",
    "rear_thread_d6": "d6",
    "shaft_end_thread_d7": "d7",
    "lower_hole_offset_m2": "m2",
    "upper_hole_offset_m3": "m3",
    "face_hole_spacing_m4": "m4",
    "rear_hole_height_m5": "m5",
}


def refine(p: dict, difficulty: str, rng) -> None:
    del difficulty, rng
    row = CATALOG_ROWS[int(p["catalog_index"])]
    for parameter, key in _ROW_KEYS.items():
        p[parameter] = row[key]


def check(p: dict) -> list[str]:
    bad = []
    raw_index = p.get("catalog_index")
    if isinstance(raw_index, bool) or not isinstance(raw_index, (int, float)):
        return ["catalog_index must be an integer selecting an official GN 3971 row"]
    if raw_index != int(raw_index):
        return ["catalog_index must be an exact integer, not a truncated float"]
    index = int(raw_index)
    if index < 0 or index >= len(CATALOG_ROWS):
        return ["catalog_index must select one of the 14 official GN 3971 rows"]
    row = CATALOG_ROWS[index]
    for parameter, key in _ROW_KEYS.items():
        if p.get(parameter) != row[key]:
            bad.append(f"{parameter} must equal the selected official GN 3971 row")

    if not -180.0 <= p["shaft_rotation_deg"] <= 180.0:
        bad.append("proportion: shaft_rotation_deg must stay inside the canonical full-cycle pose sweep")
    if abs((p["housing_length_l1"] - p["input_axis_height_m1"])
           - 0.5 * p["housing_size_b1"]) > 1e-9:
        bad.append("GN 3971 rows require l1-m1=b1/2 at the shaft-axis intersection")
    if not p["shaft_diameter_d1"] < p["bearing_boss_diameter_d2"] < p["housing_size_b1"]:
        bad.append("official d1/d2/b1 row must leave a positive bearing housing wall")
    if p["key_width_b2"] >= p["shaft_diameter_d1"]:
        bad.append("DIN 6885-1 key width b2 must be smaller than shaft diameter d1")
    if p["key_length_l3"] + p["key_end_margin_l4"] > p["shaft_projection_l2"]:
        bad.append("GN 3971 page 1: l3+l4 must fit inside external shaft projection l2")

    half = 0.5 * p["housing_size_b1"]
    face_r = 0.5 * p["mounting_thread_d5"]
    if 0.5 * p["face_hole_spacing_m4"] + face_r >= half:
        bad.append("GN 3971 page 2: m4/d5 face pattern must retain positive b1 edge material")
    bearing_r = 0.5 * p["bearing_boss_diameter_d2"]
    face_center_r = p["face_hole_spacing_m4"] / (2.0 ** 0.5)
    if face_center_r - face_r <= bearing_r:
        bad.append("GN 3971 page 2: m4/d5 holes must clear the d2 opening")

    L = _layout(
        p["housing_size_b1"], p["shaft_diameter_d1"],
        p["bearing_boss_diameter_d2"], p["housing_length_l1"],
        p["shaft_projection_l2"], p["input_axis_height_m1"],
        p["bearing_inset_t1"], p["shaft_reach_t2"], p["gearbox_type"])

    d4_r = 0.5 * p["mounting_hole_diameter_d4"]
    if p["gearbox_type"] == 0 and half - p["lower_hole_offset_m2"] <= d4_r:
        bad.append("GN 3971 page 2: Type-L lower d4 hole must retain rear/base material")
    # A conservative quarter-ellipse envelope keeps the diagonal d4 hole
    # clear of the analytic shoulder transition for every catalog size.  The
    # built Type-T profile uses the sourced circular-arc construction in
    # part.py; this envelope is intentionally stricter than its tangent legs.
    profile_dx = max(0.0, L["front"] - p["upper_hole_offset_m3"] - d4_r)
    profile_dz = max(0.0, L["top"] - p["upper_hole_offset_m3"] - d4_r)
    profile_rx = L["front"] - half
    profile_rz = L["top"] - half
    if (profile_dx / profile_rx) ** 2 + (profile_dz / profile_rz) ** 2 <= 1.0:
        bad.append("GN 3971 page 2: m3/d4 holes must remain inside the shoulder transition")

    rear_r = 0.5 * p["rear_thread_d6"]
    if 0.5 * p["face_hole_spacing_m4"] + rear_r >= half:
        bad.append("GN 3971 page 2: m4/d6 rear pattern must retain side material")
    rear_z = (
        L["bottom"] + p["rear_hole_height_m5"]
        if p["gearbox_type"] == 0 else 0.0
    )
    if rear_z - rear_r <= L["bottom"] or rear_z + rear_r >= L["top"]:
        bad.append("GN 3971 page 2: d6 rear holes must retain vertical housing material")

    usable_d7_depth = 1.6 * p["shaft_end_thread_d7"]
    input_shaft_length = L["input_shaft_end"] - L["shaft_start"]
    if usable_d7_depth >= input_shaft_length:
        bad.append("proportion: modeled d7 usable depth must fit inside each shaft solid")

    # the rim that carries the teeth is measured at the HEEL, where the root
    # cone is largest; the toe of a bevel gear on a through shaft is always
    # thin, so a toe-only rule would either be meaningless or reject the line
    # the tooth SPACES must clear the shaft bore at the toe as well, not only
    # at the heel: with a coarse module the root cone dives inside the bore and
    # the teeth are cut straight into the shaft
    toe_wall = L["gear_root_inner"] - 0.5 * p["shaft_diameter_d1"]
    if toe_wall < 0.30 * L["gear_module"]:
        bad.append("bevel-gear tooth spaces reach the shaft bore at the toe: the root "
                   "cone must stay outside d1/2 by at least 0.3*m")
    heel_rim = L["gear_root_outer"] - 0.5 * p["shaft_diameter_d1"]
    if heel_rim < 1.0 * L["gear_module"]:
        bad.append("proportion: bevel-gear heel rim under 1.0*m between root cone and "
                   "bore: the toothed rim would be a shell, not a blank")
    if L["shaft_start"] <= 0.5 * p["shaft_diameter_d1"]:
        bad.append("proportion: each shaft end must stop outside the perpendicular shaft radius")
    if L["shaft_start"] >= L["gear_s_inner"]:
        bad.append("proportion: each shaft must retain positive seating length in its gear bore")
    if L["gear_tip_outer"] + L["cavity_clearance"] >= half - 0.02 * p["housing_size_b1"]:
        bad.append("proportion: gear cavity must leave a positive b1 side wall")
    rear_bearing_face = L["input_rear_bearing"] - 0.5 * L["bearing_width"]
    if rear_bearing_face <= L["gear_s_outer"] + L["cavity_clearance"]:
        bad.append("proportion: input bearing stack must remain clear of the bevel gear")
    if L["input_front_bearing"] - L["input_rear_bearing"] <= L["bearing_width"]:
        bad.append("proportion: the two input bearings must remain axially separated")
    if p["gearbox_type"] == 1:
        bottom_bearing_top = L["output_second_bearing"] + 0.5 * L["bearing_width"]
        if bottom_bearing_top >= -L["gear_tip_outer"]:
            bad.append("proportion: Type-T bottom bearing must clear the input bevel gear")

    # Tooth thickness is chosen so equal gears reproduce the published
    # circumferential backlash at the pitch circle.
    # the tooth thickness is solved FROM the published backlash at this
    # instance's tooth count, so the figure is reproduced by construction;
    # what still needs checking is that the gear is proportioned like a real
    # straight bevel: face width in the b/m band: the housing envelope, not free choice, sets it here, and b <= R/3
    backlash = (1.0 - 2.0 * L["gear_tooth_fraction"]) * 360.0 / L["gear_teeth"]
    if not 2.5 <= backlash <= 3.5:
        bad.append("gear proportion must reproduce GN 3971 backlash 3 +/- 0.5 deg")
    face = (L["gear_s_outer"] - L["gear_s_inner"]) * 2.0 ** 0.5
    if not 1.8 <= face / L["gear_module"] <= 12.0:
        bad.append("bevel face width outside the b/m band: the housing envelope, not free choice, sets it here: the rim would read "
                   "as a sawblade (too few teeth) or the module is unrealistically fine")
    if face > L["gear_s_outer"] * 2.0 ** 0.5 / 3.0 + 1e-6:
        bad.append("bevel face width over R/3: outside straight-bevel practice")
    return bad
