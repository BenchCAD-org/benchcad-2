"""Sampling contract for the speaker-pole mount socket family."""


DEPTHS = [58.0, 60.0, 65.0, 76.0, 95.0, 127.0]

PARAM_SPEC = {
    "bore_d": dict(
        desc="Nominal speaker-pole diameter accepted by the socket",
        unit="mm",
        range={"easy": (35.0, 35.0), "medium": (35.0, 35.0), "hard": (35.0, 38.1)},
        choices={"easy": [35.0], "medium": [35.0], "hard": [35.0, 38.1]},
        coverage=[35.0, 38.1],
        source="Penn Elcom M1551/M1552 manufacturer pages",
        askable=True,
    ),
    "cup_outer_d": dict(
        desc="Outside diameter of the drawn cup",
        unit="mm",
        range={"easy": (41.0, 41.0), "medium": (41.0, 43.0), "hard": (41.0, 46.1)},
        source="M1551 drawing: 41 mm; otherwise pole diameter + 2 mm clearance + twice sheet thickness",
        refine=True,
        askable=True,
    ),
    "flange_od": dict(
        desc="Outside diameter of the circular mounting flange",
        unit="mm",
        range={"easy": (118.0, 118.0), "medium": (110.0, 118.0), "hard": (110.0, 118.0)},
        choices={"easy": [118.0], "medium": [110.0, 118.0], "hard": [110.0, 118.0]},
        coverage=[110.0, 118.0],
        source="Penn Elcom M1551 and M1553 manufacturer drawings",
        askable=True,
    ),
    "flange_t": dict(
        desc="Drawn-steel wall and flange thickness",
        unit="mm",
        range={"easy": (2.0, 2.0), "medium": (2.0, 3.0), "hard": (2.0, 3.0)},
        choices={"easy": [2.0], "medium": [2.0, 3.0], "hard": [2.0, 3.0]},
        coverage=[2.0, 3.0],
        source="Penn Elcom M1551 (2 mm) and M1553-series (3 mm) drawings",
        askable=True,
    ),
    "depth": dict(
        desc="Cup depth from flange underside to closed bottom",
        unit="mm",
        range={"easy": (76.0, 76.0), "medium": (60.0, 95.0), "hard": (58.0, 127.0)},
        choices={"easy": [76.0], "medium": [60.0, 65.0, 76.0, 95.0], "hard": DEPTHS},
        coverage=DEPTHS,
        source="Adam Hall SM701 and Penn Elcom M1551/M1553/M1555 size tables",
        askable=True,
    ),
    "hole_d": dict(
        desc="Diameter of each of four flange screw-clearance holes",
        unit="mm",
        range={"easy": (6.6, 6.6), "medium": (6.6, 6.6), "hard": (6.6, 6.6)},
        choices=[6.6],
        source="Penn Elcom M1553-series drawing: four holes diameter 6.6 mm",
        askable=True,
    ),
    "hole_bcd": dict(
        desc="Bolt-circle diameter through the four screw-hole centres",
        unit="mm",
        range={"easy": (82.6, 82.6), "medium": (82.6, 82.6), "hard": (82.6, 82.6)},
        choices=[82.6],
        source="M1551 retailer dimension: 82.6 mm centre-to-centre across opposite holes",
        askable=True,
    ),
    "bottom_radius": dict(
        desc="External radius on the closed cup bottom edge",
        unit="mm",
        range={"easy": (3.0, 3.0), "medium": (2.5, 4.0), "hard": (2.0, 5.0)},
        source="proportion",
    ),
}


def refine(p: dict, difficulty: str, rng) -> None:
    # The M1551 stack is pole + 2 mm diametral clearance + two wall thicknesses.
    p["cup_outer_d"] = round(p["bore_d"] + 2.0 + 2.0 * p["flange_t"], 1)


def check(p: dict) -> list[str]:
    bad = []
    inner_d = p["cup_outer_d"] - 2.0 * p["flange_t"]
    if inner_d < p["bore_d"] + 2.0:
        bad.append("cup ID must provide at least 2 mm diametral pole clearance (M1551 stack-up)")
    if not p["cup_outer_d"] < 50.8:
        bad.append("cup outer diameter must fit the 50.8 mm M1551 cabinet cutout")
    if not p["cup_outer_d"] < p["hole_bcd"] < p["flange_od"]:
        bad.append("required sandwich ordering is cup OD < hole BCD < flange OD (M1551 dimensions)")
    if p["hole_d"] <= 6.0:
        bad.append("hole diameter must clear an M6 screw (M1553 drawing uses 6.6 mm)")
    if p["bottom_radius"] >= p["cup_outer_d"] / 4.0:
        bad.append("bottom radius must remain below cup radius/2 to preserve a straight cup wall (proportion)")
    if p["depth"] <= 2.0 * p["flange_t"]:
        bad.append("cup depth must exceed twice the sheet thickness to leave a useful blind bore (geometry)")
    return bad
