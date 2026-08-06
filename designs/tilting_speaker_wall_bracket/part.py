"""tilting_speaker_wall_bracket — the parametric part (assembly).

B-Tech BT77-class tilt/swivel speaker wall mount, modelled as the MECHANISM
the drawing describes rather than a static silhouette. Reading the sheet:

* REAR VIEW — the wall plate (67.9 x 260.4) carries the keyhole at 33.3, plain
  holes at 76 / 127, the 17.2-spaced pair at 145, a 17.2 x 37.2 WINDOW below
  them, and a horizontal 8.5 x 24 slot near the bottom. That window is not
  decoration: it is the travel slot the tilt lock bolt rides in.
* SIDE VIEWS — "MAX TILT 10 deg" either way, the whole arm-and-clamp assembly
  swinging about a horizontal axis at the wall.
* TOP VIEWS — "min width 132.4" / "max width 280.3": two jaw bars telescoping
  through a round clamp body, i.e. the mount GRIPS the cabinet between two
  pads instead of bolting to it. The Ø10.5 bore on that body is the vertical
  swivel axis (the table's 360 deg swivel).

So the kinematic chain is: wall plate -> [tilt pivot + lock bolt in the
window] -> arm -> [vertical swivel post] -> clamp knuckle -> [two sliding
bars, each locked by a clamp screw] -> jaws.

Eight bodies: WALL_PLATE (hollow channel with the hole pattern, the tilt boss
and the window), ARM (clevis straddling the boss on integral pivot studs, out
to the vertical swivel post), TILT_BOLT (through the arm spine and the window
— it is what makes the tilt lockable), KNUCKLE (swivel disc bored Ø10.5 over
the post, square through-slots for the bars, top plate with the 3x Ø4.5
pattern at 91.5 x 45.8), two JAWS on their slide bars, and two CLAMP_SCREWS
locking those bars.

Frame: wall behind the XZ plane at y=0, plate vertical and centred at z=0, arm
out +Y, jaw bars along X. Tilt (about the pivot axis), swivel (about the post)
and clamp width are OPERATING STATES expressed as Locations, so a draw shows a
real pose of the mechanism; every probe sweeps the full range, not the pose.

Interface + examples: docs/DESIGN_SPEC.md
"""

import math

import cadquery as cq

# BT77 drawing constants (the catalog pattern itself, not free parameters).
# The rear view measures EVERYTHING from the plate TOP.
KEYHOLE_D = 6.5        # wall keyhole
SLOT_D = 8.5           # lower wall slot
HOLE_TOPS = (76.0, 127.0)   # single holes, from the plate top
PAIR_TOP = 145.0            # hole pair level, from the plate top
PAIR_SPAN = 17.2            # pair spacing
KEYHOLE_TOP = 33.3          # keyhole circle centre, from the plate top
WINDOW_H = 37.2             # tilt-bolt travel window height
WINDOW_W = 17.2             # tilt-bolt travel window width
SLOT_BOT = 25.0             # bottom slot centre above the plate bottom
PIVOT_D = 10.5         # swivel post / knuckle bore
CRADLE_HOLE_D = 4.5    # 3x THRU pattern
CRADLE_PAT_X = 91.5    # pattern span across the plate
CRADLE_PAT_Y = 45.8
TILT_PIN_D = 8.0       # tilt pivot studs
BOLT_D = 8.0           # tilt lock bolt
FIT = 0.4              # diametral running fit on every pin/bore pair
PIVOT_STANDOFF = 9.0   # tilt axis, off the wall-plate front face
BOSS_D = 18.0          # wall-plate tilt boss depth
YOKE_D = 12.0          # arm yoke depth (front-to-back)


