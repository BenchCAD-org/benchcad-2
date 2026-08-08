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
from part import MIN_GRIP, STEP_MAX_SLOPE, cam_offset, cam_step_run


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "head_d": dict(
        desc="head diameter above the panel",
        unit="mm",
        range={"easy": (26.0, 28.0), "medium": (22.0, 28.0), "hard": (20.0, 30.0)},
        source="Southco E5 head Ø28 p.154 / Ø22 mini p.158",
    ),
    "head_h": dict(
        desc="head height above the panel",
        unit="mm",
        range={"easy": (5.0, 6.0), "medium": (4.5, 12.2), "hard": (4.0, 13.0)},
        source="Southco E5 head 5 p.154 to 12.2 mini p.158",
    ),
    "body_d": dict(
        desc="body circle diameter (panel cutout circle)",
        unit="mm",
        range={"easy": (22.0, 22.5), "medium": (16.3, 22.5), "hard": (15.0, 23.5)},
        source="Southco E5 cutout circle Ø22.5 p.154 / Ø16.3 mini p.158",
    ),
    "afl": dict(
        desc="double-D across-flats width (anti-rotation flats)",
        unit="mm",
        range={"easy": (19.5, 20.1), "medium": (14.1, 20.1), "hard": (13.0, 21.0)},
        source="Southco E5 cutout 20.1 A/F p.154 / 14.1 mini p.158",
    ),
    "body_l": dict(
        desc="catalog depth behind the head underside — housing + cam + screw head",
        unit="mm",
        range={"easy": (27.0, 28.0), "medium": (27.0, 46.0), "hard": (27.0, 69.0)},
        choices={"easy": [27.2], "medium": [27.2, 45.5], "hard": [27.2, 45.5, 58.2, 68.2]},
        coverage=[27.2, 45.5, 58.2, 68.2],
        source="Southco E5 depth ladder: 27.2 p.154, long 45.5/58.2/68.2 p.155 "
               "(p.154 dimensions 27.2 from the head underside to the back of "
               "the cam screw's head, not to the housing end)",
    ),
    "grip": dict(
        desc="grip: head underside (under the compressed sealing washer) to the "
             "cam's clamping face — the material thickness the latch clamps",
        unit="mm",
        range={"easy": (6.0, 18.0), "medium": (6.0, 36.0), "hard": (6.0, 58.0)},
        source="Southco E5 grip 4-42 in 2 mm steps p.170 (long-housing table to "
               "82 p.155); the flat-cam subset modelled here starts where the "
               "cam clears the back of the mounting nut",
        refine=True,
    ),
    "cam_l": dict(
        desc="cam reach, axis to tip (the sheet's 45 is centreline to tip)",
        unit="mm",
        range={"easy": (40.0, 46.0), "medium": (30.0, 46.0), "hard": (28.0, 50.0)},
        source="Southco E5 cam 45 p.154 / 33 mini p.158, centreline to tip",
    ),
    "cam_w": dict(
        desc="cam blade width",
        unit="mm",
        range={"easy": (18.0, 20.0), "medium": (15.0, 21.0), "hard": (13.0, 22.0)},
        source="Southco E5 p.154 top view: the blade is dimensioned 19 wide",
    ),
    "cam_t": dict(
        desc="cam thickness (constant through hub, neck, step and tip)",
        unit="mm",
        range={"easy": (3.8, 4.2), "medium": (3.2, 4.6), "hard": (2.8, 5.2)},
        source="Southco E5 p.154: the small 4 (.16) reads across the cam plate (housing end to cam back); issue #32's table missed it, so it is corroborated by the 27.2 stack closing at 18.2+4.15+5.0",
    ),
    "tip_flat": dict(
        desc="flat clamping length past the step",
        unit="mm",
        range={"easy": (21.0, 24.0), "medium": (18.0, 25.0), "hard": (16.0, 26.0)},
        source="Southco E5 cam tip offset 23 p.154 / 15 mini p.158",
    ),
    "slotted": dict(
        desc="tool-operated slotted head (1) vs blank head (0)",
        unit="",
        range={"easy": (1, 1), "medium": (0, 1), "hard": (0, 1)},
        source="Southco E5 p.154 head styles: 00 Slotted vs 23 Blank",
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
        bad.append("head_d < body_d+3: under 1.5 of radial bearing on the panel "
                   "around the cutout — the E5 head has 2.75 (proportion)")

    # the flats must actually cut the circle (double-D, not a plain round)
    if not (0.85 * p["body_d"] <= p["afl"] <= 0.93 * p["body_d"]):
        bad.append("afl outside 0.85-0.93*body_d: the band spanned by the two "
                   "real E5 cutouts (20.1/22.5 = 0.893, 14.1/16.3 = 0.865)")

    # the cam clamps the material stack and the mounting nut sits inside that
    # stack, so the clamping face has to stay a millimetre clear of the nut's
    # back (washer 0.5 + panel 1 + nut 4.2). Below ~5.7 it is a collision;
    # between that and MIN_GRIP it is only tight, and the catalog reaches those
    # grips with offset cams, which are not modelled either way.
    if p["grip"] < MIN_GRIP:
        bad.append(f"grip < {MIN_GRIP:.1f}: leaves under 1 mm between the "
                   "clamping face and the back of the mounting nut "
                   "(the catalog reaches these grips with offset cams)")

    # what is left of the catalog depth after the cam and its screw is the
    # cam's Z-step; it has to be a formed step, not a tower
    rise = cam_offset(p["body_l"], p["cam_t"], p["grip"])
    if rise < 0.8 * p["cam_t"]:
        bad.append("cam step shallower than 0.8*cam_t: at that point it is a "
                   "plain flat cam, not the stepped one drawn (proportion)")
    if rise > 4.5 * p["cam_t"]:
        bad.append("cam step deeper than 4.5*cam_t: past a formed cam's offset "
                   "leg — that grip is a different cam part (proportion)")

    # The next two never fire inside the ranges declared above — cam_l starts
    # at 28 against a body_d/2+12 of at most 23.75, and cam_t/cam_w tops out at
    # 0.40. They are kept as the statement of what would be wrong, so widening
    # a range later cannot quietly admit a stub cam or a block one.

    # the cam tip must reach past the body to catch the frame — cam_l is the
    # FULL axis-to-tip reach (the sheet's 45), not an overall length
    if p["cam_l"] < p["body_d"] / 2.0 + 12.0:
        bad.append("cam_l < body_d/2+12: cam tip does not reach past the housing to catch the frame")

    # the step also has to climb clear of the housing barrel, and a formed
    # offset leg cannot stand up steeper than about 60 deg
    run = cam_step_run(p["cam_l"], p["tip_flat"], p["body_d"])
    if run <= 0.0:
        bad.append("no room between the housing barrel and the tip flat for the "
                   "cam's step: the blade would climb through the housing")
    elif rise > STEP_MAX_SLOPE * run:
        bad.append(f"cam step rises {rise:.1f} over {run:.1f} of run — steeper "
                   "than the ~60 deg a formed offset leg is drawn at; the sheet "
                   "dimensions no bend angle, so this is a proportion")

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
