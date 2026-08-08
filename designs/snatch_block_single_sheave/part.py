"""snatch_block_single_sheave — Crosby McKissick single-sheave snatch block.

A rigging block is a load path, and this family is modelled as one. Reading the
McKissick *Snatch Blocks* manual's disassembly order backwards gives the chain,
and every joint in it is a real bore-and-pin pair here:

    shackle bow -> shackle bolt -> swivel tee -> SWIVEL -> swivel case
                -> hook bolt -> BOTH side plates -> centre pin
                -> bushing or rollers -> sheave -> wire rope

The two members that make that chain close are the ones a block cannot be built
without, and they are what an earlier revision of this family left out:

  * the **hook bolt** (the manual's "upper bolt") runs side plate -> case ->
    side plate. It is the only thing holding the two plates apart at the fitting
    end and the only thing carrying the fitting's load into them. Its head bears
    on one plate, a round staked retention nut on the other, and a hairpin
    through the end stops the nut backing off.
  * the **swivel case** (Crosby's "yoke") is the lug the bolt passes through. Its
    underside is counterbored, and the tee's headed stem stands in that
    counterbore -- that is the swivel, and it is why the shackle can turn 360
    deg under the block without the rope winding it up.

Without those two the shackle assembly is not attached to anything: it hangs in
free space below the plates. That is exactly what the previous revision did.

The **swivel tee** is a tee because it is one: a cross barrel pierced by the
shackle bolt, with a vertical stem rising out of it into the case. Crosby sells
it as "Tee and Yoke Assembly"; the hook version of the block replaces the tee
with the hook's own shank in the same case.

Both bolts are retained the way the manual insists on: a **hitch pin** (hairpin)
through the hook bolt past its nut, and a **cotter** through the shackle bolt.
The bearing is the catalogue's own choice: a bronze bushing, or a full
complement of straight rollers running directly on the centre pin.

Opening the block (manual, p.12): pull the hitch pin, unscrew the hook bolt, and
the near plate rotates on the centre pin and swings clear. `open_angle` models
that state, and the bolt (with its hitch pin) withdraws from the swing plate
whenever it is open -- the plate cannot turn while the bolt is through it.

Frame: the sheave axis is Y, the block hangs down -Z, the plates lie in XZ, and
the centre pin is the origin because every catalogue dimension is anchored
there. See NOTES.md for the symbol map, the A = B/2 + D + E identity, and the
basis of every proportion the catalogue does not publish.
"""

import cadquery as cq
import math

# Wire-rope sheave practice: the groove bottom is an arc a little larger than
# the rope so it beds without pinching, and deep enough to hold the rope in.
_GROOVE_R_FACTOR = 0.53          # groove bottom radius / rope diameter
_GROOVE_DEPTH_FACTOR = 1.5       # groove depth / rope diameter
_FLANK_ANGLE = 20.0              # deg, groove flank flare off radial

# Proportions the catalogue does not publish (all documented in NOTES.md).
_PLATE_T = 0.10                  # plate thickness / cheek width C
_SIDE_CLR = 2.0                  # mm running clearance each side of the sheave
_FIT = 0.5                       # mm radial clearance, every pin-in-bore joint
_SWIVEL_CLR = 1.0                # mm end float in the swivel -- the manual sets
                                 # fitting-to-case clearance at .031-.062 in
_PIN_TO_CHEEK = 0.30             # centre pin diameter / C
_BOLT_TO_CHEEK = 0.26            # hook bolt diameter / C
_BOSS_TO_BOLT = 0.95             # plate tail boss radius / hook bolt diameter
_EYE_TO_BOLT = 1.05              # swivel case eye radius / hook bolt diameter
_CASE_FOOT = 1.15                # case swivel-boss radius / hook bolt diameter
_CASE_WALL = 0.40                # case bottom wall / hook bolt diameter
_CASE_WEB = 0.35                 # metal between bolt hole and counterbore / d
_STEM_TO_BOLT = 0.85             # tee stem diameter / hook bolt diameter
_HEAD_TO_STEM = 1.35             # stem head diameter / stem diameter
_NECK = 0.35                     # exposed stem length / hook bolt diameter
_PLATE_REACH = 0.36              # hook bolt axis below the centre pin / D
_SHEAVE_GAP = 4.0                # mm the fitting-end parts clear the sheave rim
_BOLT_TO_BAR = 1.13              # shackle bolt diameter / bow bar E
_TEE_TO_BOLT = 0.95              # tee barrel radius / shackle bolt diameter
_EAR_TO_BOLT = 0.72              # shackle ear boss radius / shackle bolt diameter
_EAR_SPAN = 0.73                 # shackle ear inside spacing / bow inside width G
_EAR_W = 1.4                     # shackle ear width along the bolt / bow bar E --
                                 # the ear is upset wider than the bar so the bolt
                                 # head bears on it clear of the flaring leg
