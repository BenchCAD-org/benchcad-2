# Debugging a family in a 3D GUI

`bench2 preview` gives you PNGs. To *rotate, section, and tweak* a part live:

```bash
uv run bench2 edit my_family      # opens part.py in CQ-editor — edit, press F5
```

That is the whole setup — the editor installs itself on first run. Details in
§A; ocp-vscode (a docked VS Code panel) is the alternative in §B.

## Gotchas (the pinned environment bites in specific ways)

- **`AttributeError: 'TopoDS_*' object has no attribute 'HashCode'`** — you ran
  CadQuery *outside* bench2 (a REPL, your own test script). The pinned
  `cadquery 2.3.0` calls `HashCode`, which `cadquery-ocp 7.9.3` removed. bench2
  and `debug_family.py` apply a one-time shim for you; to poke geometry in your
  own script, apply it first:
  ```python
  import sys; sys.path.insert(0, "framework")
  from bench2.render import _ocp_hashcode_fix; _ocp_hashcode_fix()
  import cadquery as cq          # now .faces()/.solids()/export work
  ```
- **`build()` may return more than one solid.** A multi-body part (a telescoping
  slide's members) is fine — `a.union(b)` of separate bodies,
  `cq.Compound.makeCompound([...])`, or a `cq.Assembly` (folded to a compound on
  export). Declare the count with `"solids": N` in `family.json`, and `validate`
  will fail if a member silently vanishes. Every body must have real volume.
- **The editor runs the pinned CadQuery.** `bench2 edit` installs CQ-editor into
  *this project's* env, so it uses the same `cadquery 2.3.0` (and the same
  `bench2.geomlib` helpers) that `bench2 validate` will score — what you see is
  what the benchmark builds. Don't `uv tool install cq-editor` separately: that
  isolated copy brings CadQuery 2.8 and can't import `bench2`.

## A. `bench2 edit` — live 3D editing (recommended)

```bash
uv run bench2 edit my_family                    # medium sample, seed 0
uv run bench2 edit my_family --diff hard --seed 3
uv run bench2 edit my_family outer_d=80 bore_d=30
uv run bench2 edit --file designs/my_family/part.py
uv run bench2 edit my_family --strip            # emergency cleanup (see below)
```

One command, no setup step. It

1. **installs CQ-editor on first use** into this project's env (`--group editor`,
   ~1 min, cached afterwards);
2. samples a valid instance (honouring `spec.check`), applies any `key=value`
   overrides, and appends a **scratch block** to `part.py` — the `PARAMS` dict
   plus the `show_object(build(**PARAMS))` call CQ-editor needs to draw anything;
3. opens the editor on that file: edit `build()` / `PARAMS`, press **F5** to
   re-render, ⌘S/Ctrl-S to save;
4. **removes the scratch block when you close the editor**, so `part.py` goes back
   to the clean `build()` the benchmark derives programs from. Your edits above
   the block are kept.

If the editor is killed (or your machine crashes) the block survives — then
`bench2 validate` fails with *"part.py still has a `bench2 edit` scratch block"*
and `bench2 edit <family> --strip` removes it.

**Overrides are raw** — they don't re-run `spec.refine()`, so a derived field
(e.g. `width = 2E+(N-1)e`) won't auto-update and `check` will flag it. That's the
point when hunting a bug; override the derived field too, or just pick a clean
sample with `--seed`.

### Just want the numbers, no GUI?

```bash
uv run python tools/debug_family.py my_family --diff hard --seed 3
uv run python tools/debug_family.py my_family outer_d=80 bore_d=30
```

builds one sample and prints `params / check / solids / bbox` (and shows it in
ocp-vscode if you have it, else writes a `*.step`).

### B. Or a docked panel in VS Code — ocp-vscode (one-time)

```bash
uv add --dev ocp-vscode
```
Then in VS Code install the **"OCP CAD Viewer"** extension, click its plug icon to
start the viewer, and re-run `tools/debug_family.py <family>` — the part renders in
a panel you can orbit/section, and it re-renders each run. You edit in VS Code
instead of in the editor window; `part.py` stays clean the whole time. Without any
viewer the tool writes a `*.step` you can open in FreeCAD.

## Hand-writing a new family

```bash
bench2 new my_family          # scaffolds designs/my_family/{part,spec,family}.py
# write build() in part.py — keep it clean; iterate on it live in CQ-editor:
uv run bench2 edit my_family  # F5 to re-render; the scratch block auto-removes on close
bench2 validate my_family     # the machine gates
```

## Reading a `part.py` fast

The parts are commented for exactly this. Look for:
- the **header docstring** — what the part is, the coordinate frame (`z=0` is …),
  and a **dimension glossary** mapping drawing symbols → code params;
- **inline comments** on each solid step (rim / hub / bore …).

Copy a known-good instance from the family's issue dimension table (or the
scratch block's `PARAMS` in `bench2 edit`), nudge one number, press F5, see what
moved.
