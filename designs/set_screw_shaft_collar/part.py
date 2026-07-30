"""Set screw shaft collar (GN 705 / DIN 705 style)."""

import cadquery as cq


def build(
    bore_d,
    outer_d,
    width,
    screw_d,
    screw_len,
    second_screw,
):
    od_r = outer_d / 2.0
    bore_r = bore_d / 2.0
    wall = od_r - bore_r
    chamfer = min(max(0.25, bore_d * 0.012), wall * 0.18, width * 0.08)

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

    screw_angles = [0]
    if second_screw:
        screw_angles.append(135)

    screw_head_d = screw_d * 1.45
    recess_depth = min(1.2, max(0.35, screw_len * 0.12))

    for angle in screw_angles:
        screw_axis = (
            cq.Workplane("YZ")
            .circle(screw_d / 2.0)
            .extrude(wall + 1.0)
            .translate((bore_r - 0.5, 0, width / 2.0))
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )
        collar = collar.cut(screw_axis)

        recess = (
            cq.Workplane("YZ")
            .circle(screw_head_d / 2.0)
            .extrude(recess_depth + 0.05)
            .translate((od_r - recess_depth, 0, width / 2.0))
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )
        collar = collar.cut(recess)

    result = collar
    return result


EXAMPLE_PARAMS = {
    "bore_d": 80.0,
    "outer_d": 110.0,
    "width": 22.0,
    "screw_d": 12.0,
    "screw_len": 20.0,
    "second_screw": 1,
}


if "show_object" in globals():
    result = build(**EXAMPLE_PARAMS)
    show_object(result, name="set_screw_shaft_collar")