_HEAD_R = 1.35                   # bolt head radius / shank radius
_HEX = 1.55                      # nut across flats / shank diameter
_RACE_BB = 0.12                  # bronze bushing wall / centre pin diameter
_ROLLER = 0.22                   # straight roller diameter / centre pin diameter
_ROLL_GAP = 0.6                  # mm between rollers in the full complement
_WIRE = 0.14                     # retaining-wire diameter / its bolt's diameter


def _hull(r_top, z_top, r_bot, z_bot, thick):
    """Closed teardrop hull of two circles on the XZ plane, extruded `thick`.

    Both the side plate and the swivel case are this shape: a big circle at one
    pin and a smaller one at the other, joined by their outer tangents.
    Workplane("XZ") extrudes toward -Y, so the result lands on Y in [-thick, 0].
    """
    span = z_top - z_bot
    cos_a = min(0.999999, (r_top - r_bot) / span)
    sin_a = math.sqrt(max(1e-9, 1.0 - cos_a * cos_a))
    hx, hz = r_top * sin_a, z_top - r_top * cos_a
    tx, tz = r_bot * sin_a, z_bot - r_bot * cos_a
    return (
        cq.Workplane("XZ")
        .moveTo(hx, hz)
        .threePointArc((0.0, z_top + r_top), (-hx, hz))
        .lineTo(-tx, tz)
        .threePointArc((0.0, z_bot - r_bot), (tx, tz))
        .close()
        .extrude(thick)
    )


def _bore_y(radius, z, length):
    """Cutter on the Y axis at height z -- every joint across the cheeks."""
    return (
        cq.Workplane("XZ").circle(radius).extrude(length)
        .translate((0.0, 0.5 * length, z))
    )


def _bore_x(radius, z, length):
    """Cutter on the X axis at height z -- the shackle bolt through the bow."""
    return (
        cq.Workplane("YZ").circle(radius).extrude(length)
        .translate((-0.5 * length, 0.0, z))
    )


def _disc_z(radius, z0, height):
    return cq.Workplane("XY").circle(radius).extrude(height).translate((0.0, 0.0, z0))


def _sheave(outer_r, bore_r, width, rope_d):
    """Grooved sheave as ONE revolve of the full section, so the groove needs no
    boolean: bore, side face, flared flank, arc bottom, flank, side face."""
    groove_r = _GROOVE_R_FACTOR * rope_d
    depth = _GROOVE_DEPTH_FACTOR * rope_d
    tread_r = outer_r - depth
    arc_end_r = tread_r + groove_r - groove_r * math.cos(math.radians(60.0))
    arc_end_y = groove_r * math.sin(math.radians(60.0))
    lip_y = arc_end_y + math.tan(math.radians(_FLANK_ANGLE)) * (outer_r - arc_end_r)
    half = width / 2.0
    return (
        cq.Workplane("XY")
        .moveTo(bore_r, -half)
        .lineTo(outer_r, -half)
        .lineTo(outer_r, -lip_y)
        .lineTo(arc_end_r, -arc_end_y)
        .threePointArc((tread_r, 0.0), (arc_end_r, arc_end_y))
        .lineTo(outer_r, lip_y)
        .lineTo(outer_r, half)
        .lineTo(bore_r, half)
        .close()
        .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    )


def _sleeve(outer_r, inner_r, width):
    """Plain bronze bushing on the Y axis."""
    half = width / 2.0
    return (
        cq.Workplane("XY")
        .moveTo(inner_r, -half)
        .lineTo(outer_r, -half)
        .lineTo(outer_r, half)
        .lineTo(inner_r, half)
        .close()
        .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    )


