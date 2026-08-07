"""truss_half_coupler_hook — the parametric part (assembly, solids=6).

A stage/theatre half coupler / hook clamp (Doughty T57000/T57200 class) drawn
closed around the (phantom) Ø48-51 mm barrel, as the six parts it is assembled
from. The outline is taken off the datasheet front view
(`docs/assets/refs/truss_half_coupler_hook_drawing.png`), measured against its
own 107 / 55 / 19 / 16 dimensions — see NOTES.md for the pixel readings.

    1. lower shell  — the one-piece extruded body: a hexagonal plate whose two
                      upper corners are ROUND LOBES around the hinge and pivot
                      pins (they sit BELOW the tube centre, and they are what
                      the 107 overall width is measured from on the left), a
                      flat top face just above the tube centre, and a deep
                      U-jaw bored through it. Below the jaw, the captive-nut
                      window and the vertical Ø12.7 fixing bore (or, on the
                      hook clamp, the protruding M12 stud).
    2. upper shell  — the closure strap: a band over the barrel that thickens
                      into a tongue at the hinge end and runs out, past the
                      pivot, into the long flat TAB the eyebolt swings in. The
                      tab is cantilevered with open air under it, and its tip
                      is the +X end of the 107.
    3. hinge pin    — roll pin through the body's left ears and the tongue
    4. closing bolt — eye on the pivot pin, plain shank up through the open
                      tab slot, ring-thread top (revolved rings, no helix)
    5. pivot pin    — roll pin through the body's right ears and the bolt eye
    6. wing nut     — DIN 315-D butterfly on the thread above the tab, its
                      internal thread rings interleaved half a pitch with the
                      bolt rings (engaged, zero interpenetration)

Every mate is contact-or-clearance, never fused: the strap is held by the hinge
pin (0.15 mm radial) and BEARS on the body's left shoulder, which is the only
face contact in the assembly; the bolt clears its tab slot by 0.7 mm a side,
and the nut hovers 0.3 mm over the tab with its rings nested between the bolt
rings. Tube axis is Y. The strap does NOT close onto the body — the
datasheet outline leaves the barrel exposed in two gaps, upper-right (where
the eyebolt crosses) and upper-left, which is what lets the clamp open.

Drawing symbols (Doughty sheet): barrel Ø48-51 -> bore_d; body width 50 ->
body_w; tube centre->base 55 -> base_drop; the sheet's 19 is the captive-nut
window across the clamp (tang_t), which is exactly the A/F of the M12 nut it
traps; 16 is the depth of the Ø12.7 fixing bore up from the base face;
overall 107 across = the left lobe (x_pin + r_lobe) plus the tab tip (x_tab).

Interface + examples: docs/DESIGN_SPEC.md
"""

import math

import cadquery as cq


def _hardware(closing_bolt_d):
    """Closing-bolt nominal Ø and its ISO 261 coarse pitch.

    This is the swing eyebolt the wing nut runs on — NOT the base fixing bore
    `hang_d`. They are separate fasteners on the real clamp and the datasheet
    lists them separately; deriving the eyebolt from the Ø12.7 fixing hole put
    a DIN 315-D M12 wing nut on the part, whose 63.5 mm span does not fit the
    catalog's 107 mm overall width. The M10 row's 49.5 span, by contrast, ends
    within a millimetre of the tab tip on the anchor row — which is what the
    datasheet's own wing nut does."""
    bolt_d = float(closing_bolt_d)
    pitch = {8.0: 1.25, 10.0: 1.5, 12.0: 1.75}.get(bolt_d,
                                                   1.5 if bolt_d < 11.0 else 1.75)
    return bolt_d, pitch


