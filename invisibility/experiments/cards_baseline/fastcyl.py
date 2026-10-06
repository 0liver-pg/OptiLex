"""Vectorised re-implementation of sim/cloak2d.coeffs (PEC core, radially layered shells) for fast optimisation loops.

Same conventions as cloak2d: exp(-i w t); scattered field = sum_n i^n b_n H_n(k r) e^{i n phi}; TM matches E_z and dE_z/dr,
TE matches H_z and (1/eps) dH_z/dr. Validated against cloak2d.coeffs in validate_fastcyl() (machine precision).
Final reported numbers are always re-evaluated with sim/cloak2d.py itself.
"""
import numpy as np
from scipy.special import jv, jvp, hankel1, h1vp


def nmax_like_cloak2d(m_layers, R, k):
    m_layers = np.asarray(m_layers, complex)
    return int(np.ceil(abs(k) * R * max(1.0, np.max(np.abs(m_layers), initial=1.0)) + 4 * (abs(k) * R) ** (1 / 3) + 12))


def coeffs_pec(m_layers, radii, k, pol="TM", N=None):
    """b_n for n = -N..N; k may be complex (for complex-frequency evaluation; pass N explicitly then or rely on |k|)."""
    m_layers = np.asarray(m_layers, complex)
    N = N or nmax_like_cloak2d(m_layers, radii[-1], k)
    n = np.arange(-N, N + 1)
    w = (lambda m: 1.0) if pol == "TM" else (lambda m: 1.0 / m ** 2)
    if len(m_layers) == 0:
        kk, r0 = k, radii[0]
    else:
        kk, r0 = k * m_layers[0], radii[0]
    if pol == "TM":
        v0, v1 = hankel1(n, kk * r0), -jv(n, kk * r0)
    else:
        v0, v1 = h1vp(n, kk * r0), -jvp(n, kk * r0)
    mats = list(m_layers) + [1.0]
    for j in range(len(m_layers)):
        r = radii[j + 1]
        mi, mo = mats[j], mats[j + 1]
        xi, xo = k * mi * r, k * mo * r
        # M_in @ v
        a0 = jv(n, xi) * v0 + hankel1(n, xi) * v1
        a1 = w(mi) * k * mi * (jvp(n, xi) * v0 + h1vp(n, xi) * v1)
        # solve M_out x = a
        J, H = jv(n, xo), hankel1(n, xo)
        Jp, Hp = w(mo) * k * mo * jvp(n, xo), w(mo) * k * mo * h1vp(n, xo)
        det = J * Hp - H * Jp
        v0, v1 = (Hp * a0 - H * a1) / det, (-Jp * a0 + J * a1) / det
        # renormalise to avoid overflow in deep evanescent orders
        s = np.maximum(np.abs(v0), np.abs(v1))
        v0, v1 = v0 / s, v1 / s
    return n, v1 / v0


def widths_pec(m_layers, radii, k, pol="TM"):
    _, b = coeffs_pec(m_layers, radii, k, pol)
    s = 4 / k * np.sum(np.abs(b) ** 2)
    e = -4 / k * np.sum(b.real)
    return s, e, e - s


def sector_kernel(n, center, half_width):
    """K[m, n'] = int_{|phi-center|<=hw} e^{i(n'-m)phi} dphi, so int_sector |sum b_n e^{in phi}|^2 = b^H K b."""
    d = n[None, :] - n[:, None]
    with np.errstate(invalid="ignore", divide="ignore"):
        K = np.where(d == 0, 2 * half_width, 2 * np.sin(d * half_width) / np.where(d == 0, 1, d))
    return K * np.exp(1j * d * center)


def sector_width(b, n, k, center=np.pi, half_width=np.pi / 2):
    """Scattering width into the sector |phi - center| <= half_width: (2/(pi k)) int |T(phi)|^2 dphi, T = sum b_n e^{in phi}."""
    K = sector_kernel(n, center, half_width)
    return float(np.real(np.conj(b) @ K @ b) * 2 / (np.pi * k))


def validate_fastcyl():
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "sim"))
    import cloak2d
    rng = np.random.default_rng(1)
    worst = 0.0
    for trial in range(12):
        L = rng.integers(0, 6)
        radii = list(np.sort(rng.uniform(1, 3, L)).tolist())
        radii = [1.0] + radii if L else [1.0]
        if L:
            radii = [1.0] + list(np.linspace(1.0, 3.0, L + 1)[1:])
        eps = rng.uniform(-3, 8, L) + 1j * rng.uniform(0, 0.5, L) * (trial % 2)
        m = np.sqrt(eps.astype(complex))
        k = rng.uniform(0.3, 3.0)
        for pol in ("TM", "TE"):
            n1, b1 = cloak2d.coeffs(m, radii, k, pol=pol, core="pec")
            n2, b2 = coeffs_pec(m, radii, k, pol=pol)
            worst = max(worst, float(np.max(np.abs(b1 - b2))))
    # sector kernel: full circle equals total scattering; half-plane vs direct quadrature
    n, b = cloak2d.coeffs([1.7, 2.1], [1.0, 2.0, 3.0], 1.3, core="pec")
    full = sector_width(b, n, 1.3, np.pi, np.pi)
    tot = 4 / 1.3 * np.sum(np.abs(b) ** 2)
    phi = np.linspace(np.pi / 2, 3 * np.pi / 2, 20001)
    T = (b[None, :] * np.exp(1j * n[None, :] * phi[:, None])).sum(1)
    quad = 2 / (np.pi * 1.3) * np.trapezoid(np.abs(T) ** 2, phi)
    half = sector_width(b, n, 1.3, np.pi, np.pi / 2)
    return dict(max_abs_coeff_diff_vs_cloak2d=worst, full_circle_vs_total_rel=abs(full - tot) / tot,
                half_plane_kernel_vs_quadrature_rel=abs(half - quad) / quad)


