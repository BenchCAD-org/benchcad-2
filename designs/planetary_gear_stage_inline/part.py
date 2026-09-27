"""Single-stage inline planetary gear stage for BenchCAD issue #182.

Only the four issue components are modelled:
1. housing_ring_gear: a thin annular ring with internal teeth;
2. sun_shaft: sun gear integral with its input shaft;
3. planet_gear: N separate rotating planet gears;
4. carrier_output: two discs, planet pins and output shaft as one rigid body.

No outer gearbox shell, covers, bearings, seals, flanges, adapters, bolts or
clamp hubs are included.
"""

import cadquery as cq
import math


_PRESSURE_ANGLE = math.radians(20.0)  # ISO 53 / DIN 867
_ADDENDUM = 1.0
_DEDENDUM = 1.25
_BACKLASH = 0.06
_FLANK_POINTS = 9


def _inv(angle):
    return math.tan(angle) - angle


def _external_half_angle(radius, base_radius, teeth):
    r = max(radius, base_radius * (1.0 + 1e-8))
    return math.pi / (2.0 * teeth) + _inv(_PRESSURE_ANGLE) - _inv(
        math.acos(min(1.0, base_radius / r))
    )


def _gear_outline(module, teeth, internal=False, phase_deg=0.0):
    """Closed all-tooth involute outline; internal form is the cutter void."""
    pitch_r = module * teeth / 2.0
    base_r = pitch_r * math.cos(_PRESSURE_ANGLE)
    tooth_pitch = 2.0 * math.pi / teeth
    phase = math.radians(phase_deg)

    if internal:
        root_r, tip_r = pitch_r + _DEDENDUM * module, pitch_r - _ADDENDUM * module

        def half_at(radius):
            return math.pi / teeth - _external_half_angle(radius, base_r, teeth)
    else:
        root_r = max(pitch_r - _DEDENDUM * module, 0.20 * pitch_r)
        tip_r = pitch_r + _ADDENDUM * module

        def half_at(radius):
            return _external_half_angle(radius, base_r, teeth) - (
                _BACKLASH * module / max(radius, 1e-8) / 2.0
            )

    radii = [
        root_r + (tip_r - root_r) * i / (_FLANK_POINTS - 1)
        for i in range(_FLANK_POINTS)
    ]
    pts = []
    for tooth in range(int(teeth)):
        centre = phase + tooth * tooth_pitch
        for radius in radii:
            a = centre - half_at(radius)
            pts.append((radius * math.cos(a), radius * math.sin(a)))
        for j in range(1, 3):
            a = centre - half_at(radii[-1]) + 2.0 * half_at(radii[-1]) * j / 3.0
            pts.append((radii[-1] * math.cos(a), radii[-1] * math.sin(a)))
        for radius in reversed(radii):
            a = centre + half_at(radius)
            pts.append((radius * math.cos(a), radius * math.sin(a)))
    return pts


def _gear(module, teeth, width, internal=False, phase_deg=0.0, z0=0.0):
    return (
        cq.Workplane("XY")
        .polyline(_gear_outline(module, int(teeth), internal, phase_deg))
        .close()
        .extrude(width)
        .translate((0.0, 0.0, z0))
    )


def _tube(outer_r, inner_r, length, z0=0.0):
    result = cq.Workplane("XY").circle(outer_r)
    if inner_r > 0.0:
        result = result.circle(inner_r)
    return result.extrude(length).translate((0.0, 0.0, z0))


def _mesh_phase(z_planet, z_ring):
    """A tooth phase that gives each planet a sun and ring mesh."""
    if int(z_planet) % 2 == 0:
        return 0.0, 180.0 - 180.0 / z_planet
    return 180.0 / z_ring, 0.0


def _check_kinematics(z_sun, z_planet, z_ring, n_planets):
    if int(z_ring) != int(z_sun) + 2 * int(z_planet):
        raise ValueError("z_ring must equal z_sun + 2*z_planet")
    if (int(z_sun) + int(z_ring)) % int(n_planets):
        raise ValueError("equal-pitch planet assembly condition is not satisfied")
    if (z_sun + z_planet) * math.sin(math.pi / n_planets) <= z_planet + 2:
        raise ValueError("neighbouring planet tip circles overlap")


