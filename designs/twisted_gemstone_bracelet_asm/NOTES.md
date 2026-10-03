# Twisted gemstone bracelet assembly

Implements [family issue #226](https://github.com/BenchCAD-org/benchcad-2/issues/226)
from a user-supplied SOLIDWORKS snapshot. The result is one bracelet body and
four identical faceted gems, represented by a named `cq.Assembly` with five
solids. There is no native-CAD import, mesh import, file access, or randomness
in `part.py`.

## Source and measurements

Archive: `new-twisted-bracelet-04-1.snapshot.4.zip`.
SHA256: `EF7866754A649840932288BF5DB22D159AED49A5B0EA7769296155C43C146721`.
The assembly references `YENİ-BİLEZİK-04.SLDPRT` and four instances of
`ELMAS.SLDPRT`. Inspected in SOLIDWORKS 2023 SP5 through its feature tree,
sketches, component transforms, mass properties, and independent STEP exports.

[Source manifest](https://github.com/sunzhenchuan007/benchcad-2/blob/ff5d31476178264f14e2cb70558b5c78fbf1c57f/docs/assets/refs/twisted_gemstone_bracelet_asm/source_manifest.json)
and the issue's reference images preserve the measurement basis. The original
author and redistribution license are unverified, so the native archive is not
republished. All ranges are **proportion**: one supplied model establishes no
catalog range, manufacturing tolerance, strength rating, or jewelry standard.

| Native quantity | Measurement (mm unless stated) |
|---|---:|
| Straight sweep path | 76.2 |
| Circular profile radius | 0.635 |
| First sweep axis offset from the common spine | 1.32471928 |
| Distance between the two eccentric sweep axes | 2.54 |
| Twist / circular array | 4 turns / 5 instances |
| Additional mirrored strips | 5 |
| Nominal seat-centre radius R | 12.62815122 |
| Seat outside radius B | 4.77865370 |
| Seat cavity radius | 3.50865370 |
| Radial sphere trims | 8.98756303 / 15.39899389 |
| Gem circumdiameter / height | 6.11754694 / 4.35786021 |
| Gem girdle thickness / crown height | 0.25 / 1.50 |
| Gem table recess diameter / depth | 1.80609106 / 0.05 |

The reconstructed drawing labels the seat radius B. The file is called a
bracelet, but its small native dimensions
are retained as a geometric reference, without claiming adult wrist sizing.

## Reconstruction and requested repairs

The source contains a central round spine plus ten eccentric twisted strips
and five selected mirrored strips. A source circle lies obliquely to its
straight path; replacing these strips with circular pipes would lose their
flattened appearance. `_bridge()` reconstructs the eccentric paths, rotates
the cross sections by the measured bend-frame direction, and maps each span
onto the circular centreline. Projected sections are interpolated by periodic
splines and lofted with seam correspondence retained explicitly. These are
smooth B-spline faces, not polygonal strips.

The bridge approximation uses 20 intervals per exposed quarter span and 16
points around each projected section. Path-normal projection is an explicit
cross-kernel approximation to SOLIDWORKS Flex, not an exact reproduction of its
deformed surfaces. The Boolean tolerance is 0.0001 mm in the native working
scale, and all output dimensions then scale uniformly with R. The braid's
offset and section radius retain fixed native proportions to R.

The contributor explicitly requested correction of source defects:

- Open all four spherical cavities; the native part has only three.
- Place seats at exact quarter turns instead of the slightly irregular sketch
  positions, and keep strip end caps inside the seats.
- Apply inner/outer spherical trims to seats, preserving complete braid
  surfaces instead of clipping strips into protruding tips.
- Exclude the hidden construction disc.
- Use four matching gem seats with positive setting clearance. The native
  assembly's local 0.6 mm chamfer is replaced by this consistent seat geometry.

The spherical seat surfaces provide the rounded form; there are no fabricated
fillets or assumed edge radii. Gemstone faces are reconstructed analytically:
16 pavilion triangles, 16 girdle faces, 24 crown triangles, an octagonal table,
and a shallow circular recess. The nominal gem has 59 faces and volume
59.02477207 mm³, versus native 59.02477220 mm³.

## Parameters and constraints

R sets the overall size. Seat radius B, wall W, gem diameter G and height H
vary through coupled proportion bands. Easy uses tight bands around the native
ratios; medium and hard widen them. The setting-tool enlargement is C = 0.004 G.
The actual normal gap is smaller than C because of the inclined facets; C is
not a certified tolerance or a claim of mechanical retention. This geometric
assembly does not model adhesive or prongs.

`check()` enforces positive dimensions, separated neighbouring seats, a
positive spherical shell, a girdle that fits the cavity equator, and the stated
shape-preserving proportion bands. The nominal assembly has five valid solids,
zero pairwise intersection volume, and a 0.0157741 mm minimum gem-to-seat gap.
The repairs intentionally change the body volume; it is not presented as an
exact native-body replica.

## Verification

Full local `bench2 validate`: easy/medium/hard each 4/4, 12/12 unique shapes,
five non-degenerate solids in every sample. An additional BRep validity audit
passed for all 60 sampled solids. Ruff lint passes.

All five official previews are generated with `bench2 preview --per-diff 1`,
including minimum/maximum draws, orthographic/cutaway views and component
evidence. Extreme instances also pass the five-solid validity audit. The
standard renderer suppresses shallow-angle facet edges; the gem remains a
59-face BRep even where a preview shades its crown smoothly.
