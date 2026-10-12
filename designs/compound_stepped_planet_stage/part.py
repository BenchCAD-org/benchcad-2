"""Single-ring compound stepped planetary stage for BenchCAD issue #186.

The two planet tooth sections are rigidly one part.  Step A meshes externally
with the sun; step B meshes internally with the one held ring.  This is not the
two-ring Wolfrom arrangement of issue #187.
"""

import math

import cadquery as cq


_PRESSURE_ANGLE = math.radians(20.0)  # ISO 53 / DIN 867
_ADDENDUM = 1.0
_DEDENDUM = 1.25
_BACKLASH = 0.06
_FLANK_POINTS = 9


def _frac(value):
    return value - math.floor(value)


def _involute(angle):
    return math.tan(angle) - angle


def _external_half_angle(radius, base_radius, teeth):
    radius = max(radius, base_radius * (1.0 + 1e-9))
    return (
        math.pi / (2.0 * teeth)
        + _involute(_PRESSURE_ANGLE)
        - _involute(math.acos(min(1.0, base_radius / radius)))
    )


def _gear_outline(module, teeth, internal=False, phase_deg=0.0):
    """Closed ISO 20-degree involute outline; internal form is a cutter void."""
    teeth = int(teeth)
    pitch_r = module * teeth / 2.0
    base_r = pitch_r * math.cos(_PRESSURE_ANGLE)
    tooth_pitch = 2.0 * math.pi / teeth
    phase = math.radians(phase_deg)

    if internal:
        root_r = pitch_r + _DEDENDUM * module
        tip_r = pitch_r - _ADDENDUM * module

        def half_at(radius):
            return math.pi / teeth - _external_half_angle(radius, base_r, teeth)
    else:
        root_r = max(pitch_r - _DEDENDUM * module, 0.20 * pitch_r)
        tip_r = pitch_r + _ADDENDUM * module

        def half_at(radius):
            return _external_half_angle(radius, base_r, teeth) - (
                _BACKLASH * module / (2.0 * max(radius, 1e-9))
            )

    radii = [
        root_r + (tip_r - root_r) * i / (_FLANK_POINTS - 1)
        for i in range(_FLANK_POINTS)
    ]
    points = []
    for tooth in range(teeth):
        centre = phase + tooth * tooth_pitch
        for radius in radii:
            angle = centre - half_at(radius)
            points.append((radius * math.cos(angle), radius * math.sin(angle)))
        for j in range(1, 3):
            angle = centre - half_at(radii[-1]) + 2.0 * half_at(radii[-1]) * j / 3.0
            points.append((radii[-1] * math.cos(angle), radii[-1] * math.sin(angle)))
        for radius in reversed(radii):
            angle = centre + half_at(radius)
            points.append((radius * math.cos(angle), radius * math.sin(angle)))
    return points


def _gear(module, teeth, width, z0=0.0, internal=False, phase_deg=0.0):
    return (
        cq.Workplane("XY")
        .polyline(_gear_outline(module, teeth, internal, phase_deg))
        .close()
        .extrude(width)
        .translate((0.0, 0.0, z0))
    )


def _tube(outer_radius, inner_radius, length, z0=0.0):
    result = cq.Workplane("XY").circle(outer_radius)
    if inner_radius > 0.0:
        result = result.circle(inner_radius)
    return result.extrude(length).translate((0.0, 0.0, z0))


def _fuse(*workplanes):
    """Fuse through Shape to support the pinned CadQuery/OCP combination."""
    result = workplanes[0].val()
    for workplane in workplanes[1:]:
        result = result.fuse(workplane.val())
    return cq.Workplane("XY").newObject([result])


def _cut(workplane, cutter):
    return cq.Workplane("XY").newObject([workplane.val().cut(cutter.val())])


def _timed_planet_phases(theta_deg, zs, za, zb, zr):
    """Solve both mesh phases using the issue #186 u_A + u_B = 1/2 rule."""
    pitch_s = 360.0 / zs
    pitch_a = 360.0 / za
    pitch_b = 360.0 / zb
    pitch_r = 360.0 / zr

    # Sun-to-planet is radial theta; planet-A-to-sun is theta + 180 degrees.
    u_sun = _frac(-theta_deg / pitch_s)
    phase_a = theta_deg + 180.0 + pitch_a * _frac(0.5 - u_sun)

    # The planet-B and internal-ring contact both face radially outward.
    u_ring = _frac(-theta_deg / pitch_r)
    phase_b = theta_deg + pitch_b * _frac(0.5 - u_ring)
    return phase_a, phase_b


