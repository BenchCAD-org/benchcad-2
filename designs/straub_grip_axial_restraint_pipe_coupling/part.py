"""STRAUB-GRIP-L two-bolt axial-restraint pipe coupling.

The four catalog rows modelled here are the fixed two-lock-bolt construction.
Dimensions B, C, DV, R and the pipe O.D. range come from Dixon DPL424 p. 965.
The separate casing, bars, anchoring rings and sealing sleeve follow Straub's
published section drawing; locally un-dimensioned thicknesses are proportions.
"""

import math

import cadquery as cq


def _tube_x(length, outer_r, inner_r, x0=0.0):
    """Annular solid whose flow axis is X."""
    return cq.Workplane("YZ").workplane(offset=x0).circle(outer_r).circle(inner_r).extrude(length)


def _split_tube_x(length, outer_r, inner_r, slot_w, slot_h, x0=0.0):
    """A rolled, slotted sleeve. The top slot is the lock-bar opening."""
    sleeve = _tube_x(length, outer_r, inner_r, x0)
    # Overcut slightly beyond the outside radius to prevent a tolerance sliver
    # from becoming a second solid at the opening.
    slot = (cq.Workplane("XY").box(length + 1.0, slot_w, slot_h + 2.0)
            .translate((x0 + length / 2.0, 0.0, outer_r - slot_h / 2.0 + 1.0)))
    return sleeve.cut(slot)


def _annular_sector_x(length, outer_r, inner_r, start_deg, end_deg, x0=0.0):
    """Annular sector extruded along X; angles are in the YZ cross-section."""
    def point(radius, degrees):
        angle = math.radians(degrees)
        return (radius * math.cos(angle), radius * math.sin(angle))

    # Three true circular arcs avoid the faceted polygon-band appearance.
    cuts = [start_deg + (end_deg - start_deg) * i / 3.0 for i in range(4)]
    path = cq.Workplane("YZ").workplane(offset=x0).moveTo(*point(outer_r, cuts[0]))
    for a, b in zip(cuts, cuts[1:]):
        path = path.threePointArc(point(outer_r, 0.5 * (a + b)), point(outer_r, b))
    path = path.lineTo(*point(inner_r, cuts[-1]))
    for a, b in zip(reversed(cuts[1:]), reversed(cuts[:-1])):
        path = path.threePointArc(point(inner_r, 0.5 * (a + b)), point(inner_r, b))
    return path.close().extrude(length)


def _outer_wrap_casing(length, outer_r, inner_r, x0=0.0):
    """Rolled outer casing with the continuous circular end profile.

    The published end view is a thin circular casing surrounding the seal,
    with two raised closure ears tangent to the ring.  The ears are added by
    _add_casing_latch_housings; they must not be replaced by a solid crown.
    """
    return _tube_x(length, outer_r, inner_r, x0).val()


def _anchoring_ring_x(x0, width, outer_r, root_r, tooth_d, tooth_w, teeth):
    """One annular grip ring with a fine, continuous serrated inner edge.

    The source photographs and section drawing show many closely spaced grip
    marks around the bore.  Build that edge as one serrated aperture instead
    of fusing a few large rectangular lugs onto a smooth annulus.
    """
    outer = (cq.Workplane("YZ").workplane(offset=x0)
             .circle(outer_r).extrude(width).val())
    points = []
    for i in range(2 * teeth):
        angle = math.pi * i / teeth
        radius = root_r if i % 2 == 0 else root_r - tooth_d
        points.append((radius * math.cos(angle), radius * math.sin(angle)))
    serrated_bore = (cq.Workplane("YZ").workplane(offset=x0)
                     .polyline(points).close().extrude(width).val())
    _ = tooth_w  # Retained as the catalog-proportion hint for this detail.
    return outer.cut(serrated_bore)


def _add_rolled_end_lips(casing, length, outer_r, inner_r, slot_w):
    """Add the casing's two shallow rolled sheet edges as one casing body."""
    lip_w = max(0.9, 0.015 * length)
    wall = outer_r - inner_r
    lip_outer = outer_r + 0.32 * wall
    lip_inner = inner_r - 0.16 * wall
    shaped = casing.val()
    for x0 in (0.0, length - lip_w):
        lip = _split_tube_x(lip_w, lip_outer, lip_inner, slot_w, 1.35 * lip_w, x0)
        shaped = shaped.fuse(lip.val())
    return shaped


