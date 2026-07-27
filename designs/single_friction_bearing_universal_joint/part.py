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
        slot = (
            cq.Workplane("XY")
            .box(depth, keyway_width, keyway_depth + 0.02)
            .translate((x, 0.0, d2 / 2.0 + keyway_depth / 2.0))
        )
        tool = tool.union(slot.val())
    return tool


def _build_input_yoke(d1, d2, square_s, l3, shaft_depth, bore_code,
                      keyway_width, keyway_depth):
    """Build the left yoke; its trunnion bore axis is global Z."""
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

    trunnion_hole_d = 0.19 * d1
    for z in (-ear_offset, ear_offset):
        hole = _centered_cylinder(
            trunnion_hole_d, ear_thickness + 0.08 * d1, "Z"
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
                       keyway_width, keyway_depth, joint_angle):
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


def _build_cross(d1):
    """Build one orthogonal cross with proportion-based trunnion geometry."""
    ear_offset = 0.37 * d1
    ear_thickness = 0.18 * d1
    end_clearance = 0.02 * d1
    arm_length = 2.0 * (ear_offset + ear_thickness / 2.0 - end_clearance)
    arm_d = 0.16 * d1
    cross_y = _centered_cylinder(arm_d, arm_length, "Y")
    cross_z = _centered_cylinder(arm_d, arm_length, "Z")
    return cross_y.union(cross_z.val())


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
    """Build the DIN 808 single-jointed EG static three-component envelope."""
    del catalog_row, l1
    input_yoke = _build_input_yoke(
        d1, d2, square_s, l3, shaft_depth, bore_code, keyway_width, keyway_depth
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
    )
    cross = _build_cross(d1)

    result = cq.Assembly(name="single_friction_bearing_universal_joint")
    result.add(input_yoke, name="input_yoke")
    result.add(output_yoke, name="output_yoke")
    result.add(cross, name="cross")
    return result
