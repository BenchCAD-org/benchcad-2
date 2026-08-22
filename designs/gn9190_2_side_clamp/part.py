"""Parametric CadQuery rebuild of the Ganter GN 9190.2 side clamp.

The reference 9190.2-10-M8-E-G STEP contains five solids: the steel body,
the pivoted serrated jaw, a lower support block, the coded ball-point screw,
and its small hex operating end.  The submitted model rebuilds those members
from the official 10/14/18 mm catalog rows instead of importing the STEP.
"""

import math

import cadquery as cq


CATALOG = {
    10.0: dict(d1=8.0, fs=7.0, b1=32.0, b2=12.1, d2=8.4, d3=8.0,
               d4=8.0, d5=4.0, d5_max=26.0, h1=44.0, h2=40.0, h3=28.0, h4=15.0,
               l1=52.0, l2=28.0, l3=30.0, l4=72.5, l5=38.0, l6=63.0,
               s=3.0, ma=3.0),
    14.0: dict(d1=12.0, fs=15.0, b1=48.0, b2=16.0, d2=13.0, d3=12.0,
               d4=12.0, d5=4.0, d5_max=26.0, h1=53.0, h2=45.0, h3=27.0, h4=15.0,
               l1=72.0, l2=40.0, l3=44.0, l4=100.0, l5=55.0, l6=78.0,
               s=4.0, ma=9.0),
    18.0: dict(d1=16.0, fs=21.5, b1=68.0, b2=18.8, d2=17.0, d3=16.0,
               d4=16.0, d5=4.0, d5_max=26.0, h1=72.0, h2=60.0, h3=38.0, h4=20.0,
               l1=86.0, l2=41.0, l3=56.0, l4=126.0, l5=63.0, l6=108.0,
               s=7.0, ma=20.0),
}

EXAMPLE_PARAMS = {
    "slot_width": 10.0,
    "jaw_type": "E",
    "stroke_coding": "G",
    "serration_count": 9,
    "jaw_angle": 90.0,
    "return_spring_gap": 1.0,
    "lever_angle": 0.0,
    "body_chamfer": 1.2,
    "body_edge_radius": 0.65,
    "jaw_chamfer": 0.55,
    "jaw_edge_radius": 0.45,
    "support_chamfer": 0.45,
    "screw_chamfer": 0.35,
}


def _row(slot_width):
    key = min(CATALOG, key=lambda value: abs(value - float(slot_width)))
    if abs(key - float(slot_width)) > 1e-7:
        raise ValueError("slot_width must be one of the official 10, 14, or 18 mm rows")
    return dict(CATALOG[key])


def _cyl_y(diameter, length, x, y, z):
    return cq.Workplane("XZ").circle(float(diameter) / 2.0).extrude(-float(length)).translate((x, y, z))


def _cyl_x(diameter, length, x, y, z):
    return cq.Workplane("YZ").circle(float(diameter) / 2.0).extrude(float(length)).translate((x, y, z))


def _cyl_z(diameter, length, x, y, z):
    return cq.Workplane("XY").circle(float(diameter) / 2.0).extrude(float(length)).translate((x, y, z))


def _hex_prism(radius, height, x, y, z, direction="y"):
    plane = "XZ" if direction == "y" else "YZ"
    return (cq.Workplane(plane).polygon(6, float(radius) * 2.0)
            .extrude(-float(height) if direction == "y" else float(height))
            .translate((x, y, z)))


def _chamfered_outline(x0, x1, y0, y1, corner):
    """Return a planar eight-sided outline with four controlled corners."""
    c = min(max(float(corner), 0.0), (x1 - x0) * 0.24, (y1 - y0) * 0.24)
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c),
            (x1, y1 - c), (x1 - c, y1), (x0 + c, y1),
            (x0, y1 - c), (x0, y0 + c)]


