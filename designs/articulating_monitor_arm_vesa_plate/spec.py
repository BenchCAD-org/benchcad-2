"""articulating_monitor_arm_vesa_plate - the benchmark generator spec.

The part is a VESA display adapter plate (FDMI MIS-D/E/F). PARAM_SPEC declares
every build() parameter; check() holds the engineering rules a reviewer audits.
pattern_y is COUPLED to pattern_x (only the standardized VESA square/rectangular
pairs are legal), so it is filled in refine(). Spec: docs/DESIGN_SPEC.md

Sources:
- VESA FDMI (Flat Display Mounting Interface) MIS-D 75/100, MIS-E 100x200,
  MIS-F 200-stepped; clearance holes M4/M6/M8 -> ~5/7/9 mm, +-0.25 mm.
  https://en.wikipedia.org/wiki/Flat_Display_Mounting_Interface
- Plate thickness, boss, bore, edge margin: manufacturer plates vary within the
  standard hole pattern (Ergotron, VIVO, Ergomart) -> "proportion".
"""

from bench2 import Resample

# Legal VESA partners for each X spacing (Y >= X), from the FDMI pattern table.
_VESA_PARTNERS = {75.0: [75.0], 100.0: [100.0, 200.0], 200.0: [200.0, 400.0], 400.0: [400.0]}


# -- 1. PARAM_SPEC ------------------------------------------------------------
PARAM_SPEC = {
    "pattern_x": dict(
        desc="VESA horizontal hole spacing (FDMI pattern X)",
        unit="mm",
        range={"easy": (75.0, 100.0), "medium": (75.0, 200.0), "hard": (75.0, 400.0)},
        source="VESA FDMI MIS-D/E/F standard pattern sizes",
        choices={"easy": [100.0], "medium": [75.0, 100.0, 200.0], "hard": [75.0, 100.0, 200.0, 400.0]},
        coverage=[75.0, 100.0, 200.0, 400.0],
        askable=True,
    ),
    "pattern_y": dict(
        desc="VESA vertical hole spacing (FDMI pattern Y); a legal partner of X",
        unit="mm",
        range={"easy": (75.0, 400.0), "medium": (75.0, 400.0), "hard": (75.0, 400.0)},
        source="VESA FDMI standard pattern sizes (Y>=X legal pairs)",
        refine=True,
        coverage=[75.0, 100.0, 200.0, 400.0],
        askable=True,
    ),
    "hole_d": dict(
        desc="VESA fixing hole / slot width (clearance for M4/M6/M8)",
        unit="mm",
        range={"easy": (5.0, 9.0), "medium": (5.0, 9.0), "hard": (5.0, 9.0)},
        source="VESA clearance holes M4~5, M6~7, M8~9 mm (+-0.25)",
        choices={"easy": [5.0], "medium": [5.0, 7.0], "hard": [5.0, 7.0, 9.0]},
        coverage=[5.0, 7.0, 9.0],
        askable=True,
    ),
    "plate_t": dict(
        desc="adapter plate thickness",
        unit="mm",
        range={"easy": (2.5, 4.0), "medium": (2.0, 5.0), "hard": (2.0, 6.0)},
        source="steel adapter plates 2-6 mm (manufacturer range) -> proportion",
        askable=True,
    ),
    "margin": dict(
        desc="plate border: material beyond the hole pattern on each side",
        unit="mm",
        range={"easy": (16.0, 24.0), "medium": (12.0, 32.0), "hard": (12.0, 42.0)},
        source="proportion (outer plate = pattern + 2*margin)",
        askable=True,
    ),
    "boss_d": dict(
        desc="central arm-interface boss diameter",
        unit="mm",
        range={"easy": (36.0, 50.0), "medium": (32.0, 60.0), "hard": (30.0, 72.0)},
        source="proportion (monitor-arm mounting boss)",
        askable=True,
    ),
    "boss_h": dict(
        desc="boss height above the plate face",
        unit="mm",
        range={"easy": (5.0, 10.0), "medium": (4.0, 12.0), "hard": (4.0, 16.0)},
        source="proportion (arm quick-release engagement depth)",
        askable=True,
    ),
    "bore_d": dict(
        desc="central bore through the boss for the arm fixing",
        unit="mm",
        range={"easy": (6.0, 12.0), "medium": (6.0, 16.0), "hard": (6.0, 22.0)},
        source="proportion (arm post / fixing screw clearance)",
        askable=True,
    ),
    "slotted": dict(
        desc="VESA holes are outward adjustment slots (1) vs round holes (0)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        source="manufacturer adjustment slots for off-standard displays",
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        feature=True,
    ),
    "slot_len": dict(
        desc="outward travel of each adjustment slot (used when slotted=1)",
        unit="mm",
        range={"easy": (5.0, 10.0), "medium": (5.0, 18.0), "hard": (5.0, 28.0)},
        source="proportion (VESA fine-adjust travel)",
        askable=True,
    ),
}


# -- 2. check -----------------------------------------------------------------
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    import math

    bad = []
    px, py, hd = p["pattern_x"], p["pattern_y"], p["hole_d"]

    # VESA pair must be a legal FDMI combination (Y a listed partner of X)
    if py not in _VESA_PARTNERS.get(px, []):
        bad.append(f"pattern {px}x{py} is not a VESA FDMI pair: legal Y for X={px} are {_VESA_PARTNERS.get(px, [])}")

    # MIS-F (>=200 mm span) uses M6/M8, not M4 - larger displays need shear area
    if min(px, py) >= 200.0 and hd < 7.0:
        bad.append("MIS-F pattern (>=200 mm) requires M6/M8 (hole_d>=7): M4 lacks shear area (VESA FDMI)")

    # central boss must clear the nearest VESA hole (screw head / washer room)
    corner = math.hypot(px / 2.0, py / 2.0)
    if p["boss_d"] / 2.0 + 3.0 > corner - hd / 2.0:
        bad.append("boss overlaps a VESA hole: boss_d/2 + 3 must clear the hole edge (fastener access)")

    # arm bore must leave a boss wall
    if p["bore_d"] > p["boss_d"] - 4.0:
        bad.append("bore_d > boss_d-4: boss wall < 2 mm around the arm bore (would tear out)")

    # hole (or slot end) needs edge material to the plate border - tear-out
    reach = hd / 2.0 + (p["slot_len"] if p["slotted"] else 0.0)
    if p["margin"] < reach + 3.0:
        bad.append("margin too small: <3 mm of material past the hole/slot to the plate edge (tear-out)")

    # boss must protrude to actually engage the arm
    if p["boss_h"] < p["plate_t"]:
        bad.append("boss_h < plate_t: boss does not stand proud of the plate (no arm engagement)")

    return bad


# -- 3. refine ----------------------------------------------------------------
def refine(p: dict, difficulty: str, rng) -> None:
    """pattern_y is coupled to pattern_x: pick a legal VESA partner (Y >= X)."""
    partners = _VESA_PARTNERS.get(p["pattern_x"])
    if not partners:
        raise Resample
    p["pattern_y"] = float(partners[int(rng.integers(len(partners)))])
