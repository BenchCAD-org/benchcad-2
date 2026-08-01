"""Parametric RÖHM DURO-M three-jaw geared scroll chuck assembly.

Mechanism (RÖHM catalogue p.3035 cutaway, "Geared scroll chucks"): the chuck
key turns a radially arranged bevel PINION; its teeth mesh a bevel CROWN RING
on the back of the SCROLL PLATE; the scroll's front face carries a flat
Archimedean SPIRAL THREAD which engages arc teeth on the underside of the
three JAWS, feeding them radially in unison in their T-guideways.  All the
drive interfaces are modelled and engaged: spiral<->jaw teeth and
crown<->pinion teeth interleave with computed running clearances; no two
bodies share volume.

Symbol glossary (drawing dimension -> parameter):
  chuck table p.3048, DIN 6350 cylindrical centre mount:
    A  outer_dia_A       chuck outside diameter
    B  register_dia_B    rear centering recess diameter (H6)
    C  register_depth_C  rear centering recess depth
    D  height_D          axial body height
    E  bore_E            through-hole diameter
    F  bolt_circle_F     rear mounting bolt circle
    G  mount_thread_G    mounting thread nominal diameter (x mount_hole_count)
    K  key_square_K      chuck-key square
  jaw table p.3060, outward stepped jaw BB:
    A  jaw_length_A      jaw length            B  jaw_width_B   jaw width
    C  jaw_height_C      jaw overall height    F  jaw_step_F    top step length
    G  jaw_step_G        second step length    H  jaw_step_H    step height
    D  jaw_serration_D   underside serration band -> scroll thread pitch
    E  jaw_tongue_E      guide-tongue band -> T-flange height
  chucking ranges p.3044: A1 -> grip_min_A1 / grip_max_A1 (clamp_d inside).

Internal drive-train values the catalogue does not dimension (tooth counts,
bevel cone angles, thread section, clearances) are derived proportions,
documented in NOTES.md.  Bevel teeth are straight, planar-flank approximations
with a shared pitch-cone apex on the chuck axis (tan(delta_wheel) =
Z_wheel/Z_pinion, shaft angle 90 deg); the scroll thread is a rectangular-
section Archimedean band; jaw teeth are concentric arc segments at the local
spiral gap radii (the real 1/3-pitch stagger between jaws 1/2/3 emerges from
evaluating the spiral at each jaw's meridian).
"""

import cadquery as cq
import math

PINION_TEETH = 12          # straight-bevel pinion tooth count (proportion)
FLANK_HALF_DEG = 20.0      # tooth flank half-angle, both gears (proportion)
JAW_ANGLES = (0.0, 120.0, 240.0)
PINION_ANGLES = (60.0, 180.0, 300.0)


def _annulus(z0, height, outer_d, inner_d):
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, z0))
        .circle(outer_d / 2.0)
        .circle(inner_d / 2.0)
        .extrude(height)
    )


