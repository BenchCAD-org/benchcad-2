"""Reproducible component previews for named-Assembly families.

The normal STEP path folds a cq.Assembly into a compound, so component names
and hierarchy never reach the renderer. This module re-executes the DERIVED
stand-alone program — the same artifact every other preview renders — with an
export harness that keeps the tree (`execute_cq_to_parts`): one STEP per
shape-bearing node plus its absolute world transform. The meshes then render
as separate VTK actors sharing one normalized frame, so `preview_parts.png`
shows, deterministically for hard / seed 0:

  - one four-view row per semantic component (its own frame, catalog-style),
  - the complete assembly in its true pose,
  - one red-on-gray highlight row per component, in family.json order
    (repeated instances together by default; `per_instance` splits them).

Naming contract (validated against family.json `components`): every
shape-bearing Assembly node is named either exactly after its component
(quantity 1) or `<component>_<NN>` for repeated instances; semantically
distinct components stay separate even when their geometry matches.
"""

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

import numpy as np

_INSTANCE_SUFFIX = re.compile(r"_(\d+)$")


def param_caption(spec, p) -> str:
    """Compact `name=value` summary of the meaningful params (~2 per line) for a
    preview row label — lets a reviewer map the rendered part to its numbers and
    to the source drawing. Covers askable dimensions plus feature params so
    every relevant catalog symbol is legible."""
    parts = [f"{k}={p[k]}" for k, e in spec.PARAM_SPEC.items()
             if (e.get("askable") or e.get("feature")) and k in p]
    return "\n".join(", ".join(parts[i:i + 2]) for i in range(0, len(parts), 2))


def component_contract(meta: dict) -> list[tuple[str, int]]:
    """family.json `components` as ordered (name, quantity) pairs, validated:
    non-empty unique names, positive integer quantities, and `solids` equal to
    the quantity sum (so the body-count gate and the component contract can
    never drift apart)."""
    entries = meta.get("components")
    if not isinstance(entries, list) or not entries:
        raise ValueError(
            "family.json: an assembly family must declare `components`, e.g. "
            '"components": [{"name": "body", "quantity": 1}, {"name": "bolt", "quantity": 2}]'
        )
    contract: list[tuple[str, int]] = []
    for entry in entries:
        name = entry.get("name") if isinstance(entry, dict) else None
        quantity = entry.get("quantity") if isinstance(entry, dict) else None
        if not isinstance(name, str) or not name:
            raise ValueError("family.json components: every entry needs a non-empty string `name`")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise ValueError(
                f"family.json components: {name!r} needs a positive integer `quantity`"
            )
        contract.append((name, quantity))
    names = [name for name, _ in contract]
    if len(names) != len(set(names)):
        dupes = sorted({n for n in names if names.count(n) > 1})
        raise ValueError(f"family.json components: duplicate component name(s) {dupes}")
    total = sum(quantity for _, quantity in contract)
    if meta.get("solids") != total:
        raise ValueError(
            f"family.json: `solids` must be declared and equal the components quantity "
            f"sum ({total}); found {meta.get('solids')!r}"
        )
    return contract


def classify_instance(instance: str, component_names: list[str]) -> str:
    """Map an Assembly node name to its semantic component.

    Precedence: an exact declared name first (so a component literally named
    `plate_2` wins over `plate` + instance 2), then `<component>_<digits>` for
    repeated instances. Any other name fails — an undeclared prefix
    (`bolt_left` with only `bolt` declared) is a distinct semantic component
    and must be declared as such."""
    if instance in component_names:
        return instance
    m = _INSTANCE_SUFFIX.search(instance)
    if m and instance[: m.start()] in component_names:
        return instance[: m.start()]
    raise ValueError(
        f"Assembly instance {instance!r} matches no family.json component "
        f"(declared: {component_names}): name every shape-bearing node exactly after "
        "its component, or `<component>_<NN>` for repeated instances"
    )


def group_instances(leaves: list[dict], contract: list[tuple[str, int]]) -> dict[str, list[int]]:
    """component name -> leaf indices (assembly tree order); fails clearly when
    instance names are not unique, match no component, or quantities drift
    from the declared contract."""
    instance_names = [leaf["name"] for leaf in leaves]
    if len(instance_names) != len(set(instance_names)):
        dupes = sorted({n for n in instance_names if instance_names.count(n) > 1})
        raise ValueError(
            f"Assembly instance name(s) {dupes} are not unique — every shape-bearing "
            "node needs its own stable name"
        )
    component_names = [name for name, _ in contract]
    groups: dict[str, list[int]] = {name: [] for name in component_names}
    for index, leaf in enumerate(leaves):
        groups[classify_instance(leaf["name"], component_names)].append(index)
    drift = [
        f"{name}: declared {quantity}, built {len(groups[name])}"
        for name, quantity in contract
        if len(groups[name]) != quantity
    ]
    if drift:
        raise ValueError(
            "Assembly does not match family.json components (" + "; ".join(drift) + ")"
        )
    return groups


