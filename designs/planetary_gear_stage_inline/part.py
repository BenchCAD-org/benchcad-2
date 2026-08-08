"""planetary_gear_stage_inline — a single-stage inline planetary gearhead.

Not a bare gear set: the complete gearhead as it is sold. A sun cut on its input
shaft, N planets running on flanged bushings over cantilevered pins, an internal
ring gear cut into the housing bore, a disc carrier whose plate, pins and output
journal are one body, and the hardware that makes it a machine element rather
than a kinematic diagram — two deep-groove ball bearings on the output journal, a
bearing head that is also the machine mounting flange, a radial shaft seal, split
retaining rings on the pin ends, a motor adapter, an input clamping hub, and the
tie bolts that hold the case together.

The tooth flanks are true involutes generated from the standard basic rack
(DIN 867 / ISO 53: pressure angle 20 deg, addendum 1.0*m, dedendum 1.25*m), so
the geometry follows the standard rather than a table. The ring is generated as
the *space* form of the same involute and cut from the housing, which is what
makes its teeth mesh with the planets instead of merely looking like teeth.

The bearings and the seal are not invented either: they are selected from the
ISO 15 / DIN 625-1 series-60 and DIN 3760 form A tables below, by the smallest
standard size that accepts the output journal.

Frame: the gear axis is Z. The stage occupies z in [0, face_width]; the housing
runs back to -housing_face_t and the motor adapter back beyond that; the bearing
head runs forward from face_width and the output shaft leaves +Z. `base_plane`
is XY.
"""

import cadquery as cq
import math

_PRESSURE_ANGLE = 20.0     # deg, DIN 867 / ISO 53 basic rack
_ADDENDUM = 1.0            # x module, DIN 867
_DEDENDUM = 1.25           # x module, DIN 867
_FLANK_PTS = 14            # involute samples per flank
_TIP_PTS = 3               # samples across the tip land
# Circumferential backlash, x module, taken off the EXTERNAL members only. Real
# gears are cut with it (DIN 3967 tolerance series); without it a zero-backlash
# involute pair touches along a line, and a polyline-approximated one overlaps.
_BACKLASH = 0.08

# ISO 15 / DIN 625-1, series 60 ("light"): (bore, outside diameter, width) mm.
# Real catalogue rows -- the output bearing is selected from this table by bore,
# never dimensioned freely.
_BEARING_60 = [(10, 26, 8), (12, 28, 8), (15, 32, 9), (17, 35, 10), (20, 42, 12),
               (25, 47, 12), (30, 55, 13), (35, 62, 14), (40, 68, 15)]

# DIN 3760 form A radial shaft seals: (shaft diameter, outside diameter, width) mm.
_SEAL_A = [(10, 22, 7), (12, 24, 7), (15, 26, 7), (17, 30, 7), (20, 35, 7),
           (25, 40, 7), (30, 47, 7), (35, 52, 7), (40, 55, 8)]

# ISO 4762 socket head cap screws: (thread d, head d, head height, socket a/f).
_SHCS = {3: (5.5, 3.0, 2.5), 4: (7.0, 4.0, 3.0), 5: (8.5, 5.0, 4.0),
         6: (10.0, 6.0, 5.0), 8: (13.0, 8.0, 6.0)}

# Proportions the standard does not fix (each one listed in NOTES.md).
_PIN_D = 0.34              # planet pin diameter / (module * z_planet)
_BUSH_W = 0.18             # bushing wall / pin diameter
_CARRIER_T = 0.55          # carrier disc thickness / face width
_HUB = 1.9                 # carrier hub diameter / pin diameter
_CLR = 0.20                # running clearance, mm, on sliding fits
_WALL = 1.5                # minimum wall left over a bolt or a bearing seat, mm


def _inv(a):
    """Involute function inv(a) = tan(a) - a, the angular lag of the involute."""
    return math.tan(a) - a


def _half_angle(r, r_base, r_pitch, alpha):
    """Half the angular width of an EXTERNAL tooth at radius r, measured from
    the tooth centreline. At the pitch radius this is pi/(2z), which is what
    makes the tooth thickness pi*m/2 there."""
    if r <= r_base:
        r = r_base * (1.0 + 1e-9)
    return _inv(alpha) - _inv(math.acos(min(1.0, r_base / r)))


