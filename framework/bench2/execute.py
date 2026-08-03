"""Run a CadQuery program string -> STEP file, in a subprocess.

Vendored from BenchCAD-main `benchcad_core/scoring/exec_cq.py` (MIT) so the
contributor framework has no cross-repo dependency. Behavior is identical:
the pinned cadquery 2.3.0 / cadquery-ocp 7.9.3 environment, the OCP HashCode
shim, and export of the solid bound to `result`.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

_OCP_HASHCODE_FIX = """
# cadquery 2.3 <-> cadquery-ocp 7.9 compat: OCP removed TopoDS_*.HashCode but
# cq's exporter still calls it. Restore as identity-based stub.
from OCP.TopoDS import (TopoDS_Shape, TopoDS_Face, TopoDS_Edge, TopoDS_Vertex,
    TopoDS_Wire, TopoDS_Shell, TopoDS_Solid, TopoDS_Compound, TopoDS_CompSolid)
for _cls in (TopoDS_Shape, TopoDS_Face, TopoDS_Edge, TopoDS_Vertex,
             TopoDS_Wire, TopoDS_Shell, TopoDS_Solid, TopoDS_Compound, TopoDS_CompSolid):
    if not hasattr(_cls, "HashCode"):
        _cls.HashCode = lambda self, ub=2147483647: id(self) % ub
def show_object(*a, **k): pass
"""


def _run_program(patched: str, timeout: int) -> None:
    """Run the patched program in a fresh interpreter; raise on any failure."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(patched)
        tmp = f.name
    try:
        r = subprocess.run(
            [sys.executable, tmp],
            env=os.environ.copy(),
            timeout=timeout,
            capture_output=True,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"timeout after {timeout}s") from e
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    if r.returncode != 0:
        err = r.stderr.decode(errors="replace").strip().splitlines()[-1:] or ["unknown error"]
        raise RuntimeError(err[0][:300])


def execute_cq_to_step(code: str, step_path: Path, timeout: int = 300) -> None:
    """Execute `code` so `result` is exported to `step_path`. Raises on failure."""
    step_path.parent.mkdir(parents=True, exist_ok=True)
    if step_path.exists():
        step_path.unlink()
    out_lit = str(step_path).replace("\\", "\\\\")
    # `result` may be a Workplane, a bare Shape/Compound, or a cq.Assembly
    # (multi-body families). Normalize all three to a Shape before exporting:
    # an Assembly has no .val()/.exportStep(), so fold it to a compound first.
    export_tail = (
        "\n_r = result\n"
        "try:\n"
        "    import cadquery as _cq\n"
        "    if isinstance(_r, _cq.Assembly):\n"
        "        _r = _r.toCompound()\n"
        "except Exception:\n"
        "    pass\n"
        "if hasattr(_r, 'val'):\n"
        "    _r = _r.val()\n"
        f'_r.exportStep("{out_lit}")\n'
    )
    _run_program(_OCP_HASHCODE_FIX + "\n" + code + export_tail, timeout)
    if not step_path.exists():
        raise RuntimeError("subprocess succeeded but no STEP file written")


# Folding an Assembly to a compound (the STEP path above) erases component
# names and hierarchy. This tail keeps them: walk the Assembly exactly like
# cq's toCompound() (world location = the product of every ancestor's loc),
# export each shape-bearing node's RAW local shape to its own STEP, and record
# the node name + absolute 3x4 world transform in manifest.json. The parent
# process re-applies the transforms to the meshes, so the full assembly pose
# survives without parsing STEP product structure.
_PARTS_EXPORT_TAIL = """
_r = result
import json as _json
import cadquery as _cq
_out = "__OUTDIR__"
_leaves = []
if isinstance(_r, _cq.Assembly):
    def _walk(node, parent_loc):
        world = parent_loc * node.loc
        shapes = list(node.shapes)
        if shapes:
            shape = shapes[0] if len(shapes) == 1 else _cq.Compound.makeCompound(shapes)
            _leaves.append((node.name, shape, world))
        for child in node.children:
            _walk(child, world)
    _walk(_r, _cq.Location())
_entries = []
for _i, (_name, _shape, _world) in enumerate(_leaves):
    _shape.exportStep(f"{_out}/leaf_{_i:03d}.step")
    _t = _world.wrapped.Transformation()
    _entries.append({
        "name": _name,
        "step": f"leaf_{_i:03d}.step",
        "world_transform": [[_t.Value(_row, _col) for _col in range(1, 5)]
                            for _row in range(1, 4)],
    })
_manifest = {"is_assembly": isinstance(_r, _cq.Assembly),
             "result_type": type(_r).__name__, "leaves": _entries}
with open(f"{_out}/manifest.json", "w") as _f:
    _json.dump(_manifest, _f)
"""


def execute_cq_to_parts(code: str, out_dir: Path, timeout: int = 300) -> dict:
    """Execute `code` and export `result`'s assembly structure into `out_dir`.

    Returns the manifest dict: `is_assembly`, `result_type`, and `leaves` —
    one entry per shape-bearing Assembly node with its `name`, local-shape
    `step` filename, and absolute `world_transform` (3x4 row-major). When
    `result` is not a cq.Assembly, `is_assembly` is False and no STEP is
    written — the caller decides whether that is an error."""
    import json

    out_dir.mkdir(parents=True, exist_ok=True)
    out_lit = str(out_dir).replace("\\", "\\\\")
    tail = _PARTS_EXPORT_TAIL.replace("__OUTDIR__", out_lit)
    _run_program(_OCP_HASHCODE_FIX + "\n" + code + tail, timeout)
    manifest = out_dir / "manifest.json"
    if not manifest.exists():
        raise RuntimeError("subprocess succeeded but no manifest.json written")
    return json.loads(manifest.read_text())
