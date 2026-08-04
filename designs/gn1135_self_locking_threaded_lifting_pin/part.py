"""Parametric Ganter GN 1135 self-locking threaded lifting pin.

The public drawing controls every visible catalogue dimension.  The internal
actuator, spring, and two-segment decomposition are documented proportions
because Ganter does not publish their manufacturing geometry.
"""

import cadquery as cq


def _wp(shape):
    return cq.Workplane("XY").newObject([shape])


def _cyl_z(diameter, height, start_z, x=0.0, y=0.0):
    return _wp(cq.Solid.makeCylinder(
        diameter / 2.0, height,
        cq.Vector(x, y, start_z), cq.Vector(0.0, 0.0, 1.0)))


def _cyl_x(diameter, length, start_x, y=0.0, z=0.0):
    return _wp(cq.Solid.makeCylinder(
        diameter / 2.0, length,
        cq.Vector(start_x, y, z), cq.Vector(1.0, 0.0, 0.0)))


def _cone_x(bottom_d, top_d, length, start_x, y=0.0, z=0.0):
    return _wp(cq.Solid.makeCone(
        bottom_d / 2.0, top_d / 2.0, length,
        cq.Vector(start_x, y, z), cq.Vector(1.0, 0.0, 0.0)))


def _cone_z(bottom_d, top_d, height, start_z):
    return _wp(cq.Solid.makeCone(
        bottom_d / 2.0, top_d / 2.0, height,
        cq.Vector(0.0, 0.0, start_z), cq.Vector(0.0, 0.0, 1.0)))


def _box(x, y, z, center):
    return cq.Workplane("XY").box(x, y, z).translate(center)


def _rotz(shape, angle):
    return shape.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)


def _main_body(d1, d2, d3, d5, h2, h3, l1, l2, l3, k1):
    """Stationary pin body with real slots for the moving segments."""
    tip_chamfer = min(0.5, 0.12 * d2)
    tip = _cone_z(d2 - 2.0 * tip_chamfer, d2, tip_chamfer, -l2)
    lower_pin = _cyl_z(d2, l2 - tip_chamfer, -l2 + tip_chamfer)

    collar_start = 0.514 * h3
    lower_body = _cyl_z(d3, collar_start, 0.0)
    # The M8 STEP's upper post is d13.0 inside the d33.5 guard, i.e. 0.65*d3.
    post_d = 0.65 * d3
    post = _cyl_z(post_d, h2 - collar_start, collar_start)
    body = tip.union(lower_pin).union(lower_body).union(post)

    # A small central actuator passage continues down the pin.  The larger
    # upper counterbore houses the simplified return spring.
    rod_d = max(2.0, 0.22 * d3)
    spring_od = 0.48 * d3
    body = body.cut(_cyl_z(
        rod_d + 0.5, h2 + l2 - 1.0, -l2 + 1.0))
    # Start the pocket just below the first spring turn.  The helix has a
    # small lower lead-in below its nominal z=2 mm seat; leaving that lead
    # inside the pocket avoids fusing the spring to the body while retaining
    # the lower wall around the actuator passage.
    spring_pocket_start = 0.7
    body = body.cut(_cyl_z(
        spring_od + 0.6, collar_start + 0.4 - spring_pocket_start,
        spring_pocket_start))

    # A counterbore lets the push-button cap sit inside the upper post rather
    # than occupying the same material as the stationary body.
    button_cap_d = 0.39 * d5
    body = body.cut(_cyl_z(
        button_cap_d + 0.3, h2 - collar_start + 0.4,
        collar_start - 0.2))

    # The transverse pivot passes through a real clearance bore in the
    # stationary post.  The official M8 STEP exposes a roughly 10 mm bore at
    # h3; keep the same clearance around the simplified pivot shaft.
    pivot_d = max(4.0, 0.47 * k1 + 5.0)
    body = body.cut(_cyl_x(
        pivot_d + 0.3, d3 + 2.0, -0.5 * d3 - 1.0, 0.0, h3))

    # Opposed longitudinal slots retain separate threaded-segment solids.
    segment_width = 0.38 * d1
    slot_inner = max(0.42 * (d2 / 2.0), rod_d / 2.0 + 0.35)
    slot_depth = d1 / 2.0 - slot_inner + 0.7
    segment_z = -l1
    for side in (-1.0, 1.0):
        body = body.cut(_box(
            slot_depth, segment_width + 0.25, l3 + 0.2,
            (side * (slot_inner + slot_depth / 2.0), 0.0,
             segment_z + l3 / 2.0)))
    return body


