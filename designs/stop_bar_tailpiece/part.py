"""stop_bar_tailpiece — the parametric part.

A Gibson-style stop bar tailpiece (Gotoh GE101Z class), bar only — studs and
bushings are separate hardware. A ruled loft carries the drawing's D-section
along the crowned centre body and blends down into two flat end ears. In plan,
each ear is the dimension-driven circular lobe about its stud centre, clipped
at the front and rear faces; an 8 mm parallel-sided U-slot leaves the short
outboard curl visible in the drawing. Six string bores run front-to-back,
stepped from both faces on the real part. Bar along X, bores along Y, base z=0.

Interface + examples: docs/DESIGN_SPEC.md
"""

import math

import cadquery as cq


def _d_section(wp, w, h):
    """One D-shaped closed wire per the sheet's end view: the straight side is
    the full-depth BOTTOM face (the 18 direction), short edge lands rise at
    the front and back, and the crown arc sweeps the HEIGHT with its apex on
    top — the photo's continuous dome from the back edge over to the string
    holes. Same topology at every station so the loft is clean."""
    rise = 0.2 * h  # the end view's short ~2.75 edge land under the 12.75 crown
    return (
        wp.moveTo(-w / 2.0, 0.0)
        .lineTo(-w / 2.0, rise)
        .threePointArc((0.0, h), (w / 2.0, rise))
        .lineTo(w / 2.0, 0.0)
        .close()
    )


def _heights(stud_span, bar_h, tab_t, crown_r, ramp_len, slot_w):
    """Mirrored (x, height) stations for crown and body-to-ear blends."""
    x_ear = stud_span / 2.0 - slot_w / 2.0
    x_r0 = x_ear - ramp_len

    def crown(x):
        return bar_h - (crown_r - math.sqrt(crown_r * crown_r - x * x))

    def blend(x):
        t = (x - x_r0) / ramp_len
        return tab_t + (crown(x_r0) - tab_t) * 0.5 * (1.0 + math.cos(math.pi * t))

    # dense stations so a RULED loft (no spline overshoot) still reads smooth
    half = [(x_r0 * i / 5.0, crown(x_r0 * i / 5.0)) for i in range(6)]
    half += [(x_r0 + ramp_len * i / 14.0, blend(x_r0 + ramp_len * i / 14.0)) for i in range(1, 15)]  # fine ramp: facet turns stay under the 35 deg render threshold
    half += [(x_ear + 1.4, tab_t)]  # run flat past the ear join: no lip over the overlap
    return sorted({(round(-x, 6), h) for x, h in half} | {(round(x, 6), h) for x, h in half})


def _string_z(tab_t, hole_d):
    """Bore centre from the GE101Z elevation: the 5.1 mm entries sit low in
    the 7 mm tab envelope, with a small web left at the base and at the top."""
    return tab_t - 0.62 * hole_d