def _layout(outer_dia_A, height_D, bore_E, register_depth_C,
            jaw_serration_D, jaw_tongue_E, key_square_K):
    """Single source of truth for every internal drive-train dimension."""
    A, D = outer_dia_A, height_D
    L = {}
    clr = max(0.20, 0.004 * D)            # universal running clearance
    L["clr"] = clr

    # --- guideway / jaw-foot axial stack (from the face z=0 downward) ---
    neck_h = max(1.0, 0.55 * jaw_tongue_E)   # tongue neck (proportion of E band)
    L["neck_h"] = neck_h
    L["tier1_d"] = neck_h + clr              # narrow top-slot depth
    L["z_flange_top"] = -(L["tier1_d"] + clr)
    L["z_foot"] = L["z_flange_top"] - jaw_tongue_E   # flange bottom = foot plane
    L["z_floor"] = L["z_foot"]        # tier-2 floor / cavity top (flange rides it)

    # --- scroll thread (front of scroll plate) ---
    pitch = jaw_serration_D                  # spiral pitch = BB jaw dim D
    L["pitch"] = pitch
    L["thread_h"] = 0.55 * pitch             # square-ish thread depth
    L["ridge_w"] = 0.42 * pitch
    L["jaw_tooth_w"] = 0.34 * pitch
    L["z_ridge_top"] = L["z_foot"] - clr
    L["z_scroll_front"] = L["z_ridge_top"] - L["thread_h"]
    plate_t = max(0.09 * D, 1.15 * L["thread_h"])
    L["z_scroll_back"] = L["z_scroll_front"] - plate_t

    # --- scroll plate radial ---
    sleeve_od = max(bore_E + 0.06 * A, 0.20 * A)     # body central sleeve OD
    L["sleeve_od"] = sleeve_od
    L["scroll_id"] = sleeve_od + 2.0 * max(0.3, 0.0025 * A)
    L["scroll_od"] = 0.72 * A
    L["cavity_od"] = L["scroll_od"] + 2.0 * max(0.3, 0.0025 * A)
    L["r_spiral_start"] = L["scroll_id"] / 2.0 + 0.55 * L["ridge_w"] + 0.3
    L["r_spiral_outer"] = L["scroll_od"] / 2.0 - 0.015 * A

    # --- bevel crown ring (scroll back) + pinion, shared apex on chuck axis ---
    ring_band = 0.10 * A                      # radial face width of the ring
    L["ring_band"] = ring_band
    r_mean = min(max(0.29 * A, L["scroll_id"] / 2.0 + 0.60 * ring_band),
                 L["scroll_od"] / 2.0 - 0.55 * ring_band)
    L["ring_r_mean"] = r_mean
    L["ring_r_in"] = r_mean - ring_band / 2.0
    L["ring_r_out"] = r_mean + ring_band / 2.0

    cover_t = max(1.8, 0.085 * D, register_depth_C + 0.8)
    L["cover_t"] = cover_t
    head_clr = max(0.5, 0.008 * A)
    L["head_clr"] = head_clr
    # tooth proportions: addendum 0.75m, dedendum 1.25m, root embed 1.35m.
    # The pitch point sits below the scroll back by 1.35m PLUS the pitch-cone
    # rise over the outer half band (band/2 / tan_dw), so the ring's outer
    # edge never climbs into the plate.  Module solves the axial budget:
    # pocket bottom  zb - m*denom - head_clr >= -D + cover_t + 1
    kb = L["ring_r_out"] / r_mean
    kdelta = 3.0 * ring_band / r_mean         # = (band/2)/tan_dw per module
    denom = (1.35 + kdelta + PINION_TEETH / 2.0
             + (PINION_TEETH / 2.0 + 0.75) * kb)
    m_max = (L["z_scroll_back"] + D - cover_t - 1.0 - head_clr) / denom
    z_wheel = max(33, 3 * int(math.ceil(2.0 * r_mean / (3.0 * m_max))))
    L["z_wheel"] = z_wheel                    # crown tooth count, multiple of 3
    m = 2.0 * r_mean / z_wheel                # module at the mean radius
    L["module"] = m
    L["r_pinion_pitch"] = PINION_TEETH * m / 2.0
    L["tan_dw"] = z_wheel / float(PINION_TEETH)   # tan(delta_wheel) = Zw/Zp
    L["z_pitch_mean"] = (L["z_scroll_back"] - 1.35 * m
                         - (ring_band / 2.0) / L["tan_dw"])
    L["z_pinion_axis"] = L["z_pitch_mean"] - L["r_pinion_pitch"]

    # cavity bottom clears the deepest crown tooth tip (inner end of the band)
    z_tip_in = (L["z_pinion_axis"] + L["ring_r_in"] / L["tan_dw"]
                - 0.75 * m * (L["ring_r_in"] / r_mean))
    L["z_cavity_bot"] = z_tip_in - clr - 0.3

    # pinion journal / socket
    L["journal_d"] = max(1.7 * key_square_K, 0.9 * 2.0 * L["r_pinion_pitch"])
    L["r_journal_out"] = 0.485 * A            # outer face, recessed in the OD
    r_tip_out = (L["r_pinion_pitch"] + 0.75 * m) * kb
    L["pocket_r"] = r_tip_out + head_clr
    L["pocket_x0"] = L["ring_r_in"] - head_clr - 0.5
    L["pocket_x1"] = L["ring_r_out"] + head_clr + 0.5

    # guideways (radial), open at the OD
    L["guide_inner"] = max(bore_E / 2.0 + 0.04 * A, 0.11 * A, sleeve_od / 2.0)
    L["slot_gap"] = max(0.15, 0.0015 * A)     # per-side jaw/slot clearance
    return L


