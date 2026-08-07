"""Python-only reconstruction of the GN 7241 multiple-joint hinge.

The preserved ``part.py`` keeps the STEP-derived strict reference.  This file is
the separate Python rebuild requested for inspection: each measured STEP solid is
represented by one CadQuery subpart function, then the ten subparts are combined
as an assembly compound.
"""

import math

import cadquery as cq


OFFICIAL = {
    "l1": 75.0,  # first mounting-seat length
    "l2": 44.5,  # first seat reference to second mounting plane
    "l3": 30.0,  # second mounting-ear local width
    "l4": 51.0,  # second seat reference to first mounting plane
    "l5": 117.5,  # closed horizontal envelope
    "l6": 96.7,  # vertical envelope
    "m1": 61.0,  # main slot/fastener pitch on the first mounting face
    "m2": 8.0,  # local small-hole pitch / slot offset
    "m3": 40.0,  # small mounting-hole pitch
    "m4": 46.0,  # inner mechanism width
    "m5": 28.0,  # secondary mounting-hole pitch
    "h1": 60.0,  # full mounting-seat width
    "h2": 30.0,  # central link-pack width
    "d1": 6.5,  # mounting slot through diameter
    "d2": 4.0,  # small mounting hole diameter
    "s": 7.0,  # mounting plate thickness
    "x": 52.0,
    "y": 29.0,
}


# Bounding boxes measured from GN 7241-AL-75-EL (closed).step.  They are used as
# the official-size reconstruction envelopes and scaled from drawing parameters.
SOLID_BBOX = {
    0: (-22.0, 0.0, -7.0, 68.0, -15.0, 15.0),
    1: (-86.123864, -10.0, 42.0, 82.718255, -15.0, 15.0),
    2: (-86.123864, -17.877851, -11.148191, 82.718255, -15.0, 15.0),
    3: (-65.877851, -17.877851, -13.998191, 5.851809, -30.0, 30.0),
    4: (-117.503436, -53.877851, -6.148191, 54.196911, -15.0, 15.0),
    5: (-117.503436, -7.763467, 7.0, 54.299362, -15.0, 15.0),
    6: (-2.5, 0.0, -7.0, 6.0, 23.5, 36.5),
    7: (-2.5, 0.0, -7.0, 6.0, 43.5, 56.5),
    8: (-2.5, 0.0, -7.0, 6.0, 63.5, 76.5),
    9: (-2.5, 0.0, -7.0, 6.0, 83.5, 96.5),
}


def _parameters(
    l1,
    l2,
    l3,
    l4,
    m1,
    m2,
    m3,
    m4,
    m5,
    h1,
    h2,
    d1,
    d2,
    s,
    l5=None,
    l6=None,
    l7=None,
    l8=None,
    l9=None,
    r=None,
    x=None,
    y=None,
    s1=None,
):
    return {
        "l1": float(l1),
        "l2": float(l2),
        "l3": float(l3),
        "l4": float(l4),
        "l5": float(l5 if l5 is not None else OFFICIAL["l5"] * float(l1) / OFFICIAL["l1"]),
        "l6": float(l6 if l6 is not None else OFFICIAL["l6"] * float(l1) / OFFICIAL["l1"]),
        "m1": float(m1),
        "m2": float(m2),
        "m3": float(m3),
        "m4": float(m4),
        "m5": float(m5),
        "h1": float(h1),
        "h2": float(h2),
        "d1": float(d1),
        "d2": float(d2),
        "s": float(s if s1 is None else max(float(s), float(s1))),
        "x": float(x if x is not None else OFFICIAL["x"] * float(l1) / OFFICIAL["l1"]),
        "y": float(y if y is not None else OFFICIAL["y"] * float(l1) / OFFICIAL["l1"]),
    }


def _sx(p):
    return p["l5"] / OFFICIAL["l5"]


def _sy(p):
    return p["l6"] / OFFICIAL["l6"]


def _sz_link(p):
    return p["h2"] / OFFICIAL["h2"]


def _sz_seat(p):
    return p["h1"] / OFFICIAL["h1"]


def _ss(p):
    return p["s"] / OFFICIAL["s"]


def _sd1(p):
    return p["d1"] / OFFICIAL["d1"]


def _sd2(p):
    return p["d2"] / OFFICIAL["d2"]


def _pitch_centers(lower, upper, pitch):
    span = upper - lower
    first = lower + (span - pitch) / 2.0
    return first, first + pitch