def _cylinder_y(xc, y0, zc, radius, length):
    """Cylinder with its axis along +Y, beginning at y0."""
    return (cq.Workplane("XY").circle(radius).extrude(length)
            .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), -90.0)
            .translate((xc, y0, zc)).val())


def _d_section_bar_x(x0, length, radius, wall, center_y, center_z, angle_deg):
    """Hollow D-section bar along X, mirrored/tilted as in the end view."""
    outer = (cq.Workplane("YZ")
             .moveTo(-radius, 0.0)
             .threePointArc((0.0, radius), (radius, 0.0))
             .lineTo(-radius, 0.0)
             .close().extrude(length).val())
    inner_r = radius - wall
    inner = (cq.Workplane("YZ")
             .moveTo(-inner_r, wall)
             .threePointArc((0.0, wall + inner_r), (inner_r, wall))
             .lineTo(-inner_r, wall)
             .close().extrude(length).val())
    bar = outer.cut(inner)
    return (bar.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), angle_deg)
            .translate((x0, center_y, center_z)))


def _d_section_outer_wrap_x(x0, length, inner_radius, sheet,
                            center_y, center_z, angle_deg):
    """Curved casing sheet rolled around the outside of one D-section bar."""
    outer_r = inner_radius + sheet
    outer = (cq.Workplane("YZ")
             .moveTo(-outer_r, 0.0)
             .threePointArc((0.0, outer_r), (outer_r, 0.0))
             .lineTo(-outer_r, 0.0)
             .close().extrude(length).val())
    inner = (cq.Workplane("YZ")
             .moveTo(-inner_radius, 0.0)
             .threePointArc((0.0, inner_radius), (inner_radius, 0.0))
             .lineTo(-inner_radius, 0.0)
             .close().extrude(length).val())
    wrap = outer.cut(inner)
    return (wrap.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), angle_deg)
            .translate((x0, center_y, center_z)))


def _add_tangent_return_strips(casing, x0, length, casing_outer,
                               d_bar_radius, d_bar_centers, d_bar_center_z,
                               d_bar_angles):
    """Fuse two thin casing strips returning from the two D-bars to the ring.

    Each strip starts at the outer tangent of one D-section bar and slopes
    back to the circular rolled casing.  This makes the two distinct raised
    D-bars in the supplied end-view reference, not one central cap.
    """
    shaped = casing
    sheet = max(0.8, 0.055 * casing_outer)
    wrap_radius = d_bar_radius + sheet
    for center_y, angle_deg in zip(d_bar_centers, d_bar_angles):
        sign = -1.0 if center_y < 0.0 else 1.0
        # P and T are the contact points of the common external tangent between
        # the rolled D-edge and the circular casing.  This fixes the direction
        # from the published end view instead of choosing a visual slope.
        cy_abs = abs(center_y)
        cz = d_bar_center_z
        distance_sq = cy_abs * cy_abs + cz * cz
        radius_sq = casing_outer * casing_outer
        distance = math.sqrt(distance_sq)
        normal_delta = (casing_outer - wrap_radius) / distance
        normal_delta = max(-1.0, min(1.0, normal_delta))
        centre_angle = math.atan2(cz, cy_abs)
        normal_angle = centre_angle - math.acos(normal_delta)
        ny_abs = math.cos(normal_angle)
        nz = math.sin(normal_angle)
        ty_abs = casing_outer * ny_abs
        tz = casing_outer * nz
        py_abs = cy_abs + wrap_radius * ny_abs
        pz = cz + wrap_radius * nz
        py = sign * py_abs
        ty = sign * ty_abs
        # Offset the inner edge towards the centre of the circular casing.
        # Slightly exceed one sheet thickness so the tangent run has a small
        # volumetric overlap with both rolled sheets; exact face-only contact
        # is numerically classified as a compound by OCC.
        inward_y = -ty / casing_outer * (1.15 * sheet)
        inward_z = -tz / casing_outer * (1.15 * sheet)
        strip = (cq.Workplane("YZ").workplane(offset=x0)
                 .moveTo(py, pz)
                 .lineTo(ty, tz)
                 .lineTo(ty + inward_y, tz + inward_z)
                 .lineTo(py + inward_y, pz + inward_z)
                 .close().extrude(length))
        shaped = shaped.fuse(strip.val())
        rolled_edge = _d_section_outer_wrap_x(
            x0, length, d_bar_radius, sheet,
            center_y, d_bar_center_z, angle_deg
        )
        shaped = shaped.fuse(rolled_edge)
    return shaped


