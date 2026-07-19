"""Machine gates for a contributed family — the same checks CI runs.

Gates (see docs/DESIGN_SPEC.md):
  1. family.json present, required keys, valid base_plane
  2. part.py exposes build(); spec.py exposes PARAM_SPEC + check(); every
     build() parameter is declared in PARAM_SPEC
  3. per difficulty x N seeds: the framework sampler draws params that pass
     check(); the DERIVED stand-alone program (derive.py) binds `result` and
     executes to a non-degenerate solid
  4. determinism: same seed => byte-identical derived program
  5. difficulty separation: the three difficulties aren't all identical
  6. geometry-hash duplicate report within the sampled batch
"""

from __future__ import annotations

import hashlib
import inspect
import json
import tempfile
from pathlib import Path

from .derive import derive_program
from .loader import load_family
from .sampling import sample as sample_params

DIFFS = ("easy", "medium", "hard")
FAMILY_KEYS = ("family", "standard", "base_plane", "description", "contributor")
BASE_PLANES = {"XY", "XZ", "YZ"}
SPEC_REQUIRED = ("desc", "unit", "range", "source")


def _geom_hash(step_path: Path) -> str:
    from . import render

    verts, tris = render.step_to_normalized_mesh(step_path)  # raises if degenerate
    h = hashlib.sha256()
    h.update(verts.round(3).tobytes())
    h.update(tris.tobytes())
    return h.hexdigest()[:16]


