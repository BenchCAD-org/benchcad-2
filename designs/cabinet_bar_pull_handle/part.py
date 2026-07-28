"""cabinet_bar_pull_handle — the parametric part (simple assembly, solids=3).

A cabinet/drawer bar pull as the three parts it is assembled from: a straight
round bar, and two cylindrical standoff posts that carry it off the cabinet
face, each post tapped from the base for the mounting machine screw. The post
tops are coped (saddle-cut by the bar cylinder) so each post mates flush against
the bar's underside with zero interpenetration — the members stay three separate
solids, as assembled. The bar overhangs each post; its ends are optionally
chamfered. The cabinet face is z=0; posts stand up +Z, the bar runs along X.

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def build(center_to_center, overhang, projection, bar_d, post_d, tap_d, tap_depth, chamfer_ends):
    length = center_to_center + 2.0 * overhang  # overall bar length

    # projection is the standoff to the bar's OUTER face, so the bar axis sits
    # half a bar-diameter below it
    z_bar = projection - bar_d / 2.0

    # round bar across the posts (along X), its axis at z_bar — one solid
    bar = cq.Workplane("YZ").circle(bar_d / 2.0).extrude(length).translate((-length / 2.0, 0.0, z_bar))
    if chamfer_ends:
        bar = bar.faces(">X").chamfer(bar_d * 0.1)
        bar = bar.faces("<X").chamfer(bar_d * 0.1)

    # an uncut, unchamfered bar cylinder as the coping tool, so the post saddle
    # follows the bar surface even at a chamfered end
    bar_tool = (
        cq.Workplane("YZ").circle(bar_d / 2.0).extrude(length).translate((-length / 2.0, 0.0, z_bar))
    )

    # two posts standing off the cabinet face, each tapped from the base; each
    # rises to the bar axis and is coped by the bar so it seats on the underside
    # without intersecting it — separate solids, in contact only
    posts = []
    for sx in (-1.0, 1.0):
        post = (
            cq.Workplane("XY")
            .circle(post_d / 2.0)
            .extrude(z_bar)
            .translate((sx * center_to_center / 2.0, 0.0, 0.0))
        )
        post = post.faces("<Z").workplane(centerOption="CenterOfBoundBox").hole(tap_d, depth=tap_depth)
        post = post.cut(bar_tool)
        posts.append(post)

    result = cq.Compound.makeCompound([bar.val(), posts[0].val(), posts[1].val()])
    return result
