"""Parametric metric plastic cable gland."""

import math

import cadquery as cq


def _hex_prism(sw, height, z0):
    corner_d = sw / math.cos(math.radians(30.0))
    return cq.Workplane("XY").workplane(offset=z0).polygon(6, corner_d).extrude(height)


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

    result = _ring_thread(thread_d, thread_len, -thread_len, pitch)

    lower_hex = _hex_prism(sw, lower_hex_h, 0.0)
    result = result.union(lower_hex)

    middle_z = lower_hex_h
    middle_thread_d = 0.74 * outer_dia_a
    middle_thread = _ring_thread(middle_thread_d, middle_thread_h, middle_z, pitch)
    result = result.union(middle_thread)

    upper_hex_z = middle_z + middle_thread_h
    upper_hex = _hex_prism(sw, upper_hex_h, upper_hex_z)
    result = result.union(upper_hex)

    # Six ribs are placed only at upper-hex corners; flat centers stay smooth.
    hex_corner_r = sw / (2.0 * math.cos(math.radians(30.0)))
    rib_out = max(1.0, min(2.2, 0.045 * outer_dia_a))
    rib_width = max(1.2, 0.05 * outer_dia_a)
    rib_z = upper_hex_z + 0.12 * upper_hex_h
    rib_h = 0.76 * upper_hex_h
    for angle in range(0, 360, 60):
        rib = (
            cq.Workplane("XY")
            .workplane(offset=rib_z)
            .center(hex_corner_r + rib_out / 2.0 - 0.55, 0.0)
            .rect(rib_out + 1.1, rib_width)
            .extrude(rib_h)
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
        )
        result = result.union(rib)

    dome_z = upper_hex_z + upper_hex_h
    cap_r = outer_dia_a / 2.0
    exit_r = bore_r + max(1.8, 0.06 * outer_dia_a)
    cap_top_z = dome_z + dome_h
    dome = (
        cq.Workplane("XZ")
        .moveTo(0.0, dome_z)
        .lineTo(cap_r, dome_z)
        .threePointArc((1.02 * cap_r, dome_z + 0.36 * dome_h), (exit_r, cap_top_z))
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
    return result
