"""bench2 edit — live-edit a family's part.py in CQ-editor, in this repo's env.

    uv run bench2 edit <family>                      # medium sample, seed 0
    uv run bench2 edit <family> --diff hard --seed 3
    uv run bench2 edit <family> outer_d=80 n_grooves=2
    uv run bench2 edit --file designs/<family>/part.py
    uv run bench2 edit <family> --strip              # emergency cleanup

One command, no manual setup:

1. installs CQ-editor on first use (`uv run --group editor`, ~1 min, then cached);
2. appends a *scratch block* to `part.py` — a sampled `PARAMS` dict plus the
   `show_object(build(**PARAMS))` call CQ-editor needs in order to draw anything;
3. opens CQ-editor on that file — press **F5** to render (the part appears
   on the first F5, not on open), edit `build()`/`PARAMS`, save with ⌘S/Ctrl-S;
4. removes the scratch block again when you close the editor, so `part.py` goes
   back to the clean `build()` the benchmark derives its programs from. Your
   edits above the block are kept. (`bench2 validate` fails if a block is still
   there — e.g. after a crash; `bench2 edit <family> --strip` removes it.)

Why the project env rather than a stand-alone `uv tool install cq-editor`: the
editor then runs the *same* cadquery the benchmark pins (2.3.0) and can
`import bench2`, so families using `bench2.geomlib` helpers render exactly as
`bench2 validate` will build them.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

MARK_START = "# ── bench2 edit: scratch block — removed when you close the editor ──"
MARK_END = "# ── end bench2 edit scratch block ──"
# tools/debug_family.py wrote this one; recognise it so old blocks clean up too.
LEGACY_MARK = "# ─── DEBUG (bench2 debug --gui)"

_BLOCK = """

{start}
PARAMS = dict(
    {params}
)
try:
    show_object(build(**PARAMS), name="{family}")   # F5 in CQ-editor draws this
except NameError:                                   # plain import: no viewer
    pass
{end}
"""

# Applied in the editor process before cadquery is touched: the pinned
# cadquery 2.3.0 / OCP 7.9 pair is missing TopoDS_*.HashCode, which CQ-editor
# and build() both reach for. cqe_run.py also drops CASROOT — do the same.
_BOOT = (
    "import os, sys\n"
    "os.environ.pop('CASROOT', None)\n"
    "from bench2.render import _ocp_hashcode_fix; _ocp_hashcode_fix()\n"
    "from cq_editor.__main__ import main\n"  # builds QApplication(sys.argv) on import
    "main()\n"
)


def has_scratch_block(src: str) -> bool:
    """True if this part.py source still carries an editor scratch block."""
    return MARK_START in src or LEGACY_MARK in src


def strip_block(path: Path) -> bool:
    """Remove the scratch block, keeping everything the user wrote above it."""
    src = path.read_text()
    for mark in (MARK_START, LEGACY_MARK):
        if mark not in src:
            continue
        head, _, tail = src.partition(mark)
        rest = tail.partition(MARK_END)[2] if (mark == MARK_START and MARK_END in tail) else ""
        if mark == LEGACY_MARK and "def " in tail:
            # legacy blocks have no end sentinel; a mark that still has code
            # after it was hand-moved mid-file — refuse to eat that code
            print(f"bench2 edit: legacy debug mark mid-file in {path} (code "
                  "follows it) — not stripping; remove it by hand")
            return False
        path.write_text((head.rstrip() + "\n" + rest.lstrip("\n")).rstrip() + "\n")
        return True
    return False


def _sample_build_params(fam_dir: Path, diff: str, seed: int, overrides: dict) -> dict:
    """A valid instance for this family, filtered to build()'s own arguments."""
    import inspect

    import numpy as np

    from .loader import load_family
    from .sampling import sample

    part, spec = load_family(fam_dir)
    p = sample(spec, diff, np.random.default_rng(seed))
    ints = {k for k, e in spec.PARAM_SPEC.items() if e.get("integer")}
    for k, v in overrides.items():
        if k not in p:
            print(f"  note      : {k}= is not a parameter of this family — ignored")
            continue
        p[k] = int(round(float(v))) if k in ints else float(v)
    problems = spec.check(p)
    print(f"  instance  : {diff}, seed {seed}")
    print("  check     :", "clean" if not problems else problems)
    if overrides:
        print("  note      : overrides are raw — spec.refine() does NOT re-run, so a")
        print("              derived field stays stale until you override it too.")
    # build() takes only its own named parameters; spec-only selectors (e.g.
    # model_index) are not build arguments — the same filter derive.py applies.
    argnames = set(inspect.signature(part.build).parameters)
    return {k: v for k, v in p.items() if k in argnames}


