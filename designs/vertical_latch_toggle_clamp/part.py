"""Parametric GN 851.1 style vertical latch toggle clamp.

Coordinate convention:
- X follows the handle and mounting-base length in the top view.
- Y follows the base width / fork width.
- Z is height.

The model is a static single-solid approximation of the GN 851.1 drawing. The
catalog table drives the named drawing dimensions a1/a2/b1..b5/d1/d2/h1/h2/
l1/l2/m1..m5/r/s/w1/w2. Small hardware such as threads, nuts, grip ribs, and
exact bent-sheet radii are simplified.

Drawing/table symbol map:
- a1: side-view offset from latch rod centerline to lower catch side
- a2: side-view height to the underside of the handle bracket
- b1/b2: top-view mounting base length / overall width
- b3/b5: front-view outside fork width / inside fork width
- b4: front-view lower adjuster plate height
- d1/d2: U-bolt rod diameter / mounting hole diameter
- h1/h2: upper latch pivot height / lower catch offset
- l1/l2: handle length / small front catch tab length
- m1: top-view mounting-hole spacing across the base width
- m2/m3: secondary top-view mounting-hole offsets
- m4/m5: lower adjuster-hole height from bottom / spacing to upper adjuster-hole center
- r: adjustable range with w2 set to zero
- s: sheet/base plate thickness
- w1/w2: clamp stroke / adjustable end range
"""

import math

import cadquery as cq


def _box(x_len, y_len, z_len, radius=0.0):
    solid = cq.Workplane("XY").box(x_len, y_len, z_len)
    if radius > 0:
        solid = solid.edges("|Z").fillet(min(radius, x_len * 0.2, y_len * 0.2))
    return solid


def _capsule_x(length, width, thickness):
    radius = width / 2.0
    straight = max(length - width, width * 0.2)
    return (
        cq.Workplane("XY")
        .rect(straight, width)
        .extrude(thickness)
        .union(cq.Workplane("XY").circle(radius).extrude(thickness).translate((-straight / 2.0, 0.0, 0.0)))
        .union(cq.Workplane("XY").circle(radius).extrude(thickness).translate((straight / 2.0, 0.0, 0.0)))
    )


def _cylinder_y(radius, length):
    return cq.Workplane("XZ").circle(radius).extrude(length, both=True)


def _cylinder_x(radius, length):
    return cq.Workplane("YZ").circle(radius).extrude(length, both=True)


def _vertical_rod(radius, height):
    return cq.Workplane("XY").circle(radius).extrude(height)


