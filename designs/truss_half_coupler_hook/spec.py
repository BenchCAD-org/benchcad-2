"""truss_half_coupler_hook — the benchmark generator spec.

A stage-rigging half coupler / hook clamp for the standard Ø48-51 mm barrel
(Doughty T-series class), modelled as a six-body assembly (shells, pins,
closing bolt, wing nut — see part.py). The base fixing (hang_d) and the swing
closing bolt (closing_bolt_d) are separate fasteners on this part and are
parameterised separately. PARAM_SPEC declares each build()
parameter; check() holds the engineering rules a reviewer audits. Nothing is
coupled, so there is no refine(). Spec: docs/DESIGN_SPEC.md

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
    ),
    "wall_t": dict(
        desc="ring wall thickness around the barrel",
        unit="mm",
        range={"easy": (5.0, 7.0), "medium": (4.0, 8.0), "hard": (4.0, 9.0)},
        source="proportion (extruded AW6082-T6 clamp body)",
    ),
    "body_w": dict(
        desc="body width along the tube axis",
        unit="mm",
        range={"easy": (49.0, 51.0), "medium": (29.0, 51.0), "hard": (29.0, 51.0)},
        choices={"easy": [50.0], "medium": [30.0, 50.0], "hard": [30.0, 50.0, 51.0]},
        coverage=[30.0, 50.0, 51.0],
        source="Doughty catalog widths: 30 slimline / 50 standard / 51 Riggatec",
    ),
    "base_drop": dict(
        desc="tube centre to the tang base plane",
        unit="mm",
        range={"easy": (50.0, 55.0), "medium": (40.0, 55.0), "hard": (40.0, 55.0)},
        source="Doughty tube-centre->base 40-55 mm across the range",
    ),
    "tang_t": dict(
        desc="hanging-tang width across the clamp",
        unit="mm",
        range={"easy": (18.0, 20.0), "medium": (16.0, 22.0), "hard": (14.0, 24.0)},
        source="Doughty T57000 drawing: tang 19 across under the 12.7 bore",
    ),
    "closing_bolt_d": dict(
        desc="swing closing-bolt nominal thread (the eyebolt the wing nut runs on)",
        unit="mm",
        range={"easy": (10.0, 10.0), "medium": (8.0, 10.0), "hard": (8.0, 10.0)},
        choices={"easy": [10.0], "medium": [8.0, 10.0], "hard": [8.0, 10.0]},
        coverage=[8.0, 10.0],
        # M12 is deliberately absent: a DIN 315-D M12 wing nut spans 63.5 and
        # measures 114 mm across the clamp, outside the catalog's 107 outline.
        # check() rejects it, so declaring it would be an unreachable value.
        source="Doughty T57000 drawing: the wing nut scales to a ~46 mm span, "
               "which is the DIN 315-D M10 row (e 48-51); the datasheet does not "
               "tabulate the eyebolt, so the range around it is proportion",
    ),
    "hang_d": dict(
        desc="fixing bore in the base tang (M10-M12 clearance, with the captive-nut slot)",
        unit="mm",
        range={"easy": (12.5, 13.0), "medium": (10.3, 13.0), "hard": (10.3, 13.0)},
        choices={"easy": [12.7], "medium": [10.5, 12.7], "hard": [10.5, 12.7]},
        coverage=[10.5, 12.7],
        source="Doughty catalog: Ø12.7 (M12) or the M10 option's ~10.5 clearance",
        # NOTE: this is the HANGING fixing at the base, not the closing bolt.
        # The datasheet lists them separately ("integral flat boss drilled
        # Ø12.7 with a hex slot for a captive M10/M12 nut" vs "closed by a
        # swing-away Grade 8.8 eyebolt and wing nut"); deriving one from the
        # other put a DIN 315-D M12 wing nut on the part, which does not fit
        # inside the catalog's 107 mm overall width.
    ),
    "lug_h": dict(
        desc="closure-lug block height over the ring crown",
        unit="mm",
        range={"easy": (14.0, 18.0), "medium": (12.0, 22.0), "hard": (10.0, 24.0)},
        source="proportion (closing-bolt boss)",
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
    if not p["stud"] and tang_h < 2.2 * p["hang_d"]:
        bad.append("base_drop - bore/2 < 2.2*hang_d: no room for the fixing eye plus edge material in the tang (eye variant)")

    # the slotted crown lug must be deep enough for the closing bolt to bear on
    if p["lug_h"] < p["hang_d"] + 3.0:
        bad.append("lug_h < hang_d+3: slot fork too shallow for the closing bolt to bear (lug is the clamping face)")

    # cast body, not sheet: ring wall carries the rated load (WLL up to 750 kg)
    if p["wall_t"] < p["bore_d"] / 11.0:
        bad.append("wall_t < bore/11: ring wall too thin for a rated clamp body (extruded AW6082, WLL to 750 kg)")

    # tang thinner than the body is a plate, not a block
    if p["tang_t"] > 0.5 * p["body_w"]:
        bad.append("tang_t > 0.5*body_w: tang should be a plate under the ring, not a block")

    # Overall width against the catalog outline (T57000: 107 mm). The clamp is
    # widest at the hinge knuckle on one side and the wing-nut ear on the other,
    # both referred to the pivot standoff x_h — so the envelope is closed-form
    # and worth asserting. Nothing constrained it before, which is how a wing
    # nut ~20 mm past the silhouette went unnoticed.
    pin_d = max(5.0, 0.5 * p["hang_d"])
    k_r = max(4.5, 0.8 * pin_d)
    r_eye = pin_d / 2.0 + 2.4
    x_h = p["bore_d"] / 2.0 + p["wall_t"] + max(0.85 * k_r, r_eye + 1.5)
    wing_span_e = {8.0: 37.5, 10.0: 49.5, 12.0: 63.5}.get(
        p["closing_bolt_d"], 5.0 * p["closing_bolt_d"])
    overall_w = 2.0 * x_h + k_r + wing_span_e / 2.0     # mirrors part.py's x_h
    if not 92.0 <= overall_w <= 112.0:
        bad.append(f"overall width {overall_w:.1f} outside the catalog clamp "
                   "outline (Doughty T-series 107 for the 50 mm bodies): the "
                   "hinge knuckle and the wing-nut ear set the silhouette")

    af = 19.0 if (p["hang_d"] - 0.7) >= 11.0 else 17.0
    if p["body_w"] < af + 8.0:
        bad.append("tang too narrow for the captive-nut slot: body_w must exceed "
                   "slot A/F + 8 (parallel walls hold the hex nut - wider and it spins)")
    return bad