def _rotating_collar(d3, d4, h2, h3, k1):
    """Rotating head around the stationary central post."""
    start_z = 0.514 * h3
    end_z = min(h2 - 0.5 * k1, 1.486 * h3)
    collar = _cyl_z(d4, end_z - start_z, start_z)
    collar = collar.cut(_cyl_z(
        0.68 * d3 + 0.35, end_z - start_z + 0.4, start_z - 0.2))
    pivot_d = max(4.0, 0.47 * k1 + 5.0)
    collar = collar.cut(_cyl_x(
        pivot_d + 0.35, d4 + 2.0, -d4 / 2.0 - 1.0, 0.0, h3))
    return collar


def _safety_guard(d3, d5, h2, h3):
    """Six-flat d5 guard ring surrounding the exposed push button."""
    start_z = 1.486 * h3
    height = max(2.0, h2 - start_z)
    transition = min(0.045 * d5, 0.22 * height)
    middle_start = start_z + transition
    middle_height = height - 2.0 * transition

    # The STEP section is a d5 cylinder clipped by six flats at roughly
    # 95.5 percent of d5 across flats, rather than a knurled round ring.
    cylinder = _cyl_z(d5, middle_height, middle_start)
    hex_diameter = 0.955 * d5 / 0.8660254
    hex_prism = (
        cq.Workplane("XY")
        .polygon(6, hex_diameter)
        .extrude(middle_height)
        .translate((0.0, 0.0, middle_start))
    )
    middle = cylinder.intersect(hex_prism)
    lower = _cone_z(1.135 * d5, d5, transition, start_z)
    upper = _cone_z(d5, 0.91 * d5, transition, h2 - transition)
    guard = lower.union(middle).union(upper)


    # On the largest catalog row the stationary post grows faster than the
    # nominal guard bore.  Preserve a small running clearance around that post
    # so the guard remains a separate rotating solid for every row.
    inner_d = max(0.40 * d5, 0.65 * d3 + 0.6)
    guard = guard.cut(_cyl_z(
        inner_d, height + 0.4, start_z - 0.2))
    return guard


