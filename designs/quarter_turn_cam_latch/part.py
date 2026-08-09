"""quarter_turn_cam_latch — the parametric part (assembly).

A quarter-turn cam latch (Southco E5 class), built as the mechanism it is
rather than as a stack of solids. The double-D body is keyed to the panel
cutout and CANNOT rotate; the tool recess obviously must. So the latch is an
actuator turning inside a fixed housing — Southco's own patent for this
family (US 6,527,308) puts it as "a first body rotatably mounted within a
second body, and a cam mounted to the first body":

  housing         fixed. Ø28 head flange bearing on the panel through the
                  sealing washer, double-D barrel (circle Ø + across-flats)
                  dropping through the cutout, M22x1.5 for the mounting nut,
                  and the bore the actuator runs in
  plug            rotates. Its face is the Ø18 disc seated in the flange —
                  the inner circle every head-style icon on p.154 shows —
                  carrying the tool recess, with its shaft running down the
                  bore to a square drive under the housing
  spring          annular compression coil between the plug's face and a
                  shoulder in the bore. This is what the catalog means by
                  "spring-loaded bodies for better grip tolerance and
                  vibration resistance": it pulls the cam up against the
                  frame, so one part number covers a grip band
  o_ring          seals the plug to the bore, above the spring (the sheet's
                  detail bubble names both)
  sealing_washer  the sheet's 0.5 compressed washer, under the flange
  mounting_nut    behind the panel, clamping it against the flange
  cam             the one-sided formed arm, turned by the plug's square drive
  cam_screw       holds the cam on and preloads the spring

Datum and stack, read off the E5 section at 5.4222 px/mm (NOTES.md):

    z = 0            flange underside — what both catalog depths run from
    0 .. -0.5        compressed sealing washer
    -0.5 .. -1.5     the thinnest catalog panel
    -1.5 .. -5.7     mounting nut
    -grip            the cam's clamping face
    -body_l          the back of the cam screw's head

`body_l` is the catalog depth behind the head (27.2 / 45.5 / 58.2 / 68.2) and
covers housing + cam + screw head, so the stack ends exactly on it. The cam's
Z-step is what is left: `rise = body_l - cam_t - screw head - grip`.

The cam is built the way it is made — a constant-thickness formed part, the
Z-shaped side profile intersected with the plan footprint — so no combination
of parameters can turn its step into a solid block.

Interface + examples: docs/DESIGN_SPEC.md
"""

import math

import cadquery as cq

# ── stack constants, all off the E5 section (p.154) ──────────────────────────
WASHER_T = 0.5        # compressed sealing washer (sheet: "0.5 (.02)")
PANEL_T = 1.0         # thinnest catalog panel (sheet: "1 (.04)")
NUT_H = 4.2           # mounting nut height, scaled (4.05-4.24)
CAM_JOINT = 0.2       # parting gap, housing end to cam hub
STEP_CLEAR = 0.6      # cam-to-housing-barrel clearance at the step foot
STEP_MAX_SLOPE = 1.732  # steepest formed offset leg, tan(60 deg) — proportion
PLUG_RATIO = 0.646    # plug face Ø18.1 in the Ø28 flange, off the top view
FIT = 0.3             # running clearance, plug to housing
MIN_GRIP = WASHER_T + PANEL_T + NUT_H + 1.0


# ── derived sizes, shared with spec.check() ──────────────────────────────────
def screw_d(body_d):
    """Cam screw: M6 on the standard body, M4 on the mini (issue #32, p.158)."""
    return 6.0 if body_d >= 19.0 else 4.0


def screw_head(body_d):
    """(across-flats, height). The section's 13.1 silhouette is an ISO 4017 M6
    hex seen across corners; its height scales to 5.0, i.e. washer-faced."""
    return (10.0, 5.0) if body_d >= 19.0 else (7.0, 3.5)


def nut_af(body_d):
    """Mounting-nut across-flats. The section's nut silhouette measures 28.59
    with its two inner lines at +-0.497 of the half-width — a hex cut across
    CORNERS, so A/F = 28.59 * 0.866 = 24.76 = body_d + 2.26 at Ø22.5. Read the
    other way the corners would stand 5.1 proud of the Ø28 head; the section
    shows 0.3. A slim panel nut on the M22x1.5 body, not a structural one."""
    return body_d + 2.3


