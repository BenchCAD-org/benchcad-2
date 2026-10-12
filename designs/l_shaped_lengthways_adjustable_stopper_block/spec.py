"""MISUMI catalog-row contract for an L-shaped stopper block."""


CATALOG_SOURCE = (
    "MISUMI Threaded Stopper Blocks, L-Shaped, Lengthways Adjustable, "
    "2019 US catalog p.1700: "
    "https://us.misumi-ec.com/pdf/fa/2019/2019_US_1700.pdf"
)

# The drawing table merges dimensions across four nominal-thread groups.
# All dimensions are millimeters. H is a permitted discrete axis height;
# the remaining values are fixed for every nominal M in the group.
CATALOG_GROUPS = (
    dict(
        m_values=(3, 4),
        h_choices=(15, 20),
        top_margin_H1=4.0,
        transverse_width_T1=9.0,
        upright_length_W1=5.0,
        base_length_L1=25.0,
        base_thickness_S=6.0,
        mount_hole_pitch_P=10.0,
        first_hole_offset_G1=10.0,
        counterbore_diameter_d1=6.5,
        through_hole_diameter_d2=3.5,
        counterbore_depth_l=3.5,
    ),
    dict(
        m_values=(5, 6),
        h_choices=(15, 20),
        top_margin_H1=6.0,
        transverse_width_T1=12.0,
        upright_length_W1=8.0,
        base_length_L1=32.0,
        base_thickness_S=8.0,
        mount_hole_pitch_P=10.0,
        first_hole_offset_G1=15.0,
        counterbore_diameter_d1=8.0,
        through_hole_diameter_d2=4.5,
        counterbore_depth_l=4.5,
    ),
    dict(
        m_values=(8, 10, 12),
        h_choices=(25, 30, 35),
        top_margin_H1=10.0,
        transverse_width_T1=22.0,
        upright_length_W1=10.0,
        base_length_L1=44.0,
        base_thickness_S=10.0,
        mount_hole_pitch_P=16.0,
        first_hole_offset_G1=20.0,
        counterbore_diameter_d1=11.0,
        through_hole_diameter_d2=6.5,
        counterbore_depth_l=6.5,
    ),
    dict(
        m_values=(16, 20),
        h_choices=(35, 40),
        top_margin_H1=15.0,
        transverse_width_T1=30.0,
        upright_length_W1=15.0,
        base_length_L1=65.0,
        base_thickness_S=15.0,
        mount_hole_pitch_P=30.0,
        first_hole_offset_G1=25.0,
        counterbore_diameter_d1=14.0,
        through_hole_diameter_d2=9.0,
        counterbore_depth_l=9.0,
    ),
)

DIFFICULTY_M = {
    "easy": [3, 4, 5, 6],
    "medium": [3, 4, 5, 6, 8, 10, 12],
    "hard": [3, 4, 5, 6, 8, 10, 12, 16, 20],
}

CATALOG_DIMENSION_KEYS = (
    "top_margin_H1",
    "transverse_width_T1",
    "upright_length_W1",
    "base_length_L1",
    "base_thickness_S",
    "mount_hole_pitch_P",
    "first_hole_offset_G1",
    "counterbore_diameter_d1",
    "through_hole_diameter_d2",
    "counterbore_depth_l",
)

REFINED_KEYS = (
    "thread_axis_height_H",
    *CATALOG_DIMENSION_KEYS,
    "top_chamfer_C",
    "internal_fillet_R",
)


def _group_for_m(value):
    nominal = int(round(float(value)))
    if abs(float(value) - nominal) > 1e-9:
        return None
    for group in CATALOG_GROUPS:
        if nominal in group["m_values"]:
            return group
    return None


def _groups_for_difficulty(difficulty):
    allowed = set(DIFFICULTY_M[difficulty])
    return [group for group in CATALOG_GROUPS if allowed.intersection(group["m_values"])]


def _dimension_range(name):
    return {
        difficulty: (
            min(group[name] for group in _groups_for_difficulty(difficulty)),
            max(group[name] for group in _groups_for_difficulty(difficulty)),
        )
        for difficulty in DIFFICULTY_M
    }


