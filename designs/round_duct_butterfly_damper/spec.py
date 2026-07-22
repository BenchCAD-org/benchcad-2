"""round_duct_butterfly_damper — the benchmark generator spec.

A round manual balancing / butterfly volume damper. PARAM_SPEC declares each
build() parameter; check() holds the engineering rules a reviewer audits. No
parameters are coupled, so there is no refine(). Spec: docs/DESIGN_SPEC.md

Sources:
- Ruskin MDRS25 (light manual quadrant damper): 20 ga frame + blade (~0.9 mm),
  3/8" (10 mm) square axle, 6" (152 mm) frame, Ø 4"-20" (102-508 mm).
- Ruskin CDR94 (heavy round control damper): frame depth 152/229/305 mm, blade
  1/4"-3/8" (6-10 mm), round axle 3/4"-3" (19-76 mm), Ø 102-1829 mm.
  Frame depth / blade / shaft step UP with diameter across the size range.
"""


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "duct_d": dict(
        desc="nominal round-duct / spool outer diameter",
        unit="mm",
        range={"easy": (120.0, 350.0), "medium": (110.0, 650.0), "hard": (110.0, 1000.0)},
        source="Ruskin MDRS25/CDR94 round damper sizes (102-1829 mm range)",
        askable=True,
    ),
    "wall": dict(
        desc="rolled sheet-metal frame wall thickness",
        unit="mm",
        range={"easy": (0.9, 1.6), "medium": (0.9, 2.2), "hard": (0.9, 3.0)},
        source="sheet-metal gauge (20 ga ~0.9 mm up); SMACNA round-duct gauge",
        askable=True,
    ),
    "frame_depth": dict(
        desc="axial length of the frame spool",
        unit="mm",
        range={"easy": (150.0, 175.0), "medium": (150.0, 240.0), "hard": (150.0, 320.0)},
        source="Ruskin CDR94 frame depth 152 / 229 / 305 mm (steps with diameter)",
        askable=True,
    ),
    "blade_t": dict(
        desc="butterfly blade (disc) thickness",
        unit="mm",
        range={"easy": (1.5, 3.0), "medium": (1.5, 6.0), "hard": (1.5, 10.0)},
        source="MDRS25 20 ga blade -> CDR94 1/4-3/8 in (1.5-10 mm)",
        askable=True,
    ),
    "shaft_d": dict(
        desc="control shaft / axle diameter (round rod, or square-bar side)",
        unit="mm",
        range={"easy": (12.0, 22.0), "medium": (10.0, 45.0), "hard": (10.0, 76.0)},
        source="MDRS25 10 mm square axle; CDR94 round axle 19-76 mm",
        askable=True,
    ),
    "handle_ext": dict(
        desc="shaft extension beyond the frame on the hand-quadrant side",
        unit="mm",
        range={"easy": (45.0, 65.0), "medium": (40.0, 90.0), "hard": (40.0, 120.0)},
        source="MDRS25 hand-quadrant standoff (~2-2.75 in) -> proportion",
        askable=True,
    ),
    "stub": dict(
        desc="shaft stub beyond the frame on the bearing side",
        unit="mm",
        range={"easy": (6.0, 14.0), "medium": (5.0, 22.0), "hard": (5.0, 32.0)},
        source="proportion (bearing-side journal length)",
        askable=True,
    ),
    "square_shaft": dict(
        desc="axle is a square bar (1, MDRS25) vs a round rod (0, CDR94)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        source="MDRS25 square axle vs CDR94 round axle (documented variants)",
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        feature=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    bad = []
    d = p["duct_d"]

    # frame is rolled sheet, not a thick pipe
    if p["wall"] > d / 40.0:
        bad.append("wall > D/40: frame is rolled sheet metal, not thick pipe (SMACNA gauge)")

    # axle must not choke the bore — CDR94 shaft/diameter ratio stays small
    if p["shaft_d"] > 0.20 * d:
        bad.append("shaft_d > 0.20*D: axle too thick for the bore (CDR94 axle/diameter ratio)")

    # blade must seat within the axial depth of the spool
    if p["blade_t"] >= p["frame_depth"]:
        bad.append("blade_t >= frame_depth: blade must seat inside the spool depth")

    # the bore must stay open around the axle
    if p["shaft_d"] >= d - 2.0 * p["wall"]:
        bad.append("shaft_d >= bore: axle would span the whole bore, no blade area")

    # hand-quadrant side extends past the bearing stub (quadrant standoff)
    if p["handle_ext"] <= p["stub"]:
        bad.append("handle_ext <= stub: hand-quadrant side must stand off past the bearing stub")

    return bad
