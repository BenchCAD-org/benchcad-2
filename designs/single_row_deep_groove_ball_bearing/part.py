"""single_row_deep_groove_ball_bearing - parametric open 6000-series bearing."""

import math

import cadquery as cq


def _annular_cylinder(outer_d, inner_d, width):
    return cq.Workplane("XY").circle(outer_d / 2.0).circle(inner_d / 2.0).extrude(width)


def _counterbore_cut(inner_d, outer_d, depth, z):
    return _annular_cylinder(outer_d, inner_d, depth).translate((0, 0, z))


def _ball_centers(pitch_d, ball_count):
    radius = pitch_d / 2.0
    return [
        (radius * math.cos(2.0 * math.pi * i / ball_count), radius * math.sin(2.0 * math.pi * i / ball_count), 0.0)
        for i in range(int(ball_count))
    ]


def _torus_tool(major_r, minor_r, z):
    return cq.Workplane("XY").add(cq.Solid.makeTorus(major_r, minor_r).translate((0, 0, z)))


def _sphere_tool(radius, center):
    return cq.Workplane("XY").sphere(radius).translate(center)


def _cage_clearance(ball_d):
    return max(0.10, min(0.20, ball_d * 0.035))


def _annular_band(outer_d, inner_d, band_w, z0):
    return _annular_cylinder(outer_d, inner_d, band_w).translate((0, 0, z0))


def _z_clip(z_min, z_max):
    height = z_max - z_min
    return cq.Workplane("XY").box(200.0, 200.0, height).translate((0, 0, z_min + height / 2.0))


def _revolved_ring(pre_pts, arc_mid, arc_end, post_pts):
    """Ring cross-section: straight walls/chamfers plus ONE true circular arc
    for the raceway groove (threePointArc through shoulder edge - groove
    bottom - shoulder edge), revolved 360 deg. A real arc, not a sampled
    polyline, so the revolved raceway is a smooth toroidal surface."""
    wp = cq.Workplane("XZ").moveTo(*pre_pts[0])
    for pt in pre_pts[1:]:
        wp = wp.lineTo(*pt)
    wp = wp.threePointArc(arc_mid, arc_end)
    for pt in post_pts:
        wp = wp.lineTo(*pt)
    return wp.close().revolve(360, (0, 0, 0), (0, 1, 0))


def _groove_half_width(width, ball_d, race_groove_depth):
    return min(width * 0.40, ball_d * (0.46 + min(race_groove_depth / ball_d, 0.24)))


def _inner_ring_revolved(bore_d, shoulder_d, width, pitch_d, ball_d, race_groove_depth):
    bore_r = bore_d / 2.0
    shoulder_r = shoulder_d / 2.0
    ball_r = ball_d / 2.0
    gap = max(0.16, min(0.20, ball_d * 0.035))
    groove_r = pitch_d / 2.0 - ball_r - gap
    groove_half_w = _groove_half_width(width, ball_d, race_groove_depth)
    chamfer = min(width * 0.035, (shoulder_r - bore_r) * 0.12, 0.28)

    return _revolved_ring(
        [
            (bore_r + chamfer, 0.0),
            (bore_r, chamfer),
            (bore_r, width - chamfer),
            (bore_r + chamfer, width),
            (shoulder_r - chamfer, width),
            (shoulder_r, width - chamfer),
            (shoulder_r, width / 2.0 + groove_half_w),
        ],
        (groove_r, width / 2.0),
        (shoulder_r, width / 2.0 - groove_half_w),
        [
            (shoulder_r, chamfer),
            (shoulder_r - chamfer, 0.0),
        ],
    )


def _outer_ring_revolved(outer_d, shoulder_d, width, pitch_d, ball_d, race_groove_depth):
    outer_r = outer_d / 2.0
    shoulder_r = shoulder_d / 2.0
    ball_r = ball_d / 2.0
    gap = max(0.16, min(0.20, ball_d * 0.035))
    groove_r = pitch_d / 2.0 + ball_r + gap
    groove_half_w = _groove_half_width(width, ball_d, race_groove_depth)
    chamfer = min(width * 0.035, (outer_r - shoulder_r) * 0.12, 0.28)

    return _revolved_ring(
        [
            (outer_r - chamfer, 0.0),
            (outer_r, chamfer),
            (outer_r, width - chamfer),
            (outer_r - chamfer, width),
            (shoulder_r + chamfer, width),
            (shoulder_r, width - chamfer),
            (shoulder_r, width / 2.0 + groove_half_w),
        ],
        (groove_r, width / 2.0),
        (shoulder_r, width / 2.0 - groove_half_w),
        [
            (shoulder_r, chamfer),
            (shoulder_r + chamfer, 0.0),
        ],
    )


