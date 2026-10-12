"""JW Winco GN 784 swivel ball joint mount.

The catalog selectors choose one published row and one nonblank thread
alternative.  The four physical components remain separate in a named
CadQuery Assembly.
"""

import math

import cadquery as cq


# Thread codes are numeric because BenchCAD PARAM_SPEC values are numeric.
# (label, nominal major diameter in mm, metric flag)
_THREADS = (
    ("M4", 4.0, 1),
    ("M5", 5.0, 1),
    ("M6", 6.0, 1),
    ("M8", 8.0, 1),
    ("M10", 10.0, 1),
    ("1/4-20", 6.35, 0),
    ("3/8-16", 9.525, 0),
)


# The eight printed rows of the GN 784 metric table.  A direct is d2,
# A socket is d3, and B is d4.  None represents a blank catalog field.
_CATALOG_ROWS = (
    dict(
        label="23-M4/M5", d1=23.0, a_direct=0, a_socket=(1,), r1_a=17.3,
        r2=24.8, b_threads=(1,), r1_b=17.3, l1=8.0, d5=5.0, d6=14.0,
        d7=11.0, d8=2.5, h1=26.6, h2=21.7, h3=10.6, k=32.0, l2=22.0,
        m=7.0, af1=9.0, af2=2.5, clamp_torque=1.5, stop_torque=4.5,
    ),
    dict(
        label="23-1/4", d1=23.0, a_direct=None, a_socket=(5,), r1_a=None,
        r2=24.8, b_threads=(2, 5), r1_b=17.3, l1=10.0, d5=5.0,
        d6=14.0, d7=11.0, d8=2.5, h1=26.6, h2=21.7, h3=10.6,
        k=32.0, l2=22.0, m=7.0, af1=9.0, af2=2.5,
        clamp_torque=1.5, stop_torque=4.5,
    ),
    dict(
        label="31-M5/M6", d1=31.0, a_direct=1, a_socket=(2, 5),
        r1_a=21.5, r2=32.5, b_threads=(2, 5), r1_b=21.5, l1=10.0,
        d5=6.0, d6=18.0, d7=14.0, d8=3.5, h1=35.5, h2=29.6,
        h3=14.9, k=36.0, l2=22.0, m=9.0, af1=12.0, af2=3.0,
        clamp_torque=2.5, stop_torque=6.5,
    ),
    dict(
        label="31-M8", d1=31.0, a_direct=None, a_socket=(), r1_a=None,
        r2=32.5, b_threads=(3,), r1_b=21.5, l1=12.0, d5=6.0,
        d6=18.0, d7=14.0, d8=3.5, h1=35.5, h2=29.6, h3=14.9,
        k=36.0, l2=22.0, m=9.0, af1=12.0, af2=3.0,
        clamp_torque=2.5, stop_torque=6.5,
    ),
    dict(
        label="39-M5/M6", d1=39.0, a_direct=1, a_socket=(2,), r1_a=25.5,
        r2=36.2, b_threads=(2,), r1_b=25.5, l1=10.0, d5=8.0,
        d6=24.0, d7=15.0, d8=4.5, h1=45.0, h2=37.2, h3=18.9,
        k=44.0, l2=30.0, m=12.0, af1=13.0, af2=4.0,
        clamp_torque=4.0, stop_torque=16.0,
    ),
    dict(
        label="39-M8/3-8", d1=39.0, a_direct=None, a_socket=(3, 6),
        r1_a=None, r2=40.5, b_threads=(3, 6), r1_b=25.5, l1=12.0,
        d5=8.0, d6=24.0, d7=15.0, d8=4.5, h1=45.0, h2=37.2,
        h3=18.9, k=44.0, l2=30.0, m=12.0, af1=13.0, af2=4.0,
        clamp_torque=4.0, stop_torque=16.0,
    ),
    dict(
        label="49-M8/3-8", d1=49.0, a_direct=3, a_socket=(6,),
        r1_a=30.8, r2=44.8, b_threads=(3, 6), r1_b=30.8, l1=12.0,
        d5=8.0, d6=28.0, d7=19.5, d8=4.5, h1=56.0, h2=46.1,
        h3=24.0, k=49.0, l2=30.0, m=16.0, af1=17.0, af2=4.0,
        clamp_torque=4.0, stop_torque=20.0,
    ),
    dict(
        label="49-M10", d1=49.0, a_direct=None, a_socket=(4,),
        r1_a=None, r2=51.8, b_threads=(4,), r1_b=30.8, l1=15.0,
        d5=8.0, d6=28.0, d7=19.5, d8=4.5, h1=56.0, h2=46.1,
        h3=24.0, k=49.0, l2=30.0, m=16.0, af1=17.0, af2=4.0,
        clamp_torque=4.0, stop_torque=20.0,
    ),
)


