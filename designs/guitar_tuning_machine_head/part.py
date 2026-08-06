"""guitar_tuning_machine_head — the parametric part (assembly).

A sealed geared guitar tuning machine (Grover Rotomatic 102 class) modelled
with its REAL gear train: a single-start WORM on the key shaft drives a
WORM WHEEL pressed on the string post — z2 wheel teeth = the catalog gear
ratio (Grover 102 = 14:1, Gotoh SG381 = 16:1), so one button turn advances
the post by 1/z2 turn and the drive self-locks (lead angle < ~7 deg).

Five bodies: HOUSING (die-cast slab with the round cover boss, wheel chamber
and worm barrel), string POST (plate journal, relieved neck past the worm,
spigot through the wheel), WORM WHEEL (separate gear, running fit on the
spigot), BUTTON (key shaft with the worm cut on it and the pear grip), and
the peghole BUSHING.

Gear symbols (NOTES.md maps them to the sources):
  z2 = wheel tooth count = gear_ratio     m  = module = d_t2 / (z2 + 2)
  d1 = worm pitch diameter                a  = centre distance = (d1 + m*z2)/2
  b  = wheel face width                   px = axial pitch = pi * m

Frame: baseplate in XY centred at z=0, post up +Z, housing below, worm axis
along Y at (x=-a, z=z_w) — offset sideways from the post by the centre
distance, as a crossed-axis worm drive must be. Button out -Y. Components
mate with running clearance; nothing is fused across a joint.

Interface + examples: docs/DESIGN_SPEC.md
"""

import math

import cadquery as cq


def _gear(housing_h, housing_d, key_shaft_d, gear_ratio):
    """Worm-drive dimensions from the casting envelope and the catalog ratio.

    The wheel fills the chamber the envelope allows (tip clearance 1.7 to the
    chamber wall, 2.1 to the slab faces); the module follows from tip
    diameter d_t2 = m*(z2 + 2). The worm is cut on the key shaft:
    d1 = key_shaft_d + 1.4*m keeps a real root above the shaft."""
    z2 = float(gear_ratio)
    r_t2 = min(0.41 * housing_h - 1.7, housing_d / 2.0 - 2.1)  # wheel tip radius
    m = 2.0 * r_t2 / (z2 + 2.0)
    r2 = 0.5 * m * z2               # wheel pitch radius
    d1 = key_shaft_d + 1.4 * m      # worm pitch diameter
    r1t = 0.5 * d1 + 0.7 * m        # worm tip radius
    r1r = 0.5 * d1 - 1.2 * m        # worm root radius (0.2*m tip clearance
                                    # under the wheel tooth tips at r_t2)
    a = r2 + 0.5 * d1               # centre distance (crossed axes, offset in X)
    b = min(7.5 * m, 0.26 * housing_h)  # wheel face width
    px = math.pi * m                # worm axial pitch = wheel circular pitch
    r_sp = r2 - 1.25 * m - 1.3      # post spigot radius under the wheel bore
    return z2, m, r2, d1, r1t, r1r, a, b, px, r_sp


def _z_frame(plate_t, housing_h):
    """Vertical datums: body bottom and the worm/wheel plane z_w."""
    z_bot = -(plate_t / 2.0 + housing_h - 0.8)
    z_w = z_bot + 0.42 * housing_h
    return z_bot, z_w


