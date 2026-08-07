# Contributing

BenchCAD 2.0 is built from **explicit parametric part families**. Every
merged family contributes readable engineering knowledge: geometry, sourced
parameter ranges, constraints, reference evidence, and provenance.

Questions → [Discord](https://discord.gg/be9AtvrDyK). New to GitHub? Use the
step-by-step guides: [English](docs/GETTING_STARTED.md) ·
[Chinese](docs/GETTING_STARTED.zh.md).

## The contributor loop

```bash
uv sync
uv run bench2 new <family>
# fill designs/<family>/{part.py,spec.py,family.json}
uv run bench2 validate <family>
uv run bench2 preview <family>     # inspect every generated view yourself
# assembly family: preview also renders preview_parts.png
# (or run it alone: uv run bench2 preview-parts <family>)
# submit one PR with `Closes #<family-issue>`
```

## Ten rules

1. **One family = one issue = one PR.** A family PR touches only
   `designs/<family>/` and includes `Closes #N`.
2. **`bench2 validate` must pass locally.** CI reruns the same gates.
3. **A non-author reviews the family** using [`REVIEWING.md`](docs/REVIEWING.md).
4. **Merged is not automatically released.** Qualification and versioned
   manifests are produced in batches.
5. **Do not duplicate a known proposal.** Check [`registry.json`](registry.json)
   and create a Family request before implementing an unlisted family.
6. **No code is fine.** A Part proposal can provide a datasheet, table, and
   constraints; a maintainer may implement it with shared credit.
7. **Decisions live in issues and PRs.** Chat is for questions, not the record.
8. **Rule changes are PRs** to this document.
9. **Credit follows provenance:** proposer, implementer, and approving verifier.
10. **Sources must be reviewable.** Ranges, formulas, and constraints must
    trace to linked evidence or an honest `"proportion"` declaration.

## Family lifecycle

| # | Stage | What happens |
|---|---|---|
| 0 | Propose | Create a Family request with a real source, dimensioned drawing, and min/max table rows |
| 1 | Claim | Self-assign and verify the evidence before coding |
| 2 | Build | Implement the three family files; add `NOTES.md` for equation-heavy designs |
| 3 | Validate | Run `bench2 validate` and inspect `bench2 preview` output |
| 4 | PR | Submit one scoped PR with `Closes #N` — **after** `bench2 validate` passes locally and you inspected the previews. Want early feedback before that? Open the PR as a GitHub **Draft** |
| 5 | CI | CI reruns validation and posts the report and previews. **Your first PR here:** a maintainer must click *Approve workflows* once before CI runs — no checks yet just means that click is pending |
| 6 | Review | A non-author audits the evidence, renders, equations, constraints, and labels |
| 7 | Merge | The issue closes and provenance/status automation runs |
| 8 | Release | Qualified families enter the next versioned manifest |

## Evidence check before coding

The implementer is the first verifier. Confirm:

1. A real standard, catalog, datasheet, handbook, or honest proportion basis.
2. A true 2D orthographic dimensioned drawing that maps symbols to geometry —
   ideally the standard's parametric letter drawing paired with its size table
   (dimension arrows drawn over a product photo/render do not qualify).
3. A table or documented range containing minimum and maximum examples,
   its columns named physical-quantity + drawing symbol (`height_G`,
   `bore_E`, `pitch_P`) — a bare letter is ambiguous once it leaves the
   drawing, and carries into the `PARAM_SPEC` names.
4. At least two source values spot-checked manually.
5. At least four meaningful parameters and enough geometric variation.
6. No duplicate or near-duplicate in `registry.json` or active issues.

Missing evidence should be supplied or labeled `needs-evidence`; do not guess a
standard number or weaken an engineering constraint.

Reference assets may be stored under `docs/assets/refs/<family>_*` when
licensing permits, with the original source linked in the issue.

## What reviewers and CI enforce

- `build()` parameters exactly match `PARAM_SPEC`.
- Every range has a unit, description, difficulty bounds, and honest source.
- `check()` constraints are physically motivated and cited.
- Sampling stays inside the declared contract and remains deterministic.
- Derived programs execute to valid, non-degenerate solids.
- Difficulty levels and feature coverage are meaningful.
- Preview views and extremes match the reference evidence.
- `family.json` labels and contributor information are accurate.
- An assembly family names every component instance stably, matches its
  declared `components`/`solids`, and ships an inspected `preview_parts.png`
  (component four-views, assembly overview, ordered highlight rows — see
  `docs/DESIGN_SPEC.md`).

**Hard gates (red ✗ = cannot merge)** — so review spends its time on *truth*, not
structure. A family PR must pass all three:

| Gate | Enforces |
|---|---|
| `validate.yml` | `bench2 validate` — samples, constraints, execution, determinism, coverage, and that **every body is non-degenerate** (multi-body: matches `family.json` `"solids"`) |
| `require-issue-link.yml` | the PR body links its family issue (`Closes #N`, still open); **and every image url in the body resolves**, with anything under `designs/` pinned to a **commit sha** — a branch name is not a pin: your fork branch is deleted when this PR merges and every preview pinned to it dies with it, leaving the merged family unreviewable. Copy the sha off the branch and use `blob/<sha>/<path>?raw=true`. Both `![alt](…)` and `<img src="…">` are checked, so the width-setting form is covered too |
| `family-pr-checks.yml` | **one family per PR** (only `designs/<family>/`, plus a `geomlib` helper if you add one) — the sole exception is a **metadata-only sweep**, a diff whose `designs/` side is `spec.py` files only, which may span families because it can move no geometry and no committed render; the family ships all six files: `part.py`, `spec.py`, `family.json`, `preview.png`, `preview_views.png`, `preview_extremes.png`, plus `preview_hard_zoom.png` (the fourth render — CI *warns* while PRs opened before it existed backfill it, then it becomes required); **nothing else** goes in the family dir (reference drawings/photos/datasheets belong in the family issue); the PR checklist is fully ticked; the dir name matches the linked issue's family name; and the **PR body shows its evidence** — the issue's drawing + photo re-embedded under `## Reference`, all four renders embedded by name, the parameter/verification table, and for a multi-body family `preview_parts.png` (file **and** embed) |

## Issue taxonomy

| Title | Purpose |
|---|---|
| `[roadmap] …` | Project roadmap |
| `[workstream] …` | A roadmap workstream |
| `[category] …` | Family category and wanted list |
| `[family] <snake_case>` | Implementable family proposal |
| `[proposal] <name>` | No-code expert proposal |
| `[bug] …` | Design, framework, CI, or documentation bug |
| `[feat] …` | Framework or workflow improvement |

## Fine print

- Commits are DCO-signed (`git commit -s`).
- Code and merged designs are MIT licensed.
- Released dataset artifacts are versioned; published versions are immutable.
- If AI-assisted, the human contributor reviews every line and stands behind
  every range, source, and constraint.
