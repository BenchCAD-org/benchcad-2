"""JW Winco GN 490 swivel clamp connector joint (seven-component assembly).

Published GN 490 table values set the two clamp-body envelopes and the
actuator envelopes.  Unpublished V-groove, clearance, spring, bushing, and
secondary fastener details use the proportion rules recorded in NOTES.md.
"""

import math

import cadquery as cq


def _cylinder(radius, height, z0):
    return (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(height)
        .translate((0.0, 0.0, z0))
    )


def _clamp_body(
    z0,
    inner_face_z,
    into_sign,
    tube_axis,
    body_d4,
    jaw_l4,
    gap_l5,
    clamp_d,
    thread_d,
):
    """One complete cast clamp body with an end-entry V-groove."""
    body_r = body_d4 / 2.0
    passage_r = 0.60 * thread_d
    groove_center = -(0.50 * clamp_d + passage_r)
    groove_depth = (0.50 + math.sqrt(0.50)) * clamp_d
    groove_mouth = 2.0 * groove_depth

    edge_r = min(0.035 * body_d4, 0.18 * jaw_l4)
    body = _cylinder(body_r, jaw_l4, z0).edges("%Circle").fillet(edge_r)
    passage = _cylinder(passage_r, jaw_l4 + 2.0, z0 - 1.0)

    # The rod axis is X in one body and Y in the other.  In the normal plane,
    # the triangular prism enters from the face adjacent to the central l5 gap.
    # Its trough is radially offset, matching the catalog section and photo.
    points = [
        (groove_center - groove_mouth / 2.0, inner_face_z),
        (groove_center + groove_mouth / 2.0, inner_face_z),
        (groove_center, inner_face_z + into_sign * groove_depth),
    ]
    plane = "YZ" if int(tube_axis) == 0 else "XZ"
    groove = (
        cq.Workplane(plane)
        .polyline(points)
        .close()
        .extrude(body_d4 * 0.56, both=True)
    )

    # The pressure springs sit in coaxial counterbores behind the two inner
    # faces, as shown in the GN 490 section.  The spring envelope has a small
    # radial assembly allowance, while its end coils touch the pocket bottom
    # and the full-l5 central insert without positive-volume overlap.
    spring_wire_r = min(0.045 * thread_d, 0.035 * gap_l5)
    spring_pocket_depth = min(0.22 * jaw_l4, 0.55 * gap_l5)
    spring_pocket_r = 0.72 * thread_d + spring_wire_r + max(
        0.08,
        0.012 * thread_d,
    )
    if into_sign < 0:
        spring_pocket_z0 = inner_face_z - spring_pocket_depth
    else:
        spring_pocket_z0 = inner_face_z
    spring_pocket = _cylinder(
        spring_pocket_r,
        spring_pocket_depth,
        spring_pocket_z0,
    )

    result = body.cut(passage).cut(groove).cut(spring_pocket)
    return result


def build_lower_clamp_body(
    body_l1,
    body_d4,
    jaw_l4,
    gap_l5,
    catalog_m,
    clamp_d,
    thread_d,
):
    """Lower complete GN 490 clamp body; V-groove axis is X."""
    z0 = -body_l1 / 2.0
    inner_face_z = -catalog_m / 2.0 + clamp_d / 2.0
    result = _clamp_body(
        z0,
        inner_face_z,
        -1.0,
        0,
        body_d4,
        jaw_l4,
        gap_l5,
        clamp_d,
        thread_d,
    )
    return result


def build_upper_clamp_body(
    body_l1,
    body_d4,
    jaw_l4,
    gap_l5,
    catalog_m,
    clamp_d,
    thread_d,
):
    """Upper complete GN 490 clamp body, rotated 90 degrees about the stud."""
    z0 = gap_l5 / 2.0
    inner_face_z = catalog_m / 2.0 - clamp_d / 2.0
    result = _clamp_body(
        z0,
        inner_face_z,
        1.0,
        1,
        body_d4,
        jaw_l4,
        gap_l5,
        clamp_d,
        thread_d,
    )
    return result


