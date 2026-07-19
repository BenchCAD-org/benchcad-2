# Contributing

BenchCAD 2.0 is built from **150 explicit parametric part families**. Every
merged family contributes readable engineering knowledge: geometry, sourced
parameter ranges, constraints, reference evidence, and provenance.

Questions → [Discord](https://discord.gg/be9AtvrDyK). New to GitHub? Use the
step-by-step guides: [English](docs/GETTING_STARTED.md) ·
[中文](docs/GETTING_STARTED.zh.md).

## The contributor loop

```bash
uv sync
uv run bench2 new <family>
# fill designs/<family>/{part.py,spec.py,family.json}
uv run bench2 validate <family>
uv run bench2 preview <family>     # inspect every generated view yourself
# submit one PR with `Closes #<family-issue>`
```

## Ten rules

1. **One family = one issue = one PR.** A family PR touches only
   `designs/<family>/` and includes `Closes #N`.
2. **`bench2 validate` must pass locally.** CI reruns the same gates.
3. **A non-author reviews the family** using [`REVIEWING.md`](REVIEWING.md).
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
| 4 | PR | Submit one scoped PR with `Closes #N` |
| 5 | CI | CI reruns validation and posts the report and previews |
| 6 | Review | A non-author audits the evidence, renders, equations, constraints, and labels |
| 7 | Merge | The issue closes and provenance/status automation runs |
| 8 | Release | Qualified families enter the next versioned manifest |

## Evidence check before coding

The implementer is the first verifier. Confirm:

1. A real standard, catalog, datasheet, handbook, or honest proportion basis.
2. A dimensioned drawing or equivalent source that maps symbols to geometry.
3. A table or documented range containing minimum and maximum examples.
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

**Hard gates (red ✗ = cannot merge)** — so review spends its time on *truth*, not
structure. A family PR must pass all three:

| Gate | Enforces |
|---|---|
| `validate.yml` | `bench2 validate` — samples, constraints, execution, determinism, coverage, and that **every body is non-degenerate** (multi-body: matches `family.json` `"solids"`) |
| `require-issue-link.yml` | the PR body links its family issue (`Closes #N`, still open) |
| `family-pr-checks.yml` | **one family per PR** (only `designs/<family>/`, plus a `geomlib` helper if you add one) and the family ships all six files: `part.py`, `spec.py`, `family.json`, `preview.png`, `preview_views.png`, `preview_extremes.png` |

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
