"""round_duct_butterfly_damper — the parametric part.

A round HVAC manual balancing damper, drawn in the CLOSED position: a rolled
sheet-metal spool (annular frame) that slips into round duct, a circular
butterfly blade filling the bore, and a through-shaft on a diameter that carries
the blade and extends out one side for the locking hand quadrant. The shaft is
round, or a square axle (MDRS25 style). Airflow runs along the spool axis (Z).

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def build(duct_d, wall, frame_depth, blade_t, shaft_d, handle_ext, stub, square_shaft):
    outer_r = duct_d / 2.0
    bore_r = outer_r - wall

    # frame spool: annular sheet-metal tube along Z, centred at z=0
    result = cq.Workplane("XY").circle(outer_r).circle(bore_r).extrude(frame_depth / 2.0, both=True)

    # butterfly blade: a disc filling the bore, centred at mid-depth (closed)
    blade = cq.Workplane("XY").circle(bore_r).extrude(blade_t / 2.0, both=True)
    result = result.union(blade)

    # control shaft on a diameter (along X): bearing stub one side, handle
    # extension the other. Round rod, or a square axle.
    length = duct_d + stub + handle_ext
    if square_shaft:
        shaft = cq.Workplane("YZ").rect(shaft_d, shaft_d).extrude(length)
    else:
        shaft = cq.Workplane("YZ").circle(shaft_d / 2.0).extrude(length)
    shaft = shaft.translate((-(outer_r + stub), 0.0, 0.0))
    result = result.union(shaft)

    return result
