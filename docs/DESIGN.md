# BenchCAD 2.0 — Design Blueprint

Decision record for the benchmark, family interface, release model, and
governance.

## 1. What this is

BenchCAD 2.0 combines two ideas:

**Agentic evaluation.** An agent can execute, render, compare, and measure its
candidate under a turn or token budget. Results are reported as
quality-versus-budget curves and pass@budget. A one-turn run remains the
one-shot baseline.

**Community-grounded data.** The project targets **150 industrial part
families**, each defined by an explicit parametric design whose ranges and
engineering constraints are sourced, readable, and reviewed.

## 2. Family composition

Earlier BenchCAD families are not inherited automatically. A family enters
BenchCAD 2.0 only after it is upgraded to the explicit design interface, its
ranges are grounded against real sources, and its constraints and geometry are
reviewed. Dataset instances are regenerated from the accepted designs.

## 3. The contribution unit

Each family has three auditable files:

| Piece | File | Purpose |
|---|---|---|
| `build(<named params>)` | `part.py` | Human-readable parametric CadQuery part |
| `PARAM_SPEC`, `check`, optional `refine` | `spec.py` | Ranges, sources, sampling contract, engineering constraints |
| labels and provenance | `family.json` | Family name, standard, base plane, description, source, contributor |

The framework owns sampling and derives stand-alone CadQuery programs. Shared
geometry helpers live in `bench2.geomlib`. Machine validation checks the
interface, sampling contract, determinism, execution, geometry diversity, and
helper inlining. Humans review the engineering truth of the ranges and
constraints, the source evidence, renders, and labels.

## 4. Sampling

Families are sampled toward geometric saturation instead of a flat quota.
Simple parameter spaces stop earlier; complex families support more instances.
The instance count per family is a measured property of its parameter space.

Difficulty tiers have explicit semantics:

- **easy** — core geometry, features off, tight central ranges;
- **medium** — additional features and broader ranges;
- **hard** — full feature combinations and valid boundary cases.

## 5. Release and versioning

Released dataset versions are immutable. Fixes and new designs merge through
the normal review process and accumulate into the next release. Every reported
score records the dataset version and agent budget used.

Versioned manifests, generation summaries, and contributor provenance make a
release reproducible without changing an already published benchmark revision.

## 6. Governance

One family corresponds to one issue and one PR. CI runs the same validation
command contributors run locally. A non-author reviewer verifies the evidence,
renders, parameter extremes, equations, constraints, and labels before merge.

The issue and PR form the family dossier. Contributor roles — proposer,
implementer, and verifier — are derived from that record and reflected in the
provenance board and dataset card.

## 7. Repository layout

```text
benchcad-2/              framework, design specs, family sources, CI, docs
BenchCAD-main/           scoring engine
Hugging Face releases    versioned dataset artifacts
```

Change this blueprint through a reviewed PR so architectural decisions remain
explicit.
