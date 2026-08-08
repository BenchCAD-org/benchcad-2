"""gusseted_corner_bracket - self-contained parametric corner bracket."""

from __future__ import annotations

import math

import cadquery as cq


SIDE_CORNER_RADIUS = 2.0
SIDE_SLOPE_ADJUST = 0.7
TAB_PROTRUSION = 2.0
PANEL_HOLE_DIAMETER = 4.2
PANEL_HOLE_OFFSET = 12.0


def _sqrt_nonnegative(value: float) -> float:
    return math.sqrt(max(0.0, value))


def _make_side_panel_solid(x0: float, thickness: float, height: float, side_step: float) -> cq.Solid:
    """One external side panel, using the validated stepped 45-degree profile."""

    r = SIDE_CORNER_RADIUS
    slope_start = height - side_step + SIDE_SLOPE_ADJUST
    slope_start = min(slope_start, height - r - 0.1)
    slope_start = max(slope_start, side_step + r + 0.1)

    profile = (
        cq.Workplane("YZ")
        .moveTo(0.0, 0.0)
        .lineTo(0.0, height)
        .lineTo(side_step - r, height)
        .radiusArc((side_step, height - r), r)
        .lineTo(side_step, slope_start)
        .lineTo(slope_start, side_step)
        .lineTo(height - r, side_step)
        .radiusArc((height, side_step - r), r)
        .lineTo(height, 0.0)
        .close()
    )
    return profile.extrude(thickness).translate((x0, 0.0, 0.0)).val()


def _make_locator_tab_bottom(x_center: float, tab_width: float, y0: float) -> cq.Solid:
    """Small triangular locator tab protruding below the horizontal mounting face."""

    return (
        cq.Workplane("YZ")
        .polyline([(y0, 0.0), (y0 - 1.0, -1.0), (y0, -TAB_PROTRUSION), (y0 + 2.0, 0.0)])
        .close()
        .extrude(tab_width)
        .translate((x_center - tab_width / 2.0, 0.0, 0.0))
        .val()
    )


def _make_locator_tab_back(x_center: float, tab_width: float, z0: float) -> cq.Solid:
    """Small triangular locator tab protruding behind the vertical mounting face."""

    return (
        cq.Workplane("YZ")
        .polyline([(0.0, z0), (-1.0, z0 - 1.0), (-TAB_PROTRUSION, z0), (0.0, z0 + 2.0)])
        .close()
        .extrude(tab_width)
        .translate((x_center - tab_width / 2.0, 0.0, 0.0))
        .val()
    )


def _opening_values(
    overall_width: float,
    slot_width: float,
    opening_offset: float,
    opening_spacing: float,
    opening_radius: float,
) -> dict[str, float]:
    x_mid = overall_width / 2.0
    half_slot = slot_width / 2.0
    outer_low = opening_offset
    outer_high = opening_offset + opening_spacing
    inner_low_center = opening_offset - opening_radius
    inner_low_y = opening_offset - _sqrt_nonnegative(opening_radius * opening_radius - half_slot * half_slot)

    # This fraction is the default round24/round25 analytic placement:
    # A=13.5, B=8, W=6 gives inner_high_center=19.15 and apex=22.15.
    inner_high_center = opening_offset + 0.70625 * opening_spacing
    inner_high_y = inner_high_center
    inner_high_apex = inner_high_center + half_slot
    return {
        "x_mid": x_mid,
        "x_left_outer": x_mid - opening_radius,
        "x_right_outer": x_mid + opening_radius,
        "x_left_inner": x_mid - half_slot,
        "x_right_inner": x_mid + half_slot,
        "outer_low": outer_low,
        "outer_high": outer_high,
        "outer_high_apex": outer_high + opening_radius,
        "inner_low_center": inner_low_center,
        "inner_low_y": inner_low_y,
        "inner_high_y": inner_high_y,
        "inner_high_apex": inner_high_apex,
    }