def _add_outer_closure_cover(casing, length, slot_w, stations, bar_y, bar_z,
                             casing_outer, shank_r):
    """Fuse the casing's long overlap cover over the rolled-shell opening.

    The published side drawing shows the clasp mechanism enclosed by a formed
    longitudinal cover, rather than exposing a bare slot between two isolated
    bars.  Its ends and sheet thickness are proportional formed-sheet details.
    """
    cover_h = 0.52 * bar_z
    # Narrower than the C-shell opening: the two longitudinal side windows
    # deliberately expose the sleeve and anchoring-ring structure below.
    cover = (cq.Workplane("XY").box(length - 1.2, max(0.58 * slot_w, 0.85 * bar_y), cover_h)
             .translate((0.5 * length, 0.0, casing_outer + 0.31 * cover_h)))
    shaped = casing.fuse(cover.val())
    for xc in stations:
        through = (cq.Workplane("XY").workplane(offset=casing_outer - 1.0)
                   .circle(1.12 * shank_r).extrude(cover_h + 3.0)
                   .translate((xc, 0.0, 0.0)))
        shaped = shaped.cut(through.val())
    return shaped


def _transverse_lock_bolt(xc, zc, span, shank_r, head_r):
    """Socket-head bolt along Y, passing through both D-section bars."""
    shank = _cylinder_y(xc, -0.5 * span, zc, shank_r, span)
    head_h = 0.62 * head_r
    head = _cylinder_y(xc, 0.5 * span, zc, head_r, head_h)
    bolt = shank.fuse(head)
    socket = (cq.Workplane("XY").polygon(6, 1.05 * shank_r)
              .extrude(head_h + 0.2)
              .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), -90.0)
              .translate((xc, 0.5 * span - 0.1, zc)).val())
    return bolt.cut(socket)


