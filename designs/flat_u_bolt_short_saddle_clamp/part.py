import math
import cadquery as cq


def _metric_fastener_dimensions(nominal_d):
    # ISO 261/68-1 thread data with ISO 4017 head and ISO 4032 nut envelopes.
    rows = {
        10.0: (1.50, 16.0, 6.4, 16.0, 8.4),
        12.0: (1.75, 18.0, 7.5, 18.0, 10.8),
        16.0: (2.00, 24.0, 10.0, 24.0, 14.8),
        20.0: (2.50, 30.0, 12.5, 30.0, 18.0),
        24.0: (3.00, 36.0, 15.0, 36.0, 21.5),
    }
    return rows[float(nominal_d)]


def _modeled_external_metric_thread(nominal_d, pitch, length):
    major_r = nominal_d / 2.0
    root_r = (nominal_d - 1.226869 * pitch) / 2.0
    radial_embed = min(0.08, 0.05 * pitch)
    half_width = (major_r - root_r + radial_embed) / math.sqrt(3.0)
    path_r = (major_r + root_r) / 2.0
    path_height = length - 2.0 * half_width
    core = cq.Workplane("XY").circle(root_r).extrude(length)
    path = cq.Wire.makeHelix(pitch, path_height, path_r)
    profile = (cq.Workplane("XZ")
               .polyline([(root_r - radial_embed, -half_width),
                          (major_r, 0.0),
                          (root_r - radial_embed, half_width)])
               .close())
    ridge = profile.sweep(path, isFrenet=True).translate((0.0, 0.0, half_width))
    return core.union(ridge)


def _modeled_internal_metric_groove(nominal_d, pitch, length):
    major_r = nominal_d / 2.0
    minor_r = (nominal_d - 1.082532 * pitch) / 2.0
    radial_embed = min(0.08, 0.05 * pitch)
    half_width = (major_r - minor_r + radial_embed) / math.sqrt(3.0)
    path = cq.Wire.makeHelix(pitch, length + 2.0 * half_width, minor_r)
    profile = (cq.Workplane("XZ")
               .polyline([(minor_r - radial_embed, -half_width),
                          (major_r, 0.0),
                          (minor_r - radial_embed, half_width)])
               .close())
    return profile.sweep(path, isFrenet=True).translate((0.0, 0.0, -half_width))


def _iso_hex_nut(nominal_d):
    pitch, _head_af, _head_h, across_flats, height = _metric_fastener_dimensions(nominal_d)
    corner_d = across_flats / math.cos(math.pi / 6.0)
    blank = cq.Workplane("XY").polygon(6, corner_d).extrude(height).val()
    chamfer_h = min(0.12 * height, 0.30 * nominal_d)
    face_land_r = 0.475 * across_flats
    crown_r = corner_d / 2.0 + 0.01
    envelope = (cq.Workplane("XZ").moveTo(0.0, 0.0)
                .lineTo(face_land_r, 0.0).lineTo(crown_r, chamfer_h)
                .lineTo(crown_r, height - chamfer_h).lineTo(face_land_r, height)
                .lineTo(0.0, height).close()
                .revolve(360.0, (0.0, 0.0), (0.0, 1.0)).val())
    minor_d = nominal_d - 1.082532 * pitch
    bore = cq.Workplane("XY").circle(minor_d / 2.0).extrude(height).val()
    nut = blank.intersect(envelope).cut(bore)
    groove = _modeled_internal_metric_groove(nominal_d, pitch, height).val()
    return cq.Workplane(obj=nut.cut(groove))


def _iso_hex_bolt(nominal_d, length):
    pitch, head_af, head_h, _nut_af, _nut_h = _metric_fastener_dimensions(nominal_d)
    # The catalogue permits ISO 4014 / 4017.  Use a visible full-thread 4017
    # representation so the sourced MxL interface remains explicit.
    shank = _modeled_external_metric_thread(nominal_d, pitch, length)
    corner_d = head_af / math.cos(math.pi / 6.0)
    head = cq.Workplane("XY").polygon(6, corner_d).extrude(head_h)
    return head.union(shank.translate((0.0, 0.0, head_h)))