def _tilt_frame(plate_h, plate_d, max_tilt):
    """Datums shared by the wall plate, the arm and the bolt.

    The tilt axis sits on the boss standing off the plate face; the arm's
    yoke hangs BELOW it and carries the lock bolt at the window. The yoke's
    standoff is DERIVED from max_tilt for two reasons, not guessed:

      * it must clear the boss in Y at all times (yoke ahead of the boss);
      * swinging to -max_tilt rotates the yoke's LOWEST point toward the
        wall by |dz|*sin(t), so the standoff has to absorb that or the arm
        sweeps into the plate — which is exactly what a fixed offset did at
        the +/-20 deg class.
    """
    s = math.sin(math.radians(max_tilt))
    c = math.cos(math.radians(max_tilt))
    top = plate_h / 2.0
    z_pivot = top - PAIR_TOP - 14.0
    z_window = z_pivot - 26.0                 # travel window, below the pivot
    drop = 26.0 + 7.0                         # yoke's lowest point, off the pivot
    boss_clear = BOSS_D + 1.0                 # yoke must sit ahead of the boss
    sweep = (drop * s - (PIVOT_STANDOFF - 1.0)) / c
    yoke_y = max(boss_clear, sweep) + 1.0
    return z_pivot, z_window, yoke_y


def _beam_y0(plate_d, beam_w, max_tilt):
    """Where the beam may start. Its rear-top corner swings TOWARD the wall by
    (beam_w/2)*sin(t) as the arm tilts up, so the beam has to begin clear of
    the boss front by that much — the corner that was scraping the boss at the
    +/-20 deg class before this was derived."""
    s = math.sin(math.radians(max_tilt))
    c = math.cos(math.radians(max_tilt))
    clear = (BOSS_D - PIVOT_STANDOFF + 1.0 + (beam_w / 2.0) * s) / c
    return plate_d + PIVOT_STANDOFF + clear + 1.0


def _wall_plate(plate_w, plate_h, plate_t, plate_d, max_tilt):
    """Wall member per the BT77 side view: a moulded channel column plate_d
    (drawing: 29) deep, hollow toward the wall, with the hole pattern through
    its plate_t front face, the tilt-bolt travel window, and the tilt boss the
    arm's clevis pivots on."""
    z_pivot, z_window, yoke_y = _tilt_frame(plate_h, plate_d, max_tilt)
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
    # tilt boss: a rib standing off the front face, bored across for the
    # arm's pivot studs. Its width sets the clevis gap.
    boss_w = PIVOT_D * 1.7
    boss_h = TILT_PIN_D * 2.6
    boss_y = plate_d + PIVOT_STANDOFF
    boss = (
        cq.Workplane("XY").box(boss_w, BOSS_D, boss_h)
        .edges("|X").fillet(2.0)
        .translate((0, plate_d + BOSS_D / 2.0, z_pivot))
    )
    plate = plate.union(boss)
    plate = plate.cut(
        cq.Workplane("YZ").workplane(offset=-plate_w)
        .center(boss_y, z_pivot)
        .circle((TILT_PIN_D + FIT) / 2.0).extrude(2.0 * plate_w)
    )
    top = plate_h / 2.0

    def zc(from_top):
        return top - from_top

    cuts = [
        # keyhole: circle at 33.3 with its slot rising to 20.8 from the top
        cq.Workplane("XZ").workplane(offset=plate_d * 2)
        .center(0, zc(KEYHOLE_TOP)).circle(KEYHOLE_D / 2.0).extrude(-plate_d * 4),
        cq.Workplane("XZ").workplane(offset=plate_d * 2)
        .center(0, (zc(KEYHOLE_TOP) + zc(20.8)) / 2.0)
        .slot2D(KEYHOLE_TOP - 20.8 + KEYHOLE_D * 0.55, KEYHOLE_D * 0.55, 90)
        .extrude(-plate_d * 4),
        # the tilt-bolt travel window (17.2 x 37.2)
        cq.Workplane("XZ").workplane(offset=plate_d * 2)
        .center(0, z_window)
        .slot2D(WINDOW_H, WINDOW_W, 90).extrude(-plate_d * 4),
        # bottom slot is HORIZONTAL: 8.5 x 24 near the plate bottom
        cq.Workplane("XZ").workplane(offset=plate_d * 2)
        .center(0, -top + SLOT_BOT).slot2D(24.0, SLOT_D, 0)
        .extrude(-plate_d * 4),
    ]
    for from_top in HOLE_TOPS:
        cuts.append(cq.Workplane("XZ").workplane(offset=plate_d * 2)
                    .center(0, zc(from_top)).circle(KEYHOLE_D / 2.0)
                    .extrude(-plate_d * 4))
    for sx in (-PAIR_SPAN / 2.0, PAIR_SPAN / 2.0):
        cuts.append(cq.Workplane("XZ").workplane(offset=plate_d * 2)
                    .center(sx, zc(PAIR_TOP)).circle(KEYHOLE_D / 2.0)
                    .extrude(-plate_d * 4))
    for c in cuts:
        plate = plate.cut(c)
    return plate