def _shackle(h1, h2, h3, h4, k1, k2, k3, d4):
    """Forged eye and pivot bosses sampled from the official M8 STEP."""
    section_y = -k1 / 2.0
    outer_x_scale = k2 / 68.0
    inner_top = h1 - (123.7 - 109.7) * (k1 / 11.0)
    inner_bottom = inner_top - h4

    def inner_point(x, z):
        return cq.Vector(
            x * k3 / 46.0,
            section_y,
            inner_bottom + (z - 67.2) * h4 / 42.5,
        )

    def mirror(points):
        return [(-x, z) for x, z in points]

    # This is the broad upper-loop outline from the M8 STEP's centre section.
    # The lower stepped pivot details are reconstructed separately below,
    # because they are smaller than the forged edge round-over on the eye.
    outer_long = [
        (0.0, 123.7), (8.797, 123.688), (17.351, 122.527),
        (22.689, 115.58), (27.739, 108.376), (32.773, 101.162),
        (33.993, 92.623), (34.0, 83.826), (33.973, 75.029),
        (32.322, 66.42), (29.348, 58.142), (28.997, 49.376),
        (28.998, 40.578),
    ]
    inner_upper = [
        (0.0, 109.7), (2.998, 109.508), (5.944, 108.925),
        (8.788, 107.959), (11.481, 106.63), (13.977, 104.959),
        (16.234, 102.977), (18.219, 100.723), (19.898, 98.232),
        (21.236, 95.543), (22.208, 92.701), (22.798, 89.756),
        (23.0, 86.76), (22.911, 83.756), (22.646, 80.762),
        (22.2, 77.79), (21.579, 74.85),
    ]
    inner_lower = [
        (21.579, 74.85), (21.055, 73.269), (20.275, 71.798),
        (19.262, 70.477), (18.044, 69.342), (16.654, 68.425),
        (15.132, 67.751), (13.519, 67.339), (11.859, 67.2),
    ]
    # The upper eye uses the smooth broad sections from the same STEP outline,
    # but keeps only the large curves so its k1 face round-over remains stable.
    ring_x_scale = k2 / 68.0
    ring_z_scale = (h1 - h3) / (123.7 - 25.7)

    def ring_point(x, z):
        lower_lug_offset = 0.0
        if ring_x_scale > 1.01 and z < 65.0:
            lower_lug_offset = 3.0 * min(1.0, (65.0 - z) / 25.0)
        if x > 0.0:
            x_offset = lower_lug_offset
        elif x < 0.0:
            x_offset = -lower_lug_offset
        else:
            x_offset = 0.0
        return cq.Vector(
            x * ring_x_scale + x_offset,
            section_y,
            h3 + (z - 25.7) * ring_z_scale,
        )

    # Keep the forged neck just outside the rotating-head envelope.  The
    # measured 19.15 mm shoulder anchors the M8 section; the catalog's M20
    # head grows faster than the eye scale, so the larger row uses a wider
    # proportioned neck plus a d4-derived running-clearance floor.
    ring_neck_floor = 24.0 if ring_x_scale <= 1.01 else 29.0
    ring_neck = max(ring_neck_floor, d4 / (2.0 * ring_x_scale) + 0.2)
    ring_neck_low = h3 + (36.685 - 25.7) * ring_z_scale
    ring_neck_high = h3 + (49.7 - 25.7) * ring_z_scale
    ring_bridge = 9.5 * ring_x_scale
    ring_bridge_z = h3 + (59.7 - 25.7) * ring_z_scale
    ring_left_path = mirror(list(reversed(outer_long)))
    ring_right_path = list(reversed(outer_long))
    ring_outer_wire = cq.Wire.assembleEdges([
        cq.Edge.makeSpline(
            [cq.Vector(-ring_neck, section_y, ring_neck_low)] + [
                ring_point(x, z) for x, z in ring_left_path]),
        cq.Edge.makeSpline(
            [ring_point(x, z) for x, z in reversed(ring_right_path)]),
        # This is the forged outside transition into the pivot ear.  A direct
        # chord here creates a visible diagonal ridge; its control points
        # follow the adjoining M8 section samples (40.578 -> 36.327 -> 34.2)
        # before blending into the measured 19.5 mm neck.
        cq.Edge.makeThreePointArc(
            ring_point(28.998, 40.578),
            ring_point(31.65, 34.2 + (1.0 if ring_x_scale > 1.01 else 0.0)),
            cq.Vector(ring_neck, section_y, ring_neck_low)),
        cq.Edge.makeLine(
            cq.Vector(ring_neck, section_y, ring_neck_low),
            cq.Vector(ring_neck, section_y, ring_neck_high)),
        cq.Edge.makeSpline([
            cq.Vector(ring_neck, section_y, ring_neck_high),
            cq.Vector(ring_bridge, section_y, ring_bridge_z),
            cq.Vector(-ring_bridge, section_y, ring_bridge_z),
            cq.Vector(-ring_neck, section_y, ring_neck_high),
        ]),
        cq.Edge.makeLine(
            cq.Vector(-ring_neck, section_y, ring_neck_high),
            cq.Vector(-ring_neck, section_y, ring_neck_low)),
    ])
    ring_right_inner = inner_upper + inner_lower[1:]
    ring_left_inner = [(-x, z) for x, z in reversed(ring_right_inner)]
    ring_inner_wire = cq.Wire.assembleEdges([
        cq.Edge.makeSpline([inner_point(x, z) for x, z in ring_right_inner]),
        cq.Edge.makeLine(
            inner_point(ring_right_inner[-1][0], ring_right_inner[-1][1]),
            inner_point(ring_left_inner[0][0], ring_left_inner[0][1])),
        cq.Edge.makeSpline([inner_point(x, z) for x, z in ring_left_inner]),
    ])
    rounded_eye = _wp(cq.Solid.extrudeLinear(
        ring_outer_wire, [ring_inner_wire], cq.Vector(0.0, k1, 0.0)))
    profile_edge_selector = cq.selectors.InverseSelector(
        cq.selectors.ParallelDirSelector(cq.Vector(0.0, 1.0, 0.0)))
    eye_fillet = (min(0.18 * k1, 2.0)
                  if ring_x_scale <= 1.01 else min(0.12 * k1, 1.2))
    rounded_eye = rounded_eye.edges(profile_edge_selector).fillet(eye_fillet)

    # In side view the official forging is not an equal-thickness strip at the
    # top: its half-thickness stays 5.5 mm to y=109.7, then reduces to
    # 1.681 mm at y=123.7.  Apply the measured taper after the broad-face
    # round-over so an edge-on eye finishes in the same narrow point.
    taper_start_z = h3 + (109.7 - 25.7) * ring_z_scale
    taper_hold_z = h3 + (111.0 - 25.7) * ring_z_scale
    taper_mid_z = h3 + (115.58 - 25.7) * ring_z_scale
    taper_mid_half = 0.8736 * (k1 / 2.0)
    taper_end_half = 0.3056 * (k1 / 2.0)
    cut_extent = k2 + 4.0
    positive_taper_cut = (
        cq.Workplane("YZ")
        .moveTo(k1 / 2.0, taper_start_z)
        .lineTo(k1 / 2.0 + 1.0, taper_start_z)
        .lineTo(k1 / 2.0 + 1.0, h1 + 1.0)
        .lineTo(taper_end_half, h1)
        .spline(
            [
                (taper_mid_half, taper_mid_z),
                (k1 / 2.0, taper_hold_z),
                (k1 / 2.0, taper_start_z),
            ],
            includeCurrent=True)
        .close()
        .extrude(cut_extent / 2.0, both=True)
    )
    negative_taper_cut = (
        cq.Workplane("YZ")
        .moveTo(-k1 / 2.0, taper_start_z)
        .lineTo(-k1 / 2.0 - 1.0, taper_start_z)
        .lineTo(-k1 / 2.0 - 1.0, h1 + 1.0)
        .lineTo(-taper_end_half, h1)
        .spline(
            [
                (-taper_mid_half, taper_mid_z),
                (-k1 / 2.0, taper_hold_z),
                (-k1 / 2.0, taper_start_z),
            ],
            includeCurrent=True)
        .close()
        .extrude(cut_extent / 2.0, both=True)
    )
    rounded_eye = rounded_eye.cut(positive_taper_cut).cut(negative_taper_cut)
    # The long loop already reaches the stepped cylinders through its forged
    # neck.  Retaining the cut plate here would expose a flat, artificial
    # cheek in the iso-B view, so the measured pivot details below form the
    # lower continuation instead.
    shackle = rounded_eye

    # The STEP centre section retains one short square stop at the inboard end
    # of each pivot arm.  It spans x=19.15..22.15 and z=30.85..36.685 on the
    # M8 part.  Keeping this local prism preserves the visible iso-B shoulder
    # without bringing back the broad flat cheek that formerly crossed the
    # whole arm.
    stop_start = max(19.15 * outer_x_scale, d4 / 2.0 + 0.4)
    stop_length = 3.0 * outer_x_scale
    stop_low = h3 + (30.85 - 25.7) * ring_z_scale
    stop_high = h3 + (36.685 - 25.7) * ring_z_scale
    stop_height = stop_high - stop_low
    right_stop = _box(
        stop_length, k1, stop_height,
        (stop_start + stop_length / 2.0, 0.0,
         stop_low + stop_height / 2.0))
    left_stop = _box(
        stop_length, k1, stop_height,
        (-stop_start - stop_length / 2.0, 0.0,
         stop_low + stop_height / 2.0))
    shackle = shackle.union(left_stop).union(right_stop)

    # The cylindrical portion of each boss occupies only its measured central
    # span.  The surrounding stepped profile above provides the forged blend.
    lug_radius = 0.3026 * d4
    lug_start = 22.15 * outer_x_scale
    lug_length = 6.50 * outer_x_scale
    right_lug = _cyl_x(2.0 * lug_radius, lug_length, lug_start, 0.0, h3)
    left_lug = _cyl_x(
        2.0 * lug_radius, lug_length, -lug_start - lug_length, 0.0, h3)

    # Both end bosses are stepped: a 17 mm shoulder continues inward from the
    # large cylindrical span and a 13.5 mm land sits at the outer face.  These
    # dimensions come from the same M8 section (17.0 and 13.5 mm) and scale
    # with the published head/eye envelope for the other catalog rows.
    arm_radius = 0.2237 * d4
    arm_start = max(19.15 * outer_x_scale, d4 / 2.0 + 0.3)
    arm_length = 10.0 * outer_x_scale

    # The official eye has planar end cheeks around the round boss: in the
    # section they are a roughly 2*arm_radius square with lightly eased
    # longitudinal corners, not another circular shaft.  Keep the bore and
    # the outer land cylindrical, but make this shoulder a rounded prism.
    arm_edge_radius = min(0.16 * d4, 1.5)

    def arm_prism(start_x):
        arm = _box(
            arm_length, 2.0 * arm_radius, 2.0 * arm_radius,
            (start_x + arm_length / 2.0, 0.0, h3))
        return arm.edges(cq.selectors.ParallelDirSelector(
            cq.Vector(1.0, 0.0, 0.0))).fillet(arm_edge_radius)

    right_arm = arm_prism(arm_start)
    left_arm = arm_prism(-arm_start - arm_length)
    land_radius = 0.1776 * d4
    land_start = 29.15 * outer_x_scale
    land_length = 2.10 * outer_x_scale
    right_land = _cyl_x(2.0 * land_radius, land_length, land_start, 0.0, h3)
    left_land = _cyl_x(
        2.0 * land_radius, land_length, -land_start - land_length, 0.0, h3)
    shackle = (
        shackle
        .union(left_arm)
        .union(right_arm)
        .union(left_lug)
        .union(right_lug)
        .union(left_land)
        .union(right_land)
    )

    # The M20 eye cheek is the only row whose scaled lower transition reaches
    # the d59 head envelope.  A short local relief at that transition keeps
    # the forged cheek clear without changing the catalog outline above it.
    if outer_x_scale > 1.01:
        relief_width = d4 + 1.0
        relief_height = 14.0
        relief_center_z = h3 + 13.0
        shackle = shackle.cut(_box(
            relief_width, 2.0 * d4, relief_height,
            (0.0, 0.0, relief_center_z)))

    pivot_d = max(4.0, 0.468 * k1 + 5.15)
    shackle = shackle.cut(_cyl_x(
        pivot_d + 0.3, k2 + 2.0, -k2 / 2.0 - 1.0, 0.0, h3))

    # The outer 1.7 mm lands around each eye are counterbored for the larger
    # pivot heads.  The official section shows this stepped clearance rather
    # than one constant bore; without it the separate pivot solid intersects
    # the forged lug at each end.
    shaft_d = max(4.0, 0.47 * k1 + 5.0)
    head_t = max(0.8, 0.10 * k1)
    head_d = shaft_d + 0.27 * k1
    counterbore_d = head_d + 0.3
    counterbore_length = head_t + 0.8
    counterbore_end = land_start + land_length + 0.4
    counterbore_start = counterbore_end - counterbore_length
    shackle = shackle.cut(_cyl_x(
        counterbore_d, counterbore_length, counterbore_start, 0.0, h3))
    shackle = shackle.cut(_cyl_x(
        counterbore_d, counterbore_length, -counterbore_end,
        0.0, h3))
    return shackle


