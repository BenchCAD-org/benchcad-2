"""Parametric Häfele Minifix 15 eccentric-cam connector housing."""

import math

import cadquery as cq


def _sector_wire(outer_r, inner_r, z, angle_0, angle_1):
    """Return a closed annular-sector wire with exact circular boundaries."""
    outer = cq.Edge.makeCircle(
        outer_r,
        (0.0, 0.0, z),
        (0.0, 0.0, 1.0),
        angle_0,
        angle_1,
        True,
    )
    inner = cq.Edge.makeCircle(
        inner_r,
        (0.0, 0.0, z),
        (0.0, 0.0, 1.0),
        angle_0,
        angle_1,
        False,
    )
    return cq.Wire.assembleEdges(
        [
            outer,
            cq.Edge.makeLine(outer.endPoint(), inner.startPoint()),
            inner,
            cq.Edge.makeLine(inner.endPoint(), outer.startPoint()),
        ]
    )


def _sector_prism(outer_r, wall, z0, z1, center, half_angle):
    """Make one curved cage-wall sector between two axial stations."""
    inner_r = outer_r - wall
    bottom = _sector_wire(outer_r, inner_r, z0, center - half_angle, center + half_angle)
    top = _sector_wire(outer_r, inner_r, z1, center - half_angle, center + half_angle)
    return cq.Solid.makeLoft([bottom, top], ruled=True)


def _open_plate(radius, thickness, z0, mouth_center_x, mouth_half_width):
    """Make a circular C-plate with a round-ended radial bolt-entry mouth."""
    plate = cq.Workplane("XY").workplane(offset=z0).circle(radius).extrude(thickness)
    plate = plate.edges("%CIRCLE").fillet(min(0.28, thickness * 0.30))
    cut_z = z0 - 0.05
    cut_depth = thickness + 0.10
    round_end = (
        cq.Workplane("XY")
        .workplane(offset=cut_z)
        .center(mouth_center_x, 0.0)
        .circle(mouth_half_width)
        .extrude(cut_depth)
    )
    outer_x = radius + 0.8
    rect_length = outer_x - mouth_center_x
    open_end = (
        cq.Workplane("XY")
        .workplane(offset=cut_z)
        .center((mouth_center_x + outer_x) / 2.0, 0.0)
        .rect(rect_length, mouth_half_width * 2.0)
        .extrude(cut_depth)
    )
    return plate.cut(round_end.union(open_end))


def _capture_cutter(body_diameter, bolt_axis_height, bolt_hole_diameter):
    """Make the OEM flat-ended, round-closed radial capture opening."""
    scale = body_diameter / 15.0
    clearance_scale = 1.0 + 0.06 * (bolt_hole_diameter - 7.0)
    lip_x = -1.80 * scale
    round_radius = 1.70 * scale * clearance_scale
    flat = 0.30 * scale * clearance_scale
    lower_center_z = bolt_axis_height - flat / 2.0
    upper_center_z = bolt_axis_height + flat / 2.0
    apex_x = lip_x - round_radius
    diagonal = round_radius / math.sqrt(2.0)
    outer_x = (body_diameter - 0.10) / 2.0 + 0.80
    profile = (
        cq.Workplane("XZ")
        .moveTo(outer_x, lower_center_z - round_radius)
        .lineTo(lip_x, lower_center_z - round_radius)
        .threePointArc(
            (lip_x - diagonal, lower_center_z - diagonal),
            (apex_x, lower_center_z),
        )
        .lineTo(apex_x, upper_center_z)
        .threePointArc(
            (lip_x - diagonal, upper_center_z + diagonal),
            (lip_x, upper_center_z + round_radius),
        )
        .lineTo(outer_x, upper_center_z + round_radius)
        .close()
        .extrude(body_diameter, both=True)
    )
    return profile


def _radial_rib(inner_r, outer_r, thickness, z0, z1, angle):
    """Make a straight radial web joining the inner cam to the outer cage."""
    length = outer_r - inner_r
    rib = (
        cq.Workplane("XY")
        .box(length, thickness, z1 - z0)
        .translate(((inner_r + outer_r) / 2.0, 0.0, (z0 + z1) / 2.0))
    )
    return rib.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)


def _gusset(inner_r, outer_r, z0, height, thickness, angle):
    """Make one triangular die-cast root gusset at the face plate."""
    gusset = (
        cq.Workplane("XZ")
        .moveTo(inner_r, z0)
        .lineTo(outer_r, z0)
        .lineTo(outer_r, z0 + height)
        .lineTo(inner_r, z0 + height * 0.18)
        .close()
        .extrude(thickness / 2.0, both=True)
    )
    return gusset.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)


