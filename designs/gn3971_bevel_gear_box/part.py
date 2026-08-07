"""Parametric Ganter GN 3971 bevel gear box assembly.

The official GN 3971 drawing controls the external envelope, shaft ends,
parallel keys, and mounting-hole locations.  Hidden gear, bearing, cavity,
and small edge details are documented proportions because the public sheet
does not publish those manufacturing dimensions.

Coordinate system:
  * input shaft axis: +X
  * output shaft axis: +Z
  * common bevel-gear pitch-cone apex: (0, 0, 0)

Type L has one +X input end and one +Z output end.  Type T retains the same
input end and uses one continuous output shaft with +Z and -Z ends.
"""

import cadquery as cq
import math


# The catalog publishes no gear data, so the tooth count follows from a REAL
# module rather than being picked: choose the coarsest ISO 54 preferred module
# that still leaves the face width at least 5.5 modules (straight bevel gears
# are normally proportioned with b/m in the 6-12 band), then z = 2*r_mean/m.
# A fixed 16 gave b/m 4.2-4.5 — the rim read as a sawblade; a fixed 24 fixed
# that but drove the module to 0.45 on the smallest boxes, finer than a real
# steel gearbox that size would use. The ladder keeps both honest.
# ISO 23509 straight-bevel tooth proportions, applied to the TRANSVERSE
# section at each cone distance (Tredgold's substitute: the section is treated
# as a spur gear of z teeth and the local module m_t = 2*s/z, and because
# m_t scales with s the two end sections are similar, so the tip and root
# cones both run through the pitch apex — the classic standard taper).
PRESSURE_ANGLE_DEG = 20.0
ADDENDUM_FACTOR = 1.00
DEDENDUM_FACTOR = 1.25          # 0.25*m tip clearance
FACE_MODULES_TARGET = 6.0       # gen-1 picks b/m from {4..8}; 6 is its middle
BACKLASH_DEG = 3.15             # published GN 3971 backlash (3 +/- 0.5 deg)
TOE_WALL_MODULES = 0.30         # metal left between the toe root cone and bore
INVOLUTE_STEPS = 6              # points sampled along each involute flank
# STUB tooth proportions, measured PERPENDICULAR to the pitch cone: addendum
# 0.8*m, dedendum 1.0*m (whole depth 1.8*m). Stub teeth are the standard
# answer when the blank cannot host a full-depth tooth — here the bore is up
# to 46% of the box, and a full-depth root cone dives straight into the shaft.  The tooth sections
# below are sketched at constant z, and the tip/root cones are parallel to the
# 45-degree pitch cone, so a perpendicular offset a becomes a RADIAL offset
# a/cos(45 deg) at constant z.  Skipping that conversion is what made the
# earlier 0.50*m / 0.60*m radial figures only 0.78*m of real tooth depth.
PITCH_ANGLE_DEG = 45.0
_RADIAL = 1.0 / math.cos(math.radians(PITCH_ANGLE_DEG))
ADDENDUM_RADIAL = 0.80 * _RADIAL
DEDENDUM_RADIAL = 1.00 * _RADIAL
# both are proportional to the module, and m = 2*r_mean/z, so the tip and root
# cones are fixed multiples of the pitch cone regardless of size
RIM_WALL_FACTOR = 1.2   # heel rim under the root cone, in modules


