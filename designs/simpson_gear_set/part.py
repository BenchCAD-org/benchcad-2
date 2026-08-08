"""simpson_gear_set — two simple planetary stages on ONE sun, coupled.

The Simpson set is not "two copies of #182". Two ordinary planetary stages share
a single sun, and the front carrier is bolted to the rear ring — that one coupling
is what turns two ordinary stages into a multi-ratio set, and it is modelled here
as it is built: `carrier1_ring2_output` is a SINGLE solid carrying the stage-1
carrier plate, its planet pins, the stage-2 ring teeth on the inside of a drum,
and the output flange.

Frame: the gear axis is Z, the set stacks +Z.

    [-in]       ring 1 input flange, sun drum
    [0, b]      stage 1 — sun, n1 planets, ring 1
    [b, b+tc]   carrier 1 plate (annulus; the sun passes through it)
    gap         the output drum only
    stage 2     sun, n2 planets, ring 2 = teeth inside that same drum
    [+tc]       carrier 2 plate, the reaction member
    [+hub]      carrier 2 hub on the axis

Members leave in directions that cannot collide: the sun and ring 1 to -Z (axis
and rim), the output flange and the carrier-2 hub to +Z (rim and axis). A real
Simpson gearbox routes all four through concentric drums nested inside one
another; that is a gearbox, and this family is the gear set.

Tooth flanks are true involutes from the DIN 867 basic rack, with the root run to
the TRUE dedendum circle — below 17 teeth at 20 deg the base circle sits above it,
and clamping the root there leaves the tooth space too shallow and drives every
mating tip into solid metal.
"""

import math

import cadquery as cq

_PRESSURE_ANGLE = 20.0     # deg, DIN 867 / ISO 53 basic rack
_ADDENDUM = 1.0            # x module, DIN 867
_DEDENDUM = 1.25           # x module, DIN 867
_FLANK_PTS = 14            # involute samples per flank
_TIP_PTS = 3               # samples across the tip land
_BACKLASH = 0.08           # circumferential backlash, x module, off the externals

# Proportions the standard does not fix (listed in NOTES.md).
_PIN_D = 0.34              # planet pin diameter / (module * z_planet)
_PLATE_T = 0.55            # carrier plate thickness / face width
_RIM = 0.16                # drum wall outside the ring root / ring pitch diameter
_CLR = 0.25                # running clearance, mm
_GAP = 0.35                # axial clearance between members, mm


def _inv(a):
    return math.tan(a) - a


def _half_angle(r, r_base, alpha):
    if r <= r_base:
        r = r_base * (1.0 + 1e-9)
    return _inv(alpha) - _inv(math.acos(min(1.0, r_base / r)))


def _gear_profile(module, z, internal, phase_deg=0.0):
    alpha = math.radians(_PRESSURE_ANGLE)
    r_pitch = 0.5 * module * z
    r_base = r_pitch * math.cos(alpha)
    if internal:
        r_tip, r_root = r_pitch - _ADDENDUM * module, r_pitch + _DEDENDUM * module
    else:
        r_tip = r_pitch + _ADDENDUM * module
        r_root = max(r_pitch - _DEDENDUM * module, 0.15 * r_pitch)
    base_half = math.pi / (2.0 * z)

    def half_at(r):
        h = base_half + _half_angle(r, r_base, alpha)
        if internal:
            return math.pi / z - h
        return h - 0.5 * _BACKLASH * module / max(r, 1e-6)

    lo, hi = min(r_tip, r_root), max(r_tip, r_root)
    radii = [lo + (hi - lo) * i / (_FLANK_PTS - 1) for i in range(_FLANK_PTS)]
    if internal:
        radii.reverse()
    pts, pitch, ph = [], 2.0 * math.pi / z, math.radians(phase_deg)
    for k in range(int(z)):
        c = k * pitch + ph
        for r in radii:
            a = c - half_at(r)
            pts.append((r * math.cos(a), r * math.sin(a)))
        th = half_at(radii[-1])
        for i in range(1, _TIP_PTS):
            a = c - th + 2.0 * th * i / _TIP_PTS
            pts.append((radii[-1] * math.cos(a), radii[-1] * math.sin(a)))
        for r in reversed(radii):
            a = c + half_at(r)
            pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def _gear_solid(module, z, width, z0=0.0, internal=False, phase_deg=0.0):
    return (
        cq.Workplane("XY")
        .polyline(_gear_profile(module, z, internal, phase_deg))
        .close()
        .extrude(width)
        .translate((0.0, 0.0, z0))
    )


