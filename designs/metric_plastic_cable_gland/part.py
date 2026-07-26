"""Parametric metric plastic cable gland."""

import math

import cadquery as cq


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
    """Build an assembled SKINTOP-style metric polyamide cable gland."""
    pitch = 1.5
    body_and_cap_h = overall_len - thread_len
    body_h = 0.42 * body_and_cap_h
    cap_h = body_and_cap_h - body_h
    cap_r = outer_dia_a / 2.0
    grip_depth = max(1.0, min(2.5, 0.05 * outer_dia_a))
    grip_root_r = cap_r - grip_depth
    bore_r = clamp_max / 2.0
    exit_r = bore_r + max(1.8, 0.08 * outer_dia_a)

    # Simplified external Mx1.5 connection thread: a minor cylinder plus
    # pitch-spaced crests. The published nominal diameter and pitch are exact;
    # the crest form is a proportion because the molded thread profile is not.
    thread_core_d = thread_d - 1.2 * pitch
    result = (
        cq.Workplane("XY")
        .workplane(offset=-thread_len)
        .circle(thread_core_d / 2.0)
        .extrude(thread_len)
    )
    crest_count = int(thread_len / pitch)
    for i in range(crest_count):
        z = -thread_len + 0.45 + i * pitch
        crest = (
            cq.Workplane("XY")
            .workplane(offset=z)
            .circle(thread_d / 2.0)
            .extrude(0.45)
        )
        result = result.union(crest)

    # The body is specified by its wrench size SW; the cap diameter A lies
    # between the hex flats and corners in every catalog row.
    hex_corner_d = sw / math.cos(math.radians(30.0))
    body = cq.Workplane("XY").polygon(6, hex_corner_d).extrude(body_h)
    result = result.union(body)

    # Revolved domed cap. The internal trapezoidal thread and seal insert are
    # intentionally represented by the functional through-bore.
    dome_start_z = body_h + 0.55 * cap_h
    cap = (
        cq.Workplane("XZ")
        .moveTo(0.0, body_h)
        .lineTo(grip_root_r, body_h)
        .lineTo(grip_root_r, dome_start_z)
        .lineTo(cap_r, dome_start_z)
        .threePointArc(
            (0.92 * cap_r, body_h + 0.82 * cap_h),
            (exit_r, body_h + cap_h),
        )
        .lineTo(0.0, body_h + cap_h)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )

    # Twelve longitudinal ribs reproduce the round-fluted cap while preserving
    # the catalog diameter A as the outer envelope.
    flute_h = 0.48 * cap_h
    for angle in range(0, 360, 30):
        rib = (
            cq.Workplane("XY")
            .workplane(offset=body_h)
            .center(grip_root_r + 0.5 * grip_depth - 0.75, 0.0)
            .rect(grip_depth + 1.5, max(1.0, 0.12 * cap_r))
            .extrude(flute_h)
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
        )
        cap = cap.union(rib)
    result = result.union(cap)

    # M40 and larger rows carry a 2 mm section O-ring under the shoulder.
    # Model it as the catalog-sized smooth band around the threaded core.
    if o_ring:
        seal_band = (
            cq.Workplane("XY")
            .workplane(offset=-2.0)
            .circle(thread_d / 2.0)
            .extrude(2.0)
        )
        result = result.union(seal_band)

    bore = (
        cq.Workplane("XY")
        .workplane(offset=-thread_len - 0.5)
        .circle(bore_r)
        .extrude(overall_len + 1.0)
    )
    result = result.cut(bore)
    return result