def _write_block(path: Path, family: str, params: dict) -> None:
    body = ",\n    ".join(f"{k}={v!r}" for k, v in params.items())
    with path.open("a") as f:
        f.write(_BLOCK.format(start=MARK_START, end=MARK_END, params=body, family=family))


def _launch(path: Path) -> int:
    """Run CQ-editor in this project's env and block until the window closes."""
    uv = shutil.which("uv")
    try:
        import cq_editor  # noqa: F401

        installed = True
    except Exception:  # noqa: BLE001
        installed = False

    if uv:
        # `--group editor` installs CQ-editor into this project's env on first
        # use (cached afterwards), so there is no separate setup step.
        if not installed:
            print("  editor    : first run — installing CQ-editor into this env "
                  "(uv --group editor, ~1 min, cached after) …")
        cmd = [uv, "run", "--group", "editor", "python", "-c", _BOOT, str(path)]
    else:
        if not installed:
            print("bench2 edit: CQ-editor is not installed and `uv` is not on PATH.")
            print("             Install it into this env, then re-run:")
            print("               uv sync --group editor      # or: pip install 'cq-editor>=0.7'")
            return 1
        cmd = [sys.executable, "-c", _BOOT, str(path)]

    print(f"  editor    : opening {path} — press F5 to render (first draw included), edit build()/PARAMS.")
    print("              Close the editor window when you're done; the scratch")
    print("              block is removed automatically.")
    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        return 130


def edit_part(path: Path, family: str, fam_dir: Path | None,
              diff: str, seed: int, overrides: dict) -> int:
    """Add a scratch block (if the file needs one), open the editor, clean up."""
    src = path.read_text()
    added = False
    if has_scratch_block(src):
        print("  note      : reusing the scratch block already in the file")
    elif "show_object" in src:
        print("  note      : file already calls show_object — opening it as-is")
    elif fam_dir is None:
        print("  note      : no spec.py next to it — opening as-is (nothing to draw)")
    else:
        params = _sample_build_params(fam_dir, diff, seed, overrides)
        _write_block(path, family, params)
        added = True

    try:
        rc = _launch(path)
    finally:
        if added or has_scratch_block(path.read_text()):
            if strip_block(path):
                print(f"  cleaned   : scratch block removed from {path}")
    return rc


def cmd_edit(family: str | None, file: str | None, diff: str, seed: int,
             overrides: list[str], strip_only: bool) -> int:
    if file:
        if family:
            # with --file the family positional is unused, so argparse parks
            # the first k=v override there — reclaim it, and refuse a real
            # family name so nothing is ever silently swallowed
            if "=" in family:
                overrides = [family] + list(overrides)
            else:
                print("bench2 edit: --file and a family name are mutually "
                      f"exclusive (got --file {file} and {family!r})")
                return 2
        path = Path(file).resolve()
        if not path.is_file():
            print(f"bench2 edit: no such file: {file}")
            return 2
        fam_dir = path.parent if (path.parent / "spec.py").is_file() else None
        fam = path.parent.name
    else:
        if not family:
            print("bench2 edit: give a family name, or --file <path/to/part.py>")
            return 2
        fam_dir = Path.cwd() / "designs" / family
        if not fam_dir.is_dir():
            print(f"bench2 edit: no such family: designs/{family}/ (run from the repo root)")
            return 2
        path, fam = fam_dir / "part.py", family

    if strip_only:
        if strip_block(path):
            print(f"stripped the scratch block from {path}")
        else:
            print(f"no scratch block in {path}")
        return 0

    kv = {}
    for item in overrides:
        if "=" not in item:
            print(f"bench2 edit: ignoring {item!r} (expected key=value)")
            continue
        k, v = item.split("=", 1)
        kv[k] = v
    print(f"  family    : {fam}")
    return edit_part(path, fam, fam_dir, diff, seed, kv)
