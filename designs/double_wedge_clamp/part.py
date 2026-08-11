"""JW Winco GN 920.1 double-wedge clamp as a static catalog assembly."""

import cadquery as cq


def build(
    jaw_type,
    d,
    b,
    jaw_span,
    h1,
    h2,
    h3,
    screw_projection,
    m,
):
    """Build two opposed jaws, the central wedge, and the low-head screw."""
    jaw_width = 0.90 * d
    guide_clearance = max(0.25, 0.025 * d)
    center_gap = jaw_span - 2.0 * jaw_width
    wedge_top_width = center_gap - 2.0 * guide_clearance
    wedge_bottom_width = max(0.38 * wedge_top_width, 1.30 * d)
    lower_z = 0.14 * h1

    jaw_left = _build_jaw(
        -1.0,
        int(jaw_type),
        jaw_span,
        jaw_width,
        wedge_top_width,
        wedge_bottom_width,
        b,
        d,
        h1,
        h2,
        h3,
        m,
        guide_clearance,
        lower_z,
    )
    jaw_right = _build_jaw(
        1.0,
        int(jaw_type),
        jaw_span,
        jaw_width,
        wedge_top_width,
        wedge_bottom_width,
        b,
        d,
        h1,
        h2,
        h3,
        m,
        guide_clearance,
        lower_z,
    )
    center_wedge = _build_center_wedge(
        d,
        b,
        h1,
        h2,
        wedge_top_width,
        wedge_bottom_width,
        guide_clearance,
        lower_z,
    )
    screw = _build_screw(d, h1, h2, screw_projection)

    result = cq.Assembly()
    result.add(jaw_left, name="jaw_left")
    result.add(jaw_right, name="jaw_right")
    result.add(center_wedge, name="center_wedge")
    result.add(screw, name="screw")
    return result


def _build_jaw(
    side,
    jaw_type,
    jaw_span,
    jaw_width,
    wedge_top_width,
    wedge_bottom_width,
    b,
    d,
    h1,
    h2,
    h3,
    m,
    clearance,
    lower_z,
):
    outer_x = side * jaw_span / 2.0
    inner_top_x = side * (jaw_span / 2.0 - jaw_width)
    inner_bottom_x = side * (wedge_bottom_width / 2.0 + clearance)

    if side < 0.0:
        profile = [
            (outer_x, 0.0),
            (inner_bottom_x, 0.0),
            (inner_bottom_x, lower_z),
            (inner_top_x, h1),
            (outer_x, h1),
        ]
    else:
        profile = [
            (inner_bottom_x, 0.0),
            (outer_x, 0.0),
            (outer_x, h1),
            (inner_top_x, h1),
            (inner_bottom_x, lower_z),
        ]

    jaw = _xz_prism(profile, b)
    jaw = jaw.cut(
        _guide_prism(
            side,
            wedge_top_width,
            wedge_bottom_width,
            lower_z,
            h1,
            h1 + h2,
            b,
            clearance,
            True,
        )
    )

    # Type GA: the drawing specifies two M4 threads, 5 mm deep, per jaw.
    # Thread helices are omitted; nominal-diameter blind cylinders show them.
    if jaw_type == 1:
        for y in (-m / 2.0, m / 2.0):
            jaw = jaw.cut(_blind_hole(outer_x, y, h3, side, 4.0, 5.0))

    # Type RF: the catalog gives no tooth dimensions. A deterministic crossed
    # shallow-groove texture distinguishes the serrated clamping face.
    if jaw_type == 2:
        jaw = _add_simplified_serration(jaw, outer_x, side, b, h1)

    return jaw