def _pivot(k1, k2, h3, d3):
    shaft_d = max(4.0, 0.47 * k1 + 5.0)
    total_length = k2 - 0.50 * k1
    head_t = max(0.8, 0.10 * k1)
    shaft = _cyl_x(shaft_d, total_length - 2.0 * head_t,
                   -total_length / 2.0 + head_t, 0.0, h3)
    head_d = shaft_d + 0.27 * k1
    end_d = head_d - 0.18 * k1
    chamfer_t = min(0.45 * head_t, 0.30 * k1)
    left = _cone_x(end_d, head_d, chamfer_t,
                   -total_length / 2.0, 0.0, h3).union(
        _cyl_x(head_d, head_t - chamfer_t,
               -total_length / 2.0 + chamfer_t, 0.0, h3))
    right = _cyl_x(head_d, head_t - chamfer_t,
                   total_length / 2.0 - head_t, 0.0, h3).union(
        _cone_x(head_d, end_d, chamfer_t,
                total_length / 2.0 - chamfer_t, 0.0, h3))
    pivot = shaft.union(left).union(right)
    # The axial actuator runs through the centre of the transverse pin.  A
    # small radial relief in the pin models that hidden passage and keeps the
    # two independently scored solids from occupying the same material.
    actuator_d = max(2.0, 0.22 * d3)
    relief_d = actuator_d + 0.6
    relief_h = head_d + 0.6
    pivot = pivot.cut(_cyl_z(
        relief_d, relief_h, h3 - relief_h / 2.0))
    return pivot


