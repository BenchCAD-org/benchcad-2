# The Design Interface (part + spec)

A BenchCAD 2.0 family is one directory with two source files — the **part** you
draw, and the **spec** that varies it across the benchmark:

```
designs/<family>/
├── part.py       # the parametric part — a human writes this: build(<named params>)
├── spec.py       # the benchmark generator — PARAM_SPEC, check(), optional refine()
└── family.json   # labels: family, standard, base_plane, description, contributor
```

The split is deliberate. `part.py` reads like a part a person authored — named
parameters, ordinary CadQuery, no dictionaries and no code generation. `spec.py`
holds the machinery that turns one part into a difficulty-graded family; **the
framework does the sampling**, so you never hand-write a generator loop. Run
`bench2 new <family>` to create annotated starter files.

---

## `part.py` — `build(<named params>) -> cq.Workplane`

Write **plain parametric CadQuery**: named arguments, build the solid, bind it
to `result`, return it. This is the file a human reads.

```python
import cadquery as cq
def build(body_w, body_h, body_t, hole_d, has_holes=0):
    result = cq.Workplane("XY").box(body_w, body_h, body_t)
    if has_holes:                                # branch on a feature param directly
        result = (result.faces(">Z").workplane()
                  .pushPoints([(-body_w / 4, 0), (body_w / 4, 0)])
                  .hole(hole_d))
    return result
```

You never format numbers into strings or emit code. For a concrete instance
`bench2` **derives** the stand-alone program a model is asked to produce
(`framework/bench2/derive.py`): each `build()` argument becomes a flat module
global (`body_w = 80.0`), and every helper the body calls — a geomlib curve, one
of your own `_local` functions, a module constant — is inlined, so the emitted
program imports only `cadquery` + `math`. The derivation is a pure text
transform (same params in ⇒ byte-identical program out), and `bench2 validate`
proves the derived program executes to the *same* solid as calling `build()`
directly — the final coding is machine-guaranteed consistent.

Rules:
- **named parameters** — every argument must be declared in `spec.py`'s `PARAM_SPEC`
- bind `result`; use only `cq` / `math` / geomlib helpers / your own module-level
  `_helpers` and constants (no I/O, no randomness, no other imports)
- deterministic: same arguments ⇒ same geometry, in the pinned environment
  (`cadquery==2.3.0`)
- `result` is a single non-degenerate solid **or** a multi-body part — a compound
  (`a.union(b)` of separate bodies, or `cq.Compound.makeCompound([...])`) or a
  `cq.Assembly` (folded to a compound on export). Every body must be a real,
  non-degenerate solid; a multi-body family declares its body count with
  `"solids"` in `family.json` so a silently-vanished member is caught
- a heterogeneous family branches on a `feature` param (`if has_holes: …`) in
  ordinary `if`/`else` — the derived program keeps the branch, evaluated against
  that instance's values

---

## `spec.py` — the benchmark generator

### 1. `PARAM_SPEC: dict[str, dict]`

One entry per `build()` parameter. `desc/unit/range/source` are always
required; the remaining keys tell the framework **how to draw** the value:

| key | required | meaning |
|---|---|---|
| `desc` | ✓ | what the parameter physically is |
| `unit` | ✓ | `"mm"`, `"deg"`, `""` (counts/ratios) |
| `range` | ✓ | `{"easy": (lo, hi), "medium": (lo, hi), "hard": (lo, hi)}` — the contract every sampled value must satisfy; may widen with difficulty |
| `source` | ✓ | where the range comes from: a cited table, an engineering rule, or `"proportion"` |
| `integer` | – | draw as an integer in `range` (default is a float, 2 dp) |
| `choices` | – | draw from a discrete set — `[0, 2, 4]`, or per-difficulty `{"easy": [0], "hard": [2, 4]}` |
| `refine` | – | **not drawn** by the framework — computed in `refine()` (a coupled parameter). Still declares a `range` for the contract |
| `askable` | – | `True` if a numeric QA question may target it |
| `feature` | – | `True` if it toggles an optional feature (drives edit derivation) |
| `coverage` | – | list of values sampling **must** be able to produce (e.g. every catalog row); the validator fails if any never appears in ~120 draws |

Difficulty semantics: **easy** = core geometry, features off, tight ranges.
**medium** = features on, wider ranges. **hard** = all features, extreme-but-
valid ranges that exercise the constraint boundary.

### 2. `check(p: dict) -> list[str]`

Returns the list of violated constraints (empty = valid). This is the
engineering heart of the contribution and **the main thing humans review**.
Every constraint carries its reason — cite the rule or standard:

