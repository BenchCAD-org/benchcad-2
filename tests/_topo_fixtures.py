"""Topology fixtures for the structural tests: handles and enclosed voids."""

import cadquery as cq

S = 60.0


def plain():
    return cq.Workplane("XY").box(S, S, 20.0).val()


def _void(x):
    return cq.Workplane("XY").box(8, 8, 8).translate((x, 0, 0)).val()


def with_holes(n):
    w = cq.Workplane("XY").box(S, S, 20.0)
    if n:
        pts = [(-20.0 + i * 8.0, 20.0) for i in range(n)]
        w = w.faces(">Z").workplane().pushPoints(pts).hole(3.0)
    return w.val()


def with_voids(n):
    s = plain()
    for i in range(n):
        s = s.cut(_void(-20.0 + i * 20.0))
    return s


def hole_and_void():
    """One through hole and one enclosed void that do not intersect."""
    s = with_voids(1)
    return (
        cq.Workplane("XY").add(s)
        .faces(">Z").workplane().pushPoints([(20.0, 20.0)]).hole(3.0).val()
    )
