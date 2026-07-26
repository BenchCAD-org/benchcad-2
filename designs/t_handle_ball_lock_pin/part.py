"""Parametric Elesa+Ganter GN 113.8 T-handle ball lock pin.

The model represents the externally visible locked state.  Catalog dimensions
drive the pin and handle envelopes exactly.  The datasheet does not dimension
the ball diameter, ball-pocket depth, push button, key-ring slots, handle
curves, or edge radii; those details use the explicit proportions documented
below.  The hidden actuator and compression spring are intentionally omitted.
"""

import cadquery as cq


def build(
    catalog_index,
    pin_d,
    grip_length,
    locked_envelope_d,
    handle_height,
    handle_neck_d,
    tip_to_ball_length,
    handle_length,
    handle_thickness,
):
    """Build the five externally visible GN 113.8 bodies in locked position."""
    # catalog_index selects one coupled datasheet row in spec.py.  Geometry is
    # driven by that row's dimensions rather than by the index itself.
    _ = catalog_index

    pin_r = pin_d / 2.0
    shaft_length = tip_to_ball_length + grip_length
    tip_chamfer = min(0.08 * pin_d, 0.45 * tip_to_ball_length)

    # Stainless pin, nominal d1 and l1/l2 dimensions.  The small tip chamfer is
    # visible in the GN 113.8 drawing but not dimensioned (proportion: 0.08*d1).
    shaft = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(0.0, pin_r - tip_chamfer)
        .lineTo(tip_chamfer, pin_r)
        .lineTo(shaft_length, pin_r)
        .lineTo(shaft_length, 0.0)
        .close()
        .revolve(360.0, (0.0, 0.0), (1.0, 0.0))
    )

    # The table gives only d2, the total locked envelope across the two balls.
    # Sphere radius is therefore an honest drawing-derived proportion; their
    # centres are placed so the finished envelope is exactly d2.
    ball_protrusion = (locked_envelope_d - pin_d) / 2.0
    ball_r = max(0.16 * pin_d, 1.15 * ball_protrusion)
    ball_center_r = locked_envelope_d / 2.0 - ball_r
    ball_x = tip_to_ball_length

    upper_ball = cq.Workplane("XY").sphere(ball_r).translate((ball_x, 0.0, ball_center_r))
    lower_ball = cq.Workplane("XY").sphere(ball_r).translate((ball_x, 0.0, -ball_center_r))

    # Slightly oversized spherical pockets keep the balls as separate bodies.
    pocket_r = 1.03 * ball_r
    upper_pocket = cq.Workplane("XY").sphere(pocket_r).translate((ball_x, 0.0, ball_center_r))
    lower_pocket = cq.Workplane("XY").sphere(pocket_r).translate((ball_x, 0.0, -ball_center_r))
    shaft = shaft.cut(upper_pocket).cut(lower_pocket)

    handle_x0 = shaft_length
    handle_x1 = handle_x0 + handle_length

    # Plastic handle loft.  d3, d4, l3 and m are exact catalog envelopes;
    # the middle-section placement and ellipse are drawing proportions.  The
    # loft honors both the round neck in the end view and the broad, rounded
    # T-handle envelope at the button end.
    handle = (
        cq.Workplane("YZ", origin=(handle_x0, 0.0, 0.0))
        .circle(handle_neck_d / 2.0)
        .workplane(offset=0.46 * handle_length)
        .ellipse(0.48 * handle_thickness, 0.34 * handle_height)
        .workplane(offset=0.54 * handle_length)
        .ellipse(handle_thickness / 2.0, handle_height / 2.0)
        .loft(combine=True)
    )

    # The side view has a concave opening between the two T wings around the
    # push button.  Its radius and penetration are undimensioned proportions.
    notch_r = 0.30 * handle_height
    notch_center_x = handle_x1 + 0.16 * handle_length
    center_notch = (
        cq.Workplane("XZ", origin=(notch_center_x, 0.0, 0.0))
        .circle(notch_r)
        .extrude(handle_thickness, both=True)
    )
    handle = handle.cut(center_notch)

    # Two key-ring slots are explicitly shown in the datasheet.  Their sizes
    # are not specified: length=0.52*m, width=0.18*m, centres at +/-0.36*d3.
    slot_length = 0.52 * handle_thickness
    slot_width = 0.18 * handle_thickness
    slot_x0 = handle_x0 + 0.88 * handle_length
    slot_depth = 0.14 * handle_length + 2.0
    slot_tool = (
        cq.Workplane("YZ", origin=(slot_x0 - 1.0, 0.0, 0.0))
        .pushPoints([(0.0, 0.36 * handle_height), (0.0, -0.36 * handle_height)])
        .slot2D(slot_length, slot_width, 0.0)
        .extrude(slot_depth)
    )
    handle = handle.cut(slot_tool)

    # Spring-loaded push button, visible but undimensioned in the drawing.
    # It is a separate body; a clearance recess prevents it merging with the
    # plastic handle during STEP export.
    button_d = 0.34 * handle_neck_d
    button_length = 0.24 * handle_length
    button_x0 = handle_x1 - 0.06 * handle_length
    button = (
        cq.Workplane("YZ")
        .circle(button_d / 2.0)
        .extrude(button_length)
        .translate((button_x0, 0.0, 0.0))
    )

    result = cq.Compound.makeCompound(
        [shaft.val(), handle.val(), button.val(), upper_ball.val(), lower_ball.val()]
    )
    return result
