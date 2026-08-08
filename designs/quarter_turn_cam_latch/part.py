"""quarter_turn_cam_latch — the parametric part (assembly).

A quarter-turn cam latch (Southco E5 class) as the parts it is sold as
("Order latch and cam separately"):

  housing       domed head above the panel, compressed sealing washer under
                the rim, double-D body dropping through the panel cutout (the
                flats are the anti-rotation)
  mounting_nut  threaded up the body behind the panel, clamping the panel
  cam           the formed one-sided arm: hub, tapered neck, Z-step, and the
                flat clamping tip
  cam_screw     the M6 that holds the cam on the housing end

Datum and stack, read off the E5 section (docs/assets/refs/..._drawing.png):

    z = 0            head underside — the datum BOTH catalog depths run from
    0 .. -0.5        compressed sealing washer (the sheet's 0.5)
    -0.5 .. -1.5     the thinnest catalog panel (the sheet's 1)
    -1.5 .. -5.7     mounting nut, sitting straight up against the panel
    -grip            the cam's clamping face
    -body_l          the back of the cam screw's head

`body_l` is the catalog depth behind the head (27.2 / 45.5 / 58.2 / 68.2) and
on the sheet it covers housing + cam + screw head, so the housing itself is
`body_l - cam_t - joint - screw head` and the stack ends exactly on `body_l`.
The cam's Z-step is whatever is left over: `rise = body_l - cam_t - 4 - grip`.

The cam is built the way it is made: a constant-thickness formed part, i.e.
the Z-shaped side profile intersected with the plan footprint, so no
combination of parameters can turn the step into a solid block.

Interface + examples: docs/DESIGN_SPEC.md
"""

import math

import cadquery as cq

# ── stack constants, all off the E5 section ──────────────────────────────────
WASHER_T = 0.5        # compressed sealing washer (sheet: "0.5 (.02)")
PANEL_T = 1.0         # thinnest catalog panel (sheet: "1 (.04)")
NUT_H = 4.2           # mounting nut height, scaled off the section
CAM_JOINT = 0.2       # parting gap, housing end to cam hub
SCREW_HEAD_H = 4.0    # ISO 4017 M6 head height
SCREW_AF = 10.0       # ISO 4017 M6 head across-flats
SCREW_D = 6.0         # M6 nominal
STEP_CLEAR = 0.6      # cam-to-housing-barrel clearance at the step foot
STEP_MAX_SLOPE = 1.732  # steepest formed offset leg, tan(60 deg)
MIN_GRIP = WASHER_T + PANEL_T + NUT_H + 1.0  # see the note by check()


def nut_af(body_d):
    """Mounting-nut across-flats. The section draws the nut ~27.3 wide over
    the Ø22.5 body — taken here as across-FLATS, which leaves a 2.4 wall.
    (Its two inner lines sit at half the silhouette, which would normally
    read as across-corners; that reading gives A/F 23.6 and a 0.55 wall,
    i.e. not a nut, so the flats reading is the one that can be made.)"""
    return body_d + 4.8


def housing_length(body_l, cam_t):
    """Housing behind the head underside. `body_l` is the catalog depth and
    covers housing + cam + screw head, so the housing gets what is left."""
    return body_l - cam_t - CAM_JOINT - SCREW_HEAD_H


def cam_offset(body_l, cam_t, grip):
    """The cam's Z-step: hub plane to clamping plane (the sheet's 4)."""
    return housing_length(body_l, cam_t) + CAM_JOINT - grip


def cam_hub_r(body_d, cam_w):
    """Cam hub radius — covers the housing end, and always wider than the
    blade so the neck is a real taper."""
    return max(0.5 * body_d + 1.5, 0.55 * cam_w + 1.0)


