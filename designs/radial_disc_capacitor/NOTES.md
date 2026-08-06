# radial_disc_capacitor

Generic radial disc capacitor family built from a user-provided STEP reference and proportion-based ranges.

## Geometric interpretation

- `body_diameter`: overall disc diameter
- `body_thickness`: axial thickness of the disc body
- `lead_spacing`: center-to-center spacing between the two radial leads
- `lead_diameter`: lead wire diameter
- `lead_length`: exposed lead length below the body
- `lead_embed`: overlap used to fuse the leads into the body

## Modeling notes

- The body is a simple cylindrical disc.
- The two leads are straight radial wires placed symmetrically about the centerline.
- The default parameter set is chosen to produce a single valid solid with clean fusion.
- Ranges marked as `proportion` are benchmark sampling ranges, not catalog limits.
