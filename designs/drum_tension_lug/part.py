"""drum_tension_lug — the parametric part.

A drum-shell tension lug: a compact cast/chromed body that bolts to the outside
of the drum shell and receives the tension rod that tightens the drumhead. The
body sits on the shell (z=0, extending radially out in +Z), is mounted by two
screws on its centreline into the shell, and carries a rod-thread insert bore at
the head end (both ends when it is a double-ended tube lug). Corners are radiused
for the cast look.

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def build(body_len, body_h, body_w, hole_spacing, mount_hole_d, rod_bore, fillet_r, double_ended):
    # cast body, sitting on the shell face (z=0), extending radially out to z=body_h
    result = cq.Workplane("XY").box(body_w, body_len, body_h).translate((0.0, 0.0, body_h / 2.0))
    result = result.edges("|Z").fillet(fillet_r)

    # two mounting screws on the centreline, blind up from the shell face
    result = (
        result.faces("<Z")
        .workplane(centerOption="CenterOfBoundBox")
        .pushPoints([(0.0, hole_spacing / 2.0), (0.0, -hole_spacing / 2.0)])
        .hole(mount_hole_d, depth=body_h * 0.45)
    )

    # rod-thread insert bore at the head end (+Y), on the body axis
    result = (
        result.faces(">Y")
        .workplane(centerOption="CenterOfBoundBox")
        .hole(rod_bore, depth=body_len * 0.45)
    )
    if double_ended:
        # tube lug: a second rod bore at the opposite end
        result = (
            result.faces("<Y")
            .workplane(centerOption="CenterOfBoundBox")
            .hole(rod_bore, depth=body_len * 0.45)
        )

    return result