def _type_a_actuator(body_l1, thread_d):
    """Review-requested external-hex screw, separate from the DIN 934 nut."""
    head_h = 0.85 * thread_d
    head_circum_d = 1.60 * thread_d
    shaft_r = 0.50 * thread_d
    nut_h = 0.80 * thread_d
    shaft_bottom = -body_l1 / 2.0 - nut_h + 0.08 * thread_d
    head_bottom = body_l1 / 2.0

    shaft = _cylinder(
        shaft_r,
        head_bottom + 0.12 * head_h - shaft_bottom,
        shaft_bottom,
    )
    head = (
        cq.Workplane("XY")
        .polygon(6, head_circum_d)
        .extrude(head_h)
        .translate((0.0, 0.0, head_bottom))
    )
    socket = (
        cq.Workplane("XY")
        .polygon(6, 0.55 * thread_d)
        .extrude(0.45 * head_h)
        .translate((0.0, 0.0, head_bottom + 0.60 * head_h))
    )
    result = shaft.union(head.cut(socket))
    return result


def _type_b_actuator(body_l1, body_d4, thread_d, lever_l2, lever_l3):
    """Connected adjustable actuator with shaft, lever, and clamp screw."""
    z_top = body_l1 / 2.0
    nut_h = 0.80 * thread_d
    shaft_bottom = -body_l1 / 2.0 - nut_h + 0.08 * thread_d
    clearance = max(0.10, 0.02 * thread_d)

    # 1. Vertical shaft.  Its locating boss enters the counterbore in the
    # handle root, while the axial tap-minor bore represents the threaded hole.
    boss_r = 0.70 * thread_d
    boss_h = 0.52 * thread_d
    shaft = _cylinder(
        0.50 * thread_d,
        z_top - shaft_bottom,
        shaft_bottom,
    )
    boss = _cylinder(boss_r, boss_h, z_top)
    thread_engagement = 0.72 * thread_d
    tap_minor_r = 0.39 * thread_d
    threaded_hole = _cylinder(
        tap_minor_r,
        thread_engagement + 0.10,
        z_top + boss_h - thread_engagement,
    )
    shaft = shaft.union(boss).cut(threaded_hole)

    # 2. Independent handle.  A round root sits over the locating boss.  Its
    # larger underside counterbore steps down to a narrow screw clearance hole.
    root_r = max(1.06 * thread_d, 0.19 * body_d4)
    root_h = 0.82 * thread_d
    root_z0 = z_top + 0.14 * thread_d
    root = _cylinder(root_r, root_h, root_z0)
    root = root.edges("%Circle").fillet(0.10 * thread_d)
    counterbore_depth = boss_h - (root_z0 - z_top) + clearance
    counterbore = _cylinder(
        boss_r + clearance,
        counterbore_depth,
        root_z0 - 0.05,
    )
    screw_clearance_r = 0.49 * thread_d
    through_hole = _cylinder(
        screw_clearance_r,
        root_h + 0.20,
        root_z0 - 0.10,
    )
    # The handle is one independent part made from a cylindrical root, a short
    # multi-section loft transition, and a long inclined grip.  The first loft
    # section begins inside the root so there is no abrupt butt joint.
    tip_r = max(0.34 * thread_d, 0.065 * body_d4)
    transition_root_r = max(0.68 * thread_d, 1.80 * tip_r)
    grip_root_r = max(0.45 * thread_d, 1.12 * tip_r)
    screw_head_r = 0.74 * thread_d
    arm_drop = 0.20 * thread_d
    # Embed the transition well inside the cylindrical root.  Its underside is
    # trimmed flush with the root before the boolean union, producing a broad,
    # clean connection instead of an almost tangent attachment.
    arm_start_x = 0.42 * root_r
    arm_start = cq.Vector(
        arm_start_x,
        0.0,
        root_z0 + 0.55 * root_h - arm_drop,
    )
    arm_end = cq.Vector(
        lever_l3 - tip_r,
        0.0,
        z_top + lever_l2 - tip_r,
    )
    arm_vector = arm_end - arm_start
    arm_length = arm_vector.Length
    arm_direction = arm_vector.normalized()
    transition_length = min(
        2.20 * thread_d,
        0.28 * arm_length,
    )
    handle_plane = cq.Plane(
        origin=arm_start,
        normal=arm_direction,
    )
    transition = (
        cq.Workplane(handle_plane)
        .circle(transition_root_r)
        .workplane(offset=transition_length)
        .circle(grip_root_r)
        .loft(combine=True, ruled=False)
    )
    grip_start = arm_start + arm_direction.multiply(transition_length)
    grip_length = arm_length - transition_length
    long_grip = cq.Solid.makeCone(
        grip_root_r,
        tip_r,
        grip_length,
        grip_start,
        arm_direction,
    )
    end_cap = cq.Solid.makeSphere(
        tip_r,
        arm_end,
        arm_direction,
        0.0,
        90.0,
        360.0,
    )
    # Open the clearance above the screw all the way through the inclined
    # transition.  A cutter limited to the screw-head height leaves a thin
    # overhanging patch of handle material above the head.
    handle_top = root_z0 + root_h
    screw_clearance_top = z_top + lever_l2 + tip_r
    screw_head_clearance = _cylinder(
        screw_head_r + clearance,
        screw_clearance_top - handle_top,
        handle_top,
    )
    underside_trim_h = 2.0 * transition_root_r + thread_d
    underside_trim = (
        cq.Workplane("XY")
        .box(
            2.4 * lever_l3,
            4.0 * transition_root_r,
            underside_trim_h,
        )
        .translate(
            (
                0.5 * lever_l3,
                0.0,
                root_z0 - 0.5 * underside_trim_h,
            )
        )
    )
    arm = (
        transition
        .union(cq.Workplane(obj=long_grip))
        .union(cq.Workplane(obj=end_cap))
        .cut(screw_head_clearance)
        .cut(underside_trim)
    )
    handle = root.union(arm)
    handle = handle.cut(counterbore).cut(through_hole)

    # 3. Coaxial fastening screw.  The narrow engagement core remains inside
    # the shaft bore, and the visible shank passes through the handle root.
    screw_head_h = 0.34 * thread_d
    engagement_core = _cylinder(
        tap_minor_r - clearance,
        thread_engagement,
        z_top + boss_h - thread_engagement,
    )
    screw_shank = _cylinder(
        0.45 * thread_d,
        handle_top - (z_top + boss_h),
        z_top + boss_h,
    )
    fusion_depth = max(0.04, 0.008 * thread_d)
    screw_head_z0 = handle_top - fusion_depth
    screw_head = _cylinder(
        screw_head_r,
        screw_head_h,
        screw_head_z0,
    )
    socket_depth = 0.42 * screw_head_h
    socket = (
        cq.Workplane("XY")
        .polygon(6, 0.38 * thread_d)
        .extrude(socket_depth + 0.05)
        .translate(
            (
                0.0,
                0.0,
                screw_head_z0 + screw_head_h - socket_depth,
            )
        )
    )
    # A hidden crest inside the tapped bore represents thread engagement and
    # connects the simplified screw to the shaft.  The head is inset by the
    # same tiny modeling allowance so it clamps and connects the lever root.
    thread_crest = _cylinder(
        tap_minor_r + fusion_depth,
        0.14 * thread_d,
        z_top + boss_h - 0.50 * thread_engagement,
    )
    fastening_screw = engagement_core.union(screw_shank).union(thread_crest).union(
        screw_head.cut(socket)
    )
    result = shaft.union(fastening_screw).union(handle)
    return result


