# Standard Components

BenchCAD standard components are reusable, deterministic geometry helpers in
`bench2.geomlib`. They are framework infrastructure, not a synthetic
`designs/standard_component/` family. A consuming family still owns its
parameters, source citations, constraints, component names, and previews.

## Initial supported subset

The first subset covers common ISO metric coarse-thread sizes M3, M4, M5, M6,
M8, M10, M12, and M16:

- `iso_metric_fastener_dimensions(d)` returns ISO 261 coarse pitch, ISO 4017
  hex-head width/height, and ISO 68-1 basic external-root/internal-minor
  diameters.
- `make_iso_hex_bolt(d, length, thread_length, modeled_thread=0)` builds a
  hex-head bolt with its bearing face at `z=0` and shank along `-Z`.
- `make_iso_tapped_hole_cutter(d, depth)` returns an ISO 68-1 basic
  `minor_bore` cutter along `-Z`.

`modeled_thread=0` is the low-cost major-diameter envelope.
`modeled_thread=1` uses a deterministic visible helical ridge with a 60-degree
included V profile. The ridge uses the ISO basic root diameter, a sharp crest,
and a small embedded root for robust solid fusion; it is not a manufacturing
tolerance model. The tapped-hole cutter is likewise not a full thread or a
tap-drill recommendation.

## Source boundary

- Preferred coarse pitches: ISO 261.
- Basic metric thread profile diameters: ISO 68-1.
- Hex-head width across flats and head height: ISO 4017.

Tolerance classes, allowances, coatings, runout, under-head radii, exact
chamfers, and manufacturing tap drills are outside this first subset. A family
must cite the exact standard/table it uses in `PARAM_SPEC`; importing a helper
does not replace family-level evidence.

## Derivation contract

Public helpers are registered in `bench2.geomlib.REGISTRY`. The deriver follows
each imported function back to its defining module and recursively inlines its
helper functions, constants, and allowed `cadquery`/`math` imports. The emitted
program therefore remains stand-alone and deterministic.

Family metadata lists the public helper names it calls, for example:

```json
{"geomlib": ["make_iso_hex_bolt"]}
```

Keep framework/library work in its own PR. Existing or new family PRs remain
scoped to one `designs/<family>/` directory, except for the repository's
documented process for introducing a missing shared helper.
