"""quarter_turn_cam_latch — the parametric part (assembly).

A quarter-turn cam latch (Southco E5 class) as the parts it is sold as: the
LATCH HOUSING (domed head above the panel over the double-D body that drops
through the cutout — the flats are the panel anti-rotation), the separate
stepped CAM ("order latch and cam separately": hub with the M6 screw seat, a
neck at hub level, a Z-step, and the flat clamping tip — the sheet's 23 of
flat past the step, tip at the FULL cam reach 45 from the axis), and the
MOUNTING NUT threaded up the body behind the panel.

Drawn latched, panel face at z=0, body dropping -Z. The cam hangs off the
body end with a 0.3 mm screw-joint gap and its step rises the tip flat to the
grip plane at z = -grip. The one-sided blade sweeps a quarter turn about the
body axis; the step radius sits outside the nut's corners, so the whole
travel is interference-free by construction (and probed).

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def _housing(head_d, head_h, body_d, afl, body_l, slotted):
    # domed head above the panel: radiused rim per the E5 cap
    head = (
        cq.Workplane("XY").circle(head_d / 2.0).extrude(head_h)
        .edges(">Z").fillet(min(head_h * 0.45, head_d * 0.12))
    )
    if slotted:
        slot = (
            cq.Workplane("XY")
            .box(head_d + 2.0, head_d * 0.14, head_h * 0.55)
            .translate((0.0, 0.0, head_h))
        )
        head = head.cut(slot)
    # double-D body: circle with two parallel flats (across-flats = afl)
    body = cq.Workplane("XY").circle(body_d / 2.0).extrude(-body_l)
    flats = cq.Workplane("XY").box(afl, body_d + 4.0, 2.0 * body_l + 4.0)
    body = body.intersect(flats)
    return head.union(body)


def _cam(cam_l, cam_w, cam_t, tip_flat, rise, step_x):
    """One-sided stepped cam, local frame: axis at origin, hub top at z=0
    (mates to the body end), blade along +X, tip at x = cam_l."""
    r_hub = max(7.0, 0.55 * cam_w)
    hub = cq.Workplane("XY").circle(r_hub).extrude(-cam_t)
    # neck at hub level out to the step
    neck = (
        cq.Workplane("XY")
        .box(step_x - r_hub * 0.5 + cam_t * 1.4 + 1.0, cam_w, cam_t,
             centered=(False, True, False))
        .translate((r_hub * 0.5, 0.0, -cam_t))
    )
    # Z-step riser ON the step radius (never inboard of it, so no rotation
    # can carry it inside the housing circle), buried into the tip's start
    riser = (
        cq.Workplane("XY")
        .box(cam_t * 1.4 + cam_w * 0.5, cam_w, rise + cam_t,
             centered=(False, True, False))
        .translate((step_x, 0.0, -cam_t))
    )
    # flat clamping tip: spans exactly step_x .. cam_l (the tip IS the full
    # axis-to-tip reach; the slot's own end rounding stays inside that span)
    tip = (
        cq.Workplane("XY")
        .slot2D(tip_flat, cam_w, 0)
        .extrude(-cam_t)
        .translate(((step_x + cam_l) / 2.0, 0.0, rise))
    )
    cam = hub.union(neck).union(riser).union(tip)
    # M6 cam-screw clearance through the hub
    cam = cam.cut(
        cq.Workplane("XY").circle(3.2).extrude(-cam_t * 3.0)
        .translate((0.0, 0.0, cam_t))
    )
    return cam


def _nut(body_d):
    """Mounting nut behind the panel: hex on a round clearance bore."""
    af = body_d + 2.0
    nut = (
        cq.Workplane("XY").polygon(6, af / 0.866).extrude(-4.0)
        .cut(cq.Workplane("XY").circle(body_d / 2.0 + 0.15).extrude(-6.0)
             .translate((0.0, 0.0, 1.0)))
    )
    return nut


def build(head_d, head_h, body_d, afl, body_l, grip, cam_l, cam_w, cam_t,
          tip_flat, slotted):
    # cam joint: hub top 0.3 under the body end; the step lifts the tip flat's
    # clamping face to the grip plane z = -grip
    z_hub = -(body_l + 0.3)
    rise = body_l + 0.3 - grip
    # the riser stands outside the nut's hex corners so the quarter-turn swing
    # can never touch it
    step_x = cam_l - tip_flat

    result = cq.Assembly(name="quarter_turn_cam_latch")
    result.add(_housing(head_d, head_h, body_d, afl, body_l, slotted),
               name="housing")
    result.add(_cam(cam_l, cam_w, cam_t, tip_flat, rise, step_x), name="cam",
               loc=cq.Location((0.0, 0.0, z_hub)))
    result.add(_nut(body_d), name="mounting_nut",
               loc=cq.Location((0.0, 0.0, -1.5)))
    return result