def _catalog_dimensions(catalog_row, ball_type, thread_code):
    """Return one valid published row/type/thread combination, else None."""
    row_index = int(catalog_row)
    type_index = int(ball_type)
    code = int(thread_code)
    if (
        row_index != catalog_row
        or type_index != ball_type
        or code != thread_code
        or row_index < 0
        or row_index >= len(_CATALOG_ROWS)
        or type_index not in (0, 1)
        or code < 0
        or code >= len(_THREADS)
    ):
        return None

    row = dict(_CATALOG_ROWS[row_index])
    thread_label, thread_d, is_metric = _THREADS[code]
    if type_index == 0:
        if row["a_direct"] == code:
            a_style = 0
            r_ball = row["r1_a"]
        elif code in row["a_socket"]:
            a_style = 1
            r_ball = row["r2"]
        else:
            return None
        stud_length = 0.0
        internal_thread = 1
    else:
        if code not in row["b_threads"]:
            return None
        a_style = -1
        r_ball = row["r1_b"]
        stud_length = row["l1"]
        internal_thread = 0

    row.update(
        catalog_row=row_index,
        ball_type=type_index,
        thread_code=code,
        thread_label=thread_label,
        thread_d=thread_d,
        is_metric=is_metric,
        internal_thread=internal_thread,
        a_style=a_style,
        r_ball=r_ball,
        stud_length=stud_length,
        thread_depth=thread_d * (1.5 if is_metric else 1.2),
    )
    return row


def _valid_catalog_variants(catalog_row, difficulty):
    """Valid (ball_type, thread_code) pairs for one row and difficulty."""
    row_index = int(catalog_row)
    if row_index != catalog_row or row_index < 0 or row_index >= len(_CATALOG_ROWS):
        return ()
    row = _CATALOG_ROWS[row_index]
    variants = []
    if row["a_direct"] is not None:
        variants.append((0, row["a_direct"]))
    variants.extend((0, code) for code in row["a_socket"])
    variants.extend((1, code) for code in row["b_threads"])
    if difficulty != "hard":
        variants = [v for v in variants if _THREADS[v[1]][2] == 1]
    if difficulty == "easy":
        variants = [v for v in variants if v[0] == 0]
    return tuple(variants)