def _bolt_y(shank_r, y0, y1, z, tail):
    """Headed bolt on the Y axis, shank spanning y0..y1+nut+tail: a round head
    standing proud beyond y0, a hex nut beyond y1, and a plain tail past the nut
    cross-drilled for the hitch pin.

    Both the centre pin and the hook bolt are built this way -- the manual calls
    one a pin with a nut and the other a bolt with a round staked retention nut,
    and both are headed one end and nutted the other.  Workplane("XZ") extrudes
    toward -Y, so each piece is placed by its HIGH-Y face.
    """
    head_t = 0.8 * shank_r
    y_nut = y1 + head_t
    shank = (
        cq.Workplane("XZ").circle(shank_r).extrude(y_nut + tail - y0)
        .translate((0.0, y_nut + tail, z))
    )
    head = (
        cq.Workplane("XZ").circle(_HEAD_R * shank_r).extrude(head_t)
        .translate((0.0, y0, z))
    )
    nut = (
        cq.Workplane("XZ").polygon(6, 4.0 * _HEX * shank_r / math.sqrt(3.0))
        .extrude(head_t)
        .translate((0.0, y_nut, z))
    )
    return shank.union(head).union(nut)


def _hairpin(wire_r, shank_r):
    """Hitch pin (R-clip), built at the origin with its straight leg on Z and
    the bolt it retains on Y: one leg drops through the bolt's cross hole, the
    bend passes over the bolt, and the sprung leg comes back down outside it.

    Swept along a tangent-continuous path (line, semicircle, line), so it is one
    solid with no booleans -- and the swept volume equals pi*r^2*L, which is the
    check that the sweep did not quietly return something else.
    """
    x2 = shank_r + 2.5 * wire_r
    z_bot = -(shank_r + 2.0 * wire_r)
    z_top = shank_r + 2.2 * wire_r
    path = (
        cq.Workplane("XZ").moveTo(0.0, z_bot).lineTo(0.0, z_top)
        .threePointArc((0.5 * x2, z_top + 0.5 * x2), (x2, z_top))
        .lineTo(x2, -0.3 * shank_r)
    )
    return cq.Workplane("XY").workplane(offset=z_bot).circle(wire_r).sweep(path)


def _cotter(wire_r, shank_r):
    """Split pin for the shackle bolt: eye, leg down through the bolt's cross
    hole, and the tail bent clear so it cannot back out.  Same frame as
    `_hairpin` -- leg on Z, the bolt it retains on X."""
    # cq 2.3's makeTorus takes no sweep angle, so the eye is a closed loop --
    # which is what a split pin's eye is anyway.  The leg buries one wire radius
    # into the bottom of the loop instead of crossing its hole.
    eye_r = 1.8 * wire_r
    z_eye = shank_r + 1.6 * wire_r + eye_r
    z_bot = -(shank_r + 2.4 * wire_r)
    eye = cq.Workplane("XY").newObject([
        cq.Solid.makeTorus(eye_r, wire_r, cq.Vector(0.0, 0.0, z_eye),
                           cq.Vector(0.0, 1.0, 0.0))
    ])
    leg = _disc_z(wire_r, z_bot, (z_eye - eye_r + wire_r) - z_bot)
    tilt = math.radians(35.0)
    tail = cq.Workplane("XY").newObject([
        cq.Solid.makeCylinder(
            wire_r, 3.0 * wire_r,
            cq.Vector(0.0, 0.0, z_bot + wire_r),
            cq.Vector(math.sin(tilt), 0.0, -math.cos(tilt)))
    ])
    return eye.union(leg).union(tail)


