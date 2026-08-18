"""Parametric GN 851.1 vertical latch toggle clamp assembly.

The supplied GN 851.1-160-T3 STEP reference separates into five visible solids:
the folded mounting frame, U-bolt latch, lower fork block, adjuster block, and
handle/linkage pack. This file rebuilds those solids parametrically from the
catalog row dimensions, using the 160-T3 STEP only as proportional reference for
undimensioned bends, bosses, ribs, and handle contours.

Coordinate convention follows the STEP reference used for comparison:
- X follows the handle/base length.
- Y is vertical height and latch adjustment travel.
- Z is the clamp width.
"""

import math

import cadquery as cq


REF = {
    "a1": 5.1,
    "a2": 24.9,
    "b1": 25.9,
    "l1": 68.1,
    "h1": 37.1,
    "b2": 35.1,
    "b3": 21.1,
    "b4": 25.4,
    "b5": 14.0,
    "d1": 4.0,
    "d2": 4.3,
    "h2": 9.9,
    "l2": 4.6,
    "m1": 22.1,
    "m2": 6.6,
    "m3": 13.0,
    "m4": 6.6,
    "m5": 14.2,
    "s": 2.0,
}


def _params(
    clamp_size,
    fit_clearance,
    a1,
    a2,
    b1,
    b2,
    b3,
    b4,
    b5,
    d1,
    d2,
    h1,
    h2,
    l1,
    l2,
    m1,
    m2,
    m3,
    m4,
    m5,
    s,
):
    return locals()


def _ref_scale(p):
    sx = float(p["l1"]) / REF["l1"]
    sy = float(p["h1"]) / REF["h1"]
    sz = float(p["b2"]) / REF["b2"]
    sd = float(p["d1"]) / REF["d1"]
    return sx, sy, sz, sd


def _pt(p, x, y, z):
    sx, sy, sz, _ = _ref_scale(p)
    return x * sx, y * sy, z * sz


def _min_scale(p):
    sx, sy, sz, _ = _ref_scale(p)
    return min(sx, sy, sz)


def _ratio(p, name):
    return float(p[name]) / REF[name]


def _u_leg_z(p):
    rod = float(p["d1"])
    return (float(p["b5"]) + rod * 1.65) / 2.0


def _fork_y_bounds(p):
    _, sy, _, _ = _ref_scale(p)
    y1 = -8.7 * sy
    return y1 - (float(p["b4"]) + 0.1 * sy), y1


def _box(x, y, z, center, fillet=0.0):
    solid = cq.Workplane("XY").box(x, y, z).translate(center)
    fillet = min(float(fillet), x * 0.16, y * 0.16, z * 0.16)
    if fillet > 0.05:
        try:
            solid = solid.edges("|Y").fillet(fillet)
        except Exception:
            pass
    return solid


def _plate_xy(points, thickness_z, z_center=0.0):
    return (
        cq.Workplane("XY")
        .polyline(points)
        .close()
        .extrude(thickness_z / 2.0, both=True)
        .translate((0.0, 0.0, z_center))
    )


def _oval_plate_xy(x_radius, y_radius, thickness_z, center):
    cx, cy, cz = center
    return (
        cq.Workplane("XY")
        .center(cx, cy)
        .ellipse(x_radius, y_radius)
        .extrude(thickness_z / 2.0, both=True)
        .translate((0.0, 0.0, cz))
    )


def _cyl_x(diameter, length, center):
    return cq.Workplane("YZ").circle(diameter / 2.0).extrude(length / 2.0, both=True).translate(center)


def _cyl_y(diameter, length, center):
    return cq.Workplane("XZ").circle(diameter / 2.0).extrude(length / 2.0, both=True).translate(center)


def _cyl_z(diameter, length, center):
    return cq.Workplane("XY").circle(diameter / 2.0).extrude(length / 2.0, both=True).translate(center)


def _hex_y(width, height, center):
    r = width / 2.0
    pts = [
        (math.cos(math.pi / 6.0 + i * math.pi / 3.0) * r, math.sin(math.pi / 6.0 + i * math.pi / 3.0) * r)
        for i in range(6)
    ]
    return cq.Workplane("XZ").polyline(pts).close().extrude(height / 2.0, both=True).translate(center)


