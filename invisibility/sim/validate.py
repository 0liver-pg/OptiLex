"""Validate the simulation stack against exact answers. Run: .venv/bin/python sim/validate.py
Each check prints PASS/FAIL with the measured error and wall time. Meep is validated separately (validate_meep.py)."""
import time, json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from analytic import cylinder_tm_widths, cylinder_tm_field

results = {}


def check(name, fn):
    t = time.time()
    try:
        ok, detail = fn()
    except Exception as e:  # report, don't abort the suite
        ok, detail = False, f"error: {e!r}"
    dt = time.time() - t
    results[name] = dict(ok=bool(ok), detail=detail, seconds=round(dt, 2))
    print(f"[{'PASS' if ok else 'FAIL'}] {name:<34} {dt:7.2f}s  {detail}", flush=True)


def mie_cross():
    import scattnlay, miepython
    m, x = 1.5 + 0.01j, 5.0
    _, qext, qsca, *_ = scattnlay.scattnlay(np.array([x]), np.array([m]))
    qext2, qsca2, *_ = miepython.efficiencies_mx(m, x) if hasattr(miepython, "efficiencies_mx") else miepython.mie(m, x)
    err = max(abs(qext - qext2) / qext2, abs(qsca - qsca2) / qsca2)
    return err < 1e-6, f"scattnlay vs miepython Qext={float(qext):.6f}/{float(qext2):.6f} rel.err={float(err):.1e}"


def mie_extinction_paradox():
    import scattnlay
    _, qext, *_ = scattnlay.scattnlay(np.array([2000.0]), np.array([1.5 + 0j]))
    return abs(qext - 2) < 0.02, f"Qext(x=2000, m=1.5)={float(qext):.4f} (geometric-optics limit 2)"


def mie_scattering_cancellation():
    """Plasmonic-shell cloak (Alu & Engheta 2005): a low-permittivity shell cancels a small dielectric core's dipole."""
    import scattnlay
    x_core, x_shell, eps_core = 0.45, 0.5, 4.0
    bare = scattnlay.scattnlay(np.array([x_core]), np.array([np.sqrt(eps_core)]))[2]
    best = min((scattnlay.scattnlay(np.array([x_core, x_shell]), np.array([np.sqrt(eps_core), np.sqrt(es + 0j)]))[2], es)
               for es in np.linspace(-6, 0.9, 400))
    red = bare / best[0]
    return red > 10, f"Qsca bare={float(bare):.3e}, best shell eps={best[1]:.2f} Qsca={float(best[0]):.3e} ({float(red):.0f}x lower)"


def cylinder_series():
    s, e = cylinder_tm_widths(2.0, 1.0, 1.5)
    s2, e2 = cylinder_tm_widths(1.5 + 0.05j, 800.0, 1.0)  # small loss damps the sharp internal resonances of a lossless rod
    ok = abs(s - e) / e < 1e-10 and abs(e2 / 1600 - 2) < 0.01
    return ok, f"lossless sigma_sca=sigma_ext ({s:.6f}/{e:.6f}); large lossy cylinder sigma_ext/2a={e2/1600:.4f} (limit 2)"


