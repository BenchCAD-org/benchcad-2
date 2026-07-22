"""guitar_tuning_machine_head — the benchmark generator spec.

A sealed geared guitar tuning machine (Grover Rotomatic / Gotoh SG381 style).
PARAM_SPEC declares each build() parameter; check() holds the engineering rules
a reviewer audits. Nothing is coupled, so there is no refine().
Spec: docs/DESIGN_SPEC.md

Sources:
- Grover Rotomatic 102 dimensioned drawing (WD Music): post Ø6, bushing Ø7.8-9.9,
  M8 bushing thread, housing ~27 x 24 mm, post height ~27 mm, mount screw Ø2.6.
- Gotoh SG381 drawing: post Ø6, hex bushing OD 14 mm, housing ~27 x 22 mm.
- Gear ratio (14:1-18:1) is internal and not a CAD dimension here.
"""


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "baseplate_l": dict(
        desc="baseplate length (along the string line)",
        unit="mm",
        range={"easy": (25.0, 30.0), "medium": (22.0, 38.0), "hard": (20.0, 45.0)},
        source="Grover/Gotoh housing footprint ~27 mm -> proportion",
        askable=True,
    ),
    "baseplate_w": dict(
        desc="baseplate width",
        unit="mm",
        range={"easy": (12.0, 15.0), "medium": (11.0, 16.0), "hard": (10.0, 18.0)},
        source="Grover baseplate ~13-15 mm -> proportion",
        askable=True,
    ),
    "plate_t": dict(
        desc="baseplate thickness",
        unit="mm",
        range={"easy": (1.2, 2.0), "medium": (1.0, 2.5), "hard": (1.0, 3.0)},
        source="proportion (die-cast baseplate)",
        askable=True,
    ),
    "housing_w": dict(
        desc="gear-housing width",
        unit="mm",
        range={"easy": (18.0, 24.0), "medium": (15.0, 26.0), "hard": (14.0, 28.0)},
        source="Grover/Gotoh sealed housing ~24-27 mm -> proportion",
        askable=True,
    ),
    "housing_h": dict(
        desc="gear-housing depth behind the baseplate",
        unit="mm",
        range={"easy": (12.0, 18.0), "medium": (10.0, 20.0), "hard": (10.0, 24.0)},
        source="proportion (sealed worm-gear housing depth)",
        askable=True,
    ),
    "post_d": dict(
        desc="string-post diameter",
        unit="mm",
        range={"easy": (5.8, 6.3), "medium": (5.5, 6.5), "hard": (5.5, 6.5)},
        source="Grover 6.0 / Grover Super 6.3 / Gotoh 6.0 mm",
        askable=True,
    ),
    "post_h": dict(
        desc="string-post height above the baseplate",
        unit="mm",
        range={"easy": (24.0, 28.0), "medium": (18.0, 30.0), "hard": (15.0, 32.0)},
        source="Grover post height ~27 mm -> proportion",
        askable=True,
    ),
    "bushing_od": dict(
        desc="press-in bushing collar outer diameter",
        unit="mm",
        range={"easy": (7.5, 10.0), "medium": (7.0, 14.0), "hard": (7.0, 15.0)},
        source="Grover Ø7.8 / Ø9.9 collar; Gotoh Ø14 hex bushing",
        askable=True,
    ),
    "worm_d": dict(
        desc="worm / key-shaft diameter",
        unit="mm",
        range={"easy": (5.0, 7.0), "medium": (4.0, 8.0), "hard": (4.0, 9.0)},
        source="proportion (worm-gear key shaft)",
        askable=True,
    ),
    "mount_d": dict(
        desc="locating-screw hole diameter",
        unit="mm",
        range={"easy": (2.4, 2.8), "medium": (2.0, 3.2), "hard": (2.0, 3.5)},
        source="Grover mounting screw Ø2.6 mm",
        askable=True,
    ),
    "worm_both_sides": dict(
        desc="key shaft exits both sides of the housing (1) vs one side (0)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        source="in-line (both-sides) vs single-side key-shaft variants",
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        feature=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    bad = []

    # bushing must surround the post with a wall, and fit on the baseplate
    if p["bushing_od"] < p["post_d"] + 1.5:
        bad.append("bushing_od < post_d+1.5: bushing collar must surround the post with wall")
    if p["bushing_od"] > p["baseplate_w"] - 1.0:
        bad.append("bushing_od > baseplate_w-1: bushing wider than the baseplate")

    # housing sits on the baseplate; worm fits inside the housing depth
    if p["housing_w"] > p["baseplate_l"]:
        bad.append("housing_w > baseplate_l: gear housing overhangs the baseplate")
    if p["worm_d"] > p["housing_h"] - 2.0:
        bad.append("worm_d > housing_h-2: key shaft does not fit the housing depth")

    # the locating-screw hole (near the +X end) must clear the bushing collar
    mount_x = p["baseplate_l"] / 2.0 - p["mount_d"] - 2.0
    if mount_x - p["mount_d"] / 2.0 < p["bushing_od"] / 2.0 + 2.0:
        bad.append("mount hole overlaps the bushing: baseplate too short for the collar + screw")

    return bad
