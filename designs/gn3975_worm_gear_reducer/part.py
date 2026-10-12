"""Parametric CadQuery reconstruction of a Ganter GN 3975 reducer.

The public sheet controls the housing, shaft, mounting, and output interface
dimensions.  Worm module, tooth form, bearing section, and internal clearances
are documented proportions because Ganter does not publish those manufacturing
details.  The assembly keeps seven named solids: housing, worm/drive shaft,
worm wheel/output hub, two drive bearings, and two output bearings.
"""

import cadquery as cq
import math


WORM_STARTS = 2                 # proportion; not inferred from the ratio
MAX_VISUAL_TEETH = 48           # keeps the render deterministic and light


def _wp(shape):
    return cq.Workplane("XY").newObject([shape])


def _cyl_x(diameter, length, start_x, y=0.0, z=0.0):
    return _wp(cq.Solid.makeCylinder(
        diameter / 2.0, length,
        cq.Vector(start_x, y, z), cq.Vector(1.0, 0.0, 0.0)))


def _cyl_y(diameter, length, start_y, x=0.0, z=0.0):
    return _wp(cq.Solid.makeCylinder(
        diameter / 2.0, length,
        cq.Vector(x, start_y, z), cq.Vector(0.0, 1.0, 0.0)))


def _cyl_z(diameter, length, start_z, x=0.0, y=0.0):
    return _wp(cq.Solid.makeCylinder(
        diameter / 2.0, length,
        cq.Vector(x, y, start_z), cq.Vector(0.0, 0.0, 1.0)))


def _box(x, y, z, center):
    return cq.Workplane("XY").box(x, y, z).translate(center)


def _ring_x(outer_d, inner_d, width, center_x, y):
    ring = _cyl_x(outer_d, width, center_x - width / 2.0, y, 0.0)
    bore = _cyl_x(inner_d, width + 0.4, center_x - width / 2.0 - 0.2, y, 0.0)
    return ring.cut(bore)


def _ring_z(outer_d, inner_d, width, center_z, y):
    ring = _cyl_z(outer_d, width, center_z - width / 2.0, 0.0, y)
    bore = _cyl_z(inner_d, width + 0.4, center_z - width / 2.0 - 0.2, 0.0, y)
    return ring.cut(bore)


def _capsule_key_x(length, radial_height, width, center_x, start_y, z=0.0):
    """Raised parallel key with semicircular plan ends, axis along X."""
    radius = width / 2.0
    center_pitch = max(length - 2.0 * radius, 0.2)
    body = _box(
        center_pitch, radial_height, width,
        (center_x, start_y + radial_height / 2.0, z))
    left = _cyl_y(
        width, radial_height, start_y,
        center_x - center_pitch / 2.0, z)
    right = _cyl_y(
        width, radial_height, start_y,
        center_x + center_pitch / 2.0, z)
    return body.union(left).union(right)


def _internal_layout(housing_size_m1, housing_face_width_b1, housing_overall_length_l1,
                     drive_shaft_diameter_d1, output_bore_diameter_d2):
    """Return deterministic proportion dimensions for unpublished internals."""
    depth = float(housing_overall_length_l1)
    wheel_r = max(0.18 * depth, 0.75 * output_bore_diameter_d2)
    wheel_t = max(0.16 * housing_face_width_b1, 4.0)
    tooth_depth = max(0.8, 0.06 * wheel_r)
    worm_r = 0.5 * drive_shaft_diameter_d1 + 0.8
    # GN 3975's size designation is the published shaft-axis centre distance.
    # Keeping the output axis at y=0 therefore places the worm axis at y=m1.
    worm_y = float(housing_size_m1)
    bearing_width = max(2.0, 0.10 * output_bore_diameter_d2)
    return {
        "depth": depth,
        "wheel_r": wheel_r,
        "wheel_t": wheel_t,
        "tooth_depth": tooth_depth,
        "worm_r": worm_r,
        "worm_y": worm_y,
        "bearing_width": bearing_width,
        "clearance": max(0.35, 0.015 * housing_face_width_b1),
    }