def _layout(housing_size_b1, shaft_diameter_d1, bearing_boss_diameter_d2,
            housing_length_l1, shaft_projection_l2, input_axis_height_m1,
            bearing_inset_t1, shaft_reach_t2, gearbox_type):
    """Derive only the undocumented internal proportions in one place."""
    b1 = housing_size_b1
    d1 = shaft_diameter_d1
    d2 = bearing_boss_diameter_d2
    rear = -(housing_length_l1 - input_axis_height_m1)
    if gearbox_type == 0:
        bottom = rear
        top = input_axis_height_m1
    else:
        bottom = -0.5 * housing_length_l1
        top = 0.5 * housing_length_l1

    L = {
        "rear": rear,
        "bottom": bottom,
        "top": top,
        "front": input_axis_height_m1,
        "input_shaft_end": input_axis_height_m1 + shaft_projection_l2,
        "output_top_end": top + shaft_projection_l2,
        # The Type-T reference has sharp rear side corners; its visible
        # shoulder rounds are part of the profile, not an edge fillet.
        "edge_radius": 0.0 if gearbox_type == 1 else 0.04 * b1,
        "bearing_width": max(1.5, 0.12 * d2),
        "shaft_clearance": max(0.12, 0.008 * d1),
        "cavity_clearance": max(0.25, 0.015 * b1),
        "opening_chamfer": min(0.65, 0.045 * d2),
        # The catalog STEP uses a short 45-degree transition between two
        # tangent circular shoulder rounds on Type T.  The b1=18 reference
        # measures r=4.0 and a 0.9 mm tangent gap; scale both with b1.
        "shoulder_radius": (2.0 / 9.0) * b1,
        "shoulder_gap": 0.05 * b1,
    }

    # Both pitch cones are 45 degrees because the documented ratio is 1:1
    # and the shaft angle is 90 degrees.  The tooth count and face width are
    # proportions; the shaft bore sets the lower bound on the small end.
    # Face limits from the casting envelope. With the full-depth root cone the
    # blank must still be a blank: the rim that carries the teeth is checked at
    # the HEEL (spec.check), where the root cone is largest. Deepening the root
    # without that guard is what left the teeth standing on a 0.3 mm shell, so
    # the gear read as a crown of loose fins rather than a bevel gear.
    s_inner = max(0.24 * b1, 0.5 * d1 + 0.035 * b1)
    cav = max(0.25, 0.015 * b1)
    tip_ratio_max = 1.0 + 2.0 * ADDENDUM_FACTOR / 12.0
    s_outer = min((0.48 * b1 - cav - 0.10) / tip_ratio_max, s_inner + 0.12 * b1)
    pitch_mean = 0.5 * (s_inner + s_outer)
    face = (s_outer - s_inner) * math.sqrt(2.0)     # face width along the cone
    # TOOTH COUNT FROM TWO CLOSED FORMS, not a picked number.
    #  (a) the root cone must clear the shaft bore at the toe, where it is
    #      smallest.  root(s_i) = s_i*(1 - 2*hf/z) >= d1/2 + wall
    #      =>  z >= 2*hf / (1 - (d1/2 + wall)/s_i)
    #      More teeth pull the root cone back toward the pitch cone, which is
    #      what moves the teeth away from the shaft — and shrinks each tooth,
    #      since m = 2*s_o/z.
    #  (b) face width in modules: b/m = 6 (the middle of the gen-1 family's
    #      {4,5,6,7,8}) => z = 6 * 2*s_o / b.
    #  Floor: no undercut needs the VIRTUAL count z_v = z/cos(45 deg) >= 17,
    #  i.e. z >= 12 for a 20 deg pressure angle.
    z_clear = 12
    for _ in range(6):
        wall = TOE_WALL_MODULES * (2.0 * s_outer / max(z_clear, 12))
        denom = 1.0 - (0.5 * d1 + wall) / s_inner
        z_clear = 12 if denom <= 0.0 else max(12, math.ceil(2.0 * DEDENDUM_FACTOR / denom))
    z_face = FACE_MODULES_TARGET * 2.0 * s_outer / face
    teeth = max(12, int(math.ceil(max(z_clear, z_face))))
    teeth += teeth % 2              # even: the half-pitch mesh phase needs it
    module = 2.0 * s_outer / teeth  # OUTER transverse module m_et
    root_ratio = 1.0 - 2.0 * DEDENDUM_FACTOR / teeth
    tip_ratio = 1.0 + 2.0 * ADDENDUM_FACTOR / teeth
    tip_outer = s_outer * tip_ratio
    root_inner = s_inner * root_ratio
    tooth_fraction = 0.5 - BACKLASH_DEG * teeth / 720.0
    hub_length = 0.02 * b1
    root_ratio = 1.0 - 2.0 * DEDENDUM_RADIAL / teeth
    tip_ratio = 1.0 + 2.0 * ADDENDUM_RADIAL / teeth
    tip_outer = s_outer * tip_ratio
    root_inner = s_inner * root_ratio
    L.update({
        "gear_s_inner": s_inner,
        "gear_s_outer": s_outer,
        "gear_pitch_mean": pitch_mean,
        "gear_module": module,
        "gear_hub_length": hub_length,
        "gear_tip_outer": tip_outer,
        "gear_root_inner": root_inner,
        "gear_root_outer": s_outer * root_ratio,
        "gear_face_width": face,
        "gear_teeth": teeth,
        "gear_tooth_fraction": tooth_fraction,
        "shaft_start": max(s_inner - hub_length,
                           0.5 * d1 + 0.02 * b1),
    })

    w = L["bearing_width"]
    front = input_axis_height_m1
    L["input_front_bearing"] = front - bearing_inset_t1 - 0.5 * w
    L["input_rear_bearing"] = front - shaft_reach_t2 + 0.5 * w
    L["output_top_bearing"] = top - bearing_inset_t1 - 0.5 * w
    if gearbox_type == 0:
        L["output_second_bearing"] = front - shaft_reach_t2 + 0.5 * w
    else:
        L["output_second_bearing"] = bottom + bearing_inset_t1 + 0.5 * w
    return L


