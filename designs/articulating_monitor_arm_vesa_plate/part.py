"""articulating_monitor_arm_vesa_plate - the parametric part.

A VESA display-mount adapter plate: a flat rectangular plate carrying the four
standard VESA bolt holes (or outward adjustment slots), a central raised boss
that interfaces the monitor arm, and a central bore through the boss for the
arm fixing. Pattern sizes follow the VESA FDMI MIS-D/E/F interface standard.

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def _hole_centers(pattern_x, pattern_y):
    """The four VESA hole centres, at (+/-X/2, +/-Y/2)."""
    return [(sx * pattern_x / 2.0, sy * pattern_y / 2.0) for sx in (-1, 1) for sy in (-1, 1)]


def _slot_centers(pattern_x, pattern_y, slot_len):
    """Adjustment-slot centres: each slot starts at its VESA hole and runs
    OUTWARD (away from centre) by slot_len, so the slot centre sits half a
    slot-length outboard of the nominal hole."""
    return [
        (sx * (pattern_x / 2.0 + slot_len / 2.0), sy * pattern_y / 2.0)
        for sx in (-1, 1)
        for sy in (-1, 1)
    ]


def build(pattern_x, pattern_y, hole_d, plate_t, margin, boss_d, boss_h, bore_d, slotted, slot_len):
    outer_x = pattern_x + 2.0 * margin
    outer_y = pattern_y + 2.0 * margin

    result = cq.Workplane("XY").box(outer_x, outer_y, plate_t)

    # VESA fixing holes - round, or obround adjustment slots running outward
    top = result.faces(">Z").workplane()
    if slotted:
        result = (
            top.pushPoints(_slot_centers(pattern_x, pattern_y, slot_len))
            .slot2D(slot_len + hole_d, hole_d, 0)
            .cutThruAll()
        )
    else:
        result = top.pushPoints(_hole_centers(pattern_x, pattern_y)).circle(hole_d / 2.0).cutThruAll()

    # central arm-interface boss, then the arm fixing bore through boss + plate
    result = result.faces(">Z").workplane().circle(boss_d / 2.0).extrude(boss_h)
    result = result.faces(">Z").workplane().hole(bore_d)

    return result
