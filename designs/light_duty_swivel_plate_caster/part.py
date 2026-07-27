"""Four-component JW Winco EN 22870 Form L caster assembly."""

import math

import cadquery as cq


_RADIAL_CLEARANCE = 0.20
_AXIAL_CLEARANCE = 0.25


def _derived_geometry(
    wheel_d,
    wheel_width,
    axle_d,
    overall_h,
    plate_l,
    plate_w,
    sheet_scale=1.0,
    race_scale=1.0,
    slot_scale=1.0,
):
    """Return only explicitly proportion-based construction dimensions."""
    plate_min = min(plate_l, plate_w)
    plate_t = max(1.6, 0.035 * plate_min) * sheet_scale
    upper_race_d = 0.46 * plate_min * race_scale
    upper_race_h = max(3.0, 0.060 * overall_h) * race_scale
    lower_race_d = 0.40 * plate_min * race_scale
    lower_race_h = max(2.6, 0.050 * overall_h) * race_scale
    fork_t = max(1.6, 0.080 * wheel_width) * sheet_scale
    side_clearance = 0.8 + 0.010 * wheel_d
    yoke_outer_w = wheel_width + 2.0 * (side_clearance + fork_t)
    bridge_t = max(2.0, 0.11 * wheel_width) * sheet_scale
    slot_w = max(3.0, 0.55 * axle_d) * slot_scale
    slot_l = 1.65 * slot_w
    wheel_edge_r = min(0.08 * wheel_width, 0.04 * wheel_d)
    return {
        "plate_t": plate_t,
        "plate_corner_r": min(2.0, 0.04 * plate_min),
        "upper_race_d": upper_race_d,
        "upper_race_h": upper_race_h,
        "lower_race_d": lower_race_d,
        "lower_race_h": lower_race_h,
        "fork_t": fork_t,
        "side_clearance": side_clearance,
        "yoke_outer_w": yoke_outer_w,
        "bridge_t": bridge_t,
        "slot_w": slot_w,
        "slot_l": slot_l,
        "wheel_edge_r": wheel_edge_r,
    }