def _housing(
    gearbox_type,
    housing_size_m1,
    housing_face_width_b1,
    drive_shaft_diameter_d1,
    output_bore_diameter_d2,
    output_hub_outer_diameter_d3,
    secondary_interface_diameter_d4,
    bearing_interface_diameter_d5,
    housing_overall_length_l1,
    output_interface_length_l3,
    axial_offset_t1,
    mounting_thread_d6,
    clearance_hole_d7,
    mounting_spacing_m2,
    mounting_spacing_m3,
    mounting_offset_m4,
    mounting_offset_m5,
    mounting_spacing_m6,
    mounting_spacing_m7,
    mounting_spacing_m8,
    mounting_spacing_m9,
    mounting_spacing_m10,
    mounting_spacing_m11,
):
    dims = _internal_layout(
        housing_size_m1, housing_face_width_b1, housing_overall_length_l1,
        drive_shaft_diameter_d1, output_bore_diameter_d2)
    depth = dims["depth"]
    half_x = housing_overall_length_l1 / 2.0
    half_y = depth / 2.0
    half_z = housing_face_width_b1 / 2.0
    # The drawing locates the drive axis m8 from the lower housing edge; the
    # output axis is one centre distance m1 below it.  Keeping the output axis
    # at y=0 therefore offsets the rectangular housing by this amount.
    output_from_lower_edge = mounting_spacing_m8 - housing_size_m1
    housing_y = half_y - output_from_lower_edge
    clearance = dims["clearance"]

    housing = _box(housing_overall_length_l1, depth, housing_face_width_b1,
                   (0.0, housing_y, 0.0))

    # Drive tunnel and the tangent worm chamber.
    housing = housing.cut(_cyl_x(
        drive_shaft_diameter_d1 + 1.0, housing_overall_length_l1 + 2.0,
        -half_x - 1.0, dims["worm_y"], 0.0))
    housing = housing.cut(_cyl_x(
        2.0 * (dims["worm_r"] + clearance), housing_overall_length_l1 + 2.0,
        -half_x - 1.0, dims["worm_y"], 0.0))

    # The drawing shows a larger drive-bearing register around the shaft.
    # Type A exposes it on the single drive side; Type B has the through-shaft
    # register on both faces.  It is a recess in the housing, not another
    # benchmark solid.
    register_depth = max(0.8, min(axial_offset_t1, 0.10 * bearing_interface_diameter_d5))
    inner_register_depth = register_depth + 0.30
    drive_faces = (1.0,) if gearbox_type == 1 else (-1.0, 1.0)
    for face in drive_faces:
        register_start = (half_x - register_depth + 0.01
                          if face > 0 else -half_x - 0.01)
        housing = housing.cut(_cyl_x(
            output_hub_outer_diameter_d3, register_depth + 0.02,
            register_start, dims["worm_y"], 0.0))
        inner_start = (half_x - inner_register_depth + 0.01
                       if face > 0 else -half_x - 0.01)
        housing = housing.cut(_cyl_x(
            bearing_interface_diameter_d5, inner_register_depth + 0.02,
            inner_start, dims["worm_y"], 0.0))

    # Wheel chamber and stepped output-bearing seat.  The official STEP keeps
    # both output faces flush with the housing: d5 is the through bearing seat
    # and d3 is the larger, shallow face register on the top and bottom.
    wheel_outer = dims["wheel_r"] + dims["tooth_depth"] + clearance
    housing = housing.cut(_cyl_z(
        2.0 * wheel_outer, dims["wheel_t"] + 2.0,
        -dims["wheel_t"] / 2.0 - 1.0, 0.0, 0.0))
    housing = housing.cut(_cyl_z(
        bearing_interface_diameter_d5 + 2.0 * clearance,
        housing_face_width_b1 + 2.0,
        -half_z - 1.0, 0.0, 0.0))
    output_face_depth = max(
        0.8, min(axial_offset_t1, output_interface_length_l3 / 2.0))
    housing = housing.cut(_cyl_z(
        output_hub_outer_diameter_d3,
        output_face_depth + 0.02, half_z - output_face_depth,
        0.0, 0.0))
    housing = housing.cut(_cyl_z(
        output_hub_outer_diameter_d3,
        output_face_depth + 0.02, -half_z - 0.02,
        0.0, 0.0))

    # Six through holes follow the three official rows around the offset
    # output axis.  For size 20 these resolve exactly to the STEP centres
    # (x, y)=(+/-25,-17.5), (+/-25,1.5), (+/-15.5,33).
    top_points = [
        (-mounting_spacing_m3 / 2.0, -mounting_offset_m4),
        (mounting_spacing_m3 / 2.0, -mounting_offset_m4),
        (-mounting_spacing_m3 / 2.0, mounting_offset_m5),
        (mounting_spacing_m3 / 2.0, mounting_offset_m5),
        (-mounting_spacing_m6 / 2.0, mounting_spacing_m11),
        (mounting_spacing_m6 / 2.0, mounting_spacing_m11),
    ]
    for x, y in top_points:
        housing = housing.cut(_cyl_z(
            clearance_hole_d7, housing_face_width_b1 + 2.0,
            -half_z - 1.0, x, y))

    # Four M-size blind holes on each output face.  The official size-20 STEP
    # places them at (+/-13,+/-13), distinct from the six d7 through holes.
    blind_depth = 2.0 * mounting_thread_d6 + 0.5
    blind_points = [
        (sx * mounting_spacing_m2 / 2.0, sy * mounting_spacing_m2 / 2.0)
        for sx in (-1.0, 1.0)
        for sy in (-1.0, 1.0)
    ]
    for x, y in blind_points:
        housing = housing.cut(_cyl_z(
            0.82 * mounting_thread_d6, blind_depth + 0.01,
            half_z - blind_depth, x, y))
        housing = housing.cut(_cyl_z(
            0.82 * mounting_thread_d6, blind_depth + 0.01,
            -half_z - 0.01, x, y))

    # The four shallow threaded holes occur only on the positive-Y broad face,
    # at the drawing's m9 by m10 pattern.  A nominal d6 core and 1.6*d6 thread
    # depth follow the issue's stated usable-depth rule.
    side_x = min(abs(mounting_spacing_m9 / 2.0), half_x - mounting_thread_d6)
    side_z = min(abs(mounting_spacing_m10 / 2.0), half_z - mounting_thread_d6)
    side_depth = blind_depth
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            x = sx * side_x
            z = sz * side_z
            housing = housing.cut(_cyl_y(
                0.82 * mounting_thread_d6, side_depth + 0.2,
                housing_y + half_y - side_depth, x, z))

    # Both drive-end faces carry the drawing's m7 by m7 square pattern.
    end_y = min(abs(mounting_spacing_m7 / 2.0),
                half_y - mounting_thread_d6)
    end_z = min(abs(mounting_spacing_m7 / 2.0),
                half_z - mounting_thread_d6)
    for sy in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            y = dims["worm_y"] + sy * end_y
            z = sz * end_z
            housing = housing.cut(_cyl_x(
                0.82 * mounting_thread_d6, side_depth + 0.2,
                half_x - side_depth, y, z))
            housing = housing.cut(_cyl_x(
                0.82 * mounting_thread_d6, side_depth + 0.2,
                -half_x - 0.2, y, z))

    return housing


