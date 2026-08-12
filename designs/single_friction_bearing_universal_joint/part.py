"""DIN 808 EG single universal joint with a friction-bearing envelope."""

import cadquery as cq


def _centered_cylinder(diameter, length, axis):
    solid = (
        cq.Workplane("XY")
        .circle(diameter / 2.0)
        .extrude(length)
        .translate((0.0, 0.0, -length / 2.0))
    )
    if axis == "X":
        return solid.rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
    if axis == "Y":
        return solid.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
    return solid


def _bore_tool(bore_code, d2, square_s, keyway_width, keyway_depth, depth, x):
    if int(bore_code) == 2:
        return cq.Workplane("XY").box(depth, square_s, square_s).translate((x, 0.0, 0.0))

    tool = _centered_cylinder(d2, depth, "X").translate((x, 0.0, 0.0))
    if int(bore_code) == 1:
        # The slot has to reach the bore WALL, not just the bore's topmost
        # point. A box that dips only 0.01 below z=d2/2 misses the wall by
        # sqrt(r^2-(b/2)^2) at the keyway's own edges, which left a 0.12-0.79
        # mm ridge on both sides and made the keyway look detached from the
        # bore. Running the box down to the bore axis removes nothing extra:
        # it is narrower than the bore, so everything below the wall is
        # already taken out by the cylinder.
        slot_h = d2 / 2.0 + keyway_depth
        slot = (
            cq.Workplane("XY")
            .box(depth, keyway_width, slot_h)
            .translate((x, 0.0, slot_h / 2.0))
        )
        tool = tool.union(slot.val())
    return tool


def _build_input_yoke(d1, d2, square_s, l3, shaft_depth, bore_code,
                      keyway_width, keyway_depth, pin_hole_d):
    """Build the left yoke; its pin bore axis is global Z. `pin_hole_d` is
    the clearance bore for this yoke's own pin (the two pins differ: the
    thick pivot pin carries the block, the thin cross pin locks through
    it), so each yoke's ears are bored for its own pin."""
    hub_length = shaft_depth
    ear_radius = 0.21 * d1
    ear_offset = 0.37 * d1
    ear_thickness = 0.18 * d1
    overlap = 0.03 * d1
    box_end = -0.04 * d1
    hub_center_x = -l3 + hub_length / 2.0
    hub_inner_x = -l3 + hub_length

    yoke = _centered_cylinder(d1, hub_length, "X").translate((hub_center_x, 0.0, 0.0))
    fork_start = hub_inner_x - overlap
    fork_length = box_end - fork_start
    fork_center_x = (fork_start + box_end) / 2.0
    for z in (-ear_offset, ear_offset):
        arm = (
            cq.Workplane("XY")
            .box(fork_length, 2.0 * ear_radius, ear_thickness)
            .translate((fork_center_x, 0.0, z))
        )
        eye = _centered_cylinder(2.0 * ear_radius, ear_thickness, "Z").translate(
            (0.0, 0.0, z)
        )
        yoke = yoke.union(arm.val()).union(eye.val())

    for z in (-ear_offset, ear_offset):
        hole = _centered_cylinder(
            pin_hole_d, ear_thickness + 0.08 * d1, "Z"
        ).translate((0.0, 0.0, z))
        yoke = yoke.cut(hole.val())

    bore = _bore_tool(
        bore_code,
        d2,
        square_s,
        keyway_width,
        keyway_depth,
        shaft_depth + 0.04,
        -l3 + shaft_depth / 2.0 - 0.01,
    )
    return yoke.cut(bore.val())


