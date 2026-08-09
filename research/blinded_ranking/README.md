# Blinded human-ranking set (research)

Twelve reference/candidate pairs rendered under one camera convention, four
oblique views each, for a blinded visual ranking experiment on PR #197.

Source geometry is the public **BenchCAD** dataset
(<https://huggingface.co/datasets/BenchCAD/BenchCAD>), released **CC BY 4.0**.
Candidates are model outputs evaluated against it.

Case identities, metric values and rankings are deliberately not recorded here:
the point of the set is that a human ranks it without seeing any score.

## within_reference/

The correct experimental unit: **one fixed reference, several candidate
reconstructions of that same part**, ranked within the group. Cross-part
comparisons ("is this washer better than this spring?") are ill-posed and the
flat A–L set above is superseded by these sheets.

Candidates are real model outputs from two independent runs, selected by run
and round position only — never by any metric value.
