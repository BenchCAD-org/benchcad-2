<!-- Family PR: one PR = one family, touching only designs/<family>/.
     Open this PR AFTER `uv run bench2 validate <family>` passes locally and you
     looked at the previews; for early feedback open it as a GitHub Draft.
     First PR here? A maintainer must approve CI once — no checks = pending, not ignored.
     Reference drawings/photos/datasheets go in the family ISSUE, not designs/. -->

## Family

- Family: `<name>`
- Closes #<!-- the family issue number (required) -->
- What the part is (one sentence):

## Reference (re-embedded from the family issue — CI checks this section)

<!-- Copy the issue's dimensioned drawing AND product photo here (2+ images),
     so the renders below can be compared against the reference in one place. -->
| Dimensioned drawing | Product photo |
|---|---|
| <!-- ![drawing](…) --> | <!-- ![photo](…) --> |

## Renders (regenerated at this PR's head — CI checks each name appears)

<!-- Keep the filename in the alt text. Link the committed file at your head
     SHA (https://raw.githubusercontent.com/<org>/<repo>/<sha>/designs/<family>/…)
     or drag the image in and keep the name in the alt text. -->

![preview.png](…)          <!-- easy/medium/hard difficulty grid -->
![preview_views.png](…)    <!-- the four benchmark views the model sees -->
![preview_hard_zoom.png](…)<!-- front/side/top/iso of a hard example -->
![preview_extremes.png](…) <!-- the min & max sampled instances -->
<!-- multi-body family: also ![preview_parts.png](…) — every part in isolation -->

## Verification (CI checks a table exists)

<!-- The issue's parameter rows + what you sampled: one row per verified
     instance (difficulty/seed, key dims, solids count, bbox …). -->
| difficulty | seed | … | solids | bbox (mm) |
|---|---|---|---|---|

## Checklist

- [ ] `uv run bench2 validate <family>` **passes locally** (CI re-runs it) —
      [the contributor loop](https://github.com/BenchCAD-org/benchcad-2/blob/main/CONTRIBUTING.md#the-contributor-loop) ·
      [red-CI debugging](https://github.com/BenchCAD-org/benchcad-2/blob/main/docs/DEBUGGING.md)
- [ ] I ran `uv run bench2 preview <family>`, **looked at every image**, and
      **committed all four renders**; the easy/medium/hard labels show **every
      catalog column as a value or range** (sw, a, d, f, …) — `preview.png` (easy/medium/hard grid),
      `preview_views.png` (the four benchmark views), `preview_hard_zoom.png`
      (front/side/top/iso of a hard example), `preview_extremes.png` (min & max
      draw). The part matches the issue's reference drawing across all tiers, and
      both extremes — including the hard/largest draw — are sane
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