def validate_family(fam_dir: Path, seeds: int = 4, geometry: bool = True):
    """Returns (ok, log) where log is a list of (passed, message)."""
    import numpy as np

    log: list[tuple[bool, str]] = []

    def ok(msg):
        log.append((True, msg))

    def bad(msg):
        log.append((False, msg))

    # -- 1. family.json ------------------------------------------------------
    fj = fam_dir / "family.json"
    if not fj.exists():
        bad("family.json: missing")
        return False, log
    meta = json.loads(fj.read_text())
    missing = [k for k in FAMILY_KEYS if k not in meta]
    if missing:
        bad(f"family.json: missing keys {missing}")
    elif meta["base_plane"] not in BASE_PLANES:
        bad(f"family.json: base_plane must be one of {sorted(BASE_PLANES)}")
    else:
        ok("family.json: keys + base_plane valid")

    # -- 2. the pieces: part.build + spec.PARAM_SPEC/check -------------------
    try:
        part, spec = load_family(fam_dir)
    except Exception as e:  # noqa: BLE001
        bad(f"part.py/spec.py failed to import: {type(e).__name__}: {e}")
        return False, log
    missing_pieces = []
    if not callable(getattr(part, "build", None)):
        missing_pieces.append("part.py: build()")
    if not isinstance(getattr(spec, "PARAM_SPEC", None), dict):
        missing_pieces.append("spec.py: PARAM_SPEC")
    if not callable(getattr(spec, "check", None)):
        missing_pieces.append("spec.py: check()")
    if missing_pieces:
        bad(f"missing required piece(s): {missing_pieces}")
        return False, log

    argnames = list(inspect.signature(part.build).parameters)
    extra = [a for a in argnames if a not in spec.PARAM_SPEC]
    if extra:
        bad(f"part.build has parameter(s) not declared in PARAM_SPEC: {extra}")
        return False, log
    ok(f"pieces: build({len(argnames)} params) + PARAM_SPEC + check present")

    spec_bad = [
        f"{name}.{key}"
        for name, entry in spec.PARAM_SPEC.items()
        for key in SPEC_REQUIRED
        if key not in entry
    ]
    spec_bad += [
        f"{name}.range missing '{diff}'"
        for name, entry in spec.PARAM_SPEC.items()
        for diff in DIFFS
        if isinstance(entry.get("range"), dict) and diff not in entry["range"]
    ]
    if spec_bad:
        bad(f"PARAM_SPEC incomplete: {spec_bad[:6]}")
    else:
        ok(f"PARAM_SPEC: {len(spec.PARAM_SPEC)} params, all entries complete")

    # -- 3-6. sampling, determinism, execution, hashes -----------------------
    programs: dict[str, list[str]] = {diff: [] for diff in DIFFS}
    hashes: list[str] = []
    # optional: a family may declare its solid count (a multi-body assembly
    # declares e.g. 3); if present, every sampled instance must match it.
    want_solids = meta.get("solids")
    solid_counts: set[int] = set()
    with tempfile.TemporaryDirectory() as td:
        for diff in DIFFS:
            n_ok = 0
            for seed in range(seeds):
                try:
                    p = sample_params(spec, diff, np.random.default_rng(seed))
                    violations = spec.check(p)
                    if violations:
                        bad(f"{diff}/seed{seed}: sample violates check: {violations[:2]}")
                        continue
                    # the declared spec is a contract: every sampled value must
                    # fall inside its own PARAM_SPEC range for this difficulty
                    oob = []
                    for name, entry in spec.PARAM_SPEC.items():
                        if name not in p:
                            oob.append(f"{name} missing from sample")
                            continue
                        lo, hi = entry["range"][diff]
                        if not (lo - 1e-9 <= p[name] <= hi + 1e-9):
                            oob.append(f"{name}={p[name]} outside declared ({lo}, {hi})")
                    if oob:
                        bad(f"{diff}/seed{seed}: sample breaks PARAM_SPEC contract: {oob[:2]}")
                        continue
                    # the framework derives the stand-alone instance program
                    # from build()'s source + params (derive.py) so the
                    # contributor never writes a code generator.
                    prog = derive_program(part, p)
                    if "result" not in prog:
                        bad(f"{diff}/seed{seed}: derived program binds no `result` — build() must assign `result`")
                        continue
                    # determinism: same seed => identical params => identical program
                    p2 = sample_params(spec, diff, np.random.default_rng(seed))
                    if derive_program(part, p2) != prog:
                        bad(f"{diff}/seed{seed}: NOT deterministic (same seed, different program)")
                        continue
                    programs[diff].append(prog)
                    if geometry:
                        step = Path(td) / f"{diff}_{seed}.step"
                        from .execute import execute_cq_to_step
                        from .render import step_solid_report

                        execute_cq_to_step(prog, step)
                        # every solid the instance produces must be a real body
                        # (>0 volume): catches a member silently vanishing while
                        # the overall shape still meshes.
                        n_solids, min_vol, _ = step_solid_report(step)
                        if n_solids == 0 or min_vol <= 1e-6:
                            bad(f"{diff}/seed{seed}: degenerate/empty solid "
                                f"(solids={n_solids}, min_volume={min_vol:.3g})")
                            continue
                        if want_solids is not None and n_solids != want_solids:
                            bad(f"{diff}/seed{seed}: produced {n_solids} solid(s) but "
                                f"family.json declares solids={want_solids} "
                                "(a body vanished or unexpectedly merged?)")
                            continue
                        solid_counts.add(n_solids)
                        hashes.append(_geom_hash(step))  # raises if degenerate
                    n_ok += 1
                except Exception as e:  # noqa: BLE001
                    bad(f"{diff}/seed{seed}: {type(e).__name__}: {str(e)[:120]}")
            if n_ok == seeds:
                ok(f"{diff}: {n_ok}/{seeds} seeds sample+check+build+execute clean")

    # coverage gate: params declaring `coverage: [...]` must produce every
    # declared value across a cheap large sampling pass (no geometry).
    cov_params = {n: e["coverage"] for n, e in spec.PARAM_SPEC.items() if "coverage" in e}
    if cov_params:
        seen: dict[str, set] = {n: set() for n in cov_params}
        for diff in DIFFS:
            for seed in range(40):
                try:
                    p = sample_params(spec, diff, np.random.default_rng(1000 + seed))
                except Exception:
                    continue
                for n in cov_params:
                    seen[n].add(round(float(p[n]), 6))
        for n, values in cov_params.items():
            missing = [v_ for v_ in values if not any(abs(v_ - s) < 1e-6 for s in seen[n])]
            if missing:
                bad(f"coverage: {n} never produced declared value(s) {missing} in 120 samples")
            else:
                ok(f"coverage: {n} reaches all {len(values)} declared values (standard table fully covered)")

    # geomlib declaration: names must exist in the registry AND be inlined in
    # the emitted (stand-alone) program.
    declared = meta.get("geomlib") or []
    if declared:
        from .geomlib import REGISTRY as _REG

        unknown = [n for n in declared if n not in _REG]
        first = next((pr for progs in programs.values() for pr in progs), None)
        if unknown:
            bad(f"family.json geomlib: unknown helper(s) {unknown} (have: {sorted(_REG)})")
        elif first and any(f"def {n}(" not in first for n in declared):
            bad("family.json geomlib: declared helpers are not inlined in the emitted program")
        elif first:
            ok(f"geomlib: {declared} registered + inlined (program stays stand-alone)")

    flat = [p for progs in programs.values() for p in progs]
    if flat:
        if len({min(progs) for progs in programs.values() if progs}) == 1 and len(
            [1 for progs in programs.values() if progs]
        ) == len(DIFFS):
            bad("difficulty separation: easy/medium/hard produced identical programs")
        else:
            ok("difficulty separation: difficulties produce distinct programs")
    if hashes:
        dup = 1.0 - len(set(hashes)) / len(hashes)
        (ok if dup <= 0.5 else bad)(
            f"geometry novelty: {len(set(hashes))}/{len(hashes)} unique shapes "
            f"({dup:.0%} duplicate{' — too clone-heavy' if dup > 0.5 else ''})"
        )
    if solid_counts:
        cnt = sorted(solid_counts)
        detail = str(cnt[0]) if len(cnt) == 1 else str(cnt)
        note = f" (declares solids={want_solids})" if want_solids is not None else ""
        ok(f"solids: every instance non-degenerate, {detail} solid(s) each{note}")

    return all(passed for passed, _ in log), log