def _scroll_phase(L, clamp_d, jaw_length_A):
    """Rotate the scroll by a WHOLE number of crown pitches (k*360/Z_w), which
    leaves the bevel mesh untouched, choosing the position that seats the most
    arc teeth on the worst-off jaw — the operator's key position, made
    deterministic.  Mirrored in spec.check()."""
    p_ = L["pitch"]
    w_t = L["jaw_tooth_w"]
    x0 = clamp_d / 2.0
    x_f0 = max(x0 + 0.02 * jaw_length_A, L["guide_inner"] + 2.0 * L["slot_gap"])
    x_f1 = x0 + 0.98 * jaw_length_A
    lo = max(x_f0 + 0.6 * w_t, L["r_spiral_start"])
    hi = min(x_f1 - 0.6 * w_t, L["r_spiral_outer"] - 0.5 * L["ridge_w"])
    best = None
    for k in range(L["z_wheel"]):
        alpha = k * 360.0 / L["z_wheel"]
        counts = []
        for ang in JAW_ANGLES:
            r_base = L["r_spiral_start"] + p_ * (((ang - alpha) % 360.0) / 360.0)
            k_lo = int(math.ceil((lo - r_base) / p_ - 0.5))
            k_hi = int(math.floor((hi - r_base) / p_ - 0.5))
            counts.append(k_hi - k_lo + 1)
        key = (min(counts), sum(counts), -k)
        if best is None or key > best[0]:
            best = (key, alpha)
    return best[1]


def _spiral_thread(L):
    """Archimedean thread band standing on the scroll front face."""
    p, w = L["pitch"], L["ridge_w"]
    r0 = L["r_spiral_start"]
    r1 = L["r_spiral_outer"] - 0.5 * w
    n_turns = (r1 - r0) / p
    steps = max(60, int(n_turns * 36.0))
    out_pts, in_pts = [], []
    for s in range(steps + 1):
        th = 2.0 * math.pi * n_turns * s / steps
        r = r0 + p * th / (2.0 * math.pi)
        c, sn = math.cos(th), math.sin(th)
        out_pts.append(cq.Vector((r + w / 2.0) * c, (r + w / 2.0) * sn, 0.0))
        in_pts.append(cq.Vector((r - w / 2.0) * c, (r - w / 2.0) * sn, 0.0))
    e_out = cq.Edge.makeSpline(out_pts)
    e_in = cq.Edge.makeSpline(list(reversed(in_pts)))
    cap_end = cq.Edge.makeLine(out_pts[-1], in_pts[-1])
    cap_start = cq.Edge.makeLine(in_pts[0], out_pts[0])
    wire = cq.Wire.assembleEdges([e_out, cap_end, e_in, cap_start])
    band = cq.Solid.extrudeLinear(wire, [],
                                  cq.Vector(0.0, 0.0, L["thread_h"] + 0.3))
    return band.translate(cq.Vector(0.0, 0.0, L["z_scroll_front"] - 0.3))