# DIN 315 form D, mid-band per row (mm). Symbols are the datasheet's:
#   d2 boss Ø at the bearing face · d3 boss Ø at the top · m boss height
#   e span over the wing tips · h overall height · g2/g1 wing thickness at the
#   root/ear · r1 ear radius · r4 concave underside radius
_DIN315D = {
    8.0:  (14.5, 11.5, 37.5, 19.0,  8.2, 2.4, 4.0,  6.0, 3.0),
    10.0: (18.5, 15.5, 49.5, 24.0, 10.0, 4.0, 5.0,  8.0, 5.0),
    12.0: (21.5, 18.5, 63.5, 32.2, 12.0, 4.5, 6.0, 10.0, 6.0),
    16.0: (27.5, 22.0, 71.5, 36.2, 15.0, 6.0, 7.0, 11.0, 7.0),
}


def _din315d(d1):
    """The DIN 315-D row nearest ``d1``, scaled to the actual thread Ø so the
    nut still screws onto a non-tabulated bolt. Returns the drawing symbols
    (d2, d3, e, h, m, g1, g2, r1, r4)."""
    nom = min(_DIN315D, key=lambda k: abs(k - d1))
    k = d1 / nom
    return tuple(v * k for v in _DIN315D[nom])


def _lune(wp, rho, r3, y0):
    """The r3 root-fillet lune at boss radius ``rho``: the curvilinear triangle
    bounded by the wing face (y = y0), the boss circle and the fillet circle of
    radius r3 tangent to both — the drawing's r3 as seen from below. Lofted
    along the boss cone it becomes the flare from the plate into the boss, which
    OCC cannot produce as a fillet on a plate-on-cone seam at any radius."""
    cx = math.sqrt(max((rho + r3) ** 2 - (y0 + r3) ** 2, 1e-9))
    cy = y0 + r3
    tx, ty = cx * rho / (rho + r3), cy * rho / (rho + r3)   # tangency on the boss
    bx = math.sqrt(max(rho ** 2 - y0 ** 2, 1e-9))           # boss circle at y = y0
    ab, at = math.atan2(y0, bx), math.atan2(ty, tx)
    am = 0.5 * (ab + at)
    bm = (rho * math.cos(am), rho * math.sin(am))           # midpoint on the boss
    ux, uy = (tx - cx) / r3, (ty - cy) / r3
    n = math.hypot(ux, uy - 1.0) or 1.0
    fm = (cx + r3 * ux / n, cy + r3 * (uy - 1.0) / n)       # midpoint on the fillet
    return (wp.moveTo(bx, y0).lineTo(cx, y0)
            .threePointArc(fm, (tx, ty))
            .threePointArc(bm, (bx, y0)).close())


def _wing(e, h, m, r_boss, g_root, ear_r1, under_r4):
    """ONE lobed wing on the +X side, as the DIN 315-D front view draws it: an
    ear of radius r1 at the tip, a concave underside r4 sweeping back to the
    boss, and a valley up from the boss top. Built in XZ — the 107-width plane,
    which is where the datasheet shows the wings splayed — and extruded across
    the tube axis. The caller mirrors it for the -X side rather than
    re-deriving the profile with sign flips, which is how the arc midpoints get
    silently reflected onto the wrong side."""
    cx, cz = e / 2.0 - ear_r1, h - ear_r1              # ear centre
    tip = (e / 2.0, cz)                                # outermost point
    top = (cx, h)                                      # ear apex
    v0 = (r_boss * 0.55, m)                            # valley root, boss top
    ain, aun = math.radians(118.0), math.radians(-72.0)
    ein = (cx + ear_r1 * math.cos(ain), cz + ear_r1 * math.sin(ain))
    eun = (cx + ear_r1 * math.cos(aun), cz + ear_r1 * math.sin(aun))
    u1 = (r_boss * 0.95, 0.30 * m)                     # wing root on the boss
    vm = ((v0[0] + ein[0]) / 2.0 - 0.35 * ear_r1,
          (v0[1] + ein[1]) / 2.0 + 0.35 * ear_r1)      # concave valley
    um = ((u1[0] + eun[0]) / 2.0, (u1[1] + eun[1]) / 2.0 + 0.45 * under_r4)
    mid = ((tip[0] + eun[0]) / 2.0 + 0.18 * ear_r1, (tip[1] + eun[1]) / 2.0)
    return (cq.Workplane("XZ")
            .moveTo(*v0)
            .threePointArc(vm, ein)          # valley, concave
            .threePointArc(top, tip)         # ear: inner tangent -> apex -> tip
            .threePointArc(mid, eun)         # ear: tip -> underside tangent
            .threePointArc(um, u1)           # underside, concave r4
            .lineTo(*v0).close()
            .extrude(g_root / 2.0, both=True))


