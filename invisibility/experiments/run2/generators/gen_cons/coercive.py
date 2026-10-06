# lambda_max of Hermitian part of k^2 G_obj (TM, PEC core radius a=1) on annulus [a,b], per angular channel m
import numpy as np
from scipy.special import jv, yv, hankel1
from numpy.polynomial.legendre import leggauss
def lam_max(k, b, mmax=30, nq=200):
    x, w = leggauss(nq); r = 1 + (b-1)*(x+1)/2; w = w*(b-1)/2
    out = []
    for m in range(0, mmax+1):
        R1, R2 = np.meshgrid(r, r, indexing='ij'); rl = np.minimum(R1, R2); rg = np.maximum(R1, R2)
        c = jv(m, k)/hankel1(m, k)
        G = 0.25j*(jv(m, k*rl) - c*hankel1(m, k*rl))*hankel1(m, k*rg)
        K = 2*np.pi*k**2*np.sqrt(r*w)[:, None]*G*np.sqrt(r*w)[None, :]
        H = (K + K.conj().T)/2; A = (K - K.conj().T)/2j
        out.append((m, np.linalg.eigvalsh(H).max(), np.linalg.eigvalsh(H).min(), np.linalg.eigvalsh(A).max()))
    return out
for k, b in [(np.pi/2, 3.0), (np.pi/2, 1.5), (np.pi/2, 2.0), (0.5, 3.0), (0.5, 1.5)]:
    o = lam_max(k, b)
    mu = max(t[1] for t in o); arg = max(o, key=lambda t: t[1])[0]
    print(f"k a={k:.3f} b/a={b}: mu*=max eig Herm(k^2 G)={mu:.4f} (channel m={arg}); chi_max allowed < {1/mu:.3f} (eps_max < {1+1/mu:.3f}); min eig {min(t[2] for t in o):.3f}")
