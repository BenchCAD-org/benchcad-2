"""Parametric CadQuery rebuild of GN 866 pneumatic power clamp.

The STEP reference separates cleanly into three solids: the main body and two
mirrored grippers.  This rebuild keeps that exact assembly split, but models
each solid independently so the orientation and per-part comparison stay close
to the source STEP.
"""

import cadquery as cq


EXAMPLE_PARAMS = {
    "size": 20.0,
    "max_moment": 60.0,
    "fs": 630.0,
    "fh": 1150.0,
    "a": 21.0,
    "b": 10.0,
    "d1": 28.0,
    "d2": 5.0,
    "d3": 7.0,
    "d4": 4.1,
    "d5_major": 5.0,
    "l1": 138.0,
    "l2": 160.0,
    "l3": 57.5,
    "l4": 24.5,
    "l5": 5.0,
    "l6": 89.0,
    "m1": 12.0,
    "m2": 7.5,
    "m3": 17.0,
    "m4": 0.0,
    "m5": 22.0,
    "m6": 13.0,
    "r": 48.0,
    "s1": 32.0,
    "s2": 38.0,
    "t": 13.0,
    "w": 66.0,
}


def _box(x, y, z, center, fillet=0.0):
    part = cq.Workplane("XY").box(x, y, z).translate(center)
    fillet = min(float(fillet), x * 0.18, y * 0.18, z * 0.18)
    if fillet > 0.05:
        try:
            part = part.edges().fillet(fillet)
        except Exception:
            pass
    return part


def _cyl_x(d, length, x, y=0.0, z=0.0):
    return cq.Workplane("YZ").circle(d / 2.0).extrude(length / 2.0, both=True).translate((x, y, z))


def _cyl_y(d, length, y, x=0.0, z=0.0):
    return cq.Workplane("XZ").circle(d / 2.0).extrude(length / 2.0, both=True).translate((x, y, z))


def _cyl_z(d, length, z, x=0.0, y=0.0):
    return cq.Workplane("XY").circle(d / 2.0).extrude(length / 2.0, both=True).translate((x, y, z))


def _loft_xz_rect(stations):
    """Loft XZ rectangles along Y; stations are (y, width_x, depth_z)."""
    first_y, first_x, first_z = stations[0]
    wp = cq.Workplane("XZ").workplane(offset=-first_y).rect(first_x, first_z)
    prev_y = first_y
    for y, width_x, depth_z in stations[1:]:
        wp = wp.workplane(offset=-(y - prev_y)).rect(width_x, depth_z)
        prev_y = y
    return wp.loft(combine=True)


def _dims(size, l1, l2, l4, m3, s1, s2, t):
    scale = float(size) / 20.0 if float(size) > 0 else 1.0
    width_x = max(float(s1), 32.0 * scale)
    depth_z = max(float(s2), 38.0 * scale)
    body_len = float(l1)
    overall_len = max(float(l2), 160.0 * scale)
    lower_block_len = max(float(l4), 24.5 * scale)
    cyl_len = 57.5 * scale
    head_len = max(body_len - cyl_len, 80.5 * scale)
    gripper_y0 = 50.5 * scale
    gripper_y1 = 102.5 * scale
    return {
        "scale": scale,
        "width_x": width_x,
        "depth_z": depth_z,
        "body_len": body_len,
        "overall_len": overall_len,
        "lower_block_len": lower_block_len,
        "head_len": head_len,
        "cyl_len": cyl_len,
        "gripper_y0": gripper_y0,
        "gripper_y1": gripper_y1,
        "plate_thick": max(float(t), 13.0 * scale),
        "y_pitch": max(float(m3), 17.0 * scale),
    }


def _make_body(size, d1, d2, d3, d4, d5_major, l1, l4, l6, m3, m4, s1, s2, dims):
    width_x = dims["width_x"]
    depth_z = dims["depth_z"]
    cyl_len = dims["cyl_len"]
    head_len = dims["head_len"]
    lower_len = dims["lower_block_len"]
    scale = dims["scale"]

    cyl_d = min(float(d1), 28.0 * scale)
    body = _cyl_y(cyl_d, cyl_len, -cyl_len / 2.0, 0.0, 0.0)

    lower_block_y1 = 34.5 * scale
    lower_block = _loft_xz_rect(
        [
            (0.0, width_x, 32.0 * scale),
            (lower_block_y1, width_x, 32.0 * scale),
        ]
    )
    body = body.union(lower_block)

    shoulder = _loft_xz_rect(
        [
            (33.5 * scale, width_x, 16.0 * scale),
            (35.5 * scale, width_x * 0.98, depth_z * 0.97),
            (52.0 * scale, width_x * 0.98, depth_z * 0.97),
            (61.0 * scale, width_x * 0.90, depth_z * 0.96),
            (68.0 * scale, width_x * 0.78, depth_z * 0.92),
            (75.5 * scale, width_x * 0.60, depth_z * 0.88),
            (80.5 * scale, width_x * 0.18, depth_z * 0.82),
        ]
    )
    body = body.union(shoulder)

    side_plate_len = 44.0 * scale
    side_plate_y = 57.5 * scale
    for z in (-depth_z * 0.355, depth_z * 0.355):
        body = body.union(
            _box(
                width_x * 0.92,
                side_plate_len,
                depth_z * 0.18,
                (0.0, side_plate_y, z),
                min(width_x, depth_z) * 0.025,
            )
        )

    fork_len = max(head_len * 0.24, float(d1) * 0.72)
    body = body.cut(_box(width_x * 0.30, fork_len, depth_z * 1.08, (0.0, head_len - fork_len / 2.0, 0.0), 0.0))

    window_len = max(head_len * 0.34, lower_len * 0.95)
    window_y = head_len * 0.60
    body = body.cut(_box(width_x * 1.10, window_len, depth_z * 0.42, (0.0, window_y, 0.0), 0.0))

    z_offset = min(depth_z * 0.29, 11.0 * scale)
    lower_y = 7.5 * scale
    for y in (lower_y, lower_y + dims["y_pitch"]):
        for z in (-z_offset, z_offset):
            body = body.cut(_cyl_x(d3, width_x * 1.12, 0.0, y, z))
            body = body.cut(_cyl_x(d2, width_x * 1.22, 0.0, y, z))

    return body


