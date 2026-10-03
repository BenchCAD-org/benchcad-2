"""Native-reference proportions; no catalog or tolerance standard is claimed."""

import math

SOURCE = "proportion: native SOLIDWORKS snapshot measurements, issue #226; see NOTES.md"
DIFFS = ("easy", "medium", "hard")

PARAM_SPEC = {
    "ring_radius_R": dict(
        desc="Radius of the four spherical seat centres in the XY plane (R)",
        unit="mm",
        range={"easy": (12.3, 13.0), "medium": (11.0, 15.0), "hard": (10.0, 18.0)},
        source=SOURCE,
    ),
    "seat_radius_B": dict(
        desc="Outer radius of each spherical seat (B)",
        unit="mm",
        refine=True,
        range={"easy": (4.5, 5.1), "medium": (3.9, 6.1), "hard": (3.6, 7.2)},
        source=SOURCE,
    ),
    "seat_wall_W": dict(
        desc="Radial spherical wall before the inner/outer envelope trims (W)",
        unit="mm",
        refine=True,
        range={"easy": (1.1, 1.5), "medium": (0.97, 1.71), "hard": (0.9, 2.02)},
        source=SOURCE,
    ),
    "gem_diameter_G": dict(
        desc="Circumdiameter of the sixteen-sided gem girdle (G)",
        unit="mm",
        refine=True,
        range={"easy": (5.6, 6.7), "medium": (4.87, 7.93), "hard": (4.5, 9.36)},
        source=SOURCE,
    ),
    "gem_height_H": dict(
        desc="Gem axial height from pavilion tip to table (H)",
        unit="mm",
        refine=True,
        range={"easy": (3.9, 4.9), "medium": (3.4, 5.8), "hard": (3.15, 6.84)},
        source=SOURCE,
    ),
    "setting_clearance_C": dict(
        desc="Radial and half-height enlargement of the matching setting tool (C)",
        unit="mm",
        refine=True,
        range={d: (0.015, 0.04) for d in DIFFS},
        source=SOURCE,
    ),
}


def refine(p, difficulty, rng):
    # Correlated proportions preserve the native seat/strand interfaces.
    bands = {
        "easy": ((0.376, 0.381), (0.264, 0.269), (1.276, 1.284), (0.710, 0.715)),
        "medium": ((0.370, 0.390), (0.255, 0.275), (1.260, 1.290), (0.705, 0.725)),
        "hard": ((0.360, 0.400), (0.250, 0.280), (1.250, 1.300), (0.700, 0.730)),
    }
    br, wr, gr, hr = bands[difficulty]
    p["seat_radius_B"] = round(p["ring_radius_R"] * float(rng.uniform(*br)), 6)
    p["seat_wall_W"] = round(p["seat_radius_B"] * float(rng.uniform(*wr)), 6)
    p["gem_diameter_G"] = round(p["seat_radius_B"] * float(rng.uniform(*gr)), 6)
    p["gem_height_H"] = round(p["gem_diameter_G"] * float(rng.uniform(*hr)), 6)
    p["setting_clearance_C"] = round(0.004 * p["gem_diameter_G"], 6)


def check(p):
    bad = []
    R, B, W = p["ring_radius_R"], p["seat_radius_B"], p["seat_wall_W"]
    G, H, C = p["gem_diameter_G"], p["gem_height_H"], p["setting_clearance_C"]
    if min(R, B, W, G, H, C) <= 0:
        bad.append("All dimensions must be positive (solid geometry).")
        return bad
    if 2 * B >= math.sqrt(2) * R:
        bad.append("Adjacent spherical seats must remain separate (centre-distance geometry).")
    if not 0 < W < B:
        bad.append("A hollow spherical seat requires 0 < W < B (sphere geometry).")
    if not 0.36 * R - 1e-6 <= B <= 0.40 * R + 1e-6:
        bad.append("Seat size must preserve open braid spans (proportion: B/R 0.36–0.40).")
    if not 0.25 * B - 1e-6 <= W <= 0.28 * B + 1e-6:
        bad.append("Seat wall must retain the native hollow-seat form (proportion: W/B 0.25–0.28).")
    if not 1.25 * B - 1e-6 <= G <= 1.30 * B + 1e-6:
        bad.append("Gem girdle must fit within the seat rim (proportion: G/B 1.25–1.30).")
    if not 0.70 * G - 1e-6 <= H <= 0.73 * G + 1e-6:
        bad.append("Gem retains a shallow crown and deeper pavilion (proportion: H/G 0.70–0.73).")
    if C >= W / 10:
        bad.append("Setting clearance must remain small compared with the wall (proportion).")
    if G / 2 + C >= B - W:
        bad.append("Girdle radius plus clearance must fit the cavity equator (sphere geometry).")
    return bad
