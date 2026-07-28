# double_wedge_clamp evidence and formula notes

## Source contract

- Anchor: JW Winco GN 920.1 steel wedge clamps, official metric catalog PDF.
- Catalog order code: `GN 920.1-<d>-<b>-<type>`.
- Types: GL smooth, GA with two M4 attachment-jaw threads, RF serrated.
- The model is a static four-solid assembly: `jaw_left`, `jaw_right`,
  `center_wedge`, and `screw`.
- Workpieces, base plate/end stop, GN 920.2 pull-down plates, user-made
  attachment jaws, the hidden return spring, and thread helices are excluded.

## Catalog symbol mapping

| Catalog symbol | Model parameter | Use |
|---|---|---|
| `d` | `d` | nominal central screw diameter |
| `b` | `b` | full assembly width along Y |
| `a min/max` | `jaw_span` | overall outer-face span along X |
| `h1 max` | `h1` | jaw height |
| `h2` | `h2` | center-wedge top offset above the jaws |
| `h3` (GA) | `h3` | M4 hole-center height |
| `l max` | `screw_projection` | modeled projection below the clamp base |
| `m` (GA) | `m` | spacing of the two M4 holes on each jaw |

`catalog_row` selects one entire printed row. `refine()` copies `d`, `b`,
`h1`, `h2`, `l`, force, and torque from that same row. It copies `h3` and `m`
only for GA; GL/RF receive a non-sampled zero sentinel because those printed
fields are inapplicable. `jaw_span` is sampled only inside the selected row and
type's published `a` interval.

## Verified against the catalog

| Row/type | Recomputed model inputs | Catalog values | Result |
|---|---|---|---|
| M8-21 GA | `d=8`, `b=21`, `a=39.5..44.5`, `h1=15`, `h2=4.5`, `h3=7.5`, `l=15`, `m=10` | same printed row | exact |
| M8-50 RF | `d=8`, `b=50`, `a=34.5..39.5`, `h1=15`, `h2=4.5`, `l=15`; GA fields disabled | same printed row/type columns | exact |
| M12-50 GA | `d=12`, `b=50`, `a=40..45.5`, `h1=22`, `h2=4.5`, `h3=11`, `l=21`, `m=30` | same printed row | exact |

The published 15/30 kN forces and 25/85 N m maximum torques are carried as
metadata only. They are not computed or certified by the CAD.

## Proportion formulas

The drawing does not dimension the internal wedge, guides, clearances, jaw
slopes, screw-head/recess details, or RF tooth form. These are deliberately
modeled by the following `proportion` rules:

- Jaw X width: `0.90 d`.
- Guide clearance on each wedge side: `max(0.25, 0.025 d)`.
- Center gap: `jaw_span - 2 * jaw_width`.
- Wedge top width: `center_gap - 2 * guide_clearance`.
- Wedge bottom width: `max(0.38 * wedge_top_width, 1.30 d)`. The `1.30 d`
  lower bound keeps positive wall around the `1.15 d` shank-clearance hole and
  keeps the adjacent jaw corners clear of the screw.
- The integral center wedge begins at `0.14 h1` and occupies
  `b - 2 * guide_clearance` in depth.
- Each jaw uses a vertical relief below `0.14 h1`; its actual sloped contact
  segment therefore has exactly the same endpoints and slope as the adjacent
  center-wedge face, offset by the declared guide clearance.
- Each left/right wedge face carries one continuous T rail centered at `Y=0`.
  Its axis follows the XZ contact slope and is perpendicular to Y. The neck
  width is `max(2.60, 0.09 b)` and the visibly wider head is
  `max(5.00, 0.18 b)`; its undocumented sizes are `proportion`.
- The center side profile is one symmetric trapezoid with horizontal lower and
  upper edges, extruded perpendicular to that XZ profile. The contact slopes
  continue unchanged above `h1` until they meet the horizontal top at
  `z=h1+h2`; there is no shoulder, second slope, or rectangular cap.
- Each T rail is fused to that complete sloped face and clipped flush by the
  center's horizontal lower and upper planes. Each jaw has one matching T slot
  enlarged by 0.15 mm; its cutter extends beyond both jaw limits so the slot is
  visibly open through both the horizontal top and bottom boundaries.
- Simplified low head: diameter `1.35 d`, height `0.45 d`.
- Simplified hex recess: diameter `0.62 d`, depth `0.22 d`.
- RF surface: crossed 0.32 mm shallow grooves at fixed 2.4/2.8 mm pitches.

These formulas preserve positive material and deterministic, symmetric motion
through every published `a` interval. They are not claimed as GN 920.1 product
dimensions.

## Component and clearance checks

- The two jaws are mirrored about X=0 and move equally as `jaw_span` changes.
- Each jaw's sloped face is parallel to the matching center-wedge face. A
  positive guide clearance separates the base planes, while the wedge rail
  enters the jaw's larger complementary slot without solid intersection.
- The center wedge contains a `1.15 d` shank clearance and a larger head
  recess, so the screw remains a separate non-intersecting solid.
- Each GA jaw has two nominal-diameter M4 blind cylinders, exactly 5 mm deep,
  at `y=+/-m/2`, `z=h3`; edge and wall material are checked in `spec.py`.
- `family.json` declares four solids and four stable Assembly child names, each
  with quantity one.
- `preview_parts.png` shows standard four-view rows for the GL and GA jaw
  representatives (`quantity=2` each), separate left/right RF jaws, the center
  wedge, the screw, and a final four-solid assembly overview.
- GL and GA left/right jaws coincide after a 180-degree rigid rotation. The
  simplified RF groove phase is mirrored, so its left/right geometries are
  shown separately rather than being presented as one interchangeable part.
- Independent checks confirm one non-degenerate solid per component, T-slot
  openings through both jaw limits, stable Assembly names, and zero pairwise
  solid-intersection volume in the M12-50 RF maximum case.

## Deliberate deviations

- Thread helices are omitted. GA holes are represented as smooth nominal M4
  blind cylinders; the central screw is a smooth shank.
- The DIN 7984 callout is retained, but uncataloged head and hex details use
  the declared proportions above.
- RF uses a simplified crossed-groove texture rather than claiming an
  undocumented tooth profile.
- Fillets, chamfers, blackened finish, hardened surfaces, hidden return spring,
  and the wedge's undocumented tolerance-compensation cavity are omitted.
- The assembly is static: it encodes the symmetric catalog span but no mates,
  spring behavior, force simulation, or torque simulation.