def _geometry_proportions(d):
    """Undimensioned GN 784 details, all explicitly proportion based."""
    cavity_clearance = max(0.20, 0.012 * d["d6"])
    base_clearance = max(0.15, 0.008 * d["d1"])
    slot_clearance = max(0.25, 0.010 * d["d1"])
    base_d = 0.80 * d["d1"]
    base_t = 0.28 * d["h3"]
    opening_r = max(0.44 * d["d6"], d["d7"] / 2.0 + cavity_clearance)
    screw_d = 0.18 * d["d1"]
    actuator_clearance = max(0.20, 0.012 * d["d1"])
    housing_wall = d["d1"] / 2.0 - (d["d6"] / 2.0 + cavity_clearance)
    lower_neck_d = 0.55 * d["d7"]
    neck_embed = 0.58 * d["d6"] / 2.0
    outside_margin = max(0.60, 0.030 * d["d1"])
    lower_neck_length = d["d1"] / 2.0 + outside_margin - neck_embed
    return dict(
        cavity_clearance=cavity_clearance,
        base_clearance=base_clearance,
        slot_clearance=slot_clearance,
        base_d=base_d,
        base_t=base_t,
        opening_r=opening_r,
        screw_d=screw_d,
        actuator_clearance=actuator_clearance,
        housing_wall=housing_wall,
        lower_neck_d=lower_neck_d,
        lower_neck_length=lower_neck_length,
        neck_embed=neck_embed,
        outside_margin=outside_margin,
    )


def _hex_prism(af, height, z0):
    across_corners = 2.0 * af / math.sqrt(3.0)
    return (
        cq.Workplane("XY")
        .polygon(6, across_corners)
        .extrude(height)
        .translate((0.0, 0.0, z0))
    )


def _x_cylinder(radius, length, x0, z0):
    return (
        cq.Workplane("YZ", origin=(x0, 0.0, z0))
        .circle(radius)
        .extrude(length)
    )


def _stem_sweep_cut(d, g):
    """Clear only the lower thin neck from vertical through 90 degrees to -X."""
    sweep_length = d["r2"] + d["l1"] + d["d6"]
    slot_r = g["lower_neck_d"] / 2.0 + g["slot_clearance"]
    diagonal = sweep_length / math.sqrt(2.0)
    sector = (
        cq.Workplane(
            "XZ",
            origin=(0.0, slot_r, d["h2"]),
        )
        .moveTo(0.0, 0.0)
        .lineTo(0.0, sweep_length)
        .threePointArc(
            (-diagonal, diagonal),
            (-sweep_length, 0.0),
        )
        .close()
        .offset2D(slot_r)
        .extrude(2.0 * slot_r)
    )
    return sector.clean()


def build_housing(catalog_row, ball_type, thread_code):
    """Build the black anodized cylindrical socket housing."""
    d = _catalog_dimensions(catalog_row, ball_type, thread_code)
    if d is None:
        raise ValueError("blank or invalid GN 784 row/type/thread combination")
    g = _geometry_proportions(d)

    housing = cq.Workplane("XY").circle(d["d1"] / 2.0).extrude(d["h1"])

    ball_cavity = (
        cq.Workplane("XY")
        .sphere(d["d6"] / 2.0 + g["cavity_clearance"])
        .translate((0.0, 0.0, d["h2"]))
    )
    housing = housing.cut(ball_cavity)

    top_opening = (
        cq.Workplane("XY")
        .workplane(offset=d["h2"])
        .circle(g["opening_r"])
        .extrude(d["h1"] - d["h2"] + d["d6"])
    )
    housing = housing.cut(top_opening)
    housing = housing.cut(_stem_sweep_cut(d, g))

    base_pocket = (
        cq.Workplane("XY")
        .workplane(offset=-0.1)
        .circle(g["base_d"] / 2.0 + g["base_clearance"])
        .extrude(g["base_t"] + 0.2)
    )
    housing = housing.cut(base_pocket)

    actuator_bore = _x_cylinder(
        g["screw_d"] / 2.0 + g["actuator_clearance"],
        d["d1"] / 2.0 + 2.0,
        0.0,
        d["h3"],
    )
    housing = housing.cut(actuator_bore)

    # The complete 90-degree channel can sever small top-seat remnants.
    # Those chips are removed in the real slotting operation; retain only the
    # connected cylindrical housing body.
    housing_solids = housing.solids().vals()
    return cq.Workplane(obj=max(housing_solids, key=lambda solid: solid.Volume()))


