"""GN 586 safety swivel load ring in one fixed upright assembly pose."""

import math

import cadquery as cq


def _rounded_rectangle_yz(width, height, radius, center_z, depth):
    return (
        cq.Workplane("YZ")
        .center(0.0, center_z)
        .rect(width, height)
        .extrude(depth / 2.0, both=True)
        .edges("|X")
        .fillet(radius)
    )


def _assembly_dimensions(
    thread_major_d,
    d2,
    h1,
    h2,
    h3,
    h4,
    k1,
    k2,
    k3,
):
    """Undimensioned assembly details, all explicitly proportion based."""
    clearance = max(0.60, 0.045 * k1)
    side_section = (k2 - k3) / 2.0
    plate_t = max(1.60, 0.18 * k1)
    axis_d = min(0.80 * d2, 0.68 * k3)
    bearing_radial_clearance = 0.20
    hole_d = axis_d + 2.0 * bearing_radial_clearance
    inside_gap = math.sqrt(k1**2 + side_section**2) + 2.0 * clearance
    head_top = h1 - h3
    clevis_z = head_top + 0.32 * (h2 - head_top)
    plate_width = max(hole_d + 8.0, 0.55 * k2)
    clevis_height = inside_gap + 2.0 * plate_t
    clevis_bottom = clevis_z - clevis_height / 2.0
    target_ring_bottom = clevis_bottom + 0.25 * clevis_height
    ring_outer_bottom = h4 - side_section
    ring_z = target_ring_bottom - ring_outer_bottom

    # The reviewed ring is moved 3/4 of its depth toward the closed -X side.
    ring_x = -(axis_d / 2.0 + clearance + 1.0 + 0.75 * k1)
    straight_tangent_x = min(
        ring_x - k1 / 2.0 - clearance,
        -plate_width / 2.0 - k1 - clearance,
    )

    bore_d = 1.25 * thread_major_d + 2.0 * clearance
    post_top = clevis_z + inside_gap / 2.0 + plate_t + 1.0
    bolt_head_base = post_top + 0.80
    bolt_head_corner_d = 1.18 * hole_d
    bolt_head_across_flats = bolt_head_corner_d * math.cos(math.pi / 6.0)

    return {
        "clearance": clearance,
        "side_section": side_section,
        "plate_t": plate_t,
        "axis_d": axis_d,
        "hole_d": hole_d,
        "inside_gap": inside_gap,
        "clevis_z": clevis_z,
        "clevis_height": clevis_height,
        "clevis_bottom": clevis_bottom,
        "plate_width": plate_width,
        "ring_x": ring_x,
        "ring_z": ring_z,
        "target_ring_bottom": target_ring_bottom,
        "straight_tangent_x": straight_tangent_x,
        "bore_d": bore_d,
        "post_top": post_top,
        "bolt_head_base": bolt_head_base,
        "bolt_head_corner_d": bolt_head_corner_d,
        "bolt_head_across_flats": bolt_head_across_flats,
    }


def build_load_ring(
    h1,
    h2,
    h4,
    k1,
    k2,
    k3,
    ring_x,
    ring_z,
    clevis_z,
    clevis_open_top,
    has_ring_gap,
    angle_deg=0.0,
):
    """Build the common closed ring, then optionally cut the hard-mode gap."""
    side_section = (k2 - k3) / 2.0
    outer_bottom = h4 - side_section
    outer_height = h1 - outer_bottom
    inner_height = h2 - h4

    outer = _rounded_rectangle_yz(
        k2,
        outer_height,
        min(side_section, outer_height / 2.0) * 0.92,
        (h1 + outer_bottom) / 2.0,
        k1,
    )
    opening = _rounded_rectangle_yz(
        k3,
        inner_height,
        min(
            0.72 * side_section,
            k3 / 2.0 - 0.1,
            inner_height / 2.0 - 0.1,
        ),
        (h2 + h4) / 2.0,
        k1 + 2.0,
    )

    # Every difficulty starts from this same complete closed ring.  The hard
    # feature is a later subtraction and does not alter the catalog dimensions
    # or assembly placement.
    ring = outer.cut(opening)
    if has_ring_gap:
        lower_gap_h = clevis_open_top - outer_bottom + 1.0
        lower_gap = (
            cq.Workplane("XY")
            .box(k1 + 2.0, 0.50 * k2, lower_gap_h)
            .translate(
                (
                    0.0,
                    0.0,
                    outer_bottom - 1.5 + lower_gap_h / 2.0,
                )
            )
        )
        ring = ring.cut(lower_gap)
    ring = ring.translate((ring_x, 0.0, ring_z))
    if angle_deg:
        ring = ring.rotate(
            (ring_x, 0.0, clevis_z),
            (ring_x, 1.0, clevis_z),
            -angle_deg,
        )
    return ring