def build(
    clamp_size,
    with_u_bolt,
    handle_angle,
    a1,
    a2,
    b1,
    b2,
    b3,
    b4,
    b5,
    d1,
    d2,
    h1,
    h2,
    l1,
    l2,
    m1,
    m2,
    m3,
    m4,
    m5,
    r,
    s,
    w1,
    w2,
):
    # Mounting base, with the four d2 holes located by m1/m3 as in the top view.
    base_x = b1
    base_y = b2
    base_z = s
    base_center_x = b1 * 0.15
    result = _box(base_x, base_y, base_z, d2 * 0.25).translate((base_center_x, 0.0, base_z / 2.0))
    result = (
        result.faces(">Z")
        .workplane(centerOption="CenterOfBoundBox")
        .pushPoints(
            [
                (-m3 / 2.0, -m1 / 2.0),
                (m3 / 2.0, -m1 / 2.0),
                (-m3 / 2.0, m1 / 2.0),
                (m3 / 2.0, m1 / 2.0),
            ]
        )
        .hole(d2)
    )

    pivot_x = -b1 * 0.35
    pivot_y = 0.0
    pivot_z = h1
    rod_r = d1 / 2.0
    catch_x = pivot_x - max(a1 + d1 * 1.2, s * 3.2)
    side_plate_t = max(s * 1.25, rod_r * 1.15)
    fork_gap = max(b5, d1 * 2.2)
    fork_outer_y = max(b3, fork_gap + 2.0 * side_plate_t)
    fork_wall_x = max(s * 2.0, d1 * 1.15)
    fork_h = max(h1 - base_z, s * 7.0)

    # Front-view fork: two tall side cheeks with a top bridge and a lower web.
    for sy in (-1.0, 1.0):
        cheek = _box(fork_wall_x, side_plate_t, fork_h, side_plate_t * 0.20).translate(
            (pivot_x, sy * fork_outer_y / 2.0, base_z + fork_h / 2.0)
        )
        result = result.union(cheek)

    top_bridge = _box(fork_wall_x * 1.35, fork_outer_y, side_plate_t, side_plate_t * 0.18).translate(
        (pivot_x, 0.0, pivot_z + side_plate_t * 0.42)
    )
    lower_bridge = _box(fork_wall_x * 1.15, max(b5, fork_outer_y * 0.42), side_plate_t, side_plate_t * 0.12).translate(
        (pivot_x, 0.0, max(base_z + side_plate_t, h2))
    )
    result = result.union(top_bridge).union(lower_bridge)

    # Base-to-fork vertical support plate visible in side view.
    support_h = max(h1 - base_z - side_plate_t * 0.4, s * 4.0)
    rear_support = _box(max(s * 2.4, d1 * 1.2), max(b5, fork_outer_y * 0.38), support_h, s * 0.18).translate(
        (pivot_x + fork_wall_x * 0.72, 0.0, base_z + support_h / 2.0)
    )
    result = result.union(rear_support)

    # Sloped triangular side bracket from base to the handle support, matching the
    # prominent side-view web under the handle.
    web_top_z = max(a2, h1 - side_plate_t * 0.6)
    web_front_x = pivot_x + b4
    web_t = max(s * 1.15, d1 * 0.35)
    web = (
        cq.Workplane("XZ")
        .polyline(
            [
                (pivot_x + max(a1, fork_wall_x * 0.4), base_z),
                (web_front_x, base_z),
                (pivot_x + max(a1, fork_wall_x * 0.4), web_top_z),
            ]
        )
        .close()
        .extrude(web_t, both=True)
        .translate((0.0, 0.0, 0.0))
    )
    result = result.union(web)

    # Horizontal pivot pin and round washers/nuts spanning the fork width.
    pin_r = max(rod_r * 0.95, s * 0.85)
    pin = _cylinder_y(pin_r, fork_outer_y).translate((pivot_x, 0.0, pivot_z))
    result = result.union(pin)
    for sy in (-1.0, 1.0):
        washer = _cylinder_y(pin_r * 1.45, side_plate_t * 0.9).translate(
            (pivot_x, sy * (fork_outer_y / 2.0 + side_plate_t * 0.35), pivot_z)
        )
        result = result.union(washer)

    # Top-view handle: the horizontal metal lever runs through the pivot area,
    # while a single over-molded envelope wraps it out to the l1 right end.
    handle_w = max(b5, d1 * 2.3)
    handle_t = max(s * 1.15, d1 * 0.85)
    lift = (handle_angle / 18.0) * handle_t * 0.25
    metal_start_x = min(pivot_x - pin_r * 1.15, catch_x - rod_r * 1.2)
    metal_end_x = pivot_x + l1
    metal_len = metal_end_x - metal_start_x
    metal_w = max(handle_w * 0.52, d1 * 1.35)
    handle = _capsule_x(metal_len, metal_w, handle_t * 0.72).translate(
        (metal_start_x + metal_len / 2.0, 0.0, pivot_z + handle_t * 0.02 + lift)
    )
    result = result.union(handle)

    sleeve_x0 = catch_x + rod_r * 0.75
    sleeve_x1 = pivot_x + l1
    sleeve_w = max(metal_w * 1.45, d1 * 2.2)
    sleeve_top_z = pivot_z + handle_t * 0.74 + lift
    sleeve_bot_left_z = pivot_z - handle_t * 0.46 + lift
    sleeve_bot_right_z = pivot_z - handle_t * 0.12 + lift
    cap_x = sleeve_x1 - max(handle_t * 0.62, d1 * 0.55)
    sleeve = (
        cq.Workplane("XZ")
        .polyline(
            [
                (sleeve_x0, sleeve_bot_left_z),
                (cap_x, sleeve_bot_right_z),
                (sleeve_x1, (sleeve_top_z + sleeve_bot_right_z) / 2.0),
                (cap_x, sleeve_top_z),
                (sleeve_x0, sleeve_top_z),
            ]
        )
        .close()
        .extrude(sleeve_w, both=True)
    )
    result = result.union(sleeve)

    sleeve_lip = _box(max(d1 * 0.8, s * 1.6), sleeve_w * 1.04, handle_t * 1.18, 0.0).translate(
        (sleeve_x0, 0.0, pivot_z + handle_t * 0.12 + lift)
    )
    result = result.union(sleeve_lip)

    for i in range(7):
        rib_x = sleeve_x0 + (sleeve_x1 - sleeve_x0) * (0.33 + i * 0.065)
        rib = _box((sleeve_x1 - sleeve_x0) * 0.025, sleeve_w * 0.72, handle_t * 0.12, 0.0).translate(
            (rib_x, 0.0, sleeve_top_z + handle_t * 0.08)
        )
        rib = rib.rotate((rib_x, 0.0, pivot_z), (rib_x, 1.0, pivot_z), -14.0)
        result = result.union(rib)

    # Toggle link drawn as a diagonal slender bar beneath the handle.
    link_len = max(l1 * 0.50, b4)
    link_w = max(s * 0.8, d1 * 0.45)
    link_t = max(s * 0.70, d1 * 0.38)
    link_angle = -math.degrees(math.atan2(max(h1 - h2, s), max(link_len, s)))
    link = _box(link_len, link_w, link_t, link_w * 0.18)
    link = link.rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), link_angle + handle_angle * 0.08).translate(
        (pivot_x + link_len * 0.38, 0.0, pivot_z - (h1 - h2) * 0.35)
    )
    result = result.union(link)

    # Lower catch block and adjustment plate at the front, matching the side
    # view's long adjustable latch below the fork.
    catch_block_h = max(h2 + m4 * 0.55, m4 + d2, s * 4.0)
    catch_block = _box(max(d1 * 1.35, s * 2.2), max(b5, fork_outer_y * 0.46), catch_block_h, s * 0.12).translate(
        (catch_x, 0.0, base_z + catch_block_h / 2.0)
    )
    result = result.union(catch_block)

    adjustable_top_z = max(h2, base_z + s)
    visible_range = max(w1 * 0.95, r * 0.62)
    lower_hook_z = min(base_z - max(w2, d1 * 2.0), adjustable_top_z - visible_range - max(w2, d1 * 1.5))
    adjust_plate_x = catch_x + a1 * 0.45

    # The lower front-view adjuster plate makes the missing lower half explicit:
    # b4 controls the plate height, b5 controls the plate width, d2 cuts the two
    # through-holes, m4 locates the lower hole from the bottom, and m5 spaces the
    # upper hole from it. The drawing shows the side-view range r with a break, so
    # surrounding guide/rod geometry uses a proportional span for readability.
    adjust_plate_h = max(b4, m4 + m5 + d2 * 1.5)
    adjust_plate_y = max(b5, d2 * 2.4)
    adjust_plate_x_len = max(d1 * 1.25, s * 2.0)
    adjust_plate = _box(adjust_plate_x_len, adjust_plate_y, adjust_plate_h, 0.0).translate(
        (adjust_plate_x, 0.0, lower_hook_z + adjust_plate_h / 2.0)
    )
    result = result.union(adjust_plate)
    m4_z = lower_hook_z + m4
    m5_z = m4_z + m5

    if with_u_bolt:
        # U-bolt latch: two vertical rods flanking the fork, connected by a lower
        # rounded crosspiece. The rods run through the full r/w2 lower range.
        rod_sep = max(fork_outer_y + d1 * 1.6, b2 * 0.72)
        rod_h = max(pivot_z + d1 * 1.5 - lower_hook_z, w1 * 0.65)
        for sy in (-1.0, 1.0):
            rod = _vertical_rod(rod_r, rod_h).translate((catch_x, sy * rod_sep / 2.0, lower_hook_z))
            result = result.union(rod)
            nut = _box(d1 * 1.65, d1 * 1.65, d1 * 0.75, 0.0).translate(
                (catch_x, sy * rod_sep / 2.0, pivot_z + d1 * 0.85)
            )
            result = result.union(nut)
        lower_cross = _box(d1 * 1.15, rod_sep + d1, d1, rod_r * 0.30).translate(
            (catch_x, 0.0, lower_hook_z)
        )
        yoke_tie = _box(max(d1, s * 1.4), rod_sep + d1, max(s, d1 * 0.55), 0.0).translate(
            (catch_x, 0.0, max(h2, base_z + s))
        )
        result = result.union(lower_cross).union(yoke_tie)
    else:
        hook_len = max(w1 * 0.40, d1 * 3.0)
        hook = _capsule_x(hook_len, d1 * 1.75, d1).translate(
            (catch_x - hook_len * 0.35, 0.0, lower_hook_z)
        )
        result = result.union(hook)

    # Cross pin through the lower latch line, separate from the m4/m5 bosses.
    lower_pin = _cylinder_y(max(rod_r * 0.65, s * 0.45), max(b5, fork_outer_y * 0.8)).translate(
        (catch_x + d1 * 0.55, 0.0, adjustable_top_z)
    )
    result = result.union(lower_pin)

    connector_len = max((base_center_x - catch_x) + b1 * 0.35, s * 4.0)
    connector = _box(connector_len, max(s * 1.6, d1 * 0.7), s * 0.85, 0.0).translate(
        ((catch_x + base_center_x) / 2.0, 0.0, base_z + s * 0.42)
    )
    result = result.union(connector)

    # l2 helps locate the front catch detail in the side view.
    front_tab = _box(max(l2, s * 1.5), max(b5, d1 * 2.0), max(s, d1 * 0.45), 0.0).translate(
        (catch_x - l2 * 0.35, 0.0, base_z + h2 + s * 0.35)
    )
    result = result.union(front_tab)

    # Cut these last so later guide/ear geometry cannot refill either hole.
    for hole_z in (m4_z, m5_z):
        hole = _cylinder_x(d2 / 2.0, adjust_plate_x_len + s * 6.0).translate((adjust_plate_x, 0.0, hole_z))
        result = result.cut(hole)

    return result


