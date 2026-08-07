"""Four-component JW Winco EN 22870 Form L caster assembly."""

import math

import cadquery as cq


_RADIAL_CLEARANCE = 0.20
_AXIAL_CLEARANCE = 0.25

# The axle is a hex-head bolt and nut on the product photo, and the catalog
# gives its nominal size as d2, so the fastener is a standard part rather than
# a proportion: ISO 4014 hex head (width across flats s, head height k),
# ISO 4032 hex nut (height m), ISO 261 coarse pitch. Keyed by d2, which the
# EN 22870 Form L rows publish as 5 mm (size 40) and 6 mm (sizes 50/60/80).
_HEX_FASTENER = {
    5.0: {"s": 8.0, "k": 3.5, "m": 4.7, "pitch": 0.8},
    6.0: {"s": 10.0, "k": 4.0, "m": 5.2, "pitch": 1.0},
    8.0: {"s": 13.0, "k": 5.3, "m": 6.8, "pitch": 1.25},
}


def _fastener(axle_d):
    """ISO 4014/4032 dimensions for the catalog axle size.

    Only the sizes EN 22870 Form L actually publishes are tabulated. Anything
    else is out of catalog, so it falls back to declared proportions rather
    than inventing a standard row.
    """
    key = min(_HEX_FASTENER, key=lambda k: abs(k - axle_d))
    if abs(key - axle_d) < 1e-6:
        return dict(_HEX_FASTENER[key], standard=True)
    return {
        "s": 1.70 * axle_d,
        "k": 0.68 * axle_d,
        "m": 0.85 * axle_d,
        "pitch": 0.15 * axle_d,
        "standard": False,
    }


def _hex_prism(across_flats, length, origin):
    """Hex bar of the given width across flats, along +Y from origin."""
    circum_r = across_flats / math.sqrt(3.0)  # s = 2 * r_circum * cos(30 deg)
    return (
        cq.Workplane("XZ", origin=(origin.x, origin.y, origin.z))
        .polygon(6, 2.0 * circum_r)
        .extrude(-length)
    )


