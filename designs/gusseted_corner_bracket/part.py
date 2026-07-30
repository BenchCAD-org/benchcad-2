"""gusseted_corner_bracket - independent parametric 90-degree bracket."""

import cadquery as cq


EPS = 0.02


def _slot_cut_xy(length, width, x_center, y_center, z_thickness):
    half_len = length / 2.0
    half_w = width / 2.0
    body = cq.Workplane("XY").box(width, max(length - width, EPS), z_thickness + 2.0 * EPS, centered=(True, True, True))
    body = body.translate((x_center, y_center, z_thickness / 2.0))
    cap1 = cq.Workplane("XY").circle(half_w).extrude(z_thickness + 2.0 * EPS, both=True).translate((x_center, y_center - (half_len - half_w), z_thickness / 2.0))
    cap2 = cq.Workplane("XY").circle(half_w).extrude(z_thickness + 2.0 * EPS, both=True).translate((x_center, y_center + (half_len - half_w), z_thickness / 2.0))
    return body.union(cap1).union(cap2)


def _slot_cut_xz(length, width, x_center, z_center, y_thickness):
    half_len = length / 2.0
    half_w = width / 2.0
    body = cq.Workplane("XZ").box(width, y_thickness + 2.0 * EPS, max(length - width, EPS), centered=(True, True, True))
    body = body.translate((x_center, y_thickness / 2.0, z_center))
    cap1 = cq.Workplane("XZ").circle(half_w).extrude(y_thickness + 2.0 * EPS, both=True).translate((x_center, y_thickness / 2.0, z_center - (half_len - half_w)))
    cap2 = cq.Workplane("XZ").circle(half_w).extrude(y_thickness + 2.0 * EPS, both=True).translate((x_center, y_thickness / 2.0, z_center + (half_len - half_w)))
    return body.union(cap1).union(cap2)


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

    # Parameter and geometry safety checks happen here as a second line of defense.
    assert leg_length_1 > 0 and leg_length_2 > 0
    assert bracket_width > 0 and plate_thickness > 0 and gusset_thickness > 0

    wing_1 = cq.Workplane("XY").box(bracket_width, leg_length_1, plate_thickness, centered=(True, False, False))
    wing_2 = cq.Workplane("XZ").box(bracket_width, leg_length_2, plate_thickness, centered=(True, False, False)).translate((0.0, plate_thickness, 0.0))

    gusset = (
        cq.Workplane("YZ")
        .polyline([(0.0, 0.0), (gusset_length_1, 0.0), (0.0, gusset_length_2)])
        .close()
        .extrude(gusset_thickness)
        .translate((-gusset_thickness / 2.0, plate_thickness, plate_thickness))
    )

    result = wing_1.union(wing_2).union(gusset)

    # Gentle edge treatment is intentionally conservative in this revision.
    # The body stays valid even if no fillet/chamfer is applied.
    if edge_radius > 0.0 and gusset_radius > 0.0:
        result = _safe_fillet(result, "|X", min(edge_radius * 0.35, plate_thickness * 0.12))
        result = _safe_chamfer(result, ">Y and |X", min(edge_radius * 0.12, 0.15))
        result = _safe_fillet(result, "|Y", min(edge_radius * 0.18, plate_thickness * 0.08))
        result = _safe_fillet(result, "|Z", min(edge_radius * 0.18, plate_thickness * 0.08))
        result = _safe_fillet(result, "|X and >Z", min(gusset_radius * 0.20, plate_thickness * 0.12))

    # Slots are cut after the primary solid is fused so they remain through-holes.
    # wing_1 lives in the XY plane, so its long slot runs along Y (vertical in front view).
    # wing_2 lives in the XZ plane, so its long slot runs along Z (horizontal in top view).
    slot_1 = _slot_cut_xy(slot_width, slot_length, 0.0, slot_offset_1, plate_thickness)
    slot_2 = _slot_cut_xz(slot_width, slot_length, 0.0, slot_offset_2, plate_thickness)
    result = result.cut(slot_1).cut(slot_2)

    return result