def _gear_profile(module, z, internal, alpha_deg=_PRESSURE_ANGLE,
                  phase_deg=0.0):
    """Closed boundary of an involute gear as a point list.

    For an external gear this is the outline of the teeth. For an internal gear
    it is the *bore* outline: the tooth space of an internal gear is congruent
    to an external tooth, so the internal tooth half-angle is pi/z minus the
    external one, and the profile runs from the root (outer) in to the tip
    (inner). Cutting this from a disc leaves teeth pointing inward."""
    alpha = math.radians(alpha_deg)
    r_pitch = 0.5 * module * z
    r_base = r_pitch * math.cos(alpha)
    if internal:
        r_tip = r_pitch - _ADDENDUM * module          # innermost
        r_root = r_pitch + _DEDENDUM * module         # outermost
    else:
        r_tip = r_pitch + _ADDENDUM * module
        # The root goes to the TRUE dedendum circle, not to the base circle.
        # Below 17 teeth at 20 deg the base circle sits ABOVE the dedendum
        # circle, so stopping the flank at the base circle leaves the tooth
        # space too shallow and the mating tip drives straight into solid metal.
        # `_half_angle` clamps r to r_base, so the flank continues below the
        # base circle as a radial line -- the usual stand-in for the trochoid.
        r_root = max(r_pitch - _DEDENDUM * module, 0.15 * r_pitch)
    base_half = math.pi / (2.0 * z)
    pitch = 2.0 * math.pi / z

    def half_at(r):
        h = base_half + _half_angle(r, r_base, r_pitch, alpha)
        if internal:
            return math.pi / z - h
        return h - 0.5 * _BACKLASH * module / max(r, 1e-6)

    # radii from root to tip, along the working flank
    lo, hi = (min(r_tip, r_root), max(r_tip, r_root))
    radii = [lo + (hi - lo) * i / (_FLANK_PTS - 1) for i in range(_FLANK_PTS)]
    if internal:
        radii.reverse()                                # root (outer) -> tip (inner)

    pts = []
    ph = math.radians(phase_deg)
    for k in range(int(z)):
        c = k * pitch + ph
        for r in radii:                                # leading flank
            a = c - half_at(r)
            pts.append((r * math.cos(a), r * math.sin(a)))
        tip_half = half_at(radii[-1])                  # across the tip land
        for i in range(1, _TIP_PTS):
            a = c - tip_half + 2.0 * tip_half * i / _TIP_PTS
            pts.append((radii[-1] * math.cos(a), radii[-1] * math.sin(a)))
        for r in reversed(radii):                      # trailing flank
            a = c + half_at(r)
            pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def _gear_solid(module, z, width, internal=False, phase_deg=0.0):
    return (
        cq.Workplane("XY")
        .polyline(_gear_profile(module, z, internal, phase_deg=phase_deg))
        .close()
        .extrude(width)
    )


def mesh_phase(z_sun, z_planet, z_ring):
    """Tooth phases that let each planet mesh the sun AND the ring at once.

    `_gear_profile` puts a tooth centre at angle 0 for both the external and the
    internal form. A planet on the +X axis needs a tooth SPACE facing the sun
    (local angle 180 deg) and, against a ring that has a tooth at angle 0, a
    space facing the ring as well (local angle 0). Both are space centres only if
    180 deg is a whole number of space pitches, i.e. only if z_planet is EVEN.

    So for an odd planet the RING gets a half-pitch shift instead, and the planet
    presents a tooth to the ring and a space to the sun. Getting this wrong is
    invisible in every rendered view and shows up only as solids that overlap.

    Returns (ring_phase_deg, planet_phase_deg)."""
    if int(z_planet) % 2 == 0:
        return 0.0, 180.0 - 180.0 / z_planet
    return 180.0 / z_ring, 0.0


def planet_spin(z_sun, z_planet, z_ring, carrier_deg):
    """Absolute planet rotation at a given carrier angle, ring held.

    In the carrier frame the ring turns at -w_c and drives the planet through an
    internal mesh, giving w_p = w_c*(1 - z_ring/z_planet). With
    z_ring = z_sun + 2*z_planet that is -(z_sun + z_planet)/z_planet per unit of
    carrier rotation — NOT -z_sun/z_planet, which is the planet's speed relative
    to the carrier and leaves the teeth fouling the ring as the carrier turns."""
    return -carrier_deg * (z_sun + z_planet) / float(z_planet)


def _tube(r_out, r_in, length, z=0.0):
    """Plain annulus. Used everywhere a ring is wanted; `r_in <= 0` gives a rod."""
    w = cq.Workplane("XY").circle(r_out)
    if r_in > 0.0:
        w = w.circle(r_in)
    return w.extrude(length).translate((0.0, 0.0, z))


def _pick(table, want):
    """Smallest standard row whose first column accepts `want`. Returns None when
    the part is off the top of the table -- the caller must reject that draw
    rather than invent a size."""
    for row in table:
        if row[0] >= want - 1e-9:
            return row
    return None