def _arm(plate_h, plate_d, beam_len, beam_w, post_h, max_tilt):
    """The tilting member, built in the UNTILTED pose about the tilt axis:
    a clevis whose two cheeks straddle the wall-plate boss on integral pivot
    studs, a spine carrying the lock bolt down at the window, the beam out
    +Y, and the vertical swivel post at its far end."""
    z_pivot, z_window, yoke_y = _tilt_frame(plate_h, plate_d, max_tilt)
    boss_w = PIVOT_D * 1.7
    cheek_t = 5.0
    cheek_x = boss_w / 2.0 + 0.5 + cheek_t / 2.0
    boss_y = plate_d + PIVOT_STANDOFF
    body = None
    for sx in (-cheek_x, cheek_x):
        # The cheeks straddle the boss and carry the pivot studs. Their REAR
        # boundary is an arc centred on the pivot, so the swept envelope is
        # the same at every tilt — that is why a real clevis is round there,
        # and it is what stops the fork scraping the wall plate at -max_tilt.
        r_rear = PIVOT_STANDOFF - 1.0
        cheek = (
            cq.Workplane("YZ").workplane(offset=sx - cheek_t / 2.0)
            .center(boss_y, z_pivot).circle(r_rear).extrude(cheek_t)
        )
        nose_len = BOSS_D / 2.0 + 12.0
        cheek = cheek.union(
            cq.Workplane("XY")
            .box(cheek_t, nose_len, 2.0 * r_rear)
            .edges("|X").fillet(2.5)
            .translate((sx, boss_y + nose_len / 2.0, z_pivot))
        )
        # integral pivot stud, pointing inboard into the boss bore
        stud = (
            cq.Workplane("YZ").workplane(offset=sx - math.copysign(cheek_t / 2.0, sx))
            .center(boss_y, z_pivot).circle(TILT_PIN_D / 2.0)
            .extrude(-math.copysign(boss_w / 2.0 + 0.6, sx))
        )
        body = cheek if body is None else body.union(cheek)
        body = body.union(stud)
    # spine: joins the cheeks BELOW the boss (never through it) and carries the
    # lock-bolt hole down at the window. Its rear face sits on the pivot's own
    # y, so swinging +/-20 deg can never drive it into the wall plate.
    z_yoke_top = z_pivot + 10.0
    z_yoke_bot = z_window - 7.0
    spine = (
        cq.Workplane("XY")
        .box(2.0 * cheek_x + cheek_t, YOKE_D, z_yoke_top - z_yoke_bot)
        .edges("|Y").fillet(3.0)
        .translate((0, boss_y + yoke_y + YOKE_D / 2.0,
                    (z_yoke_top + z_yoke_bot) / 2.0))
    )
    body = body.union(spine)
    body = body.cut(
        cq.Workplane("XZ").workplane(offset=plate_d * 3)
        .center(0, z_window).circle((BOLT_D + FIT) / 2.0)
        .extrude(-plate_d * 6)
    )
    # beam out to the clamp, on the tilt axis so the reach is unchanged by pose
    beam = (
        cq.Workplane("XY").box(beam_w, beam_len, beam_w)
        .edges("|Y").fillet(beam_w * 0.18)
        .translate((0, _beam_y0(plate_d, beam_w, max_tilt) + beam_len / 2.0,
                    z_pivot))
    )
    body = body.union(beam)
    # vertical swivel post at the beam end: it starts inside the beam and
    # reaches up through the knuckle bore, so the clamp head is carried by a
    # real journal rather than floating above the arm
    post = (
        cq.Workplane("XY").circle(PIVOT_D / 2.0)
        .extrude(post_h)
        .translate((0, _beam_y0(plate_d, beam_w, max_tilt) + beam_len
                    - beam_w * 0.5, z_pivot))
        .edges(">Z").chamfer(0.6)
    )
    return body.union(post)


