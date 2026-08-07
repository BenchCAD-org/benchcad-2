import math

import cadquery as cq


def _box(length, width, height, z=0.0, x=0.0, y=0.0):
    return (
        cq.Workplane("XY")
        .box(length, width, height, centered=(True, True, False))
        .translate((x, y, z))
    )


def _solid(shape):
    return shape.val() if isinstance(shape, cq.Workplane) else shape


def _fuse(a, b):
    return _solid(a).fuse(_solid(b)).clean()


def _cut(a, b):
    return _solid(a).cut(_solid(b)).clean()


def _soften_plastic(shape, _amount):
    return _solid(shape).clean()


def _can(body_diameter, can_height, rim_radius):
    radius = body_diameter / 2.0
    can_bottom_z = 0.5
    top_round = min(max(rim_radius, 0.08), radius * 0.18, can_height * 0.12)
    top_z = can_bottom_z + can_height
    top_start = top_z - top_round

    # Single-section revolve.  The reference can body reads as one continuous
    # rolled profile from the lower neck into the main wall and then into the
    # top shoulder.  Use one spline profile instead of stacked disks or short
    # platelike steps so the rendered body does not show a horizontal seam.
    br = top_round
    roll_r = br * 1.2
    theta = 0.703
    p0 = cq.Vector(radius - br, 0.0, can_bottom_z)
    p1 = cq.Vector(radius, 0.0, can_bottom_z + br)
    p2 = cq.Vector(radius, 0.0, can_bottom_z + br * 1.2)
    c_small_r = radius - br
    p3 = cq.Vector(c_small_r + br * math.cos(theta), 0.0, p2.z + br * math.sin(theta))
    c_roll_r = radius + roll_r * 0.565
    c_roll_z = p3.z + math.sqrt(max(roll_r * roll_r - (p3.x - c_roll_r) ** 2, 0.0))
    p4 = cq.Vector(c_roll_r - roll_r, 0.0, c_roll_z)
    p5 = cq.Vector(p3.x, 0.0, c_roll_z + (c_roll_z - p3.z))
    p6 = cq.Vector(radius, 0.0, p5.z + br * math.sin(theta))
    p7 = cq.Vector(radius, 0.0, top_start)
    p8 = cq.Vector(radius - br, 0.0, top_z)

    edges = [
        cq.Edge.makeSpline(
            [p0, p1, p2, p3, p4, p5, p6, p7, p8],
            tol=1e-6,
        ),
        cq.Edge.makeLine(p8, cq.Vector(0.0, 0.0, top_z)),
        cq.Edge.makeLine(cq.Vector(0.0, 0.0, top_z), cq.Vector(0.0, 0.0, can_bottom_z)),
        cq.Edge.makeLine(cq.Vector(0.0, 0.0, can_bottom_z), p0),
    ]
    body = cq.Solid.revolve(
        cq.Wire.assembleEdges(edges),
        [],
        360,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
    ).clean()
    return body.clean()