def _button(d3, d5, h2, l1, l3, released):
    travel = 0.09 * d5 if released else 0.0
    rod_d = max(2.0, 0.22 * d3)
    cap_d = 0.39 * d5
    cap_h = max(1.8, 0.093 * d5)
    dome_h = max(0.8, 0.040 * d5)
    rod_bottom = -l1 + 0.5 * l3
    cap_start = h2 - cap_h - travel
    rod_top = cap_start + 0.2
    rod = _cyl_z(rod_d, rod_top - rod_bottom, rod_bottom)
    cap = _cyl_z(cap_d, cap_h, cap_start)
    dome = _cone_z(cap_d, 0.64 * cap_d, dome_h, h2 - travel)
    return rod.union(cap).union(dome)


def _spring(d3, h3, d5, released):
    """Simplified but genuinely helical return spring (proportion)."""
    outer_d = 0.48 * d3
    wire_d = max(0.65, 0.055 * d5)
    free_height = max(4.0, 0.36 * h3)
    compression = 0.09 * d5 if released else 0.0
    height = max(2.5 * wire_d, free_height - compression)
    turns = 5.0
    pitch = height / turns
    radius = (outer_d - wire_d) / 2.0
    path = cq.Wire.makeHelix(pitch, height, radius)
    profile = cq.Workplane("XZ").center(radius, 0.0).circle(wire_d / 2.0)
    spring = profile.sweep(cq.Workplane(obj=path), isFrenet=True)
    return spring.translate((0.0, 0.0, 2.0))


