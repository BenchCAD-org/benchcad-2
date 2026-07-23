"""Parametric Häfele Minifix 15 eccentric-cam connector housing."""

import math

import cadquery as cq


def _sector_wire(outer_r, inner_r, z, angle_0, angle_1,
                 inner_dx=0.0, inner_dy=0.0):
    """Build one exact four-edge annular-sector wire for a smooth loft."""
    outer = cq.Edge.makeCircle(
        outer_r, (0.0, 0.0, z), (0.0, 0.0, 1.0),
        angle_0, angle_1, True,
    )
    inner = cq.Edge.makeCircle(
        inner_r, (inner_dx, inner_dy, z), (0.0, 0.0, 1.0),
        angle_0, angle_1, False,
    )
    tip_1 = cq.Edge.makeLine(outer.endPoint(), inner.startPoint())
    tip_2 = cq.Edge.makeLine(inner.endPoint(), outer.startPoint())
    return cq.Wire.assembleEdges([outer, tip_1, inner, tip_2])


def _hook_wire(body_diameter, bolt_hole_diameter, z, direction,
               half_open, outer_scale, inner_scale, eccentric_scale):
    """Build one eccentric C-section, open and offset toward ``direction``."""
    inner_offset = body_diameter * eccentric_scale
    direction_rad = math.radians(direction)
    inner_dx = inner_offset * math.cos(direction_rad)
    inner_dy = inner_offset * math.sin(direction_rad)
    angle_0 = direction + half_open
    angle_1 = direction + 360.0 - half_open
    return _sector_wire(
        body_diameter * outer_scale,
        bolt_hole_diameter * inner_scale,
        z,
        angle_0,
        angle_1,
        inner_dx,
        inner_dy,
    )


def _twisted_hook(body_diameter, bolt_hole_diameter, bolt_plane,
                  cam_web_thickness):
    """Loft the lower capture hook through three shrinking, rotating C-wires."""
    bottom = _hook_wire(
        body_diameter, bolt_hole_diameter, 0.0,
        0.0, 31.0, 0.50, 0.50, 0.035,
    )
    middle = _hook_wire(
        body_diameter, bolt_hole_diameter, bolt_plane * 0.52,
        -12.0, 34.0, 0.46, 0.45, 0.038,
    )
    top = _hook_wire(
        body_diameter, bolt_hole_diameter,
        bolt_plane + cam_web_thickness * 0.18,
        -24.0, 37.0, 0.415, 0.40, 0.042,
    )
    return cq.Solid.makeLoft([bottom, middle, top], ruled=False)


def _rib_loft(radius, wall, z_bottom, z_top, center, end_half, waist_half):
    """Create one curved cage rib with broad roots and a smooth narrow waist."""
    middle_z = (z_bottom + z_top) / 2.0
    bottom = _sector_wire(
        radius, radius - wall, z_bottom,
        center - end_half, center + end_half,
    )
    middle = _sector_wire(
        radius, radius - wall, middle_z,
        center - waist_half, center + waist_half,
    )
    top = _sector_wire(
        radius, radius - wall, z_top,
        center - end_half, center + end_half,
    )
    return cq.Solid.makeLoft([bottom, middle, top], ruled=False)


def _revolved_plate(radius, height, edge, z0):
    """Create a softly bevelled head or seating flange from a radial section."""
    edge = min(edge, height * 0.35, radius * 0.08)
    return (cq.Workplane("XZ")
            .moveTo(0.0, 0.0)
            .lineTo(radius - edge, 0.0)
            .lineTo(radius, edge)
            .lineTo(radius, height - edge)
            .lineTo(radius - edge, height)
            .lineTo(0.0, height)
            .close().revolve(360.0, (0.0, 0.0), (0.0, 1.0))
            .translate((0.0, 0.0, z0)))


