"""STAUFF ACT field-tray pipe clamp assembly."""

import math
import cadquery as cq


# (tube_od_D1, body_L1, bolt_pitch_L2, body_H, group)
_BODY_ROWS = (
    (6.0, 37.0, 20.0, 26.0, "1A"),
    (6.4, 37.0, 20.0, 26.0, "1A"),
    (8.0, 37.0, 20.0, 26.0, "1A"),
    (9.5, 37.0, 20.0, 26.0, "1A"),
    (10.0, 37.0, 20.0, 26.0, "1A"),
    (12.0, 37.0, 20.0, 26.0, "1A"),
    (12.7, 42.0, 26.0, 32.0, "2"),
    (14.0, 42.0, 26.0, 32.0, "2"),
    (14.3, 42.0, 26.0, 32.0, "2"),
    (15.0, 42.0, 26.0, 32.0, "2"),
    (16.0, 42.0, 26.0, 32.0, "2"),
    (18.0, 42.0, 26.0, 32.0, "2"),
    (19.0, 50.0, 33.0, 35.5, "3"),
    (20.0, 50.0, 33.0, 35.5, "3"),
    (21.3, 50.0, 33.0, 35.5, "3"),
    (25.0, 50.0, 33.0, 35.5, "3"),
    (25.4, 50.0, 33.0, 35.5, "3"),
    (26.9, 59.0, 40.0, 42.0, "4"),
    (28.0, 59.0, 40.0, 42.0, "4"),
    (30.0, 59.0, 40.0, 42.0, "4"),
    (32.0, 71.0, 52.0, 58.0, "5"),
    (35.0, 71.0, 52.0, 58.0, "5"),
    (38.0, 71.0, 52.0, 58.0, "5"),
    (42.0, 71.0, 52.0, 58.0, "5"),
)

# group: (DP_L1, DP_L2, DP_B, DP_S, DP_D,
#         HKS_H1, HKS_H2, HKS_H3, head_B, head_L)
_HARDWARE_ROWS = {
    "1A": (34.0, 20.0, 30.0, 3.0, 7.0, 44.3, 40.0, 4.3, 6.1, 13.3),
    "2": (40.5, 26.0, 30.0, 3.0, 7.0, 49.3, 45.0, 4.3, 6.1, 13.3),
    "3": (48.0, 33.0, 30.0, 3.0, 7.0, 54.3, 50.0, 4.3, 6.1, 13.3),
    "4": (57.0, 40.0, 30.0, 3.0, 7.0, 59.3, 55.0, 4.3, 6.1, 13.3),
    "5": (70.0, 52.0, 30.0, 3.0, 7.0, 74.3, 70.0, 4.3, 6.1, 13.3),
}


def _y_cylinder(radius, length, x, z):
    # XZ's positive normal points along -Y in CadQuery.  Center the extrusion
    # and build both ways so bore cutters and ACE strips span the body depth
    # instead of projecting from one outer face.
    return (
        cq.Workplane("XZ", origin=(x, 0.0, z))
        .circle(radius)
        .extrude(length / 2.0, both=True)
    )


def _clamp_half(body_l1, body_w, body_h, tube_od, bolt_pitch, strip_d, strip_embed):
    half = cq.Workplane("XY").box(body_l1, body_w, body_h / 2.0).translate(
        (0.0, 0.0, body_h / 4.0)
    )
    half = half.cut(_y_cylinder(tube_od / 2.0, body_w + 2.0, 0.0, 0.0))
    holes = (
        cq.Workplane("XY")
        .pushPoints([(-bolt_pitch / 2.0, 0.0), (bolt_pitch / 2.0, 0.0)])
        .circle(3.6)
        .extrude(body_h + 2.0, both=True)
    )
    half = half.cut(holes)

    # Two integrated ACE contact strips per half. Their undimensioned circular
    # section and embed are explicit proportion parameters.
    contact_r = tube_od / 2.0 + strip_d / 2.0 - strip_embed
    strip_x = min(tube_od * 0.30, body_l1 * 0.13)
    strip_z = math.sqrt(max(contact_r * contact_r - strip_x * strip_x, 0.0))
    for x in (-strip_x, strip_x):
        half = half.union(_y_cylinder(strip_d / 2.0, body_w, x, strip_z))
    return half