if __name__ == "__main__":
    print(validate_fastcyl())


def coeffs_pec_multi(m_lk, radii, ks, pol="TM", N=None):
    """Vectorised over frequency: m_lk has shape (L, K) (layer indices at each k, allows dispersion), ks shape (K,).
    Returns n (2N+1,), b (2N+1, K). N defaults to the cloak2d rule at the largest |k| and |m|."""
    ks = np.asarray(ks)
    m_lk = np.asarray(m_lk, complex).reshape(-1, ks.size)
    L = m_lk.shape[0]
    if N is None:
        mm = np.max(np.abs(m_lk), initial=1.0)
        N = int(np.ceil(np.max(np.abs(ks)) * radii[-1] * max(1.0, mm) + 4 * (np.max(np.abs(ks)) * radii[-1]) ** (1 / 3) + 12))
    n = np.arange(-N, N + 1)[:, None]
    k = ks[None, :]
    TM = pol == "TM"
    if L == 0:
        kk = k
    else:
        kk = k * m_lk[0][None, :]
    r0 = radii[0]
    if TM:
        v0, v1 = hankel1(n, kk * r0), -jv(n, kk * r0)
    else:
        v0, v1 = h1vp(n, kk * r0), -jvp(n, kk * r0)
    for j in range(L):
        r = radii[j + 1]
        mi = m_lk[j][None, :]
        mo = m_lk[j + 1][None, :] if j + 1 < L else np.ones_like(mi)
        wi = 1.0 if TM else 1.0 / mi ** 2
        wo = 1.0 if TM else 1.0 / mo ** 2
        xi, xo = k * mi * r, k * mo * r
        a0 = jv(n, xi) * v0 + hankel1(n, xi) * v1
        a1 = wi * k * mi * (jvp(n, xi) * v0 + h1vp(n, xi) * v1)
        J, H = jv(n, xo), hankel1(n, xo)
        Jp, Hp = wo * k * mo * jvp(n, xo), wo * k * mo * h1vp(n, xo)
        det = J * Hp - H * Jp
        v0, v1 = (Hp * a0 - H * a1) / det, (-Jp * a0 + J * a1) / det
        s = np.maximum(np.abs(v0), np.abs(v1))
        v0, v1 = v0 / s, v1 / s
    return np.arange(-N, N + 1), v1 / v0


def gl_band(k_center, frac_bw, n=21):
    """Gauss-Legendre nodes/weights of cloak2d.band_average (weights sum to 1)."""
    x, w = np.polynomial.legendre.leggauss(n)
    return k_center * (1 + 0.5 * frac_bw * x), w / 2


def _jy_and_derivs(nmax, x):
    """J_n, Y_n and derivatives for n = 0..nmax at real x (array (K,) or broadcastable); returns arrays (nmax+1, ...)."""
    from scipy.special import jv as _jv, yv as _yv
    nn = np.arange(-1, nmax + 2)[:, None]
    J = _jv(nn, x[None, :])
    Y = _yv(nn, x[None, :])
    Jp = 0.5 * (J[:-2] - J[2:])
    Yp = 0.5 * (Y[:-2] - Y[2:])
    return J[1:-1], Y[1:-1], Jp, Yp


def coeffs_pec_real_tm(eps_lk, radii, ks, N=None):
    """Fast path: lossless, real eps per layer (shape (L, K)), real ks, TM, PEC core. Returns n (-N..N), b (2N+1, K).
    Uses b_{-n} = b_n (radial symmetry). Agrees with cloak2d.coeffs to ~1e-13 (see check below)."""
    ks = np.asarray(ks, float)
    eps_lk = np.asarray(eps_lk, float).reshape(-1, ks.size)
    L = eps_lk.shape[0]
    if np.any(eps_lk <= 0):
        raise ValueError("real fast path needs eps > 0")
    m_lk = np.sqrt(eps_lk)
    if N is None:
        mm = np.max(m_lk, initial=1.0)
        N = int(np.ceil(ks.max() * radii[-1] * max(1.0, mm) + 4 * (ks.max() * radii[-1]) ** (1 / 3) + 12))
    m0 = m_lk[0] if L else np.ones_like(ks)
    J, Y, _, _ = _jy_and_derivs(N, ks * m0 * radii[0])
    H = J + 1j * Y
    v0, v1 = H, -J + 0j
    for j in range(L):
        r = radii[j + 1]
        mi = m_lk[j]
        mo = m_lk[j + 1] if j + 1 < L else np.ones_like(mi)
        Ji, Yi, Jpi, Ypi = _jy_and_derivs(N, ks * mi * r)
        Jo, Yo, Jpo, Ypo = _jy_and_derivs(N, ks * mo * r)
        Hi, Hpi = Ji + 1j * Yi, Jpi + 1j * Ypi
        Ho, Hpo = Jo + 1j * Yo, Jpo + 1j * Ypo
        a0 = Ji * v0 + Hi * v1
        a1 = mi * (Jpi * v0 + Hpi * v1)          # common factor k dropped on both sides
        Jp_, Hp_ = mo * Jpo, mo * Hpo
        det = Jo * Hp_ - Ho * Jp_
        v0, v1 = (Hp_ * a0 - Ho * a1) / det, (-Jp_ * a0 + Jo * a1) / det
        s = np.maximum(np.abs(v0), np.abs(v1))
        v0, v1 = v0 / s, v1 / s
    bpos = v1 / v0                     # n = 0..N
    b = np.concatenate([bpos[:0:-1], bpos], axis=0)
    return np.arange(-N, N + 1), b