def plug_face_d(head_d, body_d):
    """The rotating face seated in the flange — Ø18.1 in the Ø28 head. It also
    has to land on the barrel's top face, so it cannot outgrow the barrel: at
    Ø22.5 body / Ø28 head the catalog ratio governs and gives 18.1."""
    return min(PLUG_RATIO * head_d, body_d - 3.0)


def plug_shaft_d(body_d):
    """Actuator shaft: enough wall around the cam screw to be tappable."""
    return screw_d(body_d) + 3.6


def housing_bore_d(body_d, afl):
    """The bore the plug runs in. Wide enough for the spring annulus, but it
    has to leave a barrel wall at the flats, which is the binding side."""
    return min(plug_shaft_d(body_d) + 5.0, afl - 3.0)


def housing_length(body_l, cam_t, body_d):
    """Housing behind the flange underside. `body_l` is the catalog depth and
    covers housing + cam + screw head, so the housing gets what is left."""
    return body_l - cam_t - CAM_JOINT - screw_head(body_d)[1]


def cam_offset(body_l, cam_t, grip, body_d):
    """The cam's Z-step: hub plane to clamping plane (the sheet's 5.44)."""
    return housing_length(body_l, cam_t, body_d) + CAM_JOINT - grip


def cam_hub_r(body_d, cam_w):
    """Cam hub radius — covers the housing end, and always wider than the
    blade so the neck is a real taper."""
    return max(0.5 * body_d + 1.5, 0.55 * cam_w + 1.0)


def cam_neck(cam_l, cam_w, tip_flat, r_hub):
    """The concave neck: an arc tangent to the hub circle and to the blade
    flank, so the blade grows out of the hub the way the sheet's top view
    shows it — the taper is still narrowing outside the Ø28 head.

    Returns (radius, x of the flank tangency), capped so the tangency lands
    inboard of BOTH the tip's corner rounds and the step: letting it coincide
    with the step put a 4.5 micron edge in the cam."""
    half, r_tip = 0.5 * cam_w, 0.22 * cam_w
    cx_max = min(0.55 * (cam_l - r_tip), 0.8 * (cam_l - tip_flat))
    r_max = (cx_max ** 2 / (r_hub - half) - r_hub - half) / 2.0
    r_neck = max(0.3 * cam_w, min(2.9 * cam_w, r_max))
    return r_neck, math.sqrt((r_hub + r_neck) ** 2 - (half + r_neck) ** 2)


def cam_step_run(cam_l, tip_flat, body_d):
    """Horizontal room the Z-step has: it may only leave the hub plane once it
    is clear of the housing barrel, and it must be at tip level by the time
    the flat begins. Everything inboard stays under the housing end, which is
    what keeps the cam clear of the barrel through the whole quarter turn."""
    return (cam_l - tip_flat) - (0.5 * body_d + STEP_CLEAR)


def drive_af(body_d):
    """Square drive between the plug and the cam — what transmits the turn."""
    return 0.62 * plug_shaft_d(body_d)


def cavity_depth(housing_l):
    """Depth of the wide part of the bore — the spring and O-ring live here."""
    return min(0.55 * housing_l, 12.0)


def spring_geom(body_d, afl, housing_l):
    """(mean radius, wire radius, top z, free length) of the internal coil."""
    bore, shaft = housing_bore_d(body_d, afl), plug_shaft_d(body_d)
    r_mean = (bore + shaft) / 4.0
    r_wire = 0.34 * (bore - shaft) / 2.0
    top = -(1.4 + 2.0 * o_ring_tube(body_d, afl))
    # the swept coil overhangs its nominal helix by the wire radius at each
    # end, so take that off or it fouls the O-ring above and the bore
    # shoulder below
    length = max(2.0, (cavity_depth(housing_l) - 0.6) + top - 2.0 * r_wire)
    return r_mean, r_wire, top, length


