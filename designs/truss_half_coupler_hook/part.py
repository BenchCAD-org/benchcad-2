"""truss_half_coupler_hook — the parametric part.

A stage/theatre half-coupler / hook clamp (Doughty T57000/T57200 class): an
aluminium body closed around a Ø48-51 mm scaffold/truss barrel, drawn in the
closed position as a ring, with a bolt lug across the closure at the top and a
flat hanging tang below carrying the fixing eye (Ø12.7 for M12). The hook-clamp
variant replaces the plain eye with a protruding M12 hanging stud. Tube axis is
Y; the hanging tang drops -Z to the base.

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def build(bore_d, wall_t, body_w, base_drop, tang_t, hang_d, lug_h, stud):
    r_in = bore_d / 2.0
    r_out = r_in + wall_t

    # ring closed around the barrel (tube axis = Y), centred at the origin
    ring = cq.Workplane("XZ").circle(r_out).circle(r_in).extrude(body_w)
    result = ring.translate((0.0, -body_w / 2.0, 0.0))

    # closure lug across the top: a block over the ring crown with the M12
    # closing-bolt cross-hole (axis X)
    lug = (
        cq.Workplane("XY")
        .box(2.6 * hang_d, body_w, lug_h)
        .translate((0.0, 0.0, r_out + lug_h / 2.0 - wall_t / 2.0))
    )
    lug = (
        lug.faces(">X")
        .workplane(centerOption="CenterOfBoundBox")
        .hole(hang_d)
    )
    result = result.union(lug)

    # hanging tang: a vertical plate from the ring bottom down to the base plane
    tang_h = base_drop - r_in  # plate spans ring bottom -> base
    tang = (
        cq.Workplane("XY")
        .box(tang_t, body_w, tang_h)
        .translate((0.0, 0.0, -(r_in + tang_h / 2.0)))
    )
    result = result.union(tang)

    if stud:
        # hook-clamp variant: protruding M12 hanging stud out of the tang base
        stud_len = 34.0
        s = (
            cq.Workplane("XY")
            .circle(hang_d / 2.0)
            .extrude(-stud_len)
            .translate((0.0, 0.0, -base_drop))
        )
        result = result.union(s)
    else:
        # plain fixing eye through the tang near the base (hole axis X)
        z_eye = -(base_drop - 1.2 * hang_d)
        eye = (
            cq.Workplane("YZ")
            .circle(hang_d / 2.0)
            .extrude(tang_t * 2.0, both=True)
            .translate((0.0, 0.0, z_eye))
        )
        result = result.cut(eye)

    return result
