import cadquery as cq
import math


def _box(length, width, height, z=0.0, x=0.0, y=0.0):
    return (
        cq.Workplane("XY")
        .box(length, width, height, centered=(True, True, False))
        .translate((x, y, z))
    )


def _solid(shape):
    return shape.val() if isinstance(shape, cq.Workplane) else shape


def _fuse(left, right):
    return _solid(left).fuse(_solid(right)).clean()


def _cut(left, right):
    return _solid(left).cut(_solid(right)).clean()


def _horizontal_edges_at(shape, z_level):
    return [
        edge
        for edge in _solid(shape).Edges()
        if abs(edge.BoundingBox().zmax - edge.BoundingBox().zmin) < 1e-6
        and abs(edge.BoundingBox().zmax - z_level) < 1e-6
    ]


def _circular_edges_at(shape, z_level, radius):
    circumference = 2.0 * math.pi * radius
    return [
        edge
        for edge in _horizontal_edges_at(shape, z_level)
        if edge.geomType() == "CIRCLE"
        and abs(edge.Length() - circumference) < 1e-5
    ]


def _soften_plastic(shape, amount):
    if amount <= 0:
        return _solid(shape)
    solid = _solid(shape)
    return solid.chamfer(amount, None, solid.Edges()).clean()


def _can(body_diameter, can_height, base_thickness, rim_radius):
    radius = body_diameter / 2.0
    overlap = min(0.05, base_thickness * 0.05)
    can_bottom_z = 0.5
    rim_fillet = min(rim_radius, radius * 0.25, can_height * 0.1)
    top_z = can_bottom_z + can_height
    body = cq.Workplane("XY").circle(radius).extrude(can_height)
    top_edges = _horizontal_edges_at(body, can_height)
    body = _solid(body).fillet(rim_fillet, top_edges)
    body = body.translate((0.0, 0.0, can_bottom_z))

    vent_length = body_diameter * 0.52
    vent_width = min(body_diameter * 0.038, 0.2)
    vent_depth = min(can_height * 0.006, 0.04)
    for angle in (0, 90):
        vent = (
            cq.Workplane("XY")
            .box(vent_length, vent_width, vent_depth, centered=(True, True, False))
            .rotate((0, 0, 0), (0, 0, 1), angle)
            .translate((0.0, 0.0, top_z - vent_depth))
        )
        body = _cut(body, vent)

    # Preserve the reference bead and neck proportions below the can body.
    bead_height = min(0.45, can_height * 0.08)
    neck_height = min(0.55, can_height * 0.1)
    bead_radius = radius * 1.02
    bead = (
        cq.Workplane("XY")
        .circle(bead_radius)
        .extrude(bead_height)
        .translate((0.0, 0.0, can_bottom_z + neck_height))
    )
    neck = (
        cq.Workplane("XY")
        .circle(radius * 0.94)
        .extrude(neck_height + overlap)
        .translate((0.0, 0.0, can_bottom_z - overlap))
    )
    can = _fuse(_fuse(body, bead), neck)
    groove_start_z = can_bottom_z + neck_height
    groove_width = min(bead_height * 0.75, max(0.30, rim_radius * 1.5))
    neck_radius = radius * 0.94
    groove_depth = radius - neck_radius + 0.10
    groove_radius = radius - groove_depth
    groove_cut = (
        cq.Workplane("XY")
        .circle(bead_radius + 0.10)
        .circle(groove_radius)
        .extrude(groove_width)
        .translate((0.0, 0.0, groove_start_z))
    )
    can = _cut(can, groove_cut)
    groove_fillet = min(0.10, groove_depth * 0.4, groove_width * 0.3)
    groove_edges = _circular_edges_at(can, groove_start_z, groove_radius)
    groove_edges += _circular_edges_at(
        can, groove_start_z + groove_width, groove_radius
    )
    return can.fillet(groove_fillet, groove_edges).clean()


def _base(
    base_length,
    base_width,
    base_thickness,
    body_diameter,
    terminal_span,
    terminal_width,
    terminal_thickness,
):
    plate_height = base_thickness * 0.42
    raised_height = base_thickness - plate_height
    plastic_chamfer = min(base_thickness * 0.045, terminal_width * 0.06, 0.08)
    base = _soften_plastic(_box(base_length, base_width, plate_height), plastic_chamfer)

    saddle_width = max(terminal_width * 1.05, base_width * 0.16)
    saddle_y = base_width * 0.5 - saddle_width * 0.5
    saddle_len = min(base_length * 0.34, body_diameter * 0.5)
    support_height = raised_height * 0.72
    for y in (-saddle_y, saddle_y):
        base = _fuse(
            base,
            _soften_plastic(
                _box(saddle_len, saddle_width, support_height, z=plate_height, y=y),
                plastic_chamfer * 0.7,
            ),
        )

    center_block = _box(
        min(body_diameter * 0.42, base_length * 0.3),
        min(body_diameter * 0.13, base_width * 0.14),
        raised_height * 0.38,
        z=plate_height,
    )
    base = _fuse(base, _soften_plastic(center_block, plastic_chamfer * 0.6))

    outer_x = terminal_span * 0.5
    inner_x = min(base_length * 0.5 - terminal_width * 0.18, outer_x - terminal_width)
    foot_top = 0.0
    foot_bottom = -terminal_thickness
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

    return _solid(base).clean()


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
    can = _can(body_diameter, can_height, base_thickness, rim_radius)
    result = _fuse(base, can)
    return result
