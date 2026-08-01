# Minifix 15 geometry notes

## Evidence scope

The seven installation rows come from Häfele UK catalogues `14CFC294.pdf`
and `14CFC295.pdf`, pp. 294--295. The CAD-calibrated reference is Häfele
item **262.25.035**, `Cas. Minifix 15R/19`, downloaded as STEP AP214 from the
[Häfele Minifix 15 product page](https://www.hafele.com/us/en/product/connector-housing-minifix-15/P-00861332/)
on 2026-07-23.

The STEP carries two transfer roots. Root 1 is a 27-face CADClick artefact
with zero volume; root 2 is the 342-face manufacturer solid (163 planes,
147 cylinders, 21 cones, 11 tori; no free-form surfaces). Root 2 was audited
locally by a full face census plus planar cross-sections at 21 axial stations;
the closed contours of those sections are the radial master profiles stored in
`part.py`. `build()` performs no file I/O and no OEM STEP, BREP, mesh, or
encoded topology ships in the family.

## Why a contour stack

An earlier draft built the body from concept primitives (an eccentric cam
*ring*, a thin shell, rectangular windows and rails). Cross-sectioning the OEM
solid showed that draft was topologically wrong: at the bolt plane the OEM cam
is a *solid eccentric lobe* (not a ring), the cage wall is thick and joined to
the cam by webs, the radial mouth has a shaped lip, the top carries *two*
rotation arrows, and the bottom is a splayed fork. The OEM solid is itself a
stack of flat-z extrusions (its plane census is a ladder of horizontal faces),
so the faithful and robust reconstruction is a **stack of constant-section
prisms whose outer sections are the manufacturer's own cross-sections**,
resampled to closed polylines. The outer silhouette, the cam lobe, the thick
walls, the webs, the mouth lip, the two arrows and the splayed fork are baked
into the stored contours; only a few inner loops / sharp corners at complex
sections are simplified by the chainer (see the fidelity table below).

## Baseline measurements (OEM root 2)

| Landmark | OEM root 2 | Catalogue nominal |
|---|---:|---:|
| Bounding box | 16.30 x 16.30 x 14.65 mm | -- |
| Housing casting OD | 14.90 mm | 15 mm drill hole |
| Seating rim OD | 16.30 mm | 16.5 mm |
| Seating rim projection | 0.80 mm | 1.0 mm |
| Casting end | 13.85 mm from seating plane | X = 14.5 mm |
| Bolt-axis datum | 9.50 mm | A = 9.5 mm |
| Eccentric cam outer | R4.400 mm at (1.98, -0.43) | -- |
| Eccentric cam inner | R3.787 mm at (1.53, -0.99) | -- |
| Hook inner face (seat) | y = 3.50 at A (=> Ø7 option CAD) | -- |
| OEM solid volume | 801.707894 mm3 | -- |

## Parametric story

Every catalogue row is a Ø15 housing, so the **radial** master profiles are
constant across the family. The **axial** layout is the honest parametric axis,
built as three *rigid* blocks joined by two *compressible* straight-wall necks:
the top drive cup (sections <= 2.715) is fixed at the seating plane, the
cam/mouth hook block (6.6..11.2) is translated rigidly by `A - 9.5` so its
proportions stay identical to the OEM at every row (the translation preserves
the OEM's own hook/bolt-axis offset, so the 19 mm baseline is the identity), and
the bottom fork (>= 12.85) is translated rigidly to the casting end `X - 0.65`;
only the two necks (drive-cup-to-hook and hook-to-fork) stretch or compress to
absorb the drilling depth -- the physically correct degree of freedom, which
keeps the hook from being elongated on long rows or squashed on short ones. For
rim-less rows the OEM z=0 section (the rim disc) is unavailable, so the valid
0.8 cage section is held up to the seating plane, giving a flush rim-less top.
The radial shape is unaffected by this map.

The OEM CAD exists for a single connecting-bolt option (the hook inner face at
`A` measures 3.50 mm, i.e. the Ø7 head). `bolt_hole_diameter` therefore trims a
parametric head-clearance on the hook inner face (head radius + 0.3 mm): the Ø7
option clears the baked edge, the Ø8 option trims a little more. This is the
honest proportion rule for the option without CAD, and it keeps the two
catalogue bolt-hole values geometrically distinct.

## Verification of item 262.25.035

| Metric | OEM root 2 | Parametric Ø8 | Difference |
|---|---:|---:|---:|
| Bounding box X | 16.300000 mm | 16.270 mm | -0.030 mm |
| Bounding box Y | 16.300000 mm | 16.270 mm | -0.030 mm |
| Bounding box Z | 14.650000 mm | 14.650000 mm | < 0.000001 mm |
| Solid count | 1 | 1 | 0 |
| Volume | 801.707894 mm3 | 731.81 mm3 | -69.9 mm3 (-8.7%) |

The Ø7 baseline is 743.26 mm3. Bounding box Z is exact; X/Y are within 0.03 mm
(the inscribed polygon rim). Volume is a useful mass-property check, not a claim
of identical topology.

### Section fidelity (chaining-free point-cloud Hausdorff, stored vs OEM)

The stored contours reproduce the OEM **outer silhouette and topology** well, but
a chain-free comparison (stored outer+hole points vs the union of *all* OEM
section-edge points, so neither chaining nor prism-boundary artefacts flatter the
result) shows the inner loops / sharp corners are not all captured. Directed
distance OEM->stored ("OEM boundary not covered by the stored contour"):

| z | -0.8 | -0.5 | 0.0 | 0.8 | 2.0 | 2.7 | 3.7 | 4.5 | 5.3 | 6.6 | 7.3 | 8.0 | 9.5 | 11.2 | 12.85 | 13.3 | 13.7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mm | 0.27 | 0.47 | 0.58 | 0.63 | 1.43 | 0.46 | 1.02 | 0.50 | 2.99 | 1.28 | 0.53 | 0.24 | 0.22 | 0.25 | 0.56 | 0.58 | 0.84 |

(The reverse direction, stored->OEM, is <= 0.98 mm everywhere, so the model
invents no geometry far from the OEM.) 16 of 21 stations cover the OEM boundary
within 0.63 mm. The residuals are at the drive-recess mid-depth (2.0, 3.7), the
cam-hook inner loop (5.3, 6.6) and the foot tip (13.7): at these complex /
tangent sections the endpoint-greedy edge chainer dropped an inner loop or a
sharp corner (worst 2.99 mm at 5.3 = the eccentric cam-inner wall that the
chainer merged into the outer C). The inter-plane drafts are also represented as
held sections, so the curved side surfaces show **terracing** in the render.
(An earlier linear axial map stretched the hook on long rows and squashed it on
short ones; the rigid-block map removes that proportion distortion -- verified
across easy / medium / hard and both extremes -- so terracing is now the only
axial artefact.) These inner-feature simplifications plus the held-section
approximation account for the -8.7% volume.

### Independent adversarial review

A two-lens independent verification was run. The gates/derivation lens **PASS**ed:
`validate` clean, derived programs ASCII + deterministic + mutually distinct,
`build()` binds `result` with no module-scope-illegal return. The section-fidelity
lens returned **FAIL** on a strict per-largest-ring metric that also sectioned the
model exactly on the prism-boundary planes; that metric is partly a method
artefact (it breaks whenever greedy chaining fragments a section -- it fragmented
its *own* OEM side at 6.6 and 0.8 -- and a boundary-plane section returns a
neighbour zone's held contour), and partly the real inner-loop drops above, which
the chaining-free table quantifies. That lens's topology/aspect sub-checks passed
(single solid, exact Z, cam lobe present at 9.5, two arrow holes at the top).

Two remediation attempts were prototyped against an in-memory oracle and **not**
merged: (a) a planar CCW half-edge face-walker with containment-depth nesting
mis-nested loops and collapsed the body; (b) overlaying the analytic combination
drive recess was based on two false premises -- the 5.3 gap is the cam-inner loop
not the SW4 socket (the socket, z ~ 2--3.7, is already stored), and the carried-
over PZ2 template mismatches this OEM's PZ2 by ~5 mm. Both were discarded, so the
validated 21-station contour stack above is the shipped model.

### Recommended path to close the residuals

A correctly implemented planar face-walker -- build the half-edge graph from
finely discretised section edges, walk faces by the "turn-most-clockwise" next
rule, and classify outer/hole by **containment depth** (unbounded = 0 dropped,
outer = 1, hole = 2, hole-interior = 3 dropped; this is orientation-free so the
CCW/CW sign need not be right) -- would capture every inner loop and preserve
every junction corner (closing 2.0/3.7/5.3/6.6/13.7) *and* make mid-draft
sections chainable (enabling dense stations that remove the terracing). Any
analytic overlay must first re-fit its template to the stored contour (do not
reuse an un-fitted PZ2). Re-verify with the chaining-free point-cloud Hausdorff
and an in-memory build sanity gate (single solid, sane volume, the hex/inner
loops present) before writing to `part.py`.

## Deliberate deviations

- The manufacturer STEP has no recoverable feature tree. This is a new,
  editable, section-anchored parametric reconstruction, not copied OEM topology.
- Inter-plane die-cast draft, tiny blends, ejector marks and sub-millimetre edge
  treatments are represented as held sections (21 stations) rather than modelled
  surface-by-surface.
- For `has_rim = 0` rows the rim flange is omitted and the seating-plane
  section is clipped to the Ø14.9 cage radius; this radial clip is an
  approximation and makes the no-rim envelope slightly oval in plan (measured
  14.43 x 14.90 mm on the short rows).
- Only item 262.25.035 directly anchors internal casting geometry; other
  catalogue lengths are axial extrapolations of the same radial master, not
  asserted OEM CAD.
- The family is benchmark geometry, not production tolerance or fit data.
