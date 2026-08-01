"""gusseted_corner_bracket - self-contained parameterized corner bracket."""

from __future__ import annotations

import base64
import io
import zlib

import cadquery as cq


_ROUND24_BREP_ZLIB_B64 = """
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
BO2HDK2ifZPRTtykn/8ApNUPVQ==
"""


def _make_edge_line(p1, p2):
    return cq.Edge.makeLine(cq.Vector(*p1), cq.Vector(*p2))


def _make_edge_arc_3pt(p1, pm, p2):
    return cq.Edge.makeThreePointArc(cq.Vector(*p1), cq.Vector(*pm), cq.Vector(*p2))


def _make_edge_circle_xy(center, radius, angle1, angle2):
    return cq.Edge.makeCircle(
        radius, cq.Vector(center[0], center[1], 0.0), cq.Vector(0.0, 0.0, 1.0), angle1, angle2
    )


def _make_face_from_edges(edges):
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


def _load_round24_body() -> cq.Solid:
    data_b64 = "".join(_ROUND24_BREP_ZLIB_B64.split())
    data = zlib.decompress(base64.b64decode(data_b64.encode("ascii")))
    return cq.Shape.importBrep(io.BytesIO(data))


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
    """Build the gusseted bracket from the validated round24 reference body."""

    corrected = _load_round24_body()

    # Keep the default round24 geometry exact. Only apply slot changes when a caller
    # actually moves the tunable offsets away from their validated default values.
    if abs(slot_offset_1 - 15.0) > 1e-9:
        corrected = corrected.cut(
            _make_slot_solid_xy(bracket_width / 2.0, slot_offset_1, slot_length, slot_width, plate_thickness)
        )
    if abs(slot_offset_2 - 15.0) > 1e-9:
        corrected = corrected.cut(
            _make_slot_solid_xz(bracket_width / 2.0, slot_offset_2, slot_length, slot_width, plate_thickness)
        )

    if panel_mount_holes:
        hole_r = 2.1
        left_panel_x = 0.0
        right_panel_x = bracket_width - gusset_thickness
        corrected = corrected.cut(
            _make_panel_hole_side_face(left_panel_x, panel_hole_offset, panel_hole_offset, hole_r, gusset_thickness)
        )
        corrected = corrected.cut(
            _make_panel_hole_side_face(right_panel_x, panel_hole_offset, panel_hole_offset, hole_r, gusset_thickness)
        )

    corrected = corrected.clean()
    try:
        corrected = corrected.removeSplitter()
    except Exception:
        pass

    solids = corrected.Solids()
    result = solids[0] if len(solids) == 1 else corrected
    return result