def build(
    body_diameter,
    housing_height,
    has_rim,
    rim_diameter,
    rim_height,
    bolt_axis_height,
    bolt_hole_diameter,
    cam_web_thickness,
    drive_style,
    drive_size,
):
    """Build a photo-informed, catalogue-anchored benchmark proxy.

    The catalogue fixes the mounting dimensions but not the casting internals.
    The twisted hook, curved ribs, eccentric core, and face details are smooth
    proportional geometry for qualitative resemblance, not OEM cam kinematics.
    """
    radius = body_diameter / 2.0
    head_thickness = body_diameter * 0.10
    bolt_plane = housing_height - bolt_axis_height
    cage_top = housing_height - head_thickness
    overlap = 0.28

    # One continuous, tapered C-hook replaces the former stack of flat rings.
    hook = _twisted_hook(
        body_diameter,
        bolt_hole_diameter,
        bolt_plane,
        cam_web_thickness,
    )
    result = cq.Workplane("XY").newObject([hook])

    # Exact circular-sector lofts create three curved, waisted casting ribs.
    rib_wall = body_diameter * 0.085
    rib_bottom = body_diameter * 0.037
    rib_top = cage_top + overlap
    rear_rib = _rib_loft(
        radius, rib_wall, rib_bottom, rib_top,
        180.0, 34.0, 20.0,
    )
    side_a = _rib_loft(
        radius, rib_wall, rib_bottom, rib_top,
        96.0, 19.0, 11.0,
    )
    side_b = _rib_loft(
        radius, rib_wall, rib_bottom, rib_top,
        264.0, 19.0, 11.0,
    )
    result = result.union(rear_rib).union(side_a).union(side_b)

    # The eccentric cam barrel changes centre and radius through its height.
    hook_top = bolt_plane + cam_web_thickness * 0.18
    cam_radius = body_diameter * 0.225
    cam_offset = body_diameter * 0.055
    cam_bottom = max(body_diameter * 0.14,
                     hook_top - cam_web_thickness * 0.72)
    cam_top = cage_top + overlap
    cam_height = cam_top - cam_bottom
    cam_core = (cq.Workplane("XY")
                .workplane(offset=cam_bottom)
                .center(-cam_offset * 0.45, 0.0)
                .circle(cam_radius * 0.82)
                .workplane(offset=cam_height * 0.46)
                .center(cam_offset * 1.35, 0.0)
                .circle(cam_radius)
                .workplane(offset=cam_height * 0.54)
                .center(-cam_offset * 0.28, 0.0)
                .circle(cam_radius * 0.91)
                .loft(combine=True))
    result = result.union(cam_core)

    # A curved web connects the rear hook wall to the rising eccentric core.
    ramp_rear_x = -radius + body_diameter * 0.055
    ramp_outer_end = cam_offset + cam_radius * 0.58
    ramp_inner_end = cam_offset - cam_radius * 0.28
    outer_mid = (-radius * 0.38, (hook_top + cam_bottom) * 0.56)
    inner_mid = (-radius * 0.43, (hook_top + cam_bottom) * 0.43)
    ramp = (cq.Workplane("XZ")
            .moveTo(ramp_rear_x, body_diameter * 0.09)
            .threePointArc(
                outer_mid,
                (ramp_outer_end, cam_bottom + cam_web_thickness * 0.48),
            )
            .lineTo(ramp_inner_end, cam_bottom - cam_web_thickness * 0.30)
            .threePointArc(
                inner_mid,
                (ramp_rear_x + body_diameter * 0.025,
                 body_diameter * 0.09 + cam_web_thickness),
            )
            .close().extrude(cam_web_thickness * 1.25, both=True))
    result = result.union(ramp)

    head = _revolved_plate(
        radius,
        head_thickness + overlap,
        body_diameter * 0.035,
        cage_top - overlap,
    )
    result = result.union(head)

    if has_rim:
        flange_overlap = min(0.12, rim_height * 0.12)
        flange = _revolved_plate(
            rim_diameter / 2.0,
            rim_height + flange_overlap,
            min(0.16, rim_height * 0.18),
            housing_height - flange_overlap,
        )
        result = result.union(flange)

    top_height = housing_height + (rim_height if has_rim else 0.0)

    # A toroidal cut makes the shallow circular groove around the drive boss.
    groove_minor = min(body_diameter * 0.026, head_thickness * 0.24)
    groove = cq.Solid.makeTorus(
        body_diameter * 0.30,
        groove_minor,
        (0.0, 0.0, top_height - groove_minor * 0.18),
    )
    result = result.cut(groove)

    drive_depth = min(0.70, head_thickness * 0.42)
    drive_z = top_height - drive_depth
    if drive_style == 2:
        drive = (cq.Workplane("XY").workplane(offset=drive_z)
                 .polygon(6, drive_size * 1.1547)
                 .extrude(drive_depth + 0.05))
        result = result.cut(drive)
    else:
        arm_length = body_diameter * 0.36
        drive = (cq.Workplane("XY").workplane(offset=drive_z)
                 .slot2D(arm_length, drive_size, 0.0)
                 .extrude(drive_depth + 0.05))
        if drive_style == 0:
            cross_arm = (cq.Workplane("XY").workplane(offset=drive_z)
                         .slot2D(arm_length, drive_size, 90.0)
                         .extrude(drive_depth + 0.05))
            drive = drive.union(cross_arm)
        result = result.cut(drive)
    return result
