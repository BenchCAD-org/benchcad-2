import cadquery as cq


def _make_lead(x_pos, lead_radius, lead_length, lead_embed):
    return (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x_pos, 0, -lead_length))
        .circle(lead_radius)
        .extrude(lead_length + lead_embed)
    )


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

    body = cq.Workplane("XY").circle(body_radius).extrude(body_thickness)

    leads = _make_lead(-half_spacing, lead_radius, lead_length, lead_embed).union(
        _make_lead(half_spacing, lead_radius, lead_length, lead_embed)
    )

    result = body.union(leads, clean=True).clean()
    return result