def build_actuator(
    actuator_type,
    body_l1,
    body_d4,
    thread_d,
    lever_l2,
    lever_l3,
):
    """Published Type A screw or Type B adjustable-lever/stud component."""
    if int(actuator_type) == 0:
        result = _type_a_actuator(body_l1, thread_d)
    else:
        result = _type_b_actuator(
            body_l1,
            body_d4,
            thread_d,
            lever_l2,
            lever_l3,
        )
    return result


def build_hex_nut(body_l1, thread_d):
    """Separate DIN 934-like nut with clearance entries and engagement land."""
    nut_h = 0.80 * thread_d
    nut_circum_d = 1.80 * thread_d
    nut_top = -body_l1 / 2.0
    outer = (
        cq.Workplane("XY")
        .polygon(6, nut_circum_d)
        .extrude(nut_h)
        .translate((0.0, 0.0, nut_top - nut_h))
    )
    lead_h = 0.12 * nut_h
    lower_lead = _cylinder(
        0.54 * thread_d,
        lead_h + 0.2,
        nut_top - nut_h - 0.1,
    )
    upper_lead = _cylinder(
        0.54 * thread_d,
        lead_h + 0.2,
        nut_top - lead_h - 0.1,
    )
    engagement_bore = _cylinder(
        0.50 * thread_d,
        nut_h - 2.0 * lead_h,
        nut_top - nut_h + lead_h,
    )
    result = outer.cut(lower_lead).cut(upper_lead).cut(engagement_bore)
    return result


def build_distance_bushing(gap_l5, body_d4, thread_d):
    """Full-l5 central insert contacting both clamp-body inner faces."""
    clearance = max(0.10, 0.02 * thread_d)
    height = gap_l5
    outer_r = 0.46 * body_d4
    z0 = -height / 2.0
    outer = _cylinder(outer_r, height, z0)
    bore = _cylinder(
        0.50 * thread_d + clearance,
        height + 0.4,
        z0 - 0.2,
    )
    result = outer.cut(bore)
    return result


