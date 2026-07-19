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
    patched = _OCP_HASHCODE_FIX + "\n" + code + export_tail
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
    if not step_path.exists():
        raise RuntimeError("subprocess succeeded but no STEP file written")