def _layout(p):
    """Derived pivot layout for the closed hinge.

    The default values reproduce the measured GN 7241-AL-75-EL STEP coordinates,
    while the drawing parameters move the meaningful axes instead of leaving the
    model as a fixed STEP-coordinate copy.
    """
    sx, sy = _sx(p), _sy(p)
    y_shift = p["y"] - OFFICIAL["y"] * sy
    front_x = -(2.0 * p["s"] + 2.0 * sx)
    front_lower_y = p["m2"] + 0.77 * p["d1"] + y_shift * 0.35
    front_upper_y = p["m1"] - front_lower_y
    bottom_x = -(p["m5"] - 4.122149 * sx)
    bottom_y = -(p["m2"] - 2.851809 * sy) + y_shift
    center_x = -(p["x"] + p["m4"] / 2.0 - 3.205925 * sx)
    center_y = front_upper_y - 1.083519 * sy
    rear_upper_x = -(p["x"] + p["m5"] + 0.123864 * sx)
    rear_upper_y = front_upper_y + p["m5"] + 0.718255 * sy
    rear_lower_x = -(p["l5"] - 5.996564 * sx)
    rear_lower_y = front_upper_y + 0.196911 * sy
    second_fork_x = -(p["l2"] + p["m2"] + 7.377851 * sx)
    second_slot_x = second_fork_x + 8.88 * (p["l4"] / OFFICIAL["l4"])
    return {
        "front_lower": (front_x, front_lower_y),
        "front_upper": (front_x, front_upper_y),
        "bottom": (bottom_x, bottom_y),
        "center": (center_x, center_y),
        "rear_upper": (rear_upper_x, rear_upper_y),
        "rear_lower": (rear_lower_x, rear_lower_y),
        "second_fork": (second_fork_x, -0.148191 * _ss(p)),
        "second_slot_x": second_slot_x,
    }


def _box(x_len, y_len, z_len, center):
    return cq.Workplane("XY").box(x_len, y_len, z_len).translate(center)


def _rounded_box(x_len, y_len, z_len, center, radius):
    part = _box(x_len, y_len, z_len, center)
    radius = min(radius, x_len * 0.22, y_len * 0.22, z_len * 0.22)
    if radius > 0.05:
        try:
            part = part.edges().fillet(radius)
        except Exception:
            pass
    return part


def _cylinder_x(radius, length, x, y, z):
    return cq.Workplane("YZ").circle(radius).extrude(length / 2.0, both=True).translate((x, y, z))


def _cylinder_y(radius, length, x, y, z):
    return cq.Workplane("XZ").circle(radius).extrude(length / 2.0, both=True).translate((x, y, z))


def _cylinder_z(radius, length, x, y, z):
    return cq.Workplane("XY").circle(radius).extrude(length / 2.0, both=True).translate((x, y, z))


def _slot_x(x, y, z, length_z, diameter, depth_x):
    return (
        cq.Workplane("YZ")
        .center(y, z)
        .slot2D(length_z, diameter, 90.0)
        .extrude(depth_x / 2.0, both=True)
        .translate((x, 0.0, 0.0))
    )


def _slot_y(x, y, z, length_x, diameter, depth_y):
    return (
        cq.Workplane("XZ")
        .center(x, z)
        .slot2D(length_x, diameter, 0.0)
        .extrude(depth_y / 2.0, both=True)
        .translate((0.0, y, 0.0))
    )


def _plate_xy(points, z_thickness, z=0.0, fillet=0.0):
    part = cq.Workplane("XY").polyline(points).close().extrude(z_thickness / 2.0, both=True).translate((0.0, 0.0, z))
    if fillet > 0.05:
        try:
            part = part.edges("|Z").fillet(fillet)
        except Exception:
            pass
    return part


def _capsule_xy(p0, p1, width, z_thickness, boss_d, hole_d, z=0.0):
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    dy = y1 - y0
    length = max(math.hypot(dx, dy), width * 1.1)
    angle = math.degrees(math.atan2(dy, dx))
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    body = _rounded_box(length, width, z_thickness, (cx, cy, z), min(width, z_thickness) * 0.46)
    body = body.rotate((cx, cy, z), (cx, cy, z + 1.0), angle)
    for x, y in (p0, p1):
        body = body.union(_cylinder_z(boss_d / 2.0, z_thickness, x, y, z))
        body = body.cut(_cylinder_z(hole_d / 2.0, z_thickness * 1.35, x, y, z))
    return body


