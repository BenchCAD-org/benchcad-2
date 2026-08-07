"""double_locking_tremolo_bridge — Gotoh GE1996T double-locking tremolo.

The bridge plate rocks on two hardened knife edges bearing on a pair of posts,
so `pivot_angle` is an operating state, not a dimension. Per string it carries a
saddle, a clamp block and the clamp screw; a sustain block hangs under the plate
and the two posts stand in pressed-in insert bushings.

Frame, taken from the dimension sheet and checked for self-consistency before
any geometry was written: **X is across the strings** (the 91.5 mm span, the
74 mm post spacing and the 10.8 mm string pitch all lie on it), **Y runs along
the strings** (the 36 mm depth), **Z is up**, and the sustain block hangs -Z.
The elevation's 19 / 50 / 20 / 2.5 stations sum to 91.5, which is what pins X as
the long axis rather than the string direction.
"""

import cadquery as cq
import math

# Proportions the sheet does not dimension (all listed in NOTES.md).
_KNIFE_INSET = 0.14        # knife-edge line from the back edge / plate depth
_SADDLE_ROW = 0.50         # saddle row centre from the front edge / plate depth
_CLAMP_H = 0.34            # clamp block height / saddle height
_SCREW_D = 0.30            # clamp screw diameter / string pitch
_BLOCK_W = 0.55            # sustain block width / plate span
_BLOCK_D = 0.62            # sustain block depth / plate depth
_POST_HEAD = 1.5           # post head diameter / post shaft diameter
_STEP_H = 0.45             # clamp-bearing step height / knife-edge height
_STEP_D = 0.30             # clamp-bearing step depth / plate depth
_ARM_BOSS = 1.25           # arm collet boss diameter / string pitch
_ARM_TILT = 12.0           # deg, arm collet rake off vertical


def _rounded_plate(span, depth, thick, corner_r):
    """Base plate: a rounded rectangle, thickened."""
    return (
        cq.Workplane("XY")
        .rect(span, depth)
        .extrude(thick)
        .edges("|Z")
        .fillet(corner_r)
    )


def _arm_socket(boss_d, boss_h, bore_d, tilt):
    """The tremolo arm collet: a boss on the treble end of the plate, bored at
    the sheet's rake so the arm stands off the top rather than square to it."""
    boss = (
        cq.Workplane("XY").circle(boss_d / 2.0).extrude(boss_h)
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), tilt)
    )
    bore = (
        cq.Workplane("XY").circle(bore_d / 2.0).extrude(boss_h * 3.0)
        .translate((0.0, 0.0, -boss_h))
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), tilt)
    )
    return boss.cut(bore)


def _clamp_step(span, depth_y, thick, corner_r):
    """The raised band along the back of the plate that the string clamps bear
    on — what makes this a locking bridge rather than a flat plate."""
    return (
        cq.Workplane("XY")
        .rect(span, depth_y)
        .extrude(thick)
        .edges("|Z")
        .fillet(corner_r)
    )


def _knife_edge(span, post_spacing, thick, knife_h, depth_y):
    """The two hardened bearing ridges the plate rocks on: a prism running along
    X, broken by the gap between the posts so each post sees its own edge."""
    half = knife_h
    section = (
        cq.Workplane("XZ")
        .moveTo(-half, 0.0)
        .lineTo(half, 0.0)
        .lineTo(0.0, -knife_h)
        .close()
        .extrude(depth_y)
        .translate((0.0, depth_y / 2.0, 0.0))
    )
    out = None
    for side in (-1.0, 1.0):
        piece = section.translate((side * post_spacing / 2.0, 0.0, 0.0))
        out = piece if out is None else out.union(piece)
    return out


def _saddle(width, length, height, slot_w):
    """String saddle: a block slotted lengthwise for the string, with the
    intonation foot under it."""
    body = cq.Workplane("XY").box(width, length, height, centered=(True, True, False))
    slot = (
        cq.Workplane("XY")
        .box(slot_w, length * 1.2, height * 0.45, centered=(True, True, False))
        .translate((0.0, 0.0, height * 0.55))
    )
    return body.cut(slot)


def _clamp_block(width, length, height):
    return cq.Workplane("XY").box(width, length, height, centered=(True, True, False))


def _screw(dia, length):
    head_t = dia * 0.6
    shank = cq.Workplane("XY").circle(dia / 2.0).extrude(length)
    head = (
        cq.Workplane("XY").polygon(6, dia * 1.5).extrude(head_t)
        .translate((0.0, 0.0, length))
    )
    return shank.union(head)


def _post(shaft_d, length, head_d):
    """Mounting post: threaded shaft with a domed bearing head."""
    shaft = cq.Workplane("XY").circle(shaft_d / 2.0).extrude(length)
    head = (
        cq.Workplane("XY").circle(head_d / 2.0).extrude(head_d * 0.55)
        .translate((0.0, 0.0, length - head_d * 0.15))
    )
    return shaft.union(head)


