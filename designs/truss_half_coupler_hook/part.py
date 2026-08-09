"""truss_half_coupler_hook — the parametric part (assembly, solids=8).

A stage/theatre half coupler / hook clamp (Doughty T57000/T57200 class) drawn
closed around the (phantom) Ø48-51 mm barrel, as the eight parts it is
assembled from. The outline is taken off the datasheet front view
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
    3. hinge pin    — ISO 8752 slotted spring pin through the body's left ears
                      and the tongue (hollow C-section, as the sheet draws it)
    4. closing bolt — eye on the pivot pin, plain shank up through the open
                      tab slot, ring-thread top (revolved rings, no helix)
    5. pivot pin    — ISO 8752 spring pin through the right ears and bolt eye
    6. washer       — ISO 7089 plain washer bridging the tab's open slot
    7. hex nut      — ISO 4032 hexagon nut on the washer
    8. wing nut     — DIN 315-D butterfly on top of the hex nut

The sheet draws all three of 6/7/8 on the eyebolt, not just the wing nut. The
hex nut and the wing nut thread onto the SAME ring grid as the bolt, each
taking its own stretch of it (half a pitch over the bolt's rings, radially
nested) — engaged, with zero interpenetration.

Every mate is contact-or-clearance, never fused: the strap is held by the hinge
pin (0.15 mm radial) and BEARS on the body's left shoulder, which is the only
face contact in the assembly; the bolt clears its tab slot by 0.7 mm a side,
and the washer / hex nut / wing nut stack stands off 0.2 mm at each step. Tube
axis is Y. The strap does NOT close onto the body — the
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


# DIN 315 rounded-wing form, verbatim from BenchCAD's own wing_nut family
# (Cadance cad_synth/families/wing_nut.py) so the wing nut on this clamp is the
# same part the corpus draws everywhere else. Symbols:
#   d2 boss Ø at the bearing face · m boss height · e span over the wing tips
#   h overall height · d3 the ear THICKNESS driver (Y thickness = d3/4, not a
#   diameter) · hole_d the through-hole
# An earlier revision of this family carried a different table under the same
# "DIN 315" name — 63.5 span at M12 against 55 here, 49.5 at M10 against 45 —
# and a hand-tuned wing profile that came out as a pair of round blobs. Both
# are replaced by the corpus form.
_DIN315 = {
    3.0:  (8.0,   4.0, 19.0, 10.0,  6.0,  3.2),
    4.0:  (10.0,  5.0, 25.0, 12.0,  8.0,  4.3),
    5.0:  (12.0,  6.0, 30.0, 14.0, 10.0,  5.3),
    6.0:  (14.0,  8.0, 35.0, 16.0, 11.0,  6.4),
    8.0:  (16.0, 10.0, 39.0, 20.0, 12.5,  8.4),
    10.0: (20.0, 12.0, 45.0, 24.0, 16.0, 10.5),
    12.0: (24.0, 14.0, 55.0, 28.0, 20.0, 13.0),
    16.0: (32.0, 18.0, 70.0, 36.0, 26.0, 17.0),
    20.0: (40.0, 22.0, 90.0, 44.0, 32.0, 21.0),
}
HUB_TOP_RATIO = 1.0 / 3.0      # boss top radius = d2/3   (family default)
EAR_THICK_RATIO = 1.0 / 8.0    # ear Y thickness = d3/4   (family default)
EAR_FILLET_RATIO = 0.8         # on the ear perimeter     (family default)


# ISO 7089 plain washer, 200 HV, product grade A: d1 · d2 · h by nominal size.
# ISO 4032 style-1 hexagon nut: s (width across flats) · m (height) by thread.
# Both are what the datasheet actually draws under the wing nut — see NOTES.
_ISO7089 = {8.0: (8.4, 16.0, 1.6), 10.0: (10.5, 20.0, 2.0),
            12.0: (13.0, 24.0, 2.5), 16.0: (17.0, 30.0, 3.0)}
_ISO4032 = {8.0: (13.0, 6.8), 10.0: (16.0, 8.4), 12.0: (18.0, 10.8),
            16.0: (24.0, 14.8)}


def _std_row(table, d1):
    """The row of ``table`` nearest thread Ø ``d1``, scaled to the actual Ø so
    a non-tabulated bolt still gets proportionate hardware."""
    nom = min(table, key=lambda k: abs(k - d1))
    k = d1 / nom
    return tuple(v * k for v in table[nom])


def _din315(d1):
    """The DIN 315 row nearest ``d1``, scaled to the actual thread Ø so the nut
    still screws onto a non-tabulated bolt. Returns (d2, m, e, h, d3, hole_d)."""
    return _std_row(_DIN315, d1)


def _wing(d2, d3, e, h, m):
    """ONE ear on the +X side, built exactly as BenchCAD's wing_nut family
    draws a DIN 315 rounded wing (Cadance cad_synth/families/wing_nut.py):

        (0,0) -> (d2/2, 0) -> 45 deg take-off to (e/2, e/2 - d2/2)
              -> three-point arc up to the apex (e/4 + d2/4, h)
              -> back in to (d3/2, m) -> (0, m), closed

    extruded both ways by d3*EAR_THICK_RATIO/2, i.e. a flat plate of thickness
    d3/4 lying in XZ. The arc radius is the closed form the family derives —
    R = (dX^2 + dZ^2) / (2 dZ) about a centre directly under the apex — not a
    hand-picked ear radius.
    """
    x_arc = e / 4.0 + d2 / 4.0
    x_end, z_end = e / 2.0, e / 2.0 - d2 / 2.0
    dx, dz = x_end - x_arc, h - z_end
    r = (dx * dx + dz * dz) / (2.0 * dz)
    z_c = h - r
    a_mid = (math.atan2(z_end - z_c, dx) + math.pi / 2.0) / 2.0
    mid = (x_arc + r * math.cos(a_mid), z_c + r * math.sin(a_mid))
    return (cq.Workplane("XZ")
            .moveTo(0.0, 0.0)
            .lineTo(d2 / 2.0, 0.0)
            .lineTo(x_end, z_end)
            .threePointArc(mid, (x_arc, h))
            .lineTo(d3 / 2.0, m)
            .lineTo(0.0, m)
            .close()
            .extrude(d3 * EAR_THICK_RATIO / 2.0, both=True))


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


# ISO 8752 / DIN 1481 heavy-duty slotted spring pin: wall thickness s by
# nominal Ø. The datasheet draws both pins as two concentric circles broken by
# a slot, which is this pin and not a solid dowel.
_ISO8752_S = {3.0: 0.6, 4.0: 0.8, 5.0: 1.0, 6.0: 1.25, 8.0: 1.5,
              10.0: 2.0, 12.0: 2.5}


def _roll_pin(pin_d, length):
    """A slotted spring pin: a C-section tube, wall per ISO 8752, with the slot
    opening downward the way the sheet's pin circles are broken.

    The slot width is NOT tabulated by the standard (it is a free-state
    manufacturing dimension that closes on driving), so it is a proportion."""
    nom = min(_ISO8752_S, key=lambda k: abs(k - pin_d))
    s = _ISO8752_S[nom] * pin_d / nom
    slot_w = 0.20 * pin_d                        # proportion, not from ISO 8752
    pin = _y_cyl(0.0, 0.0, length, pin_d / 2.0).cut(
        _y_cyl(0.0, 0.0, length + 2.0, pin_d / 2.0 - s).val())
    return pin.cut(
        _y_slab(0.0, 0.0, -pin_d, slot_w, length + 2.0, pin_d).val())


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


def _body_wire(wp, z_top, x_pin, z_pin, r_lobe, w_base, z_base):
    """The body outline as the manufacturer's own STEP model has it: a flat top
    face TANGENT TO THE TOP OF EACH PIN LOBE, the lobe arc from there round to
    a tangency with the sloped flank, and a flat base.

    The two widest points of the casting are the LOBES, they sit BELOW the tube
    centre, and the 107 overall width is measured from the left lobe across to
    the closure-tab tip. There is no separate "shoulder corner": the top face
    ends exactly at x = x_pin, where it meets the lobe tangentially, so the
    whole upper outline is one G1 curve."""
    tr_b = _tangent(w_base, z_base, x_pin, z_pin, r_lobe, +1)   # flank tangency
    out = (x_pin + r_lobe, z_pin)                               # lobe apex
    return (wp.moveTo(-x_pin, z_top)
            .lineTo(x_pin, z_top)
            .threePointArc(out, tr_b)
            .lineTo(w_base, z_base)
            .lineTo(-w_base, z_base)
            .lineTo(-tr_b[0], tr_b[1])
            .threePointArc((-out[0], out[1]), (-x_pin, z_top))
            .close())


def _strap_wire(wp, r_i, r_out, x_pin, z_pin, r_lobe, z_tab_lo, z_tab_hi,
                x_tab, r_nose):
    """The closure strap, hinge knuckle included, as one profile.

    Its hinge end is a FULL round knuckle of radius r_lobe about the hinge pin
    — the same radius as the body's own lobe, so strap and body finish flush at
    x = -(x_pin + r_lobe), which is the -X end of the 107. Modelling it as a
    small stub buried inside the body left the knuckle 4 mm shy of the
    silhouette and gave the joint nothing to carry load on.

    That knuckle is externally TANGENT to the barrel bore: x_pin^2 + z_pin^2 =
    (r_i + r_lobe)^2 holds exactly on the manufacturer's model, so the inner
    surface runs off the bore straight onto the knuckle with no step. The outer
    surface is the common external tangent of the knuckle and the r_out crown."""
    a_lo = math.asin(max(-1.0, min(1.0, z_tab_lo / r_i)))       # bore -> tab underside
    a_hi = math.asin(max(-1.0, min(1.0, z_tab_hi / r_out)))     # crown -> tab top
    ct = (-x_pin, z_pin)
    # common external tangent of the knuckle (ct, r_lobe) and the crown (0, r_out)
    dx, dz = -ct[0], -ct[1]
    dl = math.hypot(dx, dz)
    an = math.atan2(dz, dx) + math.acos(
        max(-1.0, min(1.0, -(r_out - r_lobe) / dl)))
    nx, nz = math.cos(an), math.sin(an)
    t_lobe = (ct[0] + r_lobe * nx, ct[1] + r_lobe * nz)
    t_out = (r_out * nx, r_out * nz)
    # the bore and the knuckle touch here — one point, no step
    p_t = (ct[0] * r_i / (r_i + r_lobe), ct[1] * r_i / (r_i + r_lobe))
    a_bore = 0.5 * (math.atan2(p_t[1], p_t[0]) + a_lo)
    a_kn = math.atan2(t_lobe[1] - ct[1], t_lobe[0] - ct[0])     # around the OUTSIDE
    a_pt = math.atan2(p_t[1] - ct[1], p_t[0] - ct[0])
    m_kn = 0.5 * (a_kn + (a_pt + 2.0 * math.pi))
    a_crown = 0.5 * (an + a_hi)
    k = 0.7071 * r_nose
    return (wp.moveTo(*p_t)
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
                           t_out)
            .lineTo(*t_lobe)
            .threePointArc((ct[0] + r_lobe * math.cos(m_kn),
                            ct[1] + r_lobe * math.sin(m_kn)), p_t)
            .close())


def _ring_stack(x_c, z0, z1, pitch, r_root, r_crest, phase, z_min=None):
    """Axisymmetric thread rings about the vertical axis at x_c: one annular
    ring of axial width 0.4*pitch every pitch, from z0 to z1, offset by phase.

    ``z_min`` skips the rings below it WITHOUT moving the grid, so two nuts
    running on the same bolt (the hex nut and the wing nut above it) each get
    their own stretch of the one thread instead of two grids that collide."""
    rings = None
    z = z0 + phase
    while z + 0.4 * pitch <= z1:
        if z_min is None or z >= z_min:
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
    bolt_d, pitch = _hardware(closing_bolt_d)
    d2, m_boss, e_span, h_nut, d3, _hole_d = _din315(bolt_d)
    w_d1, w_d2, w_h = _std_row(_ISO7089, bolt_d)     # plain washer
    n_s, n_m = _std_row(_ISO4032, bolt_d)            # hexagon nut
    pin_d = 0.75 * hang_d                        # ISO 8752 spring pin, Ø9.5 at Ø12.7
    fit = 0.15                                   # radial pin clearance

    # ── proportions read off the manufacturer's own STEP model ───────────────
    # (T57000-T57010.step; every ratio below is one of its exact dimensions
    #  divided by the Ø50.8 bore radius — see NOTES.md)
    x_pin = 1.3780 * r_i                         # 35.00 : pin centres
    r_lobe = 0.4724 * r_i                        # 12.00 : the round pin lobe
    # The lobe is externally TANGENT to the barrel bore — x_pin^2 + z_pin^2 =
    # (r_i + r_lobe)^2 holds to 4 decimals on the STEP model. Deriving z_pin
    # from it instead of carrying an independent ratio keeps the joint on the
    # bore at every sampled row, which is what makes strap and body finish
    # flush instead of stepping.
    z_pin = -math.sqrt(max((r_i + r_lobe) ** 2 - x_pin ** 2, 1e-9))   # -13.18
    z_top = z_pin + r_lobe                       # -1.18 : top face, tangent to the lobe
    t_strap = 1.35 * wall_t                      # strap thickness over the crown
    r_out = r_i + t_strap                        # 35.40 at the anchor wall
    w_base = 0.9843 * r_i                        # 25.00 : base half-width
    z_base = -float(base_drop)
    x_slot = 0.6862 * r_i                        # 17.43 : inboard end of both slots
    z_slot = -1.1720 * r_i                       # -29.77 : floor of both slots
    # Tab top face. The washer/nut boss reaches inboard to x_pin - d/2, so the
    # tab has to have STARTED by there — otherwise it lands on the crown arc
    # and the stack interpenetrates the strap on the thick-wall rows.
    x_nut_in = max(x_pin - max(d2, w_d2) / 2.0 - 0.8, 0.1)
    z_clear = math.sqrt(max(r_out ** 2 - x_nut_in ** 2, 0.0)) + 0.4
    z_tab_hi = min(max(1.0524 * r_i, z_clear), 0.93 * r_out)   # 26.73 : tab top
    z_tab_lo = max(z_tab_hi - lug_h, 0.30 * r_i)  # tab underside
    x_tab = 2.3657 * r_i                         # 60.09 : tab tip, the +X end of 107
    r_nose = 0.1575 * r_i                        # 4.00 : tab nose
    z_band = 0.0602 * r_i                        # 1.53 : below this the strap
    tongue_w = 0.5600 * body_w                   # 28.00 : narrows to the tongue
    pocket_w = 0.5900 * body_w                   # 29.50 : 0.75 clearance a side
    eye_w = bolt_d                               # 12.00 : eye thickness = thread Ø
    slot_w = bolt_d + 2.0                        # 14.00 : 1.0 clearance a side
    r_eye = 0.84 * bolt_d                        # 10.10 : eye outer radius

    def joint_slot(sign, width):
        """The slot each joint swings in: milled straight in from the outside
        face, |x| >= x_slot, down to z_slot, open through the top.

        The STEP model cuts both joints this way — a full-depth clevis, not the
        small closed pocket this part used to have. On the hinge side it is
        what lets the strap's knuckle sit flush with the body's lobe; on the
        pivot side it is what lets the eyebolt swing right out of the casting
        instead of jamming on its own lobe after 20 degrees."""
        x0 = sign * x_slot
        x1 = sign * (x_pin + r_lobe + 4.0)
        return _y_slab((x0 + x1) / 2.0, 0.0, z_slot, abs(x1 - x0), width,
                       z_top - z_slot + 4.0)

    # ── 1. lower shell ───────────────────────────────────────────────────────
    lower = _y_prism(
        lambda wp: _body_wire(wp, z_top, x_pin, z_pin, r_lobe, w_base, z_base),
        body_w,
    )
    lower = lower.cut(_y_cyl(0.0, 0.0, body_w + 2.0, r_i))        # the U-jaw
    lower = lower.cut(joint_slot(-1.0, pocket_w).val())           # hinge clevis
    lower = lower.cut(joint_slot(+1.0, slot_w).val())             # eyebolt clevis
    for x_c in (-x_pin, x_pin):                                   # spring-pin bores
        lower = lower.cut(_y_cyl(x_c, 0.0, 2.0 * body_w, pin_d / 2.0)
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
        # The fixing is VERTICAL: a Ø12.7 bore up from the base face into the
        # captive-nut window, so the M12 hangs the fixture from below and
        # threads into the nut sitting in the window. On the STEP model that
        # bore is 19.0 = 1.5 * Ø12.7 deep, and the window above it runs ALL THE
        # WAY UP INTO THE JAW — its top edge lies exactly on the barrel bore,
        # which is how you see it looking down into the trough on the real
        # part. Leaving a floor between window and jaw, as this part used to,
        # closes the pocket the nut is dropped into.
        z_hole = z_base + 1.5 * hang_d
        lower = lower.cut(
            _y_slab(0.0, 0.0, z_hole, tang_t, body_w + 2.0,
                    (-r_i) - z_hole + 0.1).val()
        )
        lower = lower.cut(
            cq.Workplane("XY").circle(hang_d / 2.0)
            .extrude(-(base_drop + 2.0))
            .translate((0.0, 0.0, z_hole + 0.1)).val()
        )

    # ── 2. upper shell — the closure strap + tab ─────────────────────────────
    upper = _y_prism(
        lambda wp: _strap_wire(wp, r_i, r_out, x_pin, z_pin, r_lobe,
                               z_tab_lo, z_tab_hi, x_tab, r_nose),
        body_w,
    )
    # Below z_band the strap narrows to the tongue that goes into the body's
    # clevis; above it, it is the full body width. One profile, then the two
    # side slabs taken off the bottom of it -- which is how the STEP model has
    # it, and it keeps the knuckle a single continuous piece with the band.
    for sy in (1.0, -1.0):
        upper = upper.cut(
            _y_slab(0.0, sy * (tongue_w + body_w) / 4.0,
                    z_pin - r_lobe - 4.0,
                    4.0 * x_tab, (body_w - tongue_w) / 2.0,
                    z_band - (z_pin - r_lobe) + 4.0).val())
    upper = upper.cut(_y_cyl(0.0, 0.0, body_w + 2.0, r_i).val())   # keep the barrel clear
    # the tab's slot is OPEN at +X: that is how the eyebolt swings clear and
    # the clamp comes off the barrel
    upper = upper.cut(
        _y_slab((x_pin - bolt_d / 2.0 - 1.0 + x_tab + 2.0) / 2.0, 0.0,
                z_tab_lo - 1.0,
                (x_tab + 2.0) - (x_pin - bolt_d / 2.0 - 1.0), slot_w,
                lug_h + 2.0).val()
    )
    upper = upper.cut(_y_cyl(-x_pin, 0.0, 2.0 * body_w, pin_d / 2.0 + fit)
                      .translate((0.0, 0.0, z_pin)).val())

    # ── 3./5. hinge pin and bolt pivot pin ───────────────────────────────────
    hinge_pin = _roll_pin(pin_d, body_w - 0.4)
    pivot_pin = _roll_pin(pin_d, body_w - 0.4)

    # ── 4. closing bolt ──────────────────────────────────────────────────────
    # The wing-nut row is needed first: the datasheet's 116 overall height is
    # measured to the eyebolt TIP protruding above the nut with the clamp shut,
    # so the bolt has to be cut to the top of the whole nut stack. The sheet
    # draws THREE things on the eyebolt above the tab, not one: an ISO 7089
    # plain washer bridging the open tab slot, an ISO 4032 hexagon nut on it,
    # and the wing nut on top of that.
    z_w0 = z_tab_hi + 0.2                        # washer, 0.2 over the tab
    z_h0 = z_w0 + w_h + 0.2                      # hex nut, 0.2 over the washer
    z_n0 = z_h0 + n_m + 0.2                      # wing nut, 0.2 over the hex nut
    # The sheet's 116 is measured to the TOP OF THE WING NUT, not to a
    # protruding thread: with the clamp shut the eyebolt ends inside the nut's
    # threaded boss and never comes out the top, so the bolt is cut to there.
    z_bolt_top = z_n0 + m_boss + 0.35 * bolt_d
    r_minor = bolt_d / 2.0 - 0.61 * pitch
    # built in the assembly's own Z (eye on the pivot line), placed by x only
    bolt = _y_cyl(0.0, 0.0, eye_w, r_eye).translate((0.0, 0.0, z_pin))
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

    r_bore = bolt_d / 2.0 + 0.35 * pitch         # nut bore at the thread root

    # ── 6. ISO 7089 plain washer ─────────────────────────────────────────────
    # It bridges the tab's OPEN slot, which is why the sheet draws one: the hex
    # nut's A/F is narrower than the slot is long, so without it the nut would
    # bear on two thin slot edges.
    washer = (cq.Workplane("XY", origin=(0.0, 0.0, z_w0))
              .circle(w_d2 / 2.0).circle(w_d1 / 2.0).extrude(w_h))

    # ── 7. ISO 4032 hexagon nut ──────────────────────────────────────────────
    hex_nut = (cq.Workplane("XY", origin=(0.0, 0.0, z_h0))
               .polygon(6, n_s / math.cos(math.pi / 6.0)).extrude(n_m)
               .cut(cq.Workplane("XY", origin=(0.0, 0.0, z_h0 - 1.0))
                    .circle(r_bore).extrude(n_m + 2.0)))
    hex_rings = _ring_stack(0.0, z_t0, z_h0 + n_m - 0.15, pitch,
                            bolt_d / 2.0 - 0.25 * pitch, r_bore + 0.01,
                            phase=0.5 * pitch, z_min=z_h0 + 0.15)
    if hex_rings is not None:
        hex_nut = hex_nut.union(hex_rings)

    # ── 8. wing nut — DIN 315 rounded wing, on the closing bolt ─────────────
    # Same construction as BenchCAD's own wing_nut family, so this clamp's nut
    # is the part the corpus draws: a tapered boss (d2 at the bearing face to
    # d2/3 at the top over m) with two flat ears splayed at 45 deg in XZ. The
    # datasheet's front view — the one carrying the 107 — shows the wings
    # splayed in that plane and only a narrow rib in the side view, which is
    # why the ears lie in XZ and not along the tube axis.
    nut = (cq.Workplane("XY", origin=(0.0, 0.0, z_n0))
           .circle(d2 / 2.0).workplane(offset=m_boss)
           .circle(d2 * HUB_TOP_RATIO).loft())
    wing = _wing(d2, d3, e_span, h_nut, m_boss).translate((0.0, 0.0, z_n0))
    nut = nut.union(wing).union(wing.mirror("YZ"))

    nut = nut.cut(cq.Workplane("XY", origin=(0.0, 0.0, z_n0 - bolt_d))
                  .circle(r_bore).extrude(h_nut + 3.0 * bolt_d))
    # the family's own finish: round the ear perimeter (edges parallel to Y)
    nut = nut.edges("|Y").fillet(d3 * EAR_THICK_RATIO * EAR_FILLET_RATIO / 2.0)
    inr = _ring_stack(0.0, z_t0, z_n0 + m_boss - 0.2, pitch,
                      bolt_d / 2.0 - 0.25 * pitch, r_bore + 0.01,
                      phase=0.5 * pitch,         # same grid as the bolt rings,
                      z_min=z_n0 + 0.15)         # half a pitch over: nested
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
    result.add(washer, name="washer", loc=cq.Location((x_pin, 0.0, 0.0)))
    result.add(hex_nut, name="hex_nut", loc=cq.Location((x_pin, 0.0, 0.0)))
    result.add(nut, name="wing_nut", loc=cq.Location((x_pin, 0.0, 0.0)))
    return result
