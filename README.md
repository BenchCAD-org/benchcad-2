# BenchCAD 2.0

**Agentic generation and multi-turn refinement over community-grounded
parametric CAD — 150 industrial part families, each backed by an auditable
parametric design.**

[![Discord](https://img.shields.io/badge/Discord-join%20the%20community-5865F2?logo=discord&logoColor=white)](https://discord.gg/be9AtvrDyK)

BenchCAD 2.0 is the successor to
[BenchCAD](https://github.com/BenchCAD/BenchCAD-main). Every family is defined
by explicit engineering knowledge: named parameters, sourced ranges,
inter-parameter constraints, and deterministic CadQuery geometry.

## Contributing a family

A family is one auditable parametric design:

```text
designs/<family>/
├── part.py       # build(<named parameters>) -> CadQuery solid
├── spec.py       # PARAM_SPEC, check(), optional refine()
└── family.json   # labels, source, and contributor
```

Start with:

- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution lifecycle and rules
- [`REVIEWING.md`](REVIEWING.md) — the human review checklist
- [`docs/DESIGN_SPEC.md`](docs/DESIGN_SPEC.md) — the part/spec interface

```bash
uv sync
uv run bench2 new my_family
# edit designs/my_family/{part.py,spec.py,family.json}
uv run bench2 validate my_family
uv run bench2 preview my_family   # inspect the renders before submitting
```

Progress is tracked in [`STATUS.md`](STATUS.md), contributor provenance in
[`CONTRIBUTORS.md`](CONTRIBUTORS.md), and active proposals in the
[family issues](../../issues?q=is%3Aissue+is%3Aopen+label%3Afamily).

The architectural rationale lives in [`DESIGN.md`](DESIGN.md). The scoring
engine is maintained in
[`BenchCAD/BenchCAD-main`](https://github.com/BenchCAD/BenchCAD-main).

## License

Code and designs are MIT licensed. Released dataset artifacts are CC BY 4.0.