def _capsule_x(length, width_z, height_y, center):
    radius = width_z / 2.0
    straight = max(length - width_z, width_z * 0.20)
    solid = (
        cq.Workplane("XZ")
        .rect(straight, width_z)
        .extrude(height_y / 2.0, both=True)
        .union(cq.Workplane("XZ").circle(radius).extrude(height_y / 2.0, both=True).translate((-straight / 2.0, 0.0, 0.0)))
        .union(cq.Workplane("XZ").circle(radius).extrude(height_y / 2.0, both=True).translate((straight / 2.0, 0.0, 0.0)))
    )
    return solid.translate(center)


def _capsule_z(length_z, width_x, height_y, center):
    radius = width_x / 2.0
    straight = max(length_z - width_x, width_x * 0.20)
    solid = (
        cq.Workplane("XZ")
        .rect(width_x, straight)
        .extrude(height_y / 2.0, both=True)
        .union(cq.Workplane("XZ").circle(radius).extrude(height_y / 2.0, both=True).translate((0.0, 0.0, -straight / 2.0)))
        .union(cq.Workplane("XZ").circle(radius).extrude(height_y / 2.0, both=True).translate((0.0, 0.0, straight / 2.0)))
    )
    return solid.translate(center)


def _rounded_rect_xz(width_x, height_z, thickness_y, center, radius):
    solid = cq.Workplane("XY").box(width_x, thickness_y, height_z).translate(center)
    radius = min(float(radius), width_x * 0.20, height_z * 0.20)
    if radius > 0.05:
        try:
            solid = solid.edges("|Y").fillet(radius)
        except Exception:
            pass
    return solid


def solid_0_base_frame(p):
    """Folded mounting frame, base plate, triangular web, and upper pin boss."""

    sx, sy, sz, _ = _ref_scale(p)
    scale = _min_scale(p)
    hole = float(p["d2"])

    sheet_t = max(float(p["s"]), 0.8)

    web = (
        cq.Workplane("XY")
        .moveTo(-6.4 * sx, 0.0 * sy)
        .lineTo(-6.4 * sx, 7.6 * sy)
        .lineTo(6.6 * sx, 7.6 * sy)
        .lineTo(6.6 * sx, 20.6 * sy)
        .lineTo(12.1 * sx, 20.6 * sy)
        .lineTo(32.6 * sx, 0.1 * sy)
        .lineTo(32.6 * sx, -5.9 * sy)
        .lineTo(6.6 * sx, -5.9 * sy)
        .lineTo(6.6 * sx, -6.4 * sy)
        .lineTo(0.0 * sx, -6.4 * sy)
        .threePointArc((-3.5 * sx, -3.2 * sy), (-3.5 * sx, 0.0 * sy))
        .lineTo(-6.4 * sx, 0.0 * sy)
        .close()
        .extrude(sheet_t / 2.0, both=True)
    )

    cap_d = 7.0 * scale
    outer_cap = _cyl_z(cap_d, 3.6 * sz, _pt(p, 0.0, 0.0, 3.75))
    inner_cap = _cyl_z(cap_d, 3.6 * sz, _pt(p, 0.0, 0.0, -3.75))
    cap_crown = _cyl_z(cap_d * 0.86, 1.0 * sz, _pt(p, 0.0, 0.0, 5.0)).union(
        _cyl_z(cap_d * 0.86, 1.0 * sz, _pt(p, 0.0, 0.0, -5.0))
    )
    neck_length = max(1.3 * sz, 3.6 * sz / 2.0 - sheet_t / 2.0 + 0.2 * scale)
    neck_offset = sheet_t / 2.0 + neck_length / 2.0 - 0.1 * scale
    cap_necks = _cyl_z(cap_d * 0.72, neck_length, (0.0, 0.0, neck_offset)).union(
        _cyl_z(cap_d * 0.72, neck_length, (0.0, 0.0, -neck_offset))
    )
    part = web.union(outer_cap).union(inner_cap).union(cap_crown).union(cap_necks)

    fold_band = _box(36.0 * sx, 1.0 * sy, 5.0 * sz, _pt(p, 14.6, -6.45, 0.0), 0.12 * scale)
    part = part.union(fold_band)

    rail_len = 26.0 * _ratio(p, "b1")
    rail_y = 2.2 * sy
    rail_z = 15.1 * sz
    for zc in (-9.95 * sz, 9.95 * sz):
        rail = _rounded_rect_xz(rail_len, rail_z, rail_y, (19.6 * sx, -7.3 * sy, zc), 2.35 * scale)
        rail_inner_z = abs(zc) - rail_z / 2.0
        lip_z = max(0.8 * sz, rail_inner_z - sheet_t / 2.0 + 0.2 * scale)
        lip_center_z = math.copysign((sheet_t / 2.0 + rail_inner_z) / 2.0, zc)
        fold_lip = _box(rail_len, 0.5 * sy, lip_z, (19.6 * sx, -6.15 * sy, lip_center_z), 0.10 * scale)
        part = part.union(rail).union(fold_lip)

    first_hole_x = float(p["b1"]) - float(p["m2"]) - float(p["m3"]) / 2.0 + 0.3 * sx
    hole_xs = (first_hole_x, first_hole_x + float(p["m3"]))
    hole_zs = (-float(p["m1"]) / 2.0, float(p["m1"]) / 2.0)
    for hx in hole_xs:
        for hz in hole_zs:
            part = part.cut(_cyl_y(hole, 4.8 * sy, (hx, -7.4 * sy, hz)))

    side_hole = max(hole * 0.82, 3.5 * scale)
    part = part.cut(_cyl_z(side_hole, sheet_t * 1.6, _pt(p, 20.6, 5.6, 0.0)))

    return part