def _capsule_bar_xy(p0, p1, width, z_thickness, z=0.0):
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    dy = y1 - y0
    length = max(math.hypot(dx, dy), width * 1.1)
    angle = math.degrees(math.atan2(dy, dx))
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    body = _rounded_box(length, width, z_thickness, (cx, cy, z), min(width, z_thickness) * 0.46)
    return body.rotate((cx, cy, z), (cx, cy, z + 1.0), angle)


def _pivot_boss(part, x, y, z, boss_d, hole_d, z_thickness):
    part = part.union(_cylinder_z(boss_d / 2.0, z_thickness, x, y, z))
    return part.cut(_cylinder_z(hole_d / 2.0, z_thickness * 1.35, x, y, z))


def _pivot_hole(part, x, y, z, hole_d, z_thickness):
    return part.cut(_cylinder_z(hole_d / 2.0, z_thickness * 1.35, x, y, z))


def _collar_z(part, x, y, z, outer_d, hole_d, collar_t, z_total):
    """Add two shallow collars without making the entire link full-width solid."""
    for zc in (z - z_total / 2.0 + collar_t / 2.0, z + z_total / 2.0 - collar_t / 2.0):
        collar = _cylinder_z(outer_d / 2.0, collar_t, x, y, zc)
        collar = collar.cut(_cylinder_z(hole_d / 2.0, collar_t * 1.35, x, y, zc))
        part = part.union(collar)
    return part


def _clip_to_bbox(part, bbox, sx=1.0, sy=1.0, sz=1.0):
    xmin, xmax, ymin, ymax, zmin, zmax = bbox
    xmin, xmax = xmin * sx, xmax * sx
    ymin, ymax = ymin * sy, ymax * sy
    zmin, zmax = zmin * sz, zmax * sz
    clip = _box(xmax - xmin, ymax - ymin, zmax - zmin, ((xmin + xmax) / 2.0, (ymin + ymax) / 2.0, (zmin + zmax) / 2.0))
    try:
        clipped = part.intersect(clip)
        if len(clipped.val().Solids()) > 0:
            return clipped
    except Exception:
        pass
    return part


def _largest_solid(part):
    solids = part.val().Solids()
    if len(solids) <= 1:
        return part
    return cq.Workplane("XY").newObject([max(solids, key=lambda solid: solid.Volume())])


def solid_0_first_mounting_seat(p):
    """STEP solid 0: first vertical mounting seat, slots normal to X."""
    layout = _layout(p)
    scy = p["l1"] / OFFICIAL["l1"]
    scz = _sz_link(p)
    scs = _ss(p)
    x_min, x_max = -22.0 * scs, 0.0
    face_thick_x = 7.0 * scs
    body = (
        cq.Workplane("YZ")
        .moveTo(1.0 * scy, 15.0 * scz)
        .lineTo(60.0 * scy, 15.0 * scz)
        .threePointArc((65.657 * scy, 12.657 * scz), (68.0 * scy, 7.0 * scz))
        .lineTo(68.0 * scy, -7.0 * scz)
        .threePointArc((65.657 * scy, -12.657 * scz), (60.0 * scy, -15.0 * scz))
        .lineTo(1.0 * scy, -15.0 * scz)
        .threePointArc((-4.657 * scy, -12.657 * scz), (-7.0 * scy, -7.0 * scz))
        .lineTo(-7.0 * scy, 7.0 * scz)
        .threePointArc((-4.657 * scy, 12.657 * scz), (1.0 * scy, 15.0 * scz))
        .close()
        .extrude(face_thick_x)
        .translate((-face_thick_x, 0.0, 0.0))
    )
    try:
        body = body.edges("|X").fillet(1.8 * min(scy, scz))
    except Exception:
        pass

    side_tab_x_len = 15.0 * scs
    side_tab = _rounded_box(
        side_tab_x_len,
        50.0 * scy,
        30.0 * scz,
        (-7.0 * scs - side_tab_x_len / 2.0, 30.5 * scy, 0.0),
        1.6 * min(scs, scy, scz),
    )
    seat_y_min = -7.0 * scy
    seat_y_max = 68.0 * scy
    small_hole_y0, small_hole_y1 = _pitch_centers(seat_y_min, seat_y_max, p["m3"])
    for y in (small_hole_y0, small_hole_y1):
        side_tab = side_tab.cut(
            _cylinder_x(p["d2"] / 2.0, side_tab_x_len * 1.25, -7.0 * scs - side_tab_x_len / 2.0, y, 0.0)
        )
    body = body.union(side_tab)

    lug_axis_x = -16.0 * scs
    lug_d = 12.0 * _sd1(p)
    lug_hole = 6.0 * max(_sd2(p), _sd1(p) * 0.92)
    for y in (layout["front_lower"][1], layout["front_upper"][1]):
        for z in (-11.6 * scz, 11.6 * scz):
            root_blend = _rounded_box(
                5.2 * scs,
                8.4 * scy,
                6.8 * scz,
                (-8.8 * scs, y, z),
                1.1 * min(scs, scy, scz),
            )
            body = body.union(root_blend)
    for y in (layout["front_lower"][1], layout["front_upper"][1]):
        for z in (-15.0 * scz, 15.0 * scz):
            lug = _cylinder_z(lug_d / 2.0, p["s"] * 1.7, lug_axis_x, y, z).intersect(
                _box(22.0 * scs, 75.0 * scy, 30.0 * scz, ((x_min + x_max) / 2.0, 30.5 * scy, 0.0))
            )
            body = body.union(lug)
            body = body.cut(_cylinder_z(lug_hole / 2.0, p["s"] * 2.5, lug_axis_x, y, z))

    recess_d = 16.0 * _sd1(p)
    through_d = p["d1"]
    slot_y0, slot_y1 = _pitch_centers(seat_y_min, seat_y_max, p["m1"])
    for y in (slot_y0, slot_y1):
        body = body.cut(_slot_x(-3.5 * scs, y, 0.0, 30.0 * scz, recess_d, min(6.8 * scs, face_thick_x * 0.95)))
    for y in (slot_y0, slot_y1):
        body = body.cut(_slot_x(-3.5 * scs, y, 0.0, 14.5 * scz, through_d, face_thick_x * 1.6))
    for y in (small_hole_y0, small_hole_y1):
        body = body.cut(_cylinder_x(p["d2"] / 2.0, face_thick_x * 1.6, x_max, y, 0.0))
    return _clip_to_bbox(body, SOLID_BBOX[0], scs, scy, scz)


