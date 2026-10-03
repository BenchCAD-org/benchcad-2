"""Four-seat twisted bracelet, reconstructed from native CAD (issue #226).

Curved strip sections are projected into the path-normal plane before lofting.
This is an explicit cross-kernel approximation; see NOTES.md.
"""

import math

import cadquery as cq


def _bridge(a, b, r, R, phase, axis, mirrored=False, sections=20):
    wires = []
    for i in range(sections + 1):
        theta = 0.18 + (math.pi / 2 - 0.36) * i / sections
        beta = 4 * theta
        off = a - axis
        x = axis - a + off * math.cos(beta)
        z = -off * math.sin(beta)
        vx = math.cos(beta)
        vz = -math.sin(beta)
        dx = -4 * off * math.sin(beta)
        dz = -4 * off * math.cos(beta)
        c, s = math.cos(phase), math.sin(phase)
        x, z = c * x - s * z, s * x + c * z
        vx, vz = c * vx - s * vz, s * vx + c * vz
        dx, dz = c * dx - s * dz, s * dx + c * dz
        if mirrored:
            z = -z
            vz = -vz
            dz = -dz
        dr = 0.319695614 * x + 0.947520297 * z
        h = 0.947520297 * x - 0.319695614 * z
        vr = 0.319695614 * vx + 0.947520297 * vz
        vh = 0.947520297 * vx - 0.319695614 * vz
        c, s = math.cos(theta), math.sin(theta)
        xd = cq.Vector(vr * c, vr * s, vh)
        yd = cq.Vector(-s, c, 0)
        drdt = 0.319695614 * dx + 0.947520297 * dz
        dhdt = 0.947520297 * dx - 0.319695614 * dz
        tangent = cq.Vector(drdt * c - (R + dr) * s, drdt * s + (R + dr) * c, dhdt).normalized()
        xd = xd - tangent.multiply(xd.dot(tangent))
        yd = yd - tangent.multiply(yd.dot(tangent))
        origin = cq.Vector((R + dr) * c, (R + dr) * s, h)
        pts = [
            origin
            + xd.multiply(r * math.cos(j * math.pi / 8))
            + yd.multiply(r * (1 + dr / R) * math.sin(j * math.pi / 8))
            for j in range(17)
        ]
        wires.append(cq.Wire.assembleEdges([cq.Edge.makeSpline(pts[:-1], periodic=True)]))
    builder = cq.occ_impl.shapes.BRepOffsetAPI_ThruSections(True, False)
    builder.CheckCompatibility(False)
    for w in wires:
        builder.AddWire(w.wrapped)
    builder.Build()
    return cq.Solid(builder.Shape())


def _face(pts):
    return cq.Face.makeFromWires(cq.Wire.makePolygon(pts, close=True))


def _gem(d=6.11754694, h=4.357860213):
    radius = d / 2
    scale = h / 4.357860213
    tip = cq.Vector(0, 0, -2.607860213 * scale)
    girdle = 0.25 * scale
    crown = 1.75 * scale
    angle = math.radians(-0.775808)
    bottom = [
        cq.Vector(
            radius * math.cos(angle + i * math.pi / 8),
            radius * math.sin(angle + i * math.pi / 8),
            0,
        )
        for i in range(16)
    ]
    upper = [cq.Vector(v.x, v.y, girdle) for v in bottom]
    top = [
        cq.Vector(
            1.77546563 / 3.05877347 * radius * math.cos(angle + i * math.pi / 4),
            1.77546563 / 3.05877347 * radius * math.sin(angle + i * math.pi / 4),
            crown,
        )
        for i in range(8)
    ]
    faces = []
    for i in range(16):
        j = (i + 1) % 16
        faces.extend(
            [_face([tip, bottom[j], bottom[i]]), _face([bottom[i], bottom[j], upper[j], upper[i]])]
        )
    for i in range(8):
        a = upper[2 * i]
        b = upper[2 * i + 1]
        c = upper[(2 * i + 2) % 16]
        t = top[i]
        u = top[(i + 1) % 8]
        faces.extend([_face([a, b, t]), _face([b, u, t]), _face([b, c, u])])
    faces.append(_face(top))
    shape = cq.Solid.makeSolid(cq.Shell.makeShell(faces))
    hole = cq.Solid.makeCylinder(
        0.903045528 / 3.05877347 * radius, 0.051 * scale, cq.Vector(0, 0, 1.7 * scale)
    )
    return shape.cut(hole)


