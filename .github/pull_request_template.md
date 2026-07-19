<!-- Family PR: one PR = one family, touching only designs/<family>/ -->

## Family

- Family: `<name>`
- Closes #<!-- the family issue number (required) -->
- What the part is (one sentence):

## Checklist

- [ ] `uv run bench2 validate <family>` **passes locally** (CI re-runs it)
- [ ] I ran `uv run bench2 preview <family>`, **looked at every image**, and
      **committed all three renders** — `preview.png` (easy/medium/hard grid),
      `preview_views.png` (the four benchmark views), `preview_extremes.png`
      (min & max draw). The part matches the issue's reference drawing across
      all tiers, and both extremes — including the hard/largest draw — are sane
- [ ] Multi-body part? `family.json` declares `"solids": N` (single-solid: omit)
- [ ] Every `PARAM_SPEC.source` and every `check()` constraint cites a real
      rule/table, or honestly says `"proportion"` — **nothing fabricated**
- [ ] PR touches only `designs/<family>/` (one family = one PR)
- [ ] Commits are DCO-signed (`git commit -s`)
- [ ] (If AI-assisted) I reviewed every line and stand behind the constraints

## Sources used

<!-- list the standards/tables/handbook rules your ranges & constraints cite -->