def _drive_shaft(
    gearbox_type,
    housing_size_m1,
    drive_shaft_diameter_d1,
    drive_keyway_width_b2,
    keyway_depth_h,
    housing_overall_length_l1,
    drive_shaft_projection_l2,
    drive_key_length_l3,
    shaft_end_margin_l4,
    shaft_end_length_t4,
    shaft_end_thread_d8,
    output_bore_diameter_d2,
):
    dims = _internal_layout(housing_size_m1, 35.0, housing_overall_length_l1,
                            drive_shaft_diameter_d1, output_bore_diameter_d2)
    worm_y = dims["worm_y"]
    half_x = housing_overall_length_l1 / 2.0
    # Type A (1) has the catalog drive extension on one side only.  Type B
    # (2) is the through-shaft version and exposes the same extension at both
    # housing faces.
    start = -half_x - (drive_shaft_projection_l2 if gearbox_type == 2 else 0.0)
    end = half_x + drive_shaft_projection_l2
    shaft = _cyl_x(drive_shaft_diameter_d1, end - start, start, worm_y, 0.0)
    shaft = shaft.edges("%CIRCLE").chamfer(0.5)

    # A two-start proportion is rendered as four broad worm lands; it is not
    # used to infer the catalog ratio or tooth count.
    pitch = max(4.0, housing_overall_length_l1 / 8.0)
    land_width = 0.42 * pitch
    land_r = dims["worm_r"]
    for i in range(4):
        cx = -1.5 * pitch + i * pitch
        land = _cyl_x(2.0 * land_r, land_width,
                       cx - land_width / 2.0, worm_y, 0.0)
        shaft = shaft.union(land)

    # DIN 6885-1 keys on the externally projecting ends.  The official STEP
    # uses a 4 mm wide capsule plan (R2 semicircular ends), starts one quarter
    # key-width beyond the housing face, and keeps the l4 end margin.
    key_start_y = (
        worm_y + drive_shaft_diameter_d1 / 2.0 - 0.01)
    positive_key_start = half_x + 0.25 * drive_keyway_width_b2
    positive_key_end = end - shaft_end_margin_l4
    external_key_length = min(
        drive_key_length_l3, positive_key_end - positive_key_start)
    positive_key_x = positive_key_end - external_key_length / 2.0
    positive_key = _capsule_key_x(
        external_key_length, keyway_depth_h, drive_keyway_width_b2,
        positive_key_x, key_start_y)
    shaft = shaft.union(positive_key)
    if gearbox_type == 2:
        negative_key_start = start + shaft_end_margin_l4
        negative_key_end = -half_x - 0.25 * drive_keyway_width_b2
        negative_key_length = min(
            drive_key_length_l3, negative_key_end - negative_key_start)
        negative_key_x = negative_key_start + negative_key_length / 2.0
        negative_key = _capsule_key_x(
            negative_key_length, keyway_depth_h, drive_keyway_width_b2,
            negative_key_x, key_start_y)
        shaft = shaft.union(negative_key)

    # Simplified internal tapped sockets on the visible drive ends.
    # The supplied Type B STEP shows a 10 mm socket depth for d8=M5; this also
    # exceeds the issue's 1.6*d minimum usable thread engagement.
    thread_depth = min(2.0 * shaft_end_thread_d8, shaft_end_length_t4)
    shaft = shaft.cut(_cyl_x(
        0.84 * shaft_end_thread_d8, thread_depth,
        end - thread_depth, worm_y, 0.0))
    if gearbox_type == 2:
        shaft = shaft.cut(_cyl_x(
            0.84 * shaft_end_thread_d8, thread_depth,
            start - 0.01, worm_y, 0.0))
    return shaft


