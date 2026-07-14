<!-- Family PR: one PR = one family, touching only designs/<family>/ -->

## Family

- Family: `<name>`
- Closes #<!-- the family issue number (required) -->
- What the part is (one sentence):

## Checklist

- [ ] `uv run bench2 validate <family>` **passes locally** (CI re-runs it)
- [ ] I ran `uv run bench2 preview <family>` and **looked at the image** — the
      part is what `family.json` says it is, across all three difficulties
- [ ] Every `PARAM_SPEC.source` and every `check()` constraint cites a real
      rule/table, or honestly says `"proportion"` — **nothing fabricated**
- [ ] PR touches only `designs/<family>/`
- [ ] Commits are DCO-signed (`git commit -s`)
- [ ] (If AI-assisted) I reviewed every line and stand behind the constraints

## Sources used

<!-- list the standards/tables/handbook rules your ranges & constraints cite -->