def _thread_rings(y0, y1, pitch, r_root, r_crest, centre_x, centre_z, phase=0.0):
    """Axisymmetric ring stack standing in for a helical thread.

    One annular ring of axial width 0.4*pitch every pitch. The repo models
    threads this way rather than with makeHelix, which silently no-ops on
    scattered size/geometry combinations in the pinned cadquery/OCP.
    """
    rings = None
    y = y0 + phase
    while y + 0.4 * pitch <= y1:
        outer = cq.Solid.makeCylinder(
            r_crest, 0.4 * pitch, cq.Vector(centre_x, y, centre_z),
            cq.Vector(0.0, 1.0, 0.0))
        inner = cq.Solid.makeCylinder(
            r_root, 0.4 * pitch + 0.2, cq.Vector(centre_x, y - 0.1, centre_z),
            cq.Vector(0.0, 1.0, 0.0))
        ring = cq.Workplane("XY").newObject([outer.cut(inner)])
        rings = ring if rings is None else rings.union(ring)
        y += pitch
    return rings


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
    # Tread shoulder. The catalog publishes d1 and b but no section, so the
    # shoulder is a proportion: a sphere through the shoulder radius rolls the
    # tread off tangentially instead of cutting a fillet into a square corner.
    # drop_max is where that sphere degenerates to the wheel radius itself;
    # staying at 3/4 of it keeps every catalog row well inside that limit.
    wheel_r = wheel_d / 2.0
    half_b = wheel_width / 2.0
    drop_max = wheel_r - math.sqrt(max(wheel_r * wheel_r - half_b * half_b, 0.0))
    crown_drop = min(0.045 * wheel_d, 0.75 * drop_max)
    crown_sphere_r = math.sqrt((wheel_r - crown_drop) ** 2 + half_b * half_b)
    # Drawn seat + kingpin hole in the plate, both proportions (unpublished).
    seat_d = 0.92 * upper_race_d
    seat_depth = min(0.45 * plate_t, 0.9)
    kingpin_d = max(3.0, 0.30 * upper_race_d)
    return {
        "crown_drop": crown_drop,
        "crown_sphere_r": crown_sphere_r,
        "seat_d": seat_d,
        "seat_depth": seat_depth,
        "kingpin_d": kingpin_d,
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
    plate = plate.union(upper_race)

    # The plate is a pressing, not a flat sheet: the product photo shows a
    # drawn circular seat around the swivel axis with the kingpin hole through
    # its floor. Neither is published, so both are proportions — and the seat
    # is drawn DOWNWARD so the plate top stays exactly at overall_h.
    seat = (
        cq.Workplane("XY")
        .workplane(offset=overall_h - g["seat_depth"])
        .circle(g["seat_d"] / 2.0)
        .extrude(g["seat_depth"] + 0.5)
    )
    kingpin = (
        cq.Workplane("XY")
        .workplane(offset=plate_bottom - g["upper_race_h"] - 0.5)
        .circle(g["kingpin_d"] / 2.0)
        .extrude(g["upper_race_h"] + plate_t + 1.0)
    )
    return plate.cut(seat).cut(kingpin)


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
    # The leg stops at the axle centre line and is closed by a round lug
    # concentric with the axle, the way the pressed leg ends on the product
    # photo — not the square corner the straight polyline left below the bore.
    lug_r = 0.95 * axle_d
    leg_profile = [
        (-0.28 * g["lower_race_d"], leg_top_z),
        (0.32 * g["lower_race_d"], leg_top_z),
        (swivel_offset + lug_r, axle_z + 0.95 * axle_d),
        (swivel_offset + lug_r, axle_z),
        (swivel_offset - lug_r, axle_z),
    ]
    centered_leg = (
        cq.Workplane("XZ")
        .polyline(leg_profile)
        .close()
        .extrude(g["fork_t"] / 2.0, both=True)
    )
    lug = (
        cq.Workplane("XZ")
        .center(swivel_offset, axle_z)
        .circle(lug_r)
        .extrude(g["fork_t"] / 2.0, both=True)
    )
    centered_leg = centered_leg.union(lug)
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
    # Shoulder the tread: intersecting the full-diameter cylinder with a sphere
    # centred on the wheel keeps d1 across the middle of the band and then
    # rolls the radius off tangentially to the shoulders, which is the rubber
    # tyre section on the product photo. It replaces a constant-radius fillet
    # on a square corner with one continuous surface. The flat side faces
    # survive inside the shoulder radius, so the side recesses below still
    # read as the wheel core.
    crown = cq.Solid.makeSphere(
        g["crown_sphere_r"],
        cq.Vector(swivel_offset, 0.0, axle_z),
        cq.Vector(0.0, 1.0, 0.0),
        -90.0,
        90.0,
        360.0,
    )
    wheel = wheel.intersect(cq.Workplane("XY").newObject([crown]))

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
    """Build the ISO 4014 hex-head bolt: head, shank, and thread rings."""
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
    f = _fastener(axle_d)
    yoke_half = g["yoke_outer_w"] / 2.0
    gap = _AXIAL_CLEARANCE

    y_head_face = -(yoke_half + gap)          # head bears on the near leg
    y_nut_face = yoke_half + gap              # nut bears on the far leg
    y_end = y_nut_face + f["m"] + 0.35 * axle_d   # shank stands proud of the nut

    head = _hex_prism(
        f["s"], f["k"],
        cq.Vector(swivel_offset, y_head_face, axle_z),
    ).translate((0.0, -f["k"], 0.0))
    # ISO 4014 is partly threaded; the run length is not a catalog value, so
    # where the thread starts is a proportion — just inboard of the nut face.
    # The core is turned down to the minor diameter over that length, the way
    # a real thread is cut into the shank, and the rings below add the crests.
    # Leaving it at full d2 would have the nut's crests bite into the shank.
    y_thread0 = y_nut_face - 1.0
    r_minor = axle_d / 2.0 - 0.61 * f["pitch"]
    plain = cq.Workplane("XY").newObject([
        cq.Solid.makeCylinder(
            axle_d / 2.0,
            y_thread0 - y_head_face,
            cq.Vector(swivel_offset, y_head_face, axle_z),
            cq.Vector(0.0, 1.0, 0.0),
        )
    ])
    core = cq.Workplane("XY").newObject([
        cq.Solid.makeCylinder(
            r_minor,
            y_end - y_thread0,
            cq.Vector(swivel_offset, y_thread0, axle_z),
            cq.Vector(0.0, 1.0, 0.0),
        )
    ])
    bolt = head.union(plain).union(core)

    ext = _thread_rings(
        y_thread0, y_end, f["pitch"],
        r_minor - 0.01, axle_d / 2.0, swivel_offset, axle_z,
    )
    if ext is not None:
        bolt = bolt.union(ext)
    return bolt


def build_axle_nut(
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
    """Build the ISO 4032 hex nut on the threaded end of the axle bolt."""
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
    f = _fastener(axle_d)
    y_nut_face = g["yoke_outer_w"] / 2.0 + _AXIAL_CLEARANCE

    nut = _hex_prism(
        f["s"], f["m"],
        cq.Vector(swivel_offset, y_nut_face, axle_z),
    )
    r_bore = axle_d / 2.0 + 0.35 * f["pitch"]
    nut = nut.cut(
        cq.Workplane("XY").newObject([
            cq.Solid.makeCylinder(
                r_bore, f["m"] + 2.0,
                cq.Vector(swivel_offset, y_nut_face - 1.0, axle_z),
                cq.Vector(0.0, 1.0, 0.0),
            )
        ])
    )
    # The nut's internal rings sit on the same axial grid as the bolt's, offset
    # half a pitch, so the pair reads as engaged and still measures zero
    # intersection volume.
    inr = _thread_rings(
        y_nut_face, y_nut_face + f["m"], f["pitch"],
        axle_d / 2.0 - 0.25 * f["pitch"], r_bore + 0.01,
        swivel_offset, axle_z, phase=0.5 * f["pitch"],
    )
    if inr is not None:
        nut = nut.union(inr)
    return nut


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
    axle_bolt = build_axle_fastener(
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

    axle_nut = build_axle_nut(
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
    result.add(axle_bolt, name="axle_bolt")
    result.add(axle_nut, name="axle_nut")
    return result