def build(
    ring_radius_R, seat_radius_B, seat_wall_W, gem_diameter_G, gem_height_H, setting_clearance_C
):
    # Work in the native scale so a uniform size change cannot change Boolean
    # tolerances relative to the thin braid. Dimensions remain fully editable.
    scale = ring_radius_R / 12.6281512226808
    R = 12.6281512226808
    B = seat_radius_B / scale
    W = seat_wall_W / scale
    G = gem_diameter_G / scale
    H = gem_height_H / scale
    C = setting_clearance_C / scale
    a, b, r = 1.32471927992021, 2.54, 0.635
    outer = cq.Solid.makeSphere(R + 0.57983753 * B, angleDegrees1=-90)
    inner = cq.Solid.makeSphere(R - 0.761844 * B, angleDegrees1=-90)
    seats = [
        cq.Solid.makeSphere(B, cq.Vector(R, 0, 0), angleDegrees1=-90),
        cq.Solid.makeSphere(B, cq.Vector(0, R, 0), angleDegrees1=-90),
    ]
    shapes = [s.intersect(outer).cut(inner) for s in seats]
    # Original: two eccentric four-turn sweeps, arrayed five times about the
    # straight spine; then five selected bodies mirrored in the native XY plane.
    for axis in (0, b):
        for n in range(5):
            shapes.append(_bridge(a, b, r, R, n * 2 * math.pi / 5, axis))
    for axis, n in ((0, 0), (0, 3), (0, 4), (b, 1), (b, 2)):
        shapes.append(_bridge(a, b, r, R, n * 2 * math.pi / 5, axis, True))
    spine = cq.Workplane("XZ").moveTo(R, 0).circle(r).revolve(90, (0, 0), (0, 1)).val()
    shapes.append(spine)
    quarter = shapes[0]
    for shape in shapes[1:]:
        quarter = quarter.fuse(shape, tol=0.0001)
    body = quarter.fuse(*[quarter.rotate((0, 0, 0), (0, 0, 1), angle) for angle in (90, 180, 270)])
    gemstone = _gem(G, H)
    # Slightly oversized matching pavilion/crown provides documented setting
    # clearance. A circular recess on the gem table is decorative, not a hole.
    seat_tool = _gem(G + 2 * C, H + 2 * C)
    gems = []
    for angle in (0, 90, 180, 270):
        theta = math.radians(angle)
        cavity = cq.Solid.makeSphere(
            B - W, cq.Vector(R * math.cos(theta), R * math.sin(theta), 0), angleDegrees1=-90
        )
        body = body.cut(cavity)
        location = cq.Location(
            cq.Vector((R + 0.43653 * B) * math.cos(theta), (R + 0.43653 * B) * math.sin(theta), 0),
            cq.Vector(-math.sin(theta), math.cos(theta), 0),
            90,
        )
        body = body.cut(seat_tool.moved(location))
        gems.append(
            cq.Location(
                cq.Vector(
                    (R + 0.43653 * B) * scale * math.cos(theta),
                    (R + 0.43653 * B) * scale * math.sin(theta),
                    0,
                ),
                cq.Vector(-math.sin(theta), math.cos(theta), 0),
                90,
            )
        )
    result = cq.Assembly(name="twisted_gemstone_bracelet_asm")
    # The right-handed reference frame has +Z opposite the original flex-plane
    # normal after +X is aligned to the source's right-hand seat.
    result.add(body.mirror("XY").scale(scale), name="bracelet", color=cq.Color(0.83, 0.65, 0.23))
    for i, location in enumerate(gems):
        result.add(
            gemstone.mirror("YZ").scale(scale),
            name=f"gem_{i + 1:02d}",
            loc=location,
            color=cq.Color(0.40, 0.65, 0.78),
        )
    return result
