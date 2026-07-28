"""stop_bar_tailpiece — the parametric part.

A Gibson-style stop bar tailpiece (Gotoh GE101Z class), bar only — studs and
bushings are separate hardware. The whole outer form is ONE lofted surface:
D-shaped cross-sections (flat back, arc front) swept along the bar, their
height following the R-crown over the centre body and blending down through a
smooth cosine ramp into the thin end ears; a stadium plan outline rounds the
ear ends. Six string holes (stepped bores on the real part) and two open stud
U-slots are cut after the loft. Bar along X, string holes along Y, base z=0.

Interface + examples: docs/DESIGN_SPEC.md
"""

import math

import cadquery as cq


def _d_section(wp, w, h):
    """One D-shaped closed wire: flat back/top/bottom, circular-arc front face
    (radius 0.75*h, apex on the front plane). Same topology at every station so
    the loft is clean."""
    r_d = 0.75 * h
    s = r_d - math.sqrt(r_d * r_d - (h / 2.0) ** 2)  # front-edge setback
    return (
        wp.moveTo(-w / 2.0, 0.0)
        .lineTo(-w / 2.0, h)
        .lineTo(w / 2.0 - s, h)
        .threePointArc((w / 2.0, h / 2.0), (w / 2.0 - s, 0.0))
        .close()
    )


def _heights(overall_l, stud_span, bar_h, tab_t, crown_r, ramp_len, slot_w):
    """(x, h) loft stations for the half-bar, mirrored to the full bar: crowned
    centre, cosine blend down over ramp_len, flat ear to the end."""
    x_r0 = stud_span / 2.0 - slot_w / 2.0 - ramp_len  # blend starts
    x_r1 = x_r0 + ramp_len                             # ear begins
    x_end = overall_l / 2.0

    def crown(x):
        return bar_h - x * x / (2.0 * crown_r)

    def blend(x):
        t = (x - x_r0) / ramp_len
        return tab_t + (crown(x_r0) - tab_t) * 0.5 * (1.0 + math.cos(math.pi * t))

    # dense stations so a RULED loft (no spline overshoot) still reads smooth
    half = [(x_r0 * i / 5.0, crown(x_r0 * i / 5.0)) for i in range(6)]
    half += [(x_r0 + ramp_len * i / 7.0, blend(x_r0 + ramp_len * i / 7.0)) for i in range(1, 8)]
    half += [(x_end, tab_t)]
    return sorted({(round(-x, 6), h) for x, h in half} | {(round(x, 6), h) for x, h in half})


def build(overall_l, stud_span, bar_w, bar_h, tab_t, crown_r, ramp_len,
          string_pitch, hole_d, slot_w, stepped_holes):
    stations = _heights(overall_l, stud_span, bar_h, tab_t, crown_r, ramp_len, slot_w)

    # one loft through D-sections whose height follows crown -> blend -> ear
    wp = cq.Workplane("YZ").workplane(offset=stations[0][0])
    wp = _d_section(wp, bar_w, stations[0][1])
    prev_x = stations[0][0]
    for x, h in stations[1:]:
        wp = _d_section(wp.workplane(offset=x - prev_x), bar_w, h)
        prev_x = x
    result = wp.loft(ruled=True)

    # stadium plan outline rounds the ear ends (radius = bar_w/2)
    plan = cq.Workplane("XY").slot2D(overall_l, bar_w, 0).extrude(1.5 * bar_h)
    result = result.intersect(plan)

    # six string holes through the crowned body (along Y)
    z_hole = tab_t + 0.45 * (bar_h - tab_t)
    pts = [((i - 2.5) * string_pitch, z_hole) for i in range(6)]
    if stepped_holes:
        exit_d = 0.6 * hole_d
        thru = cq.Workplane("XZ").pushPoints(pts).circle(exit_d / 2.0).extrude(3.0 * bar_w).translate((0.0, 1.5 * bar_w, 0.0))
        entry = cq.Workplane("XZ").pushPoints(pts).circle(hole_d / 2.0).extrude(bar_w * 0.55).translate((0.0, -bar_w * 0.45, 0.0))
        result = result.cut(thru).cut(entry)
    else:
        thru = cq.Workplane("XZ").pushPoints(pts).circle(hole_d / 2.0).extrude(3.0 * bar_w).translate((0.0, 1.5 * bar_w, 0.0))
        result = result.cut(thru)

    # open U-slots for the studs, cut out through each ear end
    for s in (-1.0, 1.0):
        x_stud = s * stud_span / 2.0
        reach = overall_l / 2.0 - abs(x_stud) + 5.0
        cutter = (
            cq.Workplane("XY")
            .box(reach, slot_w, 6.0 * tab_t)
            .translate((x_stud + s * reach / 2.0, 0.0, tab_t))
            .union(cq.Workplane("XY").circle(slot_w / 2.0).extrude(6.0 * tab_t).translate((x_stud, 0.0, -tab_t)))
        )
        result = result.cut(cutter)

    return result
