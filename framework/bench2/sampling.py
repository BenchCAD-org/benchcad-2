"""Generic instance sampler — the framework-owned generator loop.

A family's `spec.py` declares `PARAM_SPEC` (per-parameter, per-difficulty
ranges) and `check()`; the framework draws parameter sets from that declaration
so the contributor never hand-writes a rejection-sampling loop. Coupled
parameters (a bore bounded by a computed root circle, a hub sized off the bore)
are filled by an optional `spec.refine(p, difficulty, rng)` hook — plain Python
for just the coupling, not a loop.

Draw rule per PARAM_SPEC entry:
  - "refine": True                            -> not drawn here; refine() sets it
  - "choices": [...] or {difficulty: [...]}   -> pick one listed value
  - "integer": True                           -> randint in range (inclusive)
  - otherwise                                 -> uniform float in range, 2 dp
"""

from __future__ import annotations


class Resample(Exception):  # noqa: N818 — a control-flow signal, not an error
    """Raise inside refine() when a draw is infeasible for the sampled base
    params (e.g. no hub fits): the sampler discards it and draws again — the
    same escape the old hand-written loop expressed with `continue`."""


def _draw(entry: dict, difficulty: str, rng):
    if "choices" in entry:
        choices = entry["choices"]
        if isinstance(choices, dict):
            choices = choices[difficulty]
        return choices[int(rng.integers(len(choices)))]
    lo, hi = entry["range"][difficulty]
    if entry.get("integer"):
        return int(rng.integers(int(lo), int(hi) + 1))
    return round(float(rng.uniform(lo, hi)), 2)


def sample(spec, difficulty: str, rng, tries: int = 200) -> dict:
    """One valid parameter dict for `difficulty`, drawn from `spec` (a spec.py
    module). Uses ONLY `rng` for randomness, so the same seed reproduces the
    same parameters — which is what makes the derived program deterministic."""
    refine = getattr(spec, "refine", None)
    for _ in range(tries):
        try:
            p = {
                name: _draw(entry, difficulty, rng)
                for name, entry in spec.PARAM_SPEC.items()
                if not entry.get("refine")
            }
            if refine is not None:
                refine(p, difficulty, rng)
            if not spec.check(p):
                return p
        except Resample:
            continue
    raise RuntimeError(
        f"no valid sample for {difficulty!r} in {tries} tries — "
        "widen ranges, relax check(), or fix refine()"
    )
