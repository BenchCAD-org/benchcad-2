"""Demo assembly for `bench2 preview-parts` — a pillow-block-style unit.

Four named instances across three semantic components (block, bushing,
bolt x2), a nested sub-assembly with its own Location, a translated AND
rotated repeated instance — every feature the preview-parts naming
contract covers, in one small readable part.
"""

import cadquery as cq


def build(block_w, block_t, bore_d, bolt_d, bolt_pitch):
    block = (
        cq.Workplane("XY")
        .box(block_w, block_w * 0.62, block_t)
        .edges("|Z")
        .fillet(block_w * 0.08)
        .faces(">Z")
        .workplane()
        .hole(bore_d + 1.0)
        .faces(">Z")
        .workplane()
        .pushPoints([(-bolt_pitch / 2, 0), (bolt_pitch / 2, 0)])
        .cboreHole(bolt_d + 0.6, bolt_d * 1.9, bolt_d * 0.65)
    )
    flange_d = bore_d + 6.0
    bushing = (
        cq.Workplane("XY")
        .circle(bore_d / 2)
        .extrude(block_t + 3.0)
        .faces(">Z")
        .workplane()
        .circle(flange_d / 2)
        .extrude(2.5)
        .faces(">Z")
        .workplane()
        .hole(bore_d - 3.0)
    )
    shaft_len = block_t * 0.75
    bolt = (
        cq.Workplane("XY")
        .circle(bolt_d / 2)
        .extrude(shaft_len)
        .faces(">Z")
        .workplane()
        .polygon(6, bolt_d * 1.7)
        .extrude(bolt_d * 0.6)
    )

    # pose the components the way the real unit assembles, and keep them
    # visible: the bushing flange sits proud of the top face, the bolt heads
    # ride 1 mm above it (bolt_02 turned 30 deg so the rotation is legible)
    result = cq.Assembly(name="preview_parts_demo")
    result.add(block, name="block")
    result.add(bushing, name="bushing", loc=cq.Location((0, 0, -block_t / 2)))
    bolts = cq.Assembly(name="bolts", loc=cq.Location((0, 0, block_t / 2 - shaft_len + 1.0)))
    bolts.add(bolt, name="bolt_01", loc=cq.Location((-bolt_pitch / 2, 0, 0)))
    bolts.add(bolt, name="bolt_02", loc=cq.Location((bolt_pitch / 2, 0, 0), (0, 0, 1), 30))
    result.add(bolts)
    return result