def cam_neck(cam_l, cam_w, r_hub):
    """The concave neck: an arc tangent to the hub circle and to the blade
    flank, so the blade grows out of the hub the way the sheet's top view
    shows it — the taper is still narrowing well outside the Ø28 head, which
    takes a blend radius of roughly 3x the blade width.

    Returns (radius, x of the flank tangency). The radius is capped so the
    tangency always lands well inboard of the tip's corner rounds, whatever
    the sampler picks."""
    half, r_tip = 0.5 * cam_w, 0.22 * cam_w
    cx_max = 0.55 * (cam_l - r_tip)
    r_max = (cx_max ** 2 / (r_hub - half) - r_hub - half) / 2.0
    r_neck = max(0.3 * cam_w, min(2.9 * cam_w, r_max))
    return r_neck, math.sqrt((r_hub + r_neck) ** 2 - (half + r_neck) ** 2)


def cam_step_run(cam_l, tip_flat, body_d):
    """Horizontal room the Z-step has to work in: it may only start leaving
    the hub plane once it is clear of the housing barrel, and it has to be up
    at tip level by the time the flat begins. Everything inboard of this stays
    at hub level, under the housing end — which is what keeps the cam clear of
    the barrel through the whole quarter turn."""
    return (cam_l - tip_flat) - (0.5 * body_d + STEP_CLEAR)


def _housing(head_d, head_h, body_d, afl, housing_l, slotted):
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
    # the compressed sealing washer under the rim (the sheet's 0.5)
    head = head.union(
        cq.Workplane("XY").circle(head_d / 2.0 - 0.4).extrude(-WASHER_T)
    )
    # double-D body: circle with two parallel flats (across-flats = afl)
    body = cq.Workplane("XY").circle(body_d / 2.0).extrude(-housing_l)
    flats = cq.Workplane("XY").box(afl, body_d + 4.0, 2.0 * housing_l + 4.0)
    body = body.intersect(flats)
    # blind seat for the M6 cam screw, up from the housing end
    seat = min(10.0, 0.55 * housing_l)
    body = body.cut(
        cq.Workplane("XY").circle(SCREW_D / 2.0 + 0.3).extrude(seat + 1.0)
        .translate((0.0, 0.0, -housing_l - 1.0))
    )
    return head.union(body)


def _cam(cam_l, cam_w, cam_t, tip_flat, rise, r_hub, body_d):
    """One-sided formed cam, local frame: axis at origin, hub plate top at
    z=0 (mates to the housing end), blade along +X, tip at x = cam_l, the
    clamping face `rise` above the hub plane.

    Built as (Z-shaped side profile) ∩ (plan footprint) — a constant-thickness
    formed part, which is what the sheet shows and what keeps the step from
    ever becoming a block.
    """
    half = cam_w / 2.0
    r_tip = 0.22 * cam_w

    # ── plan footprint ───────────────────────────────────────────────────────
    r_neck, cx = cam_neck(cam_l, cam_w, r_hub)
    k = r_hub / (r_hub + r_neck)
    t1u = (cx * k, (half + r_neck) * k)
    t1l = (t1u[0], -t1u[1])
    t2u, t2l = (cx, half), (cx, -half)

    def arc_mid(centre, radius, pa, pb):
        a = math.atan2(pa[1] - centre[1], pa[0] - centre[0])
        b = math.atan2(pb[1] - centre[1], pb[0] - centre[0])
        if abs(b - a) > math.pi:
            b += 2 * math.pi if b < a else -2 * math.pi
        m = (a + b) / 2.0
        return (centre[0] + radius * math.cos(m), centre[1] + radius * math.sin(m))

    cu, cl = (cx, half + r_neck), (cx, -half - r_neck)
    tcu, tcl = (cam_l - r_tip, half - r_tip), (cam_l - r_tip, -half + r_tip)
    plan = (
        cq.Workplane("XY")
        .moveTo(*t1u)
        .threePointArc(arc_mid(cu, r_neck, t1u, t2u), t2u)      # concave neck
        .lineTo(cam_l - r_tip, half)
        .threePointArc(arc_mid(tcu, r_tip, (cam_l - r_tip, half),
                               (cam_l, half - r_tip)), (cam_l, half - r_tip))
        .lineTo(cam_l, -half + r_tip)
        .threePointArc(arc_mid(tcl, r_tip, (cam_l, -half + r_tip),
                               (cam_l - r_tip, -half)), (cam_l - r_tip, -half))
        .lineTo(*t2l)
        .threePointArc(arc_mid(cl, r_neck, t2l, t1l), t1l)      # concave neck
        .threePointArc((-r_hub, 0.0), t1u)                      # back of hub
        .close()
        .extrude(rise + cam_t + 2.0)
        .translate((0.0, 0.0, -cam_t - 1.0))
    )

    # ── side profile: constant-thickness Z ───────────────────────────────────
    x_step = cam_l - tip_flat                       # the sheet's 23 starts here
    # the step may only leave the hub plane once it is outside the housing
    # barrel; everything inboard of x_foot stays under the housing end
    run = max(0.5, min(1.6 * rise + cam_t, cam_step_run(cam_l, tip_flat, body_d)))
    x_foot = x_step - run                           # inboard foot of the step
    x_lo, x_hi = -(r_hub + 1.0), cam_l + 1.0
    side = (
        cq.Workplane("XZ")
        .moveTo(x_lo, 0.0)
        .lineTo(x_foot, 0.0).lineTo(x_step, rise).lineTo(x_hi, rise)
        .lineTo(x_hi, rise - cam_t).lineTo(x_step, rise - cam_t)
        .lineTo(x_foot, -cam_t).lineTo(x_lo, -cam_t)
        .close()
        .extrude(cam_w + 4.0)
        .translate((0.0, half + 2.0, 0.0))
    )

    cam = plan.intersect(side)
    # M6 cam-screw clearance through the hub
    return cam.cut(
        cq.Workplane("XY").circle(SCREW_D / 2.0 + 0.2)
        .extrude(rise + cam_t + 6.0).translate((0.0, 0.0, -cam_t - 3.0))
    )