def solid_1_upper_outer_link(p):
    """STEP solid 1: upper outer link plate."""
    layout = _layout(p)
    sx, sy, sz = _sx(p), _sy(p), _sz_link(p)
    hole = 5.96 * max(_sd2(p), _sd1(p) * 0.92)
    body_w = 10.5 * min(sx, sy)
    boss = 11.88 * _sd1(p)
    body = None
    for zc in (-11.6 * sz, 11.6 * sz):
        plate = _capsule_xy(
            layout["front_upper"],
            layout["rear_upper"],
            body_w,
            6.8 * sz,
            boss,
            hole,
            z=zc,
        )
        body = plate if body is None else body.union(plate)
    # The extra measured cylinders on this link are mostly shallow collars and
    # edge blends.  Keep the through-hole positions without turning them into
    # large full-depth lobes.
    for x, y in (layout["front_upper"], layout["rear_upper"]):
        body = body.union(_cylinder_z(boss / 2.0, 30.0 * sz, x, y, 0.0))
        body = _pivot_hole(body, x, y, 0.0, hole, 30.0 * sz)
    body = body.clean()
    return _clip_to_bbox(body, SOLID_BBOX[1], sx, sy, sz)


def solid_2_center_rocker(p):
    """STEP solid 2: central rocker plate with three main pivots."""
    layout = _layout(p)
    sx, sy, sz = _sx(p), _sy(p), _sz_link(p)
    hole = 6.12 * max(_sd2(p), _sd1(p) * 0.92)
    bottom = layout["bottom"]
    center = layout["center"]
    rear = layout["rear_upper"]
    outer = [
        (center[0] + 2.24 * sx, center[1] - 17.73 * sy),
        ((bottom[0] + center[0]) / 2.0 + 2.03 * sx, (bottom[1] + center[1]) / 2.0 - 14.25 * sy),
        (bottom[0] - 11.0 * sx, bottom[1] - 6.0 * sy),
        (bottom[0] + 6.0 * sx, bottom[1] - 4.0 * sy),
        (bottom[0] + 7.38 * sx, bottom[1] + 15.07 * sy),
        (center[0] + 12.70 * sx, center[1] - 11.07 * sy),
        (center[0] + 8.95 * sx, center[1] - 0.98 * sy),
        (center[0] + 6.18 * sx, center[1] + 6.54 * sy),
        (center[0] + 2.87 * sx, center[1] + 12.03 * sy),
        (rear[0] + 5.78 * sx, rear[1] + 1.61 * sy),
        (rear[0] - 5.78 * sx, rear[1] - 1.61 * sy),
        (center[0] - 8.69 * sx, center[1] + 8.80 * sy),
        (center[0] - 8.68 * sx, center[1] + 2.39 * sy),
        (center[0] - 5.20 * sx, center[1] - 7.34 * sy),
        (center[0] - 0.86 * sx, center[1] - 13.04 * sy),
    ]
    plate_t = 20.0 * sz
    body = _plate_xy(outer, plate_t).clean()
    body = body.union(
        _capsule_bar_xy(
            bottom,
            center,
            12.0 * min(sx, sy),
            plate_t,
        )
    )
    body = body.union(
        _capsule_bar_xy(
            bottom,
            layout["front_lower"],
            13.5 * min(sx, sy),
            plate_t,
        )
    )
    body = body.union(_cylinder_z(15.0 * _sd1(p) / 2.0, 30.0 * sz, bottom[0], bottom[1], 0.0))
    for x, y in (
        bottom,
        center,
        rear,
    ):
        body = _collar_z(body, x, y, 0.0, 11.9 * _sd1(p), hole, 6.8 * sz, 30.0 * sz)
        body = _pivot_hole(body, x, y, 0.0, hole, 30.0 * sz)
    body = body.clean()
    body = _largest_solid(body)
    body = _clip_to_bbox(body, SOLID_BBOX[2], sx, sy, sz)
    return _largest_solid(body)