def build_mounting_plate(
    wheel_d,
    wheel_width,
    axle_d,
    overall_h,
    plate_l,
    plate_w,
    mount_pitch_x,
    mount_pitch_y,
    sheet_scale,
    race_scale,
    slot_scale,
):
    """Build the mounting plate and simplified upper swivel-race envelope."""
    g = _derived_geometry(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    plate_t = g["plate_t"]
    plate_bottom = overall_h - plate_t
    plate = (
        cq.Workplane("XY")
        .workplane(offset=plate_bottom)
        .box(
            plate_l,
            plate_w,
            plate_t,
            centered=(True, True, False),
        )
        .edges("|Z")
        .fillet(g["plate_corner_r"])
    )

    # Slot size is not published. Each capsule is a documented proportion and
    # is oriented radially, matching the official drawing and product photo.
    for x in (-mount_pitch_x / 2.0, mount_pitch_x / 2.0):
        for y in (-mount_pitch_y / 2.0, mount_pitch_y / 2.0):
            angle = math.degrees(math.atan2(y, x))
            slot = (
                cq.Workplane("XY")
                .workplane(offset=plate_bottom - 0.5)
                .center(x, y)
                .slot2D(g["slot_l"], g["slot_w"], angle)
                .extrude(plate_t + 1.0)
            )
            plate = plate.cut(slot)

    upper_race = (
        cq.Workplane("XY")
        .workplane(offset=plate_bottom - g["upper_race_h"])
        .circle(g["upper_race_d"] / 2.0)
        .extrude(g["upper_race_h"] + 0.05)
    )
    return plate.union(upper_race)


def build_swivel_fork(
    wheel_d,
    wheel_width,
    axle_d,
    overall_h,
    plate_l,
    plate_w,
    swivel_offset,
    sheet_scale,
    race_scale,
    slot_scale,
):
    """Build the lower race, bridge, and two connected fork legs."""
    g = _derived_geometry(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    axle_z = wheel_d / 2.0
    plate_bottom = overall_h - g["plate_t"]
    lower_top = plate_bottom - g["upper_race_h"] - _AXIAL_CLEARANCE
    lower_bottom = lower_top - g["lower_race_h"]

    lower_race = (
        cq.Workplane("XY")
        .workplane(offset=lower_bottom)
        .circle(g["lower_race_d"] / 2.0)
        .extrude(g["lower_race_h"])
    )

    # The bridge overlaps both the lower race and the upper ends of the fork
    # legs, so the entire swivel-fork component is one connected solid.
    bridge_top_overlap = 0.30
    bridge = (
        cq.Workplane("XY")
        .workplane(
            offset=lower_bottom - g["bridge_t"] + bridge_top_overlap,
        )
        .box(
            0.80 * g["lower_race_d"],
            g["yoke_outer_w"],
            g["bridge_t"],
            centered=(True, True, False),
        )
    )

    leg_top_z = lower_bottom + 0.15
    leg_profile = [
        (-0.28 * g["lower_race_d"], leg_top_z),
        (0.32 * g["lower_race_d"], leg_top_z),
        (
            swivel_offset + 0.95 * axle_d,
            axle_z + 0.95 * axle_d,
        ),
        (
            swivel_offset + 0.95 * axle_d,
            axle_z - 0.85 * axle_d,
        ),
        (
            swivel_offset - 0.95 * axle_d,
            axle_z - 0.85 * axle_d,
        ),
    ]
    centered_leg = (
        cq.Workplane("XZ")
        .polyline(leg_profile)
        .close()
        .extrude(g["fork_t"] / 2.0, both=True)
    )
    leg_y = (
        wheel_width / 2.0
        + g["side_clearance"]
        + g["fork_t"] / 2.0
    )
    left_leg = centered_leg.translate((0.0, -leg_y, 0.0))
    right_leg = centered_leg.translate((0.0, leg_y, 0.0))
    fork = lower_race.union(bridge).union(left_leg).union(right_leg)

    axle_hole = cq.Solid.makeCylinder(
        axle_d / 2.0 + _RADIAL_CLEARANCE,
        g["yoke_outer_w"] + 2.0,
        cq.Vector(
            swivel_offset,
            -g["yoke_outer_w"] / 2.0 - 1.0,
            axle_z,
        ),
        cq.Vector(0.0, 1.0, 0.0),
    )
    return fork.cut(cq.Workplane("XY").newObject([axle_hole]))


def build_wheel(
    wheel_d,
    wheel_width,
    axle_d,
    overall_h,
    plate_l,
    plate_w,
    swivel_offset,
    sheet_scale,
    race_scale,
    slot_scale,
):
    """Build one connected wheel envelope with a through axle bore."""
    g = _derived_geometry(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    axle_z = wheel_d / 2.0
    wheel_solid = cq.Solid.makeCylinder(
        wheel_d / 2.0,
        wheel_width,
        cq.Vector(swivel_offset, -wheel_width / 2.0, axle_z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    wheel = cq.Workplane("XY").newObject([wheel_solid])
    wheel = wheel.edges("%CIRCLE").fillet(g["wheel_edge_r"])

    # Shallow side recesses leave a raised tread rim and hub in one solid.
    recess_depth = min(1.5, 0.10 * wheel_width)
    recess_outer_r = 0.34 * wheel_d
    hub_r = 0.18 * wheel_d
    left_outer = cq.Solid.makeCylinder(
        recess_outer_r,
        recess_depth + 0.05,
        cq.Vector(
            swivel_offset,
            -wheel_width / 2.0 - 0.05,
            axle_z,
        ),
        cq.Vector(0.0, 1.0, 0.0),
    )
    left_inner = cq.Solid.makeCylinder(
        hub_r,
        recess_depth + 0.05,
        cq.Vector(
            swivel_offset,
            -wheel_width / 2.0 - 0.05,
            axle_z,
        ),
        cq.Vector(0.0, 1.0, 0.0),
    )
    right_outer = cq.Solid.makeCylinder(
        recess_outer_r,
        recess_depth + 0.05,
        cq.Vector(
            swivel_offset,
            wheel_width / 2.0 + 0.05,
            axle_z,
        ),
        cq.Vector(0.0, -1.0, 0.0),
    )
    right_inner = cq.Solid.makeCylinder(
        hub_r,
        recess_depth + 0.05,
        cq.Vector(
            swivel_offset,
            wheel_width / 2.0 + 0.05,
            axle_z,
        ),
        cq.Vector(0.0, -1.0, 0.0),
    )
    left_recess = left_outer.cut(left_inner)
    right_recess = right_outer.cut(right_inner)
    wheel = wheel.cut(cq.Workplane("XY").newObject([left_recess]))
    wheel = wheel.cut(cq.Workplane("XY").newObject([right_recess]))

    axle_bore = cq.Solid.makeCylinder(
        axle_d / 2.0 + _RADIAL_CLEARANCE,
        wheel_width + 2.0,
        cq.Vector(swivel_offset, -wheel_width / 2.0 - 1.0, axle_z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    return wheel.cut(cq.Workplane("XY").newObject([axle_bore]))


def build_axle_fastener(
    wheel_d,
    wheel_width,
    axle_d,
    overall_h,
    plate_l,
    plate_w,
    swivel_offset,
    sheet_scale,
    race_scale,
    slot_scale,
):
    """Build a connected shaft with simplified cylindrical head and nut."""
    g = _derived_geometry(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    axle_z = wheel_d / 2.0
    head_gap = _AXIAL_CLEARANCE
    head_t = max(1.4, 0.30 * axle_d)
    head_d = 1.80 * axle_d
    shaft_length = g["yoke_outer_w"] + 2.0 * (head_gap + head_t)
    shaft_start_y = -shaft_length / 2.0
    shaft = cq.Solid.makeCylinder(
        axle_d / 2.0,
        shaft_length,
        cq.Vector(swivel_offset, shaft_start_y, axle_z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    left_head = cq.Solid.makeCylinder(
        head_d / 2.0,
        head_t,
        cq.Vector(swivel_offset, shaft_start_y, axle_z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    right_head = cq.Solid.makeCylinder(
        head_d / 2.0,
        head_t,
        cq.Vector(
            swivel_offset,
            g["yoke_outer_w"] / 2.0 + head_gap,
            axle_z,
        ),
        cq.Vector(0.0, 1.0, 0.0),
    )
    axle = shaft.fuse(left_head).fuse(right_head)
    return cq.Workplane("XY").newObject([axle])


def build(
    catalog_size,
    wheel_d,
    wheel_width,
    axle_d,
    overall_h,
    plate_l,
    plate_w,
    swivel_offset,
    mount_pitch_x,
    mount_pitch_y,
    sheet_scale,
    race_scale,
    slot_scale,
):
    """Build the named four-component Form L caster assembly."""
    _ = catalog_size
    mounting_plate = build_mounting_plate(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        mount_pitch_x,
        mount_pitch_y,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    swivel_fork = build_swivel_fork(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        swivel_offset,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    wheel = build_wheel(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        swivel_offset,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    axle_fastener = build_axle_fastener(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        swivel_offset,
        sheet_scale,
        race_scale,
        slot_scale,
    )

    result = cq.Assembly(name="light_duty_swivel_plate_caster")
    result.add(mounting_plate, name="mounting_plate")
    result.add(swivel_fork, name="swivel_fork")
    result.add(wheel, name="wheel")
    result.add(axle_fastener, name="axle_fastener")
    return result
