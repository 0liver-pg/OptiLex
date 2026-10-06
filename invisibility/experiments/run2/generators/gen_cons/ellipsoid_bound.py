# Global reactive-Poynting ellipsoid bound on single-frequency extinction (lossless, eps in [1,eps_max], free-form annulus, TM PEC core)
# Constraint (exact for every design, from Re of <P,(chi^-1 - k^2 G)P> = <P,E_d> and chi <= chi_max):
#   <P,(I/chi_max - Herm k^2G)P> <= Re<P,E_d>        (convex when I/chi_max - Herm k^2 G > 0)
# Objective: sigma_ext = -(4/k) Re T(0),  T(0) = T_bare(0) + (i k^2/4) sum_m i^{-m} 2pi int psi_m p_m r dr  (reciprocity)
import numpy as np, json, sys
from scipy.special import jv, hankel1
from numpy.polynomial.legendre import leggauss
def bound(k, b, eps_max, mmax=25, nq=120):
    chi = eps_max - 1
    x, w = leggauss(nq); r = 1 + (b-1)*(x+1)/2; w = w*(b-1)/2; s = np.sqrt(2*np.pi*r*w)
    lin0 = 0.0; quad = 0.0; Tbare = 0.0; ok = True
    for m in range(-mmax, mmax+1):
        am = abs(m); c = jv(am, k)/hankel1(am, k)
        psi = jv(am, k*r) - c*hankel1(am, k*r)            # core-regular radial function
        R1, R2 = np.meshgrid(r, r, indexing='ij'); rl = np.minimum(R1, R2); rg = np.maximum(R1, R2)
        G = 0.25j*(jv(am, k*rl) - c*hankel1(am, k*rl))*hankel1(am, k*rg)
        K = k**2*s[:, None]*G*s[None, :]                   # operator in orthonormalised coords y = s*p
        Q = np.eye(nq)/chi - (K + K.conj().T)/2
        if np.linalg.eigvalsh(Q).min() <= 0: ok = False; break
        e = (1j)**m*psi*s                                   # E_d channel m: i^m psi_m e^{im phi}; <P,E_d> = sum conj(y) e
        g = (1j*k**2/4)*(1j)**(-m)*psi*s                    # dT(0) = g^T y   (bilinear, not conj)
        # objective -(4/k) Re(T_bare + g^T y);  write Re(g^T y) = Re(conj(conj g)^H y)
        gc = np.conj(g)
        Qi = np.linalg.inv(Q)
        Tbare += -c                                         # b_m bare = -J_m/H_m
        lin0 += Qi @ e / 2                                   if False else 0
        # accumulate: x0 = Q^-1 e/2 ; Re(g^T x0) and quadratic terms
        x0 = Qi @ e/2
        lin0 = lin0 + np.real(g @ x0)
        quad += np.real(gc.conj() @ Qi @ gc) if False else np.real(np.conj(gc) @ (Qi @ gc))
        quad_e = np.real(np.conj(e) @ (Qi @ e))
        if m == -mmax: QE = 0.0
        QE += quad_e
    if not ok: return None
    sig_bare = -(4/k)*np.real(Tbare)
    # min over ellipsoid of -(4/k)[Re T_bare + Re g^T y]: maximise Re g^T y = lin0 + sqrt(quad)*sqrt(QE)/2
    maxdT = lin0 + np.sqrt(quad)*np.sqrt(QE)/2
    lb = -(4/k)*(np.real(Tbare) + maxdT)
    return sig_bare, lb
res = {}
for k, b, em in [(np.pi/2, 1.5, 2), (np.pi/2, 1.5, 4), (np.pi/2, 1.5, 6), (np.pi/2, 2.0, 2), (0.5, 3.0, 2), (0.5, 3.0, 4), (0.5, 1.5, 6), (0.5, 1.5, 20)]:
    out = bound(k, b, em)
    if out is None: print(k, b, em, 'not coercive'); continue
    sb, lb = out
    print(f"ka={k:.3f} b/a={b} eps_max={em}: bare sigma_ext={sb:.4f}, ellipsoid lower bound={lb:.4f}, ratio={lb/sb:.4f}")
    res[f"{k:.4f}_{b}_{em}"] = dict(sig_bare=sb, lb=lb, ratio=lb/sb)
json.dump(res, open(sys.argv[1], 'w'), indent=1)
