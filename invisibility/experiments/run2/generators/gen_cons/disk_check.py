# Lorentz class at complex frequency z: chi(z) = sum_j t_j/(w0j^2 - z^2 - i g_j z), g_j >= gmin, t = sum t_j.
# Claim: Im chi >= c |chi|^2 / t with c = Re z (2 Im z + gmin)  (disk of diameter t/c tangent to real axis at 0).
import numpy as np
rng = np.random.default_rng(0)
wc = np.pi/2
for B, gmin in [(0.1, 0.01), (0.03, 0.001), (0.3, 0.1), (0.1, 0.0)]:
    z = wc*(1 + 0.5j*B); g0 = gmin*wc
    c = z.real*(2*z.imag + g0)
    worst = np.inf
    for trial in range(20000):
        J = rng.integers(1, 6)
        t = rng.exponential(1.0, J)*wc**2
        w0 = wc*np.exp(rng.uniform(np.log(0.01), np.log(30), J))
        g = g0 + wc*rng.exponential(0.05, J)*(rng.random(J) < 0.5)
        chi = np.sum(t/(w0**2 - z**2 - 1j*g*z))
        worst = min(worst, chi.imag/(c*abs(chi)**2/t.sum()))
    # tightness: single oscillator with g = gmin lies on the circle
    chi1 = wc**2/((1.3*wc)**2 - z**2 - 1j*g0*z)
    print(f"B={B} gmin={gmin}: c/wc^2={c/wc**2:.4f}  disk diameter per unit t (in wc^2 units)={wc**2/c:.2f}  "
          f"min ratio over random media={worst:.6f} (>=1 required)  single-osc on circle: {chi1.imag/(c*abs(chi1)**2/wc**2):.12f}")
    # what a chi(z) ~ 5 (eps 6) costs in t at this z: need Im chi >= 25 c/t ; with w0 far above band, Im chi small
    for w0r in [2.0, 3.7, 10.0]:
        tt = 5*((w0r*wc)**2 - (z**2).real)  # choose t so Re chi ~ 5
        chi = tt/((w0r*wc)**2 - z**2 - 1j*g0*z)
        print(f"     eps~6 coating with w0={w0r} wc: t/wc^2={tt/wc**2:.1f} chi(z)={chi:.3f}")
