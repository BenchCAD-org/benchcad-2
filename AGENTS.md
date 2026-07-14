# BenchCAD 2.0 — Agent Guide

Guide for AI agents and humans contributing to BenchCAD 2.0. This repository
targets **150 industrial part families**.

A family is one `designs/<family>/` directory containing `part.py`, `spec.py`,
and `family.json`. Read `docs/DESIGN_SPEC.md` before implementing one.

```text
DESIGN.md           benchmark architecture and decision record
docs/DESIGN_SPEC.md the part + spec interface
CONTRIBUTING.md     contributor loop
REVIEWING.md        human review checklist
framework/bench2/   CLI: new / validate / preview
designs/            one directory per family
```

## Workflow

```bash
uv sync
uv run bench2 new <family>
uv run bench2 validate <family>
uv run bench2 preview <family>
```

## Hard rules for agent-drafted designs

1. **Never fabricate a source.** Every `PARAM_SPEC` range and every `check()`
   constraint cites a standard table, handbook rule, shop convention, or the
   honest label `"proportion"`.
2. **Constraints must be engineering-true.** Never weaken `check()` to satisfy
   the sampler. Fix inconsistent ranges instead.
3. **Determinism is absolute.** Randomness is allowed only through the `rng`
   argument in `refine()`; `build()` is pure.
4. **A human must inspect `bench2 preview` output** before the PR is opened.
5. **One family PR touches only `designs/<your-family>/`.**
6. Commits are DCO-signed (`git commit -s`) by the human contributor.
7. **Use reviewable evidence.** A family needs its own sourced proposal and a
   complete issue/PR record.

Reviewers audit whether `PARAM_SPEC`/`check()` are true and whether
`family.json` is accurate. Prefer short, readable, physically motivated code.
