"""Set screw shaft collar (GN 705 / DIN 705 style).

The set screw hole is a real tapped hole: drilled to the ISO internal-thread
minor diameter and cut out to the major diameter by a helical 60-degree V-groove
of the coarse pitch. The family is named for its set screw, so the thread is the
functional feature, not a cosmetic one -- `screw_d` runs M3 through M12 over the
catalogue rows (pitch 0.5 to 1.75 mm) and a smooth bore of that size is a
different part. Same construction as `t_slot_nut`.

There is NO spotface on the outside diameter. GN 705 dimensions exactly four
things -- d1, d2, d3 and b -- and d3 is the set screw itself (e.g. "M8 x 12").
Both catalogue types take a HEADLESS screw (Type A slotted ISO 7434, Type E hex
socket DIN 914) which seats entirely inside the tapped hole, so there is nothing
for a recess in the OD to clear. An earlier revision sank one anyway, sized
`screw_d * 1.45` deep by `min(1.2, max(0.35, screw_len * 0.12))` -- both invented.
"""

import cadquery as cq

# ISO 261 coarse pitch by nominal thread diameter, mm (the GN 705 d3 range)
_PITCH = {3: 0.5, 4: 0.7, 5: 0.8, 6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75}


def build(
    bore_d,
    outer_d,
    width,
    screw_d,
    screw_len,
    second_screw,
):
    od_r = outer_d / 2.0
    bore_r = bore_d / 2.0
    wall = od_r - bore_r
    chamfer = min(max(0.25, bore_d * 0.012), wall * 0.18, width * 0.08)

    collar = (
        cq.Workplane("XZ")
        .polyline(
            [
                (bore_r + chamfer, 0),
                (od_r - chamfer, 0),
                (od_r, chamfer),
                (od_r, width - chamfer),
                (od_r - chamfer, width),
                (bore_r + chamfer, width),
                (bore_r, width - chamfer),
                (bore_r, chamfer),
            ]
        )
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )

    screw_angles = [0]
    if second_screw:
        screw_angles.append(135)

    hole_len = wall + 1.0
    for angle in screw_angles:
        for cutter in _tapped_hole(screw_d, hole_len):
            collar = collar.cut(
                cutter
                .rotate((0, 0, 0), (0, 1, 0), 90)      # bore along +Z -> along +X
                .translate((bore_r - 0.5, 0, width / 2.0))
                .rotate((0, 0, 0), (0, 0, 1), angle)
            )

    result = collar
    return result


def _tapped_hole(thread_d, length):
    """The VOID of a metric tapped hole, along +Z from z = 0 to z = length.

    Drilled to the ISO internal-thread minor diameter and threaded out to the
    major diameter with 60-degree V-rings of the coarse pitch: crest flat P/4 at
    the minor Ø, root flat P/8 at the major Ø, depth 0.5413*P.

    Revolved RINGS, not a swept helix. A helix is the truer form and was tried
    first, but the boolean that cuts it silently no-ops below M10 -- on the ten
    rows from M3 to M8 the groove solid is built correctly (right radius, right
    length, sane volume) and the cut removes 0.0 mm3, leaving a smooth hole that
    still passes every gate. `knurled_thumb_screw_din464` records the same
    failure on its M6 and M8 rows and takes the same way out. The rings differ
    from a real thread only in lead: each turn closes on itself instead of
    advancing by P."""
    pitch = _PITCH[int(round(thread_d))]
    r_maj = thread_d / 2.0
    r_min = r_maj - 0.5413 * pitch             # ISO internal minor: d - 1.0825*P
    n = max(1, int(round(length / pitch)))

    pts = [(0.0, 0.0), (r_min, 0.0)]
    for k in range(n):
        z0 = k * pitch
        pts += [
            (r_min, z0 + pitch / 8.0),                    # end of the crest flat
            (r_maj, z0 + pitch / 2.0 - pitch / 16.0),     # flank out to the root
            (r_maj, z0 + pitch / 2.0 + pitch / 16.0),     # root flat
            (r_min, z0 + pitch - pitch / 8.0),            # flank back to the crest
        ]
    pts += [(r_min, length), (0.0, length)]

    return (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0)),
    )