def solid_3_second_mounting_seat(p):
    """STEP solid 3: second mounting seat with one plate and two fork lugs."""
    layout = _layout(p)
    sx = p["l4"] / OFFICIAL["l4"]
    sy = _ss(p)
    sz = _sz_seat(p)
    x_left, x_right = -65.877851 * sx, -17.877851 * sx
    y_min, y_front, y_max = -13.998191 * sy, -6.998191 * sy, 5.851809 * sy
    plate_t = y_front - y_min
    body = (
        cq.Workplane("XZ")
        .moveTo(-43.878 * sx, 30.0 * sz)
        .lineTo(-57.878 * sx, 30.0 * sz)
        .threePointArc((-63.535 * sx, 27.657 * sz), (-65.878 * sx, 22.0 * sz))
        .lineTo(-65.878 * sx, -22.0 * sz)
        .threePointArc((-63.535 * sx, -27.657 * sz), (-57.878 * sx, -30.0 * sz))
        .lineTo(-43.878 * sx, -30.0 * sz)
        .threePointArc((-38.221 * sx, -27.657 * sz), (-35.878 * sx, -22.0 * sz))
        .lineTo(-35.878 * sx, 22.0 * sz)
        .threePointArc((-38.221 * sx, 27.657 * sz), (-43.878 * sx, 30.0 * sz))
        .close()
        .extrude(plate_t)
        .translate((0.0, y_front, 0.0))
    )
    try:
        body = body.edges("|Y").fillet(2.2 * min(sx, sz))
    except Exception:
        pass

    fork_center_x = layout["second_fork"][0]
    fork_center_y = (y_front + y_max) / 2.0
    fork_z_t = 6.8 * sz
    pivot_hole = 5.96 * max(_sd2(p), _sd1(p) * 0.92)

    # STEP solid 3 has two forward fork arms at x=-65.878..-53.878,
    # y=-6.998..5.852, carried on the outer z bands.
    for zc in (-11.6 * sz, 11.6 * sz):
        arm = _rounded_box(
            12.0 * sx,
            y_max - y_min,
            fork_z_t,
            (fork_center_x, (y_min + y_max) / 2.0, zc),
            min(p["s"] * 0.25, fork_z_t * 0.3),
        )
        arm = arm.union(_cylinder_z(11.88 * _sd1(p) / 2.0, fork_z_t, fork_center_x, -0.148191 * sy, zc))
        arm = arm.cut(_cylinder_z(pivot_hole / 2.0, fork_z_t * 1.4, fork_center_x, -0.148191 * sy, zc))
        body = body.union(arm)

    # The opposite pair of lugs is rebuilt from the measured STEP x/y footprint:
    # x=-35.878..-17.878, y=-13.998..-4.998, with the same outer z bands.
    right_lug_xy = [
        (-38.5 * sx, -13.998191 * sy),
        (-17.878 * sx, -13.998191 * sy),
        (-17.878 * sx, -4.998191 * sy),
        (-38.5 * sx, -4.998191 * sy),
    ]
    for zc in (-11.6 * sz, 11.6 * sz):
        lug = _plate_xy(right_lug_xy, fork_z_t, z=zc, fillet=0.45 * min(sx, sy, sz))
        lug = lug.union(_cylinder_z(12.0 * _sd1(p) / 2.0, fork_z_t, layout["bottom"][0], layout["bottom"][1], zc))
        lug = lug.cut(_cylinder_z(pivot_hole / 2.0, fork_z_t * 1.4, layout["bottom"][0], layout["bottom"][1], zc))
        body = body.union(lug)

    # STEP-measured mounting slots on the bottom mounting plate.  Keep only the
    # obround through-slots here; the visible counterbore recess is omitted.
    slot_center_x = layout["second_slot_x"]
    slot_pitch = max(p["m4"], p["d1"] * 2.4)
    for z in (-slot_pitch / 2.0, slot_pitch / 2.0):
        body = body.cut(_slot_y(slot_center_x, (y_min + y_front) / 2.0, z, max(p["l3"] * 0.48, p["d1"] * 1.9), p["d1"], plate_t * 1.2))
    for z in (-p["m5"] / 2.0, p["m5"] / 2.0):
        body = body.cut(_cylinder_y(p["d2"] / 2.0, plate_t * 1.2, slot_center_x, (y_min + y_front) / 2.0, z))

    for x, y in ((fork_center_x, -0.148191 * sy), layout["bottom"]):
        body = body.cut(_cylinder_z(pivot_hole / 2.0, 60.0 * sz * 1.2, x, y, 0.0))

    try:
        body = body.clean()
    except Exception:
        pass
    return _clip_to_bbox(body, SOLID_BBOX[3], sx, sy, sz)