def _housing(plate_w, plate_t, housing_w, housing_h, housing_d,
             barrel_d, screw_d, key_shaft_d, gear_ratio):
    """Die-cast body: two-lobe baseplate (gear lobe + outboard screw ear),
    rounded slab below it holding the wheel chamber (round cover boss on the
    +Y face, concentric with the post like the drawing's GROVER cover) and
    the worm barrel bulge on the -X side at the worm axis."""
    z2, m, r2, d1, r1t, r1r, a, b, px, r_sp = _gear(
        housing_h, housing_d, key_shaft_d, gear_ratio)
    z_bot, z_w = _z_frame(plate_t, housing_h)
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
    # main slab: rounded rectangle in the XZ view (drawing: the 18 body height)
    # spanning the wheel chamber on +X and flush with the worm barrel on -X,
    # buried 0.8 into the flange so the union is one casting
    r_cov = 0.42 * housing_h - 1.0          # round cover boss radius
    x_max = r_cov + 0.8
    r_wb = r1t + 1.1                        # worm barrel outer radius
    x_min = -(a + r_wb)
    z_top = -plate_t / 2.0 + 0.8
    slab = (
        cq.Workplane("XZ").workplane(offset=housing_d / 2.0)
        .center((x_min + x_max) / 2.0, (z_bot + z_top) / 2.0)
        .rect(x_max - x_min, z_top - z_bot).extrude(-housing_d)
        .edges("|Y").fillet(2.2)
    )
    # worm barrel bulge on the worm axis (chamfer the primitive, not the union)
    barrel = (
        cq.Workplane("XZ").workplane(offset=housing_d / 2.0)
        .center(-a, z_w).circle(r_wb).extrude(-housing_d)
        .edges().chamfer(0.8)
    )
    # round pressed cover on the +Y slab face, on the post centreline like the
    # drawing's GROVER boss (centre at the gear plane height)
    cover = (
        cq.Workplane("XZ").workplane(offset=-(housing_d / 2.0 + 1.0))
        .center(0.0, z_w).circle(r_cov).extrude(1.2)
    )
    body = plate.union(slab).union(barrel).union(cover)
    # wheel chamber: cylindrical cavity about the post axis
    r_cav = 0.5 * m * (z2 + 2.0) + 0.5  # wheel tip radius + running clearance
    cav_top = z_w + b / 2.0 + 0.6
    body = body.cut(
        cq.Workplane("XY").circle(r_cav)
        .extrude((z_bot + 1.4) - cav_top).translate((0, 0, cav_top))
    )
    # worm cavity along the worm axis, closed at both housing ends
    n_t = max(2, int((housing_d - 2.6) // px))
    l_w = n_t * px
    body = body.cut(
        cq.Workplane("XZ").workplane(offset=(l_w + 1.4) / 2.0)
        .center(-a, z_w).circle(r1t + 0.45).extrude(-(l_w + 1.4))
    )
    # key-shaft bore along the worm axis, through both housing faces
    body = body.cut(
        cq.Workplane("XZ").workplane(offset=housing_d * 2.0)
        .center(-a, z_w)
        .circle(key_shaft_d / 2.0 + 0.15).extrude(-housing_d * 4.0)
    )
    # post journal bore through the flange and the chamber ceiling
    body = body.cut(
        cq.Workplane("XY").circle(barrel_d / 2.0 + 0.15)
        .extrude(cav_top - 0.2 - plate_t / 2.0).translate((0, 0, plate_t / 2.0))
    )
    # locating-screw hole through the OUTBOARD ear only
    body = body.cut(
        cq.Workplane("XY").center(ear_cx, 0.0).circle(screw_d / 2.0)
        .extrude(-plate_t * 2.0).translate((0, 0, plate_t))
    )
    return body


def _post(post_d, barrel_d, post_h, plate_t, housing_h, housing_d,
          string_hole_d, key_shaft_d, gear_ratio):
    """String post: plate journal barrel (drawing's Ø9.9), a relieved neck
    that clears the worm tip, the wheel spigot with its retaining shoulder,
    then the Ø6-class string section with turned tip and string hole."""
    z2, m, r2, d1, r1t, r1r, a, b, px, r_sp = _gear(
        housing_h, housing_d, key_shaft_d, gear_ratio)
    z_bot, z_w = _z_frame(plate_t, housing_h)
    z_j = z_w + r1t + 0.6           # journal barrel bottom: clear of the worm
    z_wt = z_w + b / 2.0            # wheel top face
    r_n = min(a - r1t - 0.7, barrel_d / 2.0 - 0.8)  # neck beside the worm
    post = (
        cq.Workplane("XY").workplane(offset=z_j)
        .circle(barrel_d / 2.0).extrude(plate_t / 2.0 - z_j)
        # neck down past the worm to the wheel shoulder
        .union(cq.Workplane("XY").workplane(offset=z_wt + 0.1)
               .circle(r_n).extrude(z_j - z_wt - 0.1 + 0.05))
        # spigot through the wheel bore, ending under the wheel
        .union(cq.Workplane("XY").workplane(offset=z_w - b / 2.0 - 0.35)
               .circle(r_sp).extrude(z_wt + 0.1 - (z_w - b / 2.0 - 0.35)))
        # string section above the plate
        .union(cq.Workplane("XY").workplane(offset=plate_t / 2.0 - 0.05)
               .circle(post_d / 2.0).extrude(post_h + 0.05))
        .union(cq.Workplane("XY").workplane(offset=plate_t / 2.0 + post_h)
               .circle(post_d * 0.62).extrude(post_d * 0.45))
    )
    top_z = plate_t / 2.0 + post_h + post_d * 0.45
    hole = (
        cq.Workplane("XZ").workplane(offset=-post_d)
        .center(0.0, top_z - 6.0)
        .circle(string_hole_d / 2.0).extrude(post_d * 2.0)
    )
    return post.cut(hole)


def _wheel(plate_t, housing_h, housing_d, key_shaft_d, gear_ratio):
    """Worm wheel: z2 = gear_ratio teeth (single-start worm, so the tooth
    count IS the catalog ratio), straight trapezoidal tooth gaps cut into the
    blank, bored for a running fit on the post spigot. The gap phase is set
    so the worm thread meshes the -X side of the wheel."""
    z2, m, r2, d1, r1t, r1r, a, b, px, r_sp = _gear(
        housing_h, housing_d, key_shaft_d, gear_ratio)
    z_bot, z_w = _z_frame(plate_t, housing_h)
    r_t2 = 0.5 * m * (z2 + 2.0)
    r_root = r2 - 1.25 * m
    blank = (
        cq.Workplane("XY").workplane(offset=z_w - b / 2.0)
        .circle(r_t2).extrude(b).edges().chamfer(0.3)
        .cut(cq.Workplane("XY").circle(r_sp + 0.05)
             .extrude(b + 2.0).translate((0, 0, z_w - b / 2.0 - 1.0)))
    )
    # tooth gaps: trapezoid flanks at 20 deg, gap 0.66*px at pitch (tooth
    # thinned for backlash against the worm thread's 0.36*px thickness)
    n_t = max(2, int((housing_d - 2.6) // px))
    w_pitch = 0.5 * 0.66 * px + 0.06  # absolute backlash floor for small m
    w_root = w_pitch - (r2 - r_root) * math.tan(math.radians(20.0))
    r_out = r_t2 + 0.4
    w_out = w_pitch + (r_out - r2) * math.tan(math.radians(20.0)) + 0.1
    # worm crest faces the wheel at the mesh plane when n_t is odd (the helix
    # phase flips with each half turn); with even n_t the wheel presents a
    # TOOTH to the worm axis instead, so shift the gaps by half a pitch
    off = 0.0 if n_t % 2 == 1 else 0.5
    cutter = None
    for i in range(int(z2)):
        th = math.radians(180.0 + (i + off) * 360.0 / z2)
        c, s = math.cos(th), math.sin(th)
        pts = [(r_root, -w_root), (r_out, -w_out), (r_out, w_out),
               (r_root, w_root)]
        world = [(x * c - y * s, x * s + y * c) for x, y in pts]
        wedge = (
            cq.Workplane("XY").workplane(offset=z_w - b / 2.0 - 0.2)
            .polyline(world).close().extrude(b + 0.4)
        )
        cutter = wedge if cutter is None else cutter.union(wedge)
    return blank.cut(cutter)


def _button(plate_w, plate_t, housing_h, housing_d, key_shaft_d, gear_ratio,
            button_w, button_h, button_t):
    """Key shaft with the WORM cut on it, thrust collar and pear grip, built
    in a local frame with the shaft along +Z (the assembly Location poses it
    onto the worm axis). The worm is a real single-start thread: trapezoidal
    section swept along a helix of pitch px, root fused on the shaft."""
    z2, m, r2, d1, r1t, r1r, a, b, px, r_sp = _gear(
        housing_h, housing_d, key_shaft_d, gear_ratio)
    n_t = max(2, int((housing_d - 2.6) // px))
    l_w = n_t * px
    z_m = housing_d / 2.0 - 0.8      # worm mid: local z_m maps to world y=0
    ext = max(housing_d * 0.5 + 3.0, plate_w / 2.0 + 1.5)
    z_pb = z_m + ext                 # pear base plane (world y = -ext)
    key_len = z_pb + button_t * 0.6
    # the worm span is a full-tip-diameter BLANK on the shaft; the thread is
    # then formed by CUTTING the helical inter-thread groove out of it.
    # (Fusing a multi-turn swept rib ONTO the shaft silently drops solids in
    # this OCC build — the groove-cut construction avoids every union with a
    # helical solid, and the probes verify the thread by driving the wheel.)
    z0 = z_m - l_w / 2.0
    # helical groove: trapezoid opening toward the tip (thread flanks 20 deg,
    # thread 0.34*px thick at the pitch line -> backlash against the wheel's
    # 0.66*px gaps). A swept helical cutter is USELESS in this pinned OCC —
    # cut and fuse both silently no-op (or annihilate) against the swept
    # solid on some draws — so the groove is a chain of straight prisms, 12
    # per turn, each sketched directly on its own posed plane (planar faces
    # only; the 0.19 mm faceting sagitta is absorbed by the gap backlash),
    # collected in one compound and removed with a single cut.
    r1p = 0.5 * d1
    g_p = 0.5 * 0.66 * px + 0.06  # absolute backlash floor for small m
    g_root = g_p - 1.2 * m * math.tan(math.radians(20.0))
    g_out = g_p + (0.7 * m + 0.45) * math.tan(math.radians(20.0))
    lam = math.atan(px / (2.0 * math.pi * r1p))  # lead angle (self-locking)
    n_seg = 12
    steps = int(n_seg * (l_w / px + 1.0)) + 1
    seg = math.sqrt((2.0 * math.pi * r1p / n_seg) ** 2 + (px / n_seg) ** 2)
    prisms = []
    for i in range(steps + 1):
        frac = i / float(n_seg)
        th = 2.0 * math.pi * frac
        z = z0 - px / 2.0 + px * frac
        cth, sth = math.cos(th), math.sin(th)
        pl = cq.Plane(origin=(r1p * cth, r1p * sth, z),
                      xDir=(cth, sth, 0.0),
                      normal=(-sth * math.cos(lam), cth * math.cos(lam),
                              math.sin(lam)))
        w = (
            cq.Workplane(pl)
            .polyline([(r1r - r1p, -g_root), (r1t + 0.45 - r1p, -g_out),
                       (r1t + 0.45 - r1p, g_out), (r1r - r1p, g_root)])
            .close()
            .extrude(seg / 2.0 + 0.45, both=True)
        )
        prisms.append(w)
    # one cut per prism: a compound tool of mutually overlapping prisms (and
    # every helical swept cutter) is silently ignored by this OCC's booleans
    blank = (
        cq.Workplane("XY").workplane(offset=z0)
        .circle(r1t).extrude(l_w).edges().chamfer(0.4)
    )
    for w in prisms:
        blank = blank.cut(w)
    shaft = (
        cq.Workplane("XY").circle(key_shaft_d / 2.0).extrude(z0 + 0.05)
        .union(blank)
        .union(cq.Workplane("XY").workplane(offset=z0 + l_w - 0.05)
               .circle(key_shaft_d / 2.0)
               .extrude(key_len - z0 - l_w + 0.05))
        # thrust collar just outside the housing face
        .union(cq.Workplane("XY").workplane(offset=z_m + housing_d / 2.0 + 0.5)
               .circle(key_shaft_d * 0.62).extrude(key_shaft_d * 0.6))
    )
    # pear grip: flat paddle, faces perpendicular to the shaft, crown toward
    # local -y (world +Z after the pose — the drawing's side-view stance)
    pear = (
        cq.Workplane("XY").workplane(offset=z_pb)
        .moveTo(-button_w / 2.0, 0.0)
        .lineTo(-button_w * 0.42, -button_h * 0.28)
        .threePointArc((0.0, -button_h), (button_w * 0.42, -button_h * 0.28))
        .lineTo(button_w / 2.0, 0.0)
        .close()
        .extrude(button_t)
    )
    return shaft.union(pear)


def _bushing(bushing_od, post_d, plate_t):
    """Peghole bushing, a separate part: press-in collar (Ø7.8 class) or the
    hex ferrule with its Ø15 washer flange (Ø14 class)."""
    bore_r = post_d / 2.0 + 0.2
    if bushing_od >= 10.0:
        # Gotoh-style ferrule at the drawing's full 14.6 stack: M8-class
        # barrel reaching down around the post, Ø15 x 1 washer, hex head
        barrel_len = 14.6 - 5.5 - 1.0
        bushing = (
            cq.Workplane("XY").circle(4.0).extrude(barrel_len)
            .faces(">Z").workplane().circle(7.5).extrude(1.0)
            .faces(">Z").workplane().polygon(6, bushing_od).extrude(5.5)
        )
        z0 = plate_t / 2.0 + 0.3
    else:
        # Grover-style press-in collar
        bushing = (
            cq.Workplane("XY").circle(bushing_od / 2.0 + 1.2).extrude(1.2)
            .faces(">Z").workplane().circle(bushing_od / 2.0).extrude(4.5)
        )
        z0 = plate_t / 2.0
    return bushing.cut(
        cq.Workplane("XY").circle(bore_r).extrude(40.0).translate((0, 0, -10.0))
    ).translate((0, 0, z0))


def build(plate_w, plate_t, housing_w, housing_h, housing_d,
          post_d, barrel_d, post_h, bushing_od, string_hole_d, screw_d,
          key_shaft_d, gear_ratio, button_w, button_h, button_t):
    z2, m, r2, d1, r1t, r1r, a, b, px, r_sp = _gear(
        housing_h, housing_d, key_shaft_d, gear_ratio)
    z_bot, z_w = _z_frame(plate_t, housing_h)
    z_m = housing_d / 2.0 - 0.8
    result = cq.Assembly(name="guitar_tuning_machine_head")
    result.add(_housing(plate_w, plate_t, housing_w, housing_h,
                        housing_d, barrel_d, screw_d, key_shaft_d, gear_ratio),
               name="housing")
    result.add(_post(post_d, barrel_d, post_h, plate_t, housing_h, housing_d,
                     string_hole_d, key_shaft_d, gear_ratio), name="post")
    result.add(_wheel(plate_t, housing_h, housing_d, key_shaft_d, gear_ratio),
               name="worm_wheel")
    # pose the button onto the worm axis: local +Z -> world -Y (shaft out the
    # -Y face), local -y -> world +Z (pear crown up). That is a 180 deg turn
    # about (0,-1,1); it also maps local +X -> world -X, which the worm/wheel
    # phase bookkeeping in _wheel/_button accounts for.
    result.add(_button(plate_w, plate_t, housing_h, housing_d, key_shaft_d,
                       gear_ratio, button_w, button_h, button_t),
               name="button",
               loc=cq.Location((-a, z_m, z_w), (0.0, -1.0, 1.0), 180.0))
    result.add(_bushing(bushing_od, post_d, plate_t), name="bushing")
    return result
