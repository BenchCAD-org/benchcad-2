# Minifix 15 geometry notes

## Evidence scope

The seven installation rows come from Häfele UK catalogues `14CFC294.pdf`
and `14CFC295.pdf`, pp. 294--295. The reference item is Häfele
**262.25.035**, `Cas. Minifix 15R/19`, downloaded as STEP AP214 from the
[Häfele Minifix 15 product page](https://www.hafele.com/us/en/product/connector-housing-minifix-15/P-00861332/)
on 2026-07-23.

The STEP has two transfer roots. Root 1 is a 27-face CADClick artefact with
zero volume. Root 2 is the actual 342-face manufacturer solid. Root 2 is used
only for local measurement and visual comparison; it is not imported by
`build()` and no OEM BREP, STEP, or encoded topology is part of this family.

## Baseline measurements

| Landmark | OEM root 2 | Catalogue nominal |
|---|---:|---:|
| Bounding box | 16.30 x 16.30 x 14.65 mm | -- |
| Housing bore | 14.90 mm casting OD | 15 mm drill hole |
| Rim diameter | 16.30 mm | 16.5 mm |
| Rim projection | 0.80 mm | 1.0 mm |
| Casting end | 13.85 mm from installation plane | X = 14.5 mm |
| Bolt-axis datum | 9.50 mm | A = 9.5 mm |
| OEM solid volume | 801.707894 mm3 | -- |

## Reconstruction approach

The model is rebuilt from named CadQuery features, in the visible OEM order:

1. shallow operating disc, drive recess, and curved direction arrow;
2. offset eccentric capture cam with a bolt-entry slot;
3. two independent open C-plates rather than a solid circular floor;
4. asymmetric legs, short upper ears, and a partial rear shell that leave the
   major OEM windows open.

The exact catalogue rows drive bore diameter, rim choice, `A`, `X`, and the
7/8 mm bolt-hole choice. The internal cam length, plate mouths, support-leg
placement, and rear-shell thickness are **proportion** fits to the one OEM
baseline because the catalogue does not dimension those casting features and
does not supply CAD for the other six rows.

## Verification of the 19 mm baseline

| Metric | OEM root 2 | Parametric reconstruction | Difference |
|---|---:|---:|---:|
| Bounding box X | 16.300000 mm | 16.300000 mm | < 0.000001 mm |
| Bounding box Y | 16.300000 mm | 16.300000 mm | < 0.000001 mm |
| Bounding box Z | 14.650000 mm | 14.650000 mm | < 0.000001 mm |
| Solid count | 1 | 1 | 0 |
| Face count | 342 | 88 | readable analytic reconstruction |
| Volume | 801.707894 mm3 | 814.091087 mm3 | +1.54% |

## Deliberate deviations

- The CAD source has no recoverable feature tree. This is a new parametric
  reconstruction, not copied manufacturer topology.
- OEM local blends, drafts, and small windows are simplified where their
  dimensions are not published.
- Only item 262.25.035 directly anchors the internal casting. Cross-SKU
  internal changes are proportional, not asserted manufacturer dimensions.
- The family is not production, tolerance, or fit data.