def _shackle_bow(inside_w, bar_r, bolt_r, ear_r, ear_w, ear_x, crown_c):
    """Anchor shackle bow, swept along its own centreline: the crown is a circle
    of radius G/2 + bar_r, and the legs are its outer TANGENTS running up to the
    ears, which sit closer together than the crown.  That is what makes the bow
    pear-shaped instead of a plain dee -- measured off the catalogue sheet, the
    ears stand at about 0.73 of the crown's inside width.

    The bolt axis is the local origin and `crown_c` is where the bar centreline
    circle sits below it, so the published G and the D/E stack both fall out:
    the crown's outside is `crown_c - R - bar_r` and its inside is
    `crown_c - R + bar_r`, exactly E apart.
    """
    major_r = 0.5 * inside_w + bar_r
    dz = -crown_c
    span = math.hypot(ear_x, dz)
    phi = math.atan2(dz, ear_x) - math.acos(min(0.999999, major_r / span))
    tx, tz = major_r * math.cos(phi), crown_c + major_r * math.sin(phi)
    dx, dzl = tx - ear_x, tz
    n = math.hypot(dx, dzl)
    path = (
        cq.Workplane("XZ").moveTo(-ear_x, 0.0).lineTo(-tx, tz)
        .threePointArc((0.0, crown_c - major_r), (tx, tz))
        .lineTo(ear_x, 0.0)
    )
    plane = cq.Plane(origin=cq.Vector(-ear_x, 0.0, 0.0),
                     xDir=cq.Vector(0.0, 1.0, 0.0),
                     normal=cq.Vector(-dx / n, 0.0, dzl / n))
    result = cq.Workplane(plane).circle(bar_r).sweep(path)
    for side in (-1.0, 1.0):
        # Workplane("YZ") extrudes toward +X, so shift by half the ear to centre
        # it on the leg -- the ear is the boss the bolt runs through.
        result = result.union(
            cq.Workplane("YZ").circle(ear_r).extrude(ear_w)
            .translate((side * ear_x - 0.5 * ear_w, 0.0, 0.0))
        )
    return result.cut(_bore_x(bolt_r, 0.0, 8.0 * major_r))


