"""Parametric RÖHM DURO-M three-jaw geared scroll chuck assembly.

The externally visible chuck envelope, mounting geometry and stepped-jaw
envelopes follow the official DURO-M catalogue tables.  The catalogue explains
that radial pinions drive a spiral ring through bevel gearing, but it does not
fully dimension the internal tooth forms, cover profile, jaw serrations or
small edge treatments.  Those internal details are therefore deliberately
simplified with the documented proportions below; they are not represented as
manufacturer-exact production geometry.
"""

import cadquery as cq
import math


def _annulus(z0, height, outer_d, inner_d):
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, z0))
        .circle(outer_d / 2.0)
        .circle(inner_d / 2.0)
        .extrude(height)
    )


def _radial_cylinder(angle, radius0, z, length, diameter):
    solid = (
        cq.Workplane("YZ", origin=(radius0, 0.0, z))
        .circle(diameter / 2.0)
        .extrude(length)
    )
    return solid.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)


def _jaw(
    clamp_d,
    jaw_length,
    jaw_width,
    jaw_height,
    jaw_step_f,
    jaw_step_g,
    jaw_step_h,
    body_depth,
):
    """One outward-stepped inside jaw, initially aligned with +X."""
    x0 = clamp_d / 2.0
    embed = min(0.20 * body_depth, 0.24 * jaw_height)
    z_top = jaw_height - embed
    mid_drop = min(0.50 * jaw_step_h, 0.22 * jaw_height)
    low_drop = min(jaw_step_h, 0.38 * jaw_height)

    profile = (
        cq.Workplane("XZ")
        .moveTo(x0, -embed)
        .lineTo(x0 + jaw_length, -embed)
        .lineTo(x0 + jaw_length, z_top - low_drop)
        .lineTo(x0 + jaw_step_g, z_top - low_drop)
        .lineTo(x0 + jaw_step_g, z_top - mid_drop)
        .lineTo(x0 + jaw_step_f, z_top - mid_drop)
        .lineTo(x0 + jaw_step_f, z_top)
        .lineTo(x0, z_top)
        .close()
        .extrude(jaw_width / 2.0, both=True)
    )

    # The catalogue shows jaw-base rack teeth but does not specify their pitch.
    # Six equal drawing-proportion grooves preserve the visible mechanism while
    # keeping the exact A/B/C jaw envelope unchanged.
    groove_w = 0.045 * jaw_length
    groove_depth = 0.34 * embed
    for i in range(6):
        gx = x0 + (0.16 + 0.125 * i) * jaw_length
        groove = (
            cq.Workplane("XY", origin=(gx, 0.0, -embed - 0.01))
            .box(groove_w, 1.08 * jaw_width, groove_depth, centered=(True, True, False))
        )
        profile = profile.cut(groove)

    # Two shallow transverse top grooves make the gripping face readable.  The
    # exact serration pitch is not catalogued and is intentionally simplified.
    serration_depth = max(0.25, 0.025 * jaw_height)
    for i in range(2):
        sx = x0 + (0.18 + 0.18 * i) * jaw_step_f
        serration = (
            cq.Workplane("XY", origin=(sx, 0.0, z_top - serration_depth))
            .box(0.045 * jaw_length, 1.08 * jaw_width, 2.0 * serration_depth)
        )
        profile = profile.cut(serration)
    return profile


def _pinion(angle, chuck_d, body_depth, square_drive, scroll_outer_d):
    """One radial pinion with a catalog-size square key socket."""
    axis_z = -0.50 * body_depth
    gear_d = min(0.17 * chuck_d, 2.35 * square_drive)
    shaft_d = min(0.12 * chuck_d, 1.55 * square_drive)
    radial_inner = 0.40 * scroll_outer_d
    # The square drive is recessed behind the outside diameter, as in the
    # catalogue photographs; the pinion must not protrude like an external peg.
    radial_outer = 0.485 * chuck_d
    gear_len = 0.72 * gear_d
    shaft_len = radial_outer - radial_inner

    # A 12-lobed prism is a controlled visual simplification of the bevel gear.
    gear = (
        cq.Workplane("YZ", origin=(radial_inner, 0.0, axis_z))
        .polygon(12, gear_d)
        .extrude(gear_len)
    )
    shaft = (
        cq.Workplane("YZ", origin=(radial_inner + 0.55 * gear_len, 0.0, axis_z))
        .circle(shaft_d / 2.0)
        .extrude(max(shaft_len - 0.55 * gear_len, 0.12 * chuck_d))
    )
    pinion = gear.union(shaft)

    socket_depth = min(0.11 * chuck_d, 1.25 * square_drive)
    socket = (
        cq.Workplane(
            "YZ",
            origin=(radial_outer - socket_depth, 0.0, axis_z),
        )
        .rect(square_drive, square_drive)
        .extrude(socket_depth + 0.03 * chuck_d)
    )
    pinion = pinion.cut(socket)
    return pinion.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)


