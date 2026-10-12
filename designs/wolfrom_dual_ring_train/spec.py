"""Issue #187 source rows, coupled sampling, and assembly constraints."""

import math

_ROWS = [(14, 20, 18, 54, 52), (16, 22, 20, 60, 58),
         (12, 24, 22, 60, 58), (18, 21, 20, 60, 59)]
_NAMES = ["sun_zs", "step_a_za", "step_b_zb",
          "ring1_zr1", "ring2_zr2"]
_ISSUE = "https://github.com/BenchCAD-org/benchcad-2/issues/187, four-row tooth ladder"


def _entry(desc, unit, bounds, source, **extra):
    return dict(desc=desc, unit=unit, range=dict(zip(("easy", "medium", "hard"), bounds)),
                source=source, **extra)


PARAM_SPEC = {
    "module_m": _entry("Tooth module m", "mm", [(1, 1.25), (0.8, 2), (0.8, 2)],
                       "ISO 54 module series as specified by issue #187",
                       choices={"easy": [1, 1.25], "medium": [0.8, 1, 1.25, 1.5, 2],
                                "hard": [0.8, 1, 1.25, 1.5, 2]},
                       coverage=[0.8, 1, 1.25, 1.5, 2]),
    "row": _entry("Coupled source tooth-count row", "", [(0, 1), (0, 3), (0, 3)],
                        _ISSUE, integer=True, coverage=[0, 1, 2, 3]),
    "n_planets": _entry("Identical stepped planets at equal angular spacing", "",
                        [(2, 2), (2, 3), (2, 3)],
                        "Derived three-mesh congruences and tip clearance; NOTES.md",
                        integer=True, refine=True, coverage=[2, 3]),
    "width_b": _entry("Toothed face width b at each axial station", "mm",
                           [(8, 15), (6.4, 24), (4.8, 28)],
                           "proportion: 8-12m / 8-12m / 6-14m; issue drawing b=24 at m=2",
                           refine=True),
    "gap_g": _entry("Axial separation g between toothed sections", "mm",
                              [(0.4, 1.25), (0.32, 3), (0.32, 4)],
                              "proportion: positive space for rigid stepped-planet waist",
                              refine=True),
    "rim_t": _entry("Material thickness t beyond internal gear root", "mm",
                              [(4, 6.25), (2.4, 12), (1.6, 14)],
                              "proportion: 4-5m / 3-6m / 2-7m; drawing implies t=10 at m=2",
                              refine=True),
    "input_deg": _entry("Sun input rotation from the timed assembly datum", "deg",
                              [(0, 0), (0, 360), (0, 3600)],
                              "proportion: operating pose; all members follow Willis equations"),
}
for _i, _name in enumerate(_NAMES):
    _easy = [_ROWS[k][_i] for k in (0, 1)]
    _all = [row[_i] for row in _ROWS]
    PARAM_SPEC[_name] = _entry(_name.replace("_", " "), "",
                              [(min(_easy), max(_easy)), (min(_all), max(_all)),
                               (min(_all), max(_all))], _ISSUE,
                              integer=True, refine=True)


def refine(p, difficulty, rng):
    row = _ROWS[int(p["row"])]
    p.update(zip(_NAMES, row))
    p["n_planets"] = int(rng.choice([2, 3])) if int(p["row"]) == 2 else (
        3 if int(p["row"]) == 3 else 2)
    m = p["module_m"]
    width_band = (6, 14) if difficulty == "hard" else (8, 12)
    gap_band = (0.4, {"easy": 1, "medium": 1.5, "hard": 2}[difficulty])
    rim_band = {"easy": (4, 5), "medium": (3, 6), "hard": (2, 7)}[difficulty]
    p["width_b"] = round(m*float(rng.uniform(*width_band)), 2)
    p["gap_g"] = round(m*float(rng.uniform(*gap_band)), 2)
    p["rim_t"] = round(m*float(rng.uniform(*rim_band)), 2)


def check(p):
    bad = []
    teeth = tuple(p[name] for name in _NAMES)
    s, a, b, r1, r2 = teeth
    n = p["n_planets"]
    if any(int(x) != x or x <= 0 for x in (*teeth, n)):
        return ["tooth counts and planet count must be positive integers (gear definition)"]
    s, a, b, r1, r2, n = map(int, (*teeth, n))
    row = p["row"]
    if int(row) != row or not 0 <= row < len(_ROWS) or teeth != _ROWS[int(row)]:
        bad.append("tooth counts must stay coupled to one complete issue #187 row")
    if r1 != s+2*a or r2 != s+a+b:
        bad.append("both stations must be coaxial at one module (issue #187)")
    if a == b or r2*a == b*r1:
        bad.append("held and output rings must not coincide (Willis degeneracy, NOTES.md)")
    d = s+a
    if (2*d) % n or (d*(a+b)) % (n*math.gcd(a, b)):
        bad.append("all three meshes must admit identical rigid planet clocking (NOTES.md)")
    if d*math.sin(math.pi/n) <= max(a,b)+2:
        bad.append("adjacent external planet tip circles intersect (geometry, NOTES.md)")
    m, width, gap, rim = (p[k] for k in (
        "module_m", "width_b", "gap_g", "rim_t"))
    if m <= 0 or width <= 0 or gap <= 0 or rim <= 0:
        return bad + ["module and physical widths must be strictly positive"]
    root = m*min(a,b)/2 - 1.25*m
    bore = 0.20*m*min(a,b) + 0.20*m
    if bore >= 0.70*root:
        bad.append("pin bore must leave positive material in the rigid planet waist")
    if 0.25*m*s >= m*s/2 - 1.25*m:
        bad.append("sun shaft must remain inside the sun root circle")
    if max(1.5*m, 0.30*width) + 0.25*m >= 8*m:
        bad.append("input shaft must project behind the carrier plate")
    return bad