def _rounded_annular_band(outer_d, inner_d, band_w, z0, radius):
    radial_w = (outer_d - inner_d) / 2.0
    r = min(radius, band_w * 0.35, radial_w * 0.35)
    if r <= 0.0 or band_w <= 2.0 * r or radial_w <= 2.0 * r:
        return _annular_band(outer_d, inner_d, band_w, z0)

    outer_r = outer_d / 2.0
    inner_r = inner_d / 2.0
    body = _annular_cylinder(outer_d - 2.0 * r, inner_d + 2.0 * r, band_w).translate((0, 0, z0))
    mid = _annular_cylinder(outer_d, inner_d, band_w - 2.0 * r).translate((0, 0, z0 + r))
    for major_r in (outer_r - r, inner_r + r):
        for z in (z0 + r, z0 + band_w - r):
            body = body.union(cq.Solid.makeTorus(major_r, r).translate((0, 0, z)))
    return body.union(mid.val())


def _spherical_cup(ball_d, center, upper):
    pocket_r = ball_d / 2.0 + _cage_clearance(ball_d)
    wall_t = max(0.20, min(ball_d * 0.08, 0.42))
    outer = _sphere_tool(pocket_r + wall_t, center)
    inner = _sphere_tool(pocket_r, center)
    cup = outer.cut(inner)
    z = center[2]
    cap_start = ball_d * 0.08
    if upper:
        return cup.intersect(_z_clip(z + cap_start, z + pocket_r + wall_t))
    return cup.intersect(_z_clip(z - pocket_r - wall_t, z - cap_start))


def _cage_halves(pitch_d, ball_d, ball_count, width, cage_t, cage_width, cage_inner_d, cage_outer_d):
    ball_r = ball_d / 2.0
    sheet_t = max(0.20, min(cage_width * 0.22, width * 0.035))
    close_gap = max(0.06, min(ball_d * 0.04, 0.20))
    main_fillet = max(0.10, min(0.20, cage_t * 0.16, cage_width * 0.12))
    lower_half = _rounded_annular_band(cage_outer_d, cage_inner_d, sheet_t, width / 2.0 - close_gap - sheet_t, main_fillet)

    # Short inner and outer lips give each half a shallow channel section. The
    # lips face away from the ball-center plane and stay visually secondary.
    lip_radial = max(0.10, min((cage_outer_d - cage_inner_d) * 0.055, cage_t * 0.18))
    lip_h = max(sheet_t * 0.75, min(ball_r * 0.16, cage_width * 0.26))
    lower_outer_lip = _rounded_annular_band(
        cage_outer_d,
        cage_outer_d - 2.0 * lip_radial,
        lip_h,
        width / 2.0 - close_gap - lip_h,
        main_fillet * 0.60,
    )
    lower_inner_lip = _rounded_annular_band(
        cage_inner_d + 2.0 * lip_radial,
        cage_inner_d,
        lip_h,
        width / 2.0 - close_gap - lip_h,
        main_fillet * 0.60,
    )
    lower_half = lower_half.union(lower_outer_lip.val()).union(lower_inner_lip.val())

    radial_clip = _annular_cylinder(cage_outer_d, cage_inner_d, width).translate((0, 0, 0))
    for x, y, z in _ball_centers(pitch_d, ball_count):
        center = (x, y, width / 2.0 + z)
        lower_cup = _spherical_cup(ball_d, center, False).intersect(radial_clip)
        lower_half = lower_half.union(lower_cup.val())

    # Final clearance pass keeps the thin cups visibly wrapped around the balls
    # while ensuring the rolling elements do not share positive volume.
    clearance_r = ball_r + _cage_clearance(ball_d)
    for x, y, z in _ball_centers(pitch_d, ball_count):
        cutter = _sphere_tool(clearance_r, (x, y, width / 2.0 + z))
        lower_half = lower_half.cut(cutter)
    upper_half = lower_half.mirror("XY").translate((0, 0, width))
    for x, y, z in _ball_centers(pitch_d, ball_count):
        cutter = _sphere_tool(clearance_r, (x, y, width / 2.0 + z))
        lower_half = lower_half.cut(cutter)
        upper_half = upper_half.cut(cutter)
    for x, y, z in _ball_centers(pitch_d, ball_count):
        cutter = _sphere_tool(clearance_r, (x, y, width / 2.0 + z))
        lower_half = lower_half.cut(cutter)
        upper_half = upper_half.cut(cutter)
    return lower_half, upper_half


