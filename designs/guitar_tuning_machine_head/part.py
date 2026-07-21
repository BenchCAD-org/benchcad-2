"""guitar_tuning_machine_head — the parametric part.

A sealed geared guitar tuning machine (Grover Rotomatic style): a baseplate that
sits against the headstock rear, a sealed gear housing behind it, a string post
standing up through the peg-hole with a press-in bushing collar at its base, a
worm/key shaft out the side of the housing, and a small locating-screw hole in
the baseplate. Built in one piece (as cast + assembled), a single solid.

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def build(baseplate_l, baseplate_w, plate_t, housing_w, housing_h,
          post_d, post_h, bushing_od, worm_d, mount_d, worm_both_sides):
    # baseplate against the headstock, centred at z=0
    result = cq.Workplane("XY").box(baseplate_l, baseplate_w, plate_t)

    # sealed gear housing behind the baseplate (-Z)
    result = result.union(
        cq.Workplane("XY").box(housing_w, baseplate_w * 0.85, housing_h)
        .translate((0.0, 0.0, -(plate_t / 2.0 + housing_h / 2.0)))
    )

    # string post up through the peg-hole, with the press-in bushing collar
    result = result.union(
        cq.Workplane("XY").workplane(offset=plate_t / 2.0).circle(post_d / 2.0).extrude(post_h)
    )
    result = result.union(
        cq.Workplane("XY").workplane(offset=plate_t / 2.0).circle(bushing_od / 2.0).extrude(plate_t * 0.7)
    )

    # worm / key shaft out the side of the housing (one side, or both)
    z_house = -(plate_t / 2.0 + housing_h / 2.0)
    reach = baseplate_w * 0.9
    shaft = cq.Workplane("XZ").circle(worm_d / 2.0).extrude(reach)  # -Y direction
    shaft = shaft.translate((0.0, baseplate_w * 0.3, z_house))
    result = result.union(shaft)
    if worm_both_sides:
        shaft2 = cq.Workplane("XZ").circle(worm_d / 2.0).extrude(-reach)  # +Y direction
        shaft2 = shaft2.translate((0.0, -baseplate_w * 0.3, z_house))
        result = result.union(shaft2)

    # locating-screw hole near the +X end of the baseplate
    mount_x = baseplate_l / 2.0 - mount_d - 2.0
    hole = cq.Workplane("XY").circle(mount_d / 2.0).extrude(200.0).translate((mount_x, 0.0, -100.0))
    result = result.cut(hole)

    return result
