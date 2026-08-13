# ACT field-tray pipe clamp notes

## Source mapping

The 24 ACT body rows and the group-coupled DP/HKS W55 table are transcribed in
Issue #90 from *STAUFF Catalogue 1 - STAUFF Clamps*, version 06/2026, pages
83-84, 90 and 93. `size_index` selects one body row; its group selects exactly
one DP/HKS row, preventing cross-group combinations.

Geometry uses body `D1`, `L1`, `L2`, `H`, and width 30; DP `L1`, `L2`, `B`,
`S`, and hole `D`; HKS `H2`, `H3`, head `B`, and head `L`; MUS-HKS M6 nut
height 5 and across-flats 10.

## Deliberate simplifications

- Each clamp half includes two longitudinal ACE contact strips. Their section
  and embed are undimensioned, so `strip_d` and `strip_embed` are labelled
  `proportion` rather than catalogue dimensions.
- Fine ribs, cavities, drainage channels, fillets, chamfers, draft, threads,
  and Biloc deformation are omitted.
- The non-standard HKS retains the catalogue's 6.1 mm hammerhead width and uses
  a visible ISO 261 M6 coarse-pitch / ISO 68-1 simplified 60-degree external
  thread on its shank. MUS-HKS uses the reviewed ISO 4032 M6 nut envelope with
  the matching modeled internal groove from the standard-components demo.
- Clamp-half and DP-cover holes remain unthreaded clearance holes: they guide
  the HKS shank but do not form the threaded joint.
- A 0.2 mm display gap separates cover/head surfaces. Tray thickness is not
  published and no tray is emitted; this is presentation-only.

## Entity contract

`build()` returns a named `cq.Assembly` with seven shape-bearing nodes: two
`clamp_half` instances, one `cover_plate`, two `hks_bolt` instances, and two
`lock_nut` instances. ACE strips are fused features. Pipe and tray are excluded.
