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
    ring_section_r = k1 / 2.0
    plate_t = max(1.60, 0.18 * k1)
    axis_d = min(0.80 * d2, 0.68 * k3)
    bearing_radial_clearance = 0.20
    hole_d = axis_d + 2.0 * bearing_radial_clearance
    # The clevis captures the swept circular ring section with only assembly
    # clearance; the former diagonal-envelope rule left a visibly loose gap.
    inside_gap = 2.0 * ring_section_r + 2.0 * clearance
    # h4 is the catalog elevation of the ring opening's lower edge and is the
    # only sourced vertical datum for the rounded U-shaped bracket pocket.
    # Keeping the pocket centered on h4 also lets the load-ring top remain at
    # the published h1 instead of translating the whole ring upward.
    clevis_z = h4
    plate_width = max(hole_d + 8.0, 0.55 * k2)
    clevis_height = inside_gap + 2.0 * plate_t
    clevis_bottom = clevis_z - clevis_height / 2.0
    # Capture the circular ring section between the bracket axis and the
    # closed return with equal clearance on both X sides.
    ring_x = -(axis_d / 2.0 + clearance + ring_section_r)
    straight_tangent_x = ring_x - ring_section_r - clearance

    bore_d = 1.25 * thread_major_d + 2.0 * clearance
    post_top = clevis_z + inside_gap / 2.0 + plate_t + 1.0
    bolt_head_base = post_top + 0.80
    bolt_head_corner_d = 1.18 * hole_d
    bolt_head_across_flats = bolt_head_corner_d * math.cos(math.pi / 6.0)

    return {
        "clearance": clearance,
        "side_section": side_section,
        "ring_section_r": ring_section_r,
        "plate_t": plate_t,
        "axis_d": axis_d,
        "hole_d": hole_d,
        "inside_gap": inside_gap,
        "clevis_z": clevis_z,
        "clevis_height": clevis_height,
        "clevis_bottom": clevis_bottom,
        "plate_width": plate_width,
        "ring_x": ring_x,
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
):
    """Sweep a circular section around the earlier squared U-shaped path."""
    side_section = (k2 - k3) / 2.0
    section_r = k1 / 2.0
    outer_bottom = h4 - side_section
    outer_height = h1 - outer_bottom
    path_width = k2 - 2.0 * section_r
    path_height = outer_height - 2.0 * section_r
    path_center_z = (h1 + outer_bottom) / 2.0

    # This is the pre-fix visual path: straight sides and restrained corner
    # radii.  Only the material section changes from a cut extrusion to a
    # genuine circle swept along the closed centerline.
    path_radius = min(
        0.82 * side_section,
        path_width / 2.0 - 0.1,
        path_height / 2.0 - 0.1,
    )
    half_w = path_width / 2.0
    half_h = path_height / 2.0
    path = cq.Wire.makePolygon(
        [
            (0.0, -half_w, path_center_z - half_h),
            (0.0, half_w, path_center_z - half_h),
            (0.0, half_w, path_center_z + half_h),
            (0.0, -half_w, path_center_z + half_h),
        ],
        close=True,
    )
    path = path.fillet2D(path_radius, path.Vertices())

    path_start = path.startPoint()
    path_tangent = path.tangentAt(0.0)
    profile_plane = cq.Plane(
        origin=path_start.toTuple(),
        xDir=(1.0, 0.0, 0.0),
        normal=path_tangent.toTuple(),
    )
    ring = (
        cq.Workplane(profile_plane)
        .circle(section_r)
        .sweep(path, isFrenet=True)
    )
    return ring.translate((ring_x, 0.0, 0.0))


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


def _external_unified_thread(thread_major_d, thread_tpi, length):
    """External 60-degree Unified thread driven by the catalog TPI.

    The basic external-thread radial depth is 0.61343*P.  A triangular ridge
    is embedded slightly into the root cylinder so the modeled thread remains
    one robust solid on every catalog row.  Crest/root truncation is a
    documented visual proportion rather than a tolerance-grade claim.
    """
    pitch = 25.4 / float(thread_tpi)
    thread_depth = 0.61343 * pitch
    major_r = thread_major_d / 2.0
    root_r = major_r - thread_depth
    radial_embed = min(0.08, 0.05 * pitch)
    half_width = 0.30 * pitch
    path_r = (major_r + root_r) / 2.0
    path_height = length - 2.0 * half_width

    core = cq.Workplane("XY").circle(root_r).extrude(length)
    helix = cq.Wire.makeHelix(pitch, path_height, path_r)
    profile = (
        cq.Workplane("XZ")
        .polyline(
            [
                (root_r - radial_embed, -half_width),
                (major_r, 0.0),
                (root_r - radial_embed, half_width),
            ]
        )
        .close()
    )
    ridge = profile.sweep(helix, isFrenet=True).translate(
        (0.0, 0.0, half_width)
    )
    return core.union(ridge)


def build_bolt(thread_major_d, thread_tpi, l1, dims):
    """Bolt with a catalog-pitch Unified external thread and hex head."""
    head_h = 0.38 * thread_major_d
    threaded_end = _external_unified_thread(
        thread_major_d, thread_tpi, l1
    ).translate((0.0, 0.0, -l1))
    plain_shank = (
        cq.Workplane("XY")
        .circle(thread_major_d / 2.0)
        .extrude(dims["bolt_head_base"] + 0.05)
        .translate((0.0, 0.0, -0.05))
    )
    head = (
        cq.Workplane("XY")
        .polygon(6, dims["bolt_head_corner_d"])
        .extrude(head_h)
        .translate((0.0, 0.0, dims["bolt_head_base"]))
    )
    return threaded_end.union(plain_shank).union(head)


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
    thread_tpi,
    d2,
    h1,
    h2,
    h3,
    h4,
    k1,
    k2,
    k3,
    l1,
    l2,
    has_rfid,
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
    bolt = build_bolt(thread_major_d, thread_tpi, l1, dims)
    clevis = build_clevis(dims)

    result = cq.Assembly(name="safety_swivel_load_ring")
    result.add(load_ring, name="load_ring", color=cq.Color(0.92, 0.12, 0.52))
    result.add(bracket, name="swivel_base", color=cq.Color(0.82, 0.18, 0.45))
    result.add(bushing, name="bearing_bushing", color=cq.Color(0.72, 0.74, 0.76))
    result.add(bolt, name="mounting_bolt", color=cq.Color(0.40, 0.42, 0.45))
    result.add(clevis, name="bracket", color=cq.Color(0.95, 0.35, 0.75))
    return result
