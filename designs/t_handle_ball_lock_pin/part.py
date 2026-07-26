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

    # Reconstruct the plastic handle from the two orthographic outlines in the
    # datasheet.  The XZ side profile supplies the two T wings and their central
    # push-button recess; the YZ end envelope supplies the rounded, eye-shaped
    # cross-section.  Their intersection preserves exact l3, d3 and m envelopes.
    wing_x0 = handle_x0 + 0.36 * handle_length
    center_recess_x = handle_x0 + 0.69 * handle_length
    recess_half_height = 0.16 * handle_neck_d
    side_profile = (
        cq.Workplane("XZ")
        .moveTo(wing_x0, 0.48 * handle_neck_d)
        .spline(
            [
                (handle_x0 + 0.56 * handle_length, 0.65 * handle_neck_d),
                (handle_x0 + 0.76 * handle_length, 0.42 * handle_height),
                (handle_x0 + 0.90 * handle_length, 0.50 * handle_height),
                (handle_x1, 0.50 * handle_height),
            ],
            includeCurrent=True,
        )
        .lineTo(handle_x1, 0.42 * handle_height)
        .spline(
            [
                (handle_x0 + 0.86 * handle_length, 0.34 * handle_height),
                (handle_x0 + 0.73 * handle_length, 0.10 * handle_height),
                (center_recess_x, recess_half_height),
            ],
            includeCurrent=True,
        )
        .lineTo(center_recess_x, -recess_half_height)
        .spline(
            [
                (handle_x0 + 0.73 * handle_length, -0.10 * handle_height),
                (handle_x0 + 0.86 * handle_length, -0.34 * handle_height),
                (handle_x1, -0.42 * handle_height),
            ],
            includeCurrent=True,
        )
        .lineTo(handle_x1, -0.50 * handle_height)
        .spline(
            [
                (handle_x0 + 0.90 * handle_length, -0.50 * handle_height),
                (handle_x0 + 0.76 * handle_length, -0.42 * handle_height),
                (handle_x0 + 0.56 * handle_length, -0.65 * handle_neck_d),
                (wing_x0, -0.48 * handle_neck_d),
            ],
            includeCurrent=True,
        )
        .close()
        .extrude(handle_thickness, both=True)
    )
    profile_round = min(
        0.045 * handle_height,
        0.06 * handle_length,
        0.10 * handle_thickness,
    )
    side_profile = side_profile.edges("|Y").fillet(profile_round)

    end_origin_x = handle_x0 + 0.32 * handle_length
    end_length = handle_x1 - end_origin_x
    end_ellipse = (
        cq.Workplane("YZ", origin=(end_origin_x, 0.0, 0.0))
        .ellipse(handle_thickness / 2.0, handle_height / 2.0)
        .extrude(end_length)
    )
    end_spine = (
        cq.Workplane("YZ", origin=(end_origin_x, 0.0, 0.0))
        .rect(0.60 * handle_thickness, handle_height)
        .extrude(end_length)
    )
    wing_body = side_profile.intersect(end_ellipse.union(end_spine))

    # The front hub is round at the pin shoulder and blends into the broad
    # handle root.  d4 is exact; the blend station is a drawing proportion.
    hub = (
        cq.Workplane("YZ", origin=(handle_x0, 0.0, 0.0))
        .circle(handle_neck_d / 2.0)
        .workplane(offset=0.48 * handle_length)
        .ellipse(handle_thickness / 2.0, handle_neck_d / 2.0)
        .loft(combine=True)
    )
    handle = hub.union(wing_body)

    # Two key-ring slots are explicitly shown in the datasheet.  Their sizes
    # are not specified: length=0.52*m, width=0.18*m, centres at +/-0.36*d3.
    slot_length = 0.52 * handle_thickness
    slot_width = 0.18 * handle_thickness
    slot_x0 = handle_x0 + 0.90 * handle_length
    slot_depth = 0.14 * handle_length + 2.0
    slot_tool = (
        cq.Workplane("YZ", origin=(slot_x0 - 1.0, 0.0, 0.0))
        .pushPoints([(0.0, 0.36 * handle_height), (0.0, -0.36 * handle_height)])
        .slot2D(slot_length, slot_width, 0.0)
        .extrude(slot_depth)
    )
    handle = handle.cut(slot_tool)

    # Spring-loaded push button, visible but undimensioned in the drawing.
    # It is coaxial with the pin (as shown in the side view) but remains a
    # clearly separate metal body: an annular clearance bore is cut into the
    # plastic handle and the exposed cap is stepped up from its sliding stem.
    button_d = 0.34 * handle_neck_d
    stem_d = 0.72 * button_d
    button_embed = 0.10 * handle_length
    button_exposed = 0.16 * handle_length
    button_gap = max(0.01 * handle_length, 0.10)
    button_face_x = center_recess_x

    button_stem = (
        cq.Workplane("YZ", origin=(button_face_x - button_embed, 0.0, 0.0))
        .circle(stem_d / 2.0)
        .extrude(button_embed + button_gap + 0.03 * handle_length)
    )
    button_cap = (
        cq.Workplane("YZ", origin=(button_face_x + button_gap, 0.0, 0.0))
        .circle(button_d / 2.0)
        .extrude(button_exposed)
    )
    button = button_stem.union(button_cap)

    button_clearance = (
        cq.Workplane(
            "YZ",
            origin=(button_face_x - button_embed - 0.02 * handle_length, 0.0, 0.0),
        )
        .circle(button_d / 2.0 + 0.035 * handle_neck_d)
        .extrude(button_embed + button_gap + 0.04 * handle_length)
    )
    handle = handle.cut(button_clearance)

    result = cq.Compound.makeCompound(
        [shaft.val(), handle.val(), button.val(), upper_ball.val(), lower_ball.val()]
    )
    return result
