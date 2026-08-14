"""bench2 anchor — turn a reference into a numeric acceptance target.

A family reproduces a real catalog row. Checking that today means putting a
render next to a drawing and trusting two pairs of eyes, which is exactly the
review an orientation error survives: a section built 18 tall x 12.75 deep when
the drawing says 12.75 tall x 18 deep looks like the part from every angle.

`bench2 anchor` makes the measurable part machine-checkable. It records what
the reference *is* — envelope, volume, body count, and the cylindrical faces
(every hole, bore and boss) with their radii and axes — as
`designs/<family>/anchor.json`. `bench2 validate --anchor` then builds the
family at that same catalog row through the normal derive -> execute -> STEP
path, measures the result with the identical function, and diffs the two.

Two kinds of reference, because vendors differ in what they publish:

* **STEP** — a reference solid is measured directly. The target is exhaustive,
  so a hole the model invents is a failure too.
* **drawing** — the numbers are read off a dimensioned sheet. The target covers
  the envelope and the callouts and nothing else; whatever the sheet does not
  dimension simply goes unchecked. Whole categories of catalog hardware ship a
  dimensioned sheet and no neutral CAD at all, and an envelope-plus-callouts
  target still catches the errors that survive human review.

Either way only the measurement is recorded. A reference file is read, never
copied into the repo: `anchor.json` holds numbers, which is what review needs
and what stays meaningful after the reference is gone.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from .execute import _OCP_HASHCODE_FIX, _run_program

SCHEMA = 1
ANCHOR_FILE = "anchor.json"

# Chosen so a faithful family passes and a wrong one does not: 1% of a 35 mm
# envelope is 0.35 mm, tighter than any drawing tolerance that matters at review
# scale, while volume absorbs the sub-mm detail a parametric model legitimately
# simplifies away (chamfer breaks, cast radii, knurl).
DEFAULT_TOL = {"bbox_pct": 1.0, "volume_pct": 3.0, "radius_mm": 0.15}

_MEASURE = '''
import json
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

shape = cq.importers.importStep("__STEP__").val()


def _canon(v):
    """A cylinder axis is the same line whichever way it points, so pin the
    first non-zero component positive and the two directions collapse."""
    v = [0.0 if abs(c) < 1e-9 else c for c in v]
    for c in v:
        if c:
            if c < 0:
                v = [-x for x in v]
            break
    return [round(c, 3) for c in v]


faces = shape.Faces()
types, cyl = {}, {}
for f in faces:
    t = f.geomType()
    types[t] = types.get(t, 0) + 1
    if t != "CYLINDER":
        continue
    ad = BRepAdaptor_Surface(f.wrapped).Cylinder()
    d = ad.Axis().Direction()
    key = (round(ad.Radius(), 3), tuple(_canon([d.X(), d.Y(), d.Z()])))
    e = cyl.setdefault(key, {"r": key[0], "axis": list(key[1]), "count": 0, "area_mm2": 0.0})
    e["count"] += 1
    e["area_mm2"] += f.Area()

bb, c = shape.BoundingBox(), shape.Center()
out = {
    "kind": "step",
    "bbox_mm": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
    "volume_mm3": round(shape.Volume(), 3),
    "area_mm2": round(shape.Area(), 3),
    "centroid_mm": [round(c.x, 3), round(c.y, 3), round(c.z, 3)],
    "solids": len(shape.Solids()),
    "faces": len(faces),
    "face_types": dict(sorted(types.items())),
    "cylinders": sorted(
        ({**e, "area_mm2": round(e["area_mm2"], 3)} for e in cyl.values()),
        key=lambda e: (-e["r"], e["axis"]),
    ),
}
with open("__OUT__", "w") as fh:
    json.dump(out, fh)
'''


def measure(step_path: Path, timeout: int = 300) -> dict:
    """Measure a STEP solid, in a subprocess under the OCP shim like every other
    geometry path here, so reference and family are measured by the same code."""
    step_path = Path(step_path)
    if not step_path.is_file():
        raise RuntimeError(f"no such STEP file: {step_path}")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "measured.json"
        code = (_MEASURE.replace("__STEP__", str(step_path).replace("\\", "\\\\"))
                        .replace("__OUT__", str(out).replace("\\", "\\\\")))
        _run_program(_OCP_HASHCODE_FIX + code, timeout)
        if not out.exists():
            raise RuntimeError("measurement subprocess wrote no result")
        return json.loads(out.read_text())


def measure_family(fam_dir: Path, params: dict, timeout: int = 300) -> dict:
    """Measure what the family produces at `params` — through the derived
    stand-alone program, not by calling build() in process, so the thing
    measured is the thing the benchmark ships."""
    from .derive import derive_program
    from .execute import execute_cq_to_step
    from .loader import load_family

    part, _spec = load_family(fam_dir)
    with tempfile.TemporaryDirectory() as td:
        step = Path(td) / "built.step"
        execute_cq_to_step(derive_program(part, params), step, timeout=timeout)
        return measure(step, timeout=timeout)


# --- comparison ------------------------------------------------------------

_AXES = {"x": 0, "y": 1, "z": 2}


def _permute(triple, align: str):
    """Map a reference triple into the family's frame. `align` names, for each
    of our axes in order, the reference axis it corresponds to: "xzy" means our
    Y is the reference's Z. It is declared once per family and then held fixed
    — never fitted, because auto-fitting would silently absorb exactly the
    axis-swap errors this gate exists to catch."""
    return [triple[_AXES[a]] for a in align]


def _pct(built, ref):
    if ref == 0:
        return 0.0 if built == 0 else float("inf")
    return abs(built - ref) / abs(ref) * 100.0


def compare(ref: dict, built: dict, align: str = "xyz", tol: dict | None = None) -> list:
    """Diff a reference against a built measurement. Returns rows of
    (ok, quantity, reference, built, delta) — the table that goes in the PR body.

    The reference declares what it knows and only that is checked."""
    tol = {**DEFAULT_TOL, **(tol or {})}
    rows = []

    for axis, r, b in zip("XYZ", _permute(ref.get("bbox_mm") or [None] * 3, align),
                          built["bbox_mm"]):
        if r is None:  # a drawing may dimension only part of the envelope
            continue
        d = _pct(b, r)
        rows.append((d <= tol["bbox_pct"], f"bbox {axis} (mm)", r, b, f"{d:.2f}%"))

    if ref.get("volume_mm3") is not None:
        d = _pct(built["volume_mm3"], ref["volume_mm3"])
        rows.append((d <= tol["volume_pct"], "volume (mm³)",
                     ref["volume_mm3"], built["volume_mm3"], f"{d:.2f}%"))

    if ref.get("solids") is not None:
        rows.append((built["solids"] == ref["solids"], "solids",
                     ref["solids"], built["solids"], "—"))

    # Cylindrical faces = the hole/bore/boss set. Match on radius (a hole is the
    # same hole wherever it sits) and report what is missing: a wrong drill size
    # or a dropped counterbore shows up here, never in the envelope.
    remaining = [dict(e) for e in built["cylinders"]]
    for e in ref.get("cylinders") or []:
        exact = [c for c in remaining
                 if abs(c["r"] - e["r"]) <= tol["radius_mm"] and c["count"] == e["count"]]
        near = [c for c in remaining if abs(c["r"] - e["r"]) <= tol["radius_mm"]]
        hit = (exact or near or [None])[0]
        label = f"cyl r={e['r']} ×{e['count']}" + (f" ({e['note']})" if e.get("note") else "")
        if hit is None:
            rows.append((False, label, f"r={e['r']} ×{e['count']}", "missing", "—"))
        else:
            remaining.remove(hit)
            rows.append((hit["count"] == e["count"], label, f"r={e['r']} ×{e['count']}",
                         f"r={hit['r']} ×{hit['count']}", f"Δr={abs(hit['r'] - e['r']):.3f}"))

    # A STEP reference is exhaustive, so a leftover is a real defect. A drawing
    # reference is not: it calls out the features worth dimensioning and the
    # model legitimately has more. Only report extras when the reference is
    # complete.
    if ref.get("kind", "step") == "step":
        for extra in remaining:
            rows.append((False, f"cyl r={extra['r']} ×{extra['count']}", "—",
                         f"r={extra['r']} ×{extra['count']}", "unexpected"))
    return rows


def markdown_table(rows: list) -> str:
    out = ["| | quantity | reference | built | delta |", "|---|---|---|---|---|"]
    for ok, q, r, b, d in rows:
        out.append(f"| {'✓' if ok else '✗'} | {q} | {r} | {b} | {d} |")
    return "\n".join(out)


# --- anchor.json -----------------------------------------------------------


def load(fam_dir: Path) -> dict | None:
    p = Path(fam_dir) / ANCHOR_FILE
    return json.loads(p.read_text()) if p.is_file() else None


def write(fam_dir: Path, anchor: dict) -> Path:
    p = Path(fam_dir) / ANCHOR_FILE
    p.write_text(json.dumps(anchor, indent=1) + "\n")
    return p


def _head(params, designation, source, align, tol):
    if sorted(align) != ["x", "y", "z"]:
        raise RuntimeError(f"align must be a permutation of xyz, got {align!r}")
    return {
        "schema": SCHEMA,
        "designation": designation,
        "source": source,
        "align": align,
        "params": params,
        "tolerance": {**DEFAULT_TOL, **(tol or {})},
    }


def create(step_path: Path, params: dict, designation: str, source: str,
           align: str = "xyz", tol: dict | None = None) -> dict:
    """Acceptance target measured from a reference solid. The STEP is read, not
    copied — only the measurement is kept."""
    return {**_head(params, designation, source, align, tol), "reference": measure(step_path)}


def create_from_drawing(dims: dict, params: dict, designation: str, source: str,
                        align: str = "xyz", tol: dict | None = None) -> dict:
    """Acceptance target read off a dimensioned drawing.

    `dims` carries what the sheet actually dimensions: `bbox_mm` (None for an
    axis it leaves open) and `cylinders` as `[{"r":…, "axis":[…], "count":…,
    "note":…}]` from its ø callouts. Volume and body count are normally unknown
    and go unchecked."""
    ref = {
        "kind": "drawing",
        "bbox_mm": dims.get("bbox_mm"),
        "cylinders": sorted(
            ({"r": float(c["r"]), "axis": list(c.get("axis", [0, 0, 1])),
              "count": int(c.get("count", 1)), "note": c.get("note", "")}
             for c in dims.get("cylinders", [])),
            key=lambda e: (-e["r"], e["axis"]),
        ),
    }
    for key in ("volume_mm3", "solids"):
        if dims.get(key) is not None:
            ref[key] = dims[key]
    return {**_head(params, designation, source, align, tol), "reference": ref}


def check(fam_dir: Path) -> tuple[bool, list]:
    """Rebuild the family at its anchor row and diff against anchor.json."""
    anchor = load(fam_dir)
    if anchor is None:
        raise RuntimeError(f"no {ANCHOR_FILE} in {fam_dir}")
    built = measure_family(fam_dir, anchor["params"])
    rows = compare(anchor["reference"], built, anchor.get("align", "xyz"), anchor.get("tolerance"))
    return all(r[0] for r in rows), rows