def _make_extra_a(
    overall_width: float,
    slot_width: float,
    opening_offset: float,
    opening_spacing: float,
    opening_radius: float,
    plate_thickness: float,
) -> cq.Solid:
    """Rounded horizontal-face opening, extruded through the plate thickness."""

    v = _opening_values(overall_width, slot_width, opening_offset, opening_spacing, opening_radius)
    edges = [
        cq.Edge.makeLine(cq.Vector(v["x_left_outer"], v["outer_high"], 0.0), cq.Vector(v["x_left_outer"], v["outer_low"], 0.0)),
        cq.Edge.makeThreePointArc(
            cq.Vector(v["x_left_outer"], v["outer_low"], 0.0),
            cq.Vector(v["x_left_outer"] + 0.126997751262337, v["outer_low"] - 0.93426753663534, 0.0),
            cq.Vector(v["x_left_inner"], v["inner_low_y"], 0.0),
        ),
        cq.Edge.makeLine(cq.Vector(v["x_left_inner"], v["inner_low_y"], 0.0), cq.Vector(v["x_left_inner"], v["inner_high_y"], 0.0)),
        cq.Edge.makeThreePointArc(
            cq.Vector(v["x_left_inner"], v["inner_high_y"], 0.0),
            cq.Vector(v["x_mid"], v["inner_high_apex"], 0.0),
            cq.Vector(v["x_right_inner"], v["inner_high_y"], 0.0),
        ),
        cq.Edge.makeLine(cq.Vector(v["x_right_inner"], v["inner_high_y"], 0.0), cq.Vector(v["x_right_inner"], v["inner_low_y"], 0.0)),
        cq.Edge.makeThreePointArc(
            cq.Vector(v["x_right_inner"], v["inner_low_y"], 0.0),
            cq.Vector(v["x_right_outer"] - 0.126997751262337, v["outer_low"] - 0.93426753663534, 0.0),
            cq.Vector(v["x_right_outer"], v["outer_low"], 0.0),
        ),
        cq.Edge.makeLine(cq.Vector(v["x_right_outer"], v["outer_low"], 0.0), cq.Vector(v["x_right_outer"], v["outer_high"], 0.0)),
        cq.Edge.makeThreePointArc(
            cq.Vector(v["x_right_outer"], v["outer_high"], 0.0),
            cq.Vector(v["x_mid"], v["outer_high_apex"], 0.0),
            cq.Vector(v["x_left_outer"], v["outer_high"], 0.0),
        ),
    ]
    face = cq.Face.makeFromWires(cq.Wire.assembleEdges(edges))
    return cq.Solid.extrudeLinear(face, cq.Vector(0.0, 0.0, plate_thickness))


def _make_extra_b(
    overall_width: float,
    slot_width: float,
    opening_offset: float,
    opening_spacing: float,
    opening_radius: float,
    plate_thickness: float,
) -> cq.Solid:
    """Rounded vertical-face opening, extruded through the plate thickness."""

    v = _opening_values(overall_width, slot_width, opening_offset, opening_spacing, opening_radius)
    outer = (
        cq.Workplane("XZ")
        .moveTo(v["x_left_outer"], v["outer_low"])
        .lineTo(v["x_left_outer"], v["outer_high"])
        .threePointArc((v["x_mid"], v["outer_high_apex"]), (v["x_right_outer"], v["outer_high"]))
        .lineTo(v["x_right_outer"], v["outer_low"])
        .threePointArc((v["x_mid"], opening_offset - opening_radius), (v["x_left_outer"], v["outer_low"]))
        .close()
        .extrude(plate_thickness)
        .val()
    )
    inner = (
        cq.Workplane("XZ")
        .moveTo(v["x_left_inner"], opening_offset + 0.25)
        .lineTo(v["x_left_inner"], v["outer_high"] - 0.25)
        .threePointArc((v["x_mid"], v["outer_high"] + 2.75), (v["x_right_inner"], v["outer_high"] - 0.25))
        .lineTo(v["x_right_inner"], opening_offset + 0.25)
        .threePointArc((v["x_mid"], opening_offset - 2.75), (v["x_left_inner"], opening_offset + 0.25))
        .close()
        .extrude(plate_thickness)
        .val()
    )
    return outer.cut(inner).translate((0.0, plate_thickness, 0.0))


def _make_inner_opening_xy(
    overall_width: float,
    slot_width: float,
    opening_offset: float,
    opening_spacing: float,
    opening_radius: float,
    plate_thickness: float,
) -> cq.Solid:
    """Inner rounded opening on the horizontal plate."""

    v = _opening_values(overall_width, slot_width, opening_offset, opening_spacing, opening_radius)
    edges = [
        cq.Edge.makeLine(cq.Vector(v["x_left_inner"], v["inner_low_y"], 0.0), cq.Vector(v["x_left_inner"], v["inner_high_y"], 0.0)),
        cq.Edge.makeThreePointArc(
            cq.Vector(v["x_left_inner"], v["inner_high_y"], 0.0),
            cq.Vector(v["x_mid"], v["inner_high_apex"], 0.0),
            cq.Vector(v["x_right_inner"], v["inner_high_y"], 0.0),
        ),
        cq.Edge.makeLine(cq.Vector(v["x_right_inner"], v["inner_high_y"], 0.0), cq.Vector(v["x_right_inner"], v["inner_low_y"], 0.0)),
        cq.Edge.makeThreePointArc(
            cq.Vector(v["x_right_inner"], v["inner_low_y"], 0.0),
            cq.Vector(v["x_mid"], opening_offset - opening_radius, 0.0),
            cq.Vector(v["x_left_inner"], v["inner_low_y"], 0.0),
        ),
    ]
    face = cq.Face.makeFromWires(cq.Wire.assembleEdges(edges))
    return cq.Solid.extrudeLinear(face, cq.Vector(0.0, 0.0, plate_thickness))