def _worm_wheel(
    housing_size_m1,
    housing_face_width_b1,
    drive_shaft_diameter_d1,
    output_keyway_width_b3,
    output_bore_diameter_d2,
    output_hub_outer_diameter_d3,
    secondary_interface_diameter_d4,
    bearing_interface_diameter_d5,
    housing_overall_length_l1,
    output_interface_length_l3,
    axial_offset_t1,
    gear_ratio_i,
):
    dims = _internal_layout(
        housing_size_m1, housing_face_width_b1, housing_overall_length_l1,
        drive_shaft_diameter_d1, output_bore_diameter_d2)
    r = dims["wheel_r"]
    t = dims["wheel_t"]
    tooth_depth = dims["tooth_depth"]
    wheel = cq.Workplane("XY").circle(r).extrude(t).translate((0.0, 0.0, -t / 2.0))

    visual_teeth = min(MAX_VISUAL_TEETH, max(12, int(round(gear_ratio_i))))
    tooth_width = max(0.7, 2.0 * math.pi * r / visual_teeth * 0.55)
    for i in range(visual_teeth):
        angle = 360.0 * i / visual_teeth
        tooth = _box(
            tooth_depth + 0.5, tooth_width, t,
            (r + tooth_depth / 2.0 - 0.2, 0.0, 0.0),
        ).rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
        wheel = wheel.union(tooth)

    # Recessed two-sided output hub reconstructed from the public d3/d4/d5 and
    # t1/l3 dimensions.  The official size-20 STEP exposes concentric diameters
    # 30, 29, 23, and 12 mm at each housing face; the 29/23 mm seal details are
    # documented visual proportions around the published d3/d4/d2 interfaces.
    half_z = housing_face_width_b1 / 2.0
    face_depth = max(0.8, min(axial_offset_t1, output_interface_length_l3 / 2.0))
    face_z = half_z - face_depth
    neck = _cyl_z(
        secondary_interface_diameter_d4, 2.0 * face_z,
        -face_z, 0.0, 0.0)
    internal_hub_length = min(
        output_interface_length_l3, housing_face_width_b1 - 2.0 * face_depth)
    internal_hub = _cyl_z(
        bearing_interface_diameter_d5, internal_hub_length,
        -internal_hub_length / 2.0, 0.0, 0.0)
    face_flange_d = output_hub_outer_diameter_d3 - 1.0
    face_flange_t = max(0.6, 0.30 * face_depth)
    top_flange = _cyl_z(
        face_flange_d, face_flange_t,
        face_z - face_flange_t, 0.0, 0.0)
    bottom_flange = _cyl_z(
        face_flange_d, face_flange_t,
        -face_z, 0.0, 0.0)
    face_boss_d = min(
        face_flange_d - 1.0,
        secondary_interface_diameter_d4 + 0.75 * output_keyway_width_b3)
    face_boss_h = min(0.40, 0.20 * face_depth)
    top_boss = _cyl_z(
        face_boss_d, face_boss_h,
        face_z, 0.0, 0.0)
    bottom_boss = _cyl_z(
        face_boss_d, face_boss_h,
        -face_z - face_boss_h, 0.0, 0.0)
    wheel = wheel.union(neck).union(internal_hub).union(top_flange).union(bottom_flange)
    wheel = wheel.union(top_boss).union(bottom_boss)

    bore = _cyl_z(
        output_bore_diameter_d2, housing_face_width_b1 + 2.0,
        -half_z - 1.0, 0.0, 0.0)
    wheel = wheel.cut(bore)
    key_depth = max(0.8, 0.45 * output_keyway_width_b3)
    key_cut = _box(
        output_keyway_width_b3, key_depth, housing_face_width_b1 + 2.0,
        (0.0, -output_bore_diameter_d2 / 2.0 - key_depth / 2.0, 0.0),
    )
    return wheel.cut(key_cut)


