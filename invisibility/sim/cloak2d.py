"""Shared, code-owned benchmark for 2D cloaking bounds: exact scattering by radially layered cylinders.

Use it to falsify proposed bounds: any passive design found here whose band-averaged metric falls BELOW a
claimed lower bound refutes that bound (for the same object, design region, materials and band).

Geometry: a core (PEC, or a dielectric of index m_core) of radius radii[0], wrapped by layers with complex
indices m[j] out to radii[j+1]; vacuum outside. Time dependence exp(-i w t); passive means Im(m^2) >= 0.
Units: lengths in units of the free-space wavelength scale you choose; k0 = 2*pi/wavelength.
"""
import numpy as np
from scipy.special import jv, jvp, hankel1, h1vp
from scipy.optimize import minimize


def _M(n, k, r, w):
    """Field-matching matrix at radius r for order n: rows (field, weighted radial derivative)."""
    x = k * r
    return np.array([[jv(n, x), hankel1(n, x)], [w * k * jvp(n, x), w * k * h1vp(n, x)]])


def coeffs(m_layers, radii, k0, pol="TM", core="pec", m_core=None, nmax=None):
    """Scattering coefficients b_n, n = -N..N, for plane-wave incidence (scattered E_z or H_z = sum i^n b_n H_n e^{in phi}).

    m_layers: indices of the shells (inner to outer); radii: [r_core, r_1, ..., r_L] (len = len(m_layers) + 1).
    pol: 'TM' (E along axis; match E_z and dE_z/dr) or 'TE' (H along axis; match H_z and (1/eps) dH_z/dr).
    core: 'pec' or 'dielectric' (then m_core is required). With no shells, pass m_layers=[] and radii=[a].
    """
    m_layers = np.asarray(m_layers, complex)
    R = radii[-1]
    N = nmax or int(np.ceil(k0 * R * max(1.0, np.max(np.abs(m_layers), initial=1.0)) + 4 * (k0 * R) ** (1 / 3) + 12))
    weight = (lambda m: 1.0) if pol == "TM" else (lambda m: 1.0 / m ** 2)
    out = np.empty(2 * N + 1, complex)
    for i, n in enumerate(range(-N, N + 1)):
        if core == "pec":
            if len(m_layers) == 0:
                k, r0, m = k0, radii[0], 1.0
            else:
                k, r0, m = k0 * m_layers[0], radii[0], m_layers[0]
            if pol == "TM":   # E_z = 0 on the conductor
                v = np.array([hankel1(n, k * r0), -jv(n, k * r0)])
            else:             # dH_z/dr = 0 on the conductor
                v = np.array([h1vp(n, k * r0), -jvp(n, k * r0)])
            layers = list(m_layers)
            start = 0
        else:
            mc = complex(m_core)
            v = np.array([1.0, 0.0], complex)
            layers = [mc] + list(m_layers)
            start = 0
        # propagate outward through each interface
        mats = layers + [1.0]
        rs = radii if core == "pec" else radii
        if core == "pec":
            for j in range(len(layers)):
                r = rs[j + 1]
                mi, mo = mats[j], mats[j + 1]
                v = np.linalg.solve(_M(n, k0 * mo, r, weight(mo)), _M(n, k0 * mi, r, weight(mi)) @ v)
        else:
            for j in range(len(layers)):
                r = rs[j]
                mi, mo = mats[j], mats[j + 1]
                v = np.linalg.solve(_M(n, k0 * mo, r, weight(mo)), _M(n, k0 * mi, r, weight(mi)) @ v)
        out[i] = v[1] / v[0]
    return np.arange(-N, N + 1), out


def widths(m_layers, radii, k0, **kw):
    """(scattering width, extinction width, absorption width), same length unit as radii."""
    _, b = coeffs(m_layers, radii, k0, **kw)
    s = 4 / k0 * np.sum(np.abs(b) ** 2)
    e = -4 / k0 * np.sum(b.real)
    return s, e, e - s


def band_average(metric_fn, k_center, frac_bw, n=41):
    """Uniform average of metric_fn(k) over [k_c(1 - B/2), k_c(1 + B/2)] (Gauss-Legendre)."""
    x, w = np.polynomial.legendre.leggauss(n)
    ks = k_center * (1 + 0.5 * frac_bw * x)
    return float(np.sum(w * np.array([metric_fn(k) for k in ks])) / 2)


def optimize_layers(n_layers, radii, k_center, frac_bw, pol="TM", core="pec", m_core=None,
                    eps_bounds=(-10.0, 10.0), loss_max=0.0, metric="ext", seeds=8, rng=0, dispersion=None):
    """Baseline adversary: search layer permittivities to minimise the band-averaged metric.

    By default each layer's permittivity is frequency-INDEPENDENT, which is unphysical over a band when Re eps < 1
    (Kramers-Kronig). Pass dispersion=callable(eps_params, k) -> eps(k) to enforce a causal model (e.g. Drude/Lorentz);
    any claimed bound must state which material class it covers, and falsification must use the same class.
    Returns (best_value, best_params).
    """
    gen = np.random.default_rng(rng)
    lo, hi = eps_bounds

    def eps_of(p, k):
        if dispersion is not None:
            return dispersion(p, k)
        re = p[:n_layers]
        im = p[n_layers:] if loss_max > 0 else np.zeros(n_layers)
        return re + 1j * im

    def f(p):
        def at(k):
            m = np.sqrt(eps_of(p, k).astype(complex))
            s, e, a = widths(m, radii, k, pol=pol, core=core, m_core=m_core)
            return {"ext": e, "sca": s}[metric]
        return band_average(at, k_center, frac_bw, n=21)

    dim = n_layers * (2 if (loss_max > 0 and dispersion is None) else 1)
    bounds = [(lo, hi)] * n_layers + ([(0, loss_max)] * n_layers if (loss_max > 0 and dispersion is None) else [])
    best = (np.inf, None)
    for _ in range(seeds):
        p0 = np.array([gen.uniform(a, b) for a, b in bounds]) if dispersion is None else gen.normal(size=dim)
        r = minimize(f, p0, method="L-BFGS-B", bounds=bounds if dispersion is None else None)
        if r.fun < best[0]:
            best = (float(r.fun), r.x)
    return best


if __name__ == "__main__":
    # Self-checks against independent exact formulas.
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from analytic import cylinder_tm_coeffs
    k0, a = 2 * np.pi, 0.5
    _, b = coeffs([], [a], k0, core="dielectric", m_core=2.0)
    _, ref = cylinder_tm_coeffs(2.0, k0 * a, nmax=(len(b) - 1) // 2)
    print("dielectric rod vs analytic, max |db|:", np.max(np.abs(b - ref)))
    _, b = coeffs([], [a], k0, core="pec")
    n = np.arange(-(len(b) - 1) // 2, (len(b) - 1) // 2 + 1)
    print("PEC rod TM vs -J/H, max |db|:", np.max(np.abs(b + jv(n, k0 * a) / hankel1(n, k0 * a))))
    s, e, ab = widths([1.3, 1.7], [0.3, 0.4, 0.5], k0, core="pec")
    print("lossless layered PEC rod: sigma_sca - sigma_ext =", s - e)
    s, e, ab = widths([1.3 + 0.1j], [0.3, 0.5], k0, core="pec")
    print("lossy shell: absorption width (must be > 0) =", ab)
