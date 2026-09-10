"""Minifix cam housing rebuilt from the user-supplied SOLIDWORKS reference.

The reference is a third-party 14.8 x 13.5 mm unrimmed housing, not a verified
Hafele SKU.  Catalogue installation rows drive height, bolt-axis location and
optional rim; undocumented casting dimensions are measured-reference proportions.
See NOTES.md for the datum mapping, evidence and deliberate simplifications.

The body is constructed with analytic cylinders, a sphere, extrusions and
fillets.  No stored section clouds, imported topology or recovery solids.
"""

import math
import cadquery as cq


def _cylinder(radius, z, height):
    return cq.Workplane("XY").workplane(offset=z).circle(radius).extrude(height)


def _block(x, y, z, dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x, y, z))


def _cross(radius, width, reach, z, depth, corner):
    core = _cylinder(radius, z, depth)
    arm = cq.Workplane("XY").rect(2 * reach, width).extrude(depth)
    if corner:
        arm = arm.edges("|Z").fillet(corner)
    arm = arm.translate((0, 0, z))
    return core.union(arm).union(arm.rotate((0, 0, 0), (0, 0, 1), 90))


def _drive_cup(z, depth):
    """R2.8 cup with a full Y arm and front half of the X arm.

    Behind the split plane the straight X web meets the circular core directly;
    the reference has no 1.4 mm half-arm overhanging that 1 mm web.
    """
    y_arm = cq.Workplane("XY").rect(2.8, 8.8).extrude(depth).edges("|Z").fillet(1.0)
    y_arm = y_arm.translate((0, 0, z))
    front_x_arm = y_arm.rotate((0, 0, 0), (0, 0, 1), 90)
    front_x_arm = front_x_arm.cut(_block(-5, -5, z - 0.1, 10, 5, depth + 0.2))
    return _cylinder(2.8, z, depth).union(y_arm).union(front_x_arm)


def _direction_marks(top):
    """Exact reference pocket outlines: clockwise from +Z; no mirrored sketch.

    SOLIDWORKS Sketch1: outer arc R6.5, band 1.12, arrow shoulders 0.6,
    left tail at 140 degrees. Head outer corner has x=5.38 at radius 7.1.
    The final tip and pointer ordinate are measured sketch coordinates.
    """
    outer, inner = 6.5, 5.38
    shoulder = 0.6
    head_angle = math.acos(inner / (outer + shoulder))
    tail_angle = math.radians(140)
    middle = (head_angle + tail_angle) / 2
    arrow = (
        cq.Workplane("XY")
        .workplane(offset=top - 0.2)
        .moveTo(outer * math.cos(head_angle), outer * math.sin(head_angle))
        .threePointArc(
            (outer * math.cos(middle), outer * math.sin(middle)),
            (outer * math.cos(tail_angle), outer * math.sin(tail_angle)),
        )
        .lineTo(inner * math.cos(tail_angle), inner * math.sin(tail_angle))
        .threePointArc(
            (inner * math.cos(middle), inner * math.sin(middle)),
            (inner * math.cos(head_angle), inner * math.sin(head_angle)),
        )
        .lineTo(
            (inner - shoulder) * math.cos(head_angle), (inner - shoulder) * math.sin(head_angle)
        )
        .lineTo(inner, 2.56760448385823)
        .lineTo(
            (outer + shoulder) * math.cos(head_angle), (outer + shoulder) * math.sin(head_angle)
        )
        .close()
        .extrude(0.3)
    )
    triangle = (
        cq.Workplane("XY")
        .workplane(offset=top - 0.2)
        .moveTo(-1, -4.74398586126434)
        .lineTo(0, -6.93239551614177)
        .lineTo(1, -4.74398586126434)
        .close()
        .extrude(0.3)
    )
    return arrow, triangle


