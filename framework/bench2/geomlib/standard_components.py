"""Reusable, deterministic ISO metric fastener geometry.

The public helpers are intentionally small enough to inline into derived
stand-alone CadQuery programs.  They perform no I/O and use no randomness.
"""

from __future__ import annotations

import math

import cadquery as cq


def iso_metric_fastener_dimensions(nominal_d):
    """Return sourced coarse-pitch and ISO 4017 hex-head dimensions.

    Supported values are the common M3--M16 subset.  ``external_root_d`` and
    ``internal_minor_d`` are ISO 68-1 basic-profile diameters; they are not a
    tolerance-class or manufacturing tap-drill specification.
    """
    rows = {
        3.0: (0.50, 5.5, 2.0),
        4.0: (0.70, 7.0, 2.8),
        5.0: (0.80, 8.0, 3.5),
        6.0: (1.00, 10.0, 4.0),
        8.0: (1.25, 13.0, 5.3),
        10.0: (1.50, 16.0, 6.4),
        12.0: (1.75, 18.0, 7.5),
        16.0: (2.00, 24.0, 10.0),
    }
    d = float(nominal_d)
    if d not in rows:
        raise ValueError("supported ISO metric sizes are M3, M4, M5, M6, M8, M10, M12, M16")
    pitch, across_flats, head_h = rows[d]
    return {
        "nominal_d": d,
        "pitch": pitch,
        "across_flats": across_flats,
        "head_h": head_h,
        "external_root_d": d - 1.226869 * pitch,
        "internal_minor_d": d - 1.082532 * pitch,
    }


def _modeled_external_metric_thread(nominal_d, pitch, length):
    """Return one solid with a visible, simplified 60-degree helical ridge."""
    major_r = float(nominal_d) / 2.0
    root_r = (float(nominal_d) - 1.226869 * float(pitch)) / 2.0
    radial_embed = min(0.08, 0.05 * float(pitch))
    # A 60-degree included V has half-width = radial height / sqrt(3).
    # Include the small radial embed so the swept ridge remains fused to core.
    half_width = (major_r - root_r + radial_embed) / math.sqrt(3.0)
    path_r = (major_r + root_r) / 2.0
    path_height = float(length) - 2.0 * half_width
    if path_height <= 0.0:
        raise ValueError("modeled thread length is too short for one 60-degree tooth")

    core = cq.Workplane("XY").circle(root_r).extrude(float(length))
    path = cq.Wire.makeHelix(float(pitch), path_height, path_r)
    profile = (
        cq.Workplane("XZ")
        .polyline(
            [
                (root_r - radial_embed, -half_width),
                (major_r, 0.0),
                (root_r - radial_embed, half_width),
            ]
        )
        .close()
    )
    ridge = profile.sweep(path, isFrenet=True).translate((0.0, 0.0, half_width))
    return core.union(ridge)


def make_iso_hex_bolt(nominal_d, length, thread_length, modeled_thread=0):
    """Build an ISO 4017-style hex-head bolt along Z.

    The head bearing face is at ``z=0`` and the shank extends toward negative
    Z.  ``modeled_thread=0`` returns the major-diameter envelope;
    ``modeled_thread=1`` adds a simplified helical ridge over ``thread_length``.
    """
    data = iso_metric_fastener_dimensions(nominal_d)
    shank_l = float(length)
    thread_l = float(thread_length)
    if shank_l <= 0.0:
        raise ValueError("bolt length must be positive")
    if thread_l <= 0.0 or thread_l > shank_l:
        raise ValueError("thread_length must be positive and no greater than length")
    if int(modeled_thread) not in (0, 1):
        raise ValueError("modeled_thread must be 0 or 1")

    d = data["nominal_d"]
    if int(modeled_thread):
        threaded = _modeled_external_metric_thread(
            d, data["pitch"], thread_l
        ).translate((0.0, 0.0, -shank_l))
        plain_l = shank_l - thread_l
        if plain_l > 0.0:
            plain = (
                cq.Workplane("XY")
                .workplane(offset=-shank_l + thread_l - 0.05)
                .circle(d / 2.0)
                .extrude(plain_l + 0.10)
            )
            shank = threaded.union(plain)
        else:
            shank = threaded
    else:
        shank = cq.Workplane("XY").circle(d / 2.0).extrude(-shank_l)

    corner_d = data["across_flats"] / math.cos(math.pi / 6.0)
    head = cq.Workplane("XY").polygon(6, corner_d).extrude(data["head_h"])
    # A 0.05 mm hidden overlap avoids a face-touch-only compound at z=0.
    neck = cq.Workplane("XY").circle(d / 2.0).extrude(0.05)
    return shank.union(neck).union(head)


def make_iso_tapped_hole_cutter(nominal_d, depth):
    """Return an ISO 68-1 basic tap-minor cylindrical cutter along -Z.

    This is explicitly a ``minor_bore`` representation, not modeled helical
    thread geometry or a manufacturing tap-drill recommendation.
    """
    data = iso_metric_fastener_dimensions(nominal_d)
    hole_depth = float(depth)
    if hole_depth <= 0.0:
        raise ValueError("tapped-hole depth must be positive")
    return (
        cq.Workplane("XY")
        .circle(data["internal_minor_d"] / 2.0)
        .extrude(-hole_depth)
    )