def solid_1_u_bolt(p):
    """Continuous round U-bolt latch rod for the T3 variant."""

    sx, sy, sz, _ = _ref_scale(p)
    rod = float(p["d1"])
    x = 1.7 * _ratio(p, "a1")
    z_half = _u_leg_z(p)
    z_sep = 2.0 * z_half
    fork_y0, _ = _fork_y_bounds(p)
    bend_bottom = fork_y0 - rod / 2.0 - 0.20 * _min_scale(p)
    free_end = 34.7 * sy
    corner_radius = min(max(rod * 1.05, z_sep * 0.18), z_sep * 0.28)
    tangent_y = bend_bottom + corner_radius

    # The catalog U-bolt is one bent round rod. Keep the two straight legs
    # tangent to two compact quarter-circle bends and a straight bottom span.
    # This follows the drawing's rounded-rectangle U profile rather than a
    # broad semicircle or a square three-cylinder junction.
    leg_length = free_end - tangent_y
    part = _cyl_y(rod, leg_length, (x, (free_end + tangent_y) / 2.0, -z_half)).union(
        _cyl_y(rod, leg_length, (x, (free_end + tangent_y) / 2.0, z_half))
    )

    bottom_span = z_sep - 2.0 * corner_radius
    part = part.union(_cyl_z(rod, bottom_span, (x, bend_bottom, 0.0)))

    corner_centers = (
        (x, tangent_y, -z_half + corner_radius, -1.0),
        (x, tangent_y, z_half - corner_radius, 1.0),
    )
    quadrant_size = corner_radius + rod
    for cx, cy, cz, side in corner_centers:
        bend = cq.Workplane("XY").newObject(
            [cq.Solid.makeTorus(corner_radius, rod / 2.0, (cx, cy, cz), (1.0, 0.0, 0.0))]
        )
        quadrant = _box(
            rod * 1.25,
            quadrant_size,
            quadrant_size,
            (
                cx,
                cy - quadrant_size / 2.0,
                cz + side * quadrant_size / 2.0,
            ),
        )
        part = part.union(bend.intersect(quadrant))

    return part