def _cover_plate(length, width, thickness, pitch, hole_d):
    return (
        cq.Workplane("XY")
        .box(length, width, thickness)
        .faces(">Z")
        .workplane()
        .pushPoints([(-pitch / 2.0, 0.0), (pitch / 2.0, 0.0)])
        .hole(hole_d)
    )


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


def _hks_bolt(shank_l, head_h, head_narrow, head_l):
    head = cq.Workplane("XY").box(head_l, head_narrow, head_h).translate(
        (0.0, 0.0, head_h / 2.0)
    )
    # HKS is a fully threaded M6 hammerhead bolt.  Keep the non-standard head
    # sourced from the catalogue and use the standard-components M6 coarse
    # thread geometry for its shank.
    shank = _modeled_external_metric_thread(6.0, 1.0, shank_l).translate(
        (0.0, 0.0, head_h)
    )
    return head.union(shank)


def _iso_hex_nut(nominal_d):
    # ISO 4032 / ISO 68-1 envelope values mirrored from the reviewed
    # standard-components demo.  ACT uses only M6 MUS-HKS nuts.
    rows = {6.0: (1.0, 10.0, 5.2)}  # d: pitch, across flats, max height
    pitch, across_flats, height = rows[float(nominal_d)]
    corner_d = across_flats / math.cos(math.pi / 6.0)
    blank = cq.Workplane("XY").polygon(6, corner_d).extrude(height).val()
    chamfer_h = min(0.12 * height, 0.30 * nominal_d)
    face_land_r = 0.475 * across_flats
    crown_r = corner_d / 2.0 + 0.01
    envelope = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(face_land_r, 0.0)
        .lineTo(crown_r, chamfer_h)
        .lineTo(crown_r, height - chamfer_h)
        .lineTo(face_land_r, height)
        .lineTo(0.0, height)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
        .val()
    )
    minor_d = nominal_d - 1.082532 * pitch
    bore = cq.Workplane("XY").circle(minor_d / 2.0).extrude(height).val()
    nut = blank.intersect(envelope).cut(bore)
    groove = _modeled_internal_metric_groove(nominal_d, pitch, height).val()
    return cq.Workplane(obj=nut.cut(groove))


def build(size_index, strip_d, strip_embed):
    """Build one row-coupled, seven-solid ACT field-tray clamp."""
    tube_od, body_l1, bolt_pitch, body_h, group = _BODY_ROWS[int(size_index)]
    (
        cover_l1,
        cover_pitch,
        cover_w,
        cover_t,
        cover_hole_d,
        _hks_total_h,
        hks_shank_l,
        head_h,
        head_narrow,
        head_l,
    ) = _HARDWARE_ROWS[group]

    half = _clamp_half(body_l1, 30.0, body_h, tube_od, bolt_pitch, strip_d, strip_embed)
    cover = _cover_plate(cover_l1, cover_w, cover_t, cover_pitch, cover_hole_d)
    bolt = _hks_bolt(hks_shank_l, head_h, head_narrow, head_l)
    nut = _iso_hex_nut(6.0)

    cover_z = body_h / 2.0 + cover_t / 2.0 + 0.2
    nut_z = body_h / 2.0 + cover_t + 0.2
    bolt_z = -body_h / 2.0 - head_h - 0.2

    result = cq.Assembly(name="act_field_tray_pipe_clamp")
    result.add(half, name="clamp_half_01", color=cq.Color(0.18, 0.20, 0.22))
    result.add(
        half,
        name="clamp_half_02",
        loc=cq.Location(cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0), 180.0),
        color=cq.Color(0.18, 0.20, 0.22),
    )
    result.add(cover, name="cover_plate", loc=cq.Location(cq.Vector(0.0, 0.0, cover_z)))
    for index, x in enumerate((-bolt_pitch / 2.0, bolt_pitch / 2.0), start=1):
        result.add(
            bolt,
            name=f"hks_bolt_{index:02d}",
            loc=cq.Location(cq.Vector(x, 0.0, bolt_z)),
        )
        result.add(
            nut,
            name=f"lock_nut_{index:02d}",
            loc=cq.Location(cq.Vector(x, 0.0, nut_z)),
        )
    return result