def _axis_cylinder(radius, start, length, axis):
    if axis == "X":
        point = cq.Vector(start, 0.0, 0.0)
        direction = cq.Vector(1.0, 0.0, 0.0)
    else:
        point = cq.Vector(0.0, 0.0, start)
        direction = cq.Vector(0.0, 0.0, 1.0)
    return cq.Solid.makeCylinder(radius, length, point, direction)


def _housing_profile(L, housing_size_b1, gearbox_type):
    """Extrude the L profile or the vertically symmetric T profile."""
    b1 = housing_size_b1
    half = 0.5 * b1
    front = L["front"]
    top = L["top"]
    horizontal_radius = front - half
    vertical_radius = top - half
    profile = (
        cq.Workplane("XZ")
        .moveTo(L["rear"], top)
        .lineTo(half, top)
    )
    if gearbox_type == 0:
        profile = (
            profile
            .ellipseArc(
                horizontal_radius, vertical_radius,
                angle1=180.0, angle2=270.0,
            )
            .lineTo(front, L["bottom"])
        )
    else:
        r = L["shoulder_radius"]
        gap = L["shoulder_gap"]
        q = r / math.sqrt(2.0)
        c1x = half + r
        c1z = half + r + gap
        c2x = half + r + gap
        c2z = half + r
        profile = (
            profile.lineTo(half, c1z)
            .threePointArc(
                (c1x - r * math.cos(math.radians(22.5)),
                 c1z - r * math.sin(math.radians(22.5))),
                (c1x - q, c1z - q),
            )
            .lineTo(c2x - q, c2z - q)
            .threePointArc(
                (c2x - r * math.cos(math.radians(67.5)),
                 c2z - r * math.sin(math.radians(67.5))),
                (c2x, half),
            )
            .lineTo(front, half)
            .lineTo(front, -half)
            .lineTo(c2x, -half)
            .threePointArc(
                (c2x - r * math.cos(math.radians(67.5)),
                 -c2z + r * math.sin(math.radians(67.5))),
                (c2x - q, -c2z + q),
            )
            .lineTo(c1x - q, -c1z + q)
            .threePointArc(
                (c1x - r * math.cos(math.radians(22.5)),
                 -c1z + r * math.sin(math.radians(22.5))),
                (half, -c1z),
            )
            .lineTo(half, -top)
        )
    housing = (
        profile
        .lineTo(L["rear"], L["bottom"])
        .close()
        .extrude(half, both=True)
    )
    if L["edge_radius"] > 0.0:
        housing = housing.edges("|Y").fillet(L["edge_radius"])
    return housing.val()