def _revolved_face(radius, thickness):
    """Make the shallow dished operating face measured from the OEM STEP."""
    radial_scale = radius / 8.15
    flat_radius = 3.90 * radial_scale
    return (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(radius, 0.0)
        .lineTo(radius - 0.013 * radial_scale, -0.184 * thickness)
        .lineTo(radius - 0.485 * radial_scale, -0.754 * thickness)
        .lineTo(flat_radius, -thickness)
        .lineTo(0.0, -thickness)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )


def _arrow_cutter(outer_r, width, z0, depth, center, half_angle):
    """Make one recessed curved direction arrow on the operating face."""
    arc = _sector_prism(outer_r, width, z0, z0 + depth, center, half_angle)
    end_angle = math.radians(center + half_angle)
    radial = (math.cos(end_angle), math.sin(end_angle))
    tangent = (-math.sin(end_angle), math.cos(end_angle))
    mid_r = outer_r - width * 0.50
    base_x = mid_r * radial[0]
    base_y = mid_r * radial[1]
    half_base = width * 1.45
    arrow_length = width * 2.35
    points = [
        (
            base_x + radial[0] * half_base,
            base_y + radial[1] * half_base,
        ),
        (
            base_x - radial[0] * half_base,
            base_y - radial[1] * half_base,
        ),
        (
            base_x + tangent[0] * arrow_length,
            base_y + tangent[1] * arrow_length,
        ),
    ]
    head = cq.Workplane("XY").workplane(offset=z0).polyline(points).close().extrude(depth)
    return cq.Workplane("XY").newObject([arc]).union(head)


def _pz_wire(scale, z):
    """Return the 28-point combined-drive outline measured from OEM CAD."""
    quadrant = (
        (3.607, 0.550),
        (3.259, 0.849),
        (1.864, 0.849),
        (1.177, 2.038),
        (0.849, 2.038),
        (0.849, 3.259),
        (0.550, 3.607),
    )
    points = []
    for quarter in range(4):
        angle = math.radians(quarter * 90.0)
        cosine = math.cos(angle)
        sine = math.sin(angle)
        for x, y in quadrant:
            points.append(
                (
                    scale * (x * cosine - y * sine),
                    scale * (x * sine + y * cosine),
                    z,
                )
            )
    return cq.Wire.makePolygon(points, close=True)


def _hex_wire(across_flats, z):
    """Return an SW hexagon wire from its dimension across flats."""
    radius = across_flats / math.sqrt(3.0)
    points = [
        (
            radius * math.cos(math.radians(30.0 + 60.0 * index)),
            radius * math.sin(math.radians(30.0 + 60.0 * index)),
            z,
        )
        for index in range(6)
    ]
    return cq.Wire.makePolygon(points, close=True)


def _combined_drive_cutter(body_diameter, face_z):
    """Make the OEM PZ2/flat/SW4 combination recess and tapered bottom."""
    scale = body_diameter / 15.0
    pz_end_z = 2.20 * scale
    pz = cq.Solid.makeLoft(
        [
            _pz_wire(scale, face_z),
            _pz_wire(scale * 0.986, pz_end_z),
        ],
        ruled=True,
    )
    hex_across = 4.02 * scale
    hex_end_z = 3.70 * scale
    hex_socket = cq.Solid.makeLoft(
        [
            _hex_wire(hex_across, pz_end_z - 0.05),
            _hex_wire(hex_across, hex_end_z),
        ],
        ruled=True,
    )
    bottom = cq.Solid.makeLoft(
        [
            _hex_wire(hex_across, hex_end_z - 0.02),
            _hex_wire(hex_across * 0.22, 3.98 * scale),
        ],
        ruled=True,
    )
    return cq.Workplane("XY").newObject([pz]).union(hex_socket).union(bottom)


