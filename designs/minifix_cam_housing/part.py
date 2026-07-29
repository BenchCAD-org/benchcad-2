"""Parametric reconstruction of the Häfele Minifix 15 eccentric cam housing.

The construction deliberately follows the OEM's visible feature hierarchy:
operating disc, eccentric capture cam, two open C-plates, and asymmetric
support legs.  It does not reuse the earlier whole-body section loft.
"""

import math

import cadquery as cq


def _annular_sector(outer_radius, inner_radius, z0, z1, center, half_angle):
    """Return one open, circular casting sector between two Z stations."""

    def wire(z):
        outer = cq.Edge.makeCircle(
            outer_radius,
            (0.0, 0.0, z),
            (0.0, 0.0, 1.0),
            center - half_angle,
            center + half_angle,
            True,
        )
        inner = cq.Edge.makeCircle(
            inner_radius,
            (0.0, 0.0, z),
            (0.0, 0.0, 1.0),
            center - half_angle,
            center + half_angle,
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

    return cq.Solid.makeLoft([wire(z0), wire(z1)], ruled=True)


def _c_plate(radius, thickness, z0, mouth_center, mouth_width):
    """Cut a broad radial mouth from a round terminal casting plate."""
    plate = cq.Workplane("XY").workplane(offset=z0).circle(radius).extrude(thickness)
    plate = plate.edges("%CIRCLE").fillet(min(0.22, thickness * 0.30))
    cutter = (
        cq.Workplane("XY")
        .workplane(offset=z0 - 0.08)
        .center(mouth_center, 0.0)
        .rect(mouth_width, radius * 1.36)
        .extrude(thickness + 0.16)
    )
    return plate.cut(cutter)


def _drive_cutter(scale, z0):
    """Make the measured PZ/flat/hex combination drive recess."""
    horizontal = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .rect(6.80 * scale, 1.62 * scale)
        .extrude(2.15 * scale)
    )
    vertical = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .rect(1.62 * scale, 6.80 * scale)
        .extrude(2.15 * scale)
    )
    pz = horizontal.union(vertical)
    hex_radius = 2.32 * scale
    hex_points = [
        (
            hex_radius * math.cos(math.radians(30.0 + 60.0 * index)),
            hex_radius * math.sin(math.radians(30.0 + 60.0 * index)),
        )
        for index in range(6)
    ]
    socket = (
        cq.Workplane("XY")
        .workplane(offset=z0 + 1.85 * scale)
        .polyline(hex_points)
        .close()
        .extrude(1.85 * scale)
    )
    return pz.union(socket)


def _arrow_cutter(radius, width, z0, depth, center):
    """Make a curved recessed operating-direction arrow."""
    half_angle = 47.0
    band = _annular_sector(radius, radius - width, z0, z0 + depth, center, half_angle)
    angle = math.radians(center + half_angle)
    radial = (math.cos(angle), math.sin(angle))
    tangent = (-radial[1], radial[0])
    middle = radius - width / 2.0
    x, y = middle * radial[0], middle * radial[1]
    head = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .polyline(
            [
                (x + radial[0] * width, y + radial[1] * width),
                (x - radial[0] * width, y - radial[1] * width),
                (x + tangent[0] * width * 2.0, y + tangent[1] * width * 2.0),
            ]
        )
        .close()
        .extrude(depth)
    )
    return band.fuse(head.val())


def _support_leg(x, y, width, depth, height, z0):
    """Return a rounded vertical die-cast support that joins both plates."""
    leg = cq.Workplane("XY").workplane(offset=z0).center(x, y).rect(width, depth).extrude(height)
    try:
        return leg.edges("|Z").fillet(min(width, depth) * 0.16)
    except ValueError:
        return leg