def _crown_ring(L):
    """Conical gear boss + straight bevel teeth on the scroll back."""
    m, r_m = L["module"], L["ring_r_mean"]
    tan_dw = L["tan_dw"]
    z_ax = L["z_pinion_axis"]
    r_i, r_o = L["ring_r_in"], L["ring_r_out"]
    tan_fl = math.tan(math.radians(FLANK_HALF_DEG))
    zb = L["z_scroll_back"]

    def z_root(x):
        return z_ax + x / tan_dw + 1.35 * m * (x / r_m)

    def z_tip(x):
        return z_ax + x / tan_dw - 0.75 * m * (x / r_m)

    # revolved boss from the plate back down to the tooth root cone (capped
    # just under the plate back so the section stays simple where the root
    # cone runs into the plate)
    sect = cq.Wire.makePolygon([
        cq.Vector(r_i, 0.0, zb + 0.5),
        cq.Vector(r_o, 0.0, zb + 0.5),
        cq.Vector(r_o, 0.0, min(z_root(r_o), zb - 0.05)),
        cq.Vector(r_i, 0.0, min(z_root(r_i), zb - 0.05)),
        cq.Vector(r_i, 0.0, zb + 0.5),
    ])
    boss = cq.Solid.revolve(cq.Face.makeFromWires(sect), 360.0,
                            cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))

    wires_pair = []
    for x in (r_i, r_o):
        th_half = 0.17 * math.pi * m * (x / r_m)   # 0.34*pi*m tooth thickness
        h = z_root(x) - z_tip(x)
        hr = th_half + 0.5 * h * tan_fl
        ht = max(0.12 * th_half, th_half - 0.5 * h * tan_fl)
        wires_pair.append(cq.Wire.makePolygon([
            cq.Vector(x, -hr, z_root(x) + 0.4),
            cq.Vector(x, hr, z_root(x) + 0.4),
            cq.Vector(x, ht, z_tip(x)),
            cq.Vector(x, -ht, z_tip(x)),
            cq.Vector(x, -hr, z_root(x) + 0.4),
        ]))
    tooth_proto = cq.Solid.makeLoft(wires_pair, True)
    teeth = []
    for k in range(L["z_wheel"]):
        ang = 60.0 + k * 360.0 / L["z_wheel"]  # tooth CENTRE on pinion meridians
        teeth.append(tooth_proto.rotate(cq.Vector(0, 0, 0),
                                        cq.Vector(0, 0, 1), ang))
    return boss, teeth


def _bevel_pinion(L, meridian_deg):
    """Straight bevel pinion + journal + square key socket, one radial unit."""
    m, r_m = L["module"], L["ring_r_mean"]
    z_ax = L["z_pinion_axis"]
    r_pp = L["r_pinion_pitch"]
    x_i, x_o = L["ring_r_in"], L["ring_r_out"]
    tan_fl = math.tan(math.radians(FLANK_HALF_DEG))
    tan_dp = r_pp / r_m               # tan(delta_pinion) = Zp/Zw

    # gear core: root cone frustum along +X (apex toward the chuck axis)
    core = cq.Solid.makeCone(
        max(0.6, x_i * tan_dp - 1.25 * m * (x_i / r_m)),
        max(0.8, x_o * tan_dp - 1.25 * m * (x_o / r_m)),
        x_o - x_i,
        cq.Vector(x_i, 0.0, 0.0), cq.Vector(1.0, 0.0, 0.0))

    # teeth: loft sections perpendicular to the pinion axis; a GAP faces +Z so
    # the crown tooth centred on this meridian drops into it
    wires_pair = []
    for x in (x_i, x_o):
        th_half = 0.17 * math.pi * m * (x / r_m)
        r_root = x * tan_dp - 1.25 * m * (x / r_m)
        r_tip = x * tan_dp + 0.75 * m * (x / r_m)
        h = r_tip - r_root
        hr = th_half + 0.5 * h * tan_fl
        ht = max(0.12 * th_half, th_half - 0.5 * h * tan_fl)
        wires_pair.append(cq.Wire.makePolygon([
            cq.Vector(x, -hr, r_root - 0.4),
            cq.Vector(x, hr, r_root - 0.4),
            cq.Vector(x, ht, r_tip),
            cq.Vector(x, -ht, r_tip),
            cq.Vector(x, -hr, r_root - 0.4),
        ]))
    tooth_proto = cq.Solid.makeLoft(wires_pair, True)
    parts = [core]
    for k in range(PINION_TEETH):
        ang = (k + 0.5) * 360.0 / PINION_TEETH   # gap centred on +Z
        parts.append(tooth_proto.rotate(cq.Vector(0, 0, 0),
                                        cq.Vector(1, 0, 0), ang))

    # journal shaft out to the recessed key face
    journal = cq.Solid.makeCylinder(
        L["journal_d"] / 2.0, L["r_journal_out"] - (x_o - 1.0),
        cq.Vector(x_o - 1.0, 0.0, 0.0), cq.Vector(1.0, 0.0, 0.0))
    pinion = parts[0].fuse(*(parts[1:] + [journal]))

    # square socket for the chuck key K, cut into the recessed outer face
    K = L["socket_K"]
    sock_d = 1.1 * K
    socket = (
        cq.Workplane("YZ", origin=(L["r_journal_out"] - sock_d, 0.0, 0.0))
        .rect(K, K)
        .extrude(sock_d + 2.0))
    pinion = pinion.cut(socket.val())
    pinion = pinion.translate(cq.Vector(0.0, 0.0, z_ax))
    return pinion.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), meridian_deg)


