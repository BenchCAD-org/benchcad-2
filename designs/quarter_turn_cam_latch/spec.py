"""quarter_turn_cam_latch — the benchmark generator spec.

A quarter-turn cam latch (Southco E5 class). PARAM_SPEC declares each build()
parameter; check() holds the engineering rules a reviewer audits. grip is
COUPLED to body_l (the cam clamps within the housing), so it is filled in
refine(). Spec: docs/DESIGN_SPEC.md

Sources:
- Southco E5 literature (e5.en.pdf): standard head Ø28x5, double-D cutout
  20.1 A/F / Ø22.5, body behind panel 27.2 (long housings 45.5/58.2/68.2),
  cam 45 long / tip offset 23, cam screw M6, grip 4-42 in 2 mm steps; mini
  head Ø22x12.2, cutout 14.1 A/F / Ø16.3, cam 33, grip 4-26.
"""

from bench2 import Resample


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "head_d": dict(
        desc="head diameter above the panel",
        unit="mm",
        range={"easy": (26.0, 28.0), "medium": (22.0, 28.0), "hard": (20.0, 30.0)},
        source="Southco E5 head Ø28 (standard) / Ø22 (mini)",
    ),
    "head_h": dict(
        desc="head height above the panel",
        unit="mm",
        range={"easy": (5.0, 6.0), "medium": (4.5, 12.2), "hard": (4.0, 13.0)},
        source="Southco E5 head 5 (standard) to 12.2 (mini knob)",
    ),
    "body_d": dict(
        desc="body circle diameter (panel cutout circle)",
        unit="mm",
        range={"easy": (22.0, 22.5), "medium": (16.3, 22.5), "hard": (15.0, 23.5)},
        source="Southco E5 cutout circle Ø22.5 (standard) / Ø16.3 (mini)",
    ),
    "afl": dict(
        desc="double-D across-flats width (anti-rotation flats)",
        unit="mm",
        range={"easy": (19.5, 20.1), "medium": (14.1, 20.1), "hard": (13.0, 21.0)},
        source="Southco E5 cutout 20.1 A/F (standard) / 14.1 (mini)",
    ),
    "body_l": dict(
        desc="body/housing length behind the panel",
        unit="mm",
        range={"easy": (25.0, 30.0), "medium": (20.0, 46.0), "hard": (18.0, 69.0)},
        source="Southco E5 27.2 standard; long housings 45.5/58.2/68.2",
    ),
    "grip": dict(
        desc="grip: panel underside to the cam clamping face",
        unit="mm",
        range={"easy": (4.0, 24.0), "medium": (4.0, 40.0), "hard": (4.0, 60.0)},
        source="Southco E5 grip 4-42 (2 mm steps); long-housing table to 82",
        refine=True,
    ),
    "cam_l": dict(
        desc="cam reach, axis to tip (the sheet's 45 is centreline to tip)",
        unit="mm",
        range={"easy": (40.0, 46.0), "medium": (30.0, 46.0), "hard": (28.0, 50.0)},
        source="Southco E5 cam 45 (standard) / 33 (mini)",
    ),
    "cam_w": dict(
        desc="cam arm width",
        unit="mm",
        range={"easy": (11.0, 14.0), "medium": (9.0, 16.0), "hard": (8.0, 18.0)},
        source="proportion (flat cam arm)",
    ),
    "cam_t": dict(
        desc="cam arm thickness",
        unit="mm",
        range={"easy": (2.5, 3.5), "medium": (2.0, 4.5), "hard": (1.8, 5.0)},
        source="proportion (stamped/zinc cam)",
    ),
    "tip_flat": dict(
        desc="flat clamping length past the step",
        unit="mm",
        range={"easy": (21.0, 24.0), "medium": (18.0, 25.0), "hard": (16.0, 26.0)},
        source="Southco E5: 23 of flat past the step",
    ),
    "slotted": dict(
        desc="tool-operated slotted head (1) vs plain knob head (0)",
        unit="",
        range={"easy": (1, 1), "medium": (0, 1), "hard": (0, 1)},
        source="Southco E5 tool-operated (slot/DIN key) vs wing-knob variants",
        choices={"easy": [1], "medium": [0, 1], "hard": [0, 1]},
        feature=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    bad = []

    # the head must overhang the cutout circle to bear on the panel
    if p["head_d"] < p["body_d"] + 3.0:
        bad.append("head_d < body_d+3: head would fall through the panel cutout")

    # the flats must actually cut the circle (double-D, not a plain round)
    if not (0.85 * p["body_d"] <= p["afl"] <= 0.93 * p["body_d"]):
        bad.append("afl outside 0.85-0.93*body_d: double-D flats must pair with the circle as in the E5 cutouts (20.1/22.5, 14.1/16.3)")

    # the cam must clamp within the housing length
    if p["grip"] + p["cam_t"] > p["body_l"]:
        bad.append("grip + cam_t > body_l: flat cam clamps within the housing (offset/deep-offset cams not modelled)")

    # the cam tip must reach past the body to catch the frame — cam_l is the
    # FULL axis-to-tip reach (the sheet's 45), not an overall length
    if p["cam_l"] < p["body_d"] / 2.0 + 12.0:
        bad.append("cam_l < body_d/2+12: cam tip does not reach past the housing to catch the frame")

    # the Z-step must stand outside the mounting nut's hex corners, so the
    # quarter-turn swing can never touch the nut (circumradius = A/F/sqrt(3))
    if p["cam_l"] - p["tip_flat"] < 0.577 * (p["body_d"] + 2.0) + 2.0:
        bad.append("cam_l - tip_flat too small: the step must clear the nut corners "
                   "(swing stays interference-free across the whole quarter turn)")

    # a flat cam, not a block
    if p["cam_t"] > 0.5 * p["cam_w"]:
        bad.append("cam_t > 0.5*cam_w: cam should be a flat arm (stamped plate)")

    return bad


# ── 3. refine ────────────────────────────────────────────────────────────────
def refine(p: dict, difficulty: str, rng) -> None:
    """grip is coupled: the cam clamps within the housing (grip + cam_t <= body_l)."""
    lo, hi = PARAM_SPEC["grip"]["range"][difficulty]
    hi = min(hi, p["body_l"] - p["cam_t"])
    if hi <= lo:
        raise Resample
    # catalog grips run in 2 mm steps
    n_steps = int((hi - lo) // 2.0)
    p["grip"] = round(lo + 2.0 * int(rng.integers(n_steps + 1)), 2)
