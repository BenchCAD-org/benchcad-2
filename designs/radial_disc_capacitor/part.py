import cadquery as cq


def _lead_path(x_pos, lead_length, bend, side):
    return cq.Workplane("XZ").moveTo(x_pos, 0.0).lineTo(x_pos, -bend).lineTo(x_pos + side * bend * 0.55, -lead_length)


def _make_lead(x_pos, lead_radius, lead_length, bend, side):
    path = _lead_path(x_pos, lead_length, bend, side).wire()
    return cq.Workplane("XY").circle(lead_radius).sweep(path, multisection=False, isFrenet=True)


def _make_body(body_radius, body_thickness, dome_height):
    cylinder = cq.Workplane("XY").circle(body_radius).extrude(body_thickness - dome_height)
    dome = cq.Workplane("XY").sphere(body_radius).translate((0, 0, body_thickness - dome_height))
    return cylinder.union(dome.intersect(cq.Workplane("XY").box(body_radius * 2.2, body_radius * 2.2, dome_height).translate((0, 0, body_thickness - dome_height / 2.0))))


def build(
    body_diameter,
    body_thickness,
    lead_spacing,
    lead_diameter,
    lead_length,
    lead_embed,
):
    body_radius = body_diameter / 2.0
    lead_radius = lead_diameter / 2.0
    half_spacing = lead_spacing / 2.0
    bend = max(0.8, 0.18 * lead_length)
    dome_height = min(0.22 * body_thickness, 0.8)

    body = _make_body(body_radius, body_thickness, dome_height)

    leads = _make_lead(-half_spacing, lead_radius, lead_length, bend, -1).union(
        _make_lead(half_spacing, lead_radius, lead_length, bend, 1)
    )
    leads = leads.translate((0.0, 0.0, -lead_embed))

    result = body.union(leads, clean=True).clean()
    return result