def build(
    module,
    z_sun,
    z_planet,
    z_ring,
    n_planets,
    face_width,
    sun_shaft_d,
    sun_shaft_len,
    output_shaft_d,
    output_shaft_len,
    shaft_collar_d,
    key_w,
    key_len,
    center_hole_d,
    center_hole_depth,
    carrier_angle,
):
    _check_kinematics(z_sun, z_planet, z_ring, n_planets)
    n = int(n_planets)
    angle = float(carrier_angle)
    ring_phase, planet_phase = _mesh_phase(z_planet, z_ring)

    # The ring is deliberately only a rim around its teeth, not a gearbox case.
    ring_root_r = module * z_ring / 2.0 + _DEDENDUM * module
    rim_t = max(1.5 * module, 0.12 * module * z_ring)
    ring = _tube(ring_root_r + rim_t, 0.0, face_width)
    ring = ring.cut(_gear(module, z_ring, face_width + 0.4, True, ring_phase, -0.2))

    sun = _gear(module, z_sun, face_width)
    sun = sun.union(_tube(sun_shaft_d / 2.0, 0.0, sun_shaft_len, -sun_shaft_len))

    pin_circle_r = module * (z_sun + z_planet) / 2.0
    pin_d = max(2.0, 0.30 * module * z_planet)
    planet_bore_d = pin_d + max(0.8, 0.28 * pin_d)
    planet_root_r = module * z_planet / 2.0 - _DEDENDUM * module
    if planet_bore_d / 2.0 >= planet_root_r - 0.4:
        raise ValueError("planet pin bore breaks through the tooth roots")

    plate_t = max(1.5, 0.25 * face_width)
    plate_r = pin_circle_r + pin_d / 2.0 + max(0.8, 0.18 * pin_d)
    sun_clear_r = module * z_sun / 2.0 + _ADDENDUM * module + 0.8

    # The carrier is one component: input-side annular plate + output-side disc
    # + pins + output shaft. The two plates are on opposite gear faces.
    rear_disc = _tube(plate_r, sun_clear_r, plate_t, -plate_t)
    # The output-side carrier plate is a disc with three large inspection
    # windows. Its hub, radial webs and pin pads remain one rigid plate, but
    # the windows leave every planet visible from the output side.
    hub_r = max(shaft_collar_d / 2.0 + 0.6, sun_clear_r * 0.55)
    # An outer rim makes the three pin pads a single continuous disc even when
    # a CAD kernel refuses to fuse two merely tangent local webs.
    front_outer_band = _tube(
        plate_r,
        # A narrow rim only; its job is to join the three pin pads, not to
        # conceal the planet gears from the inspection side.
        plate_r - max(1.0, 0.45 * pin_d),
        plate_t,
        face_width,
    )
    front_disc = _tube(hub_r, 0.0, plate_t, face_width).union(front_outer_band)
    for i in range(n):
        web_angle = 2.0 * math.pi * i / n
        # Overlap both hub and pin pad by 0.3 mm. A face-only contact can
        # become separate solids in OCC at a different module/face width.
        web_start = hub_r - 0.3
        web_length = pin_circle_r + pin_d / 2.0 + 0.75 - web_start
        web = (
            cq.Workplane("XY")
            .box(web_length, pin_d + 1.0, plate_t)
            .translate((web_start + web_length / 2.0, 0.0, face_width + plate_t / 2.0))
            .rotate((0, 0, 0), (0, 0, 1), math.degrees(web_angle))
        )
        pad = _tube(pin_d / 2.0 + 0.55, 0.0, plate_t, face_width).translate((
            pin_circle_r * math.cos(web_angle), pin_circle_r * math.sin(web_angle), 0.0
        ))
        front_disc = front_disc.union(web).union(pad)
    shaft_z0 = face_width + plate_t - 0.2
    shaft = _tube(output_shaft_d / 2.0, 0.0, output_shaft_len + 0.2, shaft_z0)
    collar_len = max(2.0, min(0.20 * output_shaft_len, 0.45 * key_len))
    collar = _tube(shaft_collar_d / 2.0, 0.0, collar_len, shaft_z0)
    carrier = rear_disc.union(front_disc).union(shaft).union(collar)

    for i in range(n):
        orbit_deg = angle + 360.0 * i / n
        orbit = math.radians(orbit_deg)
        pin = _tube(pin_d / 2.0, 0.0, face_width + 2.0 * plate_t, -plate_t)
        carrier = carrier.union(pin.translate((
            pin_circle_r * math.cos(orbit), pin_circle_r * math.sin(orbit), 0.0
        )))

    key_h = max(1.0, 0.58 * key_w)
    key_z0 = shaft_z0 + collar_len + 0.4
    key_len_actual = min(key_len, shaft_z0 + output_shaft_len - key_z0)
    if key_len_actual > 0.5:
        key = (
            cq.Workplane("XY")
            .box(key_w, key_h, key_len_actual)
            .translate((0.0, output_shaft_d / 2.0 + key_h / 2.0 - 0.1,
                        key_z0 + key_len_actual / 2.0))
        )
        carrier = carrier.union(key)

    shaft_tip = shaft_z0 + output_shaft_len
    carrier = carrier.cut(_tube(center_hole_d / 2.0, 0.0, center_hole_depth + 0.2,
                                shaft_tip - center_hole_depth))

    result = cq.Assembly(name="planetary_gear_stage_inline")
    result.add(ring, name="housing_ring_gear", color=cq.Color(0.45, 0.65, 0.85, 0.34))
    sun_angle = angle * (1.0 + z_ring / float(z_sun))
    result.add(sun.rotate((0, 0, 0), (0, 0, 1), sun_angle),
               name="sun_shaft", color=cq.Color(0.96, 0.58, 0.12, 0.96))
    result.add(carrier.rotate((0, 0, 0), (0, 0, 1), angle),
               name="carrier_output", color=cq.Color(0.14, 0.70, 0.52, 0.88))

    planet = _gear(module, z_planet, face_width).faces(">Z").workplane().hole(planet_bore_d)
    for i in range(n):
        orbit_deg = angle + 360.0 * i / n
        orbit = math.radians(orbit_deg)
        spin = planet_phase - orbit_deg * (z_sun + z_planet) / float(z_planet)
        result.add(
            planet.rotate((0, 0, 0), (0, 0, 1), spin).translate((
                pin_circle_r * math.cos(orbit), pin_circle_r * math.sin(orbit), 0.0
            )),
            name="planet_gear_%02d" % (i + 1),
            color=cq.Color(0.92, 0.76, 0.15, 0.95),
        )
    return result