def solid_2_front_fork_block(p):
    """Lower C-shaped fork block with two side-facing holes."""

    sx, sy, sz, _ = _ref_scale(p)
    scale = _min_scale(p)
    hole = float(p["d2"])
    x0, x1 = -3.5 * sx, 6.5 * sx
    y0, y1 = _fork_y_bounds(p)
    z_half = 7.0 * _ratio(p, "b3")

    height = y1 - y0
    width = x1 - x0
    arm_t = 3.1 * sz
    left_web = _box(width * 0.34, height, 2.0 * z_half, (x0 + width * 0.17, (y0 + y1) / 2.0, 0.0), 0.35 * scale)
    top_arm = _box(width * 0.92, height, arm_t, (x0 + width * 0.54, (y0 + y1) / 2.0, z_half - arm_t / 2.0), 0.25 * scale)
    bottom_arm = _box(width * 0.92, height, arm_t, (x0 + width * 0.54, (y0 + y1) / 2.0, -z_half + arm_t / 2.0), 0.25 * scale)
    block = left_web.union(top_arm).union(bottom_arm)

    for y in (y0 + float(p["m4"]), y0 + float(p["m4"]) + float(p["m5"])):
        block = block.cut(_cyl_x(hole, width * 0.70, (x0 + width * 0.26, y, 0.0)))

    rib = _plate_xy(
        [
            (x0 + 0.8 * sx, y0 + 2.8 * sy),
            (x1 - 1.2 * sx, y0 + 18.5 * sy),
            (x0 + 0.8 * sx, y0 + 18.5 * sy),
        ],
        1.0 * sz,
        -6.5 * sz,
    )
    return block.union(rib)


def solid_3_adjuster_block(p):
    """Adjuster sleeve/block with two holes and connected nut-like bosses."""

    sx, sy, sz, _ = _ref_scale(p)
    scale = _min_scale(p)
    rod = float(p["d1"])
    hole = float(p["d2"])
    x = 1.7 * _ratio(p, "a1")
    y0 = float(p["h2"]) - 0.3 * sy
    y1 = float(p["a2"]) - 0.9 * sy
    z_half = 15.0 * sz
    y_mid = (y0 + y1) / 2.0

    tube = _cyl_z(max(rod * 2.0, 7.4 * scale), 2.0 * z_half, (x, y_mid, 0.0))
    web = _capsule_z(27.0 * sz, 4.8 * sx, y1 - y0, (x, y_mid, 0.0))
    part = tube.union(web)

    u_leg_z = _u_leg_z(p)
    for z in (-u_leg_z, u_leg_z):
        part = part.union(_box(4.8 * sx, y1 - y0, 2.3 * sz, (x, y_mid, z), 0.15 * scale))
        part = part.union(_cyl_y(max(hole * 1.45, rod * 1.55), 3.4 * sy, (x, y_mid, z)))
        part = part.union(_hex_y(max(hole * 1.65, rod * 1.65), 2.3 * sy, (x, y_mid, z)))
        for y in (y0 + 1.5 * sy, y1 - 1.5 * sy):
            part = part.union(_cyl_y(max(hole * 1.22, rod * 1.25), 3.4 * sy, (x, y, z)))
            part = part.union(_hex_y(max(hole * 1.35, rod * 1.35), 1.8 * sy, (x, y, z)))
        part = part.cut(_cyl_y(hole, (y1 - y0) * 1.45, (x, y_mid, z)))

    bore = _cyl_z(max(rod * 0.75, 2.8 * scale), 2.4 * z_half, (x, y_mid, 0.0))
    return part.cut(bore)