def build(
    body_diameter=14.8,
    housing_height=13.5,
    bolt_axis_height=9.0,
    has_rim=0,
    rim_diameter=0.0,
    rim_height=0.0,
    web_thickness=1.0,
    neck_slot_width=3.0,
    has_markings=1,
):
    """Open half-shell, rounded radial slot, spherical head seat and ribbed drive."""
    r = body_diameter / 2
    h = housing_height
    axis_z = h - bolt_axis_height
    roof = axis_z + 2.583
    cap_z = h - 0.8
    blank = _cylinder(r, 0, roof)
    lower = blank.cut(_block(-r - 1, 0, -1, 2 * r + 2, r + 1, roof + 2))
    slot_radius = neck_slot_width / 2
    slot = _block(-r - 1, -r - 1, axis_z - slot_radius, r + 3.1, 2 * r + 2, 2 * slot_radius)
    slot = slot.union(
        cq.Workplane("XZ").center(2.1, axis_z).circle(slot_radius).extrude(2 * r + 2, both=True)
    )
    bowl_radius = min(3.0, axis_z - 0.7)
    bowl = cq.Workplane("XY").sphere(bowl_radius).translate((0, 0, axis_z))
    # Tip inner flanks fitted to the reference planes, clipped by the casting.
    right_tip = (
        cq.Workplane("XY")
        .polyline([(5.4785 - 0.491, -1), (5.4785 + 0.491 * 5, 5), (r + 1, 5), (r + 1, -1)])
        .close()
        .extrude(1.5)
    )
    right_tip = right_tip.intersect(_cylinder(r, 0, 1.5))
    left_profile = [(-5.1517 + 0.109, -1), (-5.1517 - 0.109 * 6, 6), (-r - 1, 6), (-r - 1, -1)]
    left_low = (
        cq.Workplane("XY")
        .polyline(left_profile)
        .close()
        .extrude(2.5 - slot_radius)
        .translate((0, 0, axis_z - 2.5))
    )
    left_high = (
        cq.Workplane("XY")
        .polyline(left_profile)
        .close()
        .extrude(roof - axis_z - slot_radius)
        .translate((0, 0, axis_z + slot_radius))
    )
    lower = (
        lower.union(right_tip).union(left_low.intersect(blank)).union(left_high.intersect(blank))
    )
    lower = lower.cut(slot).cut(bowl).edges().fillet(0.25)

    # Straight Cartesian webs remain between rounded window cuts. Filleting
    # the cutters supplies continuous R0.25 roots at the roof and top cap.
    # X web: y=-thickness..0. Y web: x=3.7053369..4.4, offset from the axis.
    cage_h = cap_z - roof
    cup_z = axis_z + 3.2
    x_web = _block(-r - 2, -web_thickness, roof - 1, 2 * r + 4, web_thickness, cage_h + 2)
    y_web = _block(3.70533689244, -r - 2, roof - 1, 4.4 - 3.70533689244, r + 2, cage_h + 2)
    cup = _drive_cup(roof - 1, cage_h + 2)
    rear_void = (
        _block(-r - 1, -r - 1, roof, 2 * r + 2, r + 1, cage_h).cut(x_web).cut(y_web).cut(cup)
    )
    rear_void = rear_void.edges("|Z").fillet(0.25)
    rear_void = rear_void.edges("not |Z").fillet(0.25)
    front_void = _block(-r - 1, 0, roof - 1, 2 * r + 2, r + 1, cage_h + 1).cut(cup)
    front_void = front_void.edges("|Z").fillet(0.25)
    front_void = front_void.edges(">Z").fillet(0.25)
    upper = _cylinder(r, roof - 0.5, cage_h + 1.3).cut(rear_void).cut(front_void)
    front_below = _block(-r - 1, 0, roof - 1, 2 * r + 2, r + 1, cup_z - roof + 1)
    front_below = front_below.edges(">Z").fillet(0.25)
    upper = upper.cut(front_below)
    # Round the exposed rib ends, cap underside and front cup bottom.
    exterior = []
    for edge in upper.edges().vals():
        b = edge.BoundingBox()
        p = edge.Center()
        outer_vertical = (
            b.zlen > 0.1
            and b.xlen < 1e-5
            and b.ylen < 1e-5
            and p.x * p.x + p.y * p.y > r * r - 0.01
        )
        cap_arc = (
            edge.geomType() == "CIRCLE"
            and abs(edge.radius() - r) < 1e-5
            and abs(b.zmin - cap_z) < 1e-5
            and b.zlen < 1e-5
        )
        cup_bottom = (
            b.zlen < 1e-5
            and abs(b.zmin - cup_z) < 1e-5
            and p.y > 0.3
            and b.xmax < 4.5
            and b.xmin > -4.5
        )
        if outer_vertical or cap_arc or cup_bottom:
            exterior.append(edge)
    upper = upper.newObject(exterior).fillet(0.25)
    body = lower.union(upper)
    if has_rim:
        body = body.union(_cylinder(rim_diameter / 2, h - 0.02, rim_height + 0.02))
    top = h + rim_height
    # Keep a 0.8 mm floor under the drive even when the upper cage is longer.
    drive_depth = bolt_axis_height - 4.0
    drive = _cross(2.0, 1.2, 3.6, h - drive_depth, drive_depth + rim_height + 0.1, 0.25)
    drive = drive.edges("|Z").fillet(0.25)
    drive = drive.edges("<Z").fillet(0.25)
    body = body.cut(drive)
    # Only the inner wire of the upper planar face is the drive mouth.
    mouth = body.faces(">Z").val().innerWires()[0].Edges()
    body = body.newObject(mouth).fillet(0.25)
    if has_markings:
        arrow, triangle = _direction_marks(top)
        body = body.cut(arrow).cut(triangle)
    # Display / mounting datum: panel seating face at z=0, casting below it.
    result = body.translate((0, 0, -h)).clean()
    return result