def _cut_tapped_hole(shape, nominal_d, depth, point, direction):
    """Cylindrical 0.8*d thread-core approximation plus entry chamfer."""
    core_r = 0.40 * nominal_d
    chamfer = 0.18 * nominal_d
    start = cq.Vector(*point)
    axis = cq.Vector(*direction)
    core = cq.Solid.makeCylinder(core_r, depth + 0.2, start, axis)
    entry = cq.Solid.makeCone(
        0.50 * nominal_d,
        core_r,
        chamfer,
        start,
        axis,
    )
    return shape.cut(core).cut(entry)


def _housing(L, housing_size_b1, shaft_diameter_d1,
             bearing_boss_diameter_d2, housing_length_l1,
             input_axis_height_m1, bearing_inset_t1, shaft_reach_t2,
             mounting_hole_diameter_d4, mounting_thread_d5,
             rear_thread_d6, lower_hole_offset_m2, upper_hole_offset_m3,
             face_hole_spacing_m4, rear_hole_height_m5, gearbox_type):
    b1 = housing_size_b1
    d1 = shaft_diameter_d1
    d2 = bearing_boss_diameter_d2
    half = 0.5 * b1
    housing = _housing_profile(L, b1, gearbox_type)

    # Gear cavities follow each 45-degree bevel gear and overlap at the mesh.
    cavity_r = L["gear_tip_outer"] + L["cavity_clearance"]
    cavity_start = (
        L["gear_s_inner"] - L["gear_hub_length"]
        - L["cavity_clearance"]
    )
    cavity_len = (
        L["gear_s_outer"] - cavity_start + L["cavity_clearance"]
    )
    housing = housing.cut(_axis_cylinder(cavity_r, cavity_start, cavity_len, "X"))
    housing = housing.cut(_axis_cylinder(cavity_r, cavity_start, cavity_len, "Z"))

    # Shaft tunnels connect the gear chamber to every external shaft end.
    tunnel_r = 0.5 * (d1 + L["shaft_clearance"])
    housing = housing.cut(_axis_cylinder(
        tunnel_r, L["shaft_start"],
        L["front"] - L["shaft_start"] + 0.5, "X"))
    z_start = L["bottom"] - 0.5 if gearbox_type == 1 else L["shaft_start"]
    housing = housing.cut(
        _axis_cylinder(tunnel_r, z_start, L["top"] - z_start + 0.5, "Z")
    )

    # Bearing pockets use the official d2 envelope.  Each Type-L axis uses one
    # pocket spanning two bearings; Type T uses top and bottom output pockets.
    w = L["bearing_width"]
    input_pocket_start = L["input_rear_bearing"] - 0.5 * w - 0.05
    housing = housing.cut(
        _axis_cylinder(0.5 * d2, input_pocket_start,
                       L["front"] - input_pocket_start + 0.2, "X")
    )
    if gearbox_type == 0:
        output_pocket_start = L["output_second_bearing"] - 0.5 * w - 0.05
        housing = housing.cut(
            _axis_cylinder(0.5 * d2, output_pocket_start,
                           L["top"] - output_pocket_start + 0.2, "Z")
        )
    else:
        top_start = L["output_top_bearing"] - 0.5 * w - 0.05
        housing = housing.cut(
            _axis_cylinder(0.5 * d2, top_start,
                           L["top"] - top_start + 0.2, "Z")
        )
        bottom_end = L["output_second_bearing"] + 0.5 * w + 0.05
        housing = housing.cut(
            _axis_cylinder(0.5 * d2, L["bottom"] - 0.2,
                           bottom_end - L["bottom"] + 0.2, "Z")
        )

    # 45-degree entry chamfers at the visible bearing openings.
    ch = L["opening_chamfer"]
    housing = housing.cut(cq.Solid.makeCone(
        0.5 * d2 + ch, 0.5 * d2, ch,
        cq.Vector(L["front"], 0.0, 0.0), cq.Vector(-1.0, 0.0, 0.0)))
    housing = housing.cut(cq.Solid.makeCone(
        0.5 * d2 + ch, 0.5 * d2, ch,
        cq.Vector(0.0, 0.0, L["top"]), cq.Vector(0.0, 0.0, -1.0)))
    if gearbox_type == 1:
        housing = housing.cut(cq.Solid.makeCone(
            0.5 * d2 + ch, 0.5 * d2, ch,
            cq.Vector(0.0, 0.0, L["bottom"]), cq.Vector(0.0, 0.0, 1.0)))

    # d4 clearance holes are the two circles in the official side view.
    if gearbox_type == 0:
        d4_points = [(-lower_hole_offset_m2, -lower_hole_offset_m2),
                     (upper_hole_offset_m3, upper_hole_offset_m3)]
    else:
        d4_points = [(upper_hole_offset_m3, upper_hole_offset_m3),
                     (upper_hole_offset_m3, -upper_hole_offset_m3)]
    for x, z in d4_points:
        cutter = cq.Solid.makeCylinder(
            0.5 * mounting_hole_diameter_d4,
            b1 + 1.0,
            cq.Vector(x, -half - 0.5, z),
            cq.Vector(0.0, 1.0, 0.0),
        )
        housing = housing.cut(cutter)

    # Four d5 holes surround each bearing face on the official m4 square.
    offset = 0.5 * face_hole_spacing_m4
    for a in (-offset, offset):
        for b in (-offset, offset):
            housing = _cut_tapped_hole(
                housing, mounting_thread_d5, 2.0 * mounting_thread_d5,
                (L["front"] + 0.1, a, b), (-1.0, 0.0, 0.0))
            housing = _cut_tapped_hole(
                housing, mounting_thread_d5, 2.0 * mounting_thread_d5,
                (a, b, L["top"] + 0.1), (0.0, 0.0, -1.0))
            if gearbox_type == 1:
                housing = _cut_tapped_hole(
                    housing, mounting_thread_d5, 2.0 * mounting_thread_d5,
                    (a, b, L["bottom"] - 0.1), (0.0, 0.0, 1.0))

    # The rear view puts Type-L d6 holes at m5 and Type-T holes on center.
    rear_z = (
        L["bottom"] + rear_hole_height_m5
        if gearbox_type == 0 else 0.0
    )
    for y in (-offset, offset):
        housing = _cut_tapped_hole(
            housing, rear_thread_d6, 2.0 * rear_thread_d6,
            (L["rear"] - 0.1, y, rear_z), (1.0, 0.0, 0.0))
    return housing