def build_ball(catalog_row, ball_type, thread_code, swivel_angle):
    """Build the captured ball plus its selected A or B threaded boss."""
    d = _catalog_dimensions(catalog_row, ball_type, thread_code)
    if d is None:
        raise ValueError("blank or invalid GN 784 row/type/thread combination")
    angle = float(swivel_angle)
    if angle < 0.0 or angle > 90.0:
        raise ValueError("swivel_angle must stay inside the published 0-90 degree range")
    g = _geometry_proportions(d)

    ball_r = d["d6"] / 2.0
    result = (
        cq.Workplane("XY")
        .sphere(ball_r)
        .translate((0.0, 0.0, d["h2"]))
    )

    neck_bottom = d["h2"] + g["neck_embed"]
    neck_top = neck_bottom + g["lower_neck_length"]
    lower_neck = (
        cq.Workplane("XY")
        .circle(g["lower_neck_d"] / 2.0)
        .extrude(g["lower_neck_length"])
        .translate((0.0, 0.0, neck_bottom))
    )
    result = result.union(lower_neck)

    if d["ball_type"] == 0:
        top_z = d["h2"] + d["r_ball"]
        available = top_z - neck_top
        min_upper_h = max(0.25 * d["thread_d"], 0.05 * d["d1"])
        wanted_middle_h = max(0.16 * d["d1"], 0.32 * d["af1"])
        middle_h = min(wanted_middle_h, available - min_upper_h)
        if middle_h <= 0.5:
            raise ValueError("GN 784 row leaves no positive middle collar height")
        middle_top = neck_top + middle_h
        collar = (
            cq.Workplane("XY")
            .circle(d["d7"] / 2.0)
            .extrude(middle_h)
            .translate((0.0, 0.0, neck_top))
        )
        hex_h = 0.55 * middle_h
        middle_hex = _hex_prism(d["af1"], hex_h, middle_top - hex_h)
        upper_d = min(
            0.78 * d["d7"],
            max(d["thread_d"] + 0.10 * d["d1"], 0.62 * d["d7"]),
        )
        upper = (
            cq.Workplane("XY")
            .circle(upper_d / 2.0)
            .extrude(top_z - middle_top)
            .translate((0.0, 0.0, middle_top))
        )
        result = result.union(collar).union(middle_hex).union(upper)
        thread_hole = (
            cq.Workplane("XY")
            .workplane(offset=top_z + 0.05)
            .circle(d["thread_d"] / 2.0)
            .extrude(-d["thread_depth"] - 0.10)
        )
        result = result.cut(thread_hole)
    else:
        middle_top = d["h2"] + d["r_ball"]
        middle_h = middle_top - neck_top
        if middle_h <= 0.5:
            raise ValueError("GN 784 row leaves no positive middle collar height")
        collar = (
            cq.Workplane("XY")
            .circle(d["d7"] / 2.0)
            .extrude(middle_h)
            .translate((0.0, 0.0, neck_top))
        )
        hex_h = 0.55 * middle_h
        middle_hex = _hex_prism(d["af1"], hex_h, middle_top - hex_h)
        result = result.union(collar).union(middle_hex)
        stud = (
            cq.Workplane("XY")
            .workplane(offset=middle_top)
            .circle(d["thread_d"] / 2.0)
            .extrude(d["stud_length"])
        )
        result = result.union(stud)

    return result.rotate(
        (0.0, 0.0, d["h2"]),
        (0.0, 1.0, d["h2"]),
        -angle,
    )


def build_base(catalog_row, ball_type, thread_code):
    """Build the plain-aluminum bottom base plate."""
    d = _catalog_dimensions(catalog_row, ball_type, thread_code)
    if d is None:
        raise ValueError("blank or invalid GN 784 row/type/thread combination")
    g = _geometry_proportions(d)

    base = cq.Workplane("XY").circle(g["base_d"] / 2.0).extrude(g["base_t"])
    base_thread = (
        cq.Workplane("XY")
        .circle(d["d5"] / 2.0)
        .extrude(g["base_t"] + 0.1)
    )
    anti_rotation = (
        cq.Workplane("XY")
        .center(-d["m"], 0.0)
        .circle(d["d8"] / 2.0)
        .extrude(g["base_t"] + 0.1)
    )
    return base.cut(base_thread).cut(anti_rotation)