def _gripper_outline(side, dims, a):
    scale = dims["scale"]
    mirror = -1.0 if side < 0 else 1.0
    x_scale = scale * max(float(a) / 21.0, 0.80)
    y_scale = scale
    raw = [
        (16.0, 82.304),
        (8.0, 82.304),
        (4.639, 83.4),
        (-8.581, 79.858),
        (-11.41, 77.029),
        (-14.364, 66.005),
        (-14.5, 64.97),
        (-14.5, 54.5),
        (-10.5, 50.5),
        (-0.86, 50.5),
        (6.517, 55.404),
        (16.0, 78.0),
    ]
    return [(mirror * x * x_scale, y * y_scale) for x, y in raw]


def _make_gripper(side, a, b, d1, d2, d3, d4, l3, m1, m2, dims):
    scale = dims["scale"]
    thick_z = max(float(dims["plate_thick"]), 13.0 * scale)
    outline = _gripper_outline(side, dims, a)
    mirror = -1.0 if side < 0 else 1.0

    body = cq.Workplane("XY").polyline(outline).close().extrude(thick_z / 2.0, both=True)

    # Side-face bores restored; the front-facing round/unknown holes stay out.
    bore_y_1 = 83.272 * scale
    bore_y_2 = 95.272 * scale
    bore_x_outer = mirror * 14.95 * scale
    bore_x_inner = mirror * 10.95 * scale
    bore_len_outer = max(float(d1) * 0.075, 2.1 * scale)
    bore_len_inner = max(float(d1) * 0.21, 5.9 * scale)
    for y in (bore_y_1, bore_y_2):
        body = body.cut(_cyl_x(float(d3), bore_len_outer, bore_x_outer, y, 0.0))
        body = body.cut(_cyl_x(float(d2), bore_len_inner, bore_x_inner, y, 0.0))

    # Top lug: a single tapered stem with the two STEP-like bores, not a U-cut fork.
    stem = _loft_xz_rect(
        [
            (82.0 * scale, 10.2 * scale, thick_z * 1.01),
            (88.0 * scale, 8.8 * scale, thick_z * 1.01),
            (102.5 * scale, 7.8 * scale, thick_z * 1.01),
        ]
    ).translate((mirror * 11.0 * scale, 0.0, 0.0))
    body = body.union(stem)

    tip_hole_x = mirror * 11.0 * scale
    for y in (88.8 * scale, 99.2 * scale):
        body = body.cut(_cyl_x(float(d3), 9.8 * scale, tip_hole_x, y, 0.0))
        body = body.cut(_cyl_x(float(d2), 12.2 * scale, tip_hole_x, y, 0.0))

    return body.translate((0.0, 0.0, side * 1.5 * scale))


def build(
    size,
    max_moment,
    fs,
    fh,
    a,
    b,
    d1,
    d2,
    d3,
    d4,
    d5_major,
    l1,
    l2,
    l3,
    l4,
    l5,
    l6,
    m1,
    m2,
    m3,
    m4,
    m5,
    m6,
    r,
    s1,
    s2,
    t,
    w,
):
    dims = _dims(float(size), float(l1), float(l2), float(l4), float(m3), float(s1), float(s2), float(t))
    body = _make_body(
        float(size),
        float(d1),
        float(d2),
        float(d3),
        float(d4),
        float(d5_major),
        float(l1),
        float(l4),
        float(l6),
        float(m3),
        float(m4),
        float(s1),
        float(s2),
        dims,
    )
    left_gripper = _make_gripper(-1.0, float(a), float(b), float(d1), float(d2), float(d3), float(d4), float(l3), float(m1), float(m2), dims)
    right_gripper = _make_gripper(1.0, float(a), float(b), float(d1), float(d2), float(d3), float(d4), float(l3), float(m1), float(m2), dims)

    result = cq.Compound.makeCompound([body.val(), left_gripper.val(), right_gripper.val()])
    return result


if "show_object" in globals():
    result = build(**EXAMPLE_PARAMS)
    show_object(result, name="gn866_pneumatic_power_clamp_assembly")
