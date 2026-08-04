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

import cadquery as cq


def _hardware(hang_d):
    """Closing-bolt nominal Ø and ISO 261 coarse pitch from the fixing size:
    hang_d is the catalog clearance bore (Ø12.7 for M12, ~Ø10.5 for M10), so
    bolt nominal = clearance bore - 0.7 mm play."""
    bolt_d = hang_d - 0.7
    pitch = 1.5 if bolt_d < 11.0 else 1.75
    return bolt_d, pitch


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


def build(bore_d, wall_t, body_w, base_drop, tang_t, hang_d, lug_h, stud):
    r_in = bore_d / 2.0
    r_out = r_in + wall_t
    gap = 0.6                                    # split-plane gap each side
    bolt_d, pitch = _hardware(hang_d)
    pin_d = max(5.0, 0.5 * hang_d)               # hinge / pivot pin Ø
    k_r = max(4.5, 0.8 * pin_d)                  # knuckle boss radius
    r_eye = 1.1 * (hang_d - 0.7)                 # bolt pivot-eye outer radius
    # pin axes stand off the ring so boss and bolt eye clear the shell (the
    # drawing's 107 overall width vs the ~Ø60 ring: pivots sit well outside)
    x_h = r_out + max(2.2 * k_r, r_eye + 1.5)
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
    tang_h = base_drop - r_in
    tang = (_y_slab(0.0, 0.0, -base_drop, tang_t, body_w, tang_h)
            .edges("|Z").fillet(min(2.5, 0.2 * tang_t)))
    lower = lower.union(tang)
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
        af = 19.0 if bolt_d >= 11.0 else 17.0
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

    # ---- 6. wing nut (DIN 315 proportions: hub ~1.8d, wings span ~4.5d) ------
    r_hub = 0.9 * bolt_d
    nut_h = 1.1 * bolt_d
    z_n0 = z_lug_top + 0.3                       # hovers 0.3 over the lug face
    nut = (
        cq.Workplane("XY", origin=(0.0, 0.0, z_n0)).circle(r_hub).extrude(nut_h))
    # DIN 315 proportion: span = 2*(0.5*hub + wing) ~ 3.3*d (~40 on M12); the
    # wings run along the TUBE axis (Y), matching the folded pose the sheet's
    # 107 overall width is measured in
    wing_l, wing_t = 1.2 * bolt_d, 0.45 * bolt_d
    for sy in (-1.0, 1.0):
        y_wc = sy * (0.5 * r_hub + wing_l / 2.0)
        wing = _y_slab(0.0, y_wc, z_n0 + 0.25 * nut_h,
                       wing_t, wing_l, nut_h + 0.9 * bolt_d)
        wing = wing.edges("|X").fillet(0.3 * bolt_d)
        nut = nut.union(wing)
    r_bore = bolt_d / 2.0 + 0.35 * pitch         # bore at the nut thread root
    nut = nut.cut(
        cq.Workplane("XY", origin=(0.0, 0.0, z_n0 - bolt_d))
        .circle(r_bore)
        .extrude(nut_h + 3.0 * bolt_d))
    inr = _ring_stack(0.0, z_t0, z_n0 + nut_h - 0.2, pitch,
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