def screw_size(ring_pitch_d):
    """Tie-bolt thread, stepped with the frame the way a catalogue does."""
    for limit, d in ((30.0, 3), (60.0, 4), (100.0, 5), (160.0, 6)):
        if ring_pitch_d < limit:
            return d
    return 8


def clamp_boss_h(screw_d):
    """Axial height of the clamp boss. It has to exceed the clamp screw diameter
    with material left above and below, or the boss is cut in half by its own
    hole and the C-ring falls into three pieces."""
    return screw_d + 2.4


def clamp_length(sun_shaft_len, screw_d):
    """Axial length of the input clamping hub — long enough to carry that boss."""
    return max(4.0, 0.35 * sun_shaft_len, clamp_boss_h(screw_d) / 0.8 + 0.6)


def housing_od_min(module, z_ring, output_shaft_d):
    """Smallest housing that can carry its own tie bolts outside both the ring
    gear and the output bearing seat. This is a REQUIREMENT, not a proportion,
    and it is what sets `housing_od` -- shared with `layout()` and with
    `spec.refine()` so the three cannot drift apart."""
    ring_pitch_d = module * z_ring
    ring_root_r = 0.5 * ring_pitch_d + _DEDENDUM * module
    bearing = _pick(_BEARING_60, output_shaft_d)
    if bearing is None:
        return None
    head_d = _SHCS[screw_size(ring_pitch_d)][0]
    bolt_r = max(ring_root_r, 0.5 * bearing[1]) + _WALL + 0.5 * head_d
    return 2.0 * (bolt_r + 0.5 * head_d + _WALL)


def output_bearing(output_shaft_d):
    """The ISO 15 series-60 row the output journal takes, or None if the shaft is
    off the top of the table."""
    return _pick(_BEARING_60, output_shaft_d)