def mesh_phase(z_planet, z_ring):
    """Phases that let a planet mesh the sun AND its ring at once, given a sun
    with a tooth centred at angle 0.

    Both forms put a tooth centre at 0, so a planet on the +X axis needs a space
    facing the sun (local 180) and a space facing the ring (local 0) — and both
    are space centres only when z_planet is EVEN. For an odd planet the RING
    takes a half-pitch shift instead.

    Each stage has its OWN ring, so the shared sun costs nothing here: stage 2
    picks its phases independently of stage 1."""
    if int(z_planet) % 2 == 0:
        return 0.0, 180.0 - 180.0 / z_planet
    return 180.0 / z_ring, 0.0


def member_angles(z_sun, z_p1, z_p2, out_deg):
    """Absolute angle of every member for a given OUTPUT angle, in 1st gear —
    ring 1 driving, carrier 2 held, carrier 1 (= ring 2) the output.

    Solved from the mesh relations rather than tabulated, and the resulting input
    angle equals the closed form (z_r1 + z_r2 + z_sun)/z_r1 exactly."""
    z_r1, z_r2 = z_sun + 2 * z_p1, z_sun + 2 * z_p2
    a_out = float(out_deg)
    a_sun = -a_out * z_r2 / z_sun                       # stage 2, carrier 2 held
    a_p2 = a_out * z_r2 / z_p2
    a_p1 = a_out - (z_sun / z_p1) * (a_sun - a_out)     # stage 1, carrier 1 = out
    a_r1 = a_out + (z_p1 / z_r1) * (a_p1 - a_out)
    return dict(sun=a_sun, p1=a_p1, p2=a_p2, r1=a_r1, c1=a_out, c2=0.0)


def _planet_angle(z_sun, z_planet, phase, a_sun, psi):
    """A planet at carrier position `psi` meshing a sun at absolute angle
    `a_sun`: in the carrier frame the sun mesh fixes it outright."""
    return phase + psi - (z_sun / z_planet) * (a_sun - psi)


def _tube(r_out, r_in, length, z0=0.0):
    w = cq.Workplane("XY").circle(r_out)
    if r_in > 0.0:
        w = w.circle(r_in)
    return w.extrude(length).translate((0.0, 0.0, z0))


