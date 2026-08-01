"""gusseted_corner_bracket - self-contained parametric corner bracket."""

import cadquery as cq


def _make_slot_solid_xy(cx: float, cy: float, slot_length: float, slot_width: float, depth: float) -> cq.Solid:
    half_w = slot_width / 2.0
    half_body = (slot_length - slot_width) / 2.0
    edges = [
        cq.Edge.makeLine(cq.Vector(cx - half_w, cy - half_body, 0.0), cq.Vector(cx - half_w, cy + half_body, 0.0)),
        cq.Edge.makeCircle(half_w, cq.Vector(cx, cy + half_body, 0.0), cq.Vector(0.0, 0.0, 1.0), 180.0, 0.0),
        cq.Edge.makeLine(cq.Vector(cx + half_w, cy + half_body, 0.0), cq.Vector(cx + half_w, cy - half_body, 0.0)),
        cq.Edge.makeCircle(half_w, cq.Vector(cx, cy - half_body, 0.0), cq.Vector(0.0, 0.0, 1.0), 0.0, 180.0),
    ]
    face = cq.Face.makeFromWires(cq.Wire.assembleEdges(edges))
    return cq.Solid.extrudeLinear(face, cq.Vector(0.0, 0.0, depth))


def _make_slot_solid_xz(cx: float, cz: float, slot_length: float, slot_width: float, depth: float) -> cq.Solid:
    half_w = slot_width / 2.0
    half_body = (slot_length - slot_width) / 2.0
    return (
        cq.Workplane("XZ")
        .moveTo(cx - half_w, cz - half_body)
        .lineTo(cx - half_w, cz + half_body)
        .threePointArc((cx, cz + half_body + half_w), (cx + half_w, cz + half_body))
        .lineTo(cx + half_w, cz - half_body)
        .threePointArc((cx, cz - half_body - half_w), (cx - half_w, cz - half_body))
        .close()
        .extrude(depth)
        .val()
    )


def _make_panel_hole_side_face(x0: float, y_center: float, z_center: float, radius: float, thickness: float) -> cq.Solid:
    """Cylindrical cutter for one optional side-panel hole, axis along X."""

    return (
        cq.Workplane("YZ")
        .center(y_center, z_center)
        .circle(radius)
        .extrude(thickness + 0.4)
        .translate((x0 - 0.2, 0.0, 0.0))
        .val()
    )


def _safe_fillet(shape, selector: str, radius: float):
    if radius <= 0:
        return shape
    try:
        return shape.edges(selector).fillet(radius)
    except Exception:
        return shape


def _build_core(
    leg_length_1: float,
    leg_length_2: float,
    bracket_width: float,
    plate_thickness: float,
    gusset_thickness: float,
    gusset_length_1: float,
    gusset_length_2: float,
    slot_width: float,
    slot_length: float,
    slot_offset_1: float,
    slot_offset_2: float,
    edge_radius: float,
    gusset_radius: float,
) -> cq.Solid:
    wing_1 = cq.Workplane("XY").box(bracket_width, leg_length_1, plate_thickness, centered=(True, False, False))
    wing_2 = cq.Workplane("XY").box(bracket_width, plate_thickness, leg_length_2, centered=(True, False, False))

    gusset = (
        cq.Workplane("YZ")
        .polyline(
            [
                (plate_thickness, plate_thickness),
                (gusset_length_1, plate_thickness),
                (plate_thickness, gusset_length_2),
            ]
        )
        .close()
        .extrude(gusset_thickness)
        .translate((-gusset_thickness / 2.0, 0.0, 0.0))
        .val()
    )

    wing_1 = _safe_fillet(wing_1, "|Z", edge_radius)
    wing_2 = _safe_fillet(wing_2, "|Y", edge_radius)
    gusset = _safe_fillet(gusset, "|X", gusset_radius)

    result = wing_1.union(wing_2).union(gusset)

    slot_1 = _make_slot_solid_xy(0.0, slot_offset_1, slot_length, slot_width, plate_thickness + 0.4).translate((0.0, 0.0, -0.2))
    slot_2 = _make_slot_solid_xz(0.0, slot_offset_2, slot_length, slot_width, plate_thickness + 0.4).translate((0.0, -0.2, 0.0))
    result = result.cut(slot_1).cut(slot_2)

    return result


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
    panel_mount_holes,
    panel_hole_offset,
    panel_hole_diameter,
    edge_radius,
    gusset_radius,
):
    """Build a self-contained gusseted corner bracket."""

    result = _build_core(
        leg_length_1=leg_length_1,
        leg_length_2=leg_length_2,
        bracket_width=bracket_width,
        plate_thickness=plate_thickness,
        gusset_thickness=gusset_thickness,
        gusset_length_1=gusset_length_1,
        gusset_length_2=gusset_length_2,
        slot_width=slot_width,
        slot_length=slot_length,
        slot_offset_1=slot_offset_1,
        slot_offset_2=slot_offset_2,
        edge_radius=edge_radius,
        gusset_radius=gusset_radius,
    )

    if panel_mount_holes:
        hole_r = panel_hole_diameter / 2.0
        left_x0 = -bracket_width / 2.0
        right_x0 = bracket_width / 2.0 - gusset_thickness
        result = result.cut(_make_panel_hole_side_face(left_x0, panel_hole_offset, panel_hole_offset, hole_r, gusset_thickness))
        result = result.cut(_make_panel_hole_side_face(right_x0, panel_hole_offset, panel_hole_offset, hole_r, gusset_thickness))

    result = result.clean()
    try:
        result = result.removeSplitter()
    except Exception:
        pass
    return result