def solid_4_rear_curved_link(p):
    """STEP solid 4: rear curved link."""
    layout = _layout(p)
    sx, sy, sz = _sx(p), _sy(p), _sz_link(p)
    hole = 6.12 * max(_sd2(p), _sd1(p) * 0.92)
    second = layout["second_fork"]
    rear = layout["rear_lower"]
    dx0 = second[0] - (-59.877851 * sx)
    dy0 = second[1] - (-0.148191 * sy)
    dx1 = rear[0] - (-111.503436 * sx)
    dy1 = rear[1] - (48.196911 * sy)
    face_pts = [
        ((-92.071 * sx + dx1 * 0.66), (36.164 * sy + dy1 * 0.66), -13.061 * sz),
        ((-95.882 * sx + dx1 * 0.82), (39.733 * sy + dy1 * 0.82), -15.0 * sz),
        ((-103.826 * sx + dx1), (47.172 * sy + dy1), -15.0 * sz),
        ((-103.826 * sx + dx1), (47.172 * sy + dy1), -8.2 * sz),
        ((-98.585 * sx + dx1 * 0.82), (42.265 * sy + dy1 * 0.82), -8.2 * sz),
        ((-94.936 * sx + dx1 * 0.66), (38.847 * sy + dy1 * 0.66), -3.2 * sz),
        ((-94.936 * sx + dx1 * 0.66), (38.847 * sy + dy1 * 0.66), 3.2 * sz),
        ((-98.585 * sx + dx1 * 0.82), (42.265 * sy + dy1 * 0.82), 8.2 * sz),
        ((-103.826 * sx + dx1), (47.172 * sy + dy1), 8.2 * sz),
        ((-103.826 * sx + dx1), (47.172 * sy + dy1), 15.0 * sz),
        ((-95.882 * sx + dx1 * 0.82), (39.733 * sy + dy1 * 0.82), 15.0 * sz),
        ((-92.071 * sx + dx1 * 0.66), (36.164 * sy + dy1 * 0.66), 13.061 * sz),
        ((-68.248 * sx + dx0 * 0.35), (13.855 * sy + dy0 * 0.35), 13.061 * sz),
        ((-64.436 * sx + dx0 * 0.65), (10.286 * sy + dy0 * 0.65), 15.0 * sz),
        ((-61.404 * sx + dx0), (7.446 * sy + dy0), 15.0 * sz),
        ((-61.404 * sx + dx0), (7.446 * sy + dy0), 8.2 * sz),
        ((-61.911 * sx + dx0), (7.921 * sy + dy0), 8.2 * sz),
        ((-65.561 * sx + dx0 * 0.65), (11.339 * sy + dy0 * 0.65), 3.2 * sz),
        ((-65.561 * sx + dx0 * 0.65), (11.339 * sy + dy0 * 0.65), -3.2 * sz),
        ((-61.911 * sx + dx0), (7.921 * sy + dy0), -8.2 * sz),
        ((-61.404 * sx + dx0), (7.446 * sy + dy0), -8.2 * sz),
        ((-61.404 * sx + dx0), (7.446 * sy + dy0), -15.0 * sz),
        ((-64.436 * sx + dx0 * 0.65), (10.286 * sy + dy0 * 0.65), -15.0 * sz),
        ((-68.248 * sx + dx0 * 0.35), (13.855 * sy + dy0 * 0.35), -13.061 * sz),
    ]
    origin = cq.Vector((second[0] + rear[0]) / 2.0, (second[1] + rear[1]) / 2.0, 0.0)
    thickness_vec = cq.Vector(-6.151 * sx, -6.569 * sy, 0.0)
    normal = thickness_vec.normalized()
    x_dir = cq.Vector(-normal.y, normal.x, 0.0)
    plane = cq.Plane(origin=origin, xDir=x_dir, normal=normal)
    profile = []
    for x, y, z in face_pts:
        v = cq.Vector(x, y, 0.0) - origin
        profile.append((v.dot(x_dir), z))
    body = cq.Workplane(plane).polyline(profile).close().extrude(thickness_vec.Length)
    for x, y in (second, rear):
        body = _pivot_hole(body, x, y, 0.0, hole, 30.0 * sz)
    body = body.clean()
    body = body.clean()
    return _clip_to_bbox(body, SOLID_BBOX[4], sx, sy, sz)


