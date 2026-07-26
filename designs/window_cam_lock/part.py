"""Two-body simplified AmesburyTruth 17 Series cam-lock assembly."""

import cadquery as cq


def build(
    product_row,
    body_length,
    body_width,
    end_pad_h,
    body_h,
    deck_h,
    overall_h,
    hole_spacing,
    hole_d,
    hole_edge_offset,
    has_alignment_lugs,
    hole_csk_d,
    hole_csk_angle,
    housing_length,
    cavity_h,
    closed_wall_t,
    lever_length,
    lever_width,
    lever_tip_width,
    lever_t,
    lever_angle,
):
    """Build the fixed housing and rotating handle as two separate solids."""
    half_l = body_length / 2.0
    half_w = body_width / 2.0
    corner_cut = 0.10 * body_width
    base_profile = [
        (-half_l + corner_cut, -half_w),
        (half_l - corner_cut, -half_w),
        (half_l, -half_w + corner_cut),
        (half_l, half_w - corner_cut),
        (half_l - corner_cut, half_w),
        (-half_l + corner_cut, half_w),
        (-half_l, half_w - corner_cut),
        (-half_l, -half_w + corner_cut),
    ]

    base = cq.Workplane("XY").polyline(base_profile).close().extrude(end_pad_h)
    hole_y = -half_w + hole_edge_offset
    hole_points = [(-hole_spacing / 2.0, hole_y), (hole_spacing / 2.0, hole_y)]
    base = (
        base.faces(">Z")
        .workplane()
        .pushPoints(hole_points)
        .cskHole(hole_d, hole_csk_d, hole_csk_angle)
    )

    housing_width = 0.82 * body_width
    lower_housing = (
        cq.Workplane("XY")
        .ellipse(housing_length / 2.0, housing_width / 2.0)
        .extrude(body_h)
    )
    deck = (
        cq.Workplane("XY")
        .workplane(offset=body_h)
        .ellipse(housing_length / 2.0, housing_width / 2.0)
        .extrude(deck_h - body_h)
    )
    fixed_body = base.union(lower_housing).union(deck)

    # A shallow underside cavity is asymmetric: it opens through the near
    # (negative-Y) long side while the far long side and both short ends remain
    # closed. Cavity height is independent of every retained wall thickness.
    cavity_width = housing_width + 1.0 - closed_wall_t
    cavity_center_y = -(1.0 + closed_wall_t) / 2.0
    cavity = (
        cq.Workplane("XY")
        .center(0.0, cavity_center_y)
        .box(
            housing_length - 2.0 * closed_wall_t,
            cavity_width,
            cavity_h,
            centered=(True, True, False),
        )
    )
    fixed_body = fixed_body.cut(cavity)

    # 17.32 has two undimensioned alignment lugs on one long side. Both start
    # at Z=0 and therefore do not project below the flat mounting plane.
    if has_alignment_lugs:
        lug_length = 0.11 * body_length
        lug_width = 0.055 * body_width
        lug_h = 0.28 * end_pad_h
        lug_x = 0.28 * body_length
        lugs = (
            cq.Workplane("XY")
            .pushPoints(
                [
                    (-lug_x, -half_w - lug_width / 2.0),
                    (lug_x, -half_w - lug_width / 2.0),
                ]
            )
            .box(lug_length, lug_width, lug_h, centered=(True, True, False))
        )
        fixed_body = fixed_body.union(lugs)

    pivot_x = 0.10 * body_length
    boss_d = 0.48 * body_width
    spindle_d = 0.16 * body_width
    radial_clearance = 0.20
    axial_clearance = 0.20

    # Cut a real bearing opening so the spindle belongs to the rotating body
    # without intersecting or touching the fixed housing.
    pivot_bore = (
        cq.Workplane("XY")
        .workplane(offset=cavity_h)
        .center(pivot_x, 0.0)
        .circle(spindle_d / 2.0 + radial_clearance)
        .extrude(deck_h - cavity_h + axial_clearance)
    )
    fixed_body = fixed_body.cut(pivot_bore)

    cap_bottom = deck_h + axial_clearance
    cap = (
        cq.Workplane("XY")
        .workplane(offset=cap_bottom)
        .center(pivot_x, 0.0)
        .circle(boss_d / 2.0)
        .extrude(overall_h - cap_bottom)
    )
    spindle = (
        cq.Workplane("XY")
        .workplane(offset=cavity_h + axial_clearance)
        .center(pivot_x, 0.0)
        .circle(spindle_d / 2.0)
        .extrude(overall_h - cavity_h - axial_clearance)
    )

    # The lever is one continuous solid with a thin middle and abrupt downward
    # steps at the pivot and free end. It is fused only to the rotating cap.
    root_x = -0.18 * lever_length
    tip_step_x = -0.76 * lever_length
    lever_plan = [
        (0.0, -lever_width / 2.0),
        (root_x, -lever_width / 2.0),
        (tip_step_x, -0.42 * lever_tip_width),
        (-lever_length, -lever_tip_width / 2.0),
        (-lever_length, lever_tip_width / 2.0),
        (tip_step_x, 0.42 * lever_tip_width),
        (root_x, lever_width / 2.0),
        (0.0, lever_width / 2.0),
    ]
    lever_mid_t = 0.48 * lever_t
    lever_top_z = overall_h
    lever = (
        cq.Workplane("XY")
        .workplane(offset=lever_top_z - lever_mid_t)
        .polyline(lever_plan)
        .close()
        .extrude(lever_mid_t)
    )
    root_step = (
        cq.Workplane("XY")
        .workplane(offset=lever_top_z - lever_t)
        .rect(0.22 * lever_length, lever_width)
        .extrude(lever_t)
        .translate((-0.09 * lever_length, 0.0, 0.0))
    )
    tip_step_plan = [
        (tip_step_x, -0.42 * lever_tip_width),
        (-lever_length, -lever_tip_width / 2.0),
        (-lever_length, lever_tip_width / 2.0),
        (tip_step_x, 0.42 * lever_tip_width),
    ]
    tip_step = (
        cq.Workplane("XY")
        .workplane(offset=lever_top_z - lever_t)
        .polyline(tip_step_plan)
        .close()
        .extrude(lever_t - lever_mid_t)
    )
    lever = lever.union(root_step).union(tip_step)
    lever = (
        lever.translate((pivot_x, 0.0, 0.0))
        .rotate(
            (pivot_x, 0.0, lever_top_z),
            (pivot_x, 0.0, lever_top_z + 1.0),
            lever_angle,
        )
    )
    rotating_body = cap.union(spindle).union(lever)

    result = cq.Compound.makeCompound([fixed_body.val(), rotating_body.val()])
    return result