def build_bracket(
    thread_major_d,
    d2,
    h4,
    k1,
    k3,
    l2,
    has_rfid,
    dims,
):
    """Elliptical base plus the vertical annular bracket axis."""
    base_h = 0.24 * h4
    bore_d = dims["bore_d"]
    base = (
        cq.Workplane("XY")
        .ellipse(l2 / 2.0, d2 / 2.0)
        .extrude(base_h)
        .cut(
            cq.Workplane("XY")
            .circle(bore_d / 2.0)
            .extrude(base_h + 2.0)
            .translate((0.0, 0.0, -1.0))
        )
    )

    collar_bottom = 0.55 * base_h
    post = (
        cq.Workplane("XY")
        .circle(dims["axis_d"] / 2.0)
        .circle(bore_d / 2.0)
        .extrude(dims["post_top"] - collar_bottom)
        .translate((0.0, 0.0, collar_bottom))
    )
    bracket = base.union(post)

    if has_rfid:
        # RFID presence is documented; its undimensioned pad is proportion.
        rfid_pad = (
            cq.Workplane("XY")
            .circle(0.105 * l2)
            .extrude(0.08 * h4 + 0.2)
            .translate((-0.30 * l2, 0.0, base_h - 0.2))
        )
        bracket = bracket.union(rfid_pad)

    # Re-cut after all unions so neither the post nor RFID pad fills the bore.
    return bracket.cut(
        cq.Workplane("XY")
        .circle(bore_d / 2.0)
        .extrude(dims["post_top"] + 2.0)
        .translate((0.0, 0.0, -1.0))
    )


def build_bushing(thread_major_d, h4):
    radial_clearance = max(0.30, 0.018 * thread_major_d)
    inner_d = thread_major_d + 2.0 * radial_clearance
    outer_d = 1.25 * thread_major_d
    bushing_h = 0.24 * h4 + 0.8
    return (
        cq.Workplane("XY")
        .circle(outer_d / 2.0)
        .circle(inner_d / 2.0)
        .extrude(bushing_h)
        .translate((0.0, 0.0, -0.4))
    )


def build_bolt(thread_major_d, l1, dims):
    """Simplified bolt with a hex head above the bracket post."""
    head_h = 0.38 * thread_major_d
    shaft = (
        cq.Workplane("XY")
        .circle(thread_major_d / 2.0)
        .extrude(dims["bolt_head_base"] + l1)
        .translate((0.0, 0.0, -l1))
    )
    head = (
        cq.Workplane("XY")
        .polygon(6, dims["bolt_head_corner_d"])
        .extrude(head_h)
        .translate((0.0, 0.0, dims["bolt_head_base"]))
    )
    return shaft.union(head)


def build_clevis(dims):
    """One obround strip folded 180 degrees into a horizontal-ear clevis."""
    plate_t = dims["plate_t"]
    inside_gap = dims["inside_gap"]
    inner_r = inside_gap / 2.0
    outer_r = inner_r + plate_t
    plate_width = dims["plate_width"]
    tip_radius = plate_width / 2.0
    hole_x = 0.0
    tangent_x = dims["straight_tangent_x"]

    footprint = (
        cq.Workplane("XY")
        .box(hole_x - tangent_x, plate_width, plate_t)
        .translate(
            (
                (hole_x + tangent_x) / 2.0,
                0.0,
                plate_t / 2.0,
            )
        )
        .union(
            cq.Workplane("XY")
            .circle(tip_radius)
            .extrude(plate_t)
        )
        .cut(
            cq.Workplane("XY")
            .circle(dims["hole_d"] / 2.0)
            .extrude(plate_t + 2.0)
            .translate((0.0, 0.0, -1.0))
        )
    )

    ear_z = inside_gap / 2.0 + plate_t / 2.0
    upper = footprint.translate(
        (0.0, 0.0, dims["clevis_z"] + ear_z - plate_t / 2.0)
    )
    lower = footprint.translate(
        (0.0, 0.0, dims["clevis_z"] - ear_z - plate_t / 2.0)
    )

    annulus = (
        cq.Workplane("XZ")
        .center(tangent_x, dims["clevis_z"])
        .circle(outer_r)
        .circle(inner_r)
        .extrude(plate_width / 2.0, both=True)
    )
    closed_half = annulus.intersect(
        cq.Workplane("XY")
        .box(
            2.0 * outer_r + 2.0,
            plate_width + 2.0,
            2.0 * outer_r + 2.0,
        )
        .translate(
            (
                tangent_x - outer_r - 1.0,
                0.0,
                dims["clevis_z"],
            )
        )
    )
    return upper.union(lower).union(closed_half)


def build(
    thread_major_d,
    d2,
    h1,
    h2,
    h3,
    h4,
    k1,
    k2,
    k3,
    k4,
    k5,
    l1,
    l2,
    r,
    has_rfid,
    has_ring_gap,
):
    dims = _assembly_dimensions(
        thread_major_d,
        d2,
        h1,
        h2,
        h3,
        h4,
        k1,
        k2,
        k3,
    )
    load_ring = build_load_ring(
        h1,
        h2,
        h4,
        k1,
        k2,
        k3,
        dims["ring_x"],
        dims["ring_z"],
        dims["clevis_z"],
        (
            dims["clevis_z"]
            + dims["inside_gap"] / 2.0
            + dims["plate_t"]
        ),
        has_ring_gap,
    )
    bracket = build_bracket(
        thread_major_d,
        d2,
        h4,
        k1,
        k3,
        l2,
        has_rfid,
        dims,
    )
    bushing = build_bushing(thread_major_d, h4)
    bolt = build_bolt(thread_major_d, l1, dims)
    clevis = build_clevis(dims)

    result = cq.Assembly(name="safety_swivel_load_ring")
    result.add(load_ring, name="load_ring", color=cq.Color(0.92, 0.12, 0.52))
    result.add(bracket, name="bracket", color=cq.Color(0.82, 0.18, 0.45))
    result.add(bushing, name="bushing", color=cq.Color(0.72, 0.74, 0.76))
    result.add(bolt, name="bolt", color=cq.Color(0.40, 0.42, 0.45))
    result.add(clevis, name="clevis", color=cq.Color(0.95, 0.35, 0.75))
    return result
