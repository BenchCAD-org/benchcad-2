"""Set screw shaft collar (GN 705 / DIN 705 style).

This file works in both places:
- BenchCAD imports build(...) and supplies sampled parameters.
- CQ-editor can open this file directly and renders EXAMPLE_PARAMS.
"""

import cadquery as cq


def build(
    bore_d,
    outer_d,
    width,
    screw_d,
    screw_len,
    slot_depth,
    face_chamfer,
    screw_head_d,
):
    od_r = outer_d / 2.0
    bore_r = bore_d / 2.0
    chamfer = min(face_chamfer, (od_r - bore_r) * 0.18, width * 0.08)

    collar = (
        cq.Workplane("XZ")
        .polyline(
            [
                (bore_r + chamfer, 0),
                (od_r - chamfer, 0),
                (od_r, chamfer),
                (od_r, width - chamfer),
                (od_r - chamfer, width),
                (bore_r + chamfer, width),
                (bore_r, width - chamfer),
                (bore_r, chamfer),
            ]
        )
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )

    # Radial tapped set-screw hole, centered through the collar wall.
    screw_hole = (
        cq.Workplane("YZ")
        .circle(screw_d / 2.0)
        .extrude(outer_d + 1.0)
        .translate((-(outer_d + 1.0) / 2.0, 0, width / 2.0))
    )
    collar = collar.cut(screw_hole)

    # Shallow screw-side recess so the set-screw side is visible in renders.
    recess_depth = min(1.2, max(0.35, screw_len * 0.12))
    recess = (
        cq.Workplane("YZ")
        .circle(screw_head_d / 2.0)
        .extrude(recess_depth + 0.05)
        .translate((outer_d / 2.0 - recess_depth, 0, width / 2.0))
    )
    collar = collar.cut(recess)

    # Slotted relief across the screw side, matching the type-A drawing cue.
    slot_w = max(0.9, screw_d * 0.38)
    slot = (
        cq.Workplane("XY")
        .box(slot_depth, slot_w, width + 0.8)
        .translate((outer_d / 2.0 - slot_depth / 2.0, 0, width / 2.0))
    )
    collar = collar.cut(slot)

    result = collar
    return result


EXAMPLE_PARAMS = {
    "bore_d": 20.0,
    "outer_d": 32.0,
    "width": 14.0,
    "screw_d": 6.0,
    "screw_len": 8.0,
    "slot_depth": 2.2,
    "face_chamfer": 0.45,
    "screw_head_d": 8.7,
}


if "show_object" in globals():
    result = build(**EXAMPLE_PARAMS)
    show_object(result, name="set_screw_shaft_collar")
