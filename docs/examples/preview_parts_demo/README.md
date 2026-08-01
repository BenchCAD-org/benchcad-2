# `bench2 preview-parts` — runnable example

A documentation demo (NOT a benchmark family — it lives outside `designs/` on
purpose): a pillow-block-style assembly exercising everything the
preview-parts naming contract covers —

- three semantic components declared in `family.json` (`block`, `bushing`,
  `bolt`) with `solids` = quantity sum,
- a repeated instance pair named `bolt_01` / `bolt_02`,
- a nested sub-assembly with its own `Location`, plus a translated AND rotated
  instance (`bolt_02` is turned 30 deg about Z — visible on its hex head).

Committed artifacts, rendered deterministically from hard / seed 0:

- [`preview_parts.png`](preview_parts.png) — default grouped layout: one
  four-view row per component (with its bounding box in mm), the complete
  assembly, then one red-on-gray highlight row per component
  (`bolt` highlights both instances together, `quantity=2`);
- [`preview_parts_per_instance.png`](preview_parts_per_instance.png) — the
  `--per-instance` variant: `bolt_01` and `bolt_02` each get their own row.

Regenerate (from the repo root; the CLI itself only serves `designs/`, so the
demo calls the library directly):

```bash
uv run python -c "from pathlib import Path; from bench2.preview_parts import build_preview_parts; build_preview_parts(Path('docs/examples/preview_parts_demo'))"
uv run python -c "from pathlib import Path; from bench2.preview_parts import build_preview_parts; build_preview_parts(Path('docs/examples/preview_parts_demo'), per_instance=True)"
mv docs/examples/preview_parts_demo/preview_parts.png docs/examples/preview_parts_demo/preview_parts_per_instance.png  # after the second command
```

(Run the grouped command last if you want both files fresh; each call writes
`preview_parts.png`.) A framework test keeps this example runnable
(`tests/test_preview_parts.py`).
