# Reviewing a family PR

Every design PR must pass the automated gates and one human review by someone
who is not the author (CONTRIBUTING.md rule 3). Machines already proved the
design *runs*; your job is to judge whether it is *true*. Budget: ~15 minutes.

## What is already machine-checked (don't re-do it)

`bench2 validate` in CI: file structure, `part.py` + `spec.py` exist, every
difficulty × seed samples within constraints **and within the declared
PARAM_SPEC ranges** (spec-contract), programs execute to non-degenerate
geometry — **every body has real volume, and the body count matches
`family.json` `"solids"`** when a multi-body family declares it — same seed ⇒
byte-identical program, difficulties distinct, geometry novelty, table
`coverage`, geomlib declared + inlined. Two more gates: `require-issue-link`
(body has `Closes #N`) and `family-pr-checks` (one family per PR + all three
renders committed). CI red = stop, back to the author. CI green = start here.

## Review order

0. **Is the issue's evidence real?** The implementer verified it when
   claiming (CONTRIBUTING.md "Claiming an issue = you verify it") — you are
   the only other pair of eyes. Glance: standard link live, dimension table
   has min/max rows, no obvious mismatch with the PR. Thin evidence = request
   changes on the issue, not the code.
1. **Renders vs the source pictures.** Put `preview_views.png` (the four
   diagonal views exactly as the model will see them) next to the dimensioned
   drawing in the family issue: is it the same part? Are easy/medium/hard
   plausible tiers of one part — not three parts, not clones?
2. **Extremes vs the table.** `preview_extremes.png` shows the globally
   smallest and largest draw. Hold them against the min/max rows of the
   dimension table in the issue: sane proportions at the small end, correct
   features at the large end?
3. **Coverage.** Table-driven family ⇒ validate must print
   `coverage: <param> reaches all N declared values`. No coverage line on a
   table-anchored family? Request a `coverage=[...]` declaration.
4. **Verify the equations — NOTES.md, three layers.** Any family that derives
   geometry from equations or standard tables
   must ship a `NOTES.md` mapping datasheet symbols → parameters → formulas.
   Check the three layers in order:
   - **(a) Formula vs standard.** Every derived quantity in `part.py`/`spec.py` must
     trace to a cited clause or be declared a fit/proportion. Examples of
     what "correct" means: the implemented equation matches the cited
     source, including units, tolerances, and domain. A formula with no source
     and no `proportion` declaration is a review comment.
   - **(b) Numbers vs catalog.** Recompute **at least one row yourself**:
     take a catalog row from the issue's dimension table, push it through the
     design's formula, compare against the printed column (expect ≲ 0.5 % or
     a deviation the author explains). The author's own evidence is the
     "Verified against catalog" column in NOTES.md — your job is to spot-check
     it. Record the input row, computed result, and catalog value in the review.
   - **(c) Deviations declared.** Where the design intentionally departs from
     the catalog (fitted constants, unmodeled sub-mm features, simplified
     finishes), NOTES.md must say so under "Deliberate deviations". An
     undeclared mismatch you find in (b) is either a bug or a missing
     deviation entry — both are review comments.
5. **Audit `check()` — the heart of the review.** For every constraint: is it
   engineering-true (would a machinist agree)? Is the cited rule real —
   spot-check any standard number (**fabricated citation ⇒ reject the PR**)?
   What's *missing* — think tear-out, thin walls, tool clearance, unstable
   proportions, and check those failure modes are constrained.
6. **Audit `PARAM_SPEC`.** Ranges sensible per tier; `source` fields specific
   (a table, a rule, or honest `"proportion"`); `askable` only on parameters
   visible/derivable from the part; `feature` on optional-feature toggles;
   `coverage` on the table-driving parameter.
7. **`family.json`.** Name accurate, `standard` correct or null, `base_plane`
   matches the build, `geomlib` lists exactly the helpers used, description
   honest, `contributor` is the actual author.
8. **Scope.** PR touches only `designs/<family>/`; description has
   `Closes #N` (CI enforces); commits DCO-signed.

## The verdict

Approve with a three-line comment so the dossier is self-explaining (the
credits board records you as the verifier):

```
views ✓ (against the issue drawing)
equations ✓ (recomputed one source-table row)
constraints ✓ (wall/clearance rules are sound; no missing failure mode found)
```

Or request changes, comments limited to the topics above. One pass, verdict
within days.

## Labels

Only one matters: `needs-evidence` on an issue whose package is incomplete.
PRs need no labels — CI status + GitHub review states (approve / request
changes) are the workflow.

## After merge — all automatic

`dossier.yml` posts the acceptance evidence back to the family issue;
STATUS.md flips the family to MERGED; the credits workflow adds the full
provenance row (proposed / implemented / verified) to
CONTRIBUTORS.md. You do nothing.
