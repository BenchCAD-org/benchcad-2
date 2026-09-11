"""Sampling contract for the STAUFF ACT field-tray clamp."""


PARAM_SPEC = {
    "size_index": {
        "desc": "Index of a complete ACT body row; hardware is joined by group",
        "unit": "",
        "range": {"easy": (0, 11), "medium": (0, 19), "hard": (0, 23)},
        "choices": {
            "easy": list(range(0, 12)),
            "medium": list(range(0, 20)),
            # Same 24 rows, ordered so the validator's deterministic
            # 40-seed coverage pass reaches every hard-only group-5 row.
            "hard": [0, 22] + list(range(2, 22)) + [1, 23],
        },
        "coverage": list(range(0, 24)),
        "integer": True,
        "source": "STAUFF Catalogue 1 (06/2026), pp. 83-84, 90 and 93; Issue #90 body and same-group W55 hardware tables",
    },
    "strip_d": {
        "desc": "Simplified circular section diameter of each integrated ACE contact strip",
        "unit": "mm",
        "range": {"easy": (1.4, 1.8), "medium": (1.2, 2.0), "hard": (1.0, 2.2)},
        "source": "proportion; ACE strip section is not dimensioned in the cited catalogue",
    },
    "strip_embed": {
        "desc": "Radial embed of each ACE strip into its clamp-half body",
        "unit": "mm",
        "range": {"easy": (0.45, 0.65), "medium": (0.35, 0.75), "hard": (0.30, 0.85)},
        "source": "proportion; positive overlap integrates strips with each clamp half",
    },
}


def check(p):
    bad = []
    if int(p["size_index"]) != p["size_index"] or not 0 <= int(p["size_index"]) <= 23:
        bad.append("size_index must select one of 24 published ACT rows (STAUFF Catalogue 1, pp. 83-84)")
    if p["strip_embed"] <= 0.0 or p["strip_embed"] >= p["strip_d"]:
        bad.append("strip_embed must be positive and less than strip_d for visible fused ACE geometry (proportion)")
    return bad