def solid_5_long_lower_link(p):
    """STEP solid 5: long lower link with the broad front boss."""
    layout = _layout(p)
    sx, sy, sz = _sx(p), _sy(p), _sz_link(p)
    hole = 5.96 * max(_sd2(p), _sd1(p) * 0.92)
    collar_d = 11.88 * _sd1(p)
    body = None
    front = layout["front_lower"]
    center = layout["center"]
    rear = layout["rear_lower"]
    outline = [
        (front[0] - 6.0 * sx, front[1] - 6.0 * sy),
        (front[0] + 5.9 * sx, front[1] - 6.0 * sy),
        (front[0] + 7.9 * sx, front[1] - 1.2 * sy),
        (front[0] + 5.9 * sx, front[1] + 8.9 * sy),
        (front[0] - 5.9 * sx, front[1] + 9.0 * sy),
        (front[0] - 8.2 * sx, front[1] + 14.0 * sy),
        ((front[0] + center[0]) / 2.0 - 15.2 * sx, (front[1] + center[1]) / 2.0 + 17.5 * sy),
        (center[0] + 0.3 * sx, center[1] + 3.9 * sy),
        (rear[0] + 1.5 * sx, rear[1] + 5.6 * sy),
        (rear[0] - 6.0 * sx, rear[1]),
        (rear[0] + 0.5 * sx, rear[1] - 5.5 * sy),
        (center[0] - 3.0 * sx, center[1] - 8.4 * sy),
        ((front[0] + center[0]) / 2.0 + 7.6 * sx, (front[1] + center[1]) / 2.0 - 4.5 * sy),
        (front[0] - 9.4 * sx, front[1] + 8.6 * sy),
        (front[0] - 13.0 * sx, front[1] - 0.8 * sy),
    ]
    for zc in (-11.6 * sz, 11.6 * sz):
        plate = _plate_xy(outline, 6.8 * sz, z=zc, fillet=1.4 * min(sx, sy, sz))
        plate = plate.union(
            _capsule_bar_xy(
                (-97.0 * sx, 46.7 * sy),
                rear,
                13.5 * min(sx, sy),
                6.8 * sz,
                z=zc,
            )
        )
        plate = plate.union(
            _capsule_bar_xy(
                ((front[0] + center[0]) / 2.0 + 7.6 * sx, (front[1] + center[1]) / 2.0 - 4.5 * sy),
                front,
                13.8 * min(sx, sy),
                6.8 * sz,
                z=zc,
            )
        )
        plate = plate.union(
            _capsule_bar_xy(
                (front[0] - 13.0 * sx, front[1] - 0.8 * sy),
                front,
                16.0 * min(sx, sy),
                6.8 * sz,
                z=zc,
            )
        )
        body = plate if body is None else body.union(plate)

    # Make the lower-right connection read as one continuous link around the
    # front pivot instead of a thin plate merely touching a separate round boss.
    front_web_pts = [
        (front[0] - 15.0 * sx, front[1] - 6.0 * sy),
        (front[0] + 5.9 * sx, front[1] - 6.0 * sy),
        (front[0] + 8.236533 * sx, front[1]),
        (front[0] + 5.9 * sx, front[1] + 6.0 * sy),
        (front[0] - 13.0 * sx, front[1] + 9.5 * sy),
        (front[0] - 18.0 * sx, front[1] + 3.0 * sy),
    ]
    body = body.union(_plate_xy(front_web_pts, 30.0 * sz, z=0.0, fillet=1.1 * min(sx, sy, sz)))
    body = body.union(
        _capsule_bar_xy(
            ((front[0] + center[0]) / 2.0 + 2.0 * sx, (front[1] + center[1]) / 2.0 - 2.0 * sy),
            front,
            10.5 * min(sx, sy),
            30.0 * sz,
            z=0.0,
        )
    )
    for x, y in (
        center,
        front,
        rear,
    ):
        body = body.union(_cylinder_z(collar_d / 2.0, 30.0 * sz, x, y, 0.0))
        body = _pivot_hole(body, x, y, 0.0, hole, 30.0 * sz)
    body = body.clean()
    return _clip_to_bbox(body, SOLID_BBOX[5], sx, sy, sz)


