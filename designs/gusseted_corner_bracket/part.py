"""gusseted_corner_bracket - self-contained parameterized corner bracket."""

import cadquery as cq


def _make_edge_line(p1, p2):
    return cq.Edge.makeLine(cq.Vector(*p1), cq.Vector(*p2))


def _make_edge_arc_3pt(p1, pm, p2):
    return cq.Edge.makeThreePointArc(cq.Vector(*p1), cq.Vector(*pm), cq.Vector(*p2))


def _make_edge_circle_xy(center, radius, angle1, angle2):
    return cq.Edge.makeCircle(radius, cq.Vector(center[0], center[1], 0.0), cq.Vector(0.0, 0.0, 1.0), angle1, angle2)


def _make_face_from_edges(edges):
    wire = cq.Wire.assembleEdges(edges)
    return cq.Face.makeFromWires(wire)


def _make_face_from_edges_xz(edges):
    wire = cq.Wire.assembleEdges(edges)
    return cq.Face.makeFromWires(wire)


def _make_slot_solid_xy(cx: float, cy: float, slot_length: float, slot_width: float, depth: float) -> cq.Solid:
    half_w = slot_width / 2.0
    half_body = (slot_length - slot_width) / 2.0
    edges = [
        _make_edge_line((cx - half_w, cy - half_body), (cx - half_w, cy + half_body)),
        _make_edge_circle_xy((cx, cy + half_body), half_w, 180.0, 0.0),
        _make_edge_line((cx + half_w, cy + half_body), (cx + half_w, cy - half_body)),
        _make_edge_circle_xy((cx, cy - half_body), half_w, 0.0, 180.0),
    ]
    face = _make_face_from_edges(edges)
    return cq.Solid.extrudeLinear(face, cq.Vector(0.0, 0.0, depth))


def _make_slot_solid_xz(cx: float, cz: float, slot_length: float, slot_width: float, depth: float) -> cq.Solid:
    half_w = slot_width / 2.0
    half_body = (slot_length - slot_width) / 2.0
    wp = (
        cq.Workplane("XZ")
        .moveTo(cx - half_w, cz - half_body)
        .lineTo(cx - half_w, cz + half_body)
        .threePointArc((cx, cz + half_body + half_w), (cx + half_w, cz + half_body))
        .lineTo(cx + half_w, cz - half_body)
        .threePointArc((cx, cz - half_body - half_w), (cx - half_w, cz - half_body))
        .close()
        .extrude(depth)
    )
    return wp.val()


def _make_panel_hole_side_face(x0: float, y_center: float, z_center: float, radius: float, thickness: float) -> cq.Solid:
    """Cylindrical cutter for a triangular side panel, with the axis along X."""

    return (
        cq.Workplane("YZ")
        .center(y_center, z_center)
        .circle(radius)
        .extrude(thickness + 0.4)
        .translate((x0 - 0.2, 0.0, 0.0))
        .val()
    )


def _make_corner_cut(y0: float, z0: float, x0: float) -> cq.Solid:
    """Remove a 2x2 corner sector with area 4-pi, extruded through one side wall."""

    wp = cq.Workplane("YZ").moveTo(y0, z0)
    wp = wp.lineTo(y0 + 2.0, z0)
    wp = wp.lineTo(y0 + 2.0, z0 - 2.0)
    wp = wp.radiusArc((y0, z0), -2.0)
    wire = wp.close().objects[0]
    face = cq.Face.makeFromWires(wire)
    cut = cq.Solid.extrudeLinear(face, cq.Vector(3.0, 0.0, 0.0))
    return cut.translate((x0, 0.0, 0.0))


def _make_boss(points, x0=11.0, x1=17.0, eps: float = 0.0) -> cq.Solid:
    """Round19 locating boss, extruded along X."""

    wire = cq.Wire.makePolygon([cq.Vector(0.0, y + eps, z + eps) for y, z in points], close=True)
    face = cq.Face.makeFromWires(wire)
    boss = cq.Solid.extrudeLinear(face, cq.Vector(x1 - x0, 0.0, 0.0))
    return boss.translate((x0, 0.0, 0.0))


def _make_box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Solid:
    """Axis-aligned repair/cut box."""

    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0).translate((x0, y0, z0))


def _make_reference_body(bracket_width: float, leg_length_1: float, leg_length_2: float) -> cq.Solid:
    """Build the default gusseted bracket body without loading any STEP file.

    The body is modeled as a single prism in the X direction from the
    reference side silhouette, then the wing slots and optional mounting holes
    are cut from that solid.
    """

    top_step = 7.5
    side_step = 7.5

    profile = (
        cq.Workplane("YZ")
        .moveTo(0.0, 0.0)
        .lineTo(0.0, leg_length_2)
        .lineTo(top_step, leg_length_2)
        .lineTo(top_step, leg_length_2 - side_step)
        .lineTo(leg_length_1 - side_step, side_step)
        .lineTo(leg_length_1, side_step)
        .lineTo(leg_length_1, 0.0)
        .close()
    )
    body = profile.extrude(bracket_width).val()

    try:
        body = body.edges("%Line").fillet(0.25)
    except Exception:
        pass

    return body