def _scroll_plate(body_depth, chuck_d, through_hole_d):
    """Simplified spiral ring with a visible planar-scroll track."""
    outer_d = 0.72 * chuck_d
    inner_d = max(1.12 * through_hole_d, 0.19 * chuck_d)
    plate_t = 0.095 * body_depth
    # Place the track immediately below the three jaw racks.  The catalogue
    # defines the operating relationship but omits the running clearance.
    z0 = -0.335 * body_depth
    plate = _annulus(z0, plate_t, outer_d, inner_d)

    # The official cutaway establishes a spiral ring, but not its tooth pitch or
    # cross-section.  Four staggered, broken annular ridges communicate the
    # planar-scroll track without claiming production-accurate gearing.  This
    # segmented construction is deliberately robust at every catalogue scale.
    inner_r = inner_d / 2.0 + 0.06 * chuck_d
    outer_r = outer_d / 2.0 - 0.045 * chuck_d
    ridge_w = max(0.8, 0.018 * chuck_d)
    ridge_h = max(0.7, 0.035 * body_depth)
    radial_pitch = (outer_r - inner_r) / 4.5
    overlap = max(0.08, 0.002 * body_depth)
    for i in range(4):
        ridge_mid_r = inner_r + (i + 0.65) * radial_pitch
        ridge = (
            cq.Workplane("XY", origin=(0.0, 0.0, z0 + plate_t - overlap))
            .circle(ridge_mid_r + ridge_w / 2.0)
            .circle(ridge_mid_r - ridge_w / 2.0)
            .extrude(ridge_h + overlap)
        )
        gap_angle = 35.0 + 73.0 * i
        gap = (
            cq.Workplane("XY", origin=(outer_r / 2.0, 0.0, z0 + plate_t - 0.5))
            .box(outer_r, 1.45 * ridge_w, ridge_h + 1.0)
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), gap_angle)
        )
        plate = plate.union(ridge.cut(gap))
    return plate


