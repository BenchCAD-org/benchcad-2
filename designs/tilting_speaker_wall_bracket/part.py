"""tilting_speaker_wall_bracket — the parametric part (assembly).

B-Tech BT77-class tilt/swivel speaker wall mount, modelled as the clamp the
product is: a keyhole WALL PLATE (drawing: 67.9 x 260.4, keyhole 6.5 with the
30 top offset, centreline holes at 76 / 127, the 8.5 slot at 145), a welded
standoff ARM, the round clamp KNUCKLE the two sliding JAW bars run through
(min width 132.4 -> max 280.3), and the tilting CRADLE on its 10.5 pivot post
(top plate with the 3x 4.5 THRU pattern at 91.5 x 45.8; max tilt 10 or 20 deg
by model class).

Frame: wall behind the XZ plane at y=0, plate vertical and centred at z=0,
arm out +Y, jaw bars along X, cradle up +Z. Sliding span and tilt are
OPERATING STATES expressed as component Locations — the two jaws are one
geometry placed at +/- jaw_span/2 (the far one rotated 180 about Z), and the
cradle is rotated by tilt_pose about the pivot. The pivot standoff is computed
from max_tilt so the cradle clears the knuckle across its WHOLE travel, not
just at the sampled pose.

Interface + examples: docs/DESIGN_SPEC.md
"""

import math

import cadquery as cq

# BT77 drawing constants (the catalog pattern itself, not free parameters)
KEYHOLE_D = 6.5        # wall keyhole
SLOT_D = 8.5           # lower wall slot
HOLE_STEPS = (76.0, 127.0, 145.0)  # centreline spacings below the keyhole
TOP_OFFSET = 30.0      # keyhole centre below the plate top edge
PIVOT_D = 10.5         # cradle pivot post
CRADLE_HOLE_D = 4.5    # 3x THRU pattern
CRADLE_PAT_X = 91.5    # pattern span across the plate
CRADLE_PAT_Y = 45.8


def _wall_plate(plate_w, plate_h, plate_t, plate_d):
    """Wall member per the BT77 side view: a moulded channel column plate_d
    (drawing: 29) deep, hollow toward the wall, with the hole pattern through
    its plate_t front face — keyhole at the 30 top offset, plain holes 76 and
    127 below it, the 8.5 slot at 145, all on the centreline."""
    plate = (
        cq.Workplane("XY").box(plate_w, plate_d, plate_h)
        .edges("|Y").fillet(plate_w * 0.12)
        .translate((0, plate_d / 2.0, 0))
    )
    # hollow the wall side: perimeter walls + the front face remain
    plate = plate.cut(
        cq.Workplane("XY")
        .box(plate_w - 8.0, plate_d - plate_t, plate_h - 8.0)
        .translate((0, (plate_d - plate_t) / 2.0, 0))
    )
    zk = plate_h / 2.0 - TOP_OFFSET
    cuts = [
        cq.Workplane("XZ").workplane(offset=plate_d * 2)
        .center(0, zk).circle(KEYHOLE_D / 2.0).extrude(-plate_d * 4),
        cq.Workplane("XZ").workplane(offset=plate_d * 2)
        .center(0, zk + 6.0).slot2D(12.0, KEYHOLE_D * 0.55, 90)
        .extrude(-plate_d * 4),
        cq.Workplane("XZ").workplane(offset=plate_d * 2)
        .center(0, zk - HOLE_STEPS[2]).slot2D(24.0, SLOT_D, 90)
        .extrude(-plate_d * 4),
    ]
    for step in HOLE_STEPS[:2]:
        cuts.append(cq.Workplane("XZ").workplane(offset=plate_d * 2)
                    .center(0, zk - step).circle(KEYHOLE_D / 2.0)
                    .extrude(-plate_d * 4))
    for c in cuts:
        plate = plate.cut(c)
    return plate


def _arm(arm_reach, arm_h, beam_w, plate_d):
    """Welded standoff off the column's front face: a vertical channel
    carrying the horizontal beam out to the knuckle."""
    upright = (
        cq.Workplane("XY").box(beam_w + 10.0, 8.0, arm_h)
        .edges("|Y").fillet(3.0)
        .translate((0, plate_d + 4.0, 0))
    )
    beam = (
        cq.Workplane("XY").box(beam_w, arm_reach, beam_w)
        .translate((0, plate_d + arm_reach / 2.0, 0))
    )
    gusset = (
        cq.Workplane("XY").box(beam_w * 0.6, arm_reach * 0.35, beam_w * 0.6)
        .translate((0, plate_d + arm_reach * 0.2, -beam_w * 0.55))
    )
    return upright.union(beam).union(gusset)