def layout(module, z_sun, z_planet, z_ring, n_planets, face_width, housing_od,
           housing_face_t, sun_shaft_d, sun_shaft_len, output_shaft_d,
           output_shaft_len):
    """Every derived dimension in one place, so `check()` and `build()` cannot
    disagree about the machine they are describing. Returns None if the draw
    cannot be built as a real gearhead; the caller turns that into a Resample."""
    ring_pitch_d = module * z_ring
    ring_root_r = 0.5 * ring_pitch_d + _DEDENDUM * module

    bearing = _pick(_BEARING_60, output_shaft_d)
    seal = _pick(_SEAL_A, output_shaft_d)
    if bearing is None or seal is None:
        return None                       # output shaft is off the top of both tables
    b_bore, b_od, b_w = bearing
    s_d, s_od, s_w = seal

    screw_d = screw_size(ring_pitch_d)
    head_d, head_h, socket_af = _SHCS[screw_d]

    # The tie bolts have to pass OUTSIDE the ring gear and outside the bearing
    # seat, with a wall left on both sides. That requirement -- not a chosen
    # proportion -- is what sets the housing diameter.
    bolt_r = max(ring_root_r, 0.5 * b_od) + _WALL + 0.5 * head_d
    if housing_od < housing_od_min(module, z_ring, output_shaft_d):
        return None                       # the drawn housing cannot carry its own bolts

    pin_d = max(2.0, _PIN_D * module * z_planet)
    bush_t = max(0.35, _BUSH_W * pin_d)                     # bushing wall
    planet_bore = pin_d + 2.0 * (bush_t + _CLR * 0.5)
    planet_root_r = 0.5 * module * z_planet - _DEDENDUM * module
    if 0.5 * planet_bore > planet_root_r - 0.8:
        return None                       # no rim left between the bore and the roots
    bush_flange_r = min(0.5 * planet_bore + max(0.4, 0.18 * pin_d),
                        planet_root_r - 0.3)
    bush_flange_t = max(0.4, 0.10 * face_width)

    # DIN 471-style retaining ring on the free end of each pin
    clip_t = max(0.5, 0.09 * pin_d)
    clip_groove_r = 0.5 * pin_d - max(0.30, 0.05 * pin_d)
    clip_out_r = 0.5 * pin_d + max(0.7, 0.16 * pin_d)
    clip_gap = 0.4                                          # flange to circlip
    pin_ext = bush_flange_t + clip_gap + clip_t + 0.8       # pin beyond the planet

    disc_t = _CARRIER_T * face_width
    pin_circle_r = 0.5 * module * (z_sun + z_planet)
    # The pin must sit strictly INSIDE the plate rim. Making the plate exactly
    # tangent to the pin leaves a zero-thickness knife edge that OCC cannot
    # tessellate -- it fails late, in the renderer, as `NbNodes` on a null
    # triangulation.
    plate_r = pin_circle_r + 0.5 * pin_d + max(0.4, 0.10 * pin_d)

    end_float = max(0.15, 0.03 * face_width)
    z_head0 = face_width                  # bolted joint: head meets housing here
    z_plate0 = face_width + end_float
    z_plate1 = z_plate0 + disc_t
    z_bear_a = z_plate1 + 0.8
    z_bear_b = z_bear_a + b_w + max(1.0, 0.12 * b_w * 8)    # spacer step between them
    z_journal_end = z_bear_b + b_w
    z_seal0 = z_journal_end + 1.0
    z_head1 = z_seal0 + s_w + max(1.5, _WALL)               # head front face

    # the head bore must step DOWN monotonically toward +Z or it cannot be bored
    carrier_clr_r = max(plate_r + _CLR * 2.0, 0.5 * b_od + 0.2)
    if carrier_clr_r + _WALL > 0.5 * housing_od:
        return None
    if 0.5 * b_od <= 0.5 * s_od or 0.5 * s_od <= 0.5 * output_shaft_d:
        return None                       # bore steps are not monotonic

    if plate_r <= 0.5 * b_bore + 1.0:
        return None                       # the plate cannot carry the journal

    # input side: the sun must reach into the adapter far enough to be clamped
    clamp_len = clamp_length(sun_shaft_len, screw_d)
    clamp_od = min(1.85 * sun_shaft_d, 2.0 * (ring_root_r - 2.0))
    if clamp_od <= sun_shaft_d + 1.0:
        return None
    if sun_shaft_len < housing_face_t + clamp_len + 1.0:
        return None
    # The clamp screw has to sit entirely OUTSIDE the hub wall, in a boss. A hole
    # whose envelope reaches back inside the tube cuts a slot right through the
    # wall for the full length, and the C-ring falls into three pieces.
    hub_boss_x = 0.5 * clamp_od + 0.5 * screw_d + 0.4
    hub_boss_r = hub_boss_x + 0.5 * screw_d + 1.6
    hub_slit_w = max(0.6, 0.10 * clamp_od)
    hub_boss_w = hub_slit_w + 2.0 * (screw_d + 1.2)
    # the boss is a BOX: its corners sweep further than its radial extent, and
    # the adapter cavity has to clear the corners, not the face
    hub_sweep_r = math.hypot(hub_boss_r, 0.5 * hub_boss_w)
    z_adapter1 = -housing_face_t
    z_adapter0 = -(sun_shaft_len + 4.0)
    if hub_sweep_r + 1.4 > bolt_r - 0.5 * head_d - 1.0:
        return None                       # the clamp boss fouls the tie-bolt circle
    motor_pilot_d = min(0.55 * housing_od, 2.0 * (hub_sweep_r + 2.0))

    return dict(
        ring_root_r=ring_root_r, b_bore=b_bore, b_od=b_od, b_w=b_w,
        s_d=s_d, s_od=s_od, s_w=s_w, screw_d=screw_d, head_d=head_d,
        head_h=head_h, socket_af=socket_af, bolt_r=bolt_r,
        pin_d=pin_d, bush_t=bush_t, planet_bore=planet_bore,
        bush_flange_r=bush_flange_r, bush_flange_t=bush_flange_t,
        clip_t=clip_t, clip_groove_r=clip_groove_r, clip_out_r=clip_out_r,
        clip_gap=clip_gap, clip_z=-(bush_flange_t + clip_gap + clip_t),
        pin_ext=pin_ext, disc_t=disc_t, pin_circle_r=pin_circle_r,
        plate_r=plate_r, end_float=end_float, z_head0=z_head0,
        z_plate0=z_plate0, z_plate1=z_plate1,
        z_bear_a=z_bear_a, z_bear_b=z_bear_b, z_journal_end=z_journal_end,
        z_seal0=z_seal0, z_head1=z_head1, carrier_clr_r=carrier_clr_r,
        clamp_len=clamp_len, clamp_od=clamp_od,
        hub_boss_x=hub_boss_x, hub_boss_r=hub_boss_r,
        hub_slit_w=hub_slit_w, hub_boss_w=hub_boss_w,
        hub_sweep_r=hub_sweep_r,
        z_adapter0=z_adapter0, z_adapter1=z_adapter1,
        motor_pilot_d=motor_pilot_d,
    )


def ball_count(bore, od):
    """Ball complement, from the space available on the pitch circle. Comes out
    at 9 for a 6004, which is what a 6004 actually has."""
    r_i, r_o = 0.5 * bore, 0.5 * od
    span = r_o - r_i
    rp, rb = 0.5 * (r_i + r_o), 0.30 * span
    return max(7, min(10, int(math.pi * rp / (1.5 * rb))))


# --------------------------------------------------------------------- bodies

