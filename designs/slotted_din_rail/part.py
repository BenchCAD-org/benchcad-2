"""slotted_din_rail_th35_7_5 -- parametric CadQuery model."""

import cadquery as cq


def build(rail_length, rail_width, rail_height, rail_thickness, slot_width,
          slot_length, slot_count, lip_height, side_relief):
    center_width = rail_width * 0.54
    side_width = (rail_width - center_width) / 2.0

    # Simplified TH35 top-hat section: base flange, raised center, and edge lips.
    result = (
        cq.Workplane("XY")
        .box(rail_length, rail_width, rail_thickness)
        .translate((0.0, 0.0, rail_thickness / 2.0))
    )
    result = result.union(
        cq.Workplane("XY")
        .box(rail_length, center_width, rail_height)
        .translate((0.0, 0.0, rail_height / 2.0))
    )
    result = result.union(
        cq.Workplane("XY")
        .box(rail_length, side_width, lip_height)
        .translate((0.0, rail_width / 2.0 - side_width / 2.0, lip_height / 2.0))
    )
    result = result.union(
        cq.Workplane("XY")
        .box(rail_length, side_width, lip_height)
        .translate((0.0, -rail_width / 2.0 + side_width / 2.0, lip_height / 2.0))
    )

    usable = max(rail_length - slot_length, slot_length)
    pitch = usable / (slot_count + 1)
    for i in range(int(slot_count)):
        x = -rail_length / 2.0 + pitch * (i + 1)
        cutter = (
            cq.Workplane("XY")
            .box(slot_length, slot_width, rail_height * 3.0)
            .translate((x, 0.0, rail_height / 2.0))
        )
        result = result.cut(cutter)

    if side_relief:
        relief_w = rail_thickness * 1.5
        result = result.cut(
            cq.Workplane("XY")
            .box(rail_length * 0.92, relief_w, rail_height * 2.0)
            .translate((0.0, center_width / 2.0, rail_height / 2.0))
        )
        result = result.cut(
            cq.Workplane("XY")
            .box(rail_length * 0.92, relief_w, rail_height * 2.0)
            .translate((0.0, -center_width / 2.0, rail_height / 2.0))
        )

    return result
