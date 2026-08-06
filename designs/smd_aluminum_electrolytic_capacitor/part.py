import cadquery as cq


def _box(length, width, height, z=0.0, x=0.0, y=0.0):
    return (
        cq.Workplane("XY")
        .box(length, width, height, centered=(True, True, False))
        .translate((x, y, z))
    )


def _soften_plastic(shape, amount):
    if amount <= 0:
        return shape
    return shape.edges().chamfer(amount).clean()


def _can(body_diameter, can_height, base_thickness, rim_radius):
    radius = body_diameter / 2.0
    overlap = min(0.05, base_thickness * 0.05)
    can_bottom_z = 0.5
    edge_chamfer = min(rim_radius * 0.16, radius * 0.015, can_height * 0.008)
    top_z = can_bottom_z + can_height
    body = (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(can_height)
        .edges(">Z")
        .chamfer(edge_chamfer)
        .translate((0.0, 0.0, can_bottom_z))
    )
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
        body = body.cut(vent, clean=True)

    # A shallow lower bead and neck give the SMD can the stepped profile visible
    # in the STEP reference without adding manufacturer-specific markings.
    bead_height = min(0.45, can_height * 0.08)
    neck_height = min(0.55, can_height * 0.1)
    bead = (
        cq.Workplane("XY")
        .circle(radius * 1.02)
        .extrude(bead_height)
        .translate((0.0, 0.0, can_bottom_z + neck_height))
    )
    neck = (
        cq.Workplane("XY")
        .circle(radius * 0.94)
        .extrude(neck_height + overlap)
        .translate((0.0, 0.0, can_bottom_z - overlap))
    )
    return body.union(bead, clean=True).union(neck, clean=True).clean()


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
        base = base.union(
            _soften_plastic(
                _box(saddle_len, saddle_width, support_height, z=plate_height, y=y),
                plastic_chamfer * 0.7,
            ),
            clean=True,
        )

    center_block = _box(
        min(body_diameter * 0.42, base_length * 0.3),
        min(body_diameter * 0.13, base_width * 0.14),
        raised_height * 0.38,
        z=plate_height,
    )
    base = base.union(_soften_plastic(center_block, plastic_chamfer * 0.6), clean=True)

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
        base = base.union(terminal, clean=True)

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
    can = _can(body_diameter, can_height, base_thickness, rim_radius)
    result = base.union(can, clean=True).clean()
    return result
