"""hex_socket_flat_head_cap_screw - benchmark spec for a drawing-anchored screw."""

from bench2 import Resample


PARAM_SPEC = {
    "length": dict(
        desc="overall screw length from head top to tip",
        unit="mm",
        range={
            "easy": (28.0, 32.0),
            "medium": (24.0, 36.0),
            "hard": (20.0, 40.0),
        },
        source="baseline 30 mm from the user-provided reference drawing; benchmark perturbation around that anchor",
        askable=True,
    ),
    "shank_d": dict(
        desc="nominal shank diameter",
        unit="mm",
        range={
            "easy": (7.9, 8.1),
            "medium": (7.8, 8.2),
            "hard": (7.6, 8.4),
        },
        source="baseline 8 mm from the user-provided reference drawing; benchmark perturbation around that anchor",
        askable=True,
    ),
    "head_d": dict(
        desc="countersunk head diameter at the top face",
        unit="mm",
        range={
            "easy": (15.5, 16.1),
            "medium": (15.2, 16.4),
            "hard": (14.8, 16.8),
        },
        source="baseline 15.8 mm from the user-provided reference drawing; benchmark perturbation around that anchor",
        askable=True,
    ),
    "head_h": dict(
        desc="head height from top face to shank transition",
        unit="mm",
        range={
            "easy": (4.9, 5.2),
            "medium": (4.7, 5.4),
            "hard": (4.4, 5.7),
        },
        source="baseline 5.04 mm from the user-provided reference drawing; benchmark perturbation around that anchor",
        askable=True,
    ),
    "socket_af": dict(
        desc="hex socket across-flats size",
        unit="mm",
        range={
            "easy": (4.9, 5.1),
            "medium": (4.8, 5.2),
            "hard": (4.7, 5.3),
        },
        source="proportion; M8 countersunk socket drive kept near the common 5 mm hex-key size",
        askable=True,
    ),
    "socket_depth": dict(
        desc="depth of the hex socket recess",
        unit="mm",
        range={
            "easy": (3.0, 3.4),
            "medium": (2.8, 3.7),
            "hard": (2.6, 4.0),
        },
        source="proportion; recess depth chosen to remain visually plausible without claiming a manufacturer-specific socket depth",
        askable=True,
    ),
    "neck_d": dict(
        desc="diameter where the countersunk head blends into the shank",
        unit="mm",
        range={
            "easy": (8.8, 9.8),
            "medium": (8.6, 10.1),
            "hard": (8.4, 10.4),
        },
        source="proportion; transition diameter inferred from the reference silhouette",
        refine=True,
    ),
    "tip_chamfer": dict(
        desc="small end chamfer depth at the screw tip",
        unit="mm",
        range={
            "easy": (0.4, 0.8),
            "medium": (0.3, 1.0),
            "hard": (0.2, 1.2),
        },
        source="proportion; small end break for a machined/rolled screw tip",
    ),
}


def check(p: dict) -> list[str]:
    bad = []
    if p["length"] <= p["head_h"] + 4.0:
        bad.append("length <= head_h + 4.0: shank must remain visibly longer than the countersunk head")
    if p["head_d"] <= p["shank_d"] * 1.6:
        bad.append("head_d <= 1.6*shank_d: countersunk head must stay substantially wider than the shank")
    if p["neck_d"] <= p["shank_d"]:
        bad.append("neck_d <= shank_d: head-to-shank transition must stay wider than the shank")
    if p["neck_d"] >= p["head_d"]:
        bad.append("neck_d >= head_d: transition diameter must remain inside the head diameter")
    if p["socket_af"] >= p["head_d"] * 0.55:
        bad.append("socket_af >= 0.55*head_d: socket would consume too much of the countersunk head")
    if p["socket_depth"] >= p["head_h"] * 0.92:
        bad.append("socket_depth >= 0.92*head_h: socket recess cannot break through the underside of the head")
    if p["tip_chamfer"] >= p["shank_d"] * 0.45:
        bad.append("tip_chamfer >= 0.45*shank_d: tip break would remove too much of the shank radius")
    return bad


def refine(p: dict, difficulty: str, rng) -> None:
    lo, hi = PARAM_SPEC["neck_d"]["range"][difficulty]
    feasible_lo = max(lo, p["shank_d"] + 0.6, p["head_d"] * 0.53)
    feasible_hi = min(hi, p["head_d"] - 0.9, p["head_d"] * 0.68)
    if feasible_hi <= feasible_lo:
        raise Resample
    p["neck_d"] = round(float(rng.uniform(feasible_lo, feasible_hi)), 2)
