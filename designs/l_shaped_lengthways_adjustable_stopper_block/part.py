"""MISUMI L-shaped, lengthways-adjustable threaded stopper-block body."""

import cadquery as cq


def build(
    thread_nominal_d_M,
    thread_axis_height_H,
    top_margin_H1,
    transverse_width_T1,
    upright_length_W1,
    base_length_L1,
    base_thickness_S,
    mount_hole_pitch_P,
    first_hole_offset_G1,
    counterbore_diameter_d1,
    through_hole_diameter_d2,
    counterbore_depth_l,
    top_chamfer_C,
    internal_fillet_R,
):
    overall_height = thread_axis_height_H + top_margin_H1

    # Coordinate contract: X follows L1 from the upright outer face, Y is
    # centered across T1, and Z rises from the base underside.
    base = (
        cq.Workplane("XY")
        .box(base_length_L1, transverse_width_T1, base_thickness_S)
        .translate((base_length_L1 / 2.0, 0.0, base_thickness_S / 2.0))
    )
    upright = (
        cq.Workplane("XY")
        .box(upright_length_W1, transverse_width_T1, overall_height)
        .translate((upright_length_W1 / 2.0, 0.0, overall_height / 2.0))
        .edges("|X and >Z")
        .chamfer(top_chamfer_C)
    )
    result = base.union(upright).clean()

    # Select only the concave edge at X=W1, Z=S; it spans the full T1 width.
    edge_tolerance = 0.01
    inner_edge = cq.selectors.BoxSelector(
        (
            upright_length_W1 - edge_tolerance,
            -transverse_width_T1,
            base_thickness_S - edge_tolerance,
        ),
        (
            upright_length_W1 + edge_tolerance,
            transverse_width_T1,
            base_thickness_S + edge_tolerance,
        ),
    )
    result = result.edges(inner_edge).fillet(internal_fillet_R)

    # The catalog specifies an internal M thread. Per family scope, represent
    # it as a nominal-diameter cylindrical through bore without a helix.
    adjustment_bore = (
        cq.Workplane("YZ")
        .center(0.0, thread_axis_height_H)
        .circle(thread_nominal_d_M / 2.0)
        .extrude(upright_length_W1 + 2.0)
        .translate((-1.0, 0.0, 0.0))
    )
    result = result.cut(adjustment_bore)

    mounting_centers = [
        (first_hole_offset_G1, 0.0),
        (first_hole_offset_G1 + mount_hole_pitch_P, 0.0),
    ]
    through_holes = (
        cq.Workplane("XY")
        .pushPoints(mounting_centers)
        .circle(through_hole_diameter_d2 / 2.0)
        .extrude(base_thickness_S + 2.0)
        .translate((0.0, 0.0, -1.0))
    )
    result = result.cut(through_holes)

    counterbores = (
        cq.Workplane("XY")
        .workplane(offset=base_thickness_S - counterbore_depth_l)
        .pushPoints(mounting_centers)
        .circle(counterbore_diameter_d1 / 2.0)
        .extrude(counterbore_depth_l + 1.0)
    )
    result = result.cut(counterbores).clean()
    return result
