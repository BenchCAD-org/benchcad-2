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
    clamp_d,
    thread_d,
):
    """One complete cast clamp body with an end-entry V-groove."""
    body_r = body_d4 / 2.0
    passage_r = 0.60 * thread_d
    groove_clearance = 0.02 * clamp_d
    groove_center = -(
        0.50 * clamp_d + passage_r + groove_clearance
    )
    groove_depth = (0.50 + math.sqrt(0.50)) * clamp_d + groove_clearance
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

    result = body.cut(passage).cut(groove)
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
        clamp_d,
        thread_d,
    )
    return result


def _type_a_actuator(body_l1, thread_d):
    """DIN 912-like socket-head screw, separate from the DIN 934 nut."""
    head_h = 0.85 * thread_d
    head_r = 0.80 * thread_d
    shaft_r = 0.50 * thread_d
    nut_h = 0.80 * thread_d
    shaft_bottom = -body_l1 / 2.0 - nut_h + 0.08 * thread_d
    head_bottom = body_l1 / 2.0

    shaft = _cylinder(
        shaft_r,
        head_bottom + 0.12 * head_h - shaft_bottom,
        shaft_bottom,
    )
    head = _cylinder(head_r, head_h, head_bottom)
    socket = (
        cq.Workplane("XY")
        .polygon(6, 0.55 * thread_d)
        .extrude(0.45 * head_h)
        .translate((0.0, 0.0, head_bottom + 0.60 * head_h))
    )
    result = shaft.union(head.cut(socket))
    return result


def _type_b_actuator(body_l1, body_d4, thread_d, lever_l2, lever_l3):
    """Adjustable-lever/stud component with the published l2/l3 envelope."""
    hub_h = 1.35 * thread_d
    handle_t = max(0.70 * thread_d, 0.14 * body_d4)
    handle_w = 1.40 * handle_t
    handle_t0 = 1.18 * handle_t
    handle_t1 = 0.92 * handle_t
    end_r = handle_t1 / 2.0
    hub_r = max(0.90 * thread_d, 0.62 * handle_w)
    z_top = body_l1 / 2.0
    nut_h = 0.80 * thread_d
    shaft_bottom = -body_l1 / 2.0 - nut_h + 0.08 * thread_d

    shaft = _cylinder(
        0.50 * thread_d,
        z_top + 0.18 * hub_h - shaft_bottom,
        shaft_bottom,
    )
    hub = _cylinder(hub_r, hub_h, z_top)

    # Keep the inclination established from the two published orthogonal outer
    # projections.  The rounded finished end, not only its centerline, reaches
    # x=l3 and z=body_l1/2+l2.
    start_x = 0.35 * hub_r
    start_z = z_top + 0.70 * hub_h
    end_x = lever_l3 - end_r
    end_z = body_l1 / 2.0 + lever_l2 - end_r
    dx = end_x - start_x
    dz = end_z - start_z
    centerline_len = math.sqrt(dx * dx + dz * dz)
    normal_x = -dz / centerline_len
    normal_z = dx / centerline_len
    handle = (
        cq.Workplane("XZ")
        .polyline(
            [
                (
                    start_x + normal_x * handle_t0 / 2.0,
                    start_z + normal_z * handle_t0 / 2.0,
                ),
                (
                    end_x + normal_x * handle_t1 / 2.0,
                    end_z + normal_z * handle_t1 / 2.0,
                ),
                (
                    end_x - normal_x * handle_t1 / 2.0,
                    end_z - normal_z * handle_t1 / 2.0,
                ),
                (
                    start_x - normal_x * handle_t0 / 2.0,
                    start_z - normal_z * handle_t0 / 2.0,
                ),
            ]
        )
        .close()
        .extrude(handle_w / 2.0, both=True)
    )
    end = (
        cq.Workplane("XZ")
        .center(end_x, end_z)
        .circle(end_r)
        .extrude(handle_w / 2.0, both=True)
    )
    handle = handle.union(end).edges().fillet(0.14 * handle_t)
    button_h = 0.15 * hub_h
    button = _cylinder(
        0.34 * hub_r,
        button_h,
        z_top + hub_h - 0.05 * button_h,
    )
    result = shaft.union(hub).union(handle).union(button)
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
    """Separate DIN 934-like hex nut with a round thread-envelope bore."""
    nut_h = 0.80 * thread_d
    nut_circum_d = 1.80 * thread_d
    nut_top = -body_l1 / 2.0
    outer = (
        cq.Workplane("XY")
        .polygon(6, nut_circum_d)
        .extrude(nut_h)
        .translate((0.0, 0.0, nut_top - nut_h))
    )
    bore = _cylinder(
        0.54 * thread_d,
        nut_h + 0.4,
        nut_top - nut_h - 0.2,
    )
    result = outer.cut(bore)
    return result


def build_distance_bushing(gap_l5, body_d4, thread_d):
    """Single central circular distance bushing with no eccentric opening."""
    clearance = max(0.10, 0.02 * thread_d)
    height = 0.24 * gap_l5
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
    """One coaxial helical compression spring around the actuator."""
    coil_r = 0.72 * thread_d
    wire_r = min(0.045 * thread_d, 0.035 * gap_l5)
    pitch = spring_h / 2.5
    path = cq.Wire.makeHelix(pitch, spring_h, coil_r)
    result = (
        cq.Workplane("XZ")
        .center(coil_r, 0.0)
        .circle(wire_r)
        .sweep(path, isFrenet=True)
        .translate((0.0, 0.0, z0))
    )
    return result


def build_lower_compression_spring(gap_l5, thread_d):
    """Lower spring between the lower body and central distance bushing."""
    bushing_h = 0.24 * gap_l5
    spring_h = 0.30 * gap_l5
    clearance = 0.04 * gap_l5
    z0 = -bushing_h / 2.0 - clearance - spring_h
    result = _compression_spring(z0, spring_h, gap_l5, thread_d)
    return result


def build_upper_compression_spring(gap_l5, thread_d):
    """Upper spring between the central distance bushing and upper body."""
    bushing_h = 0.24 * gap_l5
    spring_h = 0.30 * gap_l5
    clearance = 0.04 * gap_l5
    z0 = bushing_h / 2.0 + clearance
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
    """Build the GN 490 reference pose as seven named physical components."""
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
        color=cq.Color(0.64, 0.66, 0.68),
    )
    result.add(
        upper_clamp_body,
        name="upper_clamp_body",
        color=cq.Color(0.72, 0.74, 0.76),
    )
    result.add(
        actuator,
        name="actuator",
        color=cq.Color(0.72, 0.74, 0.76),
    )
    result.add(
        hex_nut,
        name="hex_nut",
        color=cq.Color(0.48, 0.50, 0.52),
    )
    result.add(
        distance_bushing,
        name="distance_bushing",
        color=cq.Color(0.88, 0.82, 0.36),
    )
    result.add(
        lower_compression_spring,
        name="lower_compression_spring",
        color=cq.Color(0.38, 0.42, 0.46),
    )
    result.add(
        upper_compression_spring,
        name="upper_compression_spring",
        color=cq.Color(0.48, 0.52, 0.56),
    )
    return result
