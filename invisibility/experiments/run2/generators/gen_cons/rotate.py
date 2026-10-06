import numpy as np
from scipy.special import jv, hankel1
from numpy.polynomial.legendre import leggauss
def mats(k, b, m, nq=120):
    x, w = leggauss(nq); r = 1 + (b-1)*(x+1)/2; w = w*(b-1)/2; s = np.sqrt(2*np.pi*r*w)
    c = jv(m, k)/hankel1(m, k); R1, R2 = np.meshgrid(r, r, indexing='ij'); rl = np.minimum(R1, R2); rg = np.maximum(R1, R2)
    G = 0.25j*(jv(m, k*rl) - c*hankel1(m, k*rl))*hankel1(m, k*rg); K = k**2*s[:, None]*G*s[None, :]
    return (K + K.conj().T)/2, (K - K.conj().T)/2j
for k, b in [(np.pi/2, 3.0), (np.pi/2, 2.0), (np.pi/2, 1.5), (0.5, 3.0)]:
    MS = [mats(k, b, m) for m in range(0, 26)]
    best = None
    for t in [0, 0.25, 0.5, 1, 2, 4, 8, 16]:
        lam = max(np.linalg.eigvalsh(H - t*A).max() for H, A in MS)
        print(f"  ka={k:.3f} b/a={b} tan(theta)={t}: lambda_max={lam:.4f} -> eps_max up to {1+1/lam:.3f}")
