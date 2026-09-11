"""STAUFF RB round U-bolt with either an RUK or RUL plastic saddle."""

import math
import cadquery as cq


def _modeled_external_metric_thread(nominal_d, pitch, length):
    """Simplified ISO 68-1 60-degree external thread along positive Z."""
    major_r = nominal_d / 2.0
    root_r = (nominal_d - 1.226869 * pitch) / 2.0
    radial_embed = min(0.08, 0.05 * pitch)
    half_width = (major_r - root_r + radial_embed) / math.sqrt(3.0)
    path_r = (major_r + root_r) / 2.0
    path_height = length - 2.0 * half_width
    core = cq.Workplane("XY").circle(root_r).extrude(length)
    path = cq.Wire.makeHelix(pitch, path_height, path_r)
    profile = (cq.Workplane("XZ")
               .polyline([(root_r - radial_embed, -half_width),
                          (major_r, 0.0),
                          (root_r - radial_embed, half_width)])
               .close())
    ridge = profile.sweep(path, isFrenet=True).translate((0.0, 0.0, half_width))
    return core.union(ridge)


def _modeled_internal_metric_groove(nominal_d, pitch, length):
    """Simplified ISO 68-1 60-degree internal-thread groove cutter."""
    major_r = nominal_d / 2.0
    minor_r = (nominal_d - 1.082532 * pitch) / 2.0
    radial_embed = min(0.08, 0.05 * pitch)
    half_width = (major_r - minor_r + radial_embed) / math.sqrt(3.0)
    path = cq.Wire.makeHelix(pitch, length + 2.0 * half_width, minor_r)
    profile = (cq.Workplane("XZ")
               .polyline([(minor_r - radial_embed, -half_width),
                          (major_r, 0.0),
                          (minor_r - radial_embed, half_width)])
               .close())
    return profile.sweep(path, isFrenet=True).translate((0.0, 0.0, -half_width))


def _round_u_bolt(a, l1, h1, h2, h3, rod_d):
    # A is the clear inside width; L1 is the leg center spacing (= A + G).
    bend_r = l1 / 2.0
    leg_end_z = -h3
    top_z = -h3 + h1 - rod_d / 2.0
    spring_z = top_z - bend_r
    path = (
        cq.Workplane("XZ").moveTo(-bend_r, leg_end_z).lineTo(-bend_r, spring_z)
        .threePointArc((0.0, top_z), (bend_r, spring_z))
        .lineTo(bend_r, leg_end_z).wire().val()
    )
    profile = (
        cq.Workplane("XY").workplane(offset=leg_end_z)
        .center(-bend_r, 0.0).circle(rod_d / 2.0)
    )
    smooth = profile.sweep(path, isFrenet=True)

    # H2 is the sourced threaded height measured upward from both leg ends.
    pitch = {10.0: 1.50, 12.0: 1.75, 16.0: 2.00,
             20.0: 2.50, 24.0: 3.00}[float(rod_d)]
    thread = _modeled_external_metric_thread(rod_d, pitch, h2)
    for x in (-bend_r, bend_r):
        thread_cutter = (cq.Workplane("XY").workplane(offset=leg_end_z)
                         .center(x, 0.0).circle(rod_d / 2.0 + 0.05)
                         .extrude(h2))
        smooth = smooth.cut(thread_cutter)
        smooth = smooth.union(thread.translate((x, 0.0, leg_end_z)))
    _ = a
    return smooth