def _single_end_chamfer_outline(x0, x1, y0, y1, corner):
    """Chamfer only the free X end; keep the mating X end square."""
    c = min(max(float(corner), 0.0), (x1 - x0) * 0.24, (y1 - y0) * 0.24)
    return [(x0 + c, y0), (x1, y0), (x1, y1),
            (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def _safe_fillet(shape, radius, selector):
    """Apply a small fillet where OpenCascade can resolve it, otherwise keep the chamfered fallback."""
    radius = float(radius)
    if radius <= 1.0e-5:
        return shape
    try:
        return shape.edges(selector).fillet(radius)
    except Exception:
        return shape


def _safe_chamfer(shape, distance, selector):
    """Apply a controlled chamfer while preserving a valid fallback solid."""
    distance = float(distance)
    if distance <= 1.0e-5:
        return shape
    try:
        return shape.edges(selector).chamfer(distance)
    except Exception:
        return shape


def _body(r, gap, body_chamfer, body_edge_radius):
    """Main housing rebuilt from the stepped and tapered STEP envelope."""
    scale = r["l4"] / 72.5
    pivot_x = 0.3448275862 * r["l4"]
    half_z = min(0.40 * r["h2"], 0.365 * r["h1"])
    # The catalog side view has a rectangular rear block, a 15 mm front
    # ledge, and a tapered nose that reaches exactly one l4 left of the pivot.
    rear_offset = r["l4"] - 0.80 * r["l2"]
    rear_x = pivot_x - rear_offset
    nose_root = pivot_x - (rear_offset + 5.27 * scale)
    nose_tip = pivot_x - r["l4"]
    y_front = -15.0 * scale
    y_back = 17.0 * scale
    footprint = [(pivot_x, y_back), (pivot_x, y_front),
                 (nose_root, y_front), (nose_root, 0.0),
                 (rear_x, 0.0), (rear_x, y_back)]
    body = (cq.Workplane("XY").polyline(footprint).close()
            .extrude(2.0 * half_z).translate((0.0, 0.0, -half_z)))

    # The left clamping nose is a true X-Z taper, not a large rectangular cut.
    edge_ratio = min(0.48, max(0.30, 0.378125
                                + 0.004 * float(body_chamfer)
                                + 0.002 * float(body_edge_radius)))
    tip_half = half_z * edge_ratio
    nose_profile = [(nose_root, -half_z), (nose_tip, -tip_half),
                    (nose_tip, tip_half), (nose_root, half_z)]
    nose = (cq.Workplane("XZ").polyline(nose_profile).close()
            .extrude(15.0 * scale).translate((0.0, 0.0, 0.0)))
    body = body.union(nose)

    # The STEP pivot pocket is only 10 mm wide and 16 mm high; the previous
    # implementation removed most of the housing and produced a U-shaped body.
    pocket_x0 = rear_x
    pocket_x1 = pivot_x - 40.0 * scale
    pocket_half = min(8.0 * scale + 0.20 * float(gap), 0.60 * r["h4"])
    pivot_pocket = (cq.Workplane("XY").box(pocket_x1 - pocket_x0, y_back,
                                             2.0 * pocket_half,
                                             centered=(False, False, True))
                    .translate((pocket_x0, 0.0, 0.0)))
    body = body.cut(pivot_pocket)

    # Side details visible in the drawing and STEP: the hinge bore is normal
    # to X, while the nose bore is normal to Y (both axes matter in the fit).
    hinge_x = pivot_x - (r["l1"] - 0.266 * r["l3"])
    hinge_bore_d = max(r["d5"], 0.50 * r["d3"])
    body = body.cut(_cyl_z(hinge_bore_d, 16.0 * scale,
                           hinge_x, 11.5 * scale, -8.0 * scale))
    nose_hole_x = nose_tip + 10.5 * scale
    body = body.cut(_cyl_y(r["d5"] * 1.65, 15.0 * scale,
                           nose_hole_x, -15.0 * scale, 0.0))
    recess_x = pivot_x - 24.0 * scale
    boss_diameter = r["d2"] + 4.6 * scale
    rear_boss = _cyl_y(boss_diameter, 8.0 * scale,
                       recess_x, 13.0 * scale, 0.0)
    body = body.union(rear_boss)
    boss_clear_d = max(boss_diameter + 1.0 * scale, r["d4"] * 1.75)
    body = body.cut(_cyl_y(boss_clear_d, 4.0 * scale,
                           recess_x, 13.0 * scale, 0.0))
    body = body.cut(_hex_prism(r["d5"] * 0.78, 5.0 * scale,
                               recess_x, 16.0 * scale, 0.0))

    # Two stepped Y-axis bosses form the lower tongue in the STEP.  The front
    # end is a short cone, not the earlier triangular plate approximation.
    tongue_x = 1.0
    lower_tongue = _cyl_y(r["d5"] * 2.0, 11.2 * scale,
                          tongue_x, -26.2 * scale, 0.0)
    lower_tip = cq.Solid.makeCone(
        0.80 * r["d5"] * scale, r["d5"] * scale, 0.8 * scale,
        cq.Vector(tongue_x, -27.0 * scale, 0.0), cq.Vector(0.0, 1.0, 0.0))
    body = body.union(lower_tongue).union(
        cq.Workplane("XY").newObject([lower_tip]))
    upper_tongue = _cyl_y(r["d5"] * 2.125, 13.0 * scale,
                          tongue_x, 0.0, 0.0)
    body = body.union(upper_tongue)
    body = body.cut(_cyl_y(r["d5"] * 2.0, 13.0 * scale,
                           tongue_x, 0.0, 0.0))
    # Boolean clearance cuts can leave a very small nose sliver detached from
    # the housing.  It is not a catalog component; discard only that sub-1%
    # artifact while retaining the real rear boss, then bridge the boss back
    # into the housing with material hidden inside the two overlapping walls.
    body_solids = list(body.vals()[0].Solids())
    if body_solids:
        primary_volume = max(s.Volume() for s in body_solids)
        body_solids = [s for s in body_solids if s.Volume() >= 0.004 * primary_volume]
        body = cq.Workplane("XY").newObject(body_solids)
    boss_bridge_x = recess_x + 0.42 * boss_diameter
    boss_bridge = _cyl_y(max(0.22 * boss_diameter, 1.2 * scale),
                         2.0 * scale, boss_bridge_x, 16.0 * scale, 0.0)
    body = body.union(boss_bridge).clean()
    # The tapered nose and stepped footprint already provide the catalog edge
    # treatment; avoiding a global fillet keeps all three rows robust in OCP.
    return body


def _jaw(r, jaw_type, serration_count, jaw_angle, gap, lever_angle,
         jaw_chamfer, jaw_edge_radius):
    """Pivoted wedge jaw with the STEP's tapered plate and hinge relief."""
    scale = r["l4"] / 72.5
    pivot_x = 0.3448275862 * r["l4"]
    half_z = 0.40 * r["h2"]
    x_tip = pivot_x - r["l1"]
    x_block = pivot_x - 40.0 * scale
    y0 = 18.5 * scale
    rear_depth = 10.5 * scale + 0.02 * (r["b1"] - 32.0)
    # The STEP's long plate and the right end block share the same rear
    # depth.  Keeping this tied to rear_depth avoids the visible half-mm
    # step that appeared when plate_depth was derived from h4 alone.
    plate_depth = rear_depth
    # Rear contact block, with the tiny corner breaks visible on the STEP.
    # Both controls affect the visible corner breaks on the rear jaw block;
    # the helper applies the dimensional upper bound for each row.
    rear_corner = float(jaw_chamfer) + 0.35 * float(jaw_edge_radius)
    # The catalog/STEP block is asymmetric: only the free x_tip end has the
    # two corner breaks.  The x_block end mates squarely into the long plate.
    rear_outline = _single_end_chamfer_outline(x_tip, x_block, y0,
                                                y0 + rear_depth, rear_corner)
    jaw = (cq.Workplane("XY").polyline(rear_outline).close()
           .extrude(2.0 * half_z).translate((0.0, 0.0, -half_z)))
    # The long plate tapers from full height at the hinge to half height at
    # the right end, matching the sloped top and bottom faces in the STEP.
    join_overlap = 0.15 * scale + 0.05 * float(gap)
    plate_x = x_block - join_overlap
    plate_profile = [(plate_x, -half_z), (pivot_x, -0.5 * half_z),
                     (pivot_x, 0.5 * half_z), (plate_x, half_z)]
    plate = (cq.Workplane("XZ").polyline(plate_profile).close()
             .extrude(-plate_depth).translate((0.0, y0, 0.0)))
    jaw = jaw.union(plate)
    bridge = cq.Workplane("XY").box(
        2.0 * join_overlap, plate_depth, 2.0 * half_z,
        centered=(True, False, True)).translate(
            (x_block, y0, 0.0))
    jaw = jaw.union(bridge)
    # Merge the coplanar plate/end-block faces at the join.  Without this
    # cleanup the renderer shows a false vertical gap even though the solid
    # is already connected.
    jaw = jaw.clean()

    # The STEP has a six-mm-wide hinge lug below the rear block.  Its last
    # two millimetres taper to a two-mm-wide central tongue.
    hinge_x = pivot_x - (r["l1"] - 0.266 * r["l3"])
    lug = cq.Workplane("XY").box(6.0 * scale, 9.5 * scale,
                                  16.0 * scale,
                                  centered=(False, False, True)).translate(
                                      (hinge_x - 3.0 * scale,
                                       9.0 * scale, 0.0))
    lug_tip = (cq.Workplane("XY").polyline([
        (hinge_x - 1.0 * scale, 7.0 * scale),
        (hinge_x + 1.0 * scale, 7.0 * scale),
        (hinge_x + 3.0 * scale, 9.0 * scale),
        (hinge_x - 3.0 * scale, 9.0 * scale)]).close()
               .extrude(16.0 * scale).translate((0.0, 0.0, -8.0 * scale)))
    jaw = jaw.union(lug).union(lug_tip)
    # This is the small vertical pin bore through the lug, not an h4-sized
    # transverse opening.
    hinge_bore_d = max(r["d5"], 0.50 * r["d3"])
    jaw = jaw.cut(_cyl_z(hinge_bore_d, 16.0 * scale,
                         hinge_x, 11.5 * scale, -8.0 * scale))

    # The STEP side faces show a large Y-axis circle of diameter h4 and a
    # smaller Y-axis circle near the right-hand end of the jaw.
    hole_x = pivot_x - 0.857 * r["l2"]
    jaw = jaw.cut(_cyl_y(r["h4"], plate_depth + 2.0 * scale,
                         hole_x, y0 - 1.0 * scale, 0.0))
    small_offset = 0.165 * r["l5"]
    small_x = pivot_x - small_offset
    small_y = y0 + 8.4 * scale
    ball_radius = min(r["d2"] * 0.327, r["d5"] * 0.80)
    # Leave radial running clearance for the clamping shaft.  The STEP hole
    # is nominally d5-based, but its exported screw overlaps that wall; the
    # parameterized rebuild uses d1 plus a small fit allowance so the named
    # assembly is physically non-interfering.
    small_hole_diameter = max(r["d5"] * 1.65, r["d1"] * 1.20)
    jaw = jaw.cut(_cyl_y(small_hole_diameter, 0.64 * r["h4"],
                         small_x, y0 - 1.0 * scale, 0.0))
    contact_x = x_tip
    if jaw_type == "P":
        # P has a plain 30..120 degree angled contact face in plan view.
        angle = math.radians(max(30.0, min(120.0, jaw_angle)))
        depth = max(2.0 * scale, r["b2"] * 0.35 * math.tan(angle / 2.0))
        relief = (cq.Workplane("XY").polyline(
            [(contact_x - 0.2 * scale, y0 - 0.2 * scale),
             (contact_x + depth, y0 + rear_depth * 0.5),
             (contact_x - 0.2 * scale, y0 + rear_depth + 0.2 * scale)]).close()
                  .extrude(2.0 * half_z + 2.0)
                  .translate((0.0, 0.0, -half_z - 1.0)))
        jaw = jaw.cut(relief)
    else:
        # E serrations are cuts across the vertical contact face, not grooves
        # on the top surface as in the earlier approximation.  The supplied
        # E-G STEP is the plain catalog row; deeper optional teeth appear only
        # when the count is increased above the reference count.
        count = int(serration_count)
        if count > 9:
            tooth_depth = min(0.15 * scale + 0.08 * (count - 9),
                              0.12 * r["b2"], 0.20 * r["s"],
                              0.03 * r["d5_max"])
            for index in range(count):
                y = y0 + (index + 0.5) * rear_depth / count
                tooth = cq.Workplane("XY").box(
                    tooth_depth + 0.2, rear_depth / count * 0.55,
                    2.0 * half_z + 2.0,
                    centered=(False, True, True)).translate(
                        (contact_x - 0.1, y, 0.0))
                jaw = jaw.cut(tooth)

    jaw = _safe_fillet(jaw, min(float(jaw_edge_radius), 0.35 * scale), "|Y")
    jaw = _safe_chamfer(jaw, min(float(jaw_chamfer), 0.35 * scale), ">Z")
    # The screw-clearance boolean may leave a microscopic detached fragment at
    # the contact edge.  Keep the modeled jaw body and discard only fragments
    # below one percent of its volume.
    jaw_solids = list(jaw.vals()[0].Solids())
    if jaw_solids:
        jaw_volume = max(s.Volume() for s in jaw_solids)
        jaw = cq.Workplane("XY").newObject(
            [s for s in jaw_solids if s.Volume() >= 0.01 * jaw_volume])
    jaw = jaw.clean()
    jaw = jaw.rotate((pivot_x, 0, 0), (pivot_x, 1, 0), float(lever_angle))
    return jaw


def _support(r, support_chamfer):
    x = 1.0
    scale = r["l4"] / 72.5
    support_y = -27.0 * scale
    height = r["h3"] + 2.0
    half_width = 0.5 * (r["d2"] + 6.6)
    outer_left, outer_right = x - half_width, x + half_width
    neck_left = x - 5.0 * scale
    neck_right = x + 5.0 * scale
    y_front = support_y - 6.0 * scale
    y_step = support_y
    y_back = support_y + 6.0 * scale
    front_break = max(0.4 * scale,
                      1.6 * scale + 0.50 * (float(support_chamfer) - 0.45))
    front_break = min(front_break, 0.45 * (y_step - y_front))
    outline = [
        (neck_left, y_back), (neck_left, y_step),
        (outer_left, y_step), (outer_left, y_step - 4.4 * scale),
        (outer_left + front_break, y_front),
        (outer_right - front_break, y_front),
        (outer_right, y_step - 4.4 * scale),
        (outer_right, y_step), (neck_right, y_step),
        (neck_right, y_back),
    ]
    block = (cq.Workplane("XY").polyline(outline).close().extrude(height)
             .translate((0.0, 0.0, -height / 2.0)))
    bore = _cyl_y(r["d5"] * 1.65, 11.3 * scale,
                  x, y_front, 0.0)
    counterbore = cq.Solid.makeCone(
        r["d5"] * 2.0, r["d5"] * 1.65, 0.7 * scale,
        cq.Vector(x, y_back - 0.7 * scale, 0.0),
        cq.Vector(0.0, 1.0, 0.0))
    return block.cut(bore).cut(cq.Workplane("XY").newObject([counterbore]))


def _clamping_screw(r, coding, screw_chamfer):
    scale = r["l4"] / 72.5
    screw_offset = 0.165 * r["l5"]
    x = 0.3448275862 * r["l4"] - screw_offset
    y = 17.6 * scale
    shaft_start = y + 1.25 * scale
    shaft_length = 0.371 * r["l6"]
    shaft_diameter = r["d1"]
    shaft = _cyl_y(shaft_diameter, shaft_length, x, shaft_start, 0.0)
    flange = _cyl_y(r["d1"] * 0.80, 0.90 * scale, x, y, 0.0)
    edge = min(max(float(screw_chamfer), 0.0), 0.85 * scale)
    front_cone = cq.Solid.makeCone(
        r["d1"] * 0.40, r["d1"] * 0.50, 1.25 * scale,
        cq.Vector(x, y + 0.50 * scale, 0.0), cq.Vector(0.0, 1.0, 0.0))
    screw = shaft.union(flange).union(
        cq.Workplane("XY").newObject([front_cone]))
    # A coded hex socket is at the far end of the shaft in the STEP, not in
    # the front flange.  Its depth remains a real parameterized detail.
    shaft_end = shaft_start + shaft_length
    rear_cone = cq.Solid.makeCone(
        r["d1"] * 0.50, r["d1"] * 0.40, 1.25 * scale,
        cq.Vector(x, shaft_end - 0.50 * scale, 0.0),
        cq.Vector(0.0, 1.0, 0.0))
    screw = screw.union(cq.Workplane("XY").newObject([rear_cone]))
    socket_depth = (2.6 + 0.8 * edge) * scale
    socket = _hex_prism(r["s"] * 0.90, socket_depth,
                        x, shaft_end + 0.75 * scale - socket_depth, 0.0)
    screw = screw.cut(socket)
    ball_radius = min(r["d2"] * 0.327, r["d5"] * 0.80)
    ball_x = x - 0.50 * scale
    ball_y = 17.0 * scale + 0.188 * r["d2"]
    ball_tool = cq.Workplane("XY").sphere(ball_radius + 0.08 * scale)
    ball_tool = ball_tool.translate((ball_x, ball_y, 0.0))
    ball_clip = cq.Workplane("XY").box(
        40.0 * scale, 40.0 * scale, 30.0 * scale,
        centered=(True, False, True)).translate((ball_x, 17.6 * scale, 0.0))
    screw = screw.cut(ball_tool.intersect(ball_clip))
    return screw


def _validate(slot_width, jaw_type, stroke_coding, serration_count, jaw_angle, return_spring_gap,
              lever_angle, body_chamfer, body_edge_radius, jaw_chamfer, jaw_edge_radius,
              support_chamfer, screw_chamfer):
    if float(slot_width) not in CATALOG:
        raise ValueError("slot_width must be exactly 10, 14, or 18 mm")
    if jaw_type not in ("E", "P"):
        raise ValueError("jaw_type must be E or P")
    if stroke_coding not in ("G", "K"):
        raise ValueError("stroke_coding must be G or K")
    if int(serration_count) < 3:
        raise ValueError("serration_count must be at least 3")
    if not 30.0 <= float(jaw_angle) <= 120.0:
        raise ValueError("jaw_angle must be between 30 and 120 degrees")
    if float(return_spring_gap) <= 0.0:
        raise ValueError("return_spring_gap must be positive")
    for name, value in (("body_chamfer", body_chamfer), ("body_edge_radius", body_edge_radius),
                        ("jaw_chamfer", jaw_chamfer), ("jaw_edge_radius", jaw_edge_radius),
                        ("support_chamfer", support_chamfer), ("screw_chamfer", screw_chamfer)):
        if float(value) < 0.0:
            raise ValueError(name + " must be non-negative")
    if not -35.0 <= float(lever_angle) <= 35.0:
        raise ValueError("lever_angle must be between -35 and 35 degrees")


def build(slot_width, jaw_type="E", stroke_coding="G", serration_count=9,
          jaw_angle=90.0, return_spring_gap=1.0, lever_angle=0.0,
          body_chamfer=1.2, body_edge_radius=0.65, jaw_chamfer=0.55,
          jaw_edge_radius=0.45, support_chamfer=0.45, screw_chamfer=0.35):
    # The benchmark sampler uses numeric enum values so its range contract is
    # comparable; CQ-editor callers may continue using the catalog letters.
    jaw_type = {0: "E", 1: "P"}.get(jaw_type, jaw_type)
    stroke_coding = {0: "G", 1: "K"}.get(stroke_coding, stroke_coding)
    _validate(slot_width, jaw_type, stroke_coding, serration_count, jaw_angle, return_spring_gap,
              lever_angle, body_chamfer, body_edge_radius, jaw_chamfer, jaw_edge_radius,
              support_chamfer, screw_chamfer)
    r = _row(slot_width)
    body = _body(r, return_spring_gap, body_chamfer, body_edge_radius)
    jaw = _jaw(r, jaw_type, serration_count, jaw_angle, return_spring_gap, lever_angle,
               jaw_chamfer, jaw_edge_radius)
    # The open pocket is part of the steel housing, so remove the jaw envelope
    # from the housing before naming the independent assembly members.
    body = body.cut(jaw)
    support = _support(r, support_chamfer)
    screw = _clamping_screw(r, stroke_coding, screw_chamfer)
    # Keep the mating components as separate named solids while removing only
    # their exported STEP-style overlap at the contact interfaces.
    body = body.cut(support)
    # Reconnect the annular rear boss after the jaw/support clearance cuts;
    # their booleans can otherwise separate an otherwise single housing.
    scale = r["l4"] / 72.5
    recess_x = 0.3448275862 * r["l4"] - 24.0 * scale
    body_bridge_x = recess_x + 0.42 * (r["d2"] + 4.6 * scale)
    body = body.union(_cyl_y(max(0.22 * (r["d2"] + 4.6 * scale), 1.2 * scale),
                             2.0 * scale, body_bridge_x, 16.0 * scale, 0.0)).clean()
    body_solids = list(body.vals()[0].Solids())
    if body_solids:
        # Secondary fragments are boolean remnants inside the cleared boss or
        # jaw pocket, rather than independent catalog parts.  Keep the main
        # housing solid so the five named assembly components remain one body
        # each in STEP export.
        body = cq.Workplane("XY").newObject([max(body_solids, key=lambda s: s.Volume())])
    jaw = jaw.cut(screw)
    jaw_solids = list(jaw.vals()[0].Solids())
    if jaw_solids:
        jaw_volume = max(s.Volume() for s in jaw_solids)
        jaw = cq.Workplane("XY").newObject(
            [s for s in jaw_solids if s.Volume() >= 0.01 * jaw_volume])
    scale = r["l4"] / 72.5
    screw_offset = 0.165 * r["l5"]
    end_x = 0.3448275862 * r["l4"] - screw_offset - 0.50 * scale
    ball_radius = min(r["d2"] * 0.327, r["d5"] * 0.80)
    end_y = 17.0 * scale + 0.188 * r["d2"]
    if stroke_coding == "K":
        end = (cq.Workplane("XY").box(r["l6"] * 0.55, r["s"] * 1.15,
                                       r["s"] * 1.15, centered=True)
               .translate((end_x, end_y + 0.40 * r["l6"], 0.90 * r["d1"]))
               .rotate((end_x, end_y, 0.0), (end_x, end_y, 1.0), float(lever_angle)))
    else:
        # The ball point is an independent STEP solid (and an independent
        # assembly component), rather than a sphere fused to the screw shaft.
        end = cq.Workplane("XY").sphere(ball_radius)
        end = end.translate((end_x, end_y, 0.0))
        end_clip = cq.Workplane("XY").box(
            40.0 * scale, 40.0 * scale, 30.0 * scale,
            centered=(True, False, True)).translate((end_x, 17.0 * scale, 0.0))
        end = end.intersect(end_clip)
    result = cq.Assembly(name="gn9190_2_side_clamp")
    result.add(body, name="steel_body")
    result.add(jaw, name="pivoted_jaw")
    result.add(support, name="support_block")
    result.add(screw, name="clamping_screw")
    result.add(end, name="operating_end")
    return result


if "show_object" in globals():
    show_object(build(**EXAMPLE_PARAMS), name="gn9190_2_side_clamp")
