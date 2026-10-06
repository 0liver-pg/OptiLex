# Rotated complex-Poynting ellipsoid: ||P||^2/chi_max - k^2 <P,(H - t A)P> <= Re(e^{i th}<P,E_d>)/cos th, t = tan th >= 0
# Single-ellipsoid closed form, maximised over t. Objective sigma_ext linear in P (reciprocity). Valid for all designs with chi in the passive disk |chi - chi_max/2| <= chi_max/2.
import numpy as np, json
from scipy.special import jv, hankel1
from numpy.polynomial.legendre import leggauss
def pieces(k, b, mmax=25, nq=120):
    x, w = leggauss(nq); r = 1 + (b-1)*(x+1)/2; w = w*(b-1)/2; s = np.sqrt(2*np.pi*r*w); out = []
    for m in range(-mmax, mmax+1):
        am = abs(m); c = jv(am, k)/hankel1(am, k); psi = jv(am, k*r) - c*hankel1(am, k*r)
        R1, R2 = np.meshgrid(r, r, indexing='ij'); rl = np.minimum(R1, R2); rg = np.maximum(R1, R2)
        G = 0.25j*(jv(am, k*rl) - c*hankel1(am, k*rl))*hankel1(am, k*rg); K = k**2*s[:, None]*G*s[None, :]
        out.append(((K + K.conj().T)/2, (K - K.conj().T)/2j, (1j)**m*psi*s, (1j*k**2/4)*(1j)**(-m)*psi*s, -c))
    return out
def bound(k, b, em, ts):
    P = pieces(k, b); chi = em - 1; Tb = sum(p[4] for p in P); sb = -(4/k)*np.real(Tb); best = -np.inf; bt = None
    for t in ts:
        th = np.arctan(t); lin = 0; qg = 0; qe = 0; ok = True
        for H, A, e, g, _ in P:
            Q = np.eye(len(e))/chi - (H - t*A)
            if np.linalg.eigvalsh(Q).min() <= 0: ok = False; break
            et = e*np.exp(1j*th)/np.cos(th); Qi = np.linalg.inv(Q); gc = np.conj(g)
            x0 = Qi @ et/2; lin += np.real(g @ x0); qg += np.real(np.conj(gc) @ Qi @ gc); qe += np.real(np.conj(et) @ Qi @ et)
        if not ok: continue
        lb = -(4/k)*(np.real(Tb) + lin + np.sqrt(qg*qe)/2)
        if lb > best: best, bt = lb, t
    return sb, best, bt
ts = [0, 0.1, 0.25, 0.5, 1, 2, 4, 8, 16, 32]
res = {}
for k, b, em in [(np.pi/2, 1.5, 2), (np.pi/2, 1.5, 4), (np.pi/2, 1.5, 6), (np.pi/2, 2.0, 2), (np.pi/2, 2.0, 4), (np.pi/2, 2.0, 6), (np.pi/2, 3.0, 2), (np.pi/2, 3.0, 3),
                  (0.5, 3.0, 2), (0.5, 3.0, 4), (0.5, 3.0, 6), (0.5, 1.5, 6), (0.5, 1.5, 12), (0.5, 1.5, 20)]:
    sb, lb, t = bound(k, b, em, ts)
    print(f"ka={k:.3f} b/a={b} eps_max={em}: bare={sb:.4f} rotated-ellipsoid LB={lb:.4f} ratio={lb/sb:.4f} (tan th={t})", flush=True)
    res[f"{k:.4f}_{b}_{em}"] = dict(bare=sb, lb=lb, ratio=lb/sb, tan_theta=t)
json.dump(res, open('rotated.json', 'w'), indent=1)