def _component_shapes(
    designation,
    bore_d,
    outer_d,
    width,
    ball_d,
    ball_count,
    pitch_d,
    race_groove_depth,
    cage_t,
    cage_width,
):
    del designation

    ball_r = ball_d / 2.0
    span = outer_d - bore_d
    # SKF 6000 section drawing gives d1 ~= 14.8 and D2 ~= 22.6 for d/D = 10/26.
    # d1 (inner land) keeps the normalized-span anchor: it yields real shoulder
    # recesses (0.7-1.0 mm) across all six rows. D2 (outer land) must instead
    # be derived FROM the groove bottom: the old linear-span anchor happened to
    # equal the groove-bottom radius by 6005, leaving the outer raceway with no
    # recess at all. The 6000 cue calibrates the outer shoulder height to
    # 0.062*ball_d (D2 = 22.6 exactly at 6000), which also lands within
    # ~0.1 mm of the real 6005 D2.
    inner_shoulder_d = bore_d + 0.30 * span
    gap = max(0.16, min(0.20, ball_d * 0.035))
    outer_groove_bottom_d = pitch_d + ball_d + 2.0 * gap
    outer_race_d = outer_groove_bottom_d - 2.0 * 0.062 * ball_d

    # Inner and outer rings are continuous closed radial-axial profiles,
    # revolved around the bearing axis. The shoulder diameters are anchored to
    # the SKF 6000 d1/D2 section cues; the deep-groove curve and small entry
    # chamfers are proportion geometry because no editable SW feature data or
    # manufacturer internal radii are available in this workspace.
    inner_ring = _inner_ring_revolved(bore_d, inner_shoulder_d, width, pitch_d, ball_d, race_groove_depth)
    outer_ring = _outer_ring_revolved(outer_d, outer_race_d, width, pitch_d, ball_d, race_groove_depth)

    # Two-piece style retainer geometry: upper and lower annular halves with
    # spherical pockets facing the balls from each side. This avoids the
    # previous "vertical posts around each ball" look.
    balls = []
    for x, y, z in _ball_centers(pitch_d, ball_count):
        balls.append(_sphere_tool(ball_r, (x, y, width / 2.0 + z)).val())
    cage_inner_d = max(inner_shoulder_d + 0.35, pitch_d - ball_d * 0.82)
    cage_outer_d = min(outer_race_d - 0.35, pitch_d + ball_d * 0.82)
    lower_half, upper_half = _cage_halves(
        pitch_d,
        ball_d,
        ball_count,
        width,
        cage_t,
        cage_width,
        cage_inner_d,
        cage_outer_d,
    )
    return outer_ring.val(), inner_ring.val(), lower_half.val(), upper_half.val(), balls


def build(
    designation,
    bore_d,
    outer_d,
    width_B,
    ball_d,
    ball_count,
    pitch_d,
    race_groove_depth,
    cage_t,
    cage_width,
):
    """Build an open single-row deep groove ball bearing.

    `designation` selects the coupled 6000-6005 catalog row in spec.py. The
    geometry is driven by the coupled d/D/B values plus proportion-based
    internal dimensions.
    """
    outer_ring, inner_ring, lower_cage_half, upper_cage_half, balls = _component_shapes(
        designation,
        bore_d,
        outer_d,
        width_B,
        ball_d,
        ball_count,
        pitch_d,
        race_groove_depth,
        cage_t,
        cage_width,
    )
    # named assembly per the preview-parts contract: the two cage halves are
    # distinct components (opposite pocket lips); the balls are repeated
    # instances of one component whose count is the catalog value ball_count
    result = cq.Assembly(name="single_row_deep_groove_ball_bearing")
    result.add(outer_ring, name="outer_ring")
    result.add(inner_ring, name="inner_ring")
    result.add(lower_cage_half, name="cage_lower")
    result.add(upper_cage_half, name="cage_upper")
    for i, ball in enumerate(balls):
        result.add(ball, name="ball_%02d" % (i + 1))
    return result
