"""truss_half_coupler_hook — the benchmark generator spec.

A stage-rigging half coupler / hook clamp for the standard Ø48-51 mm barrel
(Doughty T-series class). PARAM_SPEC declares each build() parameter; check()
holds the engineering rules a reviewer audits. Nothing is coupled, so there is
no refine(). Spec: docs/DESIGN_SPEC.md

Sources:
- Doughty datasheets T57000/T57010 (standard, WLL 750 kg), T58080 (slimline,
  width 30), T58100 (lightweight, width 50), T57200 (hook clamp, M12x50 stud
  protruding 34): bore 48-51 mm, body width 30-50 mm, fixing M10/M12, eye
  Ø12.7 mm, tube-centre->base 40-55 mm, AW6082-T6 aluminium.
- Cross-manufacturer (Riggatec/Global Truss/Kupo): same 48-51 bore, widths
  30-51, bolts M10/M12 -> the bore is a design constant, not a free parameter.
"""


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "bore_d": dict(
        desc="barrel bore diameter (the standard scaffold/truss tube)",
        unit="mm",
        range={"easy": (48.0, 51.0), "medium": (48.0, 51.0), "hard": (48.0, 51.0)},
        source="Doughty/Riggatec/Global Truss/Kupo: universal Ø48-51 barrel",
        askable=True,
    ),
    "wall_t": dict(
        desc="ring wall thickness around the barrel",
        unit="mm",
        range={"easy": (5.0, 7.0), "medium": (4.0, 8.0), "hard": (4.0, 9.0)},
        source="proportion (cast AW6082-T6 clamp body)",
        askable=True,
    ),
    "body_w": dict(
        desc="body width along the tube axis",
        unit="mm",
        range={"easy": (45.0, 50.0), "medium": (30.0, 50.0), "hard": (28.0, 51.0)},
        source="Doughty width 50 (standard/lightweight) vs 30 (slimline); Riggatec 30-51",
        askable=True,
    ),
    "base_drop": dict(
        desc="tube centre to the tang base plane",
        unit="mm",
        range={"easy": (50.0, 55.0), "medium": (40.0, 58.0), "hard": (38.0, 62.0)},
        source="Doughty tube-centre->base 40-55 mm across the range",
        askable=True,
    ),
    "tang_t": dict(
        desc="hanging-tang plate thickness",
        unit="mm",
        range={"easy": (9.0, 12.0), "medium": (7.0, 14.0), "hard": (6.0, 16.0)},
        source="proportion (fixing tang under the ring)",
        askable=True,
    ),
    "hang_d": dict(
        desc="fixing eye / closing-bolt hole diameter (M10-M12 clearance)",
        unit="mm",
        range={"easy": (12.5, 13.0), "medium": (10.5, 13.0), "hard": (10.5, 13.5)},
        source="Doughty eye Ø12.7 (M12); M10 option on slimline/lightweight",
        askable=True,
    ),
    "lug_h": dict(
        desc="closure-lug block height over the ring crown",
        unit="mm",
        range={"easy": (14.0, 18.0), "medium": (12.0, 22.0), "hard": (10.0, 24.0)},
        source="proportion (closing-bolt boss)",
        askable=True,
    ),
    "stud": dict(
        desc="hook-clamp hanging stud protruding from the base (1) vs plain eye (0)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        source="Doughty T57200 M12x50 stud (protrudes 34) vs T57000 plain Ø12.7 eye",
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        feature=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    """Engineering constraints (empty = valid). Each cites its rule."""
    bad = []

    # the tang must reach below the ring far enough to carry the eye with edge material
    tang_h = p["base_drop"] - p["bore_d"] / 2.0
    if tang_h < 2.2 * p["hang_d"]:
        bad.append("base_drop - bore/2 < 2.2*hang_d: no room for the fixing eye plus edge material in the tang")

    # the eye/bolt hole must leave wall in the closure lug (lug block is 2.6*hang_d wide)
    if p["lug_h"] < p["hang_d"] + 3.0:
        bad.append("lug_h < hang_d+3: closing-bolt hole would break out of the lug block")

    # cast body, not sheet: ring wall carries the rated load (WLL up to 750 kg)
    if p["wall_t"] < p["bore_d"] / 13.0:
        bad.append("wall_t < bore/13: ring wall too thin for a rated clamp body (cast AW6082)")

    # tang thinner than the body is a plate, not a block
    if p["tang_t"] > 0.5 * p["body_w"]:
        bad.append("tang_t > 0.5*body_w: tang should be a plate under the ring, not a block")

    return bad
