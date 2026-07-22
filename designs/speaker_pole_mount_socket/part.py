"""Parametric flanged speaker-pole socket (top-hat mount)."""

import cadquery as cq


def build(
    bore_d,
    cup_outer_d,
    flange_od,
    flange_t,
    depth,
    hole_d,
    hole_bcd,
    bottom_radius,
):
    """Build a closed-bottom drawn cup with a four-hole mounting flange."""
    outer_r = cup_outer_d / 2.0
    inner_r = bore_d / 2.0 + 1.0  # 2 mm diametral pole clearance

    cup = (
        cq.Workplane("XY")
        .workplane(offset=-depth)
        .circle(outer_r)
        .extrude(depth)
        .edges("<Z")
        .fillet(bottom_radius)
    )
    flange = cq.Workplane("XY").circle(flange_od / 2.0).extrude(flange_t)
    result = cup.union(flange)

    # Leave a flange-thick closed bottom, while opening the cup through the top.
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=-depth + flange_t)
        .circle(inner_r)
        .extrude(depth + flange_t)
    )
    result = result.cut(cavity)

    hole_r = hole_bcd / 2.0
    hole_points = [(hole_r, 0.0), (0.0, hole_r), (-hole_r, 0.0), (0.0, -hole_r)]
    result = (
        result.faces(">Z")
        .workplane()
        .pushPoints(hole_points)
        .hole(hole_d)
    )
    return result
