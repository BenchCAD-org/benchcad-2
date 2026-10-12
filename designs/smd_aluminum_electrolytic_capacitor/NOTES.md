# smd_aluminum_electrolytic_capacitor

Generic SMD aluminum electrolytic capacitor family built from a user-provided
STEP reference and proportion-based sampling ranges.

## STEP interpretation

- The reference is a CAP-SMD style aluminum electrolytic capacitor, not a
  through-hole radial disc capacitor.
- The visible package has a vertical cylindrical can, a molded rectangular
  base, and two surface-mount terminal pads.
- The measured reference envelope is approximately 8.8 mm x 8.1 mm x 9.3 mm.
- The cylindrical can diameter is approximately 6.3 mm.
- The can body above the base is approximately 7.7 mm tall.
- The base is approximately 1.6 mm thick.

## Geometric parameters

- `body_diameter`: can diameter.
- `can_height`: can height above the molded SMD base.
- `base_length`: overall base length, including the terminal carrier.
- `base_width`: overall base width.
- `base_thickness`: molded plastic base thickness.
- `terminal_span`: placement span for the two SMD terminal pads.
- `terminal_width`: visible terminal pad width.
- `terminal_thickness`: terminal pad thickness.
- `rim_radius`: small can rim / edge blend radius.

## Modeling notes

- The formal CAD is self-contained and does not load the source STEP file.
- The reference STEP is used only as measurement evidence during development.
- The current stable version matches the recovered 79-face topology and bbox
  target (`7.3000003 x 6.6000003 x 7.7000003 mm`) with a valid single solid.
- Its remaining known limitation is volume: `251.6673226199046 mm^3`, which is
  `1.1181984258233229 mm^3` below the historical target. Existing recovered
  evidence does not uniquely identify the missing positive-volume feature.
- Ranges marked as `proportion` are benchmark sampling ranges, not catalog
  limits or capacitance-to-size rules.
- Manufacturer branding, printed polarity marks, material color, and fine
  stamping details are deliberately omitted.
