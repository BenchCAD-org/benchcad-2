"""snatch_block_single_sheave — Crosby McKissick single-sheave snatch block.

A rigging block whose near side plate swings open about the centre pin so a wire
rope can be dropped over the sheave without reeving an end through. Eight
bodies: two side plates (one fixed, one swinging), the grooved sheave, its
bushing, the centre pin, the swivel yoke, and the shackle bow with its pin.

Frame: the sheave axis is Y, the block hangs down -Z, the plates lie in XZ. The
centre pin is the origin because the catalogue anchors its dimensions there —
see NOTES.md for the symbol map and the A = B/2 + D + E identity that ties the
published overall height to the rest of the table.
"""

import cadquery as cq
import math

# Wire-rope sheave practice: the groove bottom is an arc a little larger than
# the rope so it beds without pinching, and deep enough to hold the rope in the
# sheave. Shop rules, not catalogue values.
_GROOVE_R_FACTOR = 0.53          # groove bottom radius / rope diameter
_GROOVE_DEPTH_FACTOR = 1.5       # groove depth / rope diameter
_FLANK_ANGLE = 20.0              # deg, groove flank flare off radial

# Proportions the catalogue does not publish (all documented in NOTES.md).
_PLATE_T = 0.10                  # plate thickness / cheek width C
_SIDE_CLR = 2.0                  # mm running clearance each side of the sheave
_TAIL_R = 0.16                   # plate tail radius / head width B
_YOKE_LEN = 1.8                  # yoke length / bow height H — set so the plate
                                 # takes ~60% of the overall height A, the
                                 # proportion the catalogue drawing shows
_PIN_HEAD = 1.6                  # pin head diameter / pin shank diameter


def _plate(head_r, tail_r, tail_z, thick, bore_r):
    """One side plate: the teardrop hull of the head circle at the pin and the
    tail circle at the yoke, bored for the centre pin."""
    span = abs(tail_z)
    cos_a = (head_r - tail_r) / span
    sin_a = math.sqrt(max(1e-9, 1.0 - cos_a * cos_a))
    hx, hz = head_r * sin_a, -head_r * cos_a
    tx, tz = tail_r * sin_a, tail_z - tail_r * cos_a
    outline = (
        cq.Workplane("XZ")
        .moveTo(hx, hz)
        .threePointArc((0.0, head_r), (-hx, hz))
        .lineTo(-tx, tz)
        .threePointArc((0.0, tail_z - tail_r), (tx, tz))
        .close()
    )
    # Workplane("XZ") extrudes toward -Y, so the plate lands on Y in [-thick, 0].
    return outline.extrude(thick).faces(">Y").workplane().circle(bore_r).cutThruAll()


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


def _tube(outer_r, inner_r, length):
    """Plain sleeve on the Y axis — the sheave bushing."""
    half = length / 2.0
    return (
        cq.Workplane("XY")
        .moveTo(inner_r, -half)
        .lineTo(outer_r, -half)
        .lineTo(outer_r, half)
        .lineTo(inner_r, half)
        .close()
        .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    )


def _headed_pin(shank_r, span, along_x=0):
    """Headed pin: shank with a round head one end and a hex nut the other, on
    the Y axis by default, on the X axis when `along_x` — the centre pin runs
    across the cheeks, the shackle pin runs across the bow."""
    head_r = _PIN_HEAD * shank_r
    head_t = shank_r
    plane = "YZ" if along_x else "XZ"
    body = cq.Workplane(plane).circle(shank_r).extrude(span)
    head = cq.Workplane(plane).circle(head_r).extrude(head_t).translate((0.0, 0.0, 0.0))
    nut = cq.Workplane(plane).polygon(6, 2.0 * head_r).extrude(head_t)
    # Workplane("XZ") extrudes toward -Y and Workplane("YZ") toward +X.
    sign = 1.0 if along_x else -1.0
    axis = (sign, 0.0, 0.0) if along_x else (0.0, sign, 0.0)

    def _at(shape, d):
        return shape.translate((axis[0] * d, axis[1] * d, 0.0))

    return (
        _at(body, -span / 2.0)
        .union(_at(head, span / 2.0))
        .union(_at(nut, -span / 2.0 - head_t))
    )


def _yoke(shank_r, tang_t, tang_w, top_z, bottom_z, pin_r):
    """Swivel yoke: a round shank hanging from the plate tails that flattens
    into a tang, which drops between the shackle ears and is pierced by the
    shackle pin. Round at the top so it can swivel; flat at the bottom because
    it has to fit the gap between the ears."""
    shank_len = (top_z - bottom_z) * 0.55
    shank = (
        cq.Workplane("XY").circle(shank_r).extrude(shank_len)
        .translate((0.0, 0.0, top_z - shank_len))
    )
    # overlap the shank by a shank radius so the join is buried, not tangent
    tang_top = top_z - shank_len + shank_r
    nose_r = tang_w / 2.0
    tang = (
        cq.Workplane("YZ")
        .moveTo(-tang_w / 2.0, tang_top)
        .lineTo(tang_w / 2.0, tang_top)
        .lineTo(tang_w / 2.0, bottom_z + nose_r)
        .threePointArc((0.0, bottom_z), (-tang_w / 2.0, bottom_z + nose_r))
        .close()
        .extrude(tang_t)
        .translate((-tang_t / 2.0, 0.0, 0.0))
    )
    bore = (
        cq.Workplane("YZ").circle(pin_r).extrude(3.0 * tang_t)
        .translate((-1.5 * tang_t, 0.0, bottom_z + nose_r))
    )
    return shank.union(tang).cut(bore)


