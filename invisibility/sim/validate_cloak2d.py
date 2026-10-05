"""Cross-check sim/cloak2d.py (layered cylinders, TM and TE) against an independent NGSolve FEM solve."""
import json, sys, time
from pathlib import Path
import numpy as np
import ngsolve as ng
from netgen.geom2d import SplineGeometry
from scipy.special import hankel1
sys.path.insert(0, str(Path(__file__).parent))
from cloak2d import coeffs

lam = 1.0; k = 2 * np.pi / lam
radii = [0.3, 0.4, 0.5]; m_core, shells = 2.0, [1.5, 1.2 + 0.05j]
eps_vals = {"core": m_core ** 2, "s1": shells[0] ** 2, "s2": shells[1] ** 2}

geo = SplineGeometry()
geo.AddCircle((0, 0), 2.4, leftdomain=5, bc="outer")
geo.AddCircle((0, 0), 1.7, leftdomain=4, rightdomain=5)
geo.AddCircle((0, 0), radii[2], leftdomain=3, rightdomain=4)
geo.AddCircle((0, 0), radii[1], leftdomain=2, rightdomain=3)
geo.AddCircle((0, 0), radii[0], leftdomain=1, rightdomain=2)
for i, (nm, h) in enumerate([("core", .03), ("s1", .03), ("s2", .03), ("air", .06), ("pml", .06)], 1):
    geo.SetMaterial(i, nm); geo.SetDomainMaxH(i, h)
mesh = ng.Mesh(geo.GenerateMesh(maxh=0.06)); mesh.Curve(4)
mesh.SetPML(ng.pml.Radial(rad=1.7, alpha=1j, origin=(0, 0)), "pml")
eps = mesh.MaterialCF(eps_vals, default=1)
scat = mesh.Materials("core|s1|s2")
fes = ng.H1(mesh, order=5, complex=True); u, v = fes.TnT()
uinc = ng.exp(1j * k * ng.x)
pts = [(0.8, 0.1), (0.0, 1.1), (-0.9, -0.4), (0.6, -0.7)]
r = np.array([np.hypot(*p) for p in pts]); ph = np.array([np.arctan2(p[1], p[0]) for p in pts])
out = {}
for pol in ("TM", "TE"):
    t = time.time()
    A = ng.BilinearForm(fes); f = ng.LinearForm(fes)
    if pol == "TM":
        A += (ng.grad(u) * ng.grad(v) - k ** 2 * eps * u * v) * ng.dx
        f += k ** 2 * (eps - 1) * uinc * v * ng.dx(definedon=scat)
    else:
        A += (1 / eps * ng.grad(u) * ng.grad(v) - k ** 2 * u * v) * ng.dx
        f += -(1 / eps - 1) * ng.CoefficientFunction((1j * k * uinc, 0)) * ng.grad(v) * ng.dx(definedon=scat)
    A.Assemble(); f.Assemble()
    g = ng.GridFunction(fes); g.vec.data = A.mat.Inverse(fes.FreeDofs(), inverse="umfpack") * f.vec
    num = np.array([g(mesh(*p)) for p in pts])
    n, b = coeffs(shells, radii, k, pol=pol, core="dielectric", m_core=m_core)
    ref = np.array([np.sum(1j ** n * b * hankel1(n, k * rr) * np.exp(1j * n * pp)) for rr, pp in zip(r, ph)])
    err = float(np.max(np.abs(num - ref)) / np.max(np.abs(ref)))
    out[pol] = dict(ok=err < 5e-3, rel_err=err, seconds=round(time.time() - t, 1))
    print(f"[{'PASS' if err < 5e-3 else 'FAIL'}] cloak2d {pol} layered rod vs NGSolve FEM: max rel. error {err:.2e}")
Path(__file__).with_name("validation_cloak2d.json").write_text(json.dumps(out, indent=1))
