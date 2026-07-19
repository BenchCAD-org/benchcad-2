# Getting started — for engineers who don't use GitHub

You do **not** need to know GitHub. Follow the steps literally. 中文版:
[GETTING_STARTED.zh.md](GETTING_STARTED.zh.md)

**Jargon, translated once:** *repository (repo)* = the project folder online ·
*issue* = a discussion thread / work item · *assign* = put your name on it ·
*fork* = your personal copy of the project · *pull request (PR)* = "please
review and accept my folder" · *CI* = robots that auto-check your submission ·
*merge* = accepted.

---

## Path 0 — contribute your engineering knowledge, zero code (~15 min)

You know parts, standards, and catalogs. That is the valuable half. We'll write
the code.

1. Make a free account at github.com (email + password, like any site).
2. Open the [family issues list](../../../issues?q=is%3Aissue+is%3Aopen+label%3Afamily).
   Each thread is one mechanical part we want.
3. Click a part you know (or click **New issue** for one we missed, title it
   `[family] part_name`).
4. Write a comment containing:
   - a **datasheet or catalog link** (norelem, Misumi, McMaster, a standard table…),
   - a **picture** — drag the datasheet drawing or a photo straight into the comment box,
   - the **parameter table** (which dimensions vary, their ranges),
   - the **engineering constraints** in plain words — the "a machinist would
     reject this because…" rules (e.g. *"bolt hole center must be ≥1.5×d from
     the edge or it tears out"*). These rules are the whole point.
5. Done. A maintainer turns it into code; **you are credited by name** in the
   dataset and as a co-author on the paper (see CONTRIBUTING.md rule 9).

## Path 1 — full contribution, with code (~half a day, basic Python needed)

### One-time setup (~15 min)

1. GitHub account (as above), signed in.
2. Install **git**: macOS — already there (type `git` in Terminal); Windows —
   install "Git for Windows" from git-scm.com, then use the "Git Bash" app.
3. Install **uv** (Python manager, one line, from astral.sh/uv):
   `curl -LsSf https://astral.sh/uv/install.sh | sh`
4. On the repo page, click **Fork** (top right) → Create fork. This makes your
   personal copy.
5. In your terminal:
   ```bash
   git clone https://github.com/<YOUR-USERNAME>/benchcad-2.git
   cd benchcad-2
   uv sync        # installs everything, takes a few minutes once
   ```

### Claim → build → check (the loop)

6. On the [family issues list](../../../issues?q=is%3Aissue+is%3Aopen+label%3Afamily),
   open the part you want → right sidebar → **Assignees → assign yourself**
   (or just comment "I'll take this"). Now it's yours; nobody else will start it.
7. Scaffold your family:
   ```bash
   uv run bench2 new my_family
   ```
8. Fill in the two files `part.py` and `spec.py` under `designs/my_family/`. In engineer terms:
   - `build(...)` in `part.py` — the part itself: named parameters → the solid,
     written as plain CadQuery (Python that builds the shape)
   - `PARAM_SPEC` in `spec.py` — the **parameter table** (name, unit, range per
     difficulty, and *where the range comes from*: a standard table or "proportion")
   - `check(p)` in `spec.py` — the **rejection rules** (what combinations are
     unmanufacturable, each with its reason). This is what the human reviewer reads.
   - `refine(p, difficulty, rng)` in `spec.py` — *only if* your parameters are
     coupled (one value computed from others, or a real table row); the framework
     does the sampling itself, so you never hand-write a generator
   The files created by `bench2 new` contain annotated TODOs for every required
   field. Fill `family.json` (labels) and use `NOTES.md` to map source symbols
   to formulas for table- or equation-driven families.
   `build()` must bind `result`, use only `cq`/`math`/your own `_helpers` (no
   other imports), and return one solid — or a compound / `cq.Assembly` for a
   multi-body part (then set `"solids": N` in `family.json`). Full rules:
   [`DESIGN_SPEC.md`](DESIGN_SPEC.md). If a raw CadQuery script errors with
   `HashCode`, see [`DEBUGGING.md`](DEBUGGING.md) → Gotchas.
9. Check yourself — two commands, on your machine, instant:
   ```bash
   uv run bench2 validate my_family   # PASS = your code works. That's the rule.
   uv run bench2 preview my_family    # renders preview.png + preview_views.png
   ```
   `preview_views.png` shows the four views **the model will see** — hold it
   next to the datasheet drawing from your issue. Fix and re-run until PASS
   and the renders look like the real part.

### Submit

10. ```bash
    git add designs/my_family
    git commit -s -m "Add my_family"     # -s adds your sign-off line (required)
    git push
    ```
11. Go to your fork's page on GitHub — a yellow banner says **"Compare & pull
    request"**. Click it. In the description type `Closes #<the issue number>`.
    Click **Create pull request**.
12. Robots run the same checks you ran (green check = pass) and post your
    preview image. Then one human reviews **exactly two things**: are your
    constraints true, and are your labels right.
13. If changes are requested: edit the same files locally, then
    `git add … && git commit -s -m "fix" && git push` — the PR updates by
    itself. **Never open a new PR for fixes.**
14. Merged = done. Credit is automatic (CONTRIBUTORS.md, dataset card, paper
    co-authorship). What happens next (instance generation, difficulty
    screening, release) is automated — watch your family on
    [STATUS.md](../STATUS.md). You never need to do anything after merge.

## When something goes wrong

- **CI shows a red ✗** → click "Details" next to it; the last lines of the log
  say which gate failed — it's the same output as `bench2 validate` locally.
- **"DCO" check is red** → your commit lacks the sign-off: run
  `git commit --amend -s --no-edit && git push --force-with-lease`.
- **`bench2 validate` says "sample violates check"** → your ranges and your
  constraints disagree; widen the range or fix the rule (don't delete the rule
  to make it pass — reviewers read the rules first).
- **Stuck > 20 minutes** → comment on your issue. Someone will answer there.
  (No DMs needed — everything lives in the issue, see CONTRIBUTING.md rule 7.)
