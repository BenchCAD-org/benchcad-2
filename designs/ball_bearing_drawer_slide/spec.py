"""ball_bearing_drawer_slide — the benchmark generator spec.

A full-extension ball-bearing drawer slide (three telescoping members). This is
a MULTI-BODY family: `part.build()` returns a `cq.Assembly` of three members and
`family.json` declares `"solids": 3`, so `bench2 validate` fails if a member
vanishes or merges. Nothing is coupled, so there is no refine().
Spec: docs/DESIGN_SPEC.md

Sources:
- Accuride 3832 full-extension side-mount slide: length 300-700 mm (12"-28"),
  section height 45.7 mm, installed width 12.7 mm, mounting holes Ø4.4-6.4 mm,
  ~128 mm (5.04") / 32 mm system hole pitch.
- Section height / width step up with load class across the wider catalog
  (Knape & Vogt 8400/8500, Hettich KA) -> upper ranges.
"""


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "slide_length": dict(
        desc="slide (member) length, closed",
        unit="mm",
        range={"easy": (300.0, 450.0), "medium": (300.0, 600.0), "hard": (300.0, 700.0)},
        source="Accuride 3832 lengths 300-700 mm (12-28 in, 50 mm steps)",
        askable=True,
    ),
    "member_height": dict(
        desc="section height (the tall dimension of each member)",
        unit="mm",
        range={"easy": (45.0, 50.0), "medium": (45.0, 66.0), "hard": (45.0, 76.0)},
        source="Accuride 3832 height 45.7 mm; steps up by load class (K&V/Hettich)",
        askable=True,
    ),
    "member_width": dict(
        desc="total installed width of the three stacked members",
        unit="mm",
        range={"easy": (12.5, 15.0), "medium": (12.5, 20.0), "hard": (12.5, 26.0)},
        source="Accuride 3832 installed width 12.7 mm; wider for heavier classes",
        askable=True,
    ),
    "gap": dict(
        desc="running clearance between members (where the ball retainer rides)",
        unit="mm",
        range={"easy": (0.8, 1.5), "medium": (0.6, 2.0), "hard": (0.5, 2.5)},
        source="proportion (ball-race running clearance)",
        askable=True,
    ),
    "hole_d": dict(
        desc="mounting hole / slot width",
        unit="mm",
        range={"easy": (4.0, 5.0), "medium": (4.0, 6.0), "hard": (4.0, 6.4)},
        source="Accuride 3832 mounting holes Ø4.4 / 4.6 / 5.1 / 6.4 mm",
        askable=True,
    ),
    "hole_pitch": dict(
        desc="longitudinal pitch of the mounting holes",
        unit="mm",
        range={"easy": (60.0, 100.0), "medium": (40.0, 128.0), "hard": (32.0, 160.0)},
        source="Accuride 128 mm (5.04 in) typical; 32 mm system holes",
        askable=True,
    ),
    "mount_slots": dict(
        desc="cabinet-member holes are vertical adjustment slots (1) vs round (0)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        source="Accuride offers slotted mounting holes for front-height adjustment",
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        feature=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    bad = []

    # each of the three members must be a real rail ≥ 2.5 mm thick
    rail_t = (p["member_width"] - 2.0 * p["gap"]) / 3.0
    if rail_t < 2.5:
        bad.append("member_width - 2*gap < 7.5: three members + two gaps leave a rail < 2.5 mm (not roll-formable)")

    # a slide is a tall, thin section — not a square bar
    if p["member_height"] < 1.5 * p["member_width"]:
        bad.append("member_height < 1.5*member_width: a slide section is tall and thin, not square")

    # mounting holes must not merge into a slot along the length
    if p["hole_pitch"] < p["hole_d"] + 4.0:
        bad.append("hole_pitch < hole_d+4: adjacent mounting holes would break through")

    # a vertical adjustment slot must fit inside the web height with margin
    if p["hole_d"] * 2.5 > p["member_height"] - 6.0:
        bad.append("hole_d*2.5 > member_height-6: the mounting slot does not fit the web height")

    return bad