def _saddle(variant, d1, l2, l3, b, h4, h5, h6, h7, auxiliary_d):
    bottom_z = 0.0
    relief = (
        cq.Workplane("XZ").center(0.0, h4).circle(d1 / 2.0)
        .extrude(b + 2.0).translate((0.0, -(b + 2.0) / 2.0, 0.0))
    )
    saddle = (
        cq.Workplane("XY").box(l2, b, h6)
        .translate((0.0, 0.0, bottom_z + h6 / 2.0)).cut(relief)
    )
    if int(variant) == 0:
        # RUK is between the legs; D2 is the diameter of two bottom bosses.
        for sx in (-1.0, 1.0):
            boss = (cq.Workplane("XY").workplane(offset=-h7)
                    .center(sx * l3 / 2.0, 0.0)
                    .circle(auxiliary_d / 2.0).extrude(h7 + 0.1))
            saddle = saddle.union(boss)
    else:
        # RUL spans the U legs; D4 holes lie at its sourced L3 centers.
        return (saddle.faces(">Z").workplane()
                .pushPoints([(-l3 / 2.0, 0.0), (l3 / 2.0, 0.0)])
                .hole(auxiliary_d))
    return saddle


def _iso_hex_nut(thread_d):
    # ISO 261/68-1 coarse pitch and ISO 4032 nut envelopes. M10--M16 mirror
    # the standard-components demo; M20/M24 extend the same published tables.
    rows = {
        10.0: (1.50, 16.0, 8.4),
        12.0: (1.75, 18.0, 10.8),
        16.0: (2.00, 24.0, 14.8),
        20.0: (2.50, 30.0, 18.0),
        24.0: (3.00, 36.0, 21.5),
    }
    pitch, across_flats, height = rows[float(thread_d)]
    corner_d = across_flats / math.cos(math.pi / 6.0)
    blank = cq.Workplane("XY").polygon(6, corner_d).extrude(height).val()
    chamfer_h = min(0.12 * height, 0.30 * thread_d)
    face_land_r = 0.475 * across_flats
    crown_r = corner_d / 2.0 + 0.01
    envelope = (cq.Workplane("XZ").moveTo(0.0, 0.0)
                .lineTo(face_land_r, 0.0).lineTo(crown_r, chamfer_h)
                .lineTo(crown_r, height - chamfer_h).lineTo(face_land_r, height)
                .lineTo(0.0, height).close()
                .revolve(360.0, (0.0, 0.0), (0.0, 1.0)).val())
    minor_d = thread_d - 1.082532 * pitch
    bore = cq.Workplane("XY").circle(minor_d / 2.0).extrude(height).val()
    nut = blank.intersect(envelope).cut(bore)
    groove = _modeled_internal_metric_groove(thread_d, pitch, height).val()
    return cq.Workplane(obj=nut.cut(groove))


def build(saddle_variant, catalog_row, d1, a, l1, h1, h2, thread_d,
          h3, h4, l2, l3, b, h5, h6, h7, auxiliary_d):
    """Return a named six-solid assembly: U-bolt, saddle, and four nuts."""
    del catalog_row
    u_bolt = _round_u_bolt(a, l1, h1, h2, h3, thread_d)
    saddle = _saddle(saddle_variant, d1, l2, l3, b, h4, h5, h6,
                     h7, auxiliary_d)
    saddle_top = h6
    nut_h = {10.0: 8.4, 12.0: 10.8, 16.0: 14.8,
             20.0: 18.0, 24.0: 21.5}[float(thread_d)]
    # One nut per leg lies on each side of the mounting baseline/saddle.
    gap = max(0.4, 0.04 * thread_d)  # proportion: visible, non-fusing gap
    if int(saddle_variant) == 0:
        upper_z = gap
    else:
        upper_z = saddle_top + gap
    lower_z = -nut_h - gap
    nut = _iso_hex_nut(thread_d)

    result = cq.Assembly(name="round_u_bolt_pipe_saddle_clamp")
    result.add(u_bolt, name="round_u_bolt")
    result.add(saddle, name="saddle")
    poses = [(-l1 / 2.0, lower_z), (l1 / 2.0, lower_z),
             (-l1 / 2.0, upper_z), (l1 / 2.0, upper_z)]
    for i, (x, z) in enumerate(poses, start=1):
        result.add(nut.translate((x, 0.0, z)), name=f"nut_{i:02d}")
    return result