def build(
    module,
    z_sun,
    z_step_a,
    z_step_b,
    z_ring,
    n_planets,
    tooth_width,
    interstep_gap,
    carrier_angle,
):
    """Return the named four-component issue #186 assembly."""
    zs, za, zb, zr, n = map(int, (z_sun, z_step_a, z_step_b, z_ring, n_planets))
    if zs + za != zr - zb:
        raise ValueError("coaxiality requires z_sun + z_step_a = z_ring - z_step_b")

    a_z0 = 0.0
    b_z0 = tooth_width + interstep_gap
    gear_end = b_z0 + tooth_width
    plate_t = max(2.5, 0.42 * tooth_width)

    sun_pitch_r = module * zs / 2.0
    a_pitch_r = module * za / 2.0
    b_pitch_r = module * zb / 2.0
    ring_pitch_r = module * zr / 2.0
    orbit_r = sun_pitch_r + a_pitch_r
    if abs(orbit_r - (ring_pitch_r - b_pitch_r)) > 1e-9:
        raise ValueError("step-A and step-B pitch circles are not coaxial")

    # Held internal ring exists only at station B.  For the nominal m=2,
    # z_ring=54 table row its outside diameter is 133 mm, as in Section B-B.
    ring_root_r = ring_pitch_r + _DEDENDUM * module
    rim_t = max(5.0 * module, 1.6 * module)
    ring = _tube(ring_root_r + rim_t, 0.0, tooth_width, b_z0)
    ring = _cut(ring, _gear(module, zr, tooth_width + 0.4, b_z0 - 0.2,
                             internal=True, phase_deg=0.0))

    sun_shaft_r = max(2.0 * module, 0.42 * sun_pitch_r)
    sun = _gear(module, zs, tooth_width, a_z0, phase_deg=0.0)
    sun = _fuse(sun, _tube(sun_shaft_r, 0.0, 14.0 * module + tooth_width,
                            -14.0 * module))
    sun = _cut(sun, _tube(max(module, 0.35 * sun_shaft_r), 0.0,
                           14.0 * module + 0.2, -14.0 * module - 0.1))

    pin_r = max(1.25 * module, 0.27 * module * zb)
    pin_bore_r = pin_r + 0.325 * module
    a_root_r = module * za / 2.0 - _DEDENDUM * module
    b_root_r = module * zb / 2.0 - _DEDENDUM * module
    if pin_bore_r >= min(a_root_r, b_root_r) - 0.175 * module:
        raise ValueError("planet pin bore reaches a tooth root")

    # Open carrier: a small centre hub, radial arms and planet pins.  Full
    # closing discs would hide the two toothed stations in every benchmark
    # view and would contradict the open Section B-B arrangement in #186.
    # The hollow axial spine still clears the independently rotating sun shaft.
    spine_outer_r = sun_shaft_r + module
    spine_inner_r = sun_shaft_r + 0.35 * module
    carrier_spine = _tube(spine_outer_r, spine_inner_r, gear_end + 2.0 * plate_t, -plate_t)
    hub_outer_r = spine_outer_r + 1.5 * module
    rear_hub = _tube(hub_outer_r, spine_inner_r, plate_t, -plate_t)
    front_hub = _tube(hub_outer_r, spine_inner_r, plate_t, gear_end)
    carrier = _fuse(carrier_spine, rear_hub, front_hub)

    for i in range(n):
        theta_deg = carrier_angle + 360.0 * i / n
        theta = math.radians(theta_deg)
        px, py = orbit_r * math.cos(theta), orbit_r * math.sin(theta)
        pin = _tube(pin_r, 0.0, gear_end + 2.0 * plate_t, -plate_t).translate((px, py, 0.0))
        carrier = _fuse(carrier, pin)

        web_start = hub_outer_r - 0.3 * module
        web_length = orbit_r + pin_r + 0.35 * module - web_start
        front_web = (
            cq.Workplane("XY")
            .box(web_length, 2.0 * pin_r + 0.65 * module, plate_t)
            .translate((web_start + web_length / 2.0, 0.0, gear_end + plate_t / 2.0))
            .rotate((0, 0, 0), (0, 0, 1), theta_deg)
        )
        rear_web = (
            cq.Workplane("XY")
            .box(web_length, 2.0 * pin_r + 0.65 * module, plate_t)
            .translate((web_start + web_length / 2.0, 0.0, -plate_t / 2.0))
            .rotate((0, 0, 0), (0, 0, 1), theta_deg)
        )
        rear_pad = _tube(pin_r + 0.45 * module, 0.0, plate_t, -plate_t).translate((px, py, 0.0))
        front_pad = _tube(pin_r + 0.45 * module, 0.0, plate_t, gear_end).translate((px, py, 0.0))
        carrier = _fuse(carrier, front_web, rear_web, rear_pad, front_pad)

    output_shaft_r = max(2.5 * module, 0.52 * sun_pitch_r)
    output_z0 = gear_end + plate_t - 0.075 * module
    carrier = _fuse(
        carrier,
        _tube(output_shaft_r, 0.0, 15.0 * module + 0.075 * module, output_z0),
        _tube(output_shaft_r + 1.5 * module, 0.0, 2.0 * module, output_z0),
    )

    result = cq.Assembly(name="compound_stepped_planet_stage")
    result.add(ring, name="housing_ring_gear", color=cq.Color(0.32, 0.64, 0.88, 0.34))
    result.add(sun, name="sun_shaft", color=cq.Color(0.97, 0.56, 0.10, 0.96))
    result.add(carrier, name="carrier_output", color=cq.Color(0.18, 0.76, 0.50, 0.62))

    for i in range(n):
        theta_deg = carrier_angle + 360.0 * i / n
        theta = math.radians(theta_deg)
        px, py = orbit_r * math.cos(theta), orbit_r * math.sin(theta)
        phase_a, phase_b = _timed_planet_phases(theta_deg, zs, za, zb, zr)
        step_a = _gear(module, za, tooth_width, a_z0, phase_deg=phase_a)
        step_b = _gear(module, zb, tooth_width, b_z0, phase_deg=phase_b)
        spacer = _tube(max(a_root_r, b_root_r) * 0.70, 0.0, interstep_gap, tooth_width)
        planet = _fuse(step_a, spacer, step_b)
        planet = _cut(planet, _tube(pin_bore_r, 0.0, gear_end + 0.4, -0.2))
        result.add(planet.translate((px, py, 0.0)), name="stepped_planet_%02d" % (i + 1),
                   color=cq.Color(0.94, 0.78, 0.12, 0.96))
    return result