def _y_slab(x_c, y_c, z_c, dx, dy, dz):
    """A box centred at (x_c, y_c) spanning z from z_c to z_c+dz."""
    return (
        cq.Workplane("XY")
        .box(dx, dy, dz, centered=(True, True, False))
        .translate((x_c, y_c, z_c))
    )


def _y_cyl(x_c, y_c, width, radius):
    """A cylinder about the Y axis, centred at (x_c, y_c, z=0)."""
    return (
        cq.Workplane("XZ", origin=(x_c, y_c + width / 2.0, 0.0))
        .circle(radius)
        .extrude(width)
    )


def _y_prism(wire_fn, width):
    """Extrude a closed XZ wire across the tube axis, centred on y=0."""
    wp = cq.Workplane("XZ", origin=(0.0, width / 2.0, 0.0))
    return wire_fn(wp).extrude(width)


def _tangent(px, pz, cx, cz, r, side):
    """The tangency point on circle (cx, cz, r) of the tangent drawn from the
    external point (px, pz). ``side`` = +1 / -1 selects which of the two.

    Straight-into-arc is how the datasheet outline is actually drawn (the
    sloped flanks run into the round pin lobes without a visible break), and
    solving for the tangency keeps that G1 continuity at every sampled row
    instead of leaving a kink whose size drifts with the parameters."""
    dx, dz = px - cx, pz - cz
    d = math.hypot(dx, dz)
    a = math.acos(min(1.0, r / max(d, 1e-9)))
    t = math.atan2(dz, dx) + side * a
    return cx + r * math.cos(t), cz + r * math.sin(t)


def _body_wire(wp, x_sh, z_top, x_pin, z_pin, r_lobe, w_base, z_base):
    """The datasheet's body outline: flat top face, sloped flanks running
    tangentially into a round lobe at each pin, and a flat base.

    This is NOT a ring with a tang hung off it and it is NOT a plain trapezoid.
    The two widest points of the casting are the LOBES, they sit BELOW the tube
    centre, and the 107 overall width is measured from the left lobe across to
    the tab tip. Modelling the corners as sharp fillets at tube-centre height
    put the silhouette 13 mm narrow and made the part read as a box."""
    tr_t = _tangent(x_sh, z_top, x_pin, z_pin, r_lobe, -1)      # upper tangency
    tr_b = _tangent(w_base, z_base, x_pin, z_pin, r_lobe, +1)   # lower tangency
    out = (x_pin + r_lobe, z_pin)                               # lobe apex
    return (wp.moveTo(-x_sh, z_top)
            .lineTo(x_sh, z_top)
            .lineTo(*tr_t)
            .threePointArc(out, tr_b)
            .lineTo(w_base, z_base)
            .lineTo(-w_base, z_base)
            .lineTo(-tr_b[0], tr_b[1])
            .threePointArc((-out[0], out[1]), (-tr_t[0], tr_t[1]))
            .close())