def _knuckle(knuckle_d, knuckle_t, bar_d, beam_w, standoff):
    """Round clamp body at the arm end: horizontal disc with a socket pocket
    for the arm beam (-Y side), two square X through-slots for the jaw bars,
    and the pressed 10.5 pivot post standing up to the cradle hinge."""
    body = (
        cq.Workplane("XY").circle(knuckle_d / 2.0)
        .extrude(-knuckle_t).translate((0, 0, knuckle_t / 2.0))
    )
    # arm socket: the beam nests into the disc edge with clearance
    body = body.cut(
        cq.Workplane("XY").box(beam_w + 0.4, knuckle_d * 0.32, beam_w + 0.4)
        .translate((0, -knuckle_d * 0.49, 0))
    )
    bar_off = knuckle_d * 0.18
    for yo in (bar_off, -bar_off):
        body = body.cut(
            cq.Workplane("XY").box(knuckle_d * 2.0, bar_d + 0.4, bar_d + 0.4)
            .translate((0, yo, 0))
        )
    # pressed pivot post: 12 into the disc, up to 6 under the cradle hinge
    post = (
        cq.Workplane("XY").circle(PIVOT_D / 2.0)
        .extrude(standoff - 6.0 + 12.0)
        .translate((0, 0, knuckle_t / 2.0 - 12.0))
    )
    return body.union(post)


def _jaw(jaw_h, jaw_d, bar_d, bar_len, bar_off):
    """One sliding jaw, built for the +X side: vertical grip plate with an
    inturned bottom lip, and its slide bar running inboard (-X) at the front
    bar position; the opposite jaw is this geometry turned 180 about Z."""
    jaw_t = 4.0
    plate = (
        cq.Workplane("XY").box(jaw_t, jaw_d, jaw_h)
        .edges("|X").fillet(6.0)
        .translate((jaw_t / 2.0, 0, 0))
    )
    lip = (
        cq.Workplane("XY").box(jaw_t + 14.0, jaw_d, jaw_t)
        .translate((-(jaw_t + 14.0) / 2.0 + jaw_t, 0,
                    -(jaw_h / 2.0 - jaw_t / 2.0)))
    )
    bar = (
        cq.Workplane("XY").box(bar_len, bar_d, bar_d)
        .translate((-bar_len / 2.0, bar_off, 0))
    )
    return plate.union(lip).union(bar)


def _cradle(cradle_w, cradle_l):
    """Tilting speaker cradle: the hinge saddle (pivoting about the origin,
    which sits at the post top) and the top plate with the 3x 4.5 THRU
    pattern at 91.5 x 45.8."""
    saddle = cq.Workplane("XY").box(16.0, 16.0, 5.0)
    top = (
        cq.Workplane("XY").box(cradle_l, cradle_w, 3.0)
        .edges("|Z").fillet(5.0)
        .translate((0, 0, 3.5))  # buries 0.5 into the saddle: one welded body
    )
    cradle = saddle.union(top)
    for (hx, hy) in ((-CRADLE_PAT_X / 2.0, -CRADLE_PAT_Y / 2.0),
                     (CRADLE_PAT_X / 2.0, -CRADLE_PAT_Y / 2.0),
                     (0.0, CRADLE_PAT_Y / 2.0)):
        cradle = cradle.cut(
            cq.Workplane("XY").center(hx, hy).circle(CRADLE_HOLE_D / 2.0)
            .extrude(6.0).translate((0, 0, 2.5))
        )
    return cradle


def build(plate_w, plate_h, plate_t, plate_d, arm_reach, arm_h, beam_w,
          knuckle_d, knuckle_t, bar_d, jaw_span, jaw_h, jaw_d,
          cradle_w, cradle_l, max_tilt, tilt_pose):
    arm_y = plate_d + arm_reach + knuckle_d * 0.35
    bar_off = knuckle_d * 0.18
    # bar runs from its jaw through the knuckle, never past the far jaw plate
    bar_len = min(jaw_span / 2.0 + knuckle_d / 2.0 + 15.0, jaw_span - 12.0)
    # pivot standoff sized so the cradle clears the knuckle top across the
    # WHOLE +/-max_tilt travel, not just at the sampled pose
    standoff = math.sin(math.radians(max_tilt)) * cradle_l / 2.0 + 3.0

    result = cq.Assembly(name="tilting_speaker_wall_bracket")
    result.add(_wall_plate(plate_w, plate_h, plate_t, plate_d), name="wall_plate")
    result.add(_arm(arm_reach, arm_h, beam_w, plate_d), name="arm")
    result.add(_knuckle(knuckle_d, knuckle_t, bar_d, beam_w, standoff),
               name="knuckle", loc=cq.Location((0, arm_y, 0)))
    jaw = _jaw(jaw_h, jaw_d, bar_d, bar_len, bar_off)
    result.add(jaw, name="jaw_01",
               loc=cq.Location((jaw_span / 2.0, arm_y, 0)))
    result.add(jaw, name="jaw_02",
               loc=cq.Location((-jaw_span / 2.0, arm_y, 0), (0, 0, 1), 180))
    # hinge at the post top: only the saddle + plate tilt; the post stays
    # vertical in its bore, so no pose can gouge the knuckle
    result.add(_cradle(cradle_w, cradle_l), name="cradle",
               loc=cq.Location((0, arm_y, knuckle_t / 2.0 + standoff),
                               (1, 0, 0), tilt_pose))
    return result