def ceviche_point_source():
    """2D FDFD point source vs the free-space Green's function: checks dispersion, PML and normalisation-free phase.
    ceviche uses the exp(+i w t) convention, so its outgoing wave is H0^(2), the conjugate of this file's H0^(1)."""
    import ceviche
    from scipy.special import hankel2 as hankel1
    lam, dl, N, npml = 1.0, 0.025, 300, 30
    omega = 2 * np.pi * 299792458 / (lam * 1e-6)
    sim = ceviche.fdfd_ez(omega, dl * 1e-6, np.ones((N, N)), [npml, npml])
    src = np.zeros((N, N)); src[N // 2, N // 2] = 1
    _, _, Ez = sim.solve(src)
    k = 2 * np.pi / lam
    r = np.arange(20, 96) * dl
    num = Ez[N // 2 + np.arange(20, 96), N // 2]
    ref = hankel1(0, k * r)
    ratio = num / ref
    ratio /= ratio[0]
    err = np.max(np.abs(ratio - 1))
    return err < 0.05, f"|E/H0| normalised deviation over 0.5-2.4 lambda: {err:.3f} (dl=lambda/40)"


def ngsolve_cylinder():
    """FEM scattered field of a dielectric cylinder (radial PML) vs the exact series."""
    import ngsolve as ng
    from netgen.geom2d import SplineGeometry
    lam, a, m = 1.0, 0.5, 2.0
    k = 2 * np.pi / lam
    geo = SplineGeometry()
    geo.AddCircle((0, 0), 2.5, leftdomain=3, bc="outer")
    geo.AddCircle((0, 0), 1.8, leftdomain=2, rightdomain=3)
    geo.AddCircle((0, 0), a, leftdomain=1, rightdomain=2)
    for i, (nm, h) in enumerate([("cyl", 0.04), ("air", 0.06), ("pml", 0.06)], 1):
        geo.SetMaterial(i, nm); geo.SetDomainMaxH(i, h)
    mesh = ng.Mesh(geo.GenerateMesh(maxh=0.06)); mesh.Curve(4)
    mesh.SetPML(ng.pml.Radial(rad=1.8, alpha=1j, origin=(0, 0)), "pml")
    eps = mesh.MaterialCF({"cyl": m ** 2}, default=1)
    fes = ng.H1(mesh, order=5, complex=True)
    u, v = fes.TnT()
    A = ng.BilinearForm(fes)
    A += (ng.grad(u) * ng.grad(v) - k ** 2 * eps * u * v) * ng.dx
    A.Assemble()
    uinc = ng.exp(1j * k * ng.x)
    f = ng.LinearForm(fes)
    f += k ** 2 * (eps - 1) * uinc * v * ng.dx(definedon=mesh.Materials("cyl"))
    f.Assemble()
    gfu = ng.GridFunction(fes)
    gfu.vec.data = A.mat.Inverse(fes.FreeDofs(), inverse="umfpack") * f.vec
    pts = [(0.9, 0.0), (0.0, 1.2), (-1.0, 0.3), (0.7, -0.8)]
    num = np.array([gfu(mesh(*p)) for p in pts])
    r = np.array([np.hypot(*p) for p in pts]); ph = np.array([np.arctan2(p[1], p[0]) for p in pts])
    ref = cylinder_tm_field(m, a, lam, r, ph)
    err = np.max(np.abs(num - ref)) / np.max(np.abs(ref))
    return err < 0.02, f"max rel. error of scattered E_z at 4 points: {err:.2e} (order 5, h~lambda/17)"


def mitsuba_flip():
    import mitsuba as mi, flip_evaluator as flip
    mi.set_variant("scalar_rgb")  # the LLVM variants need libLLVM (brew install llvm, about 1.5 GB); scalar is slower but exact
    scene = mi.load_dict(mi.cornell_box())
    a = np.clip(np.array(mi.render(scene, spp=64)), 0, 1)
    b = np.clip(np.array(mi.render(scene, spp=64, seed=7)), 0, 1)
    err_same = float(flip.evaluate(a, a, "LDR")[1])
    err_noise = float(flip.evaluate(a, b, "LDR")[1])
    ok = err_same < 1e-6 and 0 < err_noise < 0.2
    return ok, f"variant={mi.variant()} render {a.shape}; FLIP(same)={err_same:.2e}, FLIP(two noise seeds)={err_noise:.3f}"


for name, fn in [("Mie: scattnlay vs miepython", mie_cross), ("Mie: extinction paradox", mie_extinction_paradox),
                 ("Mie: scattering-cancellation shell", mie_scattering_cancellation), ("Cylinder series self-check", cylinder_series),
                 ("ceviche FDFD vs H0 Green fn", ceviche_point_source), ("NGSolve FEM vs exact cylinder", ngsolve_cylinder),
                 ("Mitsuba 3 render + FLIP", mitsuba_flip)]:
    check(name, fn)
Path(__file__).with_name("validation_results.json").write_text(json.dumps(results, indent=1))