def _jaw(L, jaw_idx, phase_alpha, clamp_d, jaw_length_A, jaw_width_B,
         jaw_height_C, jaw_step_F, jaw_step_G, jaw_step_H, jaw_tongue_E):
    """Stepped jaw + T-foot + underside arc teeth, built on the +X meridian."""
    x0 = clamp_d / 2.0
    z_top = L["z_foot"] + jaw_height_C       # catalog C spans foot to top
    # the BB drawing labels EACH step height H (two H callouts, one per step)
    mid_drop = min(jaw_step_H, 0.22 * jaw_height_C)
    low_drop = min(2.0 * jaw_step_H, 0.38 * jaw_height_C)

    body = (
        cq.Workplane("XZ")
        .moveTo(x0, 0.0)
        .lineTo(x0 + jaw_length_A, 0.0)
        .lineTo(x0 + jaw_length_A, z_top - low_drop)
        .lineTo(x0 + jaw_step_G, z_top - low_drop)
        .lineTo(x0 + jaw_step_G, z_top - mid_drop)
        .lineTo(x0 + jaw_step_F, z_top - mid_drop)
        .lineTo(x0 + jaw_step_F, z_top)
        .lineTo(x0, z_top)
        .close()
        .extrude(jaw_width_B / 2.0, both=True)
    )

    # gripping serrations on the VERTICAL clamping faces (the BB drawing marks
    # the nose face and both step risers, not the top land): two shallow
    # horizontal grooves per face, cut just below each face's local top edge
    serr_d = max(0.25, 0.02 * jaw_height_C)
    for xf, local_top in ((x0, z_top),
                          (x0 + jaw_step_F, z_top - mid_drop),
                          (x0 + jaw_step_G, z_top - low_drop)):
        for i in range(2):
            gz = local_top - (0.14 + 0.16 * i) * jaw_height_C
            if gz - serr_d < 0.5:
                continue
            body = body.cut(
                cq.Workplane("XY", origin=(xf - 0.45, -0.6 * jaw_width_B, gz))
                .box(0.80, 1.2 * jaw_width_B, serr_d,
                     centered=(False, False, False)))

    # nose chamfers: the BB drawing's plan view shows a narrowed tip; it is
    # also what lets three jaws meet at small clamp diameters without touching
    tip_half = 0.13 * jaw_width_B
    for sgn in (1.0, -1.0):
        cutter = (
            cq.Workplane("XY", origin=(0.0, 0.0, 0.0))
            .box(3.0 * jaw_length_A, jaw_width_B, jaw_height_C + 6.0,
                 centered=(False, False, False))
            .translate((x0 - 0.02, sgn * tip_half - (0.0 if sgn > 0 else jaw_width_B),
                        -2.0))
            .rotate((x0 - 0.02, sgn * tip_half, 0.0),
                    (x0 - 0.02, sgn * tip_half, 1.0), sgn * 35.0))
        body = body.cut(cutter)

    # T-foot: neck through tier 1, flange in tier 2 (flange height = jaw dim E)
    x_f0 = max(x0 + 0.02 * jaw_length_A, L["guide_inner"] + 2.0 * L["slot_gap"])
    x_f1 = x0 + 0.98 * jaw_length_A
    neck_w = 0.60 * jaw_width_B
    neck = (
        cq.Workplane("XY", origin=(x_f0, -neck_w / 2.0, L["z_flange_top"] - 0.2))
        .box(x_f1 - x_f0, neck_w, -(L["z_flange_top"] - 0.2) + 0.3,
             centered=(False, False, False)))
    flange = (
        cq.Workplane("XY", origin=(x_f0, -jaw_width_B / 2.0, L["z_foot"]))
        .box(x_f1 - x_f0, jaw_width_B, jaw_tongue_E + 0.2,
             centered=(False, False, False)))

    # underside arc teeth at the local spiral gap radii; evaluating the
    # (phase-rotated) spiral at this jaw's meridian gives the real 1/3-pitch
    # stagger between jaws
    p, w_t = L["pitch"], L["jaw_tooth_w"]
    theta_frac = ((JAW_ANGLES[jaw_idx] - phase_alpha) % 360.0) / 360.0
    r_base = L["r_spiral_start"] + p * theta_frac
    lo = max(x_f0 + 0.6 * w_t, L["r_spiral_start"])
    hi = min(x_f1 - 0.6 * w_t, L["r_spiral_outer"] - 0.5 * L["ridge_w"])
    k_min = int(math.ceil((lo - r_base) / p - 0.5))
    k_max = int(math.floor((hi - r_base) / p - 0.5))
    clip = (
        cq.Workplane("XY", origin=(x_f0, -jaw_width_B / 2.0 + 0.1,
                                   L["z_foot"] - L["thread_h"] - 1.0))
        .box(x_f1 - x_f0, jaw_width_B - 0.2, L["thread_h"] + 2.0,
             centered=(False, False, False)))
    teeth = []
    for k in range(k_min, k_max + 1):
        r_k = r_base + (k + 0.5) * p
        ring = _annulus(L["z_foot"] - L["thread_h"], L["thread_h"] + 0.3,
                        2.0 * r_k + w_t, 2.0 * r_k - w_t)
        teeth.append(ring.val().intersect(clip.val()))

    jaw = body.val().fuse(neck.val(), flange.val(), *teeth)
    return jaw.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1),
                      JAW_ANGLES[jaw_idx])


