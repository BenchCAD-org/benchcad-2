"""hex_socket_flat_head_cap_screw - drawing-anchored flat-head socket screw.

The shank uses simplified circumferential thread grooves for visual recognition.
They are not a full standards-accurate helical thread model.
"""

import math

import cadquery as cq


def _hex_points(across_flats: float) -> list[tuple[float, float]]:
    radius = across_flats / math.sqrt(3.0)
    pts = []
    for i in range(6):
        ang = math.pi / 6.0 + i * math.pi / 3.0
        pts.append((radius * math.cos(ang), radius * math.sin(ang)))
    return pts


def _cut_thread_grooves(
    solid: cq.Workplane,
    shank_d: float,
    shank_len: float,
    pitch: float,
    groove_depth: float,
    groove_width: float,
    tip_clear: float,
    head_clear: float,
) -> cq.Workplane:
    groove_r = max(shank_d / 2.0 - groove_depth, shank_d * 0.32)
    start_z = tip_clear + groove_width / 2.0
    end_z = shank_len - head_clear - groove_width / 2.0
    z = start_z
    result = solid
    while z <= end_z:
        cutter = (
            cq.Workplane("XZ")
            .moveTo(0.0, z - groove_width / 2.0)
            .lineTo(shank_d / 2.0, z - groove_width / 2.0)
            .lineTo(groove_r, z)
            .lineTo(shank_d / 2.0, z + groove_width / 2.0)
            .lineTo(0.0, z + groove_width / 2.0)
            .close()
            .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        )
        result = result.cut(cutter)
        z += pitch
    return result


def build(
    length,
    shank_d,
    head_d,
    head_h,
    socket_af,
    socket_depth,
    neck_d,
    tip_chamfer,
):
    shank_len = length - head_h
    shank_r = shank_d / 2.0
    head_r = head_d / 2.0
    neck_r = neck_d / 2.0
    pitch = max(round(shank_d * 0.15625, 3), 0.8)
    groove_depth = shank_d * 0.055
    groove_width = pitch * 0.56

    body = cq.Workplane("XY").circle(shank_r).extrude(shank_len)
    head = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(head_r, 0.0)
        .lineTo(neck_r, head_h)
        .lineTo(0.0, head_h)
        .close()
        .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        .translate((0.0, 0.0, shank_len))
    )
    result = body.union(head)
    result = _cut_thread_grooves(
        result,
        shank_d=shank_d,
        shank_len=shank_len,
        pitch=pitch,
        groove_depth=groove_depth,
        groove_width=groove_width,
        tip_clear=max(tip_chamfer * 1.4, pitch * 0.35),
        head_clear=pitch * 0.85,
    )

    if tip_chamfer > 0:
        tip_r = max(shank_r - tip_chamfer, shank_r * 0.35)
        tip = (
            cq.Workplane("XZ")
            .moveTo(0.0, 0.0)
            .lineTo(shank_r, 0.0)
            .lineTo(tip_r, tip_chamfer)
            .lineTo(0.0, tip_chamfer)
            .close()
            .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        )
        result = result.cut(tip)

    socket = (
        cq.Workplane("XY", origin=(0.0, 0.0, length))
        .polyline(_hex_points(socket_af))
        .close()
        .extrude(-socket_depth)
    )
    socket_tip_r = socket_af * 0.20
    socket_tip = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(socket_tip_r, 0.0)
        .lineTo(0.0, socket_tip_r * 1.2)
        .close()
        .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        .translate((0.0, 0.0, length - socket_depth))
    )
    result = result.cut(socket.union(socket_tip))
    return result