def _build_center_wedge(
    d,
    b,
    h1,
    h2,
    wedge_top_width,
    wedge_bottom_width,
    clearance,
    lower_z,
):
    top_z = h1 + h2
    head_d = 1.35 * d
    contact_rise = h1 - lower_z
    top_scale = (top_z - lower_z) / contact_rise
    center_top_width = (
        wedge_bottom_width
        + (wedge_top_width - wedge_bottom_width) * top_scale
    )
    wedge = _xz_prism(
        [
            (-wedge_bottom_width / 2.0, lower_z),
            (wedge_bottom_width / 2.0, lower_z),
            (center_top_width / 2.0, top_z),
            (-center_top_width / 2.0, top_z),
        ],
        b - 2.0 * clearance,
    )

    for side in (-1.0, 1.0):
        wedge = wedge.union(
            _guide_prism(
                side,
                wedge_top_width,
                wedge_bottom_width,
                lower_z,
                h1,
                top_z,
                b,
                clearance,
                False,
            )
        )

    shank_clearance_d = 1.15 * d
    through_hole = (
        cq.Workplane("XY")
        .workplane(offset=lower_z - 1.0)
        .circle(shank_clearance_d / 2.0)
        .extrude(top_z - lower_z + 2.0)
    )
    wedge = wedge.cut(through_hole)

    head_h = 0.45 * d
    head_protrusion = 0.35 * head_h
    recess_depth = head_h - head_protrusion
    bearing_z = top_z - recess_depth
    head_recess = (
        cq.Workplane("XY")
        .workplane(offset=bearing_z)
        .circle((head_d + 2.0 * clearance) / 2.0)
        .extrude(recess_depth + 0.1)
    )
    return wedge.cut(head_recess)


def _coarse_thread_pitch(d):
    """ISO 261 preferred coarse pitch for the two catalog screw sizes."""
    if abs(d - 8.0) < 1e-9:
        return 1.25
    if abs(d - 12.0) < 1e-9:
        return 1.75
    raise ValueError("double_wedge_clamp supports only catalog M8 and M12 screws")


def _external_thread(d, pitch, z0, z1):
    """Visible 60-degree external thread ridge on the projecting screw end."""
    major_r = d / 2.0
    root_r = major_r - 0.54 * pitch
    radial_embed = min(0.08, 0.05 * pitch)
    half_width = 0.30 * pitch
    path_r = (major_r + root_r) / 2.0
    path_height = z1 - z0 - 2.0 * half_width
    path = cq.Wire.makeHelix(pitch, path_height, path_r)
    profile = (
        cq.Workplane("XZ")
        .polyline(
            [
                (root_r - radial_embed, -half_width),
                (major_r, 0.0),
                (root_r - radial_embed, half_width),
            ]
        )
        .close()
    )
    result = profile.sweep(path, isFrenet=True).translate(
        (0.0, 0.0, z0 + half_width)
    )
    return result


def _build_screw(d, h1, h2, screw_projection):
    top_z = h1 + h2
    head_d = 1.35 * d
    head_h = 0.45 * d
    head_protrusion = 0.35 * head_h
    recess_depth = head_h - head_protrusion
    bearing_z = top_z - recess_depth
    shank_top = bearing_z + 0.2
    pitch = _coarse_thread_pitch(d)
    root_r = d / 2.0 - 0.54 * pitch

    thread_core = (
        cq.Workplane("XY")
        .workplane(offset=-screw_projection)
        .circle(root_r)
        .extrude(screw_projection + 0.05)
    )
    thread_ridge = _external_thread(
        d,
        pitch,
        -screw_projection,
        0.0,
    )
    smooth_shank = (
        cq.Workplane("XY")
        .workplane(offset=-0.05)
        .circle(d / 2.0)
        .extrude(shank_top + 0.05)
    )
    head = (
        cq.Workplane("XY")
        .workplane(offset=bearing_z)
        .circle(head_d / 2.0)
        .extrude(head_h)
    )
    screw = thread_core.union(thread_ridge).union(smooth_shank).union(head)

    # DIN 7984 is the catalog callout; exact socket dimensions are not printed
    # there, so this hex recess is an explicit visual proportion.
    socket_d = 0.62 * d
    socket_depth = 0.22 * d
    socket = (
        cq.Workplane("XY")
        .workplane(offset=top_z + 0.01)
        .polygon(6, socket_d)
        .extrude(-socket_depth)
    )
    return screw.cut(socket)


def _xz_prism(points, depth):
    return (
        cq.Workplane("XZ")
        .polyline(points)
        .close()
        .extrude(depth / 2.0, both=True)
    )


