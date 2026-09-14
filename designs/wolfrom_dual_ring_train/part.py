"""Wolfrom train: fixed R1, rotating R2 output, and a floating carrier.

The involute profile helper is adapted from BenchCAD PR #185, commit
fc3a71fbbd9295a181d0db60822b68656ea14074 (MIT, copyright 2026 The BenchCAD
Authors; full notice in the repository LICENSE). Timing, motion and this
five-component train are implemented here. See NOTES.md for approximations.
"""

import math

import cadquery as cq

_PRESSURE_ANGLE = math.radians(20.0)
_FLANK_POINTS = 14
_BACKLASH = 0.08  # External circumferential relief / module; proportion.


def _inv(angle):
    return math.tan(angle) - angle


def _gear_profile(module, teeth, internal=False, phase_deg=0.0):
    """Sampled involute flanks; radial continuation below the base circle.

    Internal returns the cutter void, with inward teeth centred at phase_deg.
    Root joins are chordal approximations, not a rack-generated trochoid.
    """
    pitch_r = module * teeth / 2.0
    base_r = pitch_r * math.cos(_PRESSURE_ANGLE)
    root_r = pitch_r + 1.25 * module if internal else pitch_r - 1.25 * module
    tip_r = pitch_r - module if internal else pitch_r + module
    pitch = 2.0 * math.pi / teeth

    def half_at(radius):
        alpha_r = math.acos(min(1.0, base_r / max(radius, base_r)))
        half = math.pi / (2.0 * teeth) + _inv(_PRESSURE_ANGLE) - _inv(alpha_r)
        if internal:
            return math.pi / teeth - half
        return half - _BACKLASH * module / (2.0 * radius)

    radii = [root_r + (tip_r - root_r) * i / (_FLANK_POINTS - 1)
             for i in range(_FLANK_POINTS)]
    points = []
    for k in range(int(teeth)):
        centre = k * pitch + math.radians(phase_deg)
        for radius in radii:
            angle = centre - half_at(radius)
            points.append((radius * math.cos(angle), radius * math.sin(angle)))
        for j in range(1, 3):
            angle = centre - half_at(tip_r) + 2.0 * half_at(tip_r) * j / 3.0
            points.append((tip_r * math.cos(angle), tip_r * math.sin(angle)))
        for radius in reversed(radii):
            angle = centre + half_at(radius)
            points.append((radius * math.cos(angle), radius * math.sin(angle)))
    return points


def _gear(module, teeth, width, internal=False, phase_deg=0.0, z0=0.0):
    return (cq.Workplane("XY")
            .polyline(_gear_profile(module, teeth, internal, phase_deg)).close()
            .extrude(width).translate((0, 0, z0)))


def _tube(outer_r, inner_r, width, z0=0.0):
    result = cq.Workplane("XY").circle(outer_r)
    if inner_r > 0:
        result = result.circle(inner_r)
    return result.extrude(width).translate((0, 0, z0))


def _fuse(first, second):
    return cq.Workplane("XY").newObject([first.val().fuse(second.val())])


def _cut(shape, cutter):
    return cq.Workplane("XY").newObject([shape.val().cut(cutter.val())])


def _initial_phases(zs, za, zb, zr1, zr2, n):
    """Degrees, identical A/B clocking on every rigid stepped planet.

    Integer congruences avoid rounding close to a tooth-index boundary.
    See NOTES: n | 2D and n*gcd(za,zb) | D*(za+zb), D=zs+za.
    """
    d = zs + za
    if (2*d) % n or (d*(za+zb)) % (n*math.gcd(za, zb)):
        raise ValueError("no equal-spacing phase solution for identical stepped planets")
    planet0 = 180.0 - 180.0 / za
    ring1 = (za % 2) * 180.0 / zr1
    ring2 = ((0.5 + zb*planet0/360.0) % 1.0) * 360.0 / zr2
    planets = []
    for j in range(n):
        k = next(k for k in range(za)
                 if (d*(za+zb)*j + n*zb*k) % (n*za) == 0)
        planets.append((planet0 + 360.0*(d*j + n*k)/(n*za)) % 360.0)
    return ring1, ring2, planets


