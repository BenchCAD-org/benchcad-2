"""Derive a stand-alone CadQuery program from a named-parameter `build()`.

The contributor writes an ordinary parametric part in `part.py` — named
arguments, no dictionaries, no code generation:

    import cadquery as cq
    def _outline(width, height):
        return [(-width / 2, -height / 2), (width / 2, -height / 2),
                (width / 2, height / 2), (-width / 2, height / 2)]

    def build(width, height, thickness):
        result = cq.Workplane("XY").polyline(_outline(width, height)).close().extrude(thickness)
        return result

For a concrete instance we DERIVE the stand-alone source a model is asked to
produce (style B — flat variables). build()'s parameters become module globals
bound to this instance's values; every helper the body calls travels with it,
inlined:

    import cadquery as cq
    def _outline(width, height):
        return [(-width / 2, -height / 2), (width / 2, -height / 2),
                (width / 2, height / 2), (-width / 2, height / 2)]

    # parameters (this instance)
    height = 40.0
    thickness = 8.0
    width = 80.0

    result = cq.Workplane("XY").polyline(_outline(width, height)).close().extrude(thickness)

The derivation is a pure text transform: same params in => byte-identical
program out. Because the emitted body IS build()'s body with the arguments
bound as globals, executing the derived program is equivalent to calling
build(**params) — the machine guarantees the final coding is consistent, and
the contributor never writes a code generator.
"""

from __future__ import annotations

import ast
import builtins
import inspect
import textwrap

_BUILTINS = set(dir(builtins))


def _func_body_source(func) -> str:
    """The body of `func` as source text (docstring + trailing `return`
    stripped), dedented to column 0, comments preserved."""
    src = textwrap.dedent(inspect.getsource(func))
    fn = ast.parse(src).body[0]
    stmts = list(fn.body)
    if (
        stmts
        and isinstance(stmts[0], ast.Expr)
        and isinstance(stmts[0].value, ast.Constant)
        and isinstance(stmts[0].value.value, str)
    ):
        stmts = stmts[1:]  # drop docstring
    if stmts and isinstance(stmts[-1], ast.Return):
        stmts = stmts[:-1]  # drop `return result`
    if not stmts:
        return ""
    lines = src.splitlines()
    start, end = stmts[0].lineno, stmts[-1].end_lineno
    return textwrap.dedent("\n".join(lines[start - 1 : end])).rstrip()


def _free_names(code_text: str) -> set[str]:
    """Names read but not bound in `code_text` (a module-level snippet)."""
    tree = ast.parse(code_text)
    bound, loaded = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            (bound if isinstance(node.ctx, ast.Store) else loaded).add(node.id)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
    return loaded - bound - _BUILTINS


def _collect(name, part, acc, seen):
    """Recursively gather what a free `name` needs to become stand-alone."""
    if name in seen or name in acc["params"]:
        return
    seen.add(name)
    val = getattr(part, name, None)
    if inspect.ismodule(val):
        acc["imports"][name] = val.__name__
    elif inspect.isfunction(val):
        fsrc = textwrap.dedent(inspect.getsource(val)).rstrip()
        acc["funcs"][name] = fsrc
        for dep in _free_names(fsrc):
            _collect(dep, part, acc, seen)
    elif val is not None:  # a module-level constant (table/number/str)
        acc["consts"][name] = f"{name} = {val!r}"
    # else: unknown free name (bound elsewhere in the body, or a builtin miss)


def derive_program(part, params: dict) -> str:
    """Return the stand-alone CadQuery source for one instance of `part`."""
    build = part.build
    body = _func_body_source(build)
    free = _free_names(body)
    argnames = set(inspect.signature(build).parameters)

    acc = {"imports": {}, "consts": {}, "funcs": {}, "params": {}}
    # build()'s parameters become this instance's flat variables
    for name in sorted(free & argnames):
        acc["params"][name] = params[name]
    seen = set(acc["params"])
    # everything else the body reads travels with it: imports, helpers, consts
    for name in sorted(free - argnames):
        _collect(name, part, acc, seen)

    out: list[str] = []
    for alias in sorted(acc["imports"]):
        mod = acc["imports"][alias]
        out.append(f"import {mod}" if mod == alias else f"import {mod} as {alias}")
    out.append("")
    if acc["consts"]:
        for name in sorted(acc["consts"]):
            out.append(acc["consts"][name])
        out.append("")
    for name in sorted(acc["funcs"]):
        out.append(acc["funcs"][name])
        out.append("")
        out.append("")
    if acc["params"]:
        out.append("# parameters (this instance)")
        for name in sorted(acc["params"]):
            out.append(f"{name} = {acc['params'][name]!r}")
        out.append("")
    out.append(body)
    return "\n".join(out).rstrip() + "\n"


def declared_helpers(part, params: dict) -> set[str]:
    """geomlib helper names the derived program actually inlines (for the
    validate cross-check against family.json)."""
    build = part.build
    body = _func_body_source(build)
    free = _free_names(body)
    argnames = set(inspect.signature(build).parameters)
    acc = {"imports": {}, "consts": {}, "funcs": {}, "params": {}}
    seen = set(free & argnames)
    for name in sorted(free - argnames):
        _collect(name, part, acc, seen)
    return set(acc["funcs"])
