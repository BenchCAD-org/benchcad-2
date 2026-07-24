"""slotted_din_rail_th35_7_5 -- parametric CadQuery model."""

import cadquery as cq


def build(rail_length, rail_width, rail_height, rail_thickness, slot_width,
          slot_length, slot_count, profile_inner_width, slot_pitch,
          side_relief):
    return_width = (rail_width - profile_inner_width) / 2.0
    wall_height = rail_height - rail_thickness

    # TH35-7.5 is a bent sheet profile: a slotted center web with side returns.
    result = _box(rail_length, profile_inner_width, rail_thickness,
                  0.0, 0.0, rail_thickness / 2.0)

    centers = _slot_centers(slot_count, slot_pitch)
    if centers:
        result = (
            result.faces(">Z").workplane()
            .pushPoints([(x, 0.0) for x in centers])
            .slot2D(slot_length, slot_width, 0)
            .cutThruAll()
        )

    for sign in (-1.0, 1.0):
        y_inner = sign * profile_inner_width / 2.0
        y_wall = y_inner - sign * rail_thickness / 2.0
        y_flange = sign * (profile_inner_width / 2.0 + return_width / 2.0)

        result = result.union(
            _box(rail_length, rail_thickness, wall_height,
                 0.0, y_wall, rail_thickness + wall_height / 2.0)
        )
        result = result.union(
            _box(rail_length, return_width, rail_thickness,
                 0.0, y_flange, rail_height - rail_thickness / 2.0)
        )

        if side_relief:
            lip_height = min(rail_thickness * 1.8, rail_height - rail_thickness)
            y_lip = sign * (rail_width / 2.0 - rail_thickness / 2.0)
            result = result.union(
                _box(rail_length, rail_thickness, lip_height,
                     0.0, y_lip, rail_height - rail_thickness - lip_height / 2.0)
            )

    return result


def _box(length, width, height, x, y, z):
    return (
        cq.Workplane("XY")
        .box(length, width, height)
        .translate((x, y, z))
    )


def _slot_centers(slot_count, slot_pitch):
    count = int(slot_count)
    if count <= 0:
        return []
    if count == 1:
        return [0.0]
    first = -slot_pitch * (count - 1) / 2.0
    return [first + slot_pitch * i for i in range(count)]
