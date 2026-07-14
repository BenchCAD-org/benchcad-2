"""Load a family's two source files as modules.

A family is `designs/<name>/` with:
  - part.py    the parametric part      -> `build(<named params>)`
  - spec.py    the benchmark generator  -> PARAM_SPEC, check, optional refine
  - family.json  metadata

Reusable reviewed geometry helpers live in `bench2.geomlib`, so
part.py never needs spec.py. When a part-specific helper is shared between
build() and a constraint (a hole layout used by both build and check), it lives
in part.py and spec.py reads it with `from part import <helper>` — spec depends
on the part, never the reverse. The loader makes that import resolve.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_family(fam_dir: Path):
    """Return (part, spec) modules for designs/<family>/.

    While spec.py executes, the part module is exposed as `part` so a
    constraint can `from part import <shared helper>`; the alias is removed
    afterwards so families don't leak into one another.
    """
    part = _load(fam_dir / "part.py", f"benchcad_part_{fam_dir.name}")
    saved = sys.modules.get("part")
    sys.modules["part"] = part
    try:
        spec = _load(fam_dir / "spec.py", f"benchcad_spec_{fam_dir.name}")
    finally:
        if saved is not None:
            sys.modules["part"] = saved
        else:
            sys.modules.pop("part", None)
    return part, spec
