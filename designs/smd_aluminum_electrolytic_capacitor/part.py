import cadquery as cq


def _box(length, width, height, z=0.0, x=0.0, y=0.0):
    return (
        cq.Workplane("XY")
        .box(length, width, height, centered=(True, True, False))
        .translate((x, y, z))
    )


def _can(body_diameter, can_height, base_thickness, rim_radius):
    radius = body_diameter / 2.0
    overlap = min(0.05, base_thickness * 0.05)
    fillet = min(rim_radius, radius * 0.18, can_height * 0.08)
    body = (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(can_height + overlap)
        .edges()
        .fillet(fillet)
        .translate((0.0, 0.0, base_thickness - overlap))
    )

    # A shallow lower bead and neck give the SMD can the stepped profile visible
    # in the STEP reference without adding manufacturer-specific markings.
    bead_height = min(0.45, can_height * 0.08)
    neck_height = min(0.55, can_height * 0.1)
    bead = (
        cq.Workplane("XY")
        .circle(radius * 1.02)
        .extrude(bead_height)
        .translate((0.0, 0.0, base_thickness + neck_height - overlap))
    )
    neck = (
        cq.Workplane("XY")
        .circle(radius * 0.94)
        .extrude(neck_height + overlap)
        .translate((0.0, 0.0, base_thickness - overlap))
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
    base = _box(base_length, base_width, base_thickness)

    saddle_height = base_thickness * 0.55
    saddle_width = max(terminal_width * 1.35, base_width * 0.24)
    saddle_y = base_width * 0.5 - saddle_width * 0.5
    saddle_len = min(base_length * 0.46, body_diameter * 0.72)
    for y in (-saddle_y, saddle_y):
        base = base.union(
            _box(saddle_len, saddle_width, saddle_height, z=base_thickness, y=y),
            clean=True,
        )

    center_block = _box(
        min(body_diameter * 0.58, base_length * 0.42),
        min(body_diameter * 0.18, base_width * 0.2),
        saddle_height * 0.55,
        z=base_thickness,
    )
    base = base.union(center_block, clean=True)

    pad_length = max(terminal_width, min(base_length * 0.24, terminal_span * 0.22))
    pad_width = base_width + 0.45
    pad_x = min(terminal_span / 2.0, base_length / 2.0 - pad_length / 2.0)
    for x in (-pad_x, pad_x):
        base = base.union(
            _box(pad_length, pad_width, terminal_thickness, z=-terminal_thickness, x=x),
            clean=True,
        )

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