def _tilt_bolt(plate_d, yoke_y):
    """The lock bolt: it passes through the arm spine and the wall-plate
    window, and clamping it is what fixes a tilt angle. Built about the
    window centre in the arm's frame."""
    y_head = plate_d + PIVOT_STANDOFF + yoke_y + YOKE_D + 4.0
    head = (
        cq.Workplane("XZ").workplane(offset=y_head)
        .circle(BOLT_D * 0.85).extrude(-4.0)
        .edges().chamfer(0.5)
    )
    # long enough that the shank still crosses the window at full tilt
    shank = (
        cq.Workplane("XZ").workplane(offset=y_head - 4.0)
        .circle(BOLT_D / 2.0).extrude(-(y_head - 4.0 + 16.0))
    )
    return head.union(shank)


def _knuckle(knuckle_d, knuckle_t, bar_d, cradle_w, cradle_l):
    """Round clamp body: bored Ø10.5 over the arm's swivel post, two square
    through-slots for the jaw bars, tapped holes for the clamp screws, and
    the top plate with the 3x 4.5 THRU pattern at 91.5 x 45.8."""
    body = (
        cq.Workplane("XY").circle(knuckle_d / 2.0)
        .extrude(knuckle_t).edges().chamfer(0.8)
    )
    top = (
        cq.Workplane("XY").box(cradle_l, cradle_w, 3.0)
        .edges("|Z").fillet(5.0)
        .translate((0, 0, knuckle_t + 1.0))  # buries 0.5: one moulded body
    )
    body = body.union(top)
    # swivel bore over the post
    body = body.cut(
        cq.Workplane("XY").circle((PIVOT_D + FIT) / 2.0)
        .extrude(knuckle_t + 6.0).translate((0, 0, -1.0))
    )
    bar_off = knuckle_d * 0.18
    for yo in (bar_off, -bar_off):
        body = body.cut(
            cq.Workplane("XY").box(knuckle_d * 2.0, bar_d + FIT, bar_d + FIT)
            .translate((0, yo, knuckle_t / 2.0))
        )
        # clamp-screw hole down onto that bar, offset outboard of the bore
        body = body.cut(
            cq.Workplane("XY").center(knuckle_d * 0.31, yo)
            .circle(BOLT_D * 0.42)
            .extrude(knuckle_t + 6.0).translate((0, 0, knuckle_t / 2.0))
        )
    for (hx, hy) in ((-CRADLE_PAT_X / 2.0, -CRADLE_PAT_Y / 2.0),
                     (CRADLE_PAT_X / 2.0, -CRADLE_PAT_Y / 2.0),
                     (0.0, CRADLE_PAT_Y / 2.0)):
        body = body.cut(
            cq.Workplane("XY").center(hx, hy).circle(CRADLE_HOLE_D / 2.0)
            .extrude(6.0).translate((0, 0, knuckle_t))
        )
    return body


def _clamp_screw(knuckle_t, bar_d, bar_off, knuckle_d):
    """Thumb screw that locks one jaw bar in the knuckle: it reaches down the
    tapped hole until it bears on the bar's top face, so the sliding width is
    actually fixed by something."""
    z_bar_top = knuckle_t / 2.0 + bar_d / 2.0
    shank_top = knuckle_t + 4.0
    screw = (
        cq.Workplane("XY").workplane(offset=z_bar_top + 0.2)
        .circle(BOLT_D * 0.40).extrude(shank_top - z_bar_top - 0.2)
        .union(cq.Workplane("XY").workplane(offset=shank_top)
               .polygon(6, BOLT_D * 1.15).extrude(3.2))
        .edges(">Z").chamfer(0.4)
    )
    return screw.translate((knuckle_d * 0.31, bar_off, 0))