def build(catalog_row, d1, l1, l2, h1, h2, h3, b1, b1_t, b2, h4,
          l3, l4, b3, d2, h5, h6, h7, bolt_d, bolt_l):
    del catalog_row
    # Drawing 01: L2 is the leg-axis pitch; H2 is the arch spring-line and
    # H1 the overall top height above the U-profile datum.  The published
    # envelope is mildly elliptical rather than inferred from pipe D1.
    outer_rx = l2 / 2.0 + b1_t / 2.0
    inner_rx = l2 / 2.0 - b1_t / 2.0
    outer_rz = h1 - h2
    inner_rz = outer_rz - b1_t
    leg_x = l2 / 2.0
    arch = (cq.Workplane("XZ").ellipse(outer_rx, outer_rz)
            .ellipse(inner_rx, inner_rz).extrude(b1 / 2.0, both=True)
            .intersect(cq.Workplane("XY").box(2.2 * outer_rx, 1.2 * b1, outer_rz)
                       .translate((0.0, 0.0, outer_rz / 2.0)))
            .translate((0.0, 0.0, h2)))
    leg_bottom = h4 - h3
    # Overlap the tangent legs into the annular arch so the bent flat steel is
    # one positive-volume solid rather than three merely coincident bodies.
    leg_h = h2 + b1_t - leg_bottom
    legs = (cq.Workplane("XY").box(b1_t, b1, leg_h)
            .translate((-leg_x, 0.0, leg_bottom + leg_h / 2.0))
            .union(cq.Workplane("XY").box(b1_t, b1, leg_h)
                   .translate((leg_x, 0.0, leg_bottom + leg_h / 2.0))))
    flat_u_bolt = arch.union(legs)

    # The product evidence shows round threaded ends beneath the two flat-bar
    # legs. Use the catalogue's MxL fastener diameter as the row-coupled end
    # size; the bent arch and upper legs remain flat steel.
    pitch, _head_af, _head_h, _nut_af, nut_h = _metric_fastener_dimensions(bolt_d)
    stud_bottom = leg_bottom
    stud_top = h4 + nut_h + 0.5 * bolt_d
    stud_l = stud_top - stud_bottom
    for x in (-leg_x, leg_x):
        lower_flat = (cq.Workplane("XY").center(x, 0.0)
                      .rect(b1_t + 0.2, b1 + 0.2)
                      .extrude(stud_l).translate((0.0, 0.0, stud_bottom)))
        flat_u_bolt = flat_u_bolt.cut(lower_flat)
        threaded_end = _modeled_external_metric_thread(bolt_d, pitch, stud_l)
        flat_u_bolt = flat_u_bolt.union(threaded_end.translate((x, 0.0, stud_bottom)))

    # Drawing 13: L3/B3 are plan dimensions, L4/D2 the two-hole interface,
    # H5 is bottom-to-groove-low thickness, H6 total height, and H7 is the
    # downward interface boss.  The saddle rests on the channel at Z=H4.
    saddle = (cq.Workplane("XY").box(l3, b3, h6)
              .translate((0.0, 0.0, h4 + h6 / 2.0)))
    groove_center_z = h4 + h5 + d1 / 2.0
    saddle = saddle.cut(cq.Workplane("XZ").circle(d1 / 2.0)
                        .extrude(b3 / 2.0 + 1.0, both=True)
                        .translate((0.0, 0.0, groove_center_z)))
    # DN40 alone has L4 staggered by 90 degrees; retaining the row's spacing
    # on Y keeps that published special case valid when L4 > L3.
    hole_points = [(0.0, -l4 / 2.0), (0.0, l4 / 2.0)] if l4 > l3 else [(-l4 / 2.0, 0.0), (l4 / 2.0, 0.0)]
    for x, y in hole_points:
        saddle = saddle.cut(cq.Workplane("XY").center(x, y).circle(d2 / 2.0)
                            .extrude(h6 + 2.0).translate((0.0, 0.0, h4 - 1.0)))
        saddle = saddle.union(cq.Workplane("XY").center(x, y)
                              .circle(min(0.85 * d2, d2 / 2.0 + 0.2 * h7))
                              .circle(d2 / 2.0).extrude(h7)
                              .translate((0.0, 0.0, h4 - h7)))

    # Drawing 01: DIN 1026 profile is L1 long and B2 x H4 in section; H3 is
    # the published top-web thickness.
    channel_t = h3
    top = cq.Workplane("XY").box(l1, b2, channel_t).translate((0.0, 0.0, h4 - channel_t / 2.0))
    wall_y = b2 / 2.0 - channel_t / 2.0
    walls = (cq.Workplane("XY").box(l1, channel_t, h4)
             .translate((0.0, -wall_y, h4 / 2.0))
             .union(cq.Workplane("XY").box(l1, channel_t, h4)
                    .translate((0.0, wall_y, h4 / 2.0))))
    u_profile = top.union(walls)
    for x in (-leg_x, leg_x):
        u_profile = u_profile.cut(cq.Workplane("XY").center(x, 0.0)
                                  .rect(b1_t + 0.8, b1 + 0.8)
                                  .extrude(channel_t + 2.0)
                                  .translate((0.0, 0.0, h4 - channel_t - 1.0)))
    for x, y in hole_points:
        u_profile = u_profile.cut(cq.Workplane("XY").center(x, y).circle(d2 / 2.0)
                                  .extrude(channel_t + 2.0)
                                  .translate((0.0, 0.0, h4 - channel_t - 1.0)))

    nut_z = h4
    nut_1 = _iso_hex_nut(bolt_d).translate((-leg_x, 0.0, nut_z))
    nut_2 = _iso_hex_nut(bolt_d).translate((leg_x, 0.0, nut_z))
    # Bolts run upward through the channel top and saddle holes. Standard head
    # dimensions are proportion-based; catalogue bolt_l controls the shank.
    bolt_head_h = _metric_fastener_dimensions(bolt_d)[2]
    bolt_start_z = h4 - channel_t - bolt_head_h
    lower_bolt_1 = _iso_hex_bolt(bolt_d, bolt_l).translate((hole_points[0][0], hole_points[0][1], bolt_start_z))
    lower_bolt_2 = _iso_hex_bolt(bolt_d, bolt_l).translate((hole_points[1][0], hole_points[1][1], bolt_start_z))

    result = cq.Assembly(name="flat_u_bolt_short_saddle_clamp")
    result.add(flat_u_bolt, name="flat_u_bolt")
    result.add(saddle, name="saddle")
    result.add(u_profile, name="u_profile")
    result.add(nut_1, name="nut_01")
    result.add(nut_2, name="nut_02")
    result.add(lower_bolt_1, name="lower_bolt_01")
    result.add(lower_bolt_2, name="lower_bolt_02")
    return result