def _strap_wire(wp, r_i, r_out, x_sh, z_top, z_tab_lo, z_tab_hi, x_tab, r_nose):
    """The closure strap: a band on the barrel that runs out into the flat tab.

    Bounded below by the bore (which is where it grips) from the hinge end
    round to where the tab underside leaves the tube, and above by a straight
    taper off the hinge end onto the r_out crown arc and then the tab's flat
    top. The old model put a 30 x 50 x 20 rectangular BLOCK here; the real
    closure is a cantilevered plate with open air under it, and that gap is the
    most recognisable thing about the part."""
    a_lo = math.asin(max(-1.0, min(1.0, z_tab_lo / r_i)))       # bore -> tab underside
    a_hi = math.asin(max(-1.0, min(1.0, z_tab_hi / r_out)))     # crown -> tab top
    t_up = _tangent(-x_sh, z_top, 0.0, 0.0, r_out, -1)          # taper off the hinge end
    a_up = math.atan2(t_up[1], t_up[0])
    a_crown = 0.5 * (a_up + a_hi)
    x_jaw = math.sqrt(max(r_i ** 2 - z_top ** 2, 1e-9))
    a_end = math.atan2(z_top, -x_jaw)
    a_bore = 0.5 * (a_end + a_lo)
    k = 0.7071 * r_nose
    return (wp.moveTo(-x_sh, z_top)
            .lineTo(-x_jaw, z_top)
            .threePointArc((r_i * math.cos(a_bore), r_i * math.sin(a_bore)),
                           (r_i * math.cos(a_lo), r_i * math.sin(a_lo)))
            .lineTo(x_tab - r_nose, z_tab_lo)
            .threePointArc((x_tab - r_nose + k, z_tab_lo + r_nose - k),
                           (x_tab, z_tab_lo + r_nose))
            .lineTo(x_tab, z_tab_hi - r_nose)
            .threePointArc((x_tab - r_nose + k, z_tab_hi - r_nose + k),
                           (x_tab - r_nose, z_tab_hi))
            .lineTo(r_out * math.cos(a_hi), z_tab_hi)
            .threePointArc((r_out * math.cos(a_crown), r_out * math.sin(a_crown)),
                           t_up)
            .close())


def _ring_stack(x_c, z0, z1, pitch, r_root, r_crest, phase):
    """Axisymmetric thread rings about the vertical axis at x_c: one annular
    ring of axial width 0.4*pitch every pitch, from z0 to z1, offset by phase."""
    rings = None
    z = z0 + phase
    while z + 0.4 * pitch <= z1:
        ring = (
            cq.Workplane("XY", origin=(x_c, 0.0, z))
            .circle(r_crest)
            .circle(r_root)
            .extrude(0.4 * pitch)
        )
        rings = ring if rings is None else rings.union(ring)
        z += pitch
    return rings