def solid_4_handle_linkage(p):
    """Pressed handle/linkage pack with split side cheeks, holes, and ribbed grip."""

    sx, sy, sz, _ = _ref_scale(p)
    scale = _min_scale(p)
    rod = float(p["d1"])
    hole = float(p["d2"])
    x0, x1 = -6.4 * sx, 61.8 * sx
    z_half = 8.25 * sz
    plate_t = max(1.6 * sz, float(p["s"]) * 0.82)
    bridge_z = 2.0 * z_half + 0.4 * sz
    zc = (-z_half + plate_t / 2.0, z_half - plate_t / 2.0)

    outer_pts = [
        (-5.7 * sx, 3.8 * sy),
        (-6.4 * sx, 0.8 * sy),
        (-6.1 * sx, -2.8 * sy),
        (-4.8 * sx, -5.6 * sy),
        (-1.8 * sx, -6.4 * sy),
        (4.8 * sx, -5.9 * sy),
        (8.8 * sx, -3.1 * sy),
        (10.4 * sx, 1.6 * sy),
        (10.1 * sx, 11.5 * sy),
        (29.8 * sx, 18.3 * sy),
        (40.8 * sx, 18.0 * sy),
        (48.8 * sx, 18.0 * sy),
        (54.8 * sx, 18.2 * sy),
        (58.8 * sx, 18.7 * sy),
        (61.0 * sx, 19.9 * sy),
        (61.6 * sx, 21.8 * sy),
        (61.4 * sx, 23.8 * sy),
        (60.8 * sx, 25.7 * sy),
        (59.8 * sx, 27.0 * sy),
        (29.8 * sx, 27.6 * sy),
        (7.2 * sx, 26.5 * sy),
        (-2.0 * sx, 20.2 * sy),
        (-6.4 * sx, 11.2 * sy),
    ]
    part = None
    for z in zc:
        side = _plate_xy(outer_pts, plate_t, z)
        side = side.union(_oval_plate_xy(7.0 * sx, 8.0 * sy, plate_t, (0.0 * sx, 0.2 * sy, z)))
        side = side.union(_oval_plate_xy(7.4 * sx, 6.8 * sy, plate_t, (1.0 * sx, 18.2 * sy, z)))
        side = side.union(_capsule_x(4.0 * sx, 1.8 * sz, 2.0 * sy, (60.0 * sx, 25.4 * sy, z)))
        for x, y, d in (
            (0.0, 0.0, 9.3 * scale),
            (1.0 * sx, 18.2 * sy, 9.1 * scale),
        ):
            side = side.union(_cyl_z(d, plate_t, (x, y, z)))
        rib = _plate_xy(
            [
                (-4.6 * sx, -4.5 * sy),
                (1.8 * sx, -1.8 * sy),
                (25.8 * sx, 18.9 * sy),
                (23.0 * sx, 20.2 * sy),
                (-4.2 * sx, 1.8 * sy),
            ],
            plate_t * 0.62,
            z,
        )
        side = side.union(rib)
        part = side if part is None else part.union(side)

    inner_pts = [
        (-6.2 * sx, 11.3 * sy),
        (-1.0 * sx, 20.0 * sy),
        (7.2 * sx, 25.7 * sy),
        (29.8 * sx, 26.4 * sy),
        (29.8 * sx, 27.6 * sy),
        (-6.2 * sx, 27.6 * sy),
    ]
    for z in (-5.0 * sz, 5.0 * sz):
        part = part.union(_plate_xy(inner_pts, max(1.05 * sz, plate_t * 0.62), z))

    upper_lip = _box(36.0 * sx, 1.2 * sy, 10.0 * sz, (11.8 * sx, 27.5 * sy, 0.0), 0.18 * scale)
    center_web = _box(8.0 * sx, 11.0 * sy, bridge_z, (24.0 * sx, 20.5 * sy, 0.0), 0.16 * scale)
    front_web = _box(4.0 * sx, 7.8 * sy, bridge_z, (11.8 * sx, 15.0 * sy, 0.0), 0.14 * scale)

    right_shell = (
        _box(23.0 * sx, 6.2 * sy, 7.8 * sz, (41.0 * sx, 24.0 * sy, 0.0), 0.20 * scale)
        .union(_box(13.0 * sx, 5.4 * sy, 8.0 * sz, (51.3 * sx, 24.4 * sy, 0.0), 0.18 * scale))
        .union(_box(6.2 * sx, 4.2 * sy, 8.0 * sz, (57.6 * sx, 24.8 * sy, 0.0), 0.12 * scale))
        .union(_capsule_x(float(p["l2"]) * (4.2 / REF["l2"]), 6.7 * sz, 6.8 * sy, (59.6 * sx, 25.0 * sy, 0.0)))
        .union(_box(28.0 * sx, 1.35 * sy, 13.6 * sz, (44.6 * sx, 28.0 * sy, 0.0), 0.16 * scale))
        .union(_capsule_x(5.4 * sx, 13.2 * sz, 1.55 * sy, (59.2 * sx, 27.6 * sy, 0.0)))
    )
    nose_tip = (
        _box(5.0 * sx, 4.6 * sy, 7.6 * sz, (57.9 * sx, 24.8 * sy, 0.0), 0.14 * scale)
        .union(_capsule_x(4.0 * sx, 6.0 * sz, 5.6 * sy, (59.9 * sx, 25.0 * sy, 0.0)))
        .cut(_box(6.0 * sx, 2.0 * sy, 8.4 * sz, (56.0 * sx, 21.7 * sy, 0.0), 0.08 * scale))
    )
    right_shell = right_shell.cut(_box(12.0 * sx, 2.4 * sy, 8.4 * sz, (47.8 * sx, 21.7 * sy, 0.0), 0.08 * scale))
    yoke_web = _box(2.0 * sx, 1.3 * sy, bridge_z, (29.8 * sx, 27.0 * sy, 0.0), 0.15 * scale)
    rear_pin = _cyl_z(max(rod * 0.76, 3.1 * scale), bridge_z, (43.8 * sx, 24.0 * sy, 0.0))
    part = (
        part.union(upper_lip)
        .union(center_web)
        .union(front_web)
        .union(right_shell)
        .union(nose_tip)
        .union(yoke_web)
        .union(rear_pin)
    )

    for x, y, d in (
        (0.0, 0.0, hole * 1.42),
        (1.0 * sx, 18.2 * sy, hole * 1.36),
        (43.8 * sx, 24.0 * sy, hole * 0.70),
    ):
        part = part.cut(_cyl_z(d, 22.0 * sz, (x, y, 0.0)))

    lower_relief = _plate_xy(
        [
            (7.5 * sx, 2.1 * sy),
            (11.6 * sx, 3.8 * sy),
            (23.0 * sx, 16.8 * sy),
            (20.8 * sx, 17.8 * sy),
            (7.5 * sx, 4.8 * sy),
        ],
        10.4 * sz,
    )
    part = part.cut(lower_relief)

    return part


