"""guitar_tuning_machine_head — the parametric part (assembly).

A sealed geared guitar tuning machine (Grover Rotomatic 102 style), modelled
as the multi-part product it is: a die-cast HOUSING (rounded gear body under a
two-lobe baseplate whose screw ear sits OUTBOARD of the gear body), a string
POST (drawing's Ø6 string section over the Ø9.9 lower barrel, with the
transverse Ø2.2 string hole), the pear-shaped tuning BUTTON on the key shaft
(worm axis perpendicular to the post axis), and the separate peghole BUSHING
(press-in collar at Ø7.8, hex ferrule with the Ø15 washer flange at Ø14).

Frame: baseplate in XY centred at z=0, post up +Z through the peghole, gear
housing below, key shaft out +Y. Components mate with running clearance —
post and button turn in the housing; nothing is fused across a joint.

Interface + examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def _housing(plate_w, plate_t, housing_w, housing_h, housing_d,
             barrel_d, screw_d, key_shaft_d):
    """Die-cast body: two-lobe baseplate (round gear lobe + outboard screw
    ear, spanning the catalog housing_w envelope) over a rounded gear box
    narrower than the plate; bored for the post barrel and key shaft."""
    lobe_r = plate_w / 2.0
    ear_r = screw_d * 1.15
    ear_cx = housing_w / 2.0 - ear_r  # ear disc centre, at the envelope end
    # two-lobe flange: gear lobe + ear lobe + a tapering web between them
    plate = (
        cq.Workplane("XY").circle(lobe_r).extrude(plate_t)
        .union(cq.Workplane("XY").center(ear_cx, 0).circle(ear_r).extrude(plate_t))
        .union(cq.Workplane("XY")
               .polyline([(0, lobe_r * 0.85), (ear_cx, ear_r * 0.9),
                          (ear_cx, -ear_r * 0.9), (0, -lobe_r * 0.85)])
               .close().extrude(plate_t))
        .translate((0, 0, -plate_t / 2.0))
    )
    # rounded gear box below (the sealed cavity, NARROWER than the plate so
    # the screw ear clears it), with the circular cover boss on its face
    box_w = plate_w * 0.68
    box = (
        cq.Workplane("XY").box(box_w, housing_d, housing_h)
        .edges("|Z").fillet(box_w * 0.18)
        .translate((0.0, 0.0, -(plate_t / 2.0 + housing_h / 2.0)))
    )
    cover_r = box_w * 0.46
    cover = (
        cq.Workplane("XZ").workplane(offset=housing_d / 2.0)
        .center(0.0, -(plate_t / 2.0 + housing_h / 2.0))
        .circle(cover_r).extrude(1.0)
    )
    body = plate.union(box).union(cover)
    # post-barrel bore through plate and box top (running clearance)
    body = body.cut(
        cq.Workplane("XY").circle(barrel_d / 2.0 + 0.15)
        .extrude(-(plate_t + housing_h * 0.55)).translate((0, 0, plate_t / 2.0))
    )
    # key-shaft through-bore at WORM depth — below the wheel on the post
    # barrel, like the real gear stack. XZ-plane sign convention: offset=+d
    # puts the plane at y=-d, extrude(-L) sweeps +Y — so this spans y -d..+d.
    body = body.cut(
        cq.Workplane("XZ").workplane(offset=housing_d)
        .center(0.0, -(plate_t / 2.0 + housing_h * 0.72))
        .circle(key_shaft_d / 2.0 + 0.15).extrude(-housing_d * 2.0)
    )
    # locating-screw hole through the OUTBOARD ear only
    body = body.cut(
        cq.Workplane("XY").center(ear_cx, 0.0).circle(screw_d / 2.0)
        .extrude(-plate_t * 2.0).translate((0, 0, plate_t))
    )
    return body


def _post(post_d, barrel_d, post_h, plate_t, housing_h, string_hole_d):
    """String post: Ø9.9-class lower barrel journalled in the housing, the
    Ø6-class string section above with a turned tip, and the transverse
    string hole 6 mm under the post top."""
    barrel_len = plate_t + housing_h * 0.5
    post = (
        cq.Workplane("XY").circle(barrel_d / 2.0).extrude(-barrel_len)
        .faces(">Z").workplane().circle(post_d / 2.0).extrude(post_h)
        .faces(">Z").workplane().circle(post_d * 0.62).extrude(post_d * 0.45)
    )
    post = post.translate((0, 0, plate_t / 2.0))
    top_z = plate_t / 2.0 + post_h + post_d * 0.45
    hole = (
        cq.Workplane("XZ").workplane(offset=-post_d)
        .center(0.0, top_z - 6.0)
        .circle(string_hole_d / 2.0).extrude(post_d * 2.0)
    )
    return post.cut(hole)


def _button(button_w, button_h, button_t, key_shaft_d, key_len, housing_d):
    """Key shaft with a thrust collar just outside the housing face and the
    pear (half-round) tuning button, built along +Y."""
    collar_y = housing_d * 0.75 + 0.5  # local: clears the +Y face for any draw
    shaft = (
        cq.Workplane("XZ").circle(key_shaft_d / 2.0).extrude(-key_len)
        .union(cq.Workplane("XZ").workplane(offset=-collar_y)
               .circle(key_shaft_d * 0.62).extrude(-key_shaft_d * 0.6))
    )
    # pear profile: flat base on the shaft axis, half-round crown hanging -Z
    # (drawing: 23.85 wide x 17 tall x 8 thick), sketched directly on XZ so it
    # extrudes into its final pose at the shaft's outboard end
    pear_y0 = key_len - button_t * 1.5
    pear = (
        cq.Workplane("XZ").workplane(offset=-pear_y0)
        .moveTo(-button_w / 2.0, 0.0)
        .lineTo(-button_w * 0.42, -button_h * 0.28)
        .threePointArc((0.0, -button_h), (button_w * 0.42, -button_h * 0.28))
        .lineTo(button_w / 2.0, 0.0)
        .close()
        .extrude(-button_t)
    )
    return shaft.union(pear)


def _bushing(bushing_od, post_d, plate_t):
    """Peghole bushing, a separate part: press-in collar (Ø7.8 class) or the
    hex ferrule with its Ø15 washer flange (Ø14 class)."""
    bore_r = post_d / 2.0 + 0.2
    if bushing_od >= 10.0:
        # Gotoh-style: Ø15 washer flange + hex body (M8-class ferrule)
        bushing = (
            cq.Workplane("XY").circle(7.5).extrude(1.0)
            .faces(">Z").workplane().polygon(6, bushing_od).extrude(5.5)
        )
    else:
        # Grover-style press-in collar
        bushing = (
            cq.Workplane("XY").circle(bushing_od / 2.0 + 1.2).extrude(1.2)
            .faces(">Z").workplane().circle(bushing_od / 2.0).extrude(4.5)
        )
    return bushing.cut(
        cq.Workplane("XY").circle(bore_r).extrude(20.0).translate((0, 0, -5.0))
    ).translate((0, 0, plate_t / 2.0))


def build(plate_w, plate_t, housing_w, housing_h, housing_d,
          post_d, barrel_d, post_h, bushing_od, string_hole_d, screw_d,
          key_shaft_d, button_w, button_h, button_t):
    # shaft long enough that the pear's inboard face clears the housing back
    # face by 3 mm for ANY draw (drawing: button axis 12.6 past the back face)
    key_len = housing_d * 0.75 + button_t * 1.5 + 3.0
    result = cq.Assembly(name="guitar_tuning_machine_head")
    result.add(_housing(plate_w, plate_t, housing_w, housing_h,
                        housing_d, barrel_d, screw_d, key_shaft_d),
               name="housing")
    result.add(_post(post_d, barrel_d, post_h, plate_t, housing_h,
                     string_hole_d), name="post")
    # key shaft reaches INTO the housing's key bore (running clearance); the
    # button then sits off the back face like the drawing's 40.8 - 28.2 stack
    result.add(_button(button_w, button_h, button_t, key_shaft_d, key_len,
                       housing_d),
               name="button",
               loc=cq.Location((0.0, -housing_d * 0.25,
                                -(plate_t / 2.0 + housing_h * 0.72))))
    result.add(_bushing(bushing_od, post_d, plate_t), name="bushing")
    return result