def build(
    catalog_index,
    gearbox_type,
    housing_size_m1,
    gear_ratio_i,
    housing_face_width_b1,
    drive_shaft_diameter_d1,
    drive_keyway_width_b2,
    output_keyway_width_b3,
    output_bore_diameter_d2,
    output_hub_outer_diameter_d3,
    secondary_interface_diameter_d4,
    bearing_interface_diameter_d5,
    keyway_depth_h,
    housing_overall_length_l1,
    drive_shaft_projection_l2,
    output_interface_length_l3,
    shaft_end_margin_l4,
    axial_offset_t1,
    keyway_length_t2,
    radial_offset_t3,
    shaft_end_length_t4,
    mounting_thread_d6,
    clearance_hole_d7,
    shaft_end_thread_d8,
    mounting_spacing_m2,
    mounting_spacing_m3,
    mounting_offset_m4,
    mounting_offset_m5,
    mounting_spacing_m6,
    mounting_spacing_m7,
    mounting_spacing_m8,
    mounting_spacing_m9,
    mounting_spacing_m10,
    mounting_spacing_m11,
    input_rotation_deg,
):
    """Return the fixed seven-solid GN 3975 assembly."""
    _ = (catalog_index, keyway_length_t2, radial_offset_t3)
    dims = _internal_layout(
        housing_size_m1, housing_face_width_b1, housing_overall_length_l1,
        drive_shaft_diameter_d1, output_bore_diameter_d2)
    housing = _housing(
        gearbox_type, housing_size_m1, housing_face_width_b1, drive_shaft_diameter_d1,
        output_bore_diameter_d2, output_hub_outer_diameter_d3,
        secondary_interface_diameter_d4, bearing_interface_diameter_d5,
        housing_overall_length_l1, output_interface_length_l3, axial_offset_t1,
        mounting_thread_d6, clearance_hole_d7, mounting_spacing_m2,
        mounting_spacing_m3, mounting_offset_m4, mounting_offset_m5,
        mounting_spacing_m6, mounting_spacing_m7, mounting_spacing_m8,
        mounting_spacing_m9, mounting_spacing_m10, mounting_spacing_m11)
    shaft = _drive_shaft(
        gearbox_type, housing_size_m1, drive_shaft_diameter_d1, drive_keyway_width_b2,
        keyway_depth_h, housing_overall_length_l1, drive_shaft_projection_l2,
        output_interface_length_l3, shaft_end_margin_l4, shaft_end_length_t4,
        shaft_end_thread_d8, output_bore_diameter_d2)
    wheel = _worm_wheel(
        housing_size_m1, housing_face_width_b1, drive_shaft_diameter_d1, output_keyway_width_b3,
        output_bore_diameter_d2, output_hub_outer_diameter_d3,
        secondary_interface_diameter_d4, bearing_interface_diameter_d5,
        housing_overall_length_l1, output_interface_length_l3,
        axial_offset_t1, gear_ratio_i)

    # Bearings are simplified sealed rings.  They remain separate assembly
    # solids and sit in the pockets cut into the housing.
    width = dims["bearing_width"]
    drive_x = housing_overall_length_l1 / 2.0 - axial_offset_t1 - width / 2.0
    output_z = housing_face_width_b1 / 2.0 - axial_offset_t1 - width / 2.0
    drive_bearing = _ring_x(
        bearing_interface_diameter_d5, drive_shaft_diameter_d1,
        width, drive_x, dims["worm_y"])
    output_bearing = _ring_z(
        bearing_interface_diameter_d5, secondary_interface_diameter_d4,
        width, output_z, 0.0)

    input_angle = float(input_rotation_deg)
    output_angle = -input_angle / float(gear_ratio_i)
    shaft = shaft.rotate(
        (0.0, dims["worm_y"], 0.0),
        (1.0, dims["worm_y"], 0.0), input_angle)
    wheel = wheel.rotate(
        (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), output_angle)

    result = cq.Assembly(name="gn3975_worm_gear_reducer")
    result.add(housing, name="housing")
    result.add(shaft, name="drive_shaft")
    result.add(wheel, name="worm_wheel")
    result.add(drive_bearing, name="drive_bearing_01")
    result.add(
        drive_bearing,
        name="drive_bearing_02",
        loc=cq.Location(cq.Vector(-2.0 * drive_x, 0.0, 0.0)),
    )
    result.add(output_bearing, name="output_bearing_01")
    result.add(
        output_bearing,
        name="output_bearing_02",
        loc=cq.Location(cq.Vector(0.0, 0.0, -2.0 * output_z)),
    )
    return result