def _base(
    base_length,
    base_width,
    base_thickness,
    body_diameter,
    terminal_span,
    terminal_width,
    terminal_thickness,
):
    frame_height = base_thickness * 0.46
    upper_height = base_thickness - frame_height
    plastic_chamfer = min(base_thickness * 0.055, terminal_width * 0.07, 0.1)
    carrier_length = base_length
    carrier_width = base_width
    base = _soften_plastic(
        _box(carrier_length, carrier_width, frame_height),
        plastic_chamfer,
    )

    front_notch_width = min(body_diameter * 0.36, base_length * 0.38)
    front_notch_depth = min(base_width * 0.22, max(terminal_width * 0.8, 0.65))
    front_notch = _box(
        front_notch_width,
        front_notch_depth + 0.02,
        frame_height * 0.72,
        z=frame_height * 0.28,
        y=-base_width * 0.5 + front_notch_depth * 0.5,
    )
    base = _cut(base, front_notch)

    rear_width = min(base_width * 0.28, terminal_width * 1.6)
    rear_riser = _soften_plastic(
        _box(
            base_length * 0.74,
            rear_width,
            upper_height * 0.72,
            z=frame_height,
            y=base_width * 0.5 - rear_width * 0.5,
        ),
        plastic_chamfer * 0.65,
    )
    base = _fuse(base, rear_riser)

    side_len = min(base_length * 0.22, body_diameter * 0.25)
    side_width = min(base_width * 0.42, body_diameter * 0.45)
    side_height = upper_height * 0.82
    side_x = base_length * 0.5 - side_len * 0.5
    for x in (-side_x, side_x):
        molded_side = _soften_plastic(
            _box(
                side_len,
                side_width,
                side_height,
                z=frame_height,
                x=x,
                y=-base_width * 0.03,
            ),
            plastic_chamfer * 0.65,
        )
        base = _fuse(base, molded_side)

    support_height = min(base_thickness * 0.23, upper_height * 0.72)
    support_radius = min(body_diameter * 0.48, min(base_length, base_width) * 0.44)
    support = (
        cq.Workplane("XY")
        .circle(support_radius)
        .extrude(support_height)
        .translate((0.0, 0.0, base_thickness - support_height))
    )
    base = _fuse(base, support)

    groove_outer = min(body_diameter * 0.50, min(base_length, base_width) * 0.455)
    groove_width = min(0.24, max(0.14, terminal_width * 0.18))
    groove_depth = min(base_thickness * 0.10, 0.22)
    groove = (
        cq.Workplane("XY")
        .circle(groove_outer)
        .circle(max(groove_outer - groove_width, 0.1))
        .extrude(groove_depth)
        .translate((0.0, 0.0, base_thickness - groove_depth))
    )
    base = _cut(base, groove)

    mouth_width = min(body_diameter * 0.28, base_length * 0.28)
    mouth_depth = min(base_width * 0.18, terminal_width * 0.9)
    mouth_height = min(base_thickness * 0.24, 0.42)
    notch = _box(
        mouth_width,
        mouth_depth,
        mouth_height,
        z=frame_height,
        y=-base_width * 0.5 + mouth_depth * 0.5,
    )
    base = _cut(base, notch)

    side_support_len = min(body_diameter * 0.23, base_length * 0.23)
    side_support_width = min(terminal_width * 0.58, base_width * 0.11)
    side_support_height = min(base_thickness * 0.18, 0.32)
    side_x = base_length * 0.5 - side_support_len * 0.5
    for x in (-side_x, side_x):
        support_block = _soften_plastic(
            _box(
                side_support_len,
                side_support_width,
                side_support_height,
                z=frame_height,
                x=x,
                y=base_width * 0.5 - side_support_width * 0.5,
            ),
            plastic_chamfer * 0.55,
        )
        base = _fuse(base, support_block)

    outer_x = terminal_span * 0.5
    inner_x = min(base_length * 0.5 - terminal_width * 0.18, outer_x - terminal_width)
    foot_bottom = 0.0
    foot_top = terminal_thickness
    bend_top = min(base_thickness * 0.78, terminal_width * 1.05)
    side_contact = min(terminal_width * 0.55, max(0.25, outer_x - inner_x))
    terminal_y = min(base_width * 0.5, max(terminal_width * 1.45, base_width * 0.2))
    for side in (-1.0, 1.0):
        sx_outer = side * outer_x
        sx_inner = side * inner_x
        sx_bend_outer = side * (inner_x + terminal_thickness)
        sx_foot_inner = side * (outer_x - side_contact)
        profile = [
            (sx_outer, foot_bottom),
            (sx_foot_inner, foot_top),
            (sx_bend_outer, foot_top),
            (sx_bend_outer, bend_top),
            (sx_inner, bend_top),
            (sx_inner, foot_bottom),
        ]
        if side < 0:
            profile.reverse()
        terminal = (
            cq.Workplane("XZ")
            .polyline(profile)
            .close()
            .extrude(terminal_y, both=True)
        )
        base = _fuse(base, terminal)

    return base.clean()


def build(
    body_diameter,
    can_height,
    base_length,
    base_width,
    base_thickness,
    terminal_span,
    terminal_width,
    terminal_thickness,
    rim_radius,
):
    base = _base(
        base_length,
        base_width,
        base_thickness,
        body_diameter,
        terminal_span,
        terminal_width,
        terminal_thickness,
    )
    can = _can(body_diameter, can_height, rim_radius)
    result = _fuse(base, can)
    return result