def build(catalog_index, fitted_pipe_od):
    """Build one exact Dixon row for a pipe O.D. in that row's stated range."""
    idx = int(catalog_index)
    if idx == 0:       # STR20650, 3 inch
        pipe_od, pipe_lo, pipe_hi, b, c, dv, gap_r = 88.90, 87.884, 89.916, 99.06, 38.10, 111.76, 5.08
    elif idx == 1:     # STR20900, 4 inch
        pipe_od, pipe_lo, pipe_hi, b, c, dv, gap_r = 114.30, 113.284, 115.316, 99.06, 38.10, 139.70, 10.16
    elif idx == 2:     # STR21350, 6 inch
        pipe_od, pipe_lo, pipe_hi, b, c, dv, gap_r = 168.402, 166.624, 169.926, 114.30, 53.34, 193.04, 10.16
    elif idx == 3:     # STR21400, 8 inch
        pipe_od, pipe_lo, pipe_hi, b, c, dv, gap_r = 219.202, 216.916, 221.234, 142.24, 78.74, 248.92, 10.16
    else:
        raise ValueError("catalog_index must be 0, 1, 2, or 3")

    if not pipe_lo <= fitted_pipe_od <= pipe_hi:
        raise ValueError("fitted_pipe_od must remain inside the selected catalog row range")

    # The casing outside dimensions remain catalog dimensions.  The resilient
    # seal and anchoring-ring bore follow the actual pipe O.D. within the
    # source-published coupling range; connected pipe geometry is not modeled.
    sleeve_inner = fitted_pipe_od / 2.0
    # The EPDM sleeve and anchoring rings form the smaller inner circular
    # package.  Their locally unlisted radial thickness is proportional.
    sleeve_outer = pipe_od / 2.0 + max(3.0, 0.025 * pipe_od)
    # DV is the published *outside* diameter of the rolled casing.  Keeping
    # this shell at DV/2 is essential: it is visibly an outer wrap around the
    # smaller sleeve/ring package rather than the same cylinder with latches.
    casing_outer = 0.5 * dv
    casing_inner = sleeve_outer + max(1.2, 0.020 * pipe_od)
    if casing_inner >= casing_outer:
        raise ValueError("published DV leaves no physical outer-casing wall")
    slot_w = max(12.0, 0.34 * dv)
    slot_h = max(5.0, 0.13 * dv)

    # 1. Rolled stainless casing: lower wrap with a non-cylindrical cover.
    casing = _outer_wrap_casing(b, casing_outer, casing_inner)

    # 2. EPDM sealing sleeve: separate and continuous around the through-bore.
    sleeve = _split_tube_x(b - 1.2, sleeve_outer, sleeve_inner, 0.58 * slot_w, 0.68 * slot_h, 0.6)

    # 3-4. Two AISI 301 anchoring rings at the published pipe-end regions.
    ring_w = max(5.0, 0.11 * b)
    ring_outer = sleeve_outer - max(0.5, 0.006 * pipe_od)
    ring_ligament = max(0.6, 0.006 * pipe_od)
    ring_root = min(
        sleeve_inner + max(1.1, 0.018 * pipe_od),
        ring_outer - ring_ligament,
    )
    # The section drawing shows a close-pitched retaining-tooth band, not a
    # few coarse lugs.  Tooth pitch and tip profile remain proportional.
    # Let only a shallow tooth tip project past the EPDM bore so the fine grip
    # marks remain visible from the coupling end without moving either ring.
    grip_overbite = max(0.35, 0.003 * pipe_od)
    tooth_d = (ring_root - sleeve_inner) + grip_overbite
    tooth_w = max(0.55, 0.006 * pipe_od)
    teeth = 64 if pipe_od < 140.0 else 80
    ring_left = _anchoring_ring_x(1.3, ring_w, ring_outer, ring_root, tooth_d, tooth_w, teeth)
    ring_right = _anchoring_ring_x(b - ring_w - 1.3, ring_w, ring_outer, ring_root, tooth_d, tooth_w, teeth)

    # 5-6. Two hollow D-section closure bars run parallel to the pipe axis.
    # Their curved faces point outward and their flat faces inward.  Two
    # transverse bolts pass through both bars at separate axial stations.
    d_bar_r = max(3.2, 0.145 * casing_outer)
    d_bar_wall = max(0.9, 0.24 * d_bar_r)
    d_bar_len = 0.94 * b
    d_bar_x0 = 0.03 * b
    # Raise the rolled D edges far enough above the circular shell for the
    # bolt-clearance opening to remain visible both above and below the bolt
    # without cutting into the main cylindrical wall.
    d_bar_center_z = 1.15 * casing_outer
    d_bar_offset_y = 0.38 * casing_outer
    d_bar_centers = (-d_bar_offset_y, d_bar_offset_y)
    # The straight diameter of each D section is nearly radial towards the
    # coupling centre, with only a small mirrored cant visible in the end
    # drawing.  The previous +/-58 degree orientation was far too oblique.
    d_bar_angles = (105.0, -105.0)
    shank_r = max(3.0, 0.032 * pipe_od)
    head_r = 1.52 * shank_r
    casing = _add_tangent_return_strips(
        casing, d_bar_x0, d_bar_len, casing_outer, d_bar_r, d_bar_centers,
        d_bar_center_z, d_bar_angles
    )
    d_bar_left = _d_section_bar_x(
        d_bar_x0, d_bar_len, d_bar_r, d_bar_wall,
        d_bar_centers[0], d_bar_center_z, d_bar_angles[0]
    )
    d_bar_right = _d_section_bar_x(
        d_bar_x0, d_bar_len, d_bar_r, d_bar_wall,
        d_bar_centers[1], d_bar_center_z, d_bar_angles[1]
    )
    bolt_span = 1.22 * casing_outer
    bolt_xs = (0.36 * b, 0.64 * b)
    bore_r = 1.12 * shank_r
    # Relief cuts belong only to the raised closure sheet.  Clipping them
    # above the circular casing prevents the large-size variants from gaining
    # unintended through-holes in the main cylindrical wall.
    clip_bottom = 1.006 * casing_outer
    clip_height = 1.20 * casing_outer
    top_relief_clip = (cq.Workplane("XY")
                       .box(1.30 * b, 3.0 * casing_outer, clip_height)
                       .translate((0.50 * b, 0.0,
                                   clip_bottom + 0.50 * clip_height)).val())
    for bolt_x in bolt_xs:
        bore = _cylinder_y(
            bolt_x, -0.62 * casing_outer, d_bar_center_z,
            bore_r, 1.24 * casing_outer
        )
        d_bar_left = d_bar_left.cut(bore)
        d_bar_right = d_bar_right.cut(bore)
        casing = casing.cut(bore.intersect(top_relief_clip))
        # Above and below the bolt the casing sheet is almost completely open;
        # two overlapping rounded cuts form a vertical slot, leaving material
        # only at the axial left/right sides of the fastener station.
        for z_offset in (-0.68 * head_r, 0.68 * head_r):
            relief = _cylinder_y(
                bolt_x, -0.66 * casing_outer,
                d_bar_center_z + z_offset,
                0.84 * head_r, 1.32 * casing_outer
            )
            casing = casing.cut(relief.intersect(top_relief_clip))
        # At the bolt section the casing does not close over the top of either
        # D bar.  Remove a rotated crown window while retaining the two narrow
        # side connections; material remains before, between and after the two
        # bolt stations, so the rolled casing is still one continuous body.
        for center_y, angle_deg in zip(d_bar_centers, d_bar_angles):
            crown_window = (cq.Workplane("XY")
                            .box(2.30 * head_r, 1.05 * d_bar_r,
                                 1.55 * d_bar_r)
                            .translate((0.0, 0.0, 0.72 * d_bar_r))
                            .rotate((0.0, 0.0, 0.0),
                                    (1.0, 0.0, 0.0), angle_deg)
                            .translate((bolt_x, center_y,
                                        d_bar_center_z)).val())
            casing = casing.cut(crown_window.intersect(top_relief_clip))
        # The reference has no casing sheet above the bolt at either bolt
        # station.  Remove the entire upper strip across both D bars while
        # leaving the separate D bars and bolt solids untouched.
        upper_clear_height = 0.85 * casing_outer
        upper_clear = (cq.Workplane("XY")
                       .box(2.30 * head_r, 1.70 * casing_outer,
                            upper_clear_height)
                       .translate((bolt_x, 0.0,
                                   d_bar_center_z
                                   + 0.50 * upper_clear_height)).val())
        casing = casing.cut(upper_clear)

    # The supplied product/reference side view shows one horizontal row of six
    # small perforations in the visible overlap sheet below the lock bolts.
    # Their exact diameter and stations are not dimensioned, so both remain an
    # honest proportion detail.  Cut only the near (+Y) casing wall: a cutter
    # through the full coupling would incorrectly perforate the opposite wall,
    # EPDM sleeve and anchoring rings as well.
    side_hole_r = max(1.15, 0.014 * pipe_od)
    # Place the row in the broad side-sheet region shown by the reviewer, well
    # below the two lock bolts.  A higher row falls onto the sloping closure
    # cover and reads only as tiny grazing marks in a true side view.
    side_hole_z = 0.30 * casing_outer
    side_surface_y = math.sqrt(
        max(0.0, casing_outer * casing_outer - side_hole_z * side_hole_z)
    )
    casing_wall = casing_outer - casing_inner
    side_hole_y0 = side_surface_y - casing_wall - 1.2
    side_hole_depth = casing_wall + 2.4
    for hole_i in range(6):
        hole_x = b * (0.22 + 0.56 * hole_i / 5.0)
        side_hole = _cylinder_y(
            hole_x, side_hole_y0, side_hole_z,
            side_hole_r, side_hole_depth,
        )
        casing = casing.cut(side_hole)

    bolt_left = _transverse_lock_bolt(
        bolt_xs[0], d_bar_center_z, bolt_span, shank_r, head_r
    )
    bolt_right = _transverse_lock_bolt(
        bolt_xs[1], d_bar_center_z, bolt_span, shank_r, head_r
    )

    # The source's R value is a pipe-end installation clearance; it is retained
    # in the catalog mapping but no pipe is part of this coupling model.
    _ = (pipe_od, pipe_hi, c, gap_r)
    result = cq.Compound.makeCompound([
        casing, sleeve.val(), ring_left, ring_right,
        d_bar_left, d_bar_right, bolt_left, bolt_right,
    ])
    return result