def _thread_segment(d1, d2, d3, l1, l3, side, released):
    """One opposed retracting segment with parallel visual thread lands."""
    core_r = d2 / 2.0
    rod_d = max(2.0, 0.22 * d3)
    slot_inner = max(0.42 * core_r, rod_d / 2.0 + 0.35)
    outer_r = core_r - 0.18 if released else d1 / 2.0
    width = 0.38 * d1
    base_outer = outer_r - max(0.15, 0.035 * d1)
    radial_depth = max(0.25, base_outer - slot_inner)
    center_x = side * (slot_inner + radial_depth / 2.0)
    z0 = -l1
    segment = _box(
        radial_depth, width, l3,
        (center_x, 0.0, z0 + l3 / 2.0))
    land_depth = max(0.20, outer_r - base_outer)
    land_radial = radial_depth + land_depth
    land_center_x = side * (slot_inner + land_radial / 2.0)
    land_h = max(0.25, 0.11 * l3)
    for i in range(4):
        z = z0 + (i + 0.5) * l3 / 4.0
        land = _box(
            land_radial, width, land_h,
            (land_center_x, 0.0, z))
        segment = segment.union(land)
    return segment


def build(
    catalog_index,
    catalog_size,
    mounting_thread_d1,
    thread_engagement_length_l1,
    lower_pin_core_diameter_d2,
    lower_body_diameter_d3,
    rotating_head_diameter_d4,
    button_guard_diameter_d5,
    overall_height_h1,
    body_height_h2,
    pivot_axis_height_h3,
    shackle_opening_height_h4,
    shackle_thickness_k1,
    shackle_outer_width_k2,
    shackle_inner_width_k3,
    lower_pin_projection_l2,
    threaded_segment_length_l3,
    max_torque_nm,
    nominal_load_f1_kn,
    nominal_load_f2_kn,
    nominal_load_f3_kn,
    lock_state,
    shackle_swivel_angle_deg,
    shackle_rotation_deg,
):
    """Return the fixed nine-solid GN 1135 mechanism assembly."""
    _ = (catalog_index, catalog_size, max_torque_nm, nominal_load_f1_kn,
         nominal_load_f2_kn, nominal_load_f3_kn)
    released = int(lock_state) == 1

    body = _main_body(
        mounting_thread_d1, lower_pin_core_diameter_d2,
        lower_body_diameter_d3, button_guard_diameter_d5,
        body_height_h2, pivot_axis_height_h3,
        thread_engagement_length_l1, lower_pin_projection_l2,
        threaded_segment_length_l3, shackle_thickness_k1)
    collar = _rotating_collar(
        lower_body_diameter_d3, rotating_head_diameter_d4,
        body_height_h2, pivot_axis_height_h3, shackle_thickness_k1)
    guard = _safety_guard(
        lower_body_diameter_d3, button_guard_diameter_d5,
        body_height_h2, pivot_axis_height_h3)
    shackle = _shackle(
        overall_height_h1, body_height_h2, pivot_axis_height_h3,
        shackle_opening_height_h4, shackle_thickness_k1,
        shackle_outer_width_k2, shackle_inner_width_k3,
        rotating_head_diameter_d4)
    pivot = _pivot(
        shackle_thickness_k1, shackle_outer_width_k2,
        pivot_axis_height_h3, lower_body_diameter_d3)
    button = _button(
        lower_body_diameter_d3, button_guard_diameter_d5, body_height_h2,
        thread_engagement_length_l1, threaded_segment_length_l3, released)
    spring = _spring(
        lower_body_diameter_d3, pivot_axis_height_h3,
        button_guard_diameter_d5, released)
    segment_left = _thread_segment(
        mounting_thread_d1, lower_pin_core_diameter_d2,
        lower_body_diameter_d3,
        thread_engagement_length_l1, threaded_segment_length_l3,
        -1.0, released)
    segment_right = _thread_segment(
        mounting_thread_d1, lower_pin_core_diameter_d2,
        lower_body_diameter_d3,
        thread_engagement_length_l1, threaded_segment_length_l3,
        1.0, released)

    # Swivel is around the transverse pivot.  Collar, guard, shackle, and pivot
    # then rotate together around the stationary threaded-pin axis.
    shackle = shackle.rotate(
        (0.0, 0.0, pivot_axis_height_h3),
        (1.0, 0.0, pivot_axis_height_h3),
        shackle_swivel_angle_deg)
    collar = _rotz(collar, shackle_rotation_deg)
    guard = _rotz(guard, shackle_rotation_deg)
    shackle = _rotz(shackle, shackle_rotation_deg)
    pivot = _rotz(pivot, shackle_rotation_deg)

    result = cq.Assembly(name="gn1135_self_locking_threaded_lifting_pin")
    result.add(body, name="main_pin_body")
    result.add(collar, name="rotating_collar")
    result.add(shackle, name="shackle")
    result.add(pivot, name="shackle_pivot")
    result.add(button, name="push_button")
    result.add(spring, name="return_spring")
    result.add(guard, name="safety_guard")
    result.add(segment_left, name="thread_segment_01")
    result.add(segment_right, name="thread_segment_02")
    return result