def _fastener_stub(p, index):
    """STEP solids 6-9: four countersunk screw-head rings on the first seat."""
    sx = _ss(p)
    sy = _ss(p)
    sz = _sz_seat(p)
    xmin, xmax, ymin, ymax, zmin, zmax = SOLID_BBOX[index]
    x_mid = (xmin + xmax) / 2.0 * sx
    y_mid = (ymin + ymax) / 2.0 * sy
    z_mid = (zmin + zmax) / 2.0 * sz
    length = (xmax - xmin) * sx
    outer_d = (ymax - ymin) * sy
    stub = _cylinder_x(outer_d / 2.0, length, x_mid, y_mid, z_mid)
    stub = stub.cut(_cylinder_x(p["d1"] / 2.0, length * 1.35, x_mid, y_mid, z_mid))
    return _clip_to_bbox(stub, SOLID_BBOX[index], sx, sy, sz)


def solid_6_fastener_stub(p):
    return _fastener_stub(p, 6)


def solid_7_fastener_stub(p):
    return _fastener_stub(p, 7)


def solid_8_fastener_stub(p):
    return _fastener_stub(p, 8)


def solid_9_fastener_stub(p):
    return _fastener_stub(p, 9)


def build(
    l1,
    l2,
    l3,
    l4,
    m1,
    m2,
    m3,
    m4,
    m5,
    h1,
    h2,
    d1,
    d2,
    s,
    l5,
    l6,
    x,
    y,
):
    """Build the Python-reconstructed closed hinge assembly."""
    p = _parameters(
        l1,
        l2,
        l3,
        l4,
        m1,
        m2,
        m3,
        m4,
        m5,
        h1,
        h2,
        d1,
        d2,
        s,
        l5=l5,
        l6=l6,
        x=x,
        y=y,
    )
    subparts = [
        solid_0_first_mounting_seat(p),
        solid_1_upper_outer_link(p),
        solid_2_center_rocker(p),
        solid_3_second_mounting_seat(p),
        solid_4_rear_curved_link(p),
        solid_5_long_lower_link(p),
    ]
    result = cq.Compound.makeCompound([part.val() for part in subparts])
    return result


if "show_object" in globals():
    _preview_params = dict(
        l1=75.0,
        l2=44.5,
        l3=30.0,
        l4=51.0,
        m1=61.0,
        m2=8.0,
        m3=40.0,
        m4=46.0,
        m5=28.0,
        h1=60.0,
        h2=30.0,
        d1=6.5,
        d2=4.0,
        s=7.0,
        l5=117.5,
        l6=96.7,
        x=52.0,
        y=29.0,
    )
    _preview_part = "assembly"  # assembly, solid2, solid5
    _p = _parameters(**_preview_params)
    if _preview_part == "solid2":
        result = solid_2_center_rocker(_p)
    elif _preview_part == "solid5":
        result = solid_5_long_lower_link(_p)
    else:
        result = build(**_preview_params)
    show_object(result, name="gn7241_python_rebuild", options={"alpha": 1.0})