def _height_range():
    return {
        difficulty: (
            min(h for group in _groups_for_difficulty(difficulty) for h in group["h_choices"]),
            max(h for group in _groups_for_difficulty(difficulty) for h in group["h_choices"]),
        )
        for difficulty in DIFFICULTY_M
    }


PARAM_SPEC = {
    "thread_nominal_d_M": dict(
        desc="nominal diameter M of the simplified horizontal threaded through bore",
        unit="mm",
        range={d: (min(v), max(v)) for d, v in DIFFICULTY_M.items()},
        choices=DIFFICULTY_M,
        coverage=[3, 4, 5, 6, 8, 10, 12, 16, 20],
        integer=True,
        source=f"{CATALOG_SOURCE}; nominal M rows",
    ),
    "thread_axis_height_H": dict(
        desc="height H from the base underside to the horizontal threaded-hole axis",
        unit="mm",
        range=_height_range(),
        coverage=[15, 20, 25, 30, 35, 40],
        integer=True,
        refine=True,
        source=f"{CATALOG_SOURCE}; H Selection values permitted by the selected M group",
    ),
    "top_margin_H1": dict(
        desc="top margin H1 from the threaded-hole axis to the upright top",
        unit="mm",
        range=_dimension_range("top_margin_H1"),
        refine=True,
        source=f"{CATALOG_SOURCE}; H1 column for the selected M group",
    ),
    "transverse_width_T1": dict(
        desc="overall transverse body width T1",
        unit="mm",
        range=_dimension_range("transverse_width_T1"),
        refine=True,
        source=f"{CATALOG_SOURCE}; T1 column for the selected M group",
    ),
    "upright_length_W1": dict(
        desc="upright leg thickness W1 measured along the base length",
        unit="mm",
        range=_dimension_range("upright_length_W1"),
        refine=True,
        source=f"{CATALOG_SOURCE}; W1 column for the selected M group",
    ),
    "base_length_L1": dict(
        desc="overall base length L1",
        unit="mm",
        range=_dimension_range("base_length_L1"),
        refine=True,
        source=f"{CATALOG_SOURCE}; L1 column for the selected M group",
    ),
    "base_thickness_S": dict(
        desc="base thickness S",
        unit="mm",
        range=_dimension_range("base_thickness_S"),
        refine=True,
        source=f"{CATALOG_SOURCE}; S column for the selected M group",
    ),
    "mount_hole_pitch_P": dict(
        desc="center distance P between the two vertical mounting holes",
        unit="mm",
        range=_dimension_range("mount_hole_pitch_P"),
        refine=True,
        source=f"{CATALOG_SOURCE}; P column for the selected M group",
    ),
    "first_hole_offset_G1": dict(
        desc="distance G1 from the upright outer end to the first mounting-hole center",
        unit="mm",
        range=_dimension_range("first_hole_offset_G1"),
        refine=True,
        source=f"{CATALOG_SOURCE}; G1 column for the selected M group",
    ),
    "counterbore_diameter_d1": dict(
        desc="diameter d1 of each vertical mounting-hole counterbore",
        unit="mm",
        range=_dimension_range("counterbore_diameter_d1"),
        refine=True,
        source=f"{CATALOG_SOURCE}; d1 counterbore column for the selected M group",
    ),
    "through_hole_diameter_d2": dict(
        desc="diameter d2 of each vertical mounting through-hole",
        unit="mm",
        range=_dimension_range("through_hole_diameter_d2"),
        refine=True,
        source=f"{CATALOG_SOURCE}; d2 through-hole column for the selected M group",
    ),
    "counterbore_depth_l": dict(
        desc="depth l of each counterbore measured down from the base top",
        unit="mm",
        range=_dimension_range("counterbore_depth_l"),
        refine=True,
        source=f"{CATALOG_SOURCE}; counterbore depth l column for the selected M group",
    ),
    "top_chamfer_C": dict(
        desc="size C of each of the two catalog 2-C2 upright top chamfers",
        unit="mm",
        range={"easy": (2.0, 2.0), "medium": (2.0, 2.0), "hard": (2.0, 2.0)},
        refine=True,
        source=f"{CATALOG_SOURCE}; drawing callout 2-C2",
    ),
    "internal_fillet_R": dict(
        desc="modeled internal junction fillet radius R within the R2-or-less callout",
        unit="mm",
        range={"easy": (1.5, 1.5), "medium": (1.5, 1.5), "hard": (1.5, 1.5)},
        refine=True,
        source=(
            f"{CATALOG_SOURCE}; drawing bound R<=2 mm; R1.5 is a documented "
            "modeling convention"
        ),
    ),
}