def _motion(zs, za, zb, zr1, zr2, input_angle):
    """Absolute carrier, planet spin, output angles from Willis equations."""
    carrier = input_angle * zs / (zs + zr1)
    planet = carrier * (1.0 - zr1 / za)
    output = carrier + (zb / zr2) * (planet - carrier)
    return carrier, planet, output


def build(module_m, row, sun_zs, step_a_za,
          step_b_zb, ring1_zr1, ring2_zr2,
          n_planets, width_b, gap_g, rim_t, input_deg):
    """Return the five component types listed in issue #187, as separate bodies."""
    m = module_m
    zs, za, zb, r1, r2, n = (int(x) for x in (
        sun_zs, step_a_za, step_b_zb,
        ring1_zr1, ring2_zr2, n_planets))
    if r1 != zs + 2*za or r2 != zs + za + zb or za == zb:
        raise ValueError("inconsistent coaxiality or coincident held/output rings")
    if not (0 <= row <= 3):
        raise ValueError("row is outside the issue's four-row ladder")
    ring1_phase, ring2_phase, planet_phases = _initial_phases(zs, za, zb, r1, r2, n)
    carrier_angle, planet_spin, output_angle = _motion(zs, za, zb, r1, r2, input_deg)
    b_z0 = width_b + gap_g
    gear_end = b_z0 + width_b
    orbit_r = m * (zs + za) / 2.0
    running_clearance = 0.20 * m
    axial_clearance = 0.25 * m
    pin_r = 0.20 * m * min(za, zb)
    bore_r = pin_r + running_clearance
    planet_root_r = m * min(za, zb) / 2.0 - 1.25*m
    shaft_r = 0.25 * m * zs
    plate_t = max(1.5*m, 0.30*width_b)
    plate_r = orbit_r + pin_r + 0.60*m
    plate_z0 = -axial_clearance - plate_t

    ring1 = _cut(_tube(m*r1/2.0 + 1.25*m + rim_t, 0, width_b),
                 _gear(m, r1, width_b + 0.2*m, internal=True,
                       phase_deg=ring1_phase, z0=-0.1*m))
    ring2 = _cut(_tube(m*r2/2.0 + 1.25*m + rim_t, 0, width_b, b_z0),
                 _gear(m, r2, width_b + 0.2*m, internal=True,
                       phase_deg=ring2_phase + output_angle, z0=b_z0-0.1*m))
    sun = _fuse(_gear(m, zs, width_b, phase_deg=input_deg),
                _tube(shaft_r, 0, 8.0*m + width_b, -8.0*m))
    carrier = _tube(plate_r, shaft_r + running_clearance, plate_t, plate_z0)

    for j in range(n):
        theta = math.radians(carrier_angle + 360.0*j/n)
        px, py = orbit_r*math.cos(theta), orbit_r*math.sin(theta)
        # Pins overlap their own carrier plate only. Planet bores clear the pins.
        pin = _tube(pin_r, 0, gear_end-plate_z0+axial_clearance, plate_z0)
        carrier = _fuse(carrier, pin.translate((px, py, 0)))

    result = cq.Assembly(name="wolfrom_dual_ring_train")
    result.add(ring1, name="housing_ring1_fixed", color=cq.Color(0.28, 0.49, 0.78))
    result.add(ring2, name="output_ring2", color=cq.Color(0.59, 0.35, 0.80))
    result.add(sun, name="sun_shaft", color=cq.Color(0.95, 0.57, 0.13))
    result.add(carrier, name="carrier", color=cq.Color(0.20, 0.65, 0.43))
    for j in range(n):
        theta = math.radians(carrier_angle + 360.0*j/n)
        px, py = orbit_r*math.cos(theta), orbit_r*math.sin(theta)
        phase = planet_phases[j] + planet_spin
        planet = _fuse(_gear(m, za, width_b, phase_deg=phase),
                       _tube(0.70*planet_root_r, 0, gap_g, width_b))
        planet = _fuse(planet, _gear(m, zb, width_b, phase_deg=phase, z0=b_z0))
        planet = _cut(planet, _tube(bore_r, 0, gear_end+0.2*m, -0.1*m))
        result.add(planet.translate((px, py, 0)), name="stepped_planet_%02d" % (j+1),
                   color=cq.Color(0.93, 0.75, 0.20))
    return result
