"""tilting_speaker_wall_bracket — the benchmark generator spec.

A tilt-adjustable loudspeaker wall mount (B-Tech BT-series style). PARAM_SPEC
declares each build() parameter; check() holds the engineering rules a reviewer
audits. Nothing is coupled, so there is no refine(). Spec: docs/DESIGN_SPEC.md

Sources:
- B-Tech BT77 (Ultragrip Pro) spec sheet: wall-plate holes Ø6.5/8.5 mm at
  76/127/145 mm vertical spacing; arm reach 135-280 mm; tilt +-10 deg.
- BT1/BT15/BT332 line: reach 72-290 mm; tilt +-10 to +-20 deg; loads 5-25 kg.
- Plate/arm proportions from the BT drawings -> proportion.
"""


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "wall_w": dict(
        desc="wall-plate width",
        unit="mm",
        range={"easy": (60.0, 75.0), "medium": (50.0, 90.0), "hard": (48.0, 100.0)},
        source="B-Tech BT77 wall plate ~68 mm wide -> proportion",
        askable=True,
    ),
    "wall_h": dict(
        desc="wall-plate height",
        unit="mm",
        range={"easy": (127.0, 150.0), "medium": (100.0, 180.0), "hard": (76.0, 200.0)},
        source="B-Tech BT77 wall-plate hole spacing 76/127/145 mm",
        askable=True,
    ),
    "plate_t": dict(
        desc="plate (wall + speaker) thickness",
        unit="mm",
        range={"easy": (3.0, 5.0), "medium": (3.0, 6.0), "hard": (2.5, 7.0)},
        source="proportion (formed steel bracket plate)",
        askable=True,
    ),
    "arm_len": dict(
        desc="arm reach (standoff from the wall)",
        unit="mm",
        range={"easy": (72.0, 135.0), "medium": (72.0, 200.0), "hard": (72.0, 290.0)},
        source="B-Tech BT-series reach 72-290 mm",
        askable=True,
    ),
    "arm_w": dict(
        desc="arm square cross-section size",
        unit="mm",
        range={"easy": (20.0, 30.0), "medium": (18.0, 40.0), "hard": (15.0, 45.0)},
        source="proportion (standoff arm)",
        askable=True,
    ),
    "tilt_angle": dict(
        desc="speaker-plate tilt from vertical",
        unit="deg",
        range={"easy": (0.0, 10.0), "medium": (0.0, 15.0), "hard": (0.0, 20.0)},
        source="B-Tech tilt +-10 (BT77) to +-20 (BT332)",
        askable=True,
    ),
    "spk_w": dict(
        desc="speaker-side plate width",
        unit="mm",
        range={"easy": (80.0, 110.0), "medium": (60.0, 140.0), "hard": (50.0, 160.0)},
        source="proportion (speaker-side clamp plate)",
        askable=True,
    ),
    "spk_h": dict(
        desc="speaker-side plate height",
        unit="mm",
        range={"easy": (90.0, 130.0), "medium": (70.0, 160.0), "hard": (60.0, 180.0)},
        source="proportion (speaker-side clamp plate)",
        askable=True,
    ),
    "bolt_d": dict(
        desc="wall-bolt / speaker-fixing hole diameter",
        unit="mm",
        range={"easy": (6.0, 7.0), "medium": (6.0, 8.5), "hard": (6.0, 8.5)},
        source="B-Tech BT77 wall holes Ø6.5 / 8.5 mm",
        askable=True,
    ),
    "gusset": dict(
        desc="triangular gusset reinforcing the arm/wall joint (1) vs none (0)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        source="heavier BT models add an arm gusset",
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        feature=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    bad = []

    # the arm must sit on the wall plate, not overhang it
    if p["arm_w"] > 0.7 * p["wall_w"]:
        bad.append("arm_w > 0.7*wall_w: arm wider than the wall plate can carry")

    # the speaker plate must be larger than the arm/pivot it mounts on
    if p["spk_w"] < p["arm_w"] + 10.0 or p["spk_h"] < p["arm_w"] + 10.0:
        bad.append("speaker plate smaller than arm+10: plate must cover the pivot knuckle")

    # a slide/plate is a tall standoff, not a stub: reach exceeds the arm section
    if p["arm_len"] < 1.5 * p["arm_w"]:
        bad.append("arm_len < 1.5*arm_w: the arm is a standoff, not a stub")

    # bolt holes must fit the plates with edge material
    if p["bolt_d"] > 0.3 * min(p["wall_w"], p["spk_h"]):
        bad.append("bolt_d > 0.3*min(wall_w,spk_h): holes leave too little plate material")

    return bad
