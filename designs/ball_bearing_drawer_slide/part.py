"""ball_bearing_drawer_slide — the parametric part (multi-body).

A full-extension ball-bearing drawer slide in the CLOSED position: three
roll-formed steel members — cabinet (outer), intermediate, and drawer (inner) —
that stack across the slide's thin width, separated by the running clearance the
ball retainers ride in. The three members are SEPARATE bodies (they slide
relative to one another), so `build()` returns a `cq.Assembly` of three parts and
`family.json` declares `"solids": 3`. The cabinet and drawer members carry the
mounting holes (round, or vertical adjustment slots on the cabinet member).

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def _rail(length, thick, height, y0):
    """One member: a tall rail spanning the slide length, centred at width y0."""
    return cq.Workplane("XY").box(length, thick, height).translate((0.0, y0, 0.0))


def _drill(rail, length, hole_pitch, hole_d, mount_slots):
    """A row of mounting holes (or vertical slots) down the member's web."""
    edge = 15.0
    span = length - 2.0 * edge
    n = max(2, int(span // hole_pitch) + 1)
    xs = [(-span / 2.0 + span * i / (n - 1)) for i in range(n)]
    face = rail.faces(">Y").workplane(centerOption="CenterOfBoundBox")
    if mount_slots:
        return face.pushPoints([(x, 0.0) for x in xs]).slot2D(hole_d * 2.2, hole_d, 90).cutThruAll()
    return face.pushPoints([(x, 0.0) for x in xs]).circle(hole_d / 2.0).cutThruAll()


def build(slide_length, member_height, member_width, gap, hole_d, hole_pitch, mount_slots):
    L, H, W = slide_length, member_height, member_width
    # three members + two ball-race gaps span the total width
    rt = (W - 2.0 * gap) / 3.0
    y_cabinet = -W / 2.0 + rt / 2.0
    y_intermediate = -W / 2.0 + 1.5 * rt + gap
    y_drawer = -W / 2.0 + 2.5 * rt + 2.0 * gap

    cabinet = _drill(_rail(L, rt, H, y_cabinet), L, hole_pitch, hole_d, mount_slots)
    intermediate = _rail(L, rt, H, y_intermediate)
    drawer = _drill(_rail(L, rt, H, y_drawer), L, hole_pitch, hole_d, 0)

    result = cq.Assembly()
    result.add(cabinet, name="cabinet_member")
    result.add(intermediate, name="intermediate_member")
    result.add(drawer, name="drawer_member")
    return result
