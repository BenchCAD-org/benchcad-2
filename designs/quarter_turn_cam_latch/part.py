"""quarter_turn_cam_latch — the parametric part.

A quarter-turn cam latch (Southco E5 class): a round head above the panel, a
double-D body (a circle with two parallel flats) dropping through the panel
cutout and forming the housing behind it, and a flat cam arm clamped at the
grip depth that swings behind the door frame. Tool-operated heads carry a
screwdriver slot. Drawn latched, panel face at z=0, body dropping -Z.

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def build(head_d, head_h, body_d, afl, body_l, grip, cam_l, cam_w, cam_t, slotted):
    # head above the panel
    head = cq.Workplane("XY").circle(head_d / 2.0).extrude(head_h)
    if slotted:
        # tool-recess: a screwdriver slot across the head top
        slot = (
            cq.Workplane("XY")
            .box(head_d + 2.0, head_d * 0.14, head_h * 0.55)
            .translate((0.0, 0.0, head_h))
        )
        head = head.cut(slot)
    result = head

    # double-D body/housing: circle with two parallel flats (across-flats = afl),
    # running from the panel face down behind it
    body = cq.Workplane("XY").circle(body_d / 2.0).extrude(-body_l)
    flats = cq.Workplane("XY").box(afl, body_d + 4.0, 2.0 * body_l + 4.0)
    body = body.intersect(flats)
    result = result.union(body)

    # cam arm: a flat slotted plate of OVERALL length cam_l whose top face
    # clamps at the grip depth. The pivot sits near mid-length (Southco E5:
    # 45 long / tip offset 23 is near-symmetric), so centre the slot on the axis.
    cam = (
        cq.Workplane("XY")
        .slot2D(cam_l, cam_w, 0)
        .extrude(-cam_t)
        .translate((0.0, 0.0, -grip))
    )
    result = result.union(cam)

    return result
