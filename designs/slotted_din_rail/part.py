"""slotted_din_rail_th35_7_5 -- parametric CadQuery model.

EN 60715 TH35 top-hat rail, AutomationDirect DN-R35S slotted precut.

It is roll-formed from one 1.0 mm strip, so it is modelled that way: the section
is drawn ONCE as the sheet's centreline, rounded at each of the four bends, and
offset by half the thickness to both sides. That gives a single closed section of
genuinely constant thickness which is then extruded to length and slotted.

The earlier revision unioned six boxes instead. That produced perfectly sharp
inside-and-outside corners at all four bends, and across the diagonal at a bend
the material measured ~1.4 mm instead of 1.0 -- a box union cannot hold sheet
thickness through a corner.

The flange edges are BARE. EN 60715 ends each 35 mm flange on the plain sheet
edge, and it has to: a device clip grabs the flange from above and below, so a
downturned return lip at the edge would stop the clip seating at all. An earlier
revision unioned such a lip under a `side_relief` flag that was tier-locked
(easy 0, hard 1), so two of the three difficulty tiers rendered a part the
catalogue does not sell.
"""

import math

import cadquery as cq

# Inside bend radius as a multiple of sheet thickness. Roll-formed mild steel at
# this gauge is bent on roughly a 1t inside radius; the DN-R35S sheet draws the
# radii but does not dimension them, so this is a documented proportion.
_BEND_R = 1.0


def build(rail_length, rail_width, rail_height, rail_thickness, slot_width,
          slot_length, slot_count, profile_inner_width, slot_pitch):
    result = _rail_body(rail_length, rail_width, rail_height, rail_thickness,
                        profile_inner_width)

    centers = _slot_centers(slot_count, slot_pitch)
    if centers:
        result = (
            result.faces("<Z").workplane(origin=(0, 0, 0))
            .pushPoints([(x, 0.0) for x in centers])
            .slot2D(slot_length, slot_width, 0)
            .cutThruAll()
        )
    return result


def _rail_body(rail_length, rail_width, rail_height, rail_thickness,
               profile_inner_width):
    """The roll-formed section, extruded to length.

    Centreline of the strip, left flange tip round to right flange tip:

        (-W/2, H-t/2) -- (-(wi+t)/2, H-t/2) -- (-(wi+t)/2, t/2)
                      -- ((wi+t)/2, t/2) -- ((wi+t)/2, H-t/2) -- (W/2, H-t/2)

    so the web spans z 0..t, the walls stand `profile_inner_width` apart on their
    INNER faces, and the flange tips land on the overall width."""
    t = rail_thickness
    y_wall = profile_inner_width / 2.0 + t / 2.0
    z_web = t / 2.0
    z_flange = rail_height - t / 2.0
    # pull the centreline ends in by half the thickness: the offset rounds each
    # flange tip with a t/2 semicircle, so the ENVELOPE then lands exactly on the
    # catalogue 35.0 rather than 35.0 + t
    y_tip = rail_width / 2.0 - t / 2.0
    pts = [(-y_tip, z_flange), (-y_wall, z_flange), (-y_wall, z_web),
           (y_wall, z_web), (y_wall, z_flange), (y_tip, z_flange)]

    section = _rounded_path(cq.Workplane("YZ"), pts, _BEND_R * t + t / 2.0)
    # offset the open centreline to both sides: one closed, constant-thickness
    # band. `.extrude` directly on the offset result — calling `toPending()` on
    # it as well adds the same wire twice and doubles the solid.
    return section.offset2D(t / 2.0, kind="arc").extrude(rail_length)


def _rounded_path(wp, pts, radius):
    """Open polyline through `pts` with a tangent arc of `radius` at every
    interior vertex — the sheet's neutral line through each bend."""
    wp = wp.moveTo(*pts[0])
    for i in range(1, len(pts) - 1):
        prev, cur, nxt = pts[i - 1], pts[i], pts[i + 1]
        a = _unit(cur, prev)          # back along the incoming leg
        b = _unit(cur, nxt)           # forward along the outgoing leg
        cosang = max(-1.0, min(1.0, a[0] * b[0] + a[1] * b[1]))
        half = math.acos(cosang) / 2.0
        setback = radius / math.tan(half)
        start = (cur[0] + a[0] * setback, cur[1] + a[1] * setback)
        end = (cur[0] + b[0] * setback, cur[1] + b[1] * setback)
        cross = a[0] * b[1] - a[1] * b[0]
        wp = wp.lineTo(*start).radiusArc(end, radius if cross < 0 else -radius)
    return wp.lineTo(*pts[-1])


def _unit(frm, to):
    dx, dy = to[0] - frm[0], to[1] - frm[1]
    d = math.hypot(dx, dy)
    return (dx / d, dy / d)


def _slot_centers(slot_count, slot_pitch):
    count = int(slot_count)
    if count <= 0:
        return []
    span = (count - 1) * slot_pitch
    return [(-span / 2.0) + i * slot_pitch for i in range(count)]