def _rounded_key_x(axis_end, shaft_radius, key_width_b2, key_height_h,
                   key_length_l3, key_end_margin_l4):
    center = axis_end - key_end_margin_l4 - 0.5 * key_length_l3
    return (
        cq.Workplane("XY", origin=(center, 0.0, shaft_radius - 0.08))
        .slot2D(key_length_l3, key_width_b2, 0.0)
        .extrude(key_height_h + 0.08)
        .val()
    )


def _rounded_key_z(center, shaft_radius, key_width_b2, key_height_h,
                   key_length_l3):
    return (
        cq.Workplane("YZ", origin=(shaft_radius - 0.08, 0.0, center))
        .slot2D(key_length_l3, key_width_b2, 90.0)
        .extrude(key_height_h + 0.08)
        .val()
    )


def _shaft_x(L, shaft_diameter_d1, key_width_b2, key_height_h,
             key_length_l3, key_end_margin_l4, shaft_end_thread_d7):
    r = 0.5 * shaft_diameter_d1
    end = L["input_shaft_end"]
    chamfer = min(0.50, 0.06 * shaft_diameter_d1)
    start = L["shaft_start"]
    shaft = cq.Solid.makeCylinder(
        r, end - chamfer - start,
        cq.Vector(start, 0.0, 0.0), cq.Vector(1.0, 0.0, 0.0))
    shaft = shaft.fuse(cq.Solid.makeCone(
        r, r - chamfer, chamfer,
        cq.Vector(end - chamfer, 0.0, 0.0), cq.Vector(1.0, 0.0, 0.0)))
    shaft = shaft.fuse(_rounded_key_x(
        end, r, key_width_b2, key_height_h, key_length_l3, key_end_margin_l4))
    return _cut_tapped_hole(
        shaft, shaft_end_thread_d7, 1.6 * shaft_end_thread_d7,
        (end + 0.1, 0.0, 0.0), (-1.0, 0.0, 0.0))