def _sun(module, z, width, shaft_d, shaft_len):
    """Sun gear cut on its own input shaft — one solid, per the category's body
    rule: they are keyed together and never move relative to each other."""
    gear = _gear_solid(module, z, width)
    shaft = _tube(0.5 * shaft_d, 0.0, width + shaft_len, -shaft_len)
    return gear.union(shaft)


def _planet(module, z, width, bore_d):
    return _gear_solid(module, z, width).faces(">Z").workplane().hole(bore_d)


def _planet_bushing(L):
    """Flanged plain bushing: the journal the planet actually turns on, and the
    flange that sets its axial position. One part instead of a bare bore plus two
    loose thrust washers — which is how this class is really built, and it saves
    2N bodies over the washer-pair construction."""
    sleeve = _tube(0.5 * L["planet_bore"] - _CLR * 0.25, 0.5 * L["pin_d"] + _CLR * 0.5,
                   L["face_width"])
    flange = _tube(L["bush_flange_r"], 0.5 * L["pin_d"] + _CLR * 0.5,
                   L["bush_flange_t"], -L["bush_flange_t"])
    return sleeve.union(flange)


def _retaining_ring(L):
    """DIN 471-style external circlip: a split annulus. The split has to have
    FINITE width — a profile whose ends meet at a point survives the boolean and
    then fails in tessellation as a knife edge."""
    ring = _tube(L["clip_out_r"], L["clip_groove_r"] + 0.05, L["clip_t"])
    slot_w = max(0.5, 0.30 * L["pin_d"])
    slot = (cq.Workplane("XY")
            .box(L["clip_out_r"] * 2.4, slot_w, L["clip_t"] * 3.0)
            .translate((L["clip_out_r"] * 1.2, 0.0, L["clip_t"] * 0.5)))
    return ring.cut(slot)


def _housing(module, z_ring, L, width, outer_d, face_t, n_screws,
             ring_phase=0.0):
    """Ring gear machined into the housing bore, not a pressed-in ring — one
    solid, as the reference cutaway shows. The rear wall closes the gear chamber
    and carries the motor adapter.

    The ring-gear cutter is blind at z = 0: it stops inside solid material, so it
    leaves an ordinary flat-bottomed bore rather than a face coplanar with
    anything, which is the difference between a clean cut and a sliver."""
    body = _tube(0.5 * outer_d, 0.0, width + face_t, -face_t)
    bore = _gear_solid(module, z_ring, width + 1.0, internal=True,
                       phase_deg=ring_phase)
    body = body.cut(bore)
    # central bore through the rear wall for the input clamping hub
    body = body.cut(_tube(0.5 * L["clamp_od"] + _CLR * 2.0, 0.0,
                          face_t + 1.0, -face_t - 0.5))
    # annular relief in the rear wall for the pin ends, the bushing flanges and
    # the circlips, all of which stand proud of z = 0
    relief = max(L["clip_out_r"], L["bush_flange_r"]) + 0.6
    body = body.cut(_tube(L["pin_circle_r"] + relief,
                          max(0.0, L["pin_circle_r"] - relief),
                          L["pin_ext"] + 0.6, -(L["pin_ext"] + 0.6)))
    # tie-bolt clearance holes, right through
    for k in range(int(n_screws)):
        a = 2.0 * math.pi * k / n_screws
        body = body.cut(_tube(0.5 * L["screw_d"] + 0.25, 0.0, width + face_t + 2.0,
                              -face_t - 1.0)
                        .translate((L["bolt_r"] * math.cos(a),
                                    L["bolt_r"] * math.sin(a), 0.0)))
    return body


def _carrier(L, n_planets, output_shaft_d, output_shaft_len):
    """Disc-design carrier: ONE plate on the output side, the planet pins
    cantilevered from it, the bearing journal and the output shaft — all one
    body, since nothing here moves relative to anything else here.

    A plate on both sides would box the gear train in. Neugart calls this
    "planet carrier in disc design" and the reference cutaway shows the planets
    open on the input side."""
    plate = _tube(L["plate_r"], 0.0, L["disc_t"], L["z_plate0"])
    result = plate
    for k in range(int(n_planets)):
        a = 2.0 * math.pi * k / n_planets
        pin = _tube(0.5 * L["pin_d"], 0.0,
                    L["face_width"] + L["disc_t"] + L["pin_ext"], -L["pin_ext"])
        # the circlip groove, cut with a cutter that over-runs the pin surface
        groove = _tube(0.5 * L["pin_d"] + 0.6, L["clip_groove_r"], L["clip_t"],
                       L["clip_z"])
        pin = pin.cut(groove)
        result = result.union(
            pin.translate((L["pin_circle_r"] * math.cos(a),
                           L["pin_circle_r"] * math.sin(a), 0.0)))
    # There is deliberately NO hub on the gear side: the sun occupies that axis.
    # A carrier hub running back to z = 0 swallows the sun gear whole, which is
    # invisible in every view and shows up only as interfering solids.
    # journal for the two output bearings, then a shoulder down to the shaft.
    # The journal OVERLAPS the plate by 0.4 mm on purpose: a fusion interface
    # that is exactly coplanar has zero volume and OCC may or may not keep it.
    journal = _tube(0.5 * L["b_bore"], 0.0,
                    L["z_journal_end"] - L["z_plate1"] + 0.4, L["z_plate1"] - 0.4)
    shaft = _tube(0.5 * output_shaft_d, 0.0,
                  (L["z_head1"] + output_shaft_len) - L["z_journal_end"] + 0.4,
                  L["z_journal_end"] - 0.4)
    return result.union(journal).union(shaft)