def _compression_spring(z0, spring_h, gap_l5, thread_d):
    """One coaxial helix with flat end coils for load-face contact."""
    coil_r = 0.72 * thread_d
    wire_r = min(0.045 * thread_d, 0.035 * gap_l5)
    pitch = spring_h / 2.0
    path = cq.Wire.makeHelix(pitch, spring_h, coil_r)
    helix = (
        cq.Workplane("XZ")
        .center(coil_r, 0.0)
        .circle(wire_r)
        .sweep(path, isFrenet=True)
        .translate((0.0, 0.0, z0))
    )
    lower_end = cq.Workplane(
        obj=cq.Solid.makeTorus(
            coil_r,
            wire_r,
            cq.Vector(0.0, 0.0, z0),
        )
    )
    upper_end = cq.Workplane(
        obj=cq.Solid.makeTorus(
            coil_r,
            wire_r,
            cq.Vector(0.0, 0.0, z0 + spring_h),
        )
    )
    result = helix.union(lower_end).union(upper_end)
    return result


def build_lower_compression_spring(gap_l5, thread_d):
    """Lower spring contacting its body pocket and the central insert."""
    wire_r = min(0.045 * thread_d, 0.035 * gap_l5)
    pocket_depth = 0.55 * gap_l5
    spring_h = pocket_depth - 2.0 * wire_r
    z0 = -gap_l5 / 2.0 - pocket_depth + wire_r
    result = _compression_spring(z0, spring_h, gap_l5, thread_d)
    return result


def build_upper_compression_spring(gap_l5, thread_d):
    """Upper spring contacting the central insert and its body pocket."""
    wire_r = min(0.045 * thread_d, 0.035 * gap_l5)
    pocket_depth = 0.55 * gap_l5
    spring_h = pocket_depth - 2.0 * wire_r
    z0 = gap_l5 / 2.0 + wire_r
    result = _compression_spring(z0, spring_h, gap_l5, thread_d)
    return result


def build(
    clamp_d,
    actuator_type,
    thread_d,
    body_d4,
    body_l1,
    lever_l2,
    lever_l3,
    jaw_l4,
    gap_l5,
    catalog_m,
):
    """Build the fixed GN 490 reference pose as seven named components."""
    lower_clamp_body = build_lower_clamp_body(
        body_l1,
        body_d4,
        jaw_l4,
        gap_l5,
        catalog_m,
        clamp_d,
        thread_d,
    )
    upper_clamp_body = build_upper_clamp_body(
        body_l1,
        body_d4,
        jaw_l4,
        gap_l5,
        catalog_m,
        clamp_d,
        thread_d,
    )
    actuator = build_actuator(
        actuator_type,
        body_l1,
        body_d4,
        thread_d,
        lever_l2,
        lever_l3,
    )
    hex_nut = build_hex_nut(body_l1, thread_d)
    distance_bushing = build_distance_bushing(gap_l5, body_d4, thread_d)
    lower_compression_spring = build_lower_compression_spring(
        gap_l5,
        thread_d,
    )
    upper_compression_spring = build_upper_compression_spring(
        gap_l5,
        thread_d,
    )

    result = cq.Assembly(name="swivel_clamp_connector_joint")
    result.add(
        lower_clamp_body,
        name="lower_clamp_body",
        color=cq.Color(0.64, 0.66, 0.68, 1.0),
    )
    result.add(
        upper_clamp_body,
        name="upper_clamp_body",
        color=cq.Color(0.72, 0.74, 0.76, 1.0),
    )
    result.add(
        actuator,
        name="actuator",
        color=cq.Color(0.72, 0.74, 0.76, 1.0),
    )
    result.add(
        hex_nut,
        name="hex_nut",
        color=cq.Color(0.48, 0.50, 0.52, 1.0),
    )
    result.add(
        distance_bushing,
        name="distance_bushing",
        color=cq.Color(0.88, 0.82, 0.36, 1.0),
    )
    result.add(
        lower_compression_spring,
        name="lower_compression_spring",
        color=cq.Color(0.38, 0.42, 0.46, 1.0),
    )
    result.add(
        upper_compression_spring,
        name="upper_compression_spring",
        color=cq.Color(0.48, 0.52, 0.56, 1.0),
    )
    return result
