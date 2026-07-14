"""Registry for reusable, reviewed geometry helpers.

A helper may be added alongside a family when the same sourced geometry is
useful across multiple designs. Helpers must be self-contained, deterministic,
and safe to inline verbatim into a stand-alone generated program.
"""

from __future__ import annotations

import inspect


REGISTRY = {}


def inline_source(*names: str) -> str:
    """Return source for named helpers, preserving order and removing repeats."""
    seen, blocks = set(), []
    for name in names:
        if name in seen:
            continue
        if name not in REGISTRY:
            raise KeyError(
                f"geomlib has no helper named {name!r} (have: {sorted(REGISTRY)})"
            )
        seen.add(name)
        blocks.append(inspect.getsource(REGISTRY[name]).rstrip())
    return "\n\n\n".join(blocks)