def _shaft_z(L, shaft_diameter_d1, key_width_b2, key_height_h,
             key_length_l3, key_end_margin_l4, shaft_end_thread_d7,
    gearbox_type):
    r = 0.5 * shaft_diameter_d1
    top_end = L["output_top_end"]
    bottom_end = (
        L["bottom"] - (top_end - L["top"])
        if gearbox_type == 1 else 0.0
    )
    chamfer = min(0.50, 0.06 * shaft_diameter_d1)
    if gearbox_type == 1:
        shaft = cq.Solid.makeCone(
            r - chamfer, r, chamfer,
            cq.Vector(0.0, 0.0, bottom_end), cq.Vector(0.0, 0.0, 1.0))
        body_start = bottom_end + chamfer
    else:
        shaft = None
        body_start = L["shaft_start"]
    body = cq.Solid.makeCylinder(
        r, top_end - chamfer - body_start,
        cq.Vector(0.0, 0.0, body_start), cq.Vector(0.0, 0.0, 1.0))
    shaft = body if shaft is None else shaft.fuse(body)
    shaft = shaft.fuse(cq.Solid.makeCone(
        r, r - chamfer, chamfer,
        cq.Vector(0.0, 0.0, top_end - chamfer), cq.Vector(0.0, 0.0, 1.0)))

    top_key_center = top_end - key_end_margin_l4 - 0.5 * key_length_l3
    shaft = shaft.fuse(_rounded_key_z(
        top_key_center, r, key_width_b2, key_height_h, key_length_l3))
    if gearbox_type == 1:
        bottom_key_center = bottom_end + key_end_margin_l4 + 0.5 * key_length_l3
        shaft = shaft.fuse(_rounded_key_z(
            bottom_key_center, r, key_width_b2, key_height_h, key_length_l3))

    thread_depth = 1.6 * shaft_end_thread_d7
    shaft = _cut_tapped_hole(
        shaft, shaft_end_thread_d7, thread_depth,
        (0.0, 0.0, top_end + 0.1), (0.0, 0.0, -1.0))
    if gearbox_type == 1:
        shaft = _cut_tapped_hole(
            shaft, shaft_end_thread_d7, thread_depth,
            (0.0, 0.0, bottom_end - 0.1), (0.0, 0.0, 1.0))
    return shaft


def _bearing_z(shaft_diameter_d1, bearing_boss_diameter_d2, width):
    """One connected chamfered ring representing one sealed ball bearing."""
    inner = 0.5 * shaft_diameter_d1
    outer = 0.5 * bearing_boss_diameter_d2
    chamfer = min(0.35, 0.12 * width, 0.18 * (outer - inner))
    z0 = -0.5 * width
    z1 = 0.5 * width
    points = [
        cq.Vector(inner + chamfer, 0.0, z0),
        cq.Vector(outer - chamfer, 0.0, z0),
        cq.Vector(outer, 0.0, z0 + chamfer),
        cq.Vector(outer, 0.0, z1 - chamfer),
        cq.Vector(outer - chamfer, 0.0, z1),
        cq.Vector(inner + chamfer, 0.0, z1),
        cq.Vector(inner, 0.0, z1 - chamfer),
        cq.Vector(inner, 0.0, z0 + chamfer),
        cq.Vector(inner + chamfer, 0.0, z0),
    ]
    wire = cq.Wire.makePolygon(points)
    return cq.Solid.revolve(
        cq.Face.makeFromWires(wire), 360.0,
        cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0))


