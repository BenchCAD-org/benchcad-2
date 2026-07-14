"""`bench2 new` — write a TODO-annotated skeleton: part.py + spec.py + family.json."""

from __future__ import annotations

import json
from pathlib import Path

_TEMPLATES = Path(__file__).parent / "templates"


def create(fam_dir: Path, family: str) -> None:
    fam_dir.mkdir(parents=True)
    for fn in ("part.py", "spec.py"):
        text = (_TEMPLATES / f"{fn}.tmpl").read_text().replace("__FAMILY__", family)
        (fam_dir / fn).write_text(text)
    meta = {
        "family": family,
        "standard": None,
        "base_plane": "XY",
        "description": "TODO: one sentence — what the part is and its main features",
        "source": "TODO: standard table / engineering rule / proportion convention",
        "contributor": "TODO: your-github-handle",
    }
    (fam_dir / "family.json").write_text(json.dumps(meta, indent=2) + "\n")