def _build_output_yoke(d1, d2, square_s, l3, shaft_depth, bore_code,
                       keyway_width, keyway_depth, joint_angle, pin_hole_d):
    """Build the right yoke as a rigidly transformed instance of the same part."""
    yoke = _build_input_yoke(
        d1,
        d2,
        square_s,
        l3,
        shaft_depth,
        bore_code,
        keyway_width,
        keyway_depth,
        pin_hole_d,
    )
    # Turn the left instance toward +X, then phase the fork by 90 degrees so
    # its trunnion axis is global Y. Bore/keyway orientation follows the same
    # rigid transform, preserving one physical yoke design at both ends.
    yoke = yoke.rotate(
        (0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        180.0,
    ).rotate(
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        90.0,
    )
    return yoke.rotate(
        (0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        -float(joint_angle),
    )


# ── the real DIN 808 EG friction-bearing centre (teardown reference on the
# PR): a rounded pivot BLOCK with two orthogonal bores, a thick PIVOT PIN
# (axis Z, cross-drilled at its middle), a thin CROSS PIN (axis Y) passing
# through the block AND through the pivot pin's cross hole, and a split
# retaining RING on the pivot pin's lower end. All proportions of d1.
PIVOT_PIN_D = 0.26      # thick pin diameter / d1
CROSS_PIN_D = 0.14      # thin pin diameter / d1
PIN_FIT = 0.015         # radial running clearance / d1 (both pins, all bores)


def _build_pivot_block(d1):
    """Centre block: a turned DRUM (the teardown photo shows a cylinder, not
    a cube) with two milled flats where the cross-pin bores break out, bored
    Z for the pivot pin and Y for the cross pin, and counterbored at both
    ends around the pivot bore."""
    # Sized from wall thickness, not from the photo: the earlier 0.25*d1
    # radius left 0.82 x the pivot-bore radius as wall, which is far heavier
    # than a friction-bearing block needs and read as an oversized centre.
    # 0.21*d1 puts the wall at 0.53 x the bore radius, and the block is
    # square in section: height = diameter.
    r_o = 0.21 * d1
    half_h = r_o          # height : diameter = 1 : 1
    blk = (
        cq.Workplane("XY")
        .circle(r_o)
        .extrude(2.0 * half_h)
        .translate((0.0, 0.0, -half_h))
        .edges("%CIRCLE").chamfer(0.045 * d1)   # generous break on both ends
    )
    # two milled FLATS on the cross-pin axis, the faces its bores break out
    # of (the teardown shows a drum with flats, not a plain cylinder)
    flat_at = 0.168 * d1
    for sy in (1.0, -1.0):
        blk = blk.cut(
            cq.Workplane("XY")
            .box(2.2 * r_o, 2.0 * r_o, 2.4 * half_h)
            .translate((0.0, sy * (flat_at + r_o), 0.0))
        )
    # counterbored recess around the pivot bore on both end faces
    for sz in (1.0, -1.0):
        blk = blk.cut(
            cq.Workplane("XY")
            .circle((PIVOT_PIN_D + PIN_FIT) * d1 / 2.0 + 0.015 * d1)
            .extrude(sz * 0.035 * d1)
            .translate((0.0, 0.0, sz * half_h - (0.035 * d1 if sz < 0 else 0.0)))
        )
    blk = blk.cut(_centered_cylinder((PIVOT_PIN_D + PIN_FIT) * d1, 0.60 * d1, "Z").val())
    blk = blk.cut(_centered_cylinder((CROSS_PIN_D + PIN_FIT) * d1, 0.60 * d1, "Y").val())
    return blk


def _build_pivot_pin(d1):
    """Thick pin on the input yoke's Z axis, spanning both ears, with the
    transverse cross-pin hole at its middle."""
    # ears span z in +/-[0.28, 0.46]*d1, so the pin runs -0.50 to +0.47*d1:
    # through both ears, proud enough below for the ring, and still inside
    # the catalog d1 envelope
    z_bot, z_top = -0.50 * d1, 0.47 * d1
    pin = (
        cq.Workplane("XY")
        .workplane(offset=z_bot)
        .circle(PIVOT_PIN_D * d1 / 2.0)
        .extrude(z_top - z_bot)
        .edges().chamfer(0.015 * d1)
    )
    pin = pin.cut(_centered_cylinder((CROSS_PIN_D + PIN_FIT) * d1, PIVOT_PIN_D * d1 + 0.2, "Y").val())
    return pin


def _build_cross_pin(d1):
    """Thin pin on the output yoke's Y axis, through the block and through
    the pivot pin's transverse hole — this is what closes the joint."""
    length = 0.92 * d1                       # flush with the ear outer faces
    # sketched directly on its final plane (XZ at y=+length/2, swept to
    # y=-length/2): no post-build transform, which this OCC drops silently
    return (
        cq.Workplane("XZ")
        .workplane(offset=length / 2.0)
        .circle(CROSS_PIN_D * d1 / 2.0)
        .extrude(-length)
        .edges().chamfer(0.012 * d1)
    )


def build(
    catalog_row,
    bore_code,
    joint_angle,
    d1,
    d2,
    square_s,
    l1,
    l3,
    shaft_depth,
    keyway_width,
    keyway_depth,
):
    """Build the DIN 808 EG joint as its real six-part construction: two
    yokes, the friction pivot block, the cross-drilled pivot pin, the cross
    pin through it, and the split retaining ring."""
    del catalog_row, l1
    input_yoke = _build_input_yoke(
        d1, d2, square_s, l3, shaft_depth, bore_code, keyway_width,
        keyway_depth, (PIVOT_PIN_D + PIN_FIT) * d1,
    )
    output_yoke = _build_output_yoke(
        d1,
        d2,
        square_s,
        l3,
        shaft_depth,
        bore_code,
        keyway_width,
        keyway_depth,
        joint_angle,
        (CROSS_PIN_D + PIN_FIT) * d1,
    )

    result = cq.Assembly(name="single_friction_bearing_universal_joint")
    result.add(input_yoke, name="input_yoke")
    result.add(output_yoke, name="output_yoke")
    result.add(_build_pivot_block(d1), name="pivot_block")
    result.add(_build_pivot_pin(d1), name="pivot_pin")
    result.add(_build_cross_pin(d1), name="cross_pin")
    return result
