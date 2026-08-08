"""snatch_block_single_sheave — Crosby McKissick single-sheave snatch block.

A rigging block is a load path, and this family is modelled as one. Reading the
McKissick *Snatch Blocks* manual's disassembly order backwards gives the chain,
and every joint in it is a real bore-and-pin pair here:

    shackle bow -> shackle bolt -> swivel tee -> SWIVEL -> swivel case
                -> hook bolt -> BOTH side plates -> centre pin
                -> bushing -> sheave -> wire rope

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

Opening the block (manual, p.12): pull the hitch pin, unscrew the hook bolt, and
the near plate rotates on the centre pin and swings clear. `open_angle` models
that state, and the bolt withdraws from the swing plate whenever it is open --
the plate cannot turn while the bolt is through it.

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
_HEX = 1.55                      # nut across flats / shank diameter
_RACE_BB = 0.12                  # bronze bushing wall / centre pin diameter
_RACE_RB = 0.22                  # roller race radial depth / centre pin diameter


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
    """Plain race on the Y axis -- the bronze bushing or the roller race."""
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


def _bolt_y(shank_r, y0, y1, z):
    """Headed bolt on the Y axis, shank spanning y0..y1 (y0 < y1): a round head
    standing proud beyond y1 and a hex nut beyond y0.

    Both the centre pin and the hook bolt are built this way -- the manual calls
    one a pin with a nut and the other a bolt with a round staked retention nut,
    and both are headed one end and nutted the other.  Workplane("XZ") extrudes
    toward -Y, so each piece is placed by its HIGH-Y face.
    """
    head_t = 0.8 * shank_r
    shank = (
        cq.Workplane("XZ").circle(shank_r).extrude(y1 - y0)
        .translate((0.0, y1, z))
    )
    head = (
        cq.Workplane("XZ").circle(1.6 * shank_r).extrude(head_t)
        .translate((0.0, y0, z))
    )
    nut = (
        cq.Workplane("XZ").polygon(6, 2.0 * _HEX * shank_r / math.sqrt(3.0))
        .extrude(head_t)
        .translate((0.0, y1 + head_t, z))
    )
    return shank.union(head).union(nut)


def _shackle_bow(inside_w, bar_r, bolt_r, ear_r, crown_z):
    """Anchor shackle bow: a semicircular crown closed by two straight legs that
    thicken into the ears the bolt runs through. The bolt axis is the local
    origin; `crown_z` is where the bar centreline circle sits below it, so the
    published G (inside width) and the D/E stack both fall out.

    Revolving the bar section about Y traces the centreline as a circle in XZ --
    the bow plane -- so the bow needs no rotation. The lower half is kept by
    intersecting a half-space; the legs start a bar radius above the torus
    centreline so they bury into it instead of meeting at a tangent knife edge.
    """
    major_r = inside_w / 2.0 + bar_r
    box = 4.0 * (major_r + bar_r)
    # makeTorus, not a revolved section: revolve wants a pending wire, so the
    # section needs .close(), but a section that already closes on itself gets a
    # zero-length edge from .close() and the revolve comes back empty.
    torus = cq.Workplane("XY").newObject(
        [cq.Solid.makeTorus(major_r, bar_r, cq.Vector(0.0, 0.0, 0.0),
                            cq.Vector(0.0, 1.0, 0.0))]
    )
    lower = cq.Workplane("XY").box(box, box, box).translate((0.0, 0.0, -box / 2.0))
    result = torus.intersect(lower).translate((0.0, 0.0, crown_z))
    leg = -crown_z + bar_r
    ear_w = 2.0 * bar_r
    for side in (-1.0, 1.0):
        result = result.union(
            _disc_z(bar_r, crown_z - bar_r, leg).translate((side * major_r, 0.0, 0.0))
        )
        # Workplane("YZ") extrudes toward +X, so shift by half the ear to centre
        # it on the leg -- the ear is the boss the bolt runs through.
        result = result.union(
            cq.Workplane("YZ").circle(ear_r).extrude(ear_w)
            .translate((side * major_r - 0.5 * ear_w, 0.0, 0.0))
        )
    return result.cut(_bore_x(bolt_r, 0.0, 3.0 * box))


def build(sheave_d, rope_d, head_w_B, cheek_w_C, pin_to_throat_D, bar_thk_E,
          bow_width_G, bow_height_H, open_angle, swivel_angle, roller_bearing=0):
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
    race_t = max(2.0, (_RACE_RB if roller_bearing else _RACE_BB) * 2.0 * pin_r)
    bore_r = pin_r + race_t                      # sheave bore

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
    bushing = _sleeve(bore_r - _FIT, pin_r + _FIT, sheave_w)
    centre_pin = _bolt_y(pin_r, -0.5 * cheek_w_C, 0.5 * cheek_w_C, 0.0)

    # ---- the fitting-end joint: bolt -> case -> swivel -> tee ------------
    # Unscrewing the hook bolt is step 2 of the manual's disassembly: the plate
    # cannot rotate while the bolt is through it, so an open block has the bolt
    # backed out of the swing plate (which is the +Y one, and carries the nut).
    withdraw = 0.0 if open_angle <= 0.0 else plate_t + 2.0
    hook_bolt = _bolt_y(bolt_r, -0.5 * cheek_w_C - withdraw,
                        0.5 * cheek_w_C - withdraw, z_bolt)

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
    bar_len = bow_width_G - 2.0 * _FIT
    tee = (
        cq.Workplane("YZ").circle(tee_r).extrude(bar_len)
        .translate((-0.5 * bar_len, 0.0, z_sb))
    )
    tee = tee.union(_disc_z(stem_r, z_sb, (cb_floor + _SWIVEL_CLR) - z_sb))
    tee = tee.union(_disc_z(head_r_stem, cb_floor + _SWIVEL_CLR, head_t))
    tee = tee.cut(_bore_x(sb_r + _FIT, z_sb, 4.0 * bow_width_G))

    # ---- shackle ---------------------------------------------------------
    crown_z = 0.5 * bow_width_G - bow_height_H - sb_r
    bow = _shackle_bow(bow_width_G, bar_r, sb_r + _FIT, ear_r, crown_z).translate(
        (0.0, 0.0, z_sb))
    span = bow_width_G + 2.0 * bar_thk_E
    shackle_bolt = (
        cq.Workplane("YZ").circle(sb_r).extrude(span)
        .translate((-0.5 * span, 0.0, z_sb))
        .union(cq.Workplane("YZ").polygon(6, 2.0 * _HEX * sb_r / math.sqrt(3.0))
               .extrude(0.8 * sb_r).translate((0.5 * span, 0.0, z_sb)))
        .union(cq.Workplane("YZ").circle(1.6 * sb_r).extrude(0.8 * sb_r)
               .translate((-0.5 * span - 0.8 * sb_r, 0.0, z_sb)))
    )

    # the swivel is the whole point of the fitting: everything below the case
    # turns about Z together, and nothing above it moves.
    def _turn(shape):
        return shape.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), swivel_angle)

    result = cq.Assembly(name="snatch_block_single_sheave")
    result.add(fixed, name="side_plate_01")
    result.add(swing, name="side_plate_02")
    result.add(sheave, name="sheave")
    result.add(bushing, name="bushing")
    result.add(centre_pin, name="centre_pin")
    result.add(hook_bolt, name="hook_bolt")
    result.add(case, name="swivel_case")
    result.add(_turn(tee), name="swivel_tee")
    result.add(_turn(bow), name="shackle_bow")
    result.add(_turn(shackle_bolt), name="shackle_bolt")
    return result