def build(
    catalog_index,
    catalog_item,
    outer_dia_A,
    register_dia_B,
    register_depth_C,
    height_D,
    bore_E,
    bolt_circle_F,
    mount_thread_G,
    mount_hole_count,
    jaw_length_A,
    jaw_width_B,
    jaw_height_C,
    jaw_serration_D,
    jaw_tongue_E,
    jaw_step_F,
    jaw_step_G,
    jaw_step_H,
    key_square_K,
    grip_min_A1,
    grip_max_A1,
    jaw_open_fraction,
    clamp_d,
    has_scallops,
):
    """Nine engaged, non-interpenetrating bodies in one fixed-count assembly."""
    _ = catalog_index
    _ = catalog_item
    _ = grip_min_A1
    _ = grip_max_A1
    _ = jaw_open_fraction

    A, D = outer_dia_A, height_D
    L = _layout(A, D, bore_E, register_depth_C,
                jaw_serration_D, jaw_tongue_E, key_square_K)
    L["socket_K"] = key_square_K

    # ---------------- one-piece body ----------------
    body = _annulus(-D, D, A, bore_E)

    cover_od = max(0.84 * A, register_dia_B + 0.03 * A)
    cc = max(0.15, 0.002 * A)
    cover_t = L["cover_t"]
    body = body.cut(
        _annulus(-D - 0.02, cover_t + 0.04, cover_od + 2.0 * cc, bore_E))

    # T-guideways, open at the OD (tier 1 narrow, tier 2 wide)
    g = L["slot_gap"]
    neck_w = 0.60 * jaw_width_B
    for angd in JAW_ANGLES:
        t1 = (
            cq.Workplane("XY", origin=(L["guide_inner"], -(neck_w / 2.0 + g),
                                       -L["tier1_d"]))
            .box(0.60 * A, neck_w + 2.0 * g, L["tier1_d"] + 0.02,
                 centered=(False, False, False))
            .rotate((0, 0, 0), (0, 0, 1), angd))
        t2 = (
            cq.Workplane("XY", origin=(L["guide_inner"],
                                       -(jaw_width_B / 2.0 + g), L["z_floor"]))
            .box(0.60 * A, jaw_width_B + 2.0 * g,
                 -L["tier1_d"] - L["z_floor"],   # stop at the tier-1 boundary:
                 centered=(False, False, False))  # the ledge retains the flange
            .rotate((0, 0, 0), (0, 0, 1), angd))
        body = body.cut(t1).cut(t2)

    # scroll cavity between central sleeve and outer wall
    body = body.cut(
        _annulus(L["z_cavity_bot"], L["z_floor"] - L["z_cavity_bot"] + 0.02,
                 L["cavity_od"], L["sleeve_od"]))

    # stepped radial pinion bores: head pocket + journal bore
    for angd in PINION_ANGLES:
        pocket = (
            cq.Workplane("YZ", origin=(L["pocket_x0"], 0.0, L["z_pinion_axis"]))
            .circle(L["pocket_r"])
            .extrude(L["pocket_x1"] - L["pocket_x0"])
            .rotate((0, 0, 0), (0, 0, 1), angd))
        journal = (
            cq.Workplane("YZ", origin=(L["pocket_x1"] - 0.5, 0.0,
                                       L["z_pinion_axis"]))
            .circle(L["journal_d"] / 2.0 + 0.15)
            .extrude(0.5 * A - L["pocket_x1"] + 2.0)
            .rotate((0, 0, 0), (0, 0, 1), angd))
        body = body.cut(pocket).cut(journal)

    # rear mounting: F bolt circle, catalog hole count, blind depth. The BODY
    # is tapped (hole at the thread minor diameter ~0.85*G, no false helix);
    # the COVER carries clearance holes.
    hole_depth = min(2.5 * mount_thread_G, 0.45 * D)
    for i in range(mount_hole_count):
        ang = 2.0 * math.pi * i / mount_hole_count
        hx = 0.5 * bolt_circle_F * math.cos(ang)
        hy = 0.5 * bolt_circle_F * math.sin(ang)
        body = body.cut(
            cq.Workplane("XY", origin=(hx, hy, -D - 0.5))
            .circle(0.85 * mount_thread_G / 2.0)
            .extrude(hole_depth + 0.5))

    # characteristic scallops (absent from size 400 up, catalog p.3041)
    if has_scallops > 0:
        notch_d = 0.13 * A
        for angd in PINION_ANGLES:
            nx = 0.515 * A * math.cos(math.radians(angd))
            ny = 0.515 * A * math.sin(math.radians(angd))
            body = body.cut(
                cq.Workplane("XY", origin=(nx, ny, -D - 0.5))
                .circle(notch_d / 2.0)
                .extrude(D + 1.0))

    # shallow concentric front-face ring (visible on the product)
    body = body.cut(
        _annulus(-0.018 * D, 0.02 * D, 0.78 * A,
                 max(0.70 * A, bore_E + 0.06 * A)))

    # ---------------- rear cover ----------------
    cover = _annulus(-D + cc, cover_t - 2.0 * cc, cover_od, bore_E + 2.0 * cc)
    # DIN 6350 rear centering RECESS: diameter B, depth C, cut into the back
    cover = cover.cut(
        _annulus(-D - 0.5, register_depth_C + 0.5 + cc, register_dia_B,
                 max(1.0, bore_E - 1.0)))
    for i in range(mount_hole_count):
        ang = 2.0 * math.pi * i / mount_hole_count
        hx = 0.5 * bolt_circle_F * math.cos(ang)
        hy = 0.5 * bolt_circle_F * math.sin(ang)
        cover = cover.cut(
            cq.Workplane("XY", origin=(hx, hy, -D - 0.5))
            .circle((mount_thread_G + max(0.4, 0.05 * mount_thread_G)) / 2.0)
            .extrude(hole_depth + 0.5))

    # ---------------- scroll plate ----------------
    plate = _annulus(L["z_scroll_back"],
                     L["z_scroll_front"] - L["z_scroll_back"],
                     L["scroll_od"], L["scroll_id"])
    boss, crown_teeth = _crown_ring(L)
    spiral = _spiral_thread(L)
    scroll = plate.val().fuse(*([boss, spiral] + crown_teeth))
    # operator's key position: whole crown pitches, bevel mesh unaffected
    phase_alpha = _scroll_phase(L, clamp_d, jaw_length_A)
    scroll = scroll.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), phase_alpha)

    # ---------------- jaws + pinions ----------------
    jaws = [
        _jaw(L, i, phase_alpha, clamp_d, jaw_length_A, jaw_width_B,
             jaw_height_C, jaw_step_F, jaw_step_G, jaw_step_H, jaw_tongue_E)
        for i in range(3)
    ]
    pinions = [_bevel_pinion(L, angd) for angd in PINION_ANGLES]

    result = cq.Compound.makeCompound(
        [body.val(), cover.val(), scroll] + jaws + pinions)
    return result