def build(bore_d, wall_t, body_w, base_drop, tang_t, hang_d, lug_h, stud,
          closing_bolt_d=10.0):
    r_i = bore_d / 2.0
    r_o = r_i + wall_t
    bolt_d, pitch = _hardware(closing_bolt_d)
    d2, d3, e_span, h_nut, m_boss, g1, g2, r1, r4 = _din315d(bolt_d)
    pin_d = max(5.0, 0.5 * hang_d)               # hinge / pivot roll pin Ø
    fit = 0.15                                   # radial pin clearance

    # ── the datasheet front view, normalised on the barrel radius ────────────
    # (pixel readings at Ø51 in NOTES.md: pins ±34.1 at z=-12.0, lobes r 12.5,
    #  top face z=+2.9 out to x=39.7, base half-width 25.5, tab tip +60.1)
    z_top = 0.113 * r_i                          # body top face, just over centre
    x_pin = max(1.337 * r_i, r_i + 0.5 * pin_d + 2.0)
    z_pin = -0.471 * r_i
    r_lobe = max(0.490 * r_i, 0.55 * pin_d + 3.0)
    t_strap = 1.35 * wall_t                      # strap thickness over the crown
    r_out = r_i + t_strap
    x_sh = max(1.557 * r_i, r_out + 2.0)         # top face outer corner
    w_base = 1.00 * r_i                          # base half-width
    z_base = -float(base_drop)
    # Tab top face. The nut boss reaches inboard to x_pin - d2/2, so the tab has
    # to have STARTED by there — otherwise the boss lands on the crown arc and
    # the nut interpenetrates the strap on the thick-wall rows (the crown is
    # higher than the tab, which is what the datasheet shows too).
    x_nut_in = max(x_pin - d2 / 2.0 - 0.8, 0.1)
    z_clear = math.sqrt(max(r_out ** 2 - x_nut_in ** 2, 0.0)) + 0.4
    z_tab_hi = min(max(1.122 * r_i, z_clear), 0.93 * r_out)   # tab top face
    z_tab_lo = max(z_tab_hi - lug_h, 0.30 * r_i)  # tab underside
    x_tab = 2.36 * r_i                           # tab tip -> the +X end of 107
    r_nose = 0.11 * r_i
    ear_w = 0.22 * body_w                        # one outer ear, each pin
    tongue_w = body_w - 2.0 * ear_w - 0.6        # strap tongue (0.3 gap a side)
    eye_w = min(0.30 * body_w, tongue_w - 2.0)   # bolt eye
    r_eye = pin_d / 2.0 + 0.26 * bolt_d + 1.4
    r_tongue = 0.62 * r_lobe

    def hinge_tongue(width, grow):
        """The strap's downward tongue at the hinge, and (grown) the pocket the
        body must give up for it: a boss around the pin plus the neck up to the
        top face."""
        boss = _y_cyl(-x_pin, 0.0, width, r_tongue + grow).translate((0.0, 0.0, z_pin))
        x0, x1 = -x_sh, -x_pin + r_tongue + grow
        # the neck runs 0.8 PAST the top face so the tongue lands inside the
        # strap: an exactly coplanar join there makes the fuse drop a body
        neck = _y_slab((x0 + x1) / 2.0, 0.0, z_pin, x1 - x0, width,
                       z_top - z_pin + 0.8 + grow)
        return boss.union(neck.val())

    def pivot_pocket(width, grow):
        """The slot the eyebolt swings in: a boss clearance around the pivot
        pin plus the channel the shank rises through to the top face."""
        boss = _y_cyl(x_pin, 0.0, width, r_eye + grow).translate((0.0, 0.0, z_pin))
        x0, x1 = x_pin - r_eye - grow, max(x_sh, x_pin + r_eye + grow) + 1.0
        neck = _y_slab((x0 + x1) / 2.0, 0.0, z_pin, x1 - x0, width,
                       z_top - z_pin + 0.8 + grow)
        return boss.union(neck.val())

    # ── 1. lower shell ───────────────────────────────────────────────────────
    lower = _y_prism(
        lambda wp: _body_wire(wp, x_sh, z_top, x_pin, z_pin, r_lobe, w_base, z_base),
        body_w,
    )
    lower = lower.cut(_y_cyl(0.0, 0.0, body_w + 2.0, r_i))        # the U-jaw
    lower = lower.cut(hinge_tongue(tongue_w + 0.6, 0.3).val())    # hinge pocket
    # the slot has to clear the SHANK as well as the eye: on the 30 mm slimline
    # body the eye is only 9 wide, and an M10 shank in a 9.8 slot cut into the
    # casting instead of swinging in it
    lower = lower.cut(
        pivot_pocket(max(eye_w + 0.8, bolt_d + 1.4), 0.4).val())   # eyebolt slot
    for x_c in (-x_pin, x_pin):                                   # roll-pin bores
        lower = lower.cut(_y_cyl(x_c, 0.0, 2.0 * body_w, pin_d / 2.0 + fit)
                          .translate((0.0, 0.0, z_pin)).val())

    if stud:
        # T57200's hanging stud is M12x50 protruding 34 — it belongs to the
        # FIXING system (hang_d), not to the swing closing bolt.
        stud_len = 34.0
        stud_d = hang_d - 0.7                    # M12 nominal under a Ø12.7 bore
        stud_pitch = 1.75 if stud_d >= 11.0 else 1.5
        r_stud_minor = stud_d / 2.0 - 0.61 * stud_pitch
        lower = lower.union(
            cq.Workplane("XY").circle(r_stud_minor).extrude(-stud_len)
            .translate((0.0, 0.0, z_base))
        )
        srings = _ring_stack(0.0, z_base - stud_len + 0.3 * stud_d,
                             z_base - 0.2, stud_pitch,
                             r_stud_minor - 0.01, stud_d / 2.0, 0.0)
        if srings is not None:
            lower = lower.union(srings)
    else:
        # The sheet's fixing is VERTICAL: a Ø12.7 bore drilled 16 up from the
        # base face into the captive-nut window, so the M12 hangs the fixture
        # from below and threads into the nut sitting in the window. The window
        # is `tang_t` (19) wide ACROSS the clamp and open along the tube — the
        # two solid lines the sheet dimensions its 19 to — because 19 is the
        # A/F of the M12 nut and those walls are what stop it spinning.
        z_hole = z_base + 1.26 * hang_d              # sheet's 16 at hang_d 12.7
        # capped 1.5 mm short of the jaw: on the deep-tang rows a full-height
        # window would break through into the barrel bore
        win_h = min(0.82 * tang_t, (-r_i - 1.5) - z_hole)
        lower = lower.cut(
            _y_slab(0.0, 0.0, z_hole, tang_t, body_w + 2.0, win_h).val()
        )
        lower = lower.cut(
            cq.Workplane("XY").circle(hang_d / 2.0)
            .extrude(-(base_drop + 2.0))
            .translate((0.0, 0.0, z_hole + 0.1)).val()
        )

    # ── 2. upper shell — the closure strap + tab ─────────────────────────────
    upper = _y_prism(
        lambda wp: _strap_wire(wp, r_i, r_out, x_sh, z_top,
                               z_tab_lo, z_tab_hi, x_tab, r_nose),
        body_w,
    )
    upper = upper.union(hinge_tongue(tongue_w, 0.0).val())
    upper = upper.cut(_y_cyl(0.0, 0.0, body_w + 2.0, r_i).val())   # keep the barrel clear
    # the tab's slot is OPEN at +X: that is how the eyebolt swings clear and
    # the clamp comes off the barrel
    upper = upper.cut(
        _y_slab((x_pin - bolt_d / 2.0 - 0.7 + x_tab + 2.0) / 2.0, 0.0,
                z_tab_lo - 1.0,
                (x_tab + 2.0) - (x_pin - bolt_d / 2.0 - 0.7), bolt_d + 1.4,
                lug_h + 2.0).val()
    )
    upper = upper.cut(_y_cyl(-x_pin, 0.0, 2.0 * body_w, pin_d / 2.0 + fit)
                      .translate((0.0, 0.0, z_pin)).val())

    # ── 3./5. hinge pin and bolt pivot pin ───────────────────────────────────
    hinge_pin = _y_cyl(0.0, 0.0, body_w - 0.4, pin_d / 2.0)
    pivot_pin = _y_cyl(0.0, 0.0, body_w - 0.4, pin_d / 2.0)

    # ── 4. closing bolt ──────────────────────────────────────────────────────
    # The wing-nut row is needed first: the datasheet's 116 overall height is
    # measured to the eyebolt TIP protruding above the nut with the clamp shut,
    # so the bolt has to be cut to the nut, not to the tab.
    z_n0 = z_tab_hi + 0.3                        # nut bearing face, 0.3 over the tab
    z_bolt_top = z_n0 + h_nut + 0.86 * bolt_d
    r_minor = bolt_d / 2.0 - 0.61 * pitch
    # built in the assembly's own Z (eye on the pivot line), placed by x only
    bolt = _y_cyl(0.0, 0.0, eye_w, r_eye - 0.6).translate((0.0, 0.0, z_pin))
    bolt = bolt.union(
        cq.Workplane("XY").circle(bolt_d / 2.0).extrude(z_tab_hi - z_pin)
        .translate((0.0, 0.0, z_pin)))           # plain shank up through the slot
    bolt = bolt.union(
        cq.Workplane("XY").circle(r_minor).extrude(z_bolt_top - z_tab_hi + 1.0)
        .translate((0.0, 0.0, z_tab_hi - 1.0)))  # thread core, 1 mm into the shank
    bolt = bolt.cut(_y_cyl(0.0, 0.0, 2.0 * eye_w, pin_d / 2.0 + fit)
                    .translate((0.0, 0.0, z_pin)).val())
    z_t0 = z_tab_hi + 0.5                        # thread rings start over the tab
    z_t1 = z_bolt_top - 0.3 * bolt_d             # plain tip above
    ext = _ring_stack(0.0, z_t0, z_t1, pitch, r_minor - 0.01, bolt_d / 2.0, 0.0)
    if ext is not None:
        bolt = bolt.union(ext)

    # ── 6. wing nut — DIN 315-D rounded wing, on the closing bolt ────────────
    # The datasheet's front view (the one carrying the 107) shows the wings
    # splayed IN THAT PLANE, with a hex-to-round boss under them; the side view
    # shows only a narrow rib. So the wings lie in XZ, not along the tube axis.
    r_bore = bolt_d / 2.0 + 0.35 * pitch         # bore at the nut thread root

    # boss: Ø d2 at the bearing face tapering to Ø d3 at the top
    nut = (cq.Workplane("XY", origin=(0.0, 0.0, z_n0))
           .circle(d2 / 2.0).workplane(offset=m_boss).circle(d3 / 2.0).loft())
    wing = _wing(e_span, h_nut, m_boss, d2 / 2.0, g2, r1, r4)
    # g2 -> g1 wedge: shave both faces from the boss wall out to the ear
    for face in (1.0, -1.0):
        wing = wing.cut(
            cq.Workplane("XZ")
            .polyline([(d2 / 2.0, g2 / 2.0), (e_span / 2.0, g1 / 2.0),
                       (e_span / 2.0, g2), (d2 / 2.0, g2)]).close()
            .extrude(face * 2.0 * h_nut))
    wing = wing.translate((0.0, 0.0, z_n0))

    # r3 flare: loft the lune along the boss cone (the tangency radius grows
    # from d3/2 at the boss top to d2/2 at the bearing face) and clip it to the
    # wing's own silhouette, so the plate meets the boss on a radius instead of
    # a hard seam.
    r3 = max(0.06 * d2, 0.6)
    prism = _wing(e_span, h_nut, m_boss, d2 / 2.0, 2.0 * (g2 / 2.0 + r3 + 1.0),
                  r1, r4).translate((0.0, 0.0, z_n0))
    for mir in (False, True):
        wp = cq.Workplane("XY", origin=(0.0, 0.0, z_n0))
        wp = _lune(wp, d2 / 2.0, r3, g2 / 2.0)
        wp = _lune(wp.workplane(offset=m_boss), d3 / 2.0, r3, g2 / 2.0)
        try:
            flare = wp.loft().intersect(prism)
        except Exception:
            break                                  # degenerate row: skip the flare
        flare = flare.mirror("XZ") if mir else flare
        wing = wing.union(flare)
    nut = nut.union(wing).union(wing.mirror("YZ"))

    nut = nut.cut(cq.Workplane("XY", origin=(0.0, 0.0, z_n0 - bolt_d))
                  .circle(r_bore).extrude(h_nut + 3.0 * bolt_d))
    inr = _ring_stack(0.0, z_t0, z_n0 + m_boss - 0.2, pitch,
                      bolt_d / 2.0 - 0.25 * pitch, r_bore + 0.01,
                      phase=0.5 * pitch)         # same grid as the bolt rings,
                                                 # half a pitch over: nested
    if inr is not None:
        nut = nut.union(inr)

    # shells carry the assembly frame; hardware is built about its own axis
    # and placed on the hinge (-x_pin) / pivot (+x_pin) lines by Location
    result = cq.Assembly(name="truss_half_coupler_hook")
    result.add(lower, name="lower_shell")
    result.add(upper, name="upper_shell")
    result.add(hinge_pin, name="hinge_pin", loc=cq.Location((-x_pin, 0.0, z_pin)))
    result.add(bolt, name="closing_bolt", loc=cq.Location((x_pin, 0.0, 0.0)))
    result.add(pivot_pin, name="pivot_pin", loc=cq.Location((x_pin, 0.0, z_pin)))
    result.add(nut, name="wing_nut", loc=cq.Location((x_pin, 0.0, 0.0)))
    return result