def build(overall_l, stud_span, bar_w, bar_h, tab_t, crown_r, ramp_len,
          string_pitch, hole_d, slot_w, web_d):
    x_ear = stud_span / 2.0 - slot_w / 2.0
    lobe_r = (overall_l - stud_span) / 2.0
    stations = _heights(stud_span, bar_h, tab_t, crown_r, ramp_len, slot_w)

    # Centre body: the D-sections follow the exact R-crown and finish at the
    # ear plane. Dense ruled stations avoid spline overshoot in the pinned OCC.
    wp = cq.Workplane("YZ").workplane(offset=stations[0][0])
    wp = _d_section(wp, bar_w, stations[0][1])
    prev_x = stations[0][0]
    for x, h in stations[1:]:
        wp = _d_section(wp.workplane(offset=x - prev_x), bar_w, h)
        prev_x = x
    result = wp.loft(ruled=True)

    # Ear plan: the sheet's ends are BLUNT — a near-flat end face with plan
    # corner rounds (the tip lands on the 102 overall), not a half-round nose
    # that reads as a curled hook.
    join_overlap = 1.0  # bury a real overlap at the join: near-coincident unions leave slivers
    for side in (-1.0, 1.0):
        x_stud = side * stud_span / 2.0
        x_join = side * (x_ear - join_overlap)
        x_tip = x_stud + side * lobe_r
        w2 = bar_w / 2.0 - 0.15
        rc = 0.35 * lobe_r                       # plan corner radius at the end
        k = 0.2929 * rc                          # 45-degree sagitta for the corner arcs
        ear = (
            cq.Workplane("XY")
            .moveTo(x_join, w2)
            .lineTo(x_tip - side * rc, w2)
            .threePointArc((x_tip - side * k, w2 - k), (x_tip, w2 - rc))
            .lineTo(x_tip, -(w2 - rc))
            .threePointArc((x_tip - side * k, -(w2 - k)), (x_tip - side * rc, -w2))
            .lineTo(x_join, -w2)
            .close()
            .extrude(tab_t)
            .intersect(_d_section(cq.Workplane("YZ").workplane(offset=x_stud - 2.0 * lobe_r),
                                  bar_w, tab_t).extrude(4.0 * lobe_r))
        )
        # the sheet's end profile keeps FALLING toward the tip: shave the ear
        # top on a wedge from full tab height at the join down to ~0.55 tab at
        # the end, so the curl reads as a low stub, not an upturned horn
        wedge = (
            cq.Workplane("XZ").workplane(offset=bar_w)
            .moveTo(x_join - side * 1.0, 0.0)
            .lineTo(x_join - side * 1.0, tab_t + 2.0)
            .lineTo(x_tip + side * 2.0, 0.55 * tab_t)
            .lineTo(x_tip + side * 2.0, 0.0)
            .close()
            .extrude(-2.0 * bar_w)
        )
        ear = ear.intersect(wedge)
        # match the bar's D-section at tab height so the join is flush (the
        # rectangular extrusion's front corner otherwise pokes past the curve)
        x_lo = min(x_join, x_tip) - 1.0
        x_hi = max(x_join, x_tip) + 1.0
        dpr = _d_section(cq.Workplane("YZ").workplane(offset=x_lo), bar_w - 0.06, tab_t - 0.03).extrude(x_hi - x_lo)
        ear = ear.intersect(dpr)
        result = result.union(ear.val())

    # Six low string bores along Y.  Their large entries intersect the curved
    # front crown (the six plan-view breakouts) while remaining circular in the
    # elevation. Their centres follow the same R300 elevation as the sheet.
    x_outer = 2.5 * string_pitch
    drop_out = crown_r - math.sqrt(crown_r * crown_r - x_outer * x_outer)
    z_outer = _string_z(tab_t, hole_d)
    pts = []
    for i in range(6):
        x_hole = (i - 2.5) * string_pitch
        drop_here = crown_r - math.sqrt(crown_r * crown_r - x_hole * x_hole)
        pts.append((x_hole, z_outer + drop_out - drop_here))

    # the drawing's bore stack is NOT optional: phi5.1 counterbores exactly
    # 4.5 deep from BOTH faces, phi3-class web through the middle
    cb_depth = 4.5
    overcut = 0.2
    thru = cq.Workplane("XZ").pushPoints(pts).circle(web_d / 2.0).extrude(3.0 * bar_w).translate((0.0, 1.5 * bar_w, 0.0))
    cb_flat = (
        cq.Workplane("XZ")
        .pushPoints(pts)
        .circle(hole_d / 2.0)
        .extrude(cb_depth + overcut)
        .translate((0.0, -bar_w / 2.0 + cb_depth, 0.0))
    )
    cb_crown = (
        cq.Workplane("XZ")
        .pushPoints(pts)
        .circle(hole_d / 2.0)
        .extrude(cb_depth + overcut)
        .translate((0.0, bar_w / 2.0 + overcut, 0.0))
    )
    result = result.cut(thru).cut(cb_flat).cut(cb_crown)

    # The marked 8 mm is the perpendicular X distance between these parallel
    # faces. They run from the front edge to a semicircular closed end centred
    # on the stud line; there is no rotated or flared wedge in the plan view.
    slot_r = slot_w / 2.0
    cut_h = 3.0 * max(tab_t, bar_h)
    mouth_reach = bar_w / 2.0 + 1.0
    for side in (-1.0, 1.0):
        x_stud = side * stud_span / 2.0
        closed_end = (
            cq.Workplane("XY")
            .circle(slot_r)
            .extrude(cut_h)
            .translate((x_stud, 0.0, -tab_t))
        )
        mouth = (
            cq.Workplane("XY")
            .rect(slot_w, mouth_reach)
            .extrude(cut_h)
            .translate((x_stud, mouth_reach / 2.0, -tab_t))
        )
        cutter = closed_end.union(mouth)  # fuse first: tangent cylinder/box seam stays in the cutter
        result = result.cut(cutter.val())

    return result
