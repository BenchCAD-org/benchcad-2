# Wolfrom dual-ring train

This is the five-component **gear train** proposed in [#187](https://github.com/BenchCAD-org/benchcad-2/issues/187), not a catalog-qualified enclosed gearhead. R1 is fixed, R2 is output, and the carrier floats. The carrier has no output shaft. The two toothed planet sections are one solid with identical clocking on every planet.

## Source and scope

- Source tooth rows and reference drawing: issue #187, drawing at repository commit `911c0cab3ea11f46302d7bc2881777f2d77e1190`.
- Involute boundary helper adapted from BenchCAD PR [#185](https://github.com/BenchCAD-org/benchcad-2/pull/185), commit `fc3a71fbbd9295a181d0db60822b68656ea14074`. MIT, copyright 2026 The BenchCAD Authors; full license is in the repository root. This is reused work, not a newly invented tooth generator.
- 20-degree pressure angle, module, pitch diameters `m*z`, addendum `m`, and dedendum `1.25m` follow the proposal's ISO 53/DIN 867 and ISO 54 convention. No unavailable paid standard table is claimed to have been read.
- Flanks are sampled involutes; below the base circle the external root follows a radial continuation and tooth-root joins are straight chords. These are documented approximations, not a complete generated trochoidal fillet. Backlash relief `0.08m` on external teeth is a chosen proportion, not a claimed DIN tolerance class. [KHK's technical reference](https://khkgears.net/pdf/internal-tech.pdf) distinguishes involute, trochoid and trimming interference; timing alone does not certify any of those.

The source's first row is pictured with three equally spaced planets. That is incompatible with `zs+zr1=68`. This implementation retains all four source tooth rows and corrects the permitted count; the issue comment asks the maintainers to confirm this scope. It does not copy the impossible pose.

| Source row | zs / za / zb | zr1 / zr2 | Exact input/output ratio | Permitted n |
|---|---|---|---|---|
| 0 | 14 / 20 / 18 | 54 / 52 | 520/7 | 2 |
| 1 | 16 / 22 / 20 | 60 / 58 | 319/4 | 2 |
| 2 | 12 / 24 / 22 | 60 / 58 | 116 | 2, 3 |
| 3 | 18 / 21 / 20 | 60 / 59 | 413/3 | 3 |

## Timing and motion

In the carrier frame, the external sun/A mesh has opposite relative rotation; both internal ring meshes have the same relative rotation. With unit sun speed and R1 held:

```
zs*(1-c) + za*(p-c) = 0
zr1*(0-c) - za*(p-c) = 0
zr2*(r-c) - zb*(p-c) = 0
```

Therefore `c=zs/(zs+zr1)`, `p=c*(1-zr1/za)`, `r=c+(zb/zr2)*(p-c)`. `_motion` multiplies those speeds by input angle. The output ratio is `(zr1+zs)*zr2*za/[zs*(zr2*za-zb*zr1)]`; coincident rings yield zero output and are rejected.

Write angles in turns, planet position `theta`, and rigid planet angle `phi`. Tooth-space alignment is:

```
zs*(sun-theta)+za*(phi-theta-1/2) = 1/2 (mod 1)
zr1*(ring1-theta)-za*(phi-theta) = 1/2 (mod 1)
zr2*(ring2-theta)-zb*(phi-theta) = 1/2 (mod 1)
```

Internal pairs use a difference, not the external pair's sum. The source's blanket sum rule does not give the internal rolling relation.

For identical steps and equal spacing, set `D=zs+za`, `g=gcd(za,zb)`. Comparing position `j/n` with zero, the sun relation gives `za*Delta_phi=D*j/n+k`. R1 then requires `2D*j/n` to be integral. R2 requires `D*(za+zb)*j/n+zb*k` to be a multiple of `za`; an integer `k` exists iff `D*(za+zb)*j/n` is divisible by `g`. Thus all positions are possible exactly when **`n | 2D` and `n*g | D*(za+zb)`**. `_initial_phases` solves the remaining finite integer congruence, rather than timing A and B independently per planet.

Adjacent tip circles additionally require `D*sin(pi/n)>max(za,zb)+2`. For source row 2, four or six planets meet the phase condition but fail this spacing check and are excluded. The external-to-internal tooth-count gaps are large, but actual geometric intersections still need separate measurement.

## Physical layout and honest proportions

Both gear stations use face width `b`; station A occupies `[0,b]`, station B `[b+g,2b+g]`. R1 and R2 remain separate moving bodies. The sun and its input shaft are fused. Each pair of planet sections is fused through a bored waist. A single rear carrier disc carries integral pins; planet bores leave radial clearance. The rear carrier plate clears the sun shaft and does not intersect either toothed station.

| Dimension | Value or range | Basis |
|---|---|---|
| module | 0.8, 1, 1.25, 1.5, 2 mm | proposal's preferred-module convention |
| face width | easy/medium 8–12m; hard 6–14m | proportion; drawing has b=24 at m=2 |
| gap g | easy 0.4–1m; medium 0.4–1.5m; hard 0.4–2m | proportion |
| rim beyond ring root | easy 4–5m; medium 3–6m; hard 2–7m | proportion; source 133 mm OD implies 10 mm rim at m=2, zr1=54 |
| pin radius | `0.20m*min(za,zb)` | proportion, constrained to fit the bored waist |
| pin radial clearance | `0.20m` | proportion |
| planet waist radius | `0.70*(m*min(za,zb)/2-1.25m)` | proportion, with positive bore wall |
| sun shaft radius | `0.25m*zs` | proportion, constrained inside root circle |
| input shaft extension | `8m` behind station A | proportion, constrained to project behind carrier |
| carrier plate thickness | `max(1.5m,0.30b)` | proportion |
| carrier plate radius | orbit radius + pin radius + `0.60m` | proportion, positive margin around pins |
| axial end clearance | `0.25m` | proportion |
| input pose | easy 0; medium 0–360; hard 0–3600 degrees | operating-state sampling; no independent member poses |

`row` locks all five tooth counts together. `check` rejects mixed rows, nonpositive dimensions, degeneracy, impossible clocking, adjacent planets that overlap, a bored-through planet waist, and a sun shaft that reaches its root circle. Neither the sampler nor check weakens these conditions to gain coverage.

## Validation and contribution status

Exact arithmetic in the separate audit independently reproduces all four ratios, rejects coincident rings, and agrees with a full-turn finite phase search on 720 additional combinations. Reference checks reproduce 28/40/108 mm pitch diameters and 34 mm orbit radius for the pictured module-2 first row.

Local validation completed on 2026-09-13: default `bench2 validate` passed all 12 builds with 12 unique geometries and complete declared coverage. The independent body audit covered 25 assembled motion/boundary cases and 435 component pairs, all with zero intersection volume; every named component was one valid non-degenerate solid. Both six-body/two-planet and seven-body/three-planet cases were covered. All five standard previews were generated and inspected by Codex. The detailed audit tools/results stay outside the family package.

No acceptance or human-preview inspection is asserted by this file. The contribution uses Codex acting on behalf of Ziao Yang (`yangziao56`), and the human review/credit route is being confirmed explicitly in #187. The independently generated corrected section drawing is supplementary contribution evidence, not a manufacturer photo.
