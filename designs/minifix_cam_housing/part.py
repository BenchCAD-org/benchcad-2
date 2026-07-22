"""minifix_cam_housing — the parametric part.

Write plain parametric CadQuery here: NAMED parameters, build the solid, bind it
to `result`, return it. No dictionaries, no string building, no code generation
— bench2 derives each instance's stand-alone program from this body
automatically (parameters become module globals; any bench2.geomlib helper you
call is inlined, so the emitted program stays self-contained).

Then:  uv run bench2 validate minifix_cam_housing   and   uv run bench2 preview minifix_cam_housing
Interface and examples: docs/DESIGN_SPEC.md
"""

import cadquery as cq


def build(length):  # TODO: your named parameters — names must match spec.py PARAM_SPEC
    # TODO: build the part with ordinary CadQuery calls, then bind `result`.
    result = cq.Workplane("XY").box(length, length / 2.0, length / 4.0)
    return result
