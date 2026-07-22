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


def _cage_bridge(pitch_d, cage_t, cage_width, bridge_len, angle, z):
    radius = pitch_d / 2.0
    cx = radius * math.cos(angle)
    cy = radius * math.sin(angle)
    angle_deg = math.degrees(angle) + 90.0
    return (
        cq.Workplane("XY")
        .box(bridge_len, cage_t, cage_width)
        .rotate((0, 0, 0), (0, 0, 1), angle_deg)
        .translate((cx, cy, z))
    )


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
    race_clearance = ball_d * 0.04
    span = outer_d - bore_d
    # SKF 6000 section drawing gives d1 ~= 14.8 and D2 ~= 22.6 for d/D = 10/26.
    # The same normalized shoulder relationship is used for the 6000-6005 rows.
    inner_shoulder_d = bore_d + 0.30 * span
    outer_race_d = outer_d - (3.4 / 16.0) * span

    # Inner and outer rings are each continuous thick annular bodies. Their
    # facing race shoulders are anchored to the SKF d1/D2 section diameters
    # rather than being simple pitch +/- ball offsets.
    inner_ring = _annular_cylinder(inner_shoulder_d, bore_d, width)
    outer_ring = _annular_cylinder(outer_d, outer_race_d, width)

    # Shallow end counterbores create visible shoulders at the open faces. They
    # are proportion cues from the SKF section/profile view, not catalog data.
    end_relief = min(width * 0.24, ball_d * 0.34)
    inner_relief_d = max(bore_d + 0.6, inner_shoulder_d - race_groove_depth * 1.55)
    outer_relief_d = min(outer_d - 0.6, outer_race_d + race_groove_depth * 1.55)
    inner_ring = inner_ring.cut(_counterbore_cut(inner_relief_d, inner_shoulder_d + 0.4, end_relief, 0.0))
    inner_ring = inner_ring.cut(_counterbore_cut(inner_relief_d, inner_shoulder_d + 0.4, end_relief, width - end_relief))
    outer_ring = outer_ring.cut(_counterbore_cut(outer_race_d - 0.4, outer_relief_d, end_relief, 0.0))
    outer_ring = outer_ring.cut(_counterbore_cut(outer_race_d - 0.4, outer_relief_d, end_relief, width - end_relief))

    # Raceway cues: local toroidal grooves on the facing cylindrical surfaces
    # of the continuous rings. This keeps each ring as one body; it does not
    # slice out the middle axial band.
    groove_r = ball_r + race_clearance + race_groove_depth * 0.04
    raceway_sweep = _torus_tool(pitch_d / 2.0, groove_r, width / 2.0)
    inner_ring = inner_ring.cut(raceway_sweep)
    outer_ring = outer_ring.cut(raceway_sweep)

    # Simplified sheet-metal cage: two side rails joined by bridges between
    # adjacent balls. This reads like an open bearing retainer instead of a
    # single middle ring passing through the rolling elements. A final oversized
    # spherical pocket cut at each ball center guarantees ball clearance.
    cage_inner_d = pitch_d - cage_t
    cage_outer_d = pitch_d + cage_t
    cage_clearance = ball_d * 0.10
    rail_w = max(0.14, min(cage_width * 0.10, width * 0.03))
    rail_offset = min(ball_r + cage_clearance + rail_w / 2.0, width / 2.0 - rail_w * 0.70)
    bridge_width = 2.0 * rail_offset + rail_w
    lower_rail = _annular_cylinder(cage_outer_d, cage_inner_d, rail_w).translate(
        (0, 0, width / 2.0 - rail_offset - rail_w / 2.0)
    )
    upper_rail = _annular_cylinder(cage_outer_d, cage_inner_d, rail_w).translate(
        (0, 0, width / 2.0 + rail_offset - rail_w / 2.0)
    )
    cage = lower_rail.union(upper_rail.val())

    bridge_span = 2.0 * math.pi * (pitch_d / 2.0) / float(ball_count)
    bridge_len = max(0.35, min(ball_d * 0.22, bridge_span - ball_d * 1.35))
    for i in range(int(ball_count)):
        mid_angle = 2.0 * math.pi * (i + 0.5) / float(ball_count)
        cage = cage.union(_cage_bridge(pitch_d, cage_t, bridge_width, bridge_len, mid_angle, width / 2.0).val())

    for x, y, z in _ball_centers(pitch_d, ball_count):
        cage = cage.cut(_sphere_tool(ball_r + cage_clearance, (x, y, width / 2.0 + z)))

    balls = []
    for x, y, z in _ball_centers(pitch_d, ball_count):
        balls.append(_sphere_tool(ball_r, (x, y, width / 2.0 + z)).val())

    return outer_ring.val(), inner_ring.val(), cage.val(), balls


def build(
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
    """Build an open single-row deep groove ball bearing.

    `designation` selects the coupled 6000-6005 catalog row in spec.py. The
    geometry is driven by the coupled d/D/B values plus proportion-based
    internal dimensions.
    """
    outer_ring, inner_ring, cage, balls = _component_shapes(
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
    )
    shapes = [outer_ring, inner_ring, cage] + balls
    result = cq.Compound.makeCompound(shapes)
    return result
