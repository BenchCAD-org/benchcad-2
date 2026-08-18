"""Table-driven specification for the two-bolt STRAUB-GRIP-L family."""

import random


PIPE_RANGES = {
    0: (87.884, 89.916),
    1: (113.284, 115.316),
    2: (166.624, 169.926),
    3: (216.916, 221.234),
}


PARAM_SPEC = {
    "catalog_index": dict(
        desc="Discrete Dixon STRAUB-GRIP-L two-lock-bolt catalog row",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (1, 3)},
        choices={"easy": [0], "medium": [0, 1], "hard": [1, 2, 3]},
        integer=True,
        coverage=[0, 1, 2, 3],
        askable=True,
        source=("Dixon DPL424 p.965: STR20650, STR20900, STR21350, "
                "STR21400; two-lock-bolt construction confirmed by "
                "STRAUB ST00152_0820"),
    ),
    "fitted_pipe_od": dict(
        desc="Actual pipe O.D. within the selected catalog row's published coupling range",
        unit="mm",
        range={"easy": PIPE_RANGES[0], "medium": (PIPE_RANGES[0][0], PIPE_RANGES[1][1]),
               "hard": (PIPE_RANGES[1][0], PIPE_RANGES[3][1])},
        source="Dixon DPL424 p.965 published min/max pipe O.D. range for each selected row",
        askable=False,
    ),
}


def refine(p: dict, difficulty: str, rng: random.Random) -> None:
    """Bind the pipe-fit state to the one selected Dixon catalog row."""
    del difficulty
    low, high = PIPE_RANGES[int(p["catalog_index"])]
    p["fitted_pipe_od"] = rng.uniform(low, high)


def check(p: dict) -> list[str]:
    """Only the four complete, fixed two-bolt catalog constructions are valid."""
    index = int(p["catalog_index"])
    if index not in (0, 1, 2, 3):
        return ["catalog_index must be one of four sourced, two-lock-bolt catalog rows"]
    low, high = PIPE_RANGES[index]
    if not low <= p["fitted_pipe_od"] <= high:
        return ["fitted_pipe_od must stay in the selected Dixon row's published range"]
    return []