def _bearing(L, z0):
    """Deep-groove ball bearing, ISO 15 / DIN 625-1 series 60, as three body
    kinds: inner ring, outer ring and the ball complement.

    The raceway grooves are cut with a torus of tube radius rb + 0.06*span, so
    the ball sits in the groove with a visible radial clearance. Cutting the
    groove at exactly the ball radius makes ball and raceway tangent, and tangent
    booleans in OCC 7.9 produce unstable or null faces."""
    r_i, r_o = 0.5 * L["b_bore"], 0.5 * L["b_od"]
    span = r_o - r_i
    rp, rb, w = 0.5 * (r_i + r_o), 0.30 * span, L["b_w"]
    inner = _tube(r_i + 0.32 * span, r_i, w, z0)
    outer = _tube(r_o, r_o - 0.32 * span, w, z0)
    groove = cq.Workplane("XY").add(
        cq.Solid.makeTorus(rp, rb + 0.06 * span).translate(
            cq.Vector(0.0, 0.0, z0 + 0.5 * w)))
    inner, outer = inner.cut(groove), outer.cut(groove)
    n = ball_count(L["b_bore"], L["b_od"])
    balls = []
    for k in range(n):
        a = 2.0 * math.pi * k / n
        balls.append(cq.Workplane("XY").sphere(rb).translate(
            (rp * math.cos(a), rp * math.sin(a), z0 + 0.5 * w)))
    return inner, outer, balls


def _output_head(L, outer_d, n_screws, output_shaft_d):
    """Bearing head and machine mounting flange in one part: it carries both
    output bearing outer races, the seal, and the bolt pattern the gearhead is
    mounted by. It also replaces the solid end face the earlier revision had,
    which the carrier plate ran straight into.

    The bore steps monotonically down toward +Z -- carrier clearance, bearing
    seat, seal seat, shaft passage -- so the whole thing is borable from one
    end, and every cutter over-runs its end faces."""
    body = _tube(0.5 * outer_d, 0.0, L["z_head1"] - L["z_head0"], L["z_head0"])
    steps = [
        (L["carrier_clr_r"], L["z_head0"] - 0.5, L["z_bear_a"]),
        (0.5 * L["b_od"], L["z_bear_a"], L["z_seal0"]),
        (0.5 * L["s_od"], L["z_seal0"], L["z_seal0"] + L["s_w"]),
        (0.5 * output_shaft_d + _CLR, L["z_seal0"] + L["s_w"], L["z_head1"] + 0.5),
    ]
    for r, za, zb in steps:
        body = body.cut(_tube(r, 0.0, zb - za, za))
    # tie-bolt clearance + counterbore for the screw head
    for k in range(int(n_screws)):
        a = 2.0 * math.pi * k / n_screws
        x, y = L["bolt_r"] * math.cos(a), L["bolt_r"] * math.sin(a)
        body = body.cut(_tube(0.5 * L["screw_d"] + 0.25, 0.0,
                              L["z_head1"] - L["z_head0"] + 2.0, L["z_head0"] - 1.0)
                        .translate((x, y, 0.0)))
        body = body.cut(_tube(0.5 * L["head_d"] + 0.3, 0.0, L["head_h"] + 1.4,
                              L["z_head1"] - L["head_h"] - 1.2)
                        .translate((x, y, 0.0)))
    # machine mounting threads, offset half a pitch from the tie bolts
    for k in range(int(n_screws)):
        a = 2.0 * math.pi * (k + 0.5) / n_screws
        body = body.cut(_tube(0.5 * L["screw_d"], 0.0, 2.2 * L["screw_d"],
                              L["z_head1"] - 2.2 * L["screw_d"])
                        .translate((L["bolt_r"] * math.cos(a),
                                    L["bolt_r"] * math.sin(a), 0.0)))
    return body


