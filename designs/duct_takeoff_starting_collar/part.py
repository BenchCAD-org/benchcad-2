"""duct_takeoff_starting_collar — the parametric part.

A round-duct takeoff / starting collar: a short galvanized sheet-metal round
collar (barrel) that starts a round branch off a plenum or main duct. A rolled
bead stiffens the top (slip-fit) end, the base carries a ring of trapezoidal
tabs that bend flat onto the duct, and an optional butterfly damper sits on a
diametral shaft inside the barrel. The barrel axis is Z; the tabs lie in the
mounting plane at z=0.

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def _tab_angles(count):
    """Angular position (deg) of each base tab."""
    return [360.0 * i / count for i in range(count)]


def build(collar_d, collar_h, wall, bead_proj, tab_h, tab_w, tab_count, damper):
    r_out = collar_d / 2.0
    r_in = r_out - wall

    # straight collar barrel (annular tube) along Z, z in [0, collar_h]
    result = cq.Workplane("XY").circle(r_out).circle(r_in).extrude(collar_h)

    # rolled bead: an outward stiffening rib around the slip-fit (top) end
    bead_h = wall * 4.0
    bead = (
        cq.Workplane("XY")
        .circle(r_out + bead_proj)
        .circle(r_in)
        .extrude(bead_h)
        .translate((0.0, 0.0, collar_h - bead_h))
    )
    result = result.union(bead)

    # base tabs: flat trapezoidal tabs bent out into the mounting plane
    for ang in _tab_angles(tab_count):
        tab = (
            cq.Workplane("XY")
            .box(tab_h, tab_w, wall)
            .translate((r_out + tab_h / 2.0 - wall, 0.0, wall / 2.0))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), ang)
        )
        result = result.union(tab)

    # optional butterfly damper: a blade disc on a diametral shaft, mid-barrel
    if damper:
        z_mid = collar_h / 2.0
        blade = cq.Workplane("XY").circle(r_in).extrude(wall, both=True).translate((0.0, 0.0, z_mid))
        shaft_l = collar_d + 20.0
        shaft = cq.Workplane("YZ").circle(3.0).extrude(shaft_l).translate((-shaft_l / 2.0, 0.0, z_mid))
        result = result.union(blade).union(shaft)

    return result
