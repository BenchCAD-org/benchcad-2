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
    "l1": 68.1,
    "h1": 37.1,
    "b2": 35.1,
    "d1": 4.0,
}


def _params(
    clamp_size,
    with_u_bolt,
    handle_angle,
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
    r,
    s,
    w1,
    w2,
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


def _oval_plate_xy(x_radius, y_radius, thickness_z, center, segments=32):
    cx, cy, cz = center
    pts = [
        (
            cx + math.cos(2.0 * math.pi * i / segments) * x_radius,
            cy + math.sin(2.0 * math.pi * i / segments) * y_radius,
        )
        for i in range(segments)
    ]
    return _plate_xy(pts, thickness_z, cz)


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


def _rotate_handle(p, solid):
    angle = float(p["handle_angle"])
    if abs(angle) < 1e-6:
        return solid
    sx, sy, _, _ = _ref_scale(p)
    pivot = (1.7 * sx, 16.0 * sy, 0.0)
    return solid.rotate(pivot, (pivot[0], pivot[1], 1.0), angle)


def solid_0_base_frame(p):
    """Folded mounting frame, base plate, triangular web, and upper pin boss."""

    sx, sy, sz, _ = _ref_scale(p)
    scale = _min_scale(p)
    hole = float(p["d2"])

    sheet_t = max(float(p["s"]) * sz, 4.0 * sz)

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
    part = web.union(outer_cap).union(inner_cap).union(cap_crown)

    fold_band = _box(36.0 * sx, 1.0 * sy, 4.8 * sz, _pt(p, 14.6, -6.45, 0.0), 0.12 * scale)
    part = part.union(fold_band)

    rail_len = 26.0 * sx
    rail_y = 2.2 * sy
    rail_z = 15.1 * sz
    for zc in (-9.95 * sz, 9.95 * sz):
        rail = _rounded_rect_xz(rail_len, rail_z, rail_y, (19.6 * sx, -7.3 * sy, zc), 2.35 * scale)
        lip_z = 0.8 * sz
        lip_center_z = math.copysign(sheet_t / 2.0 + lip_z * 0.25, zc)
        fold_lip = _box(rail_len, 0.5 * sy, lip_z, (19.6 * sx, -6.15 * sy, lip_center_z), 0.10 * scale)
        part = part.union(rail).union(fold_lip)

    hole_xs = (13.1 * sx, 26.1 * sx)
    hole_zs = (-11.0 * sz, 11.0 * sz)
    for hx in hole_xs:
        for hz in hole_zs:
            part = part.cut(_cyl_y(hole, 4.8 * sy, (hx, -7.4 * sy, hz)))

    side_hole = max(hole * 0.82, 3.5 * scale)
    part = part.cut(_cyl_z(side_hole, sheet_t * 1.6, _pt(p, 20.6, 5.6, 0.0)))

    return part


def solid_1_u_bolt(p):
    """U-bolt latch rod for the T3 variant."""

    sx, sy, sz, _ = _ref_scale(p)
    rod = float(p["d1"])
    x = 1.7 * sx
    z_sep = max(25.0 * sz, float(p["b5"]) + rod * 2.0)
    y0 = -35.7 * sy
    y1 = 34.7 * sy

    part = None
    for z in (-z_sep / 2.0, z_sep / 2.0):
        leg = _cyl_y(rod, y1 - y0, (x, (y0 + y1) / 2.0, z))
        part = leg if part is None else part.union(leg)

        thread_start = y0 + 2.4 * sy
        for i in range(6):
            ring = _cyl_y(rod * 1.05, 0.35 * sy, (x, thread_start + i * 0.95 * sy, z))
            part = part.union(ring)

    top_bridge = _cyl_z(rod, z_sep, (x, y0, 0.0))
    return part.union(top_bridge)


def solid_2_front_fork_block(p):
    """Lower C-shaped fork block with two side-facing holes."""

    sx, sy, sz, _ = _ref_scale(p)
    scale = _min_scale(p)
    hole = float(p["d2"])
    x0, x1 = -3.5 * sx, 6.5 * sx
    y0, y1 = -34.2 * sy, -8.7 * sy
    z_half = 7.0 * sz

    height = y1 - y0
    width = x1 - x0
    arm_t = 3.1 * sz
    left_web = _box(width * 0.34, height, 2.0 * z_half, (x0 + width * 0.17, (y0 + y1) / 2.0, 0.0), 0.35 * scale)
    top_arm = _box(width * 0.92, height, arm_t, (x0 + width * 0.54, (y0 + y1) / 2.0, z_half - arm_t / 2.0), 0.25 * scale)
    bottom_arm = _box(width * 0.92, height, arm_t, (x0 + width * 0.54, (y0 + y1) / 2.0, -z_half + arm_t / 2.0), 0.25 * scale)
    block = left_web.union(top_arm).union(bottom_arm)

    for y in (y0 + (y1 - y0) * 0.27, y0 + (y1 - y0) * 0.72):
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
    x = 1.7 * sx
    y0, y1 = 9.6 * sy, 24.0 * sy
    z_half = 15.0 * sz
    y_mid = (y0 + y1) / 2.0

    tube = _cyl_z(max(rod * 2.0, 7.4 * scale), 2.0 * z_half, (x, y_mid, 0.0))
    web = _capsule_z(27.0 * sz, 4.8 * sx, y1 - y0, (x, y_mid, 0.0))
    part = tube.union(web)

    for z in (-10.3 * sz, 10.3 * sz):
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
        side = side.union(_oval_plate_xy(7.0 * sx, 8.0 * sy, plate_t, (0.0 * sx, 0.2 * sy, z), 44))
        side = side.union(_oval_plate_xy(7.4 * sx, 6.8 * sy, plate_t, (1.0 * sx, 18.2 * sy, z), 44))
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
        .union(_capsule_x(4.2 * sx, 6.7 * sz, 6.8 * sy, (59.6 * sx, 25.0 * sy, 0.0)))
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
    lower_pin = _cyl_z(max(rod * 0.88, 3.5 * scale), bridge_z, (0.0, 0.0, 0.0))
    upper_pin = _cyl_z(max(rod * 0.82, 3.3 * scale), bridge_z, (1.0 * sx, 18.2 * sy, 0.0))
    rear_pin = _cyl_z(max(rod * 0.76, 3.1 * scale), bridge_z, (43.8 * sx, 24.0 * sy, 0.0))
    part = (
        part.union(upper_lip)
        .union(center_web)
        .union(front_web)
        .union(right_shell)
        .union(nose_tip)
        .union(yoke_web)
        .union(lower_pin)
        .union(upper_pin)
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

    return _rotate_handle(p, part)


def build(
    clamp_size,
    with_u_bolt,
    handle_angle,
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
    r,
    s,
    w1,
    w2,
):
    p = _params(
        clamp_size,
        with_u_bolt,
        handle_angle,
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
        r,
        s,
        w1,
        w2,
    )
    solids = [
        solid_0_base_frame(p),
        solid_2_front_fork_block(p),
        solid_3_adjuster_block(p),
        solid_4_handle_linkage(p),
    ]
    if int(round(float(with_u_bolt))):
        solids.insert(1, solid_1_u_bolt(p))

    result = cq.Compound.makeCompound([solid.val() if hasattr(solid, "val") else solid for solid in solids])
    return result


if "show_object" in globals():
    result = build(
        clamp_size=160,
        with_u_bolt=1,
        handle_angle=0.0,
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
        r=52.1,
        s=2.0,
        w1=32.0,
        w2=9.9,
    )
    show_object(result, name="vertical_latch_toggle_clamp_assembly")