def refine(p, difficulty, rng):
    group = _group_for_m(p["thread_nominal_d_M"])
    if group is None:
        return

    # H is the only second-stage catalog choice. Every other dimension is
    # copied from the same grouped row, so cross-row mixtures are impossible.
    p["thread_axis_height_H"] = int(rng.choice(group["h_choices"]))
    for name in CATALOG_DIMENSION_KEYS:
        p[name] = group[name]
    p["top_chamfer_C"] = 2.0
    p["internal_fillet_R"] = 1.5


def check(p):
    group = _group_for_m(p["thread_nominal_d_M"])
    if group is None:
        return ["[catalog] thread_nominal_d_M does not select a MISUMI catalog group"]

    bad = []
    if p["thread_axis_height_H"] not in group["h_choices"]:
        bad.append("[catalog] H must be one of the selections permitted for the chosen M group")

    for name in CATALOG_DIMENSION_KEYS:
        if abs(float(p[name]) - float(group[name])) > 1e-9:
            bad.append(f"[catalog] {name} must match the selected MISUMI grouped row")
    if abs(float(p["top_chamfer_C"]) - 2.0) > 1e-9:
        bad.append("[catalog] top_chamfer_C must be 2 mm per drawing callout 2-C2")
    if abs(float(p["internal_fillet_R"]) - 1.5) > 1e-9:
        bad.append("[convention] internal_fillet_R must be the documented R1.5 model value")

    m = p["thread_nominal_d_M"]
    h = p["thread_axis_height_H"]
    h1 = p["top_margin_H1"]
    t1 = p["transverse_width_T1"]
    w1 = p["upright_length_W1"]
    l1 = p["base_length_L1"]
    s = p["base_thickness_S"]
    pitch = p["mount_hole_pitch_P"]
    g1 = p["first_hole_offset_G1"]
    d1 = p["counterbore_diameter_d1"]
    d2 = p["through_hole_diameter_d2"]
    depth = p["counterbore_depth_l"]
    chamfer = p["top_chamfer_C"]
    fillet = p["internal_fillet_R"]

    if not d1 > d2 > 0.0:
        bad.append("[geometry] d1 must exceed positive d2 for a counterbored through-hole")
    if not 0.0 < depth < s:
        bad.append("[geometry] counterbore depth l must leave positive base material")
    if d1 >= t1:
        bad.append("[geometry] counterbore diameter d1 must fit within transverse width T1")
    if pitch <= d1:
        bad.append("[geometry] mounting pitch P must keep the two counterbores separate")
    if g1 - d1 / 2.0 <= w1:
        bad.append("[geometry] first counterbore must clear the upright footprint")
    if g1 + pitch + d1 / 2.0 >= l1:
        bad.append("[geometry] second counterbore must remain inside the free base end")
    if m >= t1:
        bad.append("[geometry] nominal threaded bore M must fit within transverse width T1")
    if h - m / 2.0 <= s:
        bad.append("[geometry] threaded bore must leave material above base thickness S")
    if h1 <= m / 2.0:
        bad.append("[geometry] top margin H1 must contain the upper half of bore M")
    if l1 <= w1:
        bad.append("[geometry] base length L1 must extend beyond upright length W1")
    if chamfer <= 0.0 or chamfer >= min(t1 / 2.0, h1):
        bad.append("[geometry] C2 chamfers must fit within upright width and top margin")
    if fillet <= 0.0 or fillet > 2.0:
        bad.append("[catalog] internal fillet must satisfy the drawing bound R2 or less")
    if w1 + fillet >= g1 - d1 / 2.0:
        bad.append("[geometry] internal fillet must clear the first counterbore envelope")
    return bad
