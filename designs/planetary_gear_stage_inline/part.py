"""planetary_gear_stage_inline — a single-stage inline planetary gear set.

Sun, N planets, an internal ring gear cut into the housing bore, and a carrier
that fuses its two discs, the planet pins and the output shaft into one rigid
body. Four body types; the only relative motion is a planet turning on its pin,
which is why the planets are the only repeated component.

The tooth flanks are true involutes generated from the standard basic rack
(DIN 867 / ISO 53: pressure angle 20 deg, addendum 1.0*m, dedendum 1.25*m), so
the geometry follows the standard rather than a table. The ring is generated as
the *space* form of the same involute and cut from the housing, which is what
makes its teeth mesh with the planets instead of merely looking like teeth.

Frame: the gear axis is Z, the stage stacks +Z from the housing face, and the
output shaft leaves +Z. `base_plane` is XY.
"""

import cadquery as cq
import math

_PRESSURE_ANGLE = 20.0     # deg, DIN 867 / ISO 53 basic rack
_ADDENDUM = 1.0            # x module, DIN 867
_DEDENDUM = 1.25           # x module, DIN 867
_FLANK_PTS = 14            # involute samples per flank
_TIP_PTS = 3               # samples across the tip land

# Proportions the standard does not fix (listed in NOTES.md).
_RIM = 0.16                # housing wall outside the ring root / ring pitch dia
_PIN_CLR = 0.12            # planet bore clearance over the pin / pin diameter
_CARRIER_T = 0.55          # carrier disc thickness / face width
_HUB = 1.9                 # carrier hub diameter / pin diameter


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


def _gear_profile(module, z, internal, alpha_deg=_PRESSURE_ANGLE):
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
        r_root = max(r_pitch - _DEDENDUM * module, r_base * 1.001)
    base_half = math.pi / (2.0 * z)
    pitch = 2.0 * math.pi / z

    def half_at(r):
        h = base_half + _half_angle(r, r_base, r_pitch, alpha)
        return (math.pi / z - h) if internal else h

    # radii from root to tip, along the working flank
    lo, hi = (min(r_tip, r_root), max(r_tip, r_root))
    radii = [lo + (hi - lo) * i / (_FLANK_PTS - 1) for i in range(_FLANK_PTS)]
    if internal:
        radii.reverse()                                # root (outer) -> tip (inner)

    pts = []
    for k in range(int(z)):
        c = k * pitch
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


def _gear_solid(module, z, width, internal=False):
    return (
        cq.Workplane("XY")
        .polyline(_gear_profile(module, z, internal))
        .close()
        .extrude(width)
    )


def _sun(module, z, width, shaft_d, shaft_len):
    """Sun gear cut on its own input shaft — one solid, per the category's body
    rule: they are keyed together and never move relative to each other."""
    gear = _gear_solid(module, z, width)
    shaft = (
        cq.Workplane("XY").circle(shaft_d / 2.0).extrude(width + shaft_len)
        .translate((0.0, 0.0, -shaft_len))
    )
    return gear.union(shaft)


def _planet(module, z, width, bore_d):
    return _gear_solid(module, z, width).faces(">Z").workplane().hole(bore_d)


def _housing(module, z_ring, width, outer_d, face_t):
    """Ring gear machined into the housing bore, not a pressed-in ring — one
    solid, as the reference cutaway shows."""
    body = cq.Workplane("XY").circle(outer_d / 2.0).extrude(width + face_t)
    bore = _gear_solid(module, z_ring, width + 2.0, internal=True).translate((0.0, 0.0, -1.0))
    return body.cut(bore)


def _carrier(pin_circle_r, n_planets, pin_d, width, disc_t, hub_d, out_d, out_len):
    """Disc-design carrier: ONE plate on the output side, the planet pins
    cantilevered from it, and the output shaft — all one body, since nothing
    here moves relative to anything else here.

    A plate on both sides would box the gear train in. Neugart calls this
    "planet carrier in disc design" and the reference cutaway shows the planets
    open on the input side; the reference carrier measures 25.1 across against a
    45.65 housing, i.e. a hub, not a lid."""
    # The pin must sit strictly INSIDE the plate rim. Making the plate exactly
    # tangent to the pin (plate_r == pin_circle_r + pin_d/2) leaves a zero-
    # thickness knife edge that OCC cannot tessellate — it fails late, in the
    # renderer, as `NbNodes` on a null triangulation.
    plate_r = pin_circle_r + pin_d / 2.0 + max(0.4, 0.10 * pin_d)
    result = (
        cq.Workplane("XY").circle(plate_r).extrude(disc_t).translate((0, 0, width))
    )
    for k in range(int(n_planets)):
        a = 2.0 * math.pi * k / n_planets
        result = result.union(
            cq.Workplane("XY").circle(pin_d / 2.0).extrude(width + disc_t)
            .translate((pin_circle_r * math.cos(a), pin_circle_r * math.sin(a), 0.0))
        )
    hub = cq.Workplane("XY").circle(hub_d / 2.0).extrude(width + disc_t)
    shaft = (
        cq.Workplane("XY").circle(out_d / 2.0).extrude(out_len)
        .translate((0.0, 0.0, width + disc_t))
    )
    return result.union(hub).union(shaft)


def build(module, z_sun, z_planet, z_ring, n_planets, face_width, housing_od,
          housing_face_t, sun_shaft_d, sun_shaft_len, output_shaft_d,
          output_shaft_len, carrier_angle):
    pin_circle_r = 0.5 * module * (z_sun + z_planet)     # sun+planet centre distance
    pin_d = max(2.0, 0.42 * module * z_planet)
    planet_bore = pin_d * (1.0 + _PIN_CLR)
    disc_t = _CARRIER_T * face_width

    housing = _housing(module, z_ring, face_width, housing_od, housing_face_t)
    sun = _sun(module, z_sun, face_width, sun_shaft_d, sun_shaft_len)
    carrier = _carrier(pin_circle_r, n_planets, pin_d, face_width, disc_t,
                       _HUB * pin_d, output_shaft_d, output_shaft_len)

    result = cq.Assembly(name="planetary_gear_stage_inline")
    result.add(housing, name="housing_ring_gear")
    result.add(sun, name="sun_shaft")
    result.add(carrier.rotate((0, 0, 0), (0, 0, 1), carrier_angle), name="carrier_output")

    planet = _planet(module, z_planet, face_width, planet_bore)
    for k in range(int(n_planets)):
        a = carrier_angle + 360.0 * k / n_planets
        ar = math.radians(a)
        # spin each planet so its teeth stay meshed with the sun as the carrier turns
        spin = -a * z_sun / z_planet
        result.add(
            planet.rotate((0, 0, 0), (0, 0, 1), spin)
            .translate((pin_circle_r * math.cos(ar), pin_circle_r * math.sin(ar), 0.0)),
            name="planet_gear_%02d" % (k + 1),
        )
    return result