def o_ring_tube(body_d, afl):
    """Section radius of the compressed seal filling the bore annulus."""
    return 0.95 * (housing_bore_d(body_d, afl) - plug_shaft_d(body_d)) / 4.0


# ── the parts ────────────────────────────────────────────────────────────────
def _housing(head_d, head_h, body_d, afl, housing_l):
    bore = housing_bore_d(body_d, afl)
    flange = (
        cq.Workplane("XY").circle(head_d / 2.0).extrude(head_h)
        .edges(">Z").fillet(min(head_h * 0.45, head_d * 0.12))
    )
    barrel = cq.Workplane("XY").circle(body_d / 2.0).extrude(-housing_l)
    barrel = barrel.intersect(
        cq.Workplane("XY").box(afl, body_d + 4.0, 2.0 * housing_l + 4.0))
    h = flange.union(barrel)
    # counterbore for the plug's face, then the running bore down to the
    # spring shoulder, then the narrow bore the shaft turns in
    h = h.cut(cq.Workplane("XY").circle((plug_face_d(head_d, body_d) + FIT) / 2.0)
              .extrude(head_h + 1.0))
    h = h.cut(cq.Workplane("XY").circle(bore / 2.0)
              .extrude(-cavity_depth(housing_l)))
    h = h.cut(cq.Workplane("XY").circle((plug_shaft_d(body_d) + FIT) / 2.0)
              .extrude(-housing_l - 1.0))
    return h


def _plug(head_d, head_h, body_d, housing_l, cam_t, slotted):
    """Rotating actuator: face disc in the flange, shaft down the bore, square
    drive standing proud of the housing end for the cam. Housing's frame."""
    d_face, d_shaft = plug_face_d(head_d, body_d), plug_shaft_d(body_d)
    drv = drive_af(body_d)
    p = (cq.Workplane("XY").circle(d_face / 2.0).extrude(head_h)
         .union(cq.Workplane("XY").circle(d_shaft / 2.0).extrude(-housing_l))
         # the drive stops flush with the cam's back face, where the screw
         # head seats — any longer and the two would occupy the same space
         .union(cq.Workplane("XY").rect(drv, drv)
                .extrude(-CAM_JOINT - cam_t)
                .translate((0.0, 0.0, -housing_l))))
    if slotted:
        # head style 00: the slot crosses the plug's face, not the flange
        p = p.cut(cq.Workplane("XY")
                  .box(d_face + 2.0, d_face * 0.20, head_h * 0.55)
                  .translate((0.0, 0.0, head_h)))
    # tapped hole for the cam screw, up from the drive end
    return p.cut(cq.Workplane("XY").circle(screw_d(body_d) / 2.0)
                 .extrude(cam_t + CAM_JOINT + 10.0)
                 .translate((0.0, 0.0, -housing_l - CAM_JOINT - cam_t)))


def _spring(body_d, afl, housing_l):
    """Annular compression coil in the bore, under the plug's face."""
    r_mean, r_wire, top, length = spring_geom(body_d, afl, housing_l)
    pitch = max(3.0 * r_wire, length / 4.0)
    path = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, length, r_mean))
    coil = (cq.Workplane("XZ").center(r_mean, 0).circle(r_wire)
            .sweep(path, isFrenet=True))
    return coil.translate((0.0, 0.0, top - r_wire - length))


def _o_ring(body_d, afl):
    """Compressed seal filling the annulus at the top of the bore."""
    bore, shaft = housing_bore_d(body_d, afl), plug_shaft_d(body_d)
    r_tube = o_ring_tube(body_d, afl)
    # moveTo, not center: center() shifts the workplane origin, which would
    # put the revolve axis through the section and fail the operation
    return (cq.Workplane("XZ").moveTo((bore + shaft) / 4.0, -(0.9 + r_tube))
            .circle(r_tube).revolve(360.0, (0, 0, 0), (0, 1, 0)))


