# Minifix 15 geometry notes

## Evidence scope

The seven nominal installation rows come from the Häfele UK catalogue,
`14CFC294.pdf` and `14CFC295.pdf`, pp. 294--295. The downloadable manufacturer
CAD on the [Häfele Minifix 15 product page](https://www.hafele.com/us/en/product/connector-housing-minifix-15/P-00861332/)
was inspected for item **262.25.035** (`Cas. Minifix 15R/19`, bright zinc
alloy), exported as STEP AP214 on 2026-07-23.

Item 262.25.035 directly anchors only the 19 mm catalogue row. It is not a
seven-row parametric manufacturer model. Nominal catalogue dimensions and
measured casting dimensions are therefore kept distinct.

## Baseline landmarks measured from item 262.25.035

| Landmark | OEM STEP | Catalogue nominal |
|---|---:|---:|
| Bounding box | 16.30 × 16.30 × 14.65 mm | — |
| Casting body outside diameter | 14.90 mm | Ø15 housing bore |
| Rim maximum diameter | 16.30 mm | Ø16.5 rim |
| Exposed face projection | 0.80 mm | 1.0 mm nominal rim height |
| Body end from installation plane | 13.85 mm | X = 14.5 mm drilling depth |
| Bolt-window clear span | z = 7.65..11.35 mm | A = 9.5 mm centre |
| Offset cam outer section | R4.4000 at (1.9829, -0.4279) mm | not listed |
| Offset cam inner section | R3.7872 at (1.5315, -0.9875) mm | not listed |
| Combination socket | PZ outline, SW4 ≈ 4.02 mm | PZ2 / flat / SW4 |

The STEP also contains a near-zero CADClick translator artefact, while its main
B-rep does not pass OpenCascade's strict validity check. It is used only for
measurements and topology inspection; it is not imported by `build()` and is
not included in the PR.

## How it is parameterized

For the baseline row `(t, A, X) = (19, 9.5, 14.5)`:

```text
body OD        = nominal bore Ø - 0.10 = 14.90 mm
body end       = X - 0.65 = 13.85 mm
rim OD         = nominal rim Ø - 0.20 = 16.30 mm
face projection= 0.80 × nominal rim height = 0.80 mm
bolt slot      = centred directly at z = A
cage wall      = 0.22 × (X - A) = 1.10 mm
```

The measured transverse cage, offset cam, C-plate, combination-drive, and
direction-arrow landmarks are normalized by the fixed Ø15 bore. For the other
six catalogue rows, `A` moves the bolt window and `X` extends the axial cage.
The wall formula, Ø7/Ø8 capture-clearance adjustment, and all cross-SKU cage
deformations are explicitly **proportion** rules because the single OEM CAD
file does not prove the internal geometry of every SKU.

`has_rim`, `rim_diameter`, and `rim_height` come from the selected catalogue
row. The operating socket is not sampled as three fictitious variants: the
baseline CAD contains one combination profile that accepts PZ2, a flat blade,
and SW4.

## Deliberate deviations

- The code rebuilds the OEM topology as readable, valid CadQuery geometry; it
  does not copy the manufacturer's invalid B-rep.
- Small casting draft, local blends, ejector marks, and sub-millimetre edge
  treatments are omitted or simplified.
- Direction arrows reproduce the visible recessed form but not every spline
  control point from the STEP.
- Only item 262.25.035 is CAD-calibrated. Other catalogue lengths are a
  benchmark-oriented parametric extrapolation, not manufacturing CAD.
- The family is not intended for fit, tolerance, kinematic, or production use.

## Verification

`bench2 validate minifix_cam_housing` checks catalogue-row coverage,
constraints, deterministic derived programs, geometry novelty, and one
non-degenerate solid per instance. `bench2 preview minifix_cam_housing`
produces the difficulty grid, four benchmark views, and min/max extremes for
visual comparison with the issue evidence and OEM CAD.