def _shackle_bow(inside_w, height, bar_r, pin_r):
    """Anchor shackle: a semicircular bow closed by two straight legs that carry
    the pin. The pin axis is the local origin and the bow's outer crown sits
    `height` below it, so `height` is the catalogue H.

    Revolving the bar section about Y traces the tube centreline as a circle in
    XZ — the bow plane — so the bow needs no rotation. The lower half is kept by
    intersecting a half-space; the legs start above the torus centre line so
    they bury into it instead of meeting it at a tangent knife edge."""
    major_r = inside_w / 2.0 + bar_r
    crown_z = -(height - major_r - bar_r)      # tube centreline circle centre
    box = 4.0 * (major_r + bar_r)
    # makeTorus, not a revolved section: revolve wants a pending wire, so the
    # section needs .close(), but a section that already closes on itself gets a
    # zero-length edge from .close() and the revolve comes back empty.
    torus = cq.Workplane("XY").newObject(
        [cq.Solid.makeTorus(major_r, bar_r, cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0))]
    )
    lower = cq.Workplane("XY").box(box, box, box).translate((0.0, 0.0, -box / 2.0))
    result = torus.intersect(lower).translate((0.0, 0.0, crown_z))
    leg = -crown_z + bar_r                      # buried one bar radius into the bow
    for side in (-1.0, 1.0):
        result = result.union(
            cq.Workplane("XY").circle(bar_r).extrude(leg)
            .translate((side * major_r, 0.0, crown_z - bar_r))
        )
    # the pin runs leg-to-leg, i.e. along X, in the plane of the bow
    bore = (
        cq.Workplane("YZ").circle(pin_r).extrude(3.0 * box)
        .translate((-1.5 * box, 0.0, 0.0))
    )
    return result.cut(bore)


def build(sheave_d, rope_d, head_w_B, cheek_w_C, pin_to_throat_D, bar_thk_E,
          bow_width_G, bow_height_H, open_angle, roller_bearing=0):
    plate_t = _PLATE_T * cheek_w_C
    sheave_w = cheek_w_C - 2.0 * plate_t - 2.0 * _SIDE_CLR
    pin_r = 0.5 * bar_thk_E
    bore_r = pin_r + (2.5 if roller_bearing else 1.5)

    head_r = head_w_B / 2.0
    tail_r = _TAIL_R * head_w_B
    # Catalogue identity A = B/2 + D + E, verified against all 27 rows: the pin
    # sits B/2 under the plate crown, the bow throat bottom is D under the pin,
    # and the bow bar is E thick below that. Placing the shackle pin so the bow
    # crown lands on -(D + E) reproduces the published overall height exactly.
    shackle_pin_z = -(pin_to_throat_D + bar_thk_E - bow_height_H)
    yoke_len = _YOKE_LEN * bow_height_H
    tail_z = shackle_pin_z + yoke_len

    plate_y = sheave_w / 2.0 + _SIDE_CLR
    fixed = _plate(head_r, tail_r, tail_z, plate_t, bore_r).translate((0.0, -plate_y, 0.0))
    swing = (
        _plate(head_r, tail_r, tail_z, plate_t, bore_r)
        .translate((0.0, plate_y + plate_t, 0.0))
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), open_angle)
    )

    sheave = _sheave(sheave_d / 2.0, bore_r, sheave_w, rope_d)
    bushing = _tube(bore_r, pin_r, sheave_w)
    pin = _headed_pin(pin_r, cheek_w_C)
    # the tang has to clear the gap between the shackle ears, which is G
    yoke = _yoke(tail_r, 0.55 * bow_width_G, 1.5 * tail_r,
                 tail_z + tail_r, shackle_pin_z, pin_r)
    bow = _shackle_bow(bow_width_G, bow_height_H, 0.5 * bar_thk_E, pin_r).translate(
        (0.0, 0.0, shackle_pin_z)
    )
    # spans ear to ear: the legs stand at +/-(G/2 + E/2)
    bow_span = bow_width_G + 2.0 * bar_thk_E
    shackle_pin = _headed_pin(pin_r, bow_span, along_x=1).translate(
        (0.0, 0.0, shackle_pin_z)
    )

    result = cq.Assembly(name="snatch_block_single_sheave")
    result.add(fixed, name="side_plate_01")
    result.add(swing, name="side_plate_02")
    result.add(sheave, name="sheave")
    result.add(bushing, name="bushing")
    result.add(pin, name="centre_pin")
    result.add(yoke, name="swivel_yoke")
    result.add(bow, name="shackle_bow")
    result.add(shackle_pin, name="shackle_pin")
    return result