def _washer(head_d, body_d):
    """The sheet's 0.5 compressed sealing washer: its own part, between the
    flange underside and the panel."""
    return (
        cq.Workplane("XY").circle(head_d / 2.0 - 0.4).extrude(-WASHER_T)
        .cut(cq.Workplane("XY").circle(body_d / 2.0 + 0.25)
             .extrude(-WASHER_T - 2.0).translate((0.0, 0.0, 1.0)))
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


def _cam(cam_l, cam_w, cam_t, tip_flat, rise, r_hub, body_d):
    """One-sided formed cam, local frame: axis at origin, hub plate top at
    z=0, blade along +X, tip at x = cam_l, clamping face `rise` above the hub.

    (Z-shaped side profile) ∩ (plan footprint) — a constant-thickness formed
    part, which is what keeps the step from ever becoming a block.
    """
    half = cam_w / 2.0
    r_tip = 0.22 * cam_w

    r_neck, cx = cam_neck(cam_l, cam_w, tip_flat, r_hub)
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

    x_step = cam_l - tip_flat                       # the sheet's 23 starts here
    run = max(0.5, min(1.6 * rise + cam_t, cam_step_run(cam_l, tip_flat, body_d)))
    x_foot = x_step - run
    x_lo, x_hi = -(r_hub + 1.0), cam_l + 1.0
    # the back face is offset PERPENDICULAR to each segment, not vertically: a
    # vertical offset would thin the sloped leg to cam_t*cos(angle) and the
    # part would stop being the constant-thickness section cam_t is declared as
    leg = math.hypot(run, rise)
    back = cam_t * (leg - run) / rise
    side = (
        cq.Workplane("XZ")
        .moveTo(x_lo, 0.0)
        .lineTo(x_foot, 0.0).lineTo(x_step, rise).lineTo(x_hi, rise)
        .lineTo(x_hi, rise - cam_t).lineTo(x_step + back, rise - cam_t)
        .lineTo(x_foot + back, -cam_t).lineTo(x_lo, -cam_t)
        .close()
        .extrude(cam_w + 4.0)
        .translate((0.0, half + 2.0, 0.0))
    )
    cam = plan.intersect(side)
    # square drive hole — this is what actually turns the cam
    drv = drive_af(body_d) + 0.25
    return cam.cut(cq.Workplane("XY").rect(drv, drv)
                   .extrude(rise + cam_t + 6.0)
                   .translate((0.0, 0.0, -cam_t - 3.0)))


def _cam_screw(body_d, cam_t):
    """Holds the cam on the plug's drive and preloads the spring. Local frame:
    head top face at z=0, so it seats against the cam's back."""
    af, hh = screw_head(body_d)
    return (cq.Workplane("XY").polygon(6, af / 0.866).extrude(-hh)
            .edges("<Z").chamfer(0.4)
            .union(cq.Workplane("XY").circle(screw_d(body_d) / 2.0 - 0.15)
                   .extrude(cam_t + CAM_JOINT + 6.0)))


def build(head_d, head_h, body_d, afl, body_l, grip, cam_l, cam_w, cam_t,
          tip_flat, slotted):
    housing_l = housing_length(body_l, cam_t, body_d)
    rise = cam_offset(body_l, cam_t, grip, body_d)
    r_hub = cam_hub_r(body_d, cam_w)
    z_hub = -(housing_l + CAM_JOINT)            # cam hub top = housing end - joint
    z_cam_back = z_hub - cam_t                  # = -body_l + screw head

    result = cq.Assembly(name="quarter_turn_cam_latch")
    result.add(_housing(head_d, head_h, body_d, afl, housing_l), name="housing")
    result.add(_plug(head_d, head_h, body_d, housing_l, cam_t, slotted), name="plug")
    result.add(_spring(body_d, afl, housing_l), name="spring")
    result.add(_o_ring(body_d, afl), name="o_ring")
    result.add(_washer(head_d, body_d), name="sealing_washer")
    result.add(_nut(body_d), name="mounting_nut",
          loc=cq.Location((0.0, 0.0, -(WASHER_T + PANEL_T))))
    result.add(_cam(cam_l, cam_w, cam_t, tip_flat, rise, r_hub, body_d), name="cam",
          loc=cq.Location((0.0, 0.0, z_hub)))
    result.add(_cam_screw(body_d, cam_t), name="cam_screw",
          loc=cq.Location((0.0, 0.0, z_cam_back)))
    return result
