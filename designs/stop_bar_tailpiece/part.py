"""stop_bar_tailpiece — the parametric part.

A Gibson-style stop bar tailpiece (Gotoh GE101Z class), bar only — the studs
and bushings are separate hardware. A full-length base plate carries an open
U-slot ear at each end (the stud slots); a raised centre body, crowned to a
large radius along its top, carries the six string holes (stepped bores on the
real part). Bar runs along X, string holes along Y, base plane z=0.

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def _hole_xs(string_pitch):
    """Six string-hole centres about the middle."""
    return [(i - 2.5) * string_pitch for i in range(6)]


def build(overall_l, stud_span, bar_w, bar_h, tab_t, crown_r, string_pitch, hole_d, slot_w, stepped_holes):
    # full-length base plate (the ears live at its ends)
    result = cq.Workplane("XY").box(overall_l, bar_w, tab_t).translate((0.0, 0.0, tab_t / 2.0))

    # raised centre body between the stud slots, crowned along the top:
    # intersect with a cylinder (axis along Y) whose crest sits at z = bar_h
    body_l = stud_span - slot_w - 6.0
    body = cq.Workplane("XY").box(body_l, bar_w, bar_h).translate((0.0, 0.0, bar_h / 2.0))
    crown = (
        cq.Workplane("XZ")
        .center(0.0, bar_h - crown_r)
        .circle(crown_r)
        .extrude(3.0 * bar_w)          # XZ extrude runs -Y
        .translate((0.0, 1.5 * bar_w, 0.0))
    )
    result = result.union(body.intersect(crown))

    # D-profile: the end view is flat-backed with a rounded front. Constructed
    # (no fillet): intersect with a cylinder along X whose crest touches the
    # front face — robust at range extremes where edge fillets fail.
    r_d = 0.75 * bar_h
    dcyl = (
        cq.Workplane("YZ")
        .center(bar_w / 2.0 - r_d, bar_h / 2.0)
        .circle(r_d)
        .extrude(1.2 * overall_l)
        .translate((-0.6 * overall_l, 0.0, 0.0))
    )
    result = result.intersect(dcyl)

    # six string holes through the body (along Y): plain bores, or the real
    # stepped bore (entry hole_d, exit ~0.6*hole_d)
    z_hole = tab_t + 0.45 * (bar_h - tab_t)
    pts = [(x, z_hole) for x in _hole_xs(string_pitch)]
    if stepped_holes:
        exit_d = 0.6 * hole_d
        thru = cq.Workplane("XZ").pushPoints(pts).circle(exit_d / 2.0).extrude(3.0 * bar_w).translate((0.0, 1.5 * bar_w, 0.0))
        entry = cq.Workplane("XZ").pushPoints(pts).circle(hole_d / 2.0).extrude(bar_w * 0.55).translate((0.0, -bar_w * 0.45, 0.0))
        result = result.cut(thru).cut(entry)
    else:
        thru = cq.Workplane("XZ").pushPoints(pts).circle(hole_d / 2.0).extrude(3.0 * bar_w).translate((0.0, 1.5 * bar_w, 0.0))
        result = result.cut(thru)

    # open U-slots for the studs: a rounded slot cut from each stud centre out
    # through the plate end
    for s in (-1.0, 1.0):
        x_stud = s * stud_span / 2.0
        reach = overall_l / 2.0 - abs(x_stud) + 5.0
        cutter = (
            cq.Workplane("XY")
            .box(reach, slot_w, 4.0 * tab_t)
            .translate((x_stud + s * reach / 2.0, 0.0, tab_t))
            .union(
                cq.Workplane("XY").circle(slot_w / 2.0).extrude(4.0 * tab_t)
                .translate((x_stud, 0.0, -tab_t))
            )
        )
        result = result.cut(cutter)

    return result
