# CLAUDE.md

Read [`AGENTS.md`](AGENTS.md) first. The interface contract is
[`docs/DESIGN_SPEC.md`](docs/DESIGN_SPEC.md).

Repo-specific reminders:

- Run commands from the repo root with `uv run`.
- The environment is pinned (`cadquery==2.3.0`, `numpy==1.26.4`).
- `bench2 validate` must pass and a human must inspect `bench2 preview` output.
- Never fabricate standards citations; use `"proportion"` when appropriate.
- Keep every family auditable: source ranges and constraints in the issue and
  preserve the one-family-per-PR boundary.
