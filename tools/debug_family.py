"""bench2 debug — open a part.py in a 3D GUI (CQ-editor) to edit it live.

Two ways to launch, pick one:

    # 1) point straight at a part.py file — opens it in CQ-editor, F5 to re-render
    uv run python tools/debug_family.py --config designs/my_family/part.py

    # 2) give a family name — samples a valid instance, then opens its part.py
    uv run python tools/debug_family.py my_family --gui

`--config <path>` is the simple entry: it launches the stand-alone CQ-editor on the
file you name. If that file is a clean family `part.py` (no `show_object`) sitting
next to a `spec.py`, it first appends a small DEBUG block (a sampled `PARAMS` +
`show_object`) so CQ-editor has something to draw; otherwise it opens the file as-is
(e.g. a scratch copy you already gave a debug block). Edit `build()` / `PARAMS`,
press **F5**. Remove the block again with `--strip`:

    uv run python tools/debug_family.py --config designs/my_family/part.py --strip

CQ-editor is a stand-alone app in its own env (`uv tool install cq-editor`, one-time);
it brings cadquery 2.8, which can't share the repo's pinned 2.3, so it is NOT a repo
dependency — this script just launches it. A family that imports from `bench2` may
not resolve in CQ-editor's env; for those use ocp-vscode (below).

Without a GUI: `debug_family.py <family> [--diff easy|medium|hard] [--seed N] [k=v ...]`
builds a sample and prints params/check/solids/bbox, showing it via ocp-vscode if
installed (`uv add --dev ocp-vscode`, works for every family), else writing a STEP.
"""
import importlib.util
import os
import sys

import numpy as np

sys.path.insert(0, "framework")
from bench2 import sampling                       # noqa: E402
from bench2.render import _ocp_hashcode_fix       # noqa: E402

_ocp_hashcode_fix()

_MARK = "# ─── DEBUG (bench2 debug --gui)"
# Appended to a part.py so CQ-editor renders it on F5. The try/except keeps a normal
# `import part` (and bench2) safe when the block is present — show_object only exists
# inside CQ-editor.
_DEBUG_BLOCK = '''

{mark} — DELETE, or run `--strip`, BEFORE COMMITTING ───────
PARAMS = dict(
    {params}
)
try:
    show_object(build(**PARAMS), name="{family}")   # F5 in CQ-editor
except NameError:
    pass
'''


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _strip(part_path):
    src = open(part_path).read()
    idx = src.find(_MARK)
    if idx < 0:
        print("no debug block to strip")
        return
    open(part_path, "w").write(src[:idx].rstrip() + "\n")
    print(f"stripped the debug block from {part_path}")


def _launch(path):
    import shutil
    import subprocess
    cqed = shutil.which("cq-editor") or os.path.expanduser("~/.local/bin/cq-editor")
    if not (os.path.exists(cqed) or shutil.which("cq-editor")):
        print("view      : CQ-editor not installed. One-time:  uv tool install cq-editor")
        print(f"            then: cq-editor {path}")
        return
    # detached so it outlives this script and doesn't block the shell
    subprocess.Popen([cqed, path], start_new_session=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"view      : opened {path} in CQ-editor — edit build()/PARAMS, press F5.")


def _open_config(path):
    """--config: open CQ-editor straight on the given part.py."""
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        print(f"no such file: {path}")
        return 2
    src = open(path).read()
    if _MARK not in src and "show_object" not in src:
        # a clean part.py — give CQ-editor something to draw by sampling a sibling spec
        d = os.path.dirname(path)
        spec_py = os.path.join(d, "spec.py")
        if os.path.isfile(spec_py):
            fam = os.path.basename(d)
            spec = _load("spec", spec_py)
            p = sampling.sample(spec, "medium", np.random.default_rng(0))
            params_src = ",\n    ".join(f"{k}={v!r}" for k, v in p.items())
            with open(path, "a") as f:
                f.write(_DEBUG_BLOCK.format(mark=_MARK, params=params_src, family=fam))
            print(f"note      : appended a DEBUG block (sampled PARAMS) — `--strip` to remove it.")
        else:
            print("note      : file has no show_object — CQ-editor opens it but draws nothing.")
    _launch(path)
    return 0


def _open_family_in_gui(family, p):
    """--gui: append a sampled block to the family's part.py, then open it."""
    part_path = f"designs/{family}/part.py"
    src = open(part_path).read()
    if _MARK not in src:
        params_src = ",\n    ".join(f"{k}={v!r}" for k, v in p.items())
        with open(part_path, "a") as f:
            f.write(_DEBUG_BLOCK.format(mark=_MARK, params=params_src, family=family))
        print(f"            ⚠️ appended a DEBUG block to {part_path}; `--strip {family}` before committing.")
    _launch(part_path)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    # --config <path>: the simple path-based entry (no family needed)
    config, strip, gui = None, False, False
    rest = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--config":
            config = argv[i + 1]; i += 2
        elif a == "--strip":
            strip = True; i += 1
        elif a == "--gui":
            gui = True; i += 1
        else:
            rest.append(a); i += 1

    if config is not None:
        if strip:
            _strip(os.path.abspath(config))
            return 0
        return _open_config(config)

    # family mode
    if not rest:
        print(__doc__)
        return 1
    family = rest[0]
    diff, seed, overrides = "medium", 0, {}
    j = 1
    while j < len(rest):
        a = rest[j]
        if a == "--diff":
            diff = rest[j + 1]; j += 2
        elif a == "--seed":
            seed = int(rest[j + 1]); j += 2
        elif "=" in a:
            k, v = a.split("=", 1)
            overrides[k] = v; j += 1
        else:
            print(f"ignoring arg {a!r}"); j += 1

    if not os.path.isdir(f"designs/{family}"):
        print(f"no such family: designs/{family}/  (run from the repo root)")
        return 2
    if strip:
        _strip(f"designs/{family}/part.py")
        return 0

    part = _load("part", f"designs/{family}/part.py")
    spec = _load("spec", f"designs/{family}/spec.py")
    p = sampling.sample(spec, diff, np.random.default_rng(seed))
    ints = {k for k, d in spec.PARAM_SPEC.items() if d.get("integer")}
    for k, v in overrides.items():
        p[k] = int(round(float(v))) if k in ints else float(v)

    bad = spec.check(p)
    print("family    :", family)
    print("params    :", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in p.items()})
    print("check     :", "clean" if not bad else bad)
    obj = part.build(**p)
    val = obj.val() if hasattr(obj, "val") else obj
    bb = val.BoundingBox()
    print("solids    :", len(val.Solids()))
    print("bbox (mm) : X %.1f  Y %.1f  Z %.1f" % (bb.xlen, bb.ylen, bb.zlen))

    if gui:
        _open_family_in_gui(family, p)
        return 0
    try:
        from ocp_vscode import show
        show(obj, name=family)
        print("view      : shown in the OCP CAD Viewer (VS Code)")
    except ImportError:
        import cadquery as cq
        out = f"{family}_debug.step"
        cq.exporters.export(val, out)
        print(f"view      : no viewer — wrote {out} (FreeCAD), or use --config <part.py> for CQ-editor.")
        print("            live viewers:  uv tool install cq-editor   |   uv add --dev ocp-vscode")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