def _normalized(verts_list: list[np.ndarray]) -> list[np.ndarray]:
    """One shared normalization (bbox center 0.5, longest axis 1) across every
    array — the frame render_iso expects, applied jointly so the assembly keeps
    its true relative placement."""
    combined = np.concatenate(verts_list, axis=0)
    lo, hi = combined.min(axis=0), combined.max(axis=0)
    longest = float((hi - lo).max())
    if longest < 1e-9:
        raise ValueError("degenerate geometry (zero extent)")
    center = (lo + hi) / 2.0
    return [(verts - center) / longest + 0.5 for verts in verts_list]


def build_preview_parts(fam_dir: Path, per_instance: bool = False,
                        required: bool = True) -> Path | None:
    """Render designs/<family>/preview_parts.png for the deterministic
    hard / seed 0 instance. With required=False (the `bench2 preview`
    auto-detect path) a non-Assembly `result` returns None instead of failing;
    every contract violation still fails clearly rather than producing a
    misleading image."""
    from . import render
    from .derive import derive_program
    from .execute import execute_cq_to_parts
    from .loader import load_family
    from .sampling import sample as sample_params

    part, spec = load_family(fam_dir)
    p = sample_params(spec, "hard", np.random.default_rng(0))
    meta = json.loads((fam_dir / "family.json").read_text())

    local_meshes, world_meshes, leaves = [], [], []
    with tempfile.TemporaryDirectory() as td:
        manifest = execute_cq_to_parts(derive_program(part, p), Path(td))
        if not manifest["is_assembly"]:
            if not required:
                return None
            raise ValueError(
                f"build() returned {manifest['result_type']}, not a named cq.Assembly — "
                "preview-parts is for assembly families (single-part families use "
                "`bench2 preview`)"
            )
        contract = component_contract(meta)
        leaves = manifest["leaves"]
        groups = group_instances(leaves, contract)
        for leaf in leaves:
            verts, tris = render.step_to_mesh(Path(td) / leaf["step"])
            m = np.array(leaf["world_transform"], dtype=np.float64)
            local_meshes.append((verts, tris))
            world_meshes.append((verts @ m[:, :3].T + m[:, 3], tris))

    rows, labels = [], []
    # one catalog-style row per semantic component: the first instance's RAW
    # local shape, normalized alone, in the four benchmark views
    for name, quantity in contract:
        verts, tris = local_meshes[groups[name][0]]
        dx, dy, dz = (verts.max(axis=0) - verts.min(axis=0)).tolist()
        rows.append(render.render_bench_views(_normalized([verts])[0], tris))
        labels.append(f"{name}\nquantity={quantity}\nbbox {dx:.1f} x {dy:.1f} x {dz:.1f} mm")

    # the complete assembly and the highlight rows share ONE normalized frame,
    # so every row shows the identical pose and scale
    shared = _normalized([verts for verts, _ in world_meshes])
    posed = list(zip(shared, [tris for _, tris in world_meshes]))
    assembly_actors = [(verts, tris, render.TEAL_STYLE) for verts, tris in posed]
    rows.append([render.render_actors(assembly_actors, front=f) for f in render.BENCH_FRONTS])
    labels.append(f"assembly overview\nhard / seed 0\n{param_caption(spec, p)}")

    if per_instance:
        highlight_rows = [
            (leaves[index]["name"], {index}, f"component={name}")
            for name, _ in contract
            for index in groups[name]
        ]
    else:
        highlight_rows = [
            (name, set(groups[name]), f"quantity={quantity}")
            for name, quantity in contract
        ]
    for row_no, (label, indices, detail) in enumerate(highlight_rows, start=1):
        actors = [
            (verts, tris, render.HIGHLIGHT_STYLE if i in indices else render.DIMMED_STYLE)
            for i, (verts, tris) in enumerate(posed)
        ]
        rows.append([render.render_actors(actors, front=f) for f in render.BENCH_FRONTS])
        labels.append(f"{row_no}. {label} highlighted\n{detail}\nassembly stays in place")

    out = fam_dir / "preview_parts.png"
    render.compose_grid(rows, labels, out)
    return out