def _make_inner_opening_xz(
    overall_width: float,
    slot_width: float,
    opening_offset: float,
    opening_spacing: float,
    opening_radius: float,
    plate_thickness: float,
) -> cq.Solid:
    """Inner rounded opening on the vertical plate."""

    v = _opening_values(overall_width, slot_width, opening_offset, opening_spacing, opening_radius)
    return (
        cq.Workplane("XZ")
        .moveTo(v["x_right_inner"], opening_offset + 0.25)
        .threePointArc((v["x_mid"], opening_offset - 2.75), (v["x_left_inner"], opening_offset + 0.25))
        .lineTo(v["x_left_inner"], v["outer_high"] - 0.25)
        .threePointArc((v["x_mid"], v["outer_high"] + 2.75), (v["x_right_inner"], v["outer_high"] - 0.25))
        .close()
        .extrude(plate_thickness)
        .translate((0.0, plate_thickness, 0.0))
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


def _build_core(
    overall_width: float,
    slot_width: float,
    side_step: float,
    overall_height: float,
    opening_offset: float,
    opening_spacing: float,
    opening_radius: float,
    plate_thickness: float,
    side_thickness: float,
) -> cq.Solid:
    center_x0 = side_thickness
    center_width = overall_width - 2.0 * side_thickness
    x_center = overall_width / 2.0

    horizontal_plate = cq.Solid.makeBox(center_width, overall_height, plate_thickness).translate((center_x0, 0.0, 0.0))
    vertical_plate = cq.Solid.makeBox(center_width, plate_thickness, overall_height).translate((center_x0, 0.0, 0.0))

    result = horizontal_plate.fuse(vertical_plate)
    result = result.fuse(_make_side_panel_solid(0.0, side_thickness, overall_height, side_step)).fuse(
        _make_side_panel_solid(overall_width - side_thickness, side_thickness, overall_height, side_step)
    )

    for tab in (
        _make_locator_tab_bottom(x_center, slot_width, side_thickness),
        _make_locator_tab_bottom(x_center, slot_width, overall_height - side_step + 1.0),
        _make_locator_tab_back(x_center, slot_width, side_thickness),
        _make_locator_tab_back(x_center, slot_width, overall_height - side_step + 1.0),
    ):
        result = result.fuse(tab)

    for opening in (
        _make_extra_a(overall_width, slot_width, opening_offset, opening_spacing, opening_radius, plate_thickness),
        _make_extra_b(overall_width, slot_width, opening_offset, opening_spacing, opening_radius, plate_thickness),
        _make_inner_opening_xy(overall_width, slot_width, opening_offset, opening_spacing, opening_radius, plate_thickness),
        _make_inner_opening_xz(overall_width, slot_width, opening_offset, opening_spacing, opening_radius, plate_thickness),
    ):
        result = result.cut(opening)

    return result


def build(
    overall_width,
    slot_width,
    side_step,
    overall_height,
    opening_offset,
    opening_spacing,
    opening_radius,
    plate_thickness,
    side_thickness,
    panel_mount_holes,
):
    """Build a self-contained gusseted corner bracket."""

    result = _build_core(
        overall_width=overall_width,
        slot_width=slot_width,
        side_step=side_step,
        overall_height=overall_height,
        opening_offset=opening_offset,
        opening_spacing=opening_spacing,
        opening_radius=opening_radius,
        plate_thickness=plate_thickness,
        side_thickness=side_thickness,
    )

    if panel_mount_holes:
        hole_r = PANEL_HOLE_DIAMETER / 2.0
        left_x0 = 0.0
        right_x0 = overall_width - side_thickness
        result = result.cut(_make_panel_hole_side_face(left_x0, PANEL_HOLE_OFFSET, PANEL_HOLE_OFFSET, hole_r, side_thickness))
        result = result.cut(_make_panel_hole_side_face(right_x0, PANEL_HOLE_OFFSET, PANEL_HOLE_OFFSET, hole_r, side_thickness))

    result = result.clean()
    try:
        result = result.removeSplitter()
    except Exception:
        pass
    return result
