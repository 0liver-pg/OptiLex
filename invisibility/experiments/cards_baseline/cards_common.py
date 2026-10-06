"""Shared definitions for the four problem cards (P1-P4): canonical parameters, exact metrics, fast adversary.

Object: PEC cylinder radius a = 1 (unit length), TM (E_z), plane wave along +x, vacuum outside r = b.
Band: uniform window k in [k_c(1 - B/2), k_c(1 + B/2)], canonical k_c a = pi/2 (a = lambda_c/4), b = 3a, B = 0.1.
All final numbers are re-scored with sim/cloak2d.py (the shared verifier); fastcyl.py is only used inside search loops.
"""
import sys, pathlib
import numpy as np
from scipy.optimize import minimize

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "sim"))
sys.path.insert(0, str(HERE))
import cloak2d  # noqa: E402
import fastcyl  # noqa: E402

A, KC, BOUT, BW = 1.0, np.pi / 2, 3.0, 0.1
import os
EPS_MIN, EPS_MAX = 1.0, float(os.environ.get('CARD_EPS_MAX', 6.0))
SECTOR_CENTER, SECTOR_HALF = np.pi, np.pi / 2   # backward half-plane |phi| >= pi/2


# ---------- exact metrics (cloak2d) ----------
def ext_width(m, radii, k):
    return cloak2d.widths(m, radii, k, core="pec")[1]


def sca_width(m, radii, k):
    return cloak2d.widths(m, radii, k, core="pec")[0]


def sector_width_c2d(m, radii, k, center=SECTOR_CENTER, half=SECTOR_HALF):
    n, b = cloak2d.coeffs(m, radii, k, core="pec")
    return fastcyl.sector_width(b, n, k, center, half)


def channel_width_c2d(m, radii, k, order):
    """Channel |n| = order width: (4/k)(|b_n|^2 + |b_-n|^2) (n != 0) or (4/k)|b_0|^2; equals channel extinction if lossless."""
    n, b = cloak2d.coeffs(m, radii, k, core="pec")
    sel = np.abs(n) == order
    return float(4 / k * np.sum(np.abs(b[sel]) ** 2))


def channel_ext_c2d(m, radii, k, order):
    n, b = cloak2d.coeffs(m, radii, k, core="pec")
    sel = np.abs(n) == order
    return float(-4 / k * np.sum(b[sel].real))


def band(fn, B=BW, n=41, kc=KC):
    return cloak2d.band_average(fn, kc, B, n=n) if B > 0 else float(fn(kc))


def dense_uniform(fn, B=BW, npts=201, kc=KC):
    """Trapezoid average on a dense uniform grid: guards against designs that exploit quadrature nodes."""
    if B == 0:
        return float(fn(kc))
    ks = np.linspace(kc * (1 - B / 2), kc * (1 + B / 2), npts)
    v = np.array([fn(k) for k in ks])
    return float(np.trapezoid(v, ks) / (ks[-1] - ks[0])), float(v.max())


def lorentzian_imF(m_of_k, radii, B=BW, kc=KC, N=60):
    """Im F(k~), F = -(4i/k) sum_n b_n, at k~ = k_c(1 + i B/2): equals int_0^inf sigma_ext(k)[L(k)+L(-k)] dk with
    Lorentzian L of half-width k_c B/2 (Hashemi 2012 identity; even extension since T(-k*) = -T(k)*).
    m_of_k(k) must be the analytic continuation of the layer indices (constant for non-dispersive real eps)."""
    kt = kc * (1 + 0.5j * B)
    _, b = cloak2d.coeffs(m_of_k(kt), radii, kt, core="pec", nmax=N)
    return float(np.imag(-4j / kt * np.sum(b)))


# ---------- fast adversary ----------
def search(fun, bounds, seeds=8, rng=0, x0s=(), maxiter=300):
    """Multi-start L-BFGS-B (finite-difference gradients), mirroring cloak2d.optimize_layers. Returns (best, x, all)."""
    gen = np.random.default_rng(rng)
    starts = [np.asarray(x, float) for x in x0s] + [np.array([gen.uniform(lo, hi) for lo, hi in bounds]) for _ in range(seeds)]
    best, allv = (np.inf, None), []
    for x0 in starts:
        r = minimize(fun, x0, method="L-BFGS-B", bounds=bounds, options=dict(maxiter=maxiter))
        allv.append(float(r.fun))
        if r.fun < best[0]:
            best = (float(r.fun), r.x.copy())
    return best[0], best[1], allv


def layered_radii(L, a=A, b=BOUT):
    return list(np.linspace(a, b, L + 1))