def _involute_section(pitch_r, module, teeth, tooth_fraction):
    """One transverse section of the gear as a true INVOLUTE profile.

    Tredgold's substitute: the section is the spur gear of `teeth` teeth at
    this pitch radius and local module. Flanks are involutes of the base
    circle r_b = r_p*cos(alpha); below the base circle the flank continues as
    a radial line down to the root circle, which is where a real tooth
    carries its fillet. `tooth_fraction` is the share of the circular pitch
    the tooth occupies at the pitch line, so the published backlash is cut
    into the tooth thickness rather than added afterwards."""
    pa = math.radians(PRESSURE_ANGLE_DEG)
    r_p = pitch_r
    r_b = r_p * math.cos(pa)
    r_a = r_p + ADDENDUM_FACTOR * module
    r_d = r_p - DEDENDUM_FACTOR * module
    inv_pa = math.tan(pa) - pa
    t_tip = math.sqrt(max(1e-9, (r_a / r_b) ** 2 - 1.0))
    psi = tooth_fraction * math.pi / teeth      # half tooth angle at the pitch

    def inv_xy(t, phi0, mirror):
        x = r_b * (math.cos(t) + t * math.sin(t))
        y = r_b * (math.sin(t) - t * math.cos(t))
        if mirror:
            y = -y
        c, s = math.cos(phi0), math.sin(phi0)
        return x * c - y * s, x * s + y * c

    pts = []
    for i in range(teeth):
        tc = 2.0 * math.pi * i / teeth
        phi_r = tc - psi - inv_pa
        phi_l = tc + psi + inv_pa
        gap = tc - math.pi / teeth
        pts.append((r_d * math.cos(gap), r_d * math.sin(gap)))
        pts.append((r_d * math.cos(phi_r), r_d * math.sin(phi_r)))
        for j in range(INVOLUTE_STEPS + 1):
            pts.append(inv_xy(t_tip * j / INVOLUTE_STEPS, phi_r, False))
        pts.append((r_a * math.cos(tc), r_a * math.sin(tc)))
        for j in range(INVOLUTE_STEPS, -1, -1):
            pts.append(inv_xy(t_tip * j / INVOLUTE_STEPS, phi_l, True))
        pts.append((r_d * math.cos(phi_l), r_d * math.sin(phi_l)))
    return [(round(x, 4), round(y, 4)) for x, y in pts]


def _bevel_gear_z(L, shaft_diameter_d1):
    """45-degree straight bevel gear about +Z, lofted between the involute
    section at the toe and the one at the heel. Both sections carry the same
    tooth count and a module proportional to the cone distance, so the flanks,
    tip cone and root cone all run through the pitch apex."""
    s_i = L["gear_s_inner"]
    s_o = L["gear_s_outer"]
    teeth = L["gear_teeth"]
    module = L["gear_module"]          # OUTER transverse module
    frac = L["gear_tooth_fraction"]
    pts_i = _involute_section(s_i, module * s_i / s_o, teeth, frac)
    pts_o = _involute_section(s_o, module, teeth, frac)
    gear = (
        cq.Workplane("XY").workplane(offset=s_i).polyline(pts_i).close()
        .workplane(offset=s_o - s_i).polyline(pts_o).close()
        .loft(ruled=True)
    )
    hub_start = s_i - L["gear_hub_length"]
    hub_outer = max(0.5 * shaft_diameter_d1 + 0.18 * module,
                    0.65 * s_i * (1.0 - 2.0 * DEDENDUM_FACTOR / teeth))
    hub = cq.Solid.makeCylinder(
        hub_outer, L["gear_hub_length"] + 0.20 * module,
        cq.Vector(0.0, 0.0, hub_start), cq.Vector(0.0, 0.0, 1.0))
    gear = gear.union(cq.Workplane(obj=hub))
    bore = cq.Solid.makeCylinder(
        0.5 * shaft_diameter_d1,
        s_o - hub_start + 1.0,
        cq.Vector(0.0, 0.0, hub_start - 0.5), cq.Vector(0.0, 0.0, 1.0))
    return gear.cut(cq.Workplane(obj=bore)).val()