def build_actuator(catalog_row, ball_type, thread_code, clamp_actuator):
    """Build identification 1 lever or identification 2 socket set screw."""
    d = _catalog_dimensions(catalog_row, ball_type, thread_code)
    if d is None:
        raise ValueError("blank or invalid GN 784 row/type/thread combination")
    actuator = int(clamp_actuator)
    if actuator != clamp_actuator or actuator not in (1, 2):
        raise ValueError("clamp_actuator must be GN 784 identification 1 or 2")
    g = _geometry_proportions(d)

    housing_r = d["d1"] / 2.0
    stud_x0 = 0.15 * d["d1"]
    if actuator == 2:
        head_length = 0.16 * d["d1"]
        x_end = housing_r + head_length
        screw = _x_cylinder(
            g["screw_d"] / 2.0,
            x_end - stud_x0,
            stud_x0,
            d["h3"],
        )
        head = _x_cylinder(
            0.72 * g["screw_d"],
            head_length,
            housing_r,
            d["h3"],
        )
        result = screw.union(head)
        socket = (
            cq.Workplane("YZ", origin=(x_end + 0.05, 0.0, d["h3"]))
            .polygon(6, 2.0 * d["af2"] / math.sqrt(3.0))
            .extrude(-0.45 * head_length)
        )
        return result.cut(socket)

    handle_w = 0.20 * d["l2"]
    handle_y = 0.17 * d["d1"]
    pivot_length = 0.16 * d["d1"]
    handle_start_x = housing_r + 0.60 * pivot_length
    handle_end_x = d["k"] - handle_w / 2.0
    handle_start_z = d["h3"]
    handle_end_z = d["h3"] + d["l2"] - handle_w / 2.0
    stud = _x_cylinder(
        g["screw_d"] / 2.0,
        housing_r + pivot_length - stud_x0,
        stud_x0,
        d["h3"],
    )
    pivot = _x_cylinder(
        0.72 * g["screw_d"],
        pivot_length,
        housing_r,
        d["h3"],
    )
    dx = handle_end_x - handle_start_x
    dz = handle_end_z - handle_start_z
    handle_angle = math.degrees(math.atan2(dz, dx))
    handle_length = math.sqrt(dx * dx + dz * dz) + handle_w
    handle = (
        cq.Workplane(
            "XZ",
            origin=(
                (handle_start_x + handle_end_x) / 2.0,
                handle_y / 2.0,
                (handle_start_z + handle_end_z) / 2.0,
            ),
        )
        .slot2D(handle_length, handle_w, handle_angle)
        .extrude(handle_y)
    )
    return stud.union(pivot).union(handle)


def build(catalog_row, ball_type, thread_code, clamp_actuator, swivel_angle):
    """Return the four-component GN 784 static catalog pose."""
    housing = build_housing(catalog_row, ball_type, thread_code)
    ball = build_ball(catalog_row, ball_type, thread_code, swivel_angle)
    base = build_base(catalog_row, ball_type, thread_code)
    actuator = build_actuator(
        catalog_row, ball_type, thread_code, clamp_actuator
    )

    result = cq.Assembly()
    result.add(housing, name="housing", color=cq.Color(0.08, 0.08, 0.08))
    result.add(ball, name="ball", color=cq.Color(0.72, 0.74, 0.76))
    result.add(base, name="base", color=cq.Color(0.72, 0.74, 0.76))
    result.add(
        actuator,
        name="clamp_actuator",
        color=cq.Color(0.58, 0.60, 0.62),
    )
    return result
