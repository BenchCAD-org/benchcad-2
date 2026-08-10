# vertical_latch_toggle_clamp Notes

## Scope and evidence

This family is the static five-component GN 851.1-T3 configuration. It does
not claim to implement the four-component T variant or a movable toggle
mechanism. The fixed pose follows the supplied 851.1-160-T3 STEP reference and
the official JW Winco / Ganter standard sheet.

Local STEP evidence used during reconstruction:

- file: `851.1-160-T3.step`
- SHA-256: `027CE979C1112FB7162DFD0D65D422B844BF9E3B57397F61D4B2239180546007`
- observed component bodies: base frame, U-bolt latch, lower fork block,
  adjuster block, and handle/linkage pack

The STEP file is reconstruction evidence only. `part.py` builds every body
parametrically and does not import the STEP.

## Catalog rows

The three sampled identifiers are 160, 320, and 700. They are size identifiers,
not force values. The official holding capacities are separate catalog data.
All dimensions in `spec.py` are the standard sheet's inch values converted to
millimetres and rounded to 0.1 mm.

For the complete 160 row, the model receives:

`a1=5.1, a2=24.9, b1=25.9, b2=35.1, b3=21.1, b4=25.4, b5=14.0,
d1=4.0, d2=4.3, h1=37.1, h2=9.9, l1=68.1, l2=4.6, m1=22.1,
m2=6.6, m3=13.0, m4=6.6, m5=14.2, s=2.0 mm`.

## Symbol to geometry mapping

| Symbol | Geometry driven in `part.py` |
| --- | --- |
| `a1` | U-bolt and adjuster X-axis datum |
| `a2` | adjuster upper Y datum |
| `b1` | base rail length and mounting-hole X placement |
| `b2` | overall Z scale |
| `b3` | lower fork outside width |
| `b4` | lower fork-block height |
| `b5` | U-bolt leg spacing |
| `d1` | U-bolt rod and associated proportional bosses |
| `d2` | mounting, fork, adjuster, and linkage holes |
| `h1` | overall Y scale |
| `h2` | adjuster lower Y datum |
| `l1` | handle/base X scale |
| `l2` | front catch-tab length |
| `m1` | transverse mounting-hole spacing |
| `m2` | first mounting-hole X offset term |
| `m3` | longitudinal mounting-hole spacing |
| `m4` | lower fork-hole center from the fork datum |
| `m5` | vertical spacing between fork holes |
| `s` | actual base sheet thickness |

Undimensioned stamped contours, bend radii, ribs, bosses, and the handle grip
retain their 160-T3 STEP proportions and scale from the nearest published
envelope dimension. Elliptical bosses use true CadQuery ellipses rather than
segmented polygons.

`fit_clearance` is the one non-catalog geometric parameter. It varies only a
hidden handle-to-frame mating relief from 0.05 to 0.20 mm, preserving the
catalog envelopes while representing a plausible manufacturing clearance.

## Static assembly and deviations

- `handle_angle` was removed. A rigid rotation of the combined handle/linkage
  body was not a valid representation of the toggle mechanism.
- `r`, `w1`, and `w2` are operating range/stroke data, not independent static
  body dimensions. They are intentionally omitted rather than attached to
  unrelated geometry.
- The unreachable T/no-U-bolt branch was removed. Component metadata now
  consistently describes the five-body T3 assembly.
- U-bolt guide axes are shared with the adjuster-hole axes. Hidden mating
  reliefs are cut from the handle/linkage body so all component pairs have
  zero positive-volume intersection for the 160, 320, and 700 rows.
- Threads, locknuts, split pins, spring wire, and exact production stamping
  radii are omitted or proportion-derived where the standard sheet gives no
  independent dimensions.