```python
def check(p):
    bad = []
    if p["web_t"] > p["web_h"] / 4:              # plate-like, not a block
        bad.append("web_t > web_h/4: web must be plate-like (structural convention)")
    return bad
```

The framework calls `check()` on every draw and rejects failures — you write the
constraints, not the loop.

### 3. `refine(p, difficulty, rng) -> None`  *(optional)*

Only needed when parameters are **coupled** — one value computed from others (a
bore bounded by a root circle, a hub sized off the bore) or drawn jointly (a
real table row, not free numbers). The framework draws every non-`refine`
parameter first, then calls `refine()` to fill the `refine=True` ones **in
place**. Write just the coupling — no rejection loop:

```python
from bench2 import Resample

def refine(p, difficulty, rng):
    lo, hi = PARAM_SPEC["bore_d"]["range"][difficulty]
    feasible_lo = max(lo, 0.20 * p["hub_d"])
    feasible_hi = min(hi, 0.55 * p["hub_d"])
    if feasible_hi <= feasible_lo:
        raise Resample          # this base draw admits no valid bore
    p["bore_d"] = round(float(rng.uniform(feasible_lo, feasible_hi)), 1)
```

Use only `rng` for randomness (same seed ⇒ same parameters). Raise
`bench2.Resample` to discard an infeasible base draw; the framework resamples.
Families with no coupled parameters omit `refine()` entirely.

---

## `family.json`

```json
{
  "family": "my_family",
  "standard": null,
  "base_plane": "XY",
  "description": "One sentence describing the part and its main features.",
  "source": "manufacturer datasheet; documented proportion rules",
  "contributor": "your-github-handle"
}
```

`standard` is the anchoring specification or `null`; `base_plane` ∈
`XY|XZ|YZ` is the natural sketch plane. A family that calls geomlib helpers
lists their registered names in a `"geomlib"` array. An optional `"solids": N`
declares how many separate bodies each instance must produce (a 3-member
telescoping slide → `3`); `bench2 validate` then fails any instance whose body
count differs — a body vanished or unexpectedly merged. Single-solid families
omit it (the validator still rejects a degenerate/empty body).

## Shared geometry helpers: `bench2.geomlib`

Reusable, sourced curve generators and table helpers live in
`framework/bench2/geomlib/`. Import and call them directly. The deriver inlines
their source into each emitted program, so it stays stand-alone:

```python
from bench2.geomlib import profile_helper

def build(width, height, thickness):
    pts = profile_helper(width, height)
    result = cq.Workplane("XY").polyline(pts).close().extrude(thickness)
    return result
```

- Declare what you use in `family.json`: `"geomlib": ["profile_helper"]`. `bench2
  validate` checks the names against the registry and confirms they are inlined.
- A geomlib helper must be **self-contained** (only `math`/builtins, no module
  state, deterministic) so it runs verbatim inside an emitted program.
- Need a helper that does not exist yet? Add its sourced implementation to
  `geomlib/` in the same PR.

**Part-specific** helper shared between `build()` and `check()` (a hole layout
used by both)? Put it in `part.py` and import it in `spec.py` with
`from part import _hole_layout` — spec may depend on the part, never the reverse.
One definition keeps build and check from drifting.

## Heterogeneous variants inside one family

Catalogs often ship one part in several closely related forms. Model them as one
family with a `feature`-flagged discrete parameter, branch in `build()`, and
give each form its own physically justified constraints in `check()`.

## What you do NOT write

No sampling loop (the framework samples from `PARAM_SPEC`), and no QA items or
edit pairs — those are derived downstream (`askable` params seed numeric QA;
`feature` params drive add/remove edits). Your jobs are `part.py`, `spec.py`,
and `family.json`.

## Machine gates (`bench2 validate`, same in CI)

1. `family.json` keys present and valid
2. `part.py:build` + `spec.py:PARAM_SPEC/check` exist; every `build()` parameter
   is declared in `PARAM_SPEC`
3. per difficulty × N seeds: the sampler draws params that pass `check`, the
   sampled value stays inside its declared `range` (the contract), and the
   derived program executes to non-degenerate geometry — every body has real
   volume, and the body count matches `"solids"` when declared
4. determinism: same seed ⇒ byte-identical derived program
5. difficulty separation: the three difficulties don't produce identical programs
6. geometry-hash report: duplicate rate within the sample batch
7. coverage: every value in a `coverage=[...]` list appears across a 120-draw pass
8. geomlib: declared helpers exist in the registry and are inlined in the program

`bench2 preview <family>` renders three PNGs: `preview.png` (difficulty × seed
overview), `preview_views.png` (the four diagonal benchmark views — what the
model sees), and `preview_extremes.png` (smallest & largest sampled draw —
acceptance evidence that both ends of your declared ranges produce sane
geometry).
