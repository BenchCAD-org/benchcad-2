"""cabinet_bar_pull_handle — the parametric part.

A cabinet/drawer bar pull: a straight round bar carried on two cylindrical posts
that stand it off the cabinet face, each post tapped from the base for the
mounting machine screw. The bar overhangs each post; its ends are optionally
chamfered. The cabinet face is z=0; posts stand up +Z, the bar runs along X.

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def build(center_to_center, overhang, projection, bar_d, post_d, tap_d, tap_depth, chamfer_ends):
    length = center_to_center + 2.0 * overhang  # overall bar length

    # two posts standing off the cabinet face, each tapped from the base
    result = None
    for sx in (-1.0, 1.0):
        post = (
            cq.Workplane("XY")
            .circle(post_d / 2.0)
            .extrude(projection)
            .translate((sx * center_to_center / 2.0, 0.0, 0.0))
        )
        post = post.faces("<Z").workplane(centerOption="CenterOfBoundBox").hole(tap_d, depth=tap_depth)
        result = post if result is None else result.union(post)

    # round bar across the top of the posts (along X), centred at the post tops
    bar = cq.Workplane("YZ").circle(bar_d / 2.0).extrude(length).translate((-length / 2.0, 0.0, projection))
    if chamfer_ends:
        bar = bar.faces(">X").chamfer(bar_d * 0.1)
        bar = bar.faces("<X").chamfer(bar_d * 0.1)
    result = result.union(bar)

    return result