def _jaw(jaw_h, jaw_d, bar_d, bar_len, bar_off):
    """One sliding jaw, built for the +X side: vertical grip plate with an
    inturned bottom lip, and its slide bar running inboard (-X) at the front
    bar position; the opposite jaw is this geometry turned 180 about Z."""
    # the photo's jaw is an L: the slide bar and the inturned foot are at the
    # BOTTOM, the grip plate stands up from there. Building it that way also
    # keeps every jaw above the beam through a full 360 deg swivel.
    jaw_t = 4.0
    plate = (
        cq.Workplane("XY").box(jaw_t, jaw_d, jaw_h)
        .edges("|X").fillet(6.0)
        .translate((jaw_t / 2.0, 0, jaw_h / 2.0))
    )
    lip = (
        cq.Workplane("XY").box(jaw_t + 14.0, jaw_d, jaw_t)
        .translate((-(jaw_t + 14.0) / 2.0 + jaw_t, 0, jaw_t / 2.0))
    )
    bar = (
        cq.Workplane("XY").box(bar_len, bar_d, bar_d)
        .translate((-bar_len / 2.0, bar_off, 0))
    )
    return plate.union(lip).union(bar)


def build(plate_w, plate_h, plate_t, plate_d, arm_reach, beam_w,
          knuckle_d, knuckle_t, bar_d, jaw_span, jaw_h, jaw_d,
          cradle_w, cradle_l, max_tilt, tilt_pose, swivel_pose):
    z_pivot, z_window, yoke_y = _tilt_frame(plate_h, plate_d, max_tilt)
    # arm_reach is the catalog's OVERALL depth (drawing: 270.3 max): place the
    # knuckle so the deepest element (jaw front or knuckle rim) lands on it
    arm_y = arm_reach - max(jaw_d, knuckle_d) / 2.0
    beam_len = arm_y - _beam_y0(plate_d, beam_w, max_tilt) + beam_w * 0.5
    bar_off = knuckle_d * 0.18
    # each bar must still be captured by BOTH knuckle slots at full opening
    bar_len = jaw_span / 2.0 + knuckle_d * 0.55
    # the knuckle seats on the beam top; the post runs from the beam centre up
    # through it, ending inside the top plate's bore
    z_seat = beam_w / 2.0 + 0.5
    post_h = z_seat + knuckle_t + 2.0

    result = cq.Assembly(name="tilting_speaker_wall_bracket")
    result.add(_wall_plate(plate_w, plate_h, plate_t, plate_d, max_tilt),
               name="wall_plate")

    # everything downstream of the tilt pivot swings together about the X axis
    # through (0, plate_d + 9, z_pivot) — that is what the window's travel buys
    tilting = cq.Assembly(
        name="tilting",
        loc=cq.Location(cq.Vector(0.0, plate_d + 9.0, z_pivot),
                        cq.Vector(1.0, 0.0, 0.0), tilt_pose)
        * cq.Location(cq.Vector(0.0, -(plate_d + 9.0), -z_pivot)))
    tilting.add(_arm(plate_h, plate_d, beam_len, beam_w, post_h, max_tilt),
                name="arm")
    tilting.add(_tilt_bolt(plate_d, yoke_y), name="tilt_bolt",
                loc=cq.Location(cq.Vector(0.0, 0.0, z_window)))

    # the clamp head swivels about the vertical post (catalog: 360 deg)
    swivelling = cq.Assembly(
        name="clamp_head",
        loc=cq.Location(cq.Vector(0.0, arm_y, z_pivot + z_seat),
                        cq.Vector(0.0, 0.0, 1.0), swivel_pose))
    swivelling.add(_knuckle(knuckle_d, knuckle_t, bar_d, cradle_w, cradle_l),
                   name="knuckle")
    jaw = _jaw(jaw_h, jaw_d, bar_d, bar_len, bar_off)
    swivelling.add(jaw, name="jaw_01",
                   loc=cq.Location(cq.Vector(jaw_span / 2.0, 0.0,
                                             knuckle_t / 2.0)))
    swivelling.add(jaw, name="jaw_02",
                   loc=cq.Location(cq.Vector(-jaw_span / 2.0, 0.0,
                                             knuckle_t / 2.0),
                                   cq.Vector(0.0, 0.0, 1.0), 180.0))
    for i, yo in enumerate((bar_off, -bar_off)):
        swivelling.add(_clamp_screw(knuckle_t, bar_d, yo, knuckle_d),
                       name="clamp_screw_%02d" % (i + 1))
    tilting.add(swivelling)
    result.add(tilting)
    return result
