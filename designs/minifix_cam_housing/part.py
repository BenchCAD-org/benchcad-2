"""Parametric Häfele Minifix 15 eccentric-cam connector housing."""

import cadquery as cq


def build(
    body_diameter,
    housing_height,
    has_rim,
    rim_diameter,
    rim_height,
    bolt_axis_height,
    bolt_hole_diameter,
    pocket_depth,
    drive_style,
    drive_slot_width,
):
    """Build a single die-cast cam housing.

    The catalog specifies the mounting bore, panel mid-plane dimension, and
    edge-bolt hole; it does not dimension the cam pocket.  The drive recess
    and side hook window therefore use the documented dimensions with the
    explicitly proportional pocket depth from ``spec.py``.
    """
    result = cq.Workplane("XY").circle(body_diameter / 2.0).extrude(housing_height)

    if has_rim:
        result = (result.faces(">Z").workplane()
                  .circle(rim_diameter / 2.0).extrude(rim_height))

    # The drive recess is visible on the panel face.  0 is the PZ cross-slot
    # shown in the catalog; 1 is the alternative straight-slot variant.
    result = (result.faces(">Z").workplane()
              .rect(body_diameter * 0.52, drive_slot_width)
              .cutBlind(-pocket_depth))
    if drive_style == 0:
        result = (result.faces(">Z").workplane()
                  .rect(drive_slot_width, body_diameter * 0.52)
                  .cutBlind(-pocket_depth))

    # X - A is the catalogued depth below the bolt axis.  A round side opening
    # represents the cam hook's entry path for the Ø7/Ø8 connecting-bolt hole.
    hook_depth = housing_height - bolt_axis_height
    hook_window = (cq.Workplane("YZ").center(0.0, hook_depth)
                   .circle(bolt_hole_diameter / 2.0)
                   .extrude(body_diameter / 2.0))
    result = result.cut(hook_window)
    return result
