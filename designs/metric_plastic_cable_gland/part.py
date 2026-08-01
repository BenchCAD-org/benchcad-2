"""Parametric metric plastic cable gland."""

import math

import cadquery as cq


def _hex_prism(sw, height, z0, chamfer_size):
    corner_d = sw / math.cos(math.radians(30.0))
    part = cq.Workplane("XY").workplane(offset=z0).polygon(6, corner_d).extrude(height)
    part = part.edges("|Z").chamfer(chamfer_size)
    # washer-face style chamfer on both hex rims (the z-direction chamfer a
    # moulded gland hex carries), sized to survive the smallest catalog rows
    face_ch = min(0.12 * height, 0.6)
    part = part.edges(">Z").chamfer(face_ch)
    part = part.edges("<Z").chamfer(face_ch)
    return part


def _ring_thread(major_d, height, z0, pitch):
    core_d = major_d - 1.2 * pitch
    threaded = cq.Workplane("XY").workplane(offset=z0).circle(core_d / 2.0).extrude(height)
    crest_count = max(1, int(height / pitch))
    for index in range(crest_count):
        crest_z = z0 + 0.35 + index * pitch
        if crest_z + 0.45 > z0 + height:
            break
        crest = cq.Workplane("XY").workplane(offset=crest_z).circle(major_d / 2.0).extrude(0.45)
        threaded = threaded.union(crest)
    return threaded


def build(
    size_index,
    thread_d,
    sw,
    outer_dia_a,
    overall_len,
    thread_len,
    clamp_min,
    clamp_max,
    o_ring,
    tightened,
):
    """Build a detailed SKINTOP-style metric polyamide cable gland."""
    pitch = 1.5
    body_h = overall_len - thread_len
    lower_hex_h = 0.16 * body_h
    middle_thread_h = 0.14 * body_h
    upper_hex_h = 0.38 * body_h
    dome_h = body_h - lower_hex_h - middle_thread_h - upper_hex_h
    bore_r = clamp_max / 2.0

    result = _ring_thread(thread_d, thread_len + 0.2, -thread_len, pitch)

    lower_hex = _hex_prism(sw, lower_hex_h, 0.0, 0.45)
    result = result.union(lower_hex)

    middle_z = lower_hex_h
    middle_thread_d = 0.74 * outer_dia_a
    middle_thread = _ring_thread(
        middle_thread_d,
        middle_thread_h + 0.4,
        middle_z - 0.2,
        pitch,
    )
    result = result.union(middle_thread)

    upper_hex_z = middle_z + middle_thread_h
    upper_hex = _hex_prism(sw, upper_hex_h, upper_hex_z, 0.65)

    # Two narrow pockets are cut beside each corner. Their central untouched
    # strip forms the grip ridge; the broad hex-flat centres remain smooth.
    hex_corner_r = sw / (2.0 * math.cos(math.radians(30.0)))
    notch_radial = max(2.2, 0.10 * outer_dia_a)
    notch_tangent = max(0.8, 0.03 * outer_dia_a)
    notch_z = upper_hex_z - 0.1
    notch_h = upper_hex_h + 0.2
    for corner_angle in range(0, 360, 60):
        for side in (-1.0, 1.0):
            notch = (
                cq.Workplane("XY")
                .workplane(offset=notch_z)
                .center(hex_corner_r - 0.75, 0.0)
                .rect(notch_radial, notch_tangent)
                .extrude(notch_h)
                .rotate(
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 1.0),
                    corner_angle + side * 8.5,
                )
            )
            upper_hex = upper_hex.cut(notch)
    result = result.union(upper_hex)

    dome_z = upper_hex_z + upper_hex_h
    # the dome base is the hex's INSCRIBED circle (tangent to the flats in top
    # view, never proud of them) — review finding on the top-view tangency
    cap_r = sw / 2.0
    cap_top_z = dome_z + dome_h
    # cap profile = one quarter ELLIPSE from the side to the FLAT top: vertical
    # tangent at the base, horizontal tangent at the top plane — no arc+line
    cb_r_ref = bore_r + max(1.2, 0.045 * outer_dia_a)
    ell_a = max(1.0, cap_r - cb_r_ref - 0.8)      # horizontal semi-axis
    ell_b = cap_top_z - (dome_z - 0.2)            # vertical semi-axis
    dome = (
        cq.Workplane("XZ")
        .moveTo(0.0, dome_z - 0.2)
        .lineTo(cap_r, dome_z - 0.2)
        .ellipseArc(ell_a, ell_b, 0, 90)
        .lineTo(0.0, cap_top_z)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )
    result = result.union(dome)

    if o_ring:
        seal_band = cq.Workplane("XY").workplane(offset=-2.0).circle(thread_d / 2.0).extrude(2.0)
        result = result.union(seal_band)

    bore = (
        cq.Workplane("XY")
        .workplane(offset=-thread_len - 0.5)
        .circle(bore_r)
        .extrude(overall_len + 1.0)
    )
    result = result.cut(bore)

    # stepped top entry: the seal counterbore — a larger opening at the dome
    # top stepping down to the clamp bore (two concentric circles in top view)
    cb_r = bore_r + max(1.2, 0.045 * outer_dia_a)
    cb_depth = 0.30 * dome_h
    counterbore = (
        cq.Workplane("XY")
        .workplane(offset=cap_top_z - cb_depth)
        .circle(cb_r)
        .extrude(cb_depth + 0.5)
    )
    result = result.cut(counterbore)

    # entry chamfers on the bottom face: 45-degree lead-in on the thread-end
    # OD (core cylinder rim) and a matching cone at the bore mouth
    core_r = (thread_d - 1.2 * pitch) / 2.0
    ch = 0.8
    od_ch = (
        cq.Workplane("XZ")
        .moveTo(core_r - ch, -thread_len)
        .lineTo(thread_d / 2.0 + 1.0, -thread_len)
        .lineTo(thread_d / 2.0 + 1.0, -thread_len + ch + 1.0)
        .lineTo(core_r, -thread_len + ch)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )
    result = result.cut(od_ch)
    bore_ch = (
        cq.Workplane("XZ")
        .moveTo(0.0, -thread_len - 0.2)
        .lineTo(bore_r + 0.7, -thread_len - 0.2)
        .lineTo(bore_r, -thread_len + 0.7)
        .lineTo(0.0, -thread_len + 0.7)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )
    result = result.cut(bore_ch)
    return result
