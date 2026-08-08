"""quarter_turn_cam_latch — the benchmark generator spec.

A quarter-turn cam latch (Southco E5 class). PARAM_SPEC declares each build()
parameter; check() holds the engineering rules a reviewer audits. `grip` is
COUPLED to body_l and cam_t (what is left of the catalog depth after the cam
and its screw becomes the cam's Z-step), so it is filled in refine().
Spec: docs/DESIGN_SPEC.md

The geometry helpers the constraints need (`cam_offset`, `MIN_GRIP`,
`nut_af`) live in part.py and are imported here, so a rule can never drift
from the solid it is meant to constrain.

Sources:
- Southco E5 literature (e5.en.pdf): standard head Ø28x5, double-D cutout
  20.1 A/F / Ø22.5, depth behind the head 27.2 (long housings 45.5/58.2/68.2),
  cam 45 axis-to-tip / 23 of flat past the step / 19 wide / 4 thick, sealing
  washer 0.5 compressed, panel 1, cam screw M6, grip 4-42 in 2 mm steps; mini
  head Ø22x12.2, cutout 14.1 A/F / Ø16.3, cam 33, grip 4-26.
- Symbol -> parameter map and the scaled-off-the-sheet values: NOTES.md.
"""

import math

from bench2 import Resample
from part import MIN_GRIP, STEP_MAX_SLOPE, cam_offset, cam_step_run, nut_af


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
        desc="catalog depth behind the head underside — housing + cam + screw head",
        unit="mm",
        range={"easy": (27.0, 28.0), "medium": (27.0, 46.0), "hard": (27.0, 69.0)},
        choices={"easy": [27.2], "medium": [27.2, 45.5], "hard": [27.2, 45.5, 58.2, 68.2]},
        coverage=[27.2, 45.5, 58.2, 68.2],
        source="Southco E5 housing ladder: 27.2 standard, long 45.5/58.2/68.2 "
               "(the sheet dimensions 27.2 from the head underside to the back "
               "of the cam screw's head, not to the housing end)",
    ),
    "grip": dict(
        desc="grip: head underside (under the compressed sealing washer) to the "
             "cam's clamping face — the material thickness the latch clamps",
        unit="mm",
        range={"easy": (6.0, 18.0), "medium": (6.0, 36.0), "hard": (6.0, 58.0)},
        source="Southco E5 grip band in 2 mm steps (4-42 short housing, table "
               "to 82 long); the flat-cam subset modelled here starts where the "
               "cam clears the back of the mounting nut",
        refine=True,
    ),
    "cam_l": dict(
        desc="cam reach, axis to tip (the sheet's 45 is centreline to tip)",
        unit="mm",
        range={"easy": (40.0, 46.0), "medium": (30.0, 46.0), "hard": (28.0, 50.0)},
        source="Southco E5 cam 45 (standard) / 33 (mini)",
    ),
    "cam_w": dict(
        desc="cam blade width",
        unit="mm",
        range={"easy": (18.0, 20.0), "medium": (15.0, 21.0), "hard": (13.0, 22.0)},
        source="Southco E5 sheet: standard flat cam 19 wide",
    ),
    "cam_t": dict(
        desc="cam thickness (constant through hub, neck, step and tip)",
        unit="mm",
        range={"easy": (3.8, 4.2), "medium": (3.2, 4.6), "hard": (2.8, 5.2)},
        source="Southco E5 sheet: the cam is dimensioned 4 (.16) thick",
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

    # the cam clamps the material stack, and the mounting nut is inside that
    # stack — so the clamping face has to sit clear below the nut's back
    if p["grip"] < MIN_GRIP:
        bad.append(f"grip < {MIN_GRIP:.1f}: the clamping face would "
                   "land inside the mounting nut (deeper-offset cams reach "
                   "shallower grips and are not modelled)")

    # what is left of the catalog depth after the cam and its screw is the
    # cam's Z-step; it has to be a formed step, not a tower
    rise = cam_offset(p["body_l"], p["cam_t"], p["grip"])
    if rise < 0.8 * p["cam_t"]:
        bad.append("cam step shallower than 0.8*cam_t: the tip flat would run "
                   "into the hub plane (a plain flat cam, not the stepped one)")
    if rise > 4.5 * p["cam_t"]:
        bad.append("cam step deeper than 4.5*cam_t: past a formed cam's offset "
                   "leg — that grip is a different cam part (proportion)")

    # the cam tip must reach past the body to catch the frame — cam_l is the
    # FULL axis-to-tip reach (the sheet's 45), not an overall length
    if p["cam_l"] < p["body_d"] / 2.0 + 12.0:
        bad.append("cam_l < body_d/2+12: cam tip does not reach past the housing to catch the frame")

    # the step must stand outside the mounting nut's hex corners
    # (circumradius = A/F / sqrt(3)), so nothing can foul on the swing
    if p["cam_l"] - p["tip_flat"] < 0.5774 * nut_af(p["body_d"]) + 2.0:
        bad.append("cam_l - tip_flat too small: the step must clear the nut corners "
                   "(swing stays interference-free across the whole quarter turn)")

    # the step also has to climb clear of the housing barrel, and a formed
    # offset leg cannot stand up steeper than about 60 deg
    run = cam_step_run(p["cam_l"], p["tip_flat"], p["body_d"])
    if run <= 0.0:
        bad.append("no room between the housing barrel and the tip flat for the "
                   "cam's step: the blade would climb through the housing")
    elif rise > STEP_MAX_SLOPE * run:
        bad.append(f"cam step rises {rise:.1f} over {run:.1f} of run — steeper "
                   "than the ~60 deg a formed offset leg is drawn at (proportion)")

    # a flat cam, not a block
    if p["cam_t"] > 0.5 * p["cam_w"]:
        bad.append("cam_t > 0.5*cam_w: cam should be a flat arm")

    return bad


# ── 3. refine ────────────────────────────────────────────────────────────────
def refine(p: dict, difficulty: str, rng) -> None:
    """grip is coupled: what the catalog depth leaves over after the cam and
    its screw is the cam's Z-step, and that step has to stay a formed step."""
    lo, hi = PARAM_SPEC["grip"]["range"][difficulty]
    lo = max(lo, MIN_GRIP)
    # rise = cam_offset(body_l, cam_t, grip) must fall in [0.8, 4.5] * cam_t
    span = cam_offset(p["body_l"], p["cam_t"], 0.0)  # the rise at grip = 0
    lo = max(lo, span - 4.5 * p["cam_t"])
    hi = min(hi, span - 0.8 * p["cam_t"])
    # ...and the step has to climb clear of the housing barrel at <= 60 deg
    run = cam_step_run(p["cam_l"], p["tip_flat"], p["body_d"])
    if run <= 0.0:
        raise Resample
    lo = max(lo, span - STEP_MAX_SLOPE * run)
    # catalog grips run in 2 mm steps
    first, last = math.ceil(lo / 2.0) * 2, math.floor(hi / 2.0) * 2
    if last < first:
        raise Resample
    p["grip"] = float(first + 2 * int(rng.integers((last - first) // 2 + 1)))
