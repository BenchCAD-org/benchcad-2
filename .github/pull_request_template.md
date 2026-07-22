<!-- Family PR: one PR = one family, touching only designs/<family>/.
     Open this PR AFTER `uv run bench2 validate <family>` passes locally and you
     looked at the previews; for early feedback open it as a GitHub Draft.
     First PR here? A maintainer must approve CI once — no checks = pending, not ignored.
     Reference drawings/photos/datasheets go in the family ISSUE, not designs/. -->

## Family

- Family: `<name>`
- Closes #<!-- the family issue number (required) -->
- What the part is (one sentence):

## Checklist

- [ ] `uv run bench2 validate <family>` **passes locally** (CI re-runs it) —
      [the contributor loop](https://github.com/BenchCAD-org/benchcad-2/blob/main/CONTRIBUTING.md#the-contributor-loop) ·
      [red-CI debugging](https://github.com/BenchCAD-org/benchcad-2/blob/main/docs/DEBUGGING.md)
- [ ] I ran `uv run bench2 preview <family>`, **looked at every image**, and
      **committed all three renders** — `preview.png` (easy/medium/hard grid),
      `preview_views.png` (the four benchmark views), `preview_extremes.png`
      (min & max draw). The part matches the issue's reference drawing across
      all tiers, and both extremes — including the hard/largest draw — are sane
- [ ] Multi-body part? `family.json` declares `"solids": N` (single-solid: omit) —
      [assembly spec](https://github.com/BenchCAD-org/benchcad-2/blob/main/docs/DESIGN_SPEC.md)
- [ ] Every `PARAM_SPEC.source` and every `check()` constraint cites a real
      rule/table, or honestly says `"proportion"` — **nothing fabricated**
      ([rule 10](https://github.com/BenchCAD-org/benchcad-2/blob/main/CONTRIBUTING.md#ten-rules))
- [ ] PR touches only `designs/<family>/`, and only the package files — reference
      drawings/photos live in the family issue
      ([hard gates](https://github.com/BenchCAD-org/benchcad-2/blob/main/CONTRIBUTING.md#what-reviewers-and-ci-enforce))
- [ ] Commits are DCO-signed (`git commit -s`) —
      [fine print](https://github.com/BenchCAD-org/benchcad-2/blob/main/CONTRIBUTING.md#fine-print)
- [ ] (If AI-assisted) I reviewed every line and stand behind the constraints

## Sources used

<!-- list the standards/tables/handbook rules your ranges & constraints cite -->
