"""truss_half_coupler_hook — the parametric part (assembly, solids=6).

A stage/theatre half coupler / hook clamp (Doughty T57000/T57200 class) as the
six parts it is assembled from, drawn closed around the (phantom) Ø48-51 mm
barrel:

    1. lower shell  — half ring below the split, hinge ears (-X), bolt-pivot
                      ears (+X), and the hanging tang with the vertical Ø12.7
                      fixing bore up into the captive-nut window (or the
                      hook-clamp's protruding M12 stud)
    2. upper shell  — half ring above the split, centre hinge knuckle (-X) and
                      the crown lug (+X) with the open slot the bolt swings into
    3. hinge pin    — through the ears + knuckle on the -X side
    4. closing bolt — pivot eye on the +X pin, plain shank up through the lug
                      slot, ring-thread top (revolved rings, no helix)
    5. pivot pin    — through the bolt-pivot ears + bolt eye
    6. wing nut     — DIN 315-style butterfly on the thread above the lug, its
                      internal thread rings interleaved half a pitch with the
                      bolt rings (engaged, zero interpenetration)

Every mate is contact-or-clearance, never fused: the shells meet only through
the hinge/pivot pins (0.15 mm radial pin clearance), the bolt clears its slot
by 0.6 mm a side, the nut hovers 0.3 mm over the lug with its rings nested
between the bolt rings. Tube axis is Y; the split plane is z=0 with a 0.6 mm
gap each side (the shells clamp shut on the barrel, absent here); the tang
drops -Z to the base plane at z = -base_drop.

Drawing symbols (Doughty sheet): barrel Ø48-51 -> bore_d; body width 50 ->
body_w; tube centre->base 55 -> base_drop; the Ø12.7 fixing bore -> hang_d,
drilled VERTICALLY up from the tang base (front view shows it as hidden
lines) into the captive-nut window; the sheet's 19 is BOTH the tang width
across the clamp (tang_t anchors on it) and the window's hex A/F (17 for
M10), window height 16 per the drawing; overall 107 across -> emerges from
x_h with the wing nut folded along the tube; pins at height 55 -> the z=0
pin axes.

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
    catalog's 107 mm overall width."""
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
    r_in = bore_d / 2.0
    r_out = r_in + wall_t
    gap = 0.6                                    # split-plane gap each side
    bolt_d, pitch = _hardware(closing_bolt_d)
    pin_d = max(5.0, 0.5 * hang_d)               # hinge / pivot pin Ø
    k_r = max(4.5, 0.8 * pin_d)                  # knuckle boss radius
    # the eye belongs to the CLOSING bolt, not to the base fixing bore; sized
    # off the pin it swings on, which is what the drawing's small pivot circles
    # show (outer Ø ~11 on a Ø6.35 pin), not 1.1x a thread diameter
    r_eye = pin_d / 2.0 + 2.4                    # bolt pivot-eye outer radius
    # Knuckle standoff measured off the T57000 front view: the pivot centres
    # sit ~4.3 mm outside the ring wall (+-35.8 about the bore on the anchor),
    # i.e. the bosses nestle INTO the shell rather than standing clear of it.
    # The old 2.2*k_r put them at +-46.2 and, once a real DIN 315-D wing nut
    # went on the bolt, pushed the wings ~20 mm past the catalog outline.
    x_h = r_out + max(0.85 * k_r, r_eye + 1.5)
    ear_w = 0.28 * body_w                        # each outer ear width
    knu_w = body_w - 2.0 * ear_w - 0.6           # centre width (0.3 mm gap a side)

    def half_annulus(sign):
        ring = _y_cyl(0.0, 0.0, body_w, r_out).cut(
            _y_cyl(0.0, 0.0, body_w + 2.0, r_in))
        if sign > 0:
            keep = _y_slab(0.0, 0.0, gap, 4.0 * r_out, 2.0 * body_w, 2.0 * r_out)
        else:
            keep = _y_slab(0.0, 0.0, -2.0 * r_out - gap, 4.0 * r_out, 2.0 * body_w, 2.0 * r_out)
        return ring.intersect(keep)

    def knuckle(x_c, y_c, width, sign):
        """Pin boss (cylinder about the pin axis) + a TAPERED cast arm
        blending it into the shell — the forging is smooth straps, not
        rectangular slabs."""
        b = _y_cyl(x_c, y_c, width, k_r)
        x0 = r_out - 0.6 * wall_t                # arm reaches into the shell wall
        x1 = abs(x_c)
        s = 1.0 if x_c > 0 else -1.0
        z0 = gap if sign > 0 else -k_r
        z1 = k_r if sign > 0 else -gap
        arm = (
            cq.Workplane("XZ", origin=(0.0, y_c + width / 2.0, 0.0))
            .moveTo(s * x0, z1)
            .lineTo(s * x1, (z1 - z0) * 0.5 + z0 + (z1 - z0) * 0.28)
            .lineTo(s * x1, z0 + (z1 - z0) * 0.22)
            .lineTo(s * x0, z0)
            .close()
            .extrude(width)
        )
        b = b.union(arm)
        return b

    # ---- 1. lower shell ------------------------------------------------------
    lower = half_annulus(-1)
    y_ear = body_w / 2.0 - ear_w / 2.0
    for x_c in (-x_h, x_h):
        for y_c in (-y_ear, y_ear):
            lower = lower.union(knuckle(x_c, y_c, ear_w, -1))
    # ---- triangular plate body ----------------------------------------------
    # The datasheet front view is NOT a ring with a tab hung off it: the body is
    # a TRIANGULAR PLATE whose upper corners are the two pivot lugs and whose
    # sides run straight down and inward to a flat bottom edge — the edge the
    # "tube centre -> base 55" is measured to, and the one the Ø12.7 fixing is
    # drilled up into. Modelling it as an annulus plus a rectangular tang gives
    # a circular silhouette that cannot reproduce the drawing's outline at all.
    w_base = 2.4 * tang_t                        # flat bottom edge width
    r_fil = min(6.0, 0.30 * tang_t)
    body = (cq.Workplane("XZ", origin=(0.0, body_w / 2.0, 0.0))
            .moveTo(-x_h, 0.0)
            .lineTo(x_h, 0.0)
            .lineTo(w_base / 2.0, -base_drop)
            .lineTo(-w_base / 2.0, -base_drop)
            .close()
            .extrude(body_w)
            .edges("|Y").fillet(r_fil)
            .cut(_y_cyl(0.0, 0.0, body_w + 2.0, r_in)))   # keep the barrel clear
    lower = lower.union(body)
    if stud:
        stud_len = 34.0                          # Doughty T57200: M12x50, 34 proud
        r_stud_minor = bolt_d / 2.0 - 0.61 * pitch
        lower = lower.union(
            cq.Workplane("XY").circle(r_stud_minor).extrude(-stud_len)
            .translate((0.0, 0.0, -base_drop))
        )
        # ring-thread the stud like the closing bolt (same NOTES-documented
        # substitution for the helix): rings over the protruding length
        srings = _ring_stack(0.0, -base_drop - stud_len + 0.3 * bolt_d,
                             -base_drop - 0.2, pitch,
                             r_stud_minor - 0.01, bolt_d / 2.0, 0.0)
        if srings is not None:
            lower = lower.union(srings)
    else:
        # the sheet's fixing is VERTICAL: a 12.7 bore drilled up from the tang
        # base into the captive-nut window, so the M12 hangs the fixture from
        # below and threads into the nut sitting in the window
        z_win = -(base_drop - 1.2 * hang_d)          # window centre height
        # A/F of the CAPTIVE FIXING nut, so it follows hang_d — not the closing
        # bolt. Once the two were decoupled, keying this off bolt_d put a 17 mm
        # window under an M12 (Ø12.7) fixing.
        af = 19.0 if hang_d >= 12.0 else 17.0
        # captive-nut window, THROUGH the tang across the tube (front view
        # shows it as hidden lines): parallel walls at the hex A/F along the
        # tube so the nut cannot spin; drawing slot height 16 (= 0.85 * 19)
        lower = lower.cut(
            _y_slab(0.0, 0.0, z_win - 0.425 * af, tang_t * 4.0, af, 0.85 * af)
        )
        lower = lower.cut(
            cq.Workplane("XY").circle(hang_d / 2.0)
            .extrude(-(base_drop + 2.0))
            .translate((0.0, 0.0, z_win))
        )

    # ---- 2. upper shell ------------------------------------------------------
    upper = half_annulus(+1)
    upper = upper.union(knuckle(-x_h, 0.0, knu_w, +1))
    z_l0 = max(r_eye + 2.5, k_r + 1.5)           # lug underside clears eye + boss
    lug_x0 = 0.35 * r_out                        # lug reaches back over the crown
    lug_x1 = x_h + 1.3 * k_r
    lug = (_y_slab((lug_x0 + lug_x1) / 2.0, 0.0, z_l0,
                   lug_x1 - lug_x0, body_w, lug_h)
           .edges("|Y").fillet(min(2.5, 0.28 * lug_h)))
    slot_x0 = x_h - (bolt_d / 2.0 + 0.6)
    slot = _y_slab((slot_x0 + lug_x1 + 2.0) / 2.0, 0.0, z_l0 - 1.0,
                   lug_x1 + 2.0 - slot_x0, bolt_d + 1.2, lug_h + 2.0)
    upper = upper.union(lug).cut(slot)

    # hinge + pivot bores through everything that wraps a pin
    for x_c in (-x_h, x_h):
        bore = _y_cyl(x_c, 0.0, 2.0 * body_w, pin_d / 2.0 + 0.15)
        lower = lower.cut(bore)
        upper = upper.cut(bore)

    # ---- 3./5. hinge pin and bolt pivot pin ----------------------------------
    hinge_pin = _y_cyl(0.0, 0.0, body_w - 0.4, pin_d / 2.0)
    pivot_pin = _y_cyl(0.0, 0.0, body_w - 0.4, pin_d / 2.0)

    # ---- 4. closing bolt -----------------------------------------------------
    z_lug_top = z_l0 + lug_h
    z_bolt_top = z_lug_top + 2.0 * bolt_d
    r_minor = bolt_d / 2.0 - 0.61 * pitch
    eye_w = 0.3 * body_w
    bolt = _y_cyl(0.0, 0.0, eye_w, r_eye).union(
        cq.Workplane("XY").circle(r_minor).extrude(z_bolt_top))
    bolt = bolt.cut(_y_cyl(0.0, 0.0, 2.0 * eye_w, pin_d / 2.0 + 0.15))
    z_t0 = z_lug_top + 0.5                       # thread rings start over the lug
    z_t1 = z_bolt_top - 0.3 * bolt_d             # plain tip above
    ext = _ring_stack(0.0, z_t0, z_t1, pitch, r_minor - 0.01, bolt_d / 2.0, 0.0)
    if ext is not None:
        bolt = bolt.union(ext)

    # ---- 6. wing nut — DIN 315 form D on the closing bolt --------------------
    # The datasheet's front view (the one carrying the 107) shows the wings
    # splayed IN THAT PLANE, with a hex-to-round boss under them; the side view
    # shows only a narrow rib. So the wings lie in XZ, not along the tube axis.
    d2, d3, e_span, h_nut, m_boss, g1, g2, r1, r4 = _din315d(bolt_d)
    z_n0 = z_lug_top + 0.3                       # bearing face, 0.3 over the lug
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
    # and placed on the hinge (-x_h) / pivot (+x_h) lines by Location
    result = cq.Assembly(name="truss_half_coupler_hook")
    result.add(lower, name="lower_shell")
    result.add(upper, name="upper_shell")
    result.add(hinge_pin, name="hinge_pin", loc=cq.Location((-x_h, 0.0, 0.0)))
    result.add(bolt, name="closing_bolt", loc=cq.Location((x_h, 0.0, 0.0)))
    result.add(pivot_pin, name="pivot_pin", loc=cq.Location((x_h, 0.0, 0.0)))
    result.add(nut, name="wing_nut", loc=cq.Location((x_h, 0.0, 0.0)))
    return result
