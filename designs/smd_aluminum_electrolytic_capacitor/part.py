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


def _horizontal_edges(shape):
    solid = _solid(shape)
    return [e for e in solid.Edges() if abs(e.BoundingBox().zmax - e.BoundingBox().zmin) < 1e-4]


def _top_horizontal_edges(shape, z_level):
    return [
        edge
        for edge in _horizontal_edges(shape)
        if abs(edge.BoundingBox().zmax - z_level) < 1e-4
    ]


def _soften_plastic(shape, amount, edge_selector=None):
    if amount <= 0:
        return _solid(shape)
    solid = _solid(shape)
    edges = _horizontal_edges(solid)
    if edge_selector is not None:
        edges = [edge for edge in edges if edge_selector(edge)]
    if not edges:
        return solid.clean()
    return solid.chamfer(amount, None, edges).clean()


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
        .translate((0.0, 0.0, can_bottom_z))
    )
    body = _solid(body).chamfer(edge_chamfer, None, _top_horizontal_edges(body, top_z)).clean()

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
        body = body.cut(_solid(vent)).clean()

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
    body = _fuse(body, bead)
    body = _fuse(body, neck)
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
    plate_height = base_thickness * 0.42
    raised_height = base_thickness - plate_height
    plastic_chamfer = min(base_thickness * 0.045, terminal_width * 0.06, 0.08)
    base = _soften_plastic(_box(base_length, base_width, plate_height), plastic_chamfer)

    saddle_width = max(terminal_width * 1.05, base_width * 0.16)
    saddle_y = base_width * 0.5 - saddle_width * 0.5
    saddle_len = min(base_length * 0.34, body_diameter * 0.5)
    support_height = raised_height * 0.72

    def first_saddle_selector(edge):
        bb = edge.BoundingBox()
        cx = (bb.xmin + bb.xmax) * 0.5
        cy = (bb.ymin + bb.ymax) * 0.5
        cz = (bb.zmin + bb.zmax) * 0.5
        dy = bb.ymax - bb.ymin
        return (
            abs(abs(cx) - saddle_len * 0.5) < 1e-4
            and abs(cy + saddle_y) < 1e-4
            and abs(dy - saddle_width) < 1e-4
            and (
                abs(cz - plate_height) < 1e-4
                or abs(cz - (plate_height + support_height)) < 1e-4
            )
        )

    for i, y in enumerate((-saddle_y, saddle_y)):
        saddle = _box(saddle_len, saddle_width, support_height, z=plate_height, y=y)
        if i == 0:
            shaped = _soften_plastic(saddle, plastic_chamfer * 0.7, first_saddle_selector)
        else:
            shaped = _soften_plastic(saddle, plastic_chamfer * 0.7)
        base = _fuse(base, shaped)

    center_block = _box(
        min(body_diameter * 0.42, base_length * 0.3),
        min(body_diameter * 0.13, base_width * 0.14),
        raised_height * 0.38,
        z=plate_height,
    )
    base = _fuse(base, center_block)

    outer_x = terminal_span * 0.5
    inner_x = min(base_length * 0.5 - terminal_width * 0.18, outer_x - terminal_width)
    z_offset = terminal_thickness
    foot_top = 0.0 + z_offset
    foot_bottom = -terminal_thickness + z_offset
    bend_top = min(base_thickness * 0.78, terminal_width * 1.05) + z_offset
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


EXAMPLE_PARAMS = {
    "body_diameter": 6.3,
    "can_height": 7.2,
    "base_length": 6.6,
    "base_width": 6.6,
    "base_thickness": 2.0,
    "terminal_span": 7.3,
    "terminal_width": 1.0,
    "terminal_thickness": 0.2,
    "rim_radius": 0.2,
}


if "show_object" in globals():
    result = build(**EXAMPLE_PARAMS)
    show_object(result, name="smd_aluminum_electrolytic_capacitor")