def _blind_hole(outer_x, y, z, side, diameter, depth):
    start_x = outer_x + side * 0.1
    direction = cq.Vector(-side, 0.0, 0.0)
    hole = cq.Solid.makeCylinder(
        diameter / 2.0,
        depth + 0.1,
        cq.Vector(start_x, y, z),
        direction,
    )
    return cq.Workplane("XY").newObject([hole])


def _guide_prism(
    side,
    wedge_top_width,
    wedge_bottom_width,
    lower_z,
    h1,
    top_z,
    b,
    clearance,
    is_slot,
):
    """One continuous, top-open T rail or slot along the sloped interface."""
    x0 = side * wedge_bottom_width / 2.0
    z0 = lower_z
    x1 = side * wedge_top_width / 2.0
    z1 = h1
    dx = x1 - x0
    dz = z1 - z0
    face_length = (dx * dx + dz * dz) ** 0.5
    tx = dx / face_length
    tz = dz / face_length
    nx = side * tz
    nz = -side * tx

    # The rail follows the unchanged contact slope beyond h1. It is modeled
    # long, then clipped by the center wedge's horizontal lower and upper
    # planes. The slot cutter remains overlong so both jaw ends are open.
    if is_slot:
        path_min_z = -max(1.0, 0.08 * h1)
        path_max_z = top_z + max(1.0, 0.08 * h1)
    else:
        path_min_z = lower_z - 2.0
        path_max_z = top_z + 2.0

    start_scale = (path_min_z - z0) / dz
    end_scale = (path_max_z - z0) / dz
    start_x = x0 + start_scale * dx
    end_x = x0 + end_scale * dx
    cx = (start_x + end_x) / 2.0
    cz = (path_min_z + path_max_z) / 2.0
    half_length = (
        ((end_x - start_x) ** 2 + (path_max_z - path_min_z) ** 2) ** 0.5
        / 2.0
    )

    fit = 0.15 if is_slot else 0.0
    embed = 0.35 + fit
    neck_height = 0.55 + fit
    head_height = 0.75 + fit

    def strip(normal_min, normal_max):
        return [
            (
                cx - tx * half_length + nx * normal_min,
                cz - tz * half_length + nz * normal_min,
            ),
            (
                cx + tx * half_length + nx * normal_min,
                cz + tz * half_length + nz * normal_min,
            ),
            (
                cx + tx * half_length + nx * normal_max,
                cz + tz * half_length + nz * normal_max,
            ),
            (
                cx - tx * half_length + nx * normal_max,
                cz - tz * half_length + nz * normal_max,
            ),
        ]

    neck_width = max(2.60, 0.09 * b)
    head_width = max(5.00, 0.18 * b)
    y_fit = fit
    neck = _xz_prism(
        strip(-embed, neck_height),
        neck_width + 2.0 * y_fit,
    )
    head = _xz_prism(
        strip(neck_height - 0.10 - fit, neck_height + head_height),
        head_width + 2.0 * y_fit,
    )
    guide = neck.union(head)
    if is_slot:
        return guide

    center_top_scale = (top_z - z0) / dz
    center_top_x = x0 + center_top_scale * dx
    slab_half_x = max(abs(x0), abs(center_top_x)) + 5.0
    slab = _xz_prism(
        [
            (-slab_half_x, lower_z),
            (slab_half_x, lower_z),
            (slab_half_x, top_z),
            (-slab_half_x, top_z),
        ],
        b + 2.0,
    )
    return guide.intersect(slab)


def _add_simplified_serration(jaw, outer_x, side, b, h1):
    cut_depth = 0.55
    groove = 0.32
    inside_x = outer_x - side * cut_depth / 2.0

    z_pitch = 2.4
    z = 1.2
    while z < 0.84 * h1:
        cutter = (
            cq.Workplane("XY")
            .box(cut_depth + 0.2, b + 0.4, groove)
            .translate((inside_x, 0.0, z))
        )
        jaw = jaw.cut(cutter)
        z += z_pitch

    y_pitch = 2.8
    y = -b / 2.0 + y_pitch
    while y < b / 2.0:
        cutter = (
            cq.Workplane("XY")
            .box(cut_depth + 0.2, groove, 0.72 * h1)
            .translate((inside_x, y, 0.40 * h1))
        )
        jaw = jaw.cut(cutter)
        y += y_pitch
    return jaw