def build(module, z_sun, z_planet1, z_planet2, z_ring1, z_ring2,
          n_planets1, n_planets2, face_width, stage_gap,
          input_len, output_len, output_angle):
    b = face_width
    tc = _PLATE_T * b
    r_sun_tip = 0.5 * module * z_sun + _ADDENDUM * module
    a1 = 0.5 * module * (z_sun + z_planet1)
    a2 = 0.5 * module * (z_sun + z_planet2)
    pin1 = max(2.0, _PIN_D * module * z_planet1)
    pin2 = max(2.0, _PIN_D * module * z_planet2)
    r_r1_root = 0.5 * module * z_ring1 + _DEDENDUM * module
    r_r2_root = 0.5 * module * z_ring2 + _DEDENDUM * module
    r_drum = r_r2_root + _RIM * module * z_ring2
    r_ring1_out = r_r1_root + _RIM * module * z_ring1

    z_s1 = 0.0                                   # stage 1 gears
    z_c1 = b + _GAP                              # carrier 1 plate
    z_s2 = z_c1 + tc + stage_gap                 # stage 2 gears
    z_c2 = z_s2 + b + _GAP                       # carrier 2 plate

    ph_r1, ph_p1 = mesh_phase(z_planet1, z_ring1)
    ph_r2, ph_p2 = mesh_phase(z_planet2, z_ring2)
    ang = member_angles(z_sun, z_planet1, z_planet2, output_angle)

    def spin(shape, deg):
        return shape.rotate((0, 0, 0), (0, 0, 1), deg)

    # ── the common sun: ONE piece, teeth at both stations, drum out -Z ────────
    r_sun_root = max(0.5 * module * z_sun - _DEDENDUM * module, 0.15 * module * z_sun)
    sun = _tube(r_sun_root, 0.0, (z_s2 + b) - (-input_len), -input_len)
    sun = sun.union(_gear_solid(module, z_sun, b, z_s1))
    sun = sun.union(_gear_solid(module, z_sun, b, z_s2))
    sun = spin(sun, ang["sun"])

    # ── ring 1, the input: drum with internal teeth over stage 1 ─────────────
    ring1 = _tube(r_ring1_out, r_r1_root, b + tc, z_s1 - tc)
    ring1 = ring1.union(_tube(r_ring1_out, r_sun_tip + _CLR, tc, -input_len))
    ring1 = ring1.union(_tube(r_r1_root, r_sun_tip + _CLR, input_len - tc,
                              -input_len + tc))
    ring1 = ring1.cut(_gear_solid(module, z_ring1, b + 2.0, z_s1 - 1.0,
                                  internal=True, phase_deg=ph_r1))
    ring1 = spin(ring1, ang["r1"])

    # ── carrier 1 ≡ ring 2 ≡ output: ONE solid. THIS is the family ───────────
    out = _tube(r_drum, r_sun_tip + _CLR, tc, z_c1)                  # carrier 1 plate
    for k in range(int(n_planets1)):                                  # its planet pins
        t = 2.0 * math.pi * k / n_planets1
        out = out.union(_tube(0.5 * pin1, 0.0, b + _GAP + tc, z_s1)
                        .translate((a1 * math.cos(t), a1 * math.sin(t), 0.0)))
    out = out.union(_tube(r_drum, r_r2_root, (z_c2 + tc) - (z_c1 + tc), z_c1 + tc))
    out = out.cut(_gear_solid(module, z_ring2, b + 2.0, z_s2 - 1.0,      # ring 2 teeth
                              internal=True, phase_deg=ph_r2))
    r_flange = r_drum + _RIM * module * z_ring2
    out = out.union(_tube(r_flange, r_r2_root, tc, z_c2 + tc))        # output flange
    out = out.union(_tube(r_drum, r_drum - 2.0 * _RIM * module * z_ring2,
                          output_len, z_c2 + tc))
    out = spin(out, ang["c1"])

    # ── carrier 2, the reaction member ───────────────────────────────────────
    c2 = _tube(r_r2_root - _CLR, r_sun_tip + _CLR, tc, z_c2)
    for k in range(int(n_planets2)):
        t = 2.0 * math.pi * k / n_planets2
        c2 = c2.union(_tube(0.5 * pin2, 0.0, b + _GAP + tc, z_s2)
                      .translate((a2 * math.cos(t), a2 * math.sin(t), 0.0)))
    c2 = c2.union(_tube(r_sun_tip + _CLR + 2.0 * module, 0.0, tc, z_c2 + tc))
    c2 = spin(c2, ang["c2"])

    result = cq.Assembly(name="simpson_gear_set")
    result.add(sun, name="common_sun_shell")
    result.add(ring1, name="ring1_input")
    result.add(out, name="carrier1_ring2_output")
    result.add(c2, name="carrier2_reaction")

    for tag, (zp, zr, n, a_pin, pin_d, z0, ph, key) in enumerate((
        (z_planet1, z_ring1, n_planets1, a1, pin1, z_s1, ph_p1, "p1"),
        (z_planet2, z_ring2, n_planets2, a2, pin2, z_s2, ph_p2, "p2"),
    )):
        carrier_ang = ang["c1"] if key == "p1" else ang["c2"]
        blank = _gear_solid(module, zp, b, z0).cut(
            _tube(0.5 * pin_d * (1.0 + 0.18), 0.0, b + 2.0, z0 - 1.0))
        for k in range(int(n)):
            psi = carrier_ang + 360.0 * k / n
            r = math.radians(psi)
            result.add(
                spin(blank, _planet_angle(z_sun, zp, ph, ang["sun"], psi))
                .translate((a_pin * math.cos(r), a_pin * math.sin(r), 0.0)),
                name="planet%d_%02d" % (tag + 1, k + 1),
            )
    return result
