"""Five-component JW Winco EN 22870 Form L caster assembly."""

import math

import cadquery as cq


_RADIAL_CLEARANCE = 0.20
_AXIAL_CLEARANCE = 0.25


def _fastener(axle_d):
    """Return explicitly proportioned axle-fastener envelope dimensions."""
    return {
        "s": 1.80 * axle_d,
        "k": max(1.4, 0.65 * axle_d),
        "m": 0.85 * axle_d,
    }


def _hex_prism(across_flats, length, origin):
    """Hex bar of the given width across flats, along +Y from origin."""
    circum_r = across_flats / math.sqrt(3.0)
    return (
        cq.Workplane("XZ", origin=(origin.x, origin.y, origin.z))
        .polygon(6, 2.0 * circum_r)
        .extrude(-length)
    )


def _derived_geometry(
    wheel_d,
    wheel_width,
    axle_d,
    overall_h,
    plate_l,
    plate_w,
    mount_slot_w,
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

    # EN 22870 publishes d2 as mounting-slot width. Only the elongated length
    # is unpublished, so slot_scale perturbs length and never changes d2.
    slot_w = mount_slot_w
    slot_l = 1.20 * mount_slot_w * slot_scale

    wheel_r = wheel_d / 2.0
    half_b = wheel_width / 2.0
    drop_max = wheel_r - math.sqrt(max(wheel_r * wheel_r - half_b * half_b, 0.0))
    crown_drop = min(0.045 * wheel_d, 0.75 * drop_max)
    crown_sphere_r = math.sqrt((wheel_r - crown_drop) ** 2 + half_b * half_b)

    # Unpublished pressing envelope: a broad draw lowers a central platform.
    transition_outer_r = 0.46 * plate_min
    platform_r = 0.30 * plate_min
    sink_depth = max(1.0, 0.85 * plate_t)
    kingpin_d = max(3.0, 0.30 * upper_race_d)
    return {
        "crown_sphere_r": crown_sphere_r,
        "transition_outer_r": transition_outer_r,
        "platform_r": platform_r,
        "sink_depth": sink_depth,
        "kingpin_d": kingpin_d,
        "plate_t": plate_t,
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
    }


def build_mounting_plate(
    wheel_d,
    wheel_width,
    axle_d,
    overall_h,
    plate_l,
    plate_w,
    mount_slot_w,
    mount_pitch_x,
    mount_pitch_y,
    sheet_scale,
    race_scale,
    slot_scale,
):
    """Build a drawn thin-sheet mounting plate and upper race envelope."""
    g = _derived_geometry(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        mount_slot_w,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    plate_t = g["plate_t"]
    flange_top = overall_h
    flange_bottom = flange_top - plate_t
    platform_top = flange_top - g["sink_depth"]
    platform_bottom = platform_top - plate_t

    # Flat outer flange with its centre removed for the annular draw.
    flange = (
        cq.Workplane("XY")
        .workplane(offset=flange_bottom)
        .box(plate_l, plate_w, plate_t, centered=(True, True, False))
    )
    flange_relief = (
        cq.Workplane("XY")
        .workplane(offset=flange_bottom - 0.1)
        .circle(g["transition_outer_r"])
        .extrude(plate_t + 0.2)
    )
    flange = flange.cut(flange_relief)

    # Use corresponding upper/lower splines rather than a straight conical
    # section. Both meet the platform and flange with horizontal tangents; the
    # lower controls are the upper controls shifted down by exactly plate_t.
    # The radial coordinates increase monotonically, so the closed section
    # cannot fold back across itself.
    # Small radial overlaps make both boolean joins robust; they lie under the
    # adjacent horizontal sheets and do not change the visible draw envelope.
    transition_inner_r = g["platform_r"] - 0.05
    transition_outer_r = g["transition_outer_r"] + 0.05
    transition_span = transition_outer_r - transition_inner_r
    upper_inner = (transition_inner_r, platform_top)
    upper_outer = (transition_outer_r, flange_top)
    lower_inner = (upper_inner[0], upper_inner[1] - plate_t)
    lower_outer = (upper_outer[0], upper_outer[1] - plate_t)
    transition = (
        cq.Workplane("XZ")
        .moveTo(*lower_inner)
        .lineTo(*upper_inner)
        .spline(
            [upper_outer],
            tangents=((transition_span, 0.0), (transition_span, 0.0)),
            includeCurrent=True,
            scale=False,
        )
        .lineTo(*lower_outer)
        .spline(
            [lower_inner],
            tangents=((-transition_span, 0.0), (-transition_span, 0.0)),
            includeCurrent=True,
            scale=False,
        )
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )
    platform = (
        cq.Workplane("XY")
        .workplane(offset=platform_bottom)
        .circle(g["platform_r"] + 0.05)
        .extrude(plate_t)
    )
    plate = flange.union(transition).union(platform)

    # d2 is exact catalog slot width; length and radial orientation are the
    # documented proportions used to complete the unpublished capsule shape.
    for x in (-mount_pitch_x / 2.0, mount_pitch_x / 2.0):
        for y in (-mount_pitch_y / 2.0, mount_pitch_y / 2.0):
            angle = math.degrees(math.atan2(y, x))
            slot = (
                cq.Workplane("XY")
                .workplane(offset=platform_bottom - 0.5)
                .center(x, y)
                .slot2D(g["slot_l"], g["slot_w"], angle)
                .extrude(g["sink_depth"] + plate_t + 1.0)
            )
            plate = plate.cut(slot)

    upper_race = (
        cq.Workplane("XY")
        .workplane(offset=platform_bottom - g["upper_race_h"])
        .circle(g["upper_race_d"] / 2.0)
        .extrude(g["upper_race_h"] + 0.05)
    )
    plate = plate.union(upper_race)
    kingpin = (
        cq.Workplane("XY")
        .workplane(offset=platform_bottom - g["upper_race_h"] - 0.5)
        .circle(g["kingpin_d"] / 2.0)
        .extrude(g["upper_race_h"] + g["sink_depth"] + plate_t + 1.0)
    )
    return plate.cut(kingpin)


def build_swivel_fork(
    wheel_d,
    wheel_width,
    axle_d,
    overall_h,
    plate_l,
    plate_w,
    mount_slot_w,
    swivel_offset,
    sheet_scale,
    race_scale,
    slot_scale,
):
    """Build the lower race, bridge, and translated copies of one fork leg."""
    g = _derived_geometry(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        mount_slot_w,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    axle_z = wheel_d / 2.0
    platform_bottom = overall_h - g["sink_depth"] - g["plate_t"]
    lower_top = platform_bottom - g["upper_race_h"] - _AXIAL_CLEARANCE
    lower_bottom = lower_top - g["lower_race_h"]

    lower_race = (
        cq.Workplane("XY")
        .workplane(offset=lower_bottom)
        .circle(g["lower_race_d"] / 2.0)
        .extrude(g["lower_race_h"])
    )
    bridge_top_overlap = 0.30
    bridge = (
        cq.Workplane("XY")
        .workplane(offset=lower_bottom - g["bridge_t"] + bridge_top_overlap)
        .box(
            0.80 * g["lower_race_d"],
            g["yoke_outer_w"],
            g["bridge_t"],
            centered=(True, True, False),
        )
    )

    leg_top_z = lower_bottom + 0.15
    lug_r = 0.95 * axle_d
    top_inner_x = -0.30 * g["lower_race_d"]
    top_outer_x = 0.34 * g["lower_race_d"]
    inner_knee_z = axle_z + 2.2 * lug_r

    # One closed, non-self-intersecting side master. The outer spline is
    # tangent to the wide top and to the circular axle ear at its top point.
    centered_leg = (
        cq.Workplane("XZ")
        .moveTo(top_inner_x, leg_top_z)
        .lineTo(top_outer_x, leg_top_z)
        .spline(
            [
                (top_outer_x + 0.20 * g["lower_race_d"], leg_top_z),
                (swivel_offset - 1.2 * lug_r, axle_z + 2.0 * lug_r),
                (swivel_offset, axle_z + lug_r),
            ],
            tangents=((1.0, 0.0), (1.0, 0.0)),
            includeCurrent=True,
        )
        .lineTo(swivel_offset, axle_z)
        .lineTo(top_inner_x + 0.08 * g["lower_race_d"], inner_knee_z)
        .close()
        .extrude(g["fork_t"] / 2.0, both=True)
    )
    lug = (
        cq.Workplane("XZ")
        .center(swivel_offset, axle_z)
        .circle(lug_r)
        .extrude(g["fork_t"] / 2.0, both=True)
    )
    leg_master = centered_leg.union(lug)

    # No mirroring or re-sketching: both plates are identical and differ only
    # by equal and opposite translations along the wheel-axis Y direction.
    leg_y = wheel_width / 2.0 + g["side_clearance"] + g["fork_t"] / 2.0
    negative_y_leg = leg_master.translate((0.0, -leg_y, 0.0))
    positive_y_leg = leg_master.translate((0.0, leg_y, 0.0))
    fork = lower_race.union(bridge).union(negative_y_leg).union(positive_y_leg)

    axle_hole = cq.Solid.makeCylinder(
        axle_d / 2.0 + _RADIAL_CLEARANCE,
        g["yoke_outer_w"] + 2.0,
        cq.Vector(swivel_offset, -g["yoke_outer_w"] / 2.0 - 1.0, axle_z),
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
    mount_slot_w,
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
        mount_slot_w,
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
    crown = cq.Solid.makeSphere(
        g["crown_sphere_r"],
        cq.Vector(swivel_offset, 0.0, axle_z),
        cq.Vector(0.0, 1.0, 0.0),
        -90.0,
        90.0,
        360.0,
    )
    wheel = wheel.intersect(cq.Workplane("XY").newObject([crown]))

    recess_depth = min(1.5, 0.10 * wheel_width)
    recess_outer_r = 0.34 * wheel_d
    hub_r = 0.18 * wheel_d
    for y, direction in (
        (-wheel_width / 2.0 - 0.05, cq.Vector(0.0, 1.0, 0.0)),
        (wheel_width / 2.0 + 0.05, cq.Vector(0.0, -1.0, 0.0)),
    ):
        outer = cq.Solid.makeCylinder(
            recess_outer_r,
            recess_depth + 0.05,
            cq.Vector(swivel_offset, y, axle_z),
            direction,
        )
        inner = cq.Solid.makeCylinder(
            hub_r,
            recess_depth + 0.05,
            cq.Vector(swivel_offset, y, axle_z),
            direction,
        )
        wheel = wheel.cut(cq.Workplane("XY").newObject([outer.cut(inner)]))

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
    mount_slot_w,
    swivel_offset,
    sheet_scale,
    race_scale,
    slot_scale,
):
    """Build a proportioned hex-head axle-bolt envelope."""
    g = _derived_geometry(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        mount_slot_w,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    axle_z = wheel_d / 2.0
    f = _fastener(axle_d)
    yoke_half = g["yoke_outer_w"] / 2.0
    y_head_face = -(yoke_half + _AXIAL_CLEARANCE)
    y_nut_face = yoke_half + _AXIAL_CLEARANCE
    y_end = y_nut_face + f["m"] + 0.35 * axle_d

    head = _hex_prism(
        f["s"], f["k"], cq.Vector(swivel_offset, y_head_face, axle_z)
    ).translate((0.0, -f["k"], 0.0))
    shank = cq.Workplane("XY").newObject(
        [
            cq.Solid.makeCylinder(
                axle_d / 2.0,
                y_end - y_head_face,
                cq.Vector(swivel_offset, y_head_face, axle_z),
                cq.Vector(0.0, 1.0, 0.0),
            )
        ]
    )
    return head.union(shank)


def build_axle_nut(
    wheel_d,
    wheel_width,
    axle_d,
    overall_h,
    plate_l,
    plate_w,
    mount_slot_w,
    swivel_offset,
    sheet_scale,
    race_scale,
    slot_scale,
):
    """Build a proportioned hex nut on the axle-bolt envelope."""
    g = _derived_geometry(
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        mount_slot_w,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    axle_z = wheel_d / 2.0
    f = _fastener(axle_d)
    y_nut_face = g["yoke_outer_w"] / 2.0 + _AXIAL_CLEARANCE
    nut = _hex_prism(
        f["s"], f["m"], cq.Vector(swivel_offset, y_nut_face, axle_z)
    )
    bore = cq.Solid.makeCylinder(
        axle_d / 2.0 + _RADIAL_CLEARANCE,
        f["m"] + 2.0,
        cq.Vector(swivel_offset, y_nut_face - 1.0, axle_z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    return nut.cut(cq.Workplane("XY").newObject([bore]))


def build(
    catalog_size,
    wheel_d,
    wheel_width,
    axle_d,
    mount_slot_w,
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
    """Build the named five-component Form L caster assembly."""
    _ = catalog_size
    common = (
        wheel_d,
        wheel_width,
        axle_d,
        overall_h,
        plate_l,
        plate_w,
        mount_slot_w,
    )
    mounting_plate = build_mounting_plate(
        *common,
        mount_pitch_x,
        mount_pitch_y,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    pose_args = (
        *common,
        swivel_offset,
        sheet_scale,
        race_scale,
        slot_scale,
    )
    swivel_fork = build_swivel_fork(*pose_args)
    wheel = build_wheel(*pose_args)
    axle_bolt = build_axle_fastener(*pose_args)
    axle_nut = build_axle_nut(*pose_args)

    result = cq.Assembly(name="light_duty_swivel_plate_caster")
    result.add(mounting_plate, name="mounting_plate")
    result.add(swivel_fork, name="swivel_fork")
    result.add(wheel, name="wheel")
    result.add(axle_bolt, name="axle_bolt")
    result.add(axle_nut, name="axle_nut")
    return result