def build(
    body_diameter,
    housing_height,
    has_rim,
    rim_diameter,
    rim_height,
    bolt_axis_height,
    bolt_hole_diameter,
):
    """Build the Minifix casting around the catalogue bore, A, and X data."""
    scale = body_diameter / 15.0
    body_radius = (body_diameter - 0.10) / 2.0
    body_depth = housing_height - 0.65
    face_radius = (rim_diameter - 0.20) / 2.0 if has_rim else body_radius
    face_thickness = 0.80 * rim_height if has_rim else 0.48 * scale
    lower_plate_thickness = 0.74 * scale
    lower_plate_z = body_depth - lower_plate_thickness
    mid_plate_z = max(3.05 * scale, bolt_axis_height - 0.85 * scale)

    # Operating disc: the OEM rim is a shallow, broad circular casting above
    # the installation plane; the recesses are cut before final orientation.
    face = (
        cq.Workplane("XY")
        .workplane(offset=-face_thickness)
        .circle(face_radius)
        .extrude(face_thickness)
    )
    face = face.edges("%CIRCLE").fillet(min(0.20 * scale, face_thickness * 0.28))
    face = face.cut(_drive_cutter(scale, -face_thickness - 0.03 * scale))
    arrow_radius = min(face_radius - 0.58 * scale, 6.35 * scale)
    arrow = _arrow_cutter(arrow_radius, 0.48 * scale, -face_thickness - 0.02, 0.22 * scale, 78.0)
    face = face.cut(arrow)

    # The central member is an offset eccentric barrel.  Its round capture
    # pocket opens toward the connecting bolt instead of filling the housing.
    cam_radius = 4.42 * scale
    cam_x, cam_y = 0.42 * scale, 1.98 * scale
    cam_z0 = -0.04
    cam_z1 = min(lower_plate_z + 0.10, mid_plate_z - 2.80 * scale)
    cam = (
        cq.Workplane("XY")
        .workplane(offset=cam_z0)
        .center(cam_x, cam_y)
        .circle(cam_radius)
        .extrude(cam_z1 - cam_z0)
    )
    clearance = 1.0 + 0.18 * (bolt_hole_diameter - 7.0)
    capture = (
        cq.Workplane("XZ")
        .center(-2.10 * scale, bolt_axis_height)
        .slot2D(4.00 * scale * clearance, 3.55 * scale * clearance, 90.0)
        .extrude(body_diameter, both=True)
    )
    cam = cam.cut(capture)

    # The lower end is the defining open C-plate, not a full circular floor.
    lower_plate = _c_plate(
        body_radius,
        lower_plate_thickness,
        lower_plate_z,
        -body_radius + 4.00 * scale,
        8.10 * scale,
    )
    mid_plate = _c_plate(
        6.45 * scale,
        0.64 * scale,
        mid_plate_z,
        -6.45 * scale + 3.15 * scale,
        bolt_hole_diameter * 0.95 * scale,
    )

    # Two broad asymmetric legs and a rear curved shell reproduce the large
    # open windows visible in the OEM views, rather than a cylindrical cage.
    leg_height = body_depth + 0.04
    left_leg = _support_leg(
        -5.52 * scale, 0.30 * scale, 1.34 * scale, 2.12 * scale, leg_height, -0.04
    )
    right_leg = _support_leg(
        3.95 * scale, -1.65 * scale, 1.58 * scale, 2.04 * scale, leg_height, -0.04
    )
    rear_shell = _annular_sector(
        body_radius,
        body_radius - 1.36 * scale,
        -0.04,
        body_depth,
        180.0,
        23.0,
    )
    rear_shell = cq.Workplane("XY").newObject([rear_shell]).cut(capture)

    # Short upper ears carry the rectangular OEM windows below the operating
    # disc while keeping the large central opening visible.
    ear_height = min(3.25 * scale, lower_plate_z * 0.42)
    left_ear = _support_leg(
        -4.75 * scale, 3.80 * scale, 1.20 * scale, 1.56 * scale, ear_height, -0.04
    )
    right_ear = _support_leg(
        4.82 * scale, 3.58 * scale, 1.20 * scale, 1.56 * scale, ear_height, -0.04
    )

    result = face.union(cam).union(lower_plate).union(mid_plate)
    result = result.union(left_leg).union(right_leg).union(rear_shell)
    result = result.union(left_ear).union(right_ear)
    result = result.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 180.0)
    return result.clean()
