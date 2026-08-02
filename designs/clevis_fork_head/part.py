"""DIN 71752 clevis fork head without pin or retaining hardware."""

import cadquery as cq


def _thread_core_d(nominal_d):
    # ISO metric coarse pitches for the catalog's M4--M16 thread sizes.
    # The common tap-drill shop rule is core diameter ~= nominal - pitch;
    # rounding to 0.1 mm reproduces the official M4 STEP's 3.3 mm passage.
    if nominal_d == 4:
        pitch = 0.7
    elif nominal_d == 5:
        pitch = 0.8
    elif nominal_d == 6:
        pitch = 1.0
    elif nominal_d == 8:
        pitch = 1.25
    elif nominal_d == 10:
        pitch = 1.5
    elif nominal_d == 12:
        pitch = 1.75
    elif nominal_d == 14:
        pitch = 2.0
    elif nominal_d == 16:
        pitch = 2.0
    else:
        raise ValueError("unsupported DIN 71752 thread size")
    return round(nominal_d - pitch, 1)


def build(
    d1,
    is_long,
    l1,
    d2,
    a,
    b,
    d3,
    l2,
    l3,
    l4,
):
    fork_root_z = l2 - l1
    shank_radius = d3 / 2.0
    sphere_span = l3 - l4
    head_radius = (sphere_span * sphere_span + shank_radius * shank_radius) / (
        2.0 * sphere_span
    )
    head_center_z = l3 - head_radius

    # The official CAD envelope is one sphere passing through the d3 circle at
    # l4 and the theoretical axial apex at l3. Clipping it to the a x a square
    # produces both the forged root saddle and the crowned fork-arm ends.
    overlap = max(0.01, 0.005 * (fork_root_z - l4))
    forged_sphere = cq.Workplane(
        obj=cq.Solid.makeSphere(
            head_radius,
            cq.Vector(0.0, 0.0, head_center_z),
            angleDegrees1=-90.0,
            angleDegrees2=90.0,
        )
    )
    envelope_height = sphere_span + 2.0 * overlap
    square_envelope = (
        cq.Workplane("XY")
        .box(a, a, envelope_height)
        .translate((0.0, 0.0, (l4 + l3) / 2.0))
    )
    forged_head = forged_sphere.intersect(square_envelope).clean()

    # The catalog does not dimension the two 45-degree shank-end chamfers.
    # Scale the 0.4 mm chamfers measured in the official M4 STEP with d2.
    end_chamfer = 0.1 * d2
    shank = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(shank_radius - end_chamfer, 0.0)
        .lineTo(shank_radius, end_chamfer)
        .lineTo(shank_radius, l4 + overlap)
        .lineTo(0.0, l4 + overlap)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, l4 + overlap))
    )
    result = shank.union(forged_head).clean()

    # The orthographic view shows a flat slot floor at l2-l1.
    slot_height = l3 - fork_root_z + 1.0
    slot = (
        cq.Workplane("XY")
        .box(a + 2.0, b, slot_height)
        .translate((0.0, 0.0, fork_root_z + slot_height / 2.0))
    )
    result = result.cut(slot)

    pin_hole = (
        cq.Workplane("XZ")
        .center(0.0, l2)
        .circle(d1 / 2.0)
        .extrude(a / 2.0 + 1.0, both=True)
    )
    result = result.cut(pin_hole)

    # The official STEP shows the simplified threaded passage breaking through
    # at the fork-slot floor. Extend it slightly into the slot to avoid leaving
    # a coincident residual face at z = l2-l1.
    thread_depth = fork_root_z + overlap
    bore_radius = _thread_core_d(d2) / 2.0
    thread_bore = cq.Workplane("XY").circle(bore_radius).extrude(thread_depth)
    result = result.cut(thread_bore)
    bore_entry = cq.Workplane(
        obj=cq.Solid.makeCone(
            bore_radius + end_chamfer,
            bore_radius,
            end_chamfer,
            cq.Vector(0.0, 0.0, 0.0),
            cq.Vector(0.0, 0.0, 1.0),
        )
    )
    result = result.cut(bore_entry)
    return result