def build(
    body_diameter,
    housing_height,
    has_rim,
    rim_diameter,
    rim_height,
    bolt_axis_height,
    bolt_hole_diameter,
    cam_web_thickness,
):
    """Build a catalogue-parametric housing calibrated to OEM 262.25.035.

    The cross-section and cage topology follow the downloadable Häfele STEP.
    The other catalogue lengths are obtained by moving the bolt window with A
    and extending the cage to X; unmeasured SKU-to-SKU changes remain declared
    proportional approximations in ``spec.py`` and ``family.json``.
    """
    # The 262.25.035 STEP measures Ø14.90 inside the nominal Ø15 bore and
    # Ø16.30 at its nominal Ø16.5 rim.  Its body stops 0.65 mm short of X.
    body_radius = (body_diameter - 0.10) / 2.0
    body_depth = housing_height - 0.65
    face_radius = (rim_diameter - 0.20) / 2.0 if has_rim else body_radius
    face_thickness = rim_height * 0.80 if has_rim else 0.48

    cap_thickness = body_diameter * (0.70 / 15.0)
    cap_z = body_depth - cap_thickness
    overlap = 0.10

    # OEM sections from z=4.212 to z=13.150 are an intersecting-circle
    # crescent.  Coordinates are rotated 90° from the native STEP so the
    # capture mouth remains on +X in this readable construction.
    cam_radius = body_diameter * (4.40 / 15.0)
    cam_dx = body_diameter * (0.4279 / 15.0)
    cam_dy = body_diameter * (1.9829 / 15.0)
    cam_inner_radius = body_diameter * (3.7872 / 15.0)
    cam_inner_dx = body_diameter * (0.9875 / 15.0)
    cam_inner_dy = body_diameter * (1.5315 / 15.0)
    hub_radius = body_diameter * (3.60 / 15.0)
    bolt_slot_half = body_diameter * (1.85 / 15.0)
    bolt_slot_half *= 1.0 + 0.06 * (bolt_hole_diameter - 7.0)
    lower_cam_z = min(
        body_diameter * (4.20 / 15.0),
        bolt_axis_height - bolt_slot_half - 0.45,
    )

    # Face plate, centred drive hub, and an offset loft form the cam spindle.
    result = _revolved_face(face_radius, face_thickness)
    drive_hub = (
        cq.Workplane("XY").workplane(offset=-0.05).circle(hub_radius).extrude(lower_cam_z + 0.18)
    )
    lower_wire = cq.Wire.makeCircle(
        hub_radius,
        (0.0, 0.0, lower_cam_z - 0.38),
        (0.0, 0.0, 1.0),
    )
    upper_wire = cq.Wire.makeCircle(
        cam_radius,
        (cam_dx, cam_dy, lower_cam_z + 0.18),
        (0.0, 0.0, 1.0),
    )
    cam_transition = cq.Solid.makeLoft([lower_wire, upper_wire], ruled=False)
    result = result.union(drive_hub).union(cam_transition)

    # A round-ended radial pocket turns the offset barrel into the actual
    # C-shaped bolt capture visible in the OEM side and end views.
    cam_barrel = (
        cq.Workplane("XY")
        .workplane(offset=lower_cam_z)
        .center(cam_dx, cam_dy)
        .circle(cam_radius)
        .extrude(cap_z - lower_cam_z + overlap)
    )
    cam_inner = (
        cq.Workplane("XY")
        .workplane(offset=lower_cam_z - 0.05)
        .center(cam_inner_dx, cam_inner_dy)
        .circle(cam_inner_radius)
        .extrude(cap_z - lower_cam_z + overlap + 0.10)
    )
    cam_barrel = cam_barrel.cut(cam_inner)
    capture_cutter = _capture_cutter(body_diameter, bolt_axis_height, bolt_hole_diameter)
    cam_barrel = cam_barrel.cut(capture_cutter)
    result = result.union(cam_barrel)

    # The opposite-end C-plate carries the same open direction as the bolt
    # pocket.  Its dimensions are normalized from the 262.25.035 top view.
    cap = _open_plate(
        body_radius,
        cap_thickness + overlap,
        cap_z - overlap,
        body_diameter * (-1.40 / 15.0),
        body_diameter * (4.10 / 15.0),
    )
    result = result.union(cap)

    # Windowed circular cage: broad rear shell, narrow side rails, and split
    # entry shoulders.  This replaces the previous three decorative lofts.
    wall = cam_web_thickness
    wall_z0 = -0.05
    wall_z1 = cap_z + overlap
    rear_wall = cq.Workplane("XY").newObject(
        [_sector_prism(body_radius, wall, wall_z0, wall_z1, 270.0, 41.0)]
    )
    lower_window_bottom = body_diameter * (2.15 / 15.0)
    lower_window_top = min(
        bolt_axis_height - bolt_slot_half - 0.38,
        body_depth * 0.48,
    )
    lower_window_height = max(1.20, lower_window_top - lower_window_bottom)
    lower_window_width = min(
        body_diameter * (2.10 / 15.0),
        lower_window_height * 0.72,
    )
    lower_window_z = (lower_window_bottom + lower_window_top) / 2.0
    lower_windows = None
    for x_offset in (-body_diameter * 0.155, body_diameter * 0.155):
        window = (
            cq.Workplane("XZ")
            .center(x_offset, lower_window_z)
            .slot2D(
                lower_window_height,
                lower_window_width,
                90.0,
            )
            .extrude(body_diameter, both=True)
        )
        lower_windows = window if lower_windows is None else lower_windows.union(window)
    rear_wall = rear_wall.cut(capture_cutter).cut(lower_windows)
    result = result.union(rear_wall)

    for center in (0.0, 180.0):
        side_rail = _sector_prism(
            body_radius,
            wall,
            wall_z0,
            wall_z1,
            center,
            9.0,
        )
        result = result.union(side_rail)

    entry_lower_top = bolt_axis_height - bolt_slot_half + 0.10
    entry_upper_bottom = bolt_axis_height + bolt_slot_half - 0.10
    for center in (52.0, 128.0):
        lower_shoulder = _sector_prism(
            body_radius,
            wall,
            wall_z0,
            entry_lower_top,
            center,
            10.0,
        )
        upper_shoulder = _sector_prism(
            body_radius,
            wall,
            entry_upper_bottom,
            wall_z1,
            center,
            10.0,
        )
        result = result.union(lower_shoulder).union(upper_shoulder)

    # Straight webs, a rear cross-ring, and flared face roots reproduce the
    # strong die-cast bracing visible through the manufacturer's windows.
    rib_inner = hub_radius * 0.88
    lower_rib_top = max(lower_window_top + 0.18, lower_cam_z)
    for angle in (28.0, 152.0):
        rib = _radial_rib(
            rib_inner,
            body_radius,
            max(0.58, wall * 0.70),
            0.05,
            lower_rib_top,
            angle,
        )
        result = result.union(rib)
        root = _gusset(
            rib_inner,
            body_radius,
            -0.02,
            min(body_diameter * 0.22, lower_rib_top * 0.72),
            max(0.70, wall * 0.88),
            angle,
        )
        result = result.union(root)

    cross_z = lower_window_top - 0.55
    cross_ring = _sector_prism(
        body_radius,
        max(0.62, wall * 0.72),
        cross_z,
        cross_z + max(0.42, wall * 0.42),
        270.0,
        112.0,
    )
    result = result.union(cross_ring)

    guide_z = bolt_axis_height - bolt_slot_half - 0.08
    guide_ring = _sector_prism(
        body_radius,
        max(0.72, wall * 0.72),
        guide_z,
        guide_z + 0.46,
        270.0,
        112.0,
    )
    result = result.union(guide_ring)

    # The OEM's dominant asymmetric member is a 1.10 mm chord web, not a
    # third radial spoke.  Its large upper window leaves two unequal rails.
    main_web_thickness = body_diameter * (1.10 / 15.0)
    web_y = -main_web_thickness / 2.0
    # Size the chord at its outer face rather than its mid-plane so the web's
    # corner stays inside the measured casting diameter.
    web_outer_y = abs(web_y) + main_web_thickness / 2.0
    web_half_width = math.sqrt(body_radius * body_radius - web_outer_y * web_outer_y)
    web_z0 = 0.08
    web_z1 = cap_z + overlap
    main_web = (
        cq.Workplane("XZ")
        .center(0.0, (web_z0 + web_z1) / 2.0)
        .rect(web_half_width * 2.0, web_z1 - web_z0)
        .extrude(main_web_thickness / 2.0, both=True)
        .translate((0.0, web_y, 0.0))
    )
    window_left = body_diameter * (-3.17 / 15.0)
    window_right = body_diameter * (4.15 / 15.0)
    web_window_z0 = lower_cam_z
    web_window_z1 = cap_z + 0.02
    web_window = (
        cq.Workplane("XZ")
        .center(
            (window_left + window_right) / 2.0,
            (web_window_z0 + web_window_z1) / 2.0,
        )
        .rect(
            window_right - window_left,
            web_window_z1 - web_window_z0,
        )
        .extrude(body_diameter, both=True)
    )
    main_web = main_web.cut(web_window).cut(capture_cutter)
    result = result.union(main_web)

    # The OEM operating face has two prominent recessed direction arrows.
    groove_width = body_diameter * (0.52 / 15.0)
    groove_outer = min(
        face_radius - body_diameter * 0.72 / 15.0,
        body_diameter * (6.40 / 15.0),
    )
    groove_depth = min(0.24, face_thickness * 0.38)
    groove_z = -face_thickness - 0.02
    arrow_a = _arrow_cutter(groove_outer, groove_width, groove_z, groove_depth, 78.0, 55.0)
    arrow_b = _arrow_cutter(groove_outer, groove_width, groove_z, groove_depth, 258.0, 55.0)
    result = result.cut(arrow_a.union(arrow_b))

    # One measured combination recess accepts PZ2, a flat blade, and SW4.
    drive_z = -face_thickness - 0.03
    drive = _combined_drive_cutter(body_diameter, drive_z)
    result = result.cut(drive)
    return result
