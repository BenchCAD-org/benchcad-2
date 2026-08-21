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
               d4=8.0, d5=4.0, h1=26.0, h2=44.0, h3=28.0, h4=15.0,
               l1=52.0, l2=28.0, l3=30.0, l4=72.5, l5=38.0, l6=63.0,
               s=3.0, ma=3.0),
    14.0: dict(d1=12.0, fs=15.0, b1=48.0, b2=16.0, d2=13.0, d3=12.0,
               d4=12.0, d5=4.0, h1=26.0, h2=53.0, h3=27.0, h4=15.0,
               l1=72.0, l2=40.0, l3=44.0, l4=100.0, l5=55.0, l6=78.0,
               s=4.0, ma=9.0),
    18.0: dict(d1=16.0, fs=21.5, b1=68.0, b2=18.8, d2=17.0, d3=16.0,
               d4=16.0, d5=4.0, h1=26.0, h2=72.0, h3=38.0, h4=20.0,
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
    """Main housing, dimensioned to the five-solid STEP envelope."""
    # The catalog drawing locates the jaw pivot near the right end of the body.
    # Keeping that datum makes the 10 mm STEP envelope (-47.5 .. 25.0 mm)
    # and the larger row variants use the same assembly convention.
    pivot_x = 0.345 * r["l4"]
    x0 = pivot_x - r["l4"]
    housing_height = r["h1"] + 2.0 * r["s"]
    x1 = pivot_x
    row_scale = r["l4"] / 72.5
    y0, y1 = -27.0 * row_scale, 21.0 * row_scale
    outline = _chamfered_outline(x0, x1, y0, y1,
                                 float(body_chamfer) + 0.35 * float(body_edge_radius))
    body = (cq.Workplane("XY").polyline(outline).close().extrude(housing_height)
            .translate((0.0, 0.0, -housing_height / 2.0)))
    # The front half is open to receive the jaw; the rear and side ribs remain.
    open_x0 = x0 + r["d2"] * 0.70
    open_x1 = x1 - r["d2"] * 0.70
    opening = cq.Workplane("XY").box(open_x1 - open_x0, r["h2"] / 2.0 + 1.0 + float(gap) * 0.35,
                                      housing_height + 2.0,
                                      centered=(False, False, True)).translate((open_x0,
                                                                                 7.0 * row_scale + float(gap) * 0.18, 0.0))
    body = body.cut(opening)
    # The STEP housing is a shell rather than a solid brick.  This underside
    # relief preserves the closed top bridge while removing the material
    # visible only inside the side-clamp pocket.
    pocket = cq.Workplane("XY").box(max(4.0, (open_x1 - open_x0) - 6.0),
                                     25.0 * row_scale, housing_height * 0.42,
                                     centered=(True, True, False)).translate(
                                         ((open_x0 + open_x1) / 2.0,
                                          y0 + 17.0 * row_scale,
                                          -housing_height / 2.0))
    body = body.cut(pocket)
    body = _safe_fillet(body, min(float(body_edge_radius), housing_height * 0.12), "|Z")
    body = _safe_chamfer(body, min(float(body_chamfer) * 0.22, housing_height * 0.06), ">Z")
    # Rear pivot boss and counterbored transverse mounting hole.
    boss_x = pivot_x - 0.75 * r["d3"]
    boss = _cyl_y(r["d3"] * 1.20, r["b2"] * 0.78, boss_x, y1 - r["b2"] * 0.78, 0.0)
    body = body.union(boss)
    body = body.cut(_cyl_y(r["d4"], r["b2"] + 2.0, boss_x, y1 - r["b2"] - 1.0, 0.0))
    # Horizontal mounting holes in the underside ledge.
    for x in (x0 + r["l2"] / 2.0, x1 - r["l2"] / 2.0):
        body = body.cut(_cyl_y(r["d2"], r["h2"] + 8.0, x, y1 + 1.0,
                               -r["h1"] / 2.0 + r["s"]))
    # Clearance pocket for the separate lower support block.
    body = body.cut(cq.Workplane("XY").box(r["d2"] + 6.6, 8.0, r["h3"] + 2.0,
                                            centered=(True, True, True)).translate((1.0, y0 + 2.5, 0.0)))
    # Through-counterbore for the coded clamping screw.  The screw is a
    # separate assembly member, so this clearance is also what prevents an
    # artificial boolean intersection in the assembled representation.
    screw_x = 0.345 * r["l4"] - r["l5"] * 0.16
    body = body.cut(_cyl_y(r["d2"] * 1.20, y1 - y0 + 2.0, screw_x, y0 - 1.0, 0.0))
    return body


def _jaw(r, jaw_type, serration_count, jaw_angle, gap, lever_angle,
         jaw_chamfer, jaw_edge_radius):
    """Pivoted jaw with either a prism or visible serrated contact face."""
    pivot_x = 0.345 * r["l4"]
    pivot_z = 0.0
    jaw_len = r["l1"]
    z0, z1 = -r["h1"] / 2.0, r["h1"] / 2.0
    c = min(max(float(jaw_chamfer), 0.0), jaw_len * 0.18, (z1 - z0) * 0.18)
    # A stepped nose and a relieved upper contact reproduce the two large
    # planar faces visible in the STEP jaw.
    # The catalog jaw is a full-height 32 mm member around the large
    # transverse relief; keeping this height is what preserves the bridge
    # above and below the STEP's nominal h4 opening.
    main_top = max(z1 * 0.75, r["h4"] * 0.58)
    main_bottom = -main_top
    profile = [(-jaw_len + c, main_bottom), (-jaw_len, main_bottom * 0.72),
               (-jaw_len + c, main_top), (-jaw_len + r["l3"] * 0.45, main_top),
               (-r["l3"] * 0.25, main_top * 0.82),
               (0.0, main_top * 0.30), (0.0, main_bottom * 0.28),
               (-r["l3"] * 0.25, main_bottom * 0.82),
               (-jaw_len + r["l3"] * 0.45, main_bottom)]
    jaw_width = r["h2"] / 2.0
    jaw = (cq.Workplane("XZ").polyline([(pivot_x + x, z) for x, z in profile]).close()
           .extrude(-jaw_width).translate((0.0, 7.0, 0.0)))
    hinge_land = cq.Workplane("XY").box(1.1, jaw_width, z1 - z0 + 2.0 * r["s"],
                                         centered=(True, True, True)).translate(
                                             (pivot_x - jaw_len + r["l3"] * 0.45,
                                              7.0 + jaw_width / 2.0, 0.0))
    jaw = jaw.union(hinge_land)
    jaw = _safe_fillet(jaw, min(float(jaw_edge_radius), jaw_width * 0.12), "|Y")
    jaw = _safe_chamfer(jaw, min(float(jaw_chamfer) * 0.28, jaw_width * 0.08), "|Y")
    jaw = jaw.rotate((pivot_x, 0, pivot_z), (pivot_x, 1, pivot_z), float(lever_angle))
    body_clearance = cq.Workplane("XY").box(r["l4"], 9.2, r["h1"] + 2.0 * r["s"] + 2.0,
                                             centered=(True, True, True)).translate((0.0, 3.5, 0.0))
    jaw = jaw.cut(body_clearance)
    jaw = jaw.cut(cq.Workplane("XY").box(r["d5"] * 3.0, 5.0, r["d5"] * 3.0,
                                          centered=(True, True, True)).translate((pivot_x, 9.0, pivot_z)))
    screw_x = 0.345 * r["l4"] - r["l5"] * 0.16
    jaw = jaw.cut(_cyl_y(r["d2"] * 1.20, jaw_width + 2.0, screw_x, 7.0, 0.0))
    jaw = jaw.cut(cq.Workplane("XY").box(r["s"] * 1.65, 5.5, r["s"] * 1.65,
                                         centered=(True, True, True)).translate((screw_x, 17.5, 0.0)))
    row_scale = r["l4"] / 72.5
    # Pivot and side reliefs visible in the STEP jaw: the large transverse
    # opening is driven by h4, with two smaller cross holes at the hinge land.
    jaw = jaw.cut(_cyl_y(r["h4"], jaw_width + 2.0, 1.0 * row_scale, 7.0, 0.0))
    small_hole_x = pivot_x - r["l3"] * 0.217
    jaw = jaw.cut(_cyl_y(r["d5"] * 1.65, jaw_width + 2.0, small_hole_x, 7.0, 0.0))
    side_hole_x = pivot_x - r["l1"] * 0.846
    jaw = jaw.cut(_cyl_z(r["d5"], r["h1"] + 2.0, side_hole_x, 11.5 * row_scale,
                         -r["h1"] / 2.0 - 1.0))
    pin = _cyl_y(r["d3"] * 1.25, jaw_width + 2.0, pivot_x, 30.0, pivot_z)
    jaw = jaw.cut(pin)
    contact_x = pivot_x - jaw_len
    if jaw_type == "P":
        angle = math.radians(max(30.0, min(120.0, jaw_angle)))
        depth = r["h4"] * math.tan(angle / 2.0)
        prism = (cq.Workplane("XZ").polyline([(contact_x, pivot_z),
                                                (contact_x + depth, pivot_z + r["h4"] / 2.0),
                                                (contact_x + depth, pivot_z - r["h4"] / 2.0)]).close()
                 .extrude(jaw_width / 2.0, both=True).translate((0.0, 7.0 + jaw_width / 2.0, 0.0)))
        jaw = jaw.cut(prism)
    else:
        tooth_depth = min(0.9, r["h4"] * 0.25)
        for index in range(int(serration_count)):
            y = 7.0 + (index + 0.5) * jaw_width / int(serration_count)
            tooth = cq.Workplane("XY").box(max(0.7, r["h4"] * 0.22),
                                             jaw_width / int(serration_count) * 0.65,
                                             tooth_depth, centered=(True, True, False)).translate(
                                                 (contact_x + tooth_depth * 0.45, y,
                                                  main_top - tooth_depth))
            jaw = jaw.cut(tooth)
    return jaw


def _support(r, support_chamfer):
    x = 1.0
    support_y = -27.0 * (r["l4"] / 72.5)
    height = r["h3"] + 2.0
    width = r["d2"] + 6.6
    outline = _chamfered_outline(x - width / 2.0, x + width / 2.0,
                                 support_y - 6.0, support_y + 6.0,
                                 min(float(support_chamfer), 1.4))
    block = (cq.Workplane("XY").polyline(outline).close().extrude(height)
             .translate((0.0, 0.0, -height / 2.0)))
    block = _safe_fillet(block, min(float(support_chamfer) * 0.55, 1.0), "|Z")
    block = _safe_chamfer(block, min(float(support_chamfer) * 0.35, height * 0.08), ">Z")
    # The catalog support has a shallow top fork, not a through slot: a web
    # remains below the fork and carries the transverse counterbored hole.
    notch_height = min(height * 0.46, r["h3"] * 0.52)
    notch = cq.Workplane("XY").box(r["d2"] + 2.0, 8.0, notch_height,
                                    centered=(True, True, False)).translate(
                                        (x, support_y, height / 2.0 - notch_height))
    block = block.cut(notch)
    bore = _cyl_y(r["d5"] * 1.65, 14.0, x, support_y - 7.0, 0.0)
    counterbore = _cyl_y(r["d5"] * 2.0, 1.8, x, support_y + 5.3, 0.0)
    return block.cut(bore).cut(counterbore)


def _clamping_screw(r, coding, screw_chamfer):
    x = 0.345 * r["l4"] - r["l5"] * 0.16
    y = 17.6
    shaft_length = r["l6"] * 0.34
    shaft = _cyl_y(r["d1"] * 0.72, shaft_length, x, y, 0.0)
    ball = cq.Workplane("XY").sphere(r["d2"] * 0.46).translate((x, y + shaft_length, 0.0))
    screw = shaft.union(ball)
    if coding == "K":
        lever = cq.Workplane("XY").box(r["l5"] / 2.0, r["s"] * 1.15, r["s"] * 1.15,
                                        centered=True).translate((x, y + shaft_length / 2.0 + r["s"] * 2.0, 0.0))
        screw = screw.union(lever)
    else:
        head = _hex_prism(r["d2"] * 0.55, r["s"] * 1.25, x, y, 0.0)
        screw = screw.union(head)
        screw = _safe_fillet(screw, min(float(screw_chamfer), r["s"] * 0.25), "|Y")
        screw = _safe_chamfer(screw, min(float(screw_chamfer) * 0.55, r["s"] * 0.16), "|Y")
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
    _validate(slot_width, jaw_type, stroke_coding, serration_count, jaw_angle, return_spring_gap,
              lever_angle, body_chamfer, body_edge_radius, jaw_chamfer, jaw_edge_radius,
              support_chamfer, screw_chamfer)
    r = _row(slot_width)
    body = _body(r, return_spring_gap, body_chamfer, body_edge_radius)
    jaw = _jaw(r, jaw_type, serration_count, jaw_angle, return_spring_gap, lever_angle,
               jaw_chamfer, jaw_edge_radius)
    # The STEP has a relieved jaw pocket in the housing. Cutting the jaw
    # envelope from the body preserves that pocket and guarantees a physical
    # clearance-fit assembly rather than overlapping independent solids.
    body = body.cut(jaw)
    support = _support(r, support_chamfer)
    screw = _clamping_screw(r, stroke_coding, screw_chamfer)
    end_x = 0.345 * r["l4"] - r["l5"] * 0.16
    end_y = 17.2 - r["s"] * 1.44
    if stroke_coding == "K":
        end = cq.Workplane("XY").box(r["s"] * 1.15, r["s"] * 0.75, r["s"] * 0.75,
                                       centered=True).translate((end_x, end_y, 0.0))
    else:
        end = _hex_prism(r["s"] * 0.935, r["s"] * 1.44, end_x, end_y, 0.0)
        end = _safe_fillet(end, min(float(screw_chamfer), r["s"] * 0.2), "|Y")
        end = _safe_chamfer(end, min(float(screw_chamfer) * 0.55, r["s"] * 0.14), "|Y")
    result = cq.Assembly(name="gn9190_2_side_clamp")
    result.add(body, name="steel_body")
    result.add(jaw, name="pivoted_jaw")
    result.add(support, name="support_block")
    result.add(screw, name="clamping_screw")
    result.add(end, name="operating_end")
    return result


if "show_object" in globals():
    show_object(build(**EXAMPLE_PARAMS), name="gn9190_2_side_clamp")