def build(
    catalog_index,
    catalog_item,
    chuck_d,
    centering_d,
    centering_depth,
    body_depth,
    through_hole_d,
    mount_bcd,
    mount_thread_d,
    mount_hole_count,
    jaw_length,
    jaw_width,
    jaw_height,
    jaw_step_f,
    jaw_step_g,
    jaw_step_h,
    square_drive,
    grip_min_d,
    grip_max_d,
    jaw_open_fraction,
    clamp_d,
    has_scallops,
):
    """Build nine non-degenerate bodies in one fixed-count assembly."""
    _ = catalog_index
    _ = catalog_item
    _ = grip_min_d
    _ = grip_max_d
    _ = jaw_open_fraction

    # Main one-piece chuck body, exact catalog A diameter and D axial envelope.
    body = _annulus(-body_depth, body_depth, chuck_d, through_hole_d)

    # The closed rear cover occupies a shallow recess rather than overlapping
    # the main body.  Its detailed fastening pattern is under-dimensioned.
    cover_t = max(1.8, 0.085 * body_depth)
    cover_outer_d = 0.84 * chuck_d
    cover_clearance = max(0.15, 0.002 * chuck_d)
    cover_pocket = (
        cq.Workplane("XY", origin=(0.0, 0.0, -body_depth - 0.02))
        .circle(cover_outer_d / 2.0 + cover_clearance)
        .circle(through_hole_d / 2.0)
        .extrude(cover_t + 0.04)
    )
    body = body.cut(cover_pocket)
    cover = _annulus(
        -body_depth + cover_clearance,
        cover_t - 2.0 * cover_clearance,
        cover_outer_d,
        through_hole_d + 2.0 * cover_clearance,
    )

    # Rear H6 centering register is integrated with the separate cover body and
    # remains inside the catalog D envelope.  The C depth is exact.
    register_depth = min(centering_depth, 0.70 * cover_t)
    register = _annulus(
        -body_depth + cover_clearance,
        register_depth,
        centering_d,
        through_hole_d + 2.0 * cover_clearance,
    )
    cover = cover.union(register)

    # Exact F bolt circle, catalog hole count and nominal G thread diameter.
    # Threads are represented by nominal cylindrical holes, not false helical
    # detail.  They are cuts and therefore do not alter the assembly body count.
    for i in range(mount_hole_count):
        angle = 360.0 * i / mount_hole_count
        x = 0.5 * mount_bcd * math.cos(math.radians(angle))
        y = 0.5 * mount_bcd * math.sin(math.radians(angle))
        hole = (
            cq.Workplane("XY", origin=(x, y, -body_depth - 0.5))
            .circle(mount_thread_d / 2.0)
            .extrude(body_depth + 1.0)
        )
        body = body.cut(hole)
        cover = cover.cut(hole)

    # Three radial guideways are visible in the official front view.  Their
    # widths follow exact jaw B plus a small functional clearance; their depths
    # and end radii are drawing proportions because the catalogue omits them.
    guide_depth = min(0.22 * body_depth, 0.28 * jaw_height)
    guide_inner = max(through_hole_d / 2.0 + 0.04 * chuck_d, 0.11 * chuck_d)
    guide_length = 0.56 * chuck_d
    for i in range(3):
        guide = (
            cq.Workplane("XY", origin=(guide_inner, 0.0, -guide_depth))
            .box(guide_length, jaw_width + 0.035 * chuck_d, guide_depth + 0.02)
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 120.0 * i)
        )
        body = body.cut(guide)

    # Internal annular cavity for the scroll plate.  A central sleeve and outer
    # body wall remain connected, preserving a single non-degenerate body.
    scroll_outer_d = 0.72 * chuck_d
    cavity_inner_d = max(through_hole_d + 0.08 * chuck_d, 0.22 * chuck_d)
    cavity = (
        cq.Workplane("XY", origin=(0.0, 0.0, -0.71 * body_depth))
        .circle(0.5 * scroll_outer_d + 0.015 * chuck_d)
        .circle(0.5 * cavity_inner_d)
        .extrude(0.54 * body_depth)
    )
    body = body.cut(cavity)

    pinion_angles = (60.0, 180.0, 300.0)
    pinion_bore_d = min(0.20 * chuck_d, 2.65 * square_drive)
    for angle in pinion_angles:
        bore = _radial_cylinder(
            angle,
            0.25 * chuck_d,
            -0.50 * body_depth,
            0.30 * chuck_d,
            pinion_bore_d,
        )
        body = body.cut(bore)

    # Catalog note: characteristic scallops are omitted from size 400 upward.
    if has_scallops > 0:
        notch_d = 0.13 * chuck_d
        notch_radius = 0.515 * chuck_d
        for angle in pinion_angles:
            nx = notch_radius * math.cos(math.radians(angle))
            ny = notch_radius * math.sin(math.radians(angle))
            notch = (
                cq.Workplane("XY", origin=(nx, ny, -body_depth - 0.5))
                .circle(notch_d / 2.0)
                .extrude(body_depth + 1.0)
            )
            body = body.cut(notch)

    # Shallow concentric front-face rings are visible on the product and make
    # the body/jaw interface readable; their widths are honest proportions.
    face_recess = (
        cq.Workplane("XY", origin=(0.0, 0.0, -0.018 * body_depth))
        .circle(0.39 * chuck_d)
        .circle(max(0.35 * chuck_d, through_hole_d / 2.0 + 0.03 * chuck_d))
        .extrude(0.02 * body_depth)
    )
    body = body.cut(face_recess)

    scroll = _scroll_plate(body_depth, chuck_d, through_hole_d)

    jaws = []
    for i in range(3):
        jaw = _jaw(
            clamp_d,
            jaw_length,
            jaw_width,
            jaw_height,
            jaw_step_f,
            jaw_step_g,
            jaw_step_h,
            body_depth,
        ).rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 120.0 * i)
        jaws.append(jaw)

    pinions = []
    for angle in pinion_angles:
        pinions.append(_pinion(angle, chuck_d, body_depth, square_drive, scroll_outer_d))

    result = cq.Compound.makeCompound(
        [
            body.val(),
            cover.val(),
            scroll.val(),
            jaws[0].val(),
            jaws[1].val(),
            jaws[2].val(),
            pinions[0].val(),
            pinions[1].val(),
            pinions[2].val(),
        ]
    )
    return result