def build(sheave_d, rope_d, head_w_B, cheek_w_C, pin_to_throat_D, bar_thk_E,
          bow_width_G, bow_height_H, open_angle, swivel_angle, roller_count,
          roller_bearing=0):
    # ---- the two ladders -------------------------------------------------
    # C, E, G, H are constant inside a capacity group, so everything sized by
    # working load limit is scaled off C; everything sized by rope is scaled off
    # the sheave.  The centre pin and the hook bolt are load-sized parts.
    plate_t = _PLATE_T * cheek_w_C
    gap = cheek_w_C - 2.0 * plate_t              # inner face to inner face
    sheave_w = gap - 2.0 * _SIDE_CLR
    pin_r = 0.5 * _PIN_TO_CHEEK * cheek_w_C
    bolt_d = _BOLT_TO_CHEEK * cheek_w_C
    bolt_r = 0.5 * bolt_d
    race_t = max(2.0, (_ROLLER if roller_bearing else _RACE_BB) * 2.0 * pin_r)
    bore_r = pin_r + 2.0 * _FIT + race_t         # sheave bore

    head_r = 0.5 * head_w_B
    tail_r = _BOSS_TO_BOLT * bolt_d
    eye_r = _EYE_TO_BOLT * bolt_d
    foot_r = _CASE_FOOT * bolt_d

    # ---- where the fitting hangs ----------------------------------------
    # The plates reach 0.36 D below the pin (the proportion the catalogue sheet
    # draws), EXCEPT that the tail boss and the swivel case both live beside the
    # sheave, so on the big-sheave rows the sheave rim pushes the whole fitting
    # further down.  That coupling is real: it is why B tracks the sheave while
    # C, E, G, H do not.
    z_bolt = -max(_PLATE_REACH * pin_to_throat_D,
                  0.5 * sheave_d + max(tail_r, eye_r) + _SHEAVE_GAP)

    sb_r = 0.5 * _BOLT_TO_BAR * bar_thk_E        # shackle bolt
    bar_r = 0.5 * bar_thk_E
    ear_r = _EAR_TO_BOLT * 2.0 * sb_r
    ear_w = _EAR_W * bar_thk_E
    ear_x = 0.5 * _EAR_SPAN * bow_width_G + 0.5 * ear_w
    tee_r = _TEE_TO_BOLT * 2.0 * sb_r
    # H is the clear throat under the shackle bolt and D reaches the inside of
    # the crown, so the bolt axis is H + one bolt radius above the throat.
    z_sb = -pin_to_throat_D + bow_height_H + sb_r

    neck = _NECK * bolt_d
    z_foot = z_sb + tee_r + neck + foot_r        # centre of the case's foot arc
    z_case_bot = z_foot - foot_r                 # case underside
    stem_r = 0.5 * _STEM_TO_BOLT * bolt_d
    head_r_stem = _HEAD_TO_STEM * stem_r
    head_t = stem_r

    # ---- side plates -----------------------------------------------------
    def _plate():
        p = _hull(head_r, 0.0, tail_r, z_bolt, plate_t)
        p = p.cut(_bore_y(pin_r + _FIT, 0.0, 6.0 * plate_t))
        return p.cut(_bore_y(bolt_r + _FIT, z_bolt, 6.0 * plate_t))

    y_in = 0.5 * gap                             # inner faces at +/- y_in
    fixed = _plate().translate((0.0, -y_in, 0.0))
    swing = (
        _plate().translate((0.0, y_in + plate_t, 0.0))
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), open_angle)
    )

    # ---- sheave train ----------------------------------------------------
    sheave = _sheave(0.5 * sheave_d, bore_r, sheave_w, rope_d)
    # The centre pin is retained by a prevailing-torque lock nut and a roll pin
    # driven into it (manual p.12), not by a visible clip -- so it gets no tail.
    centre_pin = _bolt_y(pin_r, -0.5 * cheek_w_C, 0.5 * cheek_w_C, 0.0, 0.0)

    # bearing: a bronze bushing, or a full complement of straight rollers
    # running directly on the pin.  Same component either way, so the body count
    # follows `roller_count` -- 1 sleeve, or N rollers.
    if roller_bearing:
        pitch_r = pin_r + _FIT + 0.5 * race_t
        elements = [
            _disc_z(0.5 * race_t - 0.05, 0.0, sheave_w - 2.0)
            .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
            .translate((pitch_r * math.cos(2.0 * math.pi * k / roller_count),
                        0.5 * (sheave_w - 2.0),
                        pitch_r * math.sin(2.0 * math.pi * k / roller_count)))
            for k in range(int(roller_count))
        ]
    else:
        elements = [_sleeve(bore_r - _FIT, pin_r + _FIT, sheave_w)]

    # ---- the fitting-end joint: bolt -> case -> swivel -> tee ------------
    # Unscrewing the hook bolt is step 2 of the manual's disassembly: the plate
    # cannot rotate while the bolt is through it, so an open block has the bolt
    # backed out of the swing plate (which is the +Y one, and carries the nut).
    withdraw = 0.0 if open_angle <= 0.0 else plate_t + 2.0
    bolt_wire = _WIRE * bolt_d
    nut_len = 0.9 * bolt_r
    y_face = 0.5 * cheek_w_C                     # the plates' outer faces
    hitch_y = y_face + nut_len + 2.6 * bolt_wire
    hook_bolt = (
        cq.Workplane("XZ").circle(bolt_r).extrude(2.0 * y_face + nut_len
                                                  + 4.0 * bolt_wire)
        .translate((0.0, y_face + nut_len + 4.0 * bolt_wire, z_bolt))
        .union(cq.Workplane("XZ").circle(_HEAD_R * bolt_r).extrude(0.8 * bolt_r)
               .translate((0.0, -y_face, z_bolt)))
    )
    hook_bolt = hook_bolt.cut(
        _disc_z(bolt_wire + 0.3, z_bolt - 4.0 * bolt_r, 8.0 * bolt_r)
        .translate((0.0, hitch_y, 0.0)))
    hitch_pin = _hairpin(bolt_wire, bolt_r).translate((0.0, hitch_y, z_bolt))
    hook_bolt = hook_bolt.translate((0.0, -withdraw, 0.0))
    hitch_pin = hitch_pin.translate((0.0, -withdraw, 0.0))
    # the round retention nut lives in the swing plate and turns with it
    retention_nut = (
        cq.Workplane("XZ").circle(2.4 * bolt_r).extrude(nut_len)
        .translate((0.0, y_face + nut_len, z_bolt))
        .cut(_bore_y(bolt_r + 0.3, z_bolt, 4.0 * (y_face + nut_len)))
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), open_angle)
    )

    case_t = gap - 2.0 * _FIT
    case = _hull(eye_r, z_bolt, foot_r, z_foot, case_t).translate(
        (0.0, 0.5 * case_t, 0.0))
    case = case.cut(_bore_y(bolt_r + _FIT, z_bolt, 4.0 * case_t))
    cb_floor = z_case_bot + _CASE_WALL * bolt_d
    cb_top = z_bolt - bolt_r - _CASE_WEB * bolt_d
    case = case.cut(_disc_z(head_r_stem + _FIT, cb_floor, cb_top - cb_floor))
    case = case.cut(_disc_z(stem_r + _FIT, z_case_bot - 1.0,
                            cb_floor - z_case_bot + 1.0))

    # the tee: cross barrel on the shackle bolt, stem up into the counterbore,
    # head standing on the counterbore floor -- the head is what the load pulls
    # against, so the tee cannot leave the case.
    bar_len = 2.0 * (ear_x - 0.5 * ear_w) - 2.0 * _FIT
    tee = (
        cq.Workplane("YZ").circle(tee_r).extrude(bar_len)
        .translate((-0.5 * bar_len, 0.0, z_sb))
    )
    tee = tee.union(_disc_z(stem_r, z_sb, (cb_floor + _SWIVEL_CLR) - z_sb))
    tee = tee.union(_disc_z(head_r_stem, cb_floor + _SWIVEL_CLR, head_t))
    tee = tee.cut(_bore_x(sb_r + _FIT, z_sb, 8.0 * ear_x))

    # ---- shackle ---------------------------------------------------------
    crown_z = 0.5 * bow_width_G - bow_height_H - sb_r
    bow = _shackle_bow(bow_width_G, bar_r, sb_r + _FIT, ear_r, ear_w, ear_x,
                       crown_z).translate((0.0, 0.0, z_sb))
    sb_wire = _WIRE * 2.0 * sb_r
    x_nut = ear_x + 0.5 * ear_w                  # the ears' outer faces
    # the cotter's eye stands clear of the nut it is locking, or the two foul
    cot_x = x_nut + 0.8 * sb_r + 3.4 * sb_wire
    shackle_bolt = (
        cq.Workplane("YZ").circle(sb_r).extrude(x_nut + cot_x + 1.8 * sb_wire)
        .translate((-x_nut, 0.0, z_sb))
        .union(cq.Workplane("YZ").polygon(6, 4.0 * _HEX * sb_r / math.sqrt(3.0))
               .extrude(0.8 * sb_r).translate((x_nut, 0.0, z_sb)))
        .union(cq.Workplane("YZ").circle(_HEAD_R * sb_r).extrude(0.8 * sb_r)
               .translate((-x_nut - 0.8 * sb_r, 0.0, z_sb)))
    )
    shackle_bolt = shackle_bolt.cut(
        _disc_z(sb_wire + 0.3, z_sb - 4.0 * sb_r, 8.0 * sb_r)
        .translate((cot_x, 0.0, 0.0)))
    shackle_cotter = _cotter(sb_wire, sb_r).translate((cot_x, 0.0, z_sb))

    # the swivel is the whole point of the fitting: everything below the case
    # turns about Z together, and nothing above it moves.
    def _turn(shape):
        return shape.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), swivel_angle)

    result = cq.Assembly(name="snatch_block_single_sheave")
    result.add(fixed, name="side_plate_01")
    result.add(swing, name="side_plate_02")
    result.add(sheave, name="sheave")
    result.add(centre_pin, name="centre_pin")
    result.add(hook_bolt, name="hook_bolt")
    result.add(retention_nut, name="retention_nut")
    result.add(hitch_pin, name="hitch_pin")
    result.add(case, name="swivel_case")
    result.add(_turn(tee), name="swivel_tee")
    result.add(_turn(bow), name="shackle_bow")
    result.add(_turn(shackle_bolt), name="shackle_bolt")
    result.add(_turn(shackle_cotter), name="shackle_cotter")
    for k, element in enumerate(elements):
        result.add(element, name="bearing_element_%02d" % (k + 1))
    return result