def build(
    clamp_size,
    fit_clearance,
    a1,
    a2,
    b1,
    b2,
    b3,
    b4,
    b5,
    d1,
    d2,
    h1,
    h2,
    l1,
    l2,
    m1,
    m2,
    m3,
    m4,
    m5,
    s,
):
    p = _params(
        clamp_size,
        fit_clearance,
        a1,
        a2,
        b1,
        b2,
        b3,
        b4,
        b5,
        d1,
        d2,
        h1,
        h2,
        l1,
        l2,
        m1,
        m2,
        m3,
        m4,
        m5,
        s,
    )
    base_frame = solid_0_base_frame(p)
    u_bolt_latch = solid_1_u_bolt(p)
    front_fork_block = solid_2_front_fork_block(p)
    adjuster_block = solid_3_adjuster_block(p)
    handle_linkage = solid_4_handle_linkage(p).cut(base_frame).cut(adjuster_block)
    clearance = float(p["fit_clearance"])
    sx, sy, _, _ = _ref_scale(p)
    base_relief = _box(
        4.0 * sx + 2.0 * clearance,
        7.8 * sy + 2.0 * clearance,
        4.0 + 2.0 * clearance,
        (11.8 * sx, 15.0 * sy, 0.0),
    )
    handle_linkage = handle_linkage.cut(base_relief)

    components = [
        ("base_frame", base_frame),
        ("u_bolt_latch", u_bolt_latch),
        ("front_fork_block", front_fork_block),
        ("adjuster_block", adjuster_block),
        ("handle_linkage", handle_linkage),
    ]

    result = cq.Assembly(name="vertical_latch_toggle_clamp")
    for name, solid in components:
        result.add(solid, name=name)
    return result


if "show_object" in globals():
    result = build(
        clamp_size=160,
        fit_clearance=0.10,
        a1=5.1,
        a2=24.9,
        b1=25.9,
        b2=35.1,
        b3=21.1,
        b4=25.4,
        b5=14.0,
        d1=4.0,
        d2=4.3,
        h1=37.1,
        h2=9.9,
        l1=68.1,
        l2=4.6,
        m1=22.1,
        m2=6.6,
        m3=13.0,
        m4=6.6,
        m5=14.2,
        s=2.0,
    )
    show_object(result, name="vertical_latch_toggle_clamp_assembly")
