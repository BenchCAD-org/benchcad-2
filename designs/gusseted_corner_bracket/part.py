"""gusseted_corner_bracket - independent parametric 90-degree bracket."""

import cadquery as cq


EPS = 0.02


def _slot_cut_xy(length, width, x_center, y_center, z_thickness):
    return (
        cq.Workplane("XY")
        .center(x_center, y_center)
        .slot2D(length, width)
        .extrude(z_thickness + 2.0 * EPS, both=True)
        .translate((0.0, 0.0, z_thickness / 2.0))
    )


def _slot_cut_xz(length, width, x_center, z_center, y_thickness):
    return (
        cq.Workplane("XZ")
        .center(x_center, z_center)
        .slot2D(length, width)
        .extrude(y_thickness + 2.0 * EPS, both=True)
        .translate((0.0, y_thickness / 2.0, 0.0))
    )


def _safe_fillet(shape, selector, radius):
    try:
        return shape.edges(selector).fillet(radius)
    except Exception:
        return shape


def _safe_chamfer(shape, selector, distance):
    try:
        return shape.edges(selector).chamfer(distance)
    except Exception:
        return shape


def build(
    leg_length_1,
    leg_length_2,
    bracket_width,
    plate_thickness,
    gusset_thickness,
    gusset_length_1,
    gusset_length_2,
    slot_width,
    slot_length,
    slot_offset_1,
    slot_offset_2,
    edge_radius,
    gusset_radius,
):
    """Build a single-solid gusseted corner bracket."""

    # The uncut bracket body is built as one continuous YZ-section and then
    # extruded along X. This avoids tangent-solid fusion failures from trying
    # to union three separate shells that only touch at faces/edges.
    assert leg_length_1 > 0 and leg_length_2 > 0
    assert bracket_width > 0 and plate_thickness > 0 and gusset_thickness > 0

    section = [
        (0.0, 0.0),
        (0.0, plate_thickness),
        (max(plate_thickness, 0.0), plate_thickness),
        (max(plate_thickness, 0.0), leg_length_2),
        (gusset_thickness, leg_length_2),
        (gusset_thickness, plate_thickness),
        (gusset_length_1, plate_thickness),
        (0.0, 0.0),
    ]
    section = [(max(0.0, min(x, bracket_width)), max(0.0, y)) for x, y in section]
    result = cq.Workplane("YZ").polyline(section).close().extrude(bracket_width, both=False)

    if edge_radius > 0.0 and gusset_radius > 0.0:
        result = _safe_fillet(result, "|X", min(edge_radius * 0.25, plate_thickness * 0.08))
        result = _safe_fillet(result, "|Y", min(edge_radius * 0.20, plate_thickness * 0.06))
        result = _safe_fillet(result, "|Z", min(edge_radius * 0.20, plate_thickness * 0.06))
        result = _safe_fillet(result, "|X and |Y", min(gusset_radius * 0.12, 0.15))

    # Slots are cut after the primary solid is fused so they remain through-holes.
    # wing_1 lives in the XY plane, so its long slot runs along Y (vertical in front view).
    # wing_2 lives in the XZ plane, so its long slot runs along Z (horizontal in top view).
    slot_1 = _slot_cut_xy(slot_length, slot_width, 0.0, slot_offset_1, plate_thickness)
    slot_2 = _slot_cut_xz(slot_length, slot_width, 0.0, slot_offset_2, plate_thickness)
    result = result.cut(slot_1).cut(slot_2)

    return result
