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

    # Drawn-steel sockets flare into the flange instead of meeting it at a
    # sharp corner. The drawing does not dimension this transition, so size
    # the root radius from the sheet thickness (an explicit proportion rule).
    root_radius = 2.0 * flange_t
    arc_mid = root_radius * (1.0 - 2.0**-0.5)
    root_fillet = (
        cq.Workplane("XZ")
        .moveTo(outer_r, 0.0)
        .lineTo(outer_r + root_radius, 0.0)
        .threePointArc(
            (outer_r + arc_mid, -arc_mid),
            (outer_r, -root_radius),
        )
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )
    result = result.union(root_fillet)

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
