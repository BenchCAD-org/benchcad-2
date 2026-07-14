# Debugging a family in a 3D GUI

`bench2 preview` gives you PNGs. To *rotate, section, and tweak* a part live, use a
3D viewer. Two ways, pick one.

## A. `tools/debug_family.py` (recommended — one command)

```bash
uv run python tools/debug_family.py --config designs/my_family/part.py
uv run python tools/debug_family.py --config designs/my_family/part.py --strip
uv run python tools/debug_family.py my_family
uv run python tools/debug_family.py my_family --diff hard --seed 3
uv run python tools/debug_family.py my_family outer_d=80 bore_d=30
uv run python tools/debug_family.py my_family --gui
```

It samples a valid parameter set (honouring `spec.check`), applies any `key=value`
overrides, builds, prints `params / check / solids / bbox`, and shows the model.

**Overrides are raw** — they don't re-run `spec.refine()`, so a derived field
(e.g. `width = 2E+(N-1)e`) won't auto-update and `check` will flag it. That's the
point when hunting a bug; override the derived field too, or just pick a clean
sample with `--seed`.

### Edit the geometry live in CQ-editor

Point `--config` straight at a `part.py` — it opens **that file** in CQ-editor so
you edit `build()` and press **F5** to re-render:

```bash
uv tool install cq-editor                                                    # one-time (isolated env)
uv run python tools/debug_family.py --config designs/my_family/part.py
#   … edit build()/PARAMS, press F5, iterate …
uv run python tools/debug_family.py --config designs/my_family/part.py --strip
```

If the file is a clean family `part.py` (no `show_object`) next to a `spec.py`, it
first appends a small **DEBUG block** (a sampled `PARAMS` + `show_object`) so
CQ-editor has something to draw; a scratch copy that already has a block is opened
as-is. The block is guarded (`try/except NameError`) so a normal `import part` /
`bench2` still works while it's there, but **run `--strip` (or delete it) before
you commit** — bench2 needs a clean `build()`. (`<family> --gui` does the same but
samples the family for you.)

(CQ-editor brings its own cadquery 2.8, so it is **not** a repo dependency — the
tool just shells out to the isolated install, like calling `git`. A family that
`import`s from `bench2` may not resolve in CQ-editor's env; for those use
ocp-vscode below.)

### Or a docked panel in VS Code — ocp-vscode (one-time)

```bash
uv add --dev ocp-vscode
```
Then in VS Code install the **"OCP CAD Viewer"** extension, click its plug icon to
start the viewer, and re-run the command **without** `--gui` — the part renders in
a panel you can orbit/section, and it re-renders each run. Runs in the repo env, so
it works for **every** family (including ones that `import` from `bench2`). Without
either viewer the tool writes a `*.step` you can open in FreeCAD.

## Hand-writing a new family

```bash
bench2 new my_family          # scaffolds designs/my_family/{part,spec,family}.py
# write build() in part.py — keep it clean; iterate on it live in CQ-editor (§A)
uv run python tools/debug_family.py --config designs/my_family/part.py   # edit build() in CQ-editor, F5
uv run python tools/debug_family.py my_family                            # or eyeball a sample in 3D
bench2 validate my_family                            # the machine gates
```

## Reading a `part.py` fast

The parts are commented for exactly this. Look for:
- the **header docstring** — what the part is, the coordinate frame (`z=0` is …),
  and a **dimension glossary** mapping drawing symbols → code params;
- **inline comments** on each solid step (rim / hub / bore …).

Copy a known-good instance from the family's issue dimension table (or the
`--gui` DEBUG block's `PARAMS`), nudge one number, re-run, see what moved.