def _bushing(outer_d, inner_d, length):
    """Pressed-in insert bushing, axis on Z.

    Two things have to line up or the revolve degenerates to a face. The
    section must lie in a plane that CONTAINS the axis — XZ does, XY does not —
    and `revolve`'s axis is given in the workplane's LOCAL coordinates, where
    local z is the plane normal. On an XZ workplane world Z is local (0, 1, 0),
    so passing (0, 0, 1) here would revolve about world -Y instead."""
    half = length / 2.0
    return (
        cq.Workplane("XZ")
        .moveTo(inner_d / 2.0, -half)
        .lineTo(outer_d / 2.0, -half)
        .lineTo(outer_d / 2.0, half)
        .lineTo(inner_d / 2.0, half)
        .close()
        .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    )


def build(n_strings, string_pitch, plate_span, plate_depth, plate_t, knife_h,
          post_spacing, block_height, saddle_radius, saddle_len, post_shaft_d,
          bushing_d, bushing_len, pivot_angle):
    corner_r = plate_span * 0.055
    plate = _rounded_plate(plate_span, plate_depth, plate_t, corner_r)
    knife = _knife_edge(plate_span, post_spacing, plate_t, knife_h,
                        plate_depth * 0.30)
    knife_y = plate_depth * (0.5 - _KNIFE_INSET)
    # lift the ridge into the plate so the join is a buried volume rather than
    # two coincident faces, which OCC unions unreliably
    plate = plate.union(knife.translate((0.0, knife_y, plate_t * 0.5)))

    # raised band the string clamps bear on — the feature that makes this a
    # locking bridge rather than a flat plate
    step_h = knife_h * _STEP_H
    plate = plate.union(
        _clamp_step(plate_span * 0.97, plate_depth * _STEP_D, step_h + plate_t * 0.5,
                    corner_r * 0.6)
        .translate((0.0, plate_depth * (0.5 - _STEP_D / 2.0) - corner_r,
                    plate_t * 0.5))
    )

    # tremolo arm collet on the treble end
    boss_d = string_pitch * _ARM_BOSS
    plate = plate.union(
        _arm_socket(boss_d, knife_h * 1.35, boss_d * 0.42, _ARM_TILT)
        .translate((plate_span / 2.0 - boss_d * 0.75, -plate_depth * 0.22,
                    plate_t * 0.4))
    )

    block_w = _BLOCK_W * plate_span
    block_d = _BLOCK_D * plate_depth
    block = (
        cq.Workplane("XY")
        .box(block_w, block_d, block_height, centered=(True, True, False))
        .translate((0.0, 0.0, -block_height))
    )
    # bury the block a little into the plate so the join is a volume, not a face
    block = block.union(
        cq.Workplane("XY")
        .box(block_w, block_d, plate_t * 0.8, centered=(True, True, False))
    )

    saddle_y = plate_depth * (_SADDLE_ROW - 0.5)
    span_half = string_pitch * (n_strings - 1) / 2.0

    def _rock(shape):
        """Everything carried by the plate rocks about the knife-edge line — an
        X axis through knife_y at the plate underside. The posts and bushings
        are set into the guitar body and do not move with it."""
        return shape.rotate((0.0, knife_y, 0.0), (1.0, knife_y, 0.0), pivot_angle)

    result = cq.Assembly(name="double_locking_tremolo_bridge")
    result.add(_rock(plate), name="base_plate")
    result.add(_rock(block), name="sustain_block")

    for i in range(int(n_strings)):
        x = -span_half + i * string_pitch
        # the saddle tops lie on a cylinder of radius `saddle_radius`, so the
        # outer saddles stand lower than the middle ones
        drop = saddle_radius - math.sqrt(max(1.0, saddle_radius ** 2 - x * x))
        h = plate_t + knife_h * 0.85 - drop
        clamp_y = saddle_y + saddle_len * 0.22
        sad = _saddle(string_pitch * 0.86, saddle_len, h, string_pitch * 0.30)
        result.add(_rock(sad.translate((x, saddle_y, plate_t))),
                   name="saddle_%02d" % (i + 1))
        clamp = _clamp_block(string_pitch * 0.72, saddle_len * 0.42, _CLAMP_H * h)
        result.add(_rock(clamp.translate((x, clamp_y, plate_t + h))),
                   name="clamp_block_%02d" % (i + 1))
        scr = _screw(_SCREW_D * string_pitch, _CLAMP_H * h * 1.4)
        result.add(_rock(scr.translate((x, clamp_y, plate_t + h))),
                   name="clamp_screw_%02d" % (i + 1))

    # The post head is the bearing surface the knife edge sits on, so its top
    # lands on the knife tip; the bushing is pressed into the body around it.
    knife_tip = plate_t * 0.5 - knife_h
    head_d = post_shaft_d * _POST_HEAD
    post_len = bushing_len * 1.05
    post_z = knife_tip - (post_len + head_d * 0.4)
    for j, side in enumerate((-1.0, 1.0)):
        px = side * post_spacing / 2.0
        result.add(
            _post(post_shaft_d, post_len, head_d).translate((px, knife_y, post_z)),
            name="post_%02d" % (j + 1),
        )
        result.add(
            _bushing(bushing_d, post_shaft_d * 1.12, bushing_len)
            .translate((px, knife_y, knife_tip - bushing_len / 2.0 - 2.0)),
            name="insert_bushing_%02d" % (j + 1),
        )
    return result
