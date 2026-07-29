"""Reproducible component previews for named CadQuery assemblies."""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class AssemblyLeaf:
    """One named physical instance, before and after Assembly locations."""

    instance_name: str
    component_name: str
    local_shape: object
    world_shape: object


def _component_contract(fam_dir: Path) -> list[tuple[str, int]]:
    meta = json.loads((fam_dir / "family.json").read_text(encoding="utf-8"))
    entries = meta.get("components")
    if not isinstance(entries, list) or not entries:
        raise ValueError("family.json must declare a non-empty components list")

    contract: list[tuple[str, int]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each family.json components entry must be an object")
        name, quantity = entry.get("name"), entry.get("quantity")
        if not isinstance(name, str) or not name:
            raise ValueError("each component must have a non-empty string name")
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
            raise ValueError(f"component {name!r} quantity must be a positive integer")
        contract.append((name, quantity))

    names = [name for name, _ in contract]
    if len(names) != len(set(names)):
        raise ValueError("family.json component names must be unique")
    declared_solids = meta.get("solids")
    if declared_solids is not None and declared_solids != sum(q for _, q in contract):
        raise ValueError(
            "family.json solids must equal the sum of components[].quantity "
            f"({declared_solids} != {sum(q for _, q in contract)})"
        )
    return contract


def _node_shape(node):
    import cadquery as cq

    shapes = list(node.shapes)
    if not shapes:
        return None
    if len(shapes) == 1:
        return shapes[0]
    return cq.Compound.makeCompound(shapes)


def _raw_leaves(assembly) -> list[tuple[str, object, object]]:
    """Return ``(instance_name, local_shape, world_shape)`` in tree order."""
    import cadquery as cq

    if not isinstance(assembly, cq.Assembly):
        raise TypeError("part.build(**params) must return a named cq.Assembly")

    leaves: list[tuple[str, object, object]] = []

    def visit(node, parent_location):
        world_location = parent_location * node.loc
        shape = _node_shape(node)
        if shape is not None:
            leaves.append((node.name, shape, shape.located(world_location)))
        for child in node.children:
            visit(child, world_location)

    visit(assembly, cq.Location())
    if not leaves:
        raise ValueError("Assembly contains no shape-bearing named nodes")
    names = [name for name, _, _ in leaves]
    if len(names) != len(set(names)):
        raise ValueError("Assembly leaf instance names must be unique")
    return leaves


def _component_for_instance(instance_name: str, component_names: list[str]) -> str:
    if instance_name in component_names:
        return instance_name
    matches = [name for name in component_names if instance_name.startswith(f"{name}_")]
    if matches:
        return max(matches, key=len)
    raise ValueError(
        f"Assembly instance {instance_name!r} does not match any family.json component; "
        "use the exact component name or '<component>_<stable suffix>'"
    )


def assembly_leaves(assembly, contract: list[tuple[str, int]]) -> list[AssemblyLeaf]:
    """Validate and classify Assembly instances against family metadata."""
    component_names = [name for name, _ in contract]
    leaves = [
        AssemblyLeaf(
            instance_name=name,
            component_name=_component_for_instance(name, component_names),
            local_shape=local,
            world_shape=world,
        )
        for name, local, world in _raw_leaves(assembly)
    ]
    actual = {
        name: sum(leaf.component_name == name for leaf in leaves)
        for name in component_names
    }
    expected = dict(contract)
    if actual != expected:
        details = ", ".join(
            f"{name}: expected {expected[name]}, found {actual[name]}" for name in component_names
        )
        raise ValueError(f"Assembly component quantities do not match family.json ({details})")
    return leaves


def _shape_mesh(shape):
    from . import render

    render._ocp_hashcode_fix()
    vertices, triangles = shape.tessellate(0.05)
    verts = np.array([[v.x, v.y, v.z] for v in vertices], dtype=np.float64)
    tris = np.array([[t[0], t[1], t[2]] for t in triangles], dtype=np.int64)
    if len(verts) == 0 or len(tris) == 0:
        raise ValueError("Assembly component produced an empty mesh")
    return verts, tris


def _normalized_single_mesh(shape):
    verts, tris = _shape_mesh(shape)
    lo, hi = verts.min(axis=0), verts.max(axis=0)
    longest = float((hi - lo).max())
    if longest < 1e-9:
        raise ValueError("Assembly component has zero extent")
    return (verts - (lo + hi) / 2.0) / longest + 0.5, tris


def _normalized_world_meshes(leaves: list[AssemblyLeaf]):
    raw = [(leaf.instance_name, *_shape_mesh(leaf.world_shape)) for leaf in leaves]
    combined = np.concatenate([verts for _, verts, _ in raw], axis=0)
    lo, hi = combined.min(axis=0), combined.max(axis=0)
    longest = float((hi - lo).max())
    if longest < 1e-9:
        raise ValueError("Assembly has zero extent")
    center = (lo + hi) / 2.0
    return {
        name: ((verts - center) / longest + 0.5, tris)
        for name, verts, tris in raw
    }


def _call_build(part, params: dict):
    """Call build with its declared arguments, ignoring spec-only metadata."""
    build_names = inspect.signature(part.build).parameters
    return part.build(**{name: params[name] for name in build_names})


def _highlight_groups(
    leaves: list[AssemblyLeaf],
    contract: list[tuple[str, int]],
    per_instance: bool,
) -> list[tuple[str, set[str], str, int]]:
    """Stable highlight rows: metadata order, then Assembly tree order."""
    if per_instance:
        return [
            (leaf.instance_name, {leaf.instance_name}, leaf.component_name, 1)
            for component_name, _ in contract
            for leaf in leaves
            if leaf.component_name == component_name
        ]
    return [
        (
            component_name,
            {
                leaf.instance_name
                for leaf in leaves
                if leaf.component_name == component_name
            },
            component_name,
            quantity,
        )
        for component_name, quantity in contract
    ]


def build_preview_parts(
    fam_dir: Path,
    *,
    difficulty: str = "hard",
    seed: int = 0,
    per_instance: bool = False,
    required: bool = True,
) -> Path | None:
    """Render ``preview_parts.png`` for one deterministic Assembly instance."""
    import cadquery as cq

    from . import render
    from .loader import load_family
    from .sampling import sample as sample_params

    part, spec = load_family(fam_dir)
    params = sample_params(spec, difficulty, np.random.default_rng(seed))
    # Direct in-process builds need the same CadQuery 2.3 / OCP 7.9 shim that
    # execute_cq_to_step installs in its subprocess, and it must exist before
    # selectors such as .edges() call Shape.hashCode().
    render._ocp_hashcode_fix()
    assembly = _call_build(part, params)
    if not isinstance(assembly, cq.Assembly):
        if required:
            raise TypeError("preview-parts requires part.build(**params) to return cq.Assembly")
        return None

    contract = _component_contract(fam_dir)
    leaves = assembly_leaves(assembly, contract)
    rows, labels = [], []
    for component_name, quantity in contract:
        representative = next(leaf for leaf in leaves if leaf.component_name == component_name)
        verts, tris = _normalized_single_mesh(representative.local_shape)
        rows.append(render.render_bench_views(verts, tris, img_size=260))
        labels.append(f"{component_name}\nquantity={quantity}\nfour standard views")

    world_meshes = _normalized_world_meshes(leaves)
    rows.append(render.render_multi_mesh_views(world_meshes, img_size=260))
    labels.append(
        f"assembly overview\n{difficulty} / seed {seed}\n{len(leaves)} named instances"
    )

    highlights = _highlight_groups(leaves, contract, per_instance)

    for index, (label_name, names, component_name, quantity) in enumerate(highlights, start=1):
        rows.append(
            render.render_multi_mesh_views(
                world_meshes,
                highlighted=names,
                img_size=260,
            )
        )
        suffix = (
            f"component={component_name}\ninstance highlight"
            if per_instance
            else f"quantity={quantity}\ngroup highlight"
        )
        labels.append(f"{index}. {label_name}\n{suffix}")

    out = fam_dir / "preview_parts.png"
    render.compose_grid(rows, labels, out, cell=260, label_w=300)
    return out