def _rotation_x(degrees):
    return cq.Location(cq.Vector(0.0, 0.0, 0.0), cq.Vector(1.0, 0.0, 0.0), degrees)


def _rotation_z(degrees):
    return cq.Location(cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0), degrees)


def build(
    catalog_index,
    gearbox_type,
    housing_size_b1,
    shaft_diameter_d1,
    key_width_b2,
    bearing_boss_diameter_d2,
    key_height_h,
    housing_length_l1,
    shaft_projection_l2,
    key_length_l3,
    key_end_margin_l4,
    input_axis_height_m1,
    bearing_inset_t1,
    shaft_reach_t2,
    mounting_hole_diameter_d4,
    mounting_thread_d5,
    rear_thread_d6,
    shaft_end_thread_d7,
    lower_hole_offset_m2,
    upper_hole_offset_m3,
    face_hole_spacing_m4,
    rear_hole_height_m5,
    shaft_rotation_deg,
):
    """Return the fixed nine-solid GN 3971 benchmark assembly."""
    _ = catalog_index
    L = _layout(
        housing_size_b1, shaft_diameter_d1, bearing_boss_diameter_d2,
        housing_length_l1, shaft_projection_l2, input_axis_height_m1,
        bearing_inset_t1, shaft_reach_t2, gearbox_type)

    housing = _housing(
        L, housing_size_b1, shaft_diameter_d1, bearing_boss_diameter_d2,
        housing_length_l1, input_axis_height_m1, bearing_inset_t1,
        shaft_reach_t2, mounting_hole_diameter_d4, mounting_thread_d5,
        rear_thread_d6, lower_hole_offset_m2, upper_hole_offset_m3,
        face_hole_spacing_m4, rear_hole_height_m5, gearbox_type)
    input_shaft = _shaft_x(
        L, shaft_diameter_d1, key_width_b2, key_height_h,
        key_length_l3, key_end_margin_l4, shaft_end_thread_d7)
    output_shaft = _shaft_z(
        L, shaft_diameter_d1, key_width_b2, key_height_h,
        key_length_l3, key_end_margin_l4, shaft_end_thread_d7, gearbox_type)

    output_gear = _bevel_gear_z(L, shaft_diameter_d1)
    input_gear = output_gear.rotate(
        cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0), 90.0)
    # A half-pitch phase puts an input tooth in an output gap.  Equal and
    # opposite angular displacement then preserves the 1:1 bevel mesh.
    mesh_phase = 180.0 / L["gear_teeth"]
    input_gear = input_gear.rotate(
        cq.Vector(0.0, 0.0, 0.0), cq.Vector(1.0, 0.0, 0.0), mesh_phase)

    bearing_z = _bearing_z(
        shaft_diameter_d1, bearing_boss_diameter_d2, L["bearing_width"])
    bearing_x = bearing_z.rotate(
        cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0), 90.0)

    input_angle = shaft_rotation_deg
    output_angle = -shaft_rotation_deg
    result = cq.Assembly(name="gn3971_bevel_gear_box")
    result.add(housing, name="housing")
    result.add(input_shaft, name="input_shaft", loc=_rotation_x(input_angle))
    result.add(output_shaft, name="output_shaft", loc=_rotation_z(output_angle))
    result.add(input_gear, name="input_gear", loc=_rotation_x(input_angle))
    result.add(output_gear, name="output_gear", loc=_rotation_z(output_angle))
    result.add(
        bearing_x, name="input_bearing_01",
        loc=cq.Location(cq.Vector(L["input_front_bearing"], 0.0, 0.0)))
    result.add(
        bearing_x, name="input_bearing_02",
        loc=cq.Location(cq.Vector(L["input_rear_bearing"], 0.0, 0.0)))
    result.add(
        bearing_z, name="output_bearing_01",
        loc=cq.Location(cq.Vector(0.0, 0.0, L["output_top_bearing"])))
    result.add(
        bearing_z, name="output_bearing_02",
        loc=cq.Location(cq.Vector(0.0, 0.0, L["output_second_bearing"])))
    return result