def _seal(L, output_shaft_d):
    """DIN 3760 form A radial shaft seal, as its real section: an outer case that
    presses into the head, a web, and a lip that runs on the shaft.

    The lip has a finite land. Tapering it to a mathematical point survives the
    revolve and then fails in tessellation."""
    case = _tube(0.5 * L["s_od"], 0.5 * L["s_od"] - 0.10 * L["s_od"], L["s_w"],
                 L["z_seal0"])
    web = _tube(0.5 * L["s_od"] - 0.10 * L["s_od"] + 0.05, 0.5 * output_shaft_d + 0.9,
                0.35 * L["s_w"], L["z_seal0"])
    lip = _tube(0.5 * output_shaft_d + 1.1, 0.5 * output_shaft_d + _CLR * 0.5,
                0.55 * L["s_w"], L["z_seal0"] + 0.10 * L["s_w"])
    return case.union(web).union(lip)


def _adapter(L, outer_d, n_screws, sun_shaft_d):
    """Motor adapter: closes the gear chamber at -Z, centres the motor on the
    ring axis with a pilot recess, and carries the motor bolt pattern."""
    body = _tube(0.5 * outer_d, 0.0, L["z_adapter1"] - L["z_adapter0"], L["z_adapter0"])
    # coupling cavity, then the motor pilot recess opening rearward
    body = body.cut(_tube(L["hub_sweep_r"] + 0.6, 0.0,
                          (L["z_adapter1"] + 0.5) - (L["z_adapter0"] + 0.30 *
                          (L["z_adapter1"] - L["z_adapter0"])),
                          L["z_adapter0"] + 0.30 * (L["z_adapter1"] - L["z_adapter0"])))
    body = body.cut(_tube(0.5 * L["motor_pilot_d"], 0.0,
                          0.30 * (L["z_adapter1"] - L["z_adapter0"]) + 0.5,
                          L["z_adapter0"] - 0.5))
    for k in range(int(n_screws)):
        a = 2.0 * math.pi * k / n_screws
        body = body.cut(_tube(0.5 * L["screw_d"], 0.0,
                              L["z_adapter1"] - L["z_adapter0"] + 1.0,
                              L["z_adapter0"] - 0.5)
                        .translate((L["bolt_r"] * math.cos(a),
                                    L["bolt_r"] * math.sin(a), 0.0)))
    return body


def _clamp_hub(L, sun_shaft_d):
    """Input clamping hub: what the sun is actually driven through. The sun is
    deliberately NOT carried on its own bearing — a floating sun is how this
    class shares load between the planets — so the hub and the motor shaft are
    its only support, and modelling it is what makes the floating sun honest
    rather than an omission.

    Shape order matters. The boss is added BEFORE the slit and the slit passes
    through both, so the hub stays a single C-shaped body with two ears. Drilling
    the clamp screw down the axis instead of through the boss cuts the ring into
    three pieces — which `validate` reports only as an unexpected solid count."""
    z0 = L["z_adapter1"] - L["clamp_len"] - 1.0
    slit_w = L["hub_slit_w"]
    x_b = L["hub_boss_x"]
    boss_x0 = 0.5 * L["clamp_od"] - 0.4                     # overlaps the tube
    boss_l = L["hub_boss_r"] - boss_x0
    boss_w = L["hub_boss_w"]                                # across the slit

    hub = _tube(0.5 * L["clamp_od"], 0.5 * sun_shaft_d + _CLR * 0.5,
                L["clamp_len"], z0)
    hub = hub.union(cq.Workplane("XY")
                    .box(boss_l, boss_w, clamp_boss_h(L["screw_d"]))
                    .translate((boss_x0 + 0.5 * boss_l, 0.0,
                                z0 + 0.5 * L["clamp_len"])))
    # the slit must pass COMPLETELY through the wall and through the boss;
    # stopping it at the bore leaves a zero-width web
    hub = hub.cut(cq.Workplane("XY")
                  .box(2.0 * (L["hub_boss_r"] + 1.0), slit_w, L["clamp_len"] * 1.4)
                  .translate((L["hub_boss_r"] + 1.0, 0.0,
                              z0 + 0.5 * L["clamp_len"])))
    # clamp screw, through the boss and across the slit — not down the axis
    hub = hub.cut(cq.Workplane("XZ")
                  .circle(0.5 * L["screw_d"])
                  .extrude(boss_w * 1.5, both=True)
                  .translate((x_b, 0.0, z0 + 0.5 * L["clamp_len"])))
    return hub