def _nut(body_d):
    """Mounting nut behind the panel: hex on a round clearance bore."""
    af = nut_af(body_d)
    return (
        cq.Workplane("XY").polygon(6, af / 0.866).extrude(-NUT_H)
        .edges("<Z").chamfer(0.7)
        .cut(cq.Workplane("XY").circle(body_d / 2.0 + 0.15).extrude(-NUT_H - 4.0)
             .translate((0.0, 0.0, 1.0)))
    )


def _cam_screw(cam_t, seat):
    """M6 cam screw: hex head under the cam, shank up into the housing seat.
    Local frame: head top face at z=0, so it seats against the cam's back."""
    head = (
        cq.Workplane("XY").polygon(6, SCREW_AF / 0.866).extrude(-SCREW_HEAD_H)
        .edges("<Z").chamfer(0.5)
    )
    shank = cq.Workplane("XY").circle(SCREW_D / 2.0).extrude(
        cam_t + CAM_JOINT + seat - 0.5)
    return head.union(shank)


def build(head_d, head_h, body_d, afl, body_l, grip, cam_l, cam_w, cam_t,
          tip_flat, slotted):
    housing_l = housing_length(body_l, cam_t)
    rise = cam_offset(body_l, cam_t, grip)
    r_hub = cam_hub_r(body_d, cam_w)
    z_hub = -(housing_l + CAM_JOINT)            # cam hub top = housing end - joint
    z_cam_back = z_hub - cam_t                  # = -body_l + SCREW_HEAD_H
    seat = min(10.0, 0.55 * housing_l)

    result = cq.Assembly(name="quarter_turn_cam_latch")
    result.add(_housing(head_d, head_h, body_d, afl, housing_l, slotted),
               name="housing")
    result.add(_nut(body_d), name="mounting_nut",
               loc=cq.Location((0.0, 0.0, -(WASHER_T + PANEL_T))))
    result.add(_cam(cam_l, cam_w, cam_t, tip_flat, rise, r_hub, body_d), name="cam",
               loc=cq.Location((0.0, 0.0, z_hub)))
    result.add(_cam_screw(cam_t, seat), name="cam_screw",
               loc=cq.Location((0.0, 0.0, z_cam_back)))
    return result