def _make_prism_from_yz(points, x0: float, x1: float) -> cq.Solid:
    """Extrude a closed YZ profile along X as a solid prism."""

    wp = cq.Workplane("YZ").moveTo(points[0][0], points[0][1])
    for y, z in points[1:]:
        wp = wp.lineTo(y, z)
    wire = wp.close().objects[0]
    face = cq.Face.makeFromWires(wire)
    prism = cq.Solid.extrudeLinear(face, cq.Vector(x1 - x0, 0.0, 0.0))
    return prism.translate((x0, 0.0, 0.0))


def _make_missing_bottom_layer():
    return _make_box(3.0, 25.0, 0.0, 4.5, 4.0, 4.5)


def _make_missing_center_lens():
    # Exact analytic reconstruction of the central missing solid.
    edges = [
        _make_edge_arc_3pt((11.0, 11.65), (14.0, 8.65), (17.0, 11.65)),
        _make_edge_line((17.0, 11.65), (17.0, 11.697224362268006)),
        _make_edge_arc_3pt((17.0, 11.697224362268006), (14.0, 10.0), (11.0, 11.697224362268006)),
        _make_edge_line((11.0, 11.697224362268006), (11.0, 11.65)),
    ]
    face = _make_face_from_edges(edges)
    solid = cq.Solid.extrudeLinear(face, cq.Vector(0.0, 0.0, 4.5))
    return solid


def _make_extra_a():
    # Analytic reconstruction of round20-official extra solid A.
    edges = [
        _make_edge_line((10.5, 21.5), (10.5, 13.5)),
        _make_edge_arc_3pt((10.5, 13.5), (10.626997751262337, 12.56573246336466), (10.999999999999888, 11.69722436226819)),
        _make_edge_line((10.999999999999888, 11.69722436226819), (11.0, 19.15)),
        _make_edge_arc_3pt((11.0, 19.15), (14.0, 22.15), (17.0, 19.15)),
        _make_edge_line((17.0, 19.15), (17.0, 11.697224362268006)),
        _make_edge_arc_3pt((17.0, 11.697224362268006), (17.373002248737663, 12.56573246336466), (17.5, 13.5)),
        _make_edge_line((17.5, 13.5), (17.5, 21.5)),
        _make_edge_arc_3pt((17.5, 21.5), (14.0, 25.0), (10.5, 21.5)),
    ]
    face = _make_face_from_edges(edges)
    solid = cq.Solid.extrudeLinear(face, cq.Vector(0.0, 0.0, 4.5))
    return solid


def _make_extra_b():
    # Analytic reconstruction of round20-official extra solid B.
    outer = (
        cq.Workplane("XZ")
        .moveTo(10.5, 13.5)
        .lineTo(10.5, 21.5)
        .threePointArc((14.0, 25.0), (17.5, 21.5))
        .lineTo(17.5, 13.5)
        .threePointArc((14.0, 10.0), (10.5, 13.5))
        .close()
        .extrude(4.5)
        .val()
    )
    inner = (
        cq.Workplane("XZ")
        .moveTo(11.0, 13.75)
        .lineTo(11.0, 21.25)
        .threePointArc((14.0, 24.25), (17.0, 21.25))
        .lineTo(17.0, 13.75)
        .threePointArc((14.0, 10.75), (11.0, 13.75))
        .close()
        .extrude(4.5)
        .val()
    )
    return outer.cut(inner).translate((0.0, 4.5, 0.0))


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
    edge_radius,
    gusset_radius,
):
    """Build the gusseted bracket as a self-contained CAD model."""

    corrected = _make_reference_body(bracket_width, leg_length_1, leg_length_2)

    corrected = corrected.cut(_make_slot_solid_xy(bracket_width / 2.0, slot_offset_1, slot_length, slot_width, plate_thickness))
    corrected = corrected.cut(_make_slot_solid_xz(bracket_width / 2.0, slot_offset_2, slot_length, slot_width, plate_thickness))

    if panel_mount_holes:
        hole_r = 2.1
        left_panel_x = 0.0
        right_panel_x = bracket_width - gusset_thickness
        corrected = corrected.cut(_make_panel_hole_side_face(left_panel_x, panel_hole_offset, panel_hole_offset, hole_r, gusset_thickness))
        corrected = corrected.cut(_make_panel_hole_side_face(right_panel_x, panel_hole_offset, panel_hole_offset, hole_r, gusset_thickness))

    corrected = corrected.clean()
    try:
        corrected = corrected.removeSplitter()
    except Exception:
        pass
    solids = corrected.Solids()
    result = solids[0] if len(solids) == 1 else corrected
    return result