def _screw(L, length):
    """ISO 4762 socket head cap screw. The head overlaps the shank by 0.3 mm so
    the fusion interface has volume rather than being a single coplanar face."""
    shank = _tube(0.5 * L["screw_d"], 0.0, length)
    head = _tube(0.5 * L["head_d"], 0.0, L["head_h"] + 0.3, length - 0.3)
    body = shank.union(head)
    socket = (cq.Workplane("XY")
              .polygon(6, L["socket_af"] / math.cos(math.pi / 6.0))
              .extrude(L["head_h"] * 0.7)
              .translate((0.0, 0.0, length + L["head_h"] - L["head_h"] * 0.7 + 0.3)))
    return body.cut(socket)


# ---------------------------------------------------------------------- build

def build(module, z_sun, z_planet, z_ring, n_planets, face_width, housing_od,
          housing_face_t, sun_shaft_d, sun_shaft_len, output_shaft_d,
          output_shaft_len, n_case_screws, n_output_balls, carrier_angle):
    L = layout(module, z_sun, z_planet, z_ring, n_planets, face_width, housing_od,
               housing_face_t, sun_shaft_d, sun_shaft_len, output_shaft_d,
               output_shaft_len)
    if L is None:
        raise ValueError("parameters do not describe a buildable gearhead; "
                         "spec.refine() is supposed to have rejected this draw")
    L["face_width"] = face_width
    n_screws = int(n_case_screws)

    result = cq.Assembly(name="planetary_gear_stage_inline")
    ring_phase, planet_phase = mesh_phase(z_sun, z_planet, z_ring)
    result.add(_housing(module, z_ring, L, face_width, housing_od, housing_face_t,
                        n_screws, ring_phase), name="housing_ring_gear")
    # The sun turns too. With the ring held, the carrier at `carrier_angle`
    # implies a sun at ratio * carrier_angle = (1 + z_ring/z_sun) * carrier_angle.
    # Leaving the sun still is not a still picture of the mechanism -- it is a
    # picture of the sun's teeth driven through the planets' teeth.
    sun_angle = carrier_angle * (1.0 + z_ring / float(z_sun))
    result.add(_sun(module, z_sun, face_width, sun_shaft_d, sun_shaft_len)
               .rotate((0, 0, 0), (0, 0, 1), sun_angle), name="sun_shaft")
    result.add(_adapter(L, housing_od, n_screws, sun_shaft_d), name="motor_adapter")
    result.add(_clamp_hub(L, sun_shaft_d), name="input_clamp_hub")
    result.add(_output_head(L, housing_od, n_screws, output_shaft_d),
               name="output_bearing_head")
    result.add(_seal(L, output_shaft_d), name="output_shaft_seal")

    carrier = _carrier(L, n_planets, output_shaft_d, output_shaft_len)
    result.add(carrier.rotate((0, 0, 0), (0, 0, 1), carrier_angle),
               name="carrier_output")

    planet = _planet(module, z_planet, face_width, L["planet_bore"])
    bushing = _planet_bushing(L)
    clip = _retaining_ring(L)
    for k in range(int(n_planets)):
        a = carrier_angle + 360.0 * k / n_planets
        ar = math.radians(a)
        px, py = L["pin_circle_r"] * math.cos(ar), L["pin_circle_r"] * math.sin(ar)
        # spin each planet so its teeth stay meshed with BOTH the sun and the
        # ring as the carrier turns -- see planet_spin() and mesh_phase()
        spin = planet_phase + planet_spin(z_sun, z_planet, z_ring, a)
        result.add(planet.rotate((0, 0, 0), (0, 0, 1), spin).translate((px, py, 0.0)),
                   name="planet_gear_%02d" % (k + 1))
        result.add(bushing.translate((px, py, 0.0)),
                   name="planet_bushing_%02d" % (k + 1))
        result.add(clip.rotate((0, 0, 0), (0, 0, 1), spin)
                   .translate((px, py, L["clip_z"])),
                   name="planet_retaining_ring_%02d" % (k + 1))

    ball_i = 0
    for j, z0 in enumerate((L["z_bear_a"], L["z_bear_b"])):
        inner, outer, balls = _bearing(L, z0)
        result.add(inner, name="output_bearing_inner_%02d" % (j + 1))
        result.add(outer, name="output_bearing_outer_%02d" % (j + 1))
        for b in balls:
            ball_i += 1
            result.add(b, name="output_bearing_ball_%02d" % ball_i)
    if ball_i != int(n_output_balls):
        raise ValueError("n_output_balls=%d but the two bearings hold %d"
                         % (int(n_output_balls), ball_i))

    screw_len = L["z_head1"] - L["head_h"] - L["z_adapter1"] - 0.6
    screw = _screw(L, screw_len)
    for k in range(n_screws):
        a = 2.0 * math.pi * k / n_screws
        result.add(screw.translate((L["bolt_r"] * math.cos(a),
                                    L["bolt_r"] * math.sin(a), L["z_adapter1"] + 0.3)),
                   name="case_screw_%02d" % (k + 1))
    return result
