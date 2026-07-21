"""tilting_speaker_wall_bracket — the parametric part.

A tilt-adjustable loudspeaker wall mount (B-Tech BT-style): a wall plate that
bolts to the wall, an arm that stands the speaker off the wall, and a
speaker-side plate held at a set tilt angle, with fixing holes. An optional
gusset reinforces the arm/wall joint. Modelled as one connected bracket at a
fixed tilt position. The wall is the Y-Z plane at x=0; the arm reaches out +X.

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def build(wall_w, wall_h, plate_t, arm_len, arm_w, tilt_angle, spk_w, spk_h, bolt_d, gusset):
    # wall plate (against the wall, normal +X), centred at x=0
    result = cq.Workplane("YZ").box(wall_w, wall_h, plate_t)
    # wall bolt holes (through the plate along X), a rectangular pattern
    bx, bz = wall_w * 0.32, wall_h * 0.34
    holes = cq.Workplane("YZ").pushPoints([(bx, bz), (-bx, bz), (bx, -bz), (-bx, -bz)]).circle(bolt_d / 2.0).extrude(plate_t * 3.0, both=True)
    result = result.cut(holes)

    # standoff arm reaching out from the wall plate
    x_arm_start = plate_t / 2.0
    result = result.union(
        cq.Workplane("XY").box(arm_len, arm_w, arm_w).translate((x_arm_start + arm_len / 2.0, 0.0, 0.0))
    )

    # optional gusset: a triangular rib under the arm, wall -> arm
    if gusset:
        g = (
            cq.Workplane("XZ")
            .polyline([(x_arm_start, -arm_w / 2.0), (x_arm_start + arm_len * 0.6, -arm_w / 2.0),
                       (x_arm_start, -arm_w / 2.0 - wall_h * 0.28)])
            .close()
            .extrude(arm_w * 0.6, both=True)
        )
        result = result.union(g)

    # tilt-pivot knuckle at the arm front (a hub on the horizontal Y axis) — the
    # tilted plate always intersects it, so the bracket stays one connected body
    x_front = x_arm_start + arm_len
    hub = cq.Workplane("XZ").circle(arm_w * 0.55).extrude(arm_w).translate((x_front, arm_w / 2.0, 0.0))
    result = result.union(hub)

    # speaker-side plate, built flat (with its fixing holes) then tilted about the
    # horizontal (Y) axis to the set tilt angle and set on the pivot
    spk = cq.Workplane("XY").box(plate_t, spk_w, spk_h)
    fz = spk_h * 0.3
    spk = spk.faces(">X").workplane().pushPoints([(0.0, fz), (0.0, -fz)]).hole(bolt_d)
    spk = spk.rotate((x_front, 0.0, 0.0), (x_front, 1.0, 0.0), tilt_angle).translate((x_front, 0.0, 0.0))
    result = result.union(spk)

    return result
