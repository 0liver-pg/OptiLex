"""Intrinsic tightness of the log-subharmonic (Jensen) transfer for the angle-limited metric (card P2), bare PEC.
Chain: (1/J) sum_j log V(z_j) <= int K log V  (K = mixture of Poisson kernels at z_j = s_j + i eta),
then Jensen on the band and on the out-of-band part, giving a floor on <sigma_Theta>_U from complex-frequency values.
V(z) = |q(z)|^2 int_Theta e^{-2 c_phi Im z} |T(phi,z)|^2 dphi, q = sqrt(2 kap)/(z + i kap), c_phi = 2 b |sin(phi/2)| with b = 3 (class radius)."""
import sys, numpy as np
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d
from scipy.integrate import quad
kc, B, b = np.pi / 2, 0.1, 3.0
k1, k2 = kc * (1 - B / 2), kc * (1 + B / 2)
kap = kc
xg, wg = np.polynomial.legendre.leggauss(200)
phis = np.pi / 2 + (xg + 1) * np.pi / 2          # phi in [pi/2, 3pi/2] = backward half-plane
wph = wg * np.pi / 2
cphi = 2 * b * np.abs(np.sin(phis / 2))
m, radii = [], [1.0]
def Vfun(z):
    nm = int(abs(z) * 1.0 + 25)
    n, bb = cloak2d.coeffs(m, radii, z, core='pec', nmax=nm)
    T = (bb[None, :] * np.exp(1j * np.outer(phis, n))).sum(1)
    q2 = abs(np.sqrt(2 * kap) / (z + 1j * kap)) ** 2
    return q2 * np.sum(wph * np.exp(-2 * cphi * z.imag) * np.abs(T) ** 2)
def sigTheta(t):
    return Vfun(complex(t, 0)) / (abs(np.sqrt(2 * kap) / (t + 1j * kap)) ** 2 * np.pi * t / 2)
true_avg = quad(sigTheta, k1, k2, epsrel=1e-9)[0] / (k2 - k1)
print('bare <sigma_Theta>_U = %.5f (card: 1.714)' % true_avg)
# real-axis V on a grid for out-of-band integrals
tt = np.concatenate([np.linspace(1e-3, 1.4, 300), np.linspace(1.4, 1.75, 300)[1:], np.linspace(1.75, 8, 400)[1:], np.geomspace(8, 60, 200)[1:]])
VV = np.array([Vfun(complex(t, 0)) for t in tt])
for J, alpha in [(1, 0.5), (4, 1.0), (8, 1.0), (8, 0.6), (16, 1.0)]:
    L = k2 - k1
    s = k1 + (np.arange(J) + 0.5) * L / J
    eta = alpha * L / J
    zs = s + 1j * eta
    def K(t):
        t = np.asarray(t, float)
        return np.mean([(eta / np.pi) / ((t - sj) ** 2 + eta ** 2) for sj in s], axis=0)
    # mirror: V even, so int_R K V = int_0^inf (K(t)+K(-t)) V(t) dt
    Kt = K(tt) + K(-tt)
    inb = (tt >= k1) & (tt <= k2)
    omega_I = quad(lambda t: K(t), k1, k2, limit=200)[0]
    supK = max(K(np.linspace(k1, k2, 2001)))
    omega_out = 1 - omega_I
    out_KV = np.trapezoid(np.where(inb, 0, Kt * VV), tt) + 1e-12
    mean_logVz = np.mean([np.log(Vfun(z)) for z in zs])
    qmax = max(abs(np.sqrt(2 * kap) / (t + 1j * kap)) ** 2 * np.pi * t / 2 for t in np.linspace(k1, k2, 201))
    res = []
    for mult in [1, 10, 100]:
        U = mult * out_KV
        lnI = (mean_logVz - omega_out * np.log(U / omega_out)) / omega_I
        intV = omega_I / supK * np.exp(lnI)
        res.append(intV / (L * qmax))
    lin = (np.mean([Vfun(z) for z in zs]) - out_KV) / supK / (L * qmax)
    print('J=%2d eta/|I|=%.3f omega_I=%.3f  log-route floor (U=1x,10x,100x true out-of-band) = %s  ratio_to_true(1x)=%.3f | linear-route floor (true U) = %.4f' % (
        J, eta / L, omega_I, ' '.join('%.4f' % r for r in res), res[0] / true_avg, lin))