if "show_object" in globals():
    result = build(
        clamp_size=320,  # catalog size row / holding-capacity class
        with_u_bolt=1,  # 1 = T3 with U-bolt latch and catch; 0 = T without U-bolt
        handle_angle=0.0,  # operating-principle handle pose, proportion-derived
        a1=7.9,  # table a1: side-view offset from latch rod centerline to lower catch side
        a2=37.1,  # table a2: side-view height to underside of the handle bracket
        b1=36.1,  # table b1: top-view mounting base length
        b2=43.9,  # table b2: top-view overall base / handle envelope width
        b3=32.0,  # table b3: front-view outside fork/base width
        b4=37.1,  # table b4: front-view lower bracket height span
        b5=22.1,  # table b5: front-view inside fork width
        d1=6.0,  # table d1: U-bolt latch rod nominal diameter
        d2=6.6,  # table d2: mounting hole diameter in the base
        h1=54.1,  # table h1: side-view upper latch pivot height
        h2=15.0,  # table h2: side-view lower catch offset
        l1=105.9,  # table l1: top-view overall handle length
        l2=6.1,  # table l2: small front catch tab length
        m1=25.4,  # table m1: top-view handle grip/body width
        m2=8.4,  # table m2: top-view transverse mounting-hole spacing
        m3=19.1,  # table m3: top-view longitudinal mounting-hole spacing
        m4=10.4,  # table m4: front-view lower adjuster-hole height from lower datum
        m5=20.6,  # table m5: front-view spacing to upper adjuster-hole center
        r=78.0,  # table R: adjustable range with w2 set to zero
        s=3.0,  # table s: sheet/base plate thickness
        w1=53.1,  # table w1: clamp stroke
        w2=21.1,  # table w2: adjustable end range
    )
    show_object(result, name="vertical_latch_toggle_clamp")
