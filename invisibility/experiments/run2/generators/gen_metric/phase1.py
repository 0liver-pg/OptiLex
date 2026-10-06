"""Phase 1: is the lossless real-frequency Lagrange dual feasible at all?  max over (lam, mu>=0) of lambda_min(H_n) for each
harmonic n separately (ring- or node-local multipliers, angle-constant => decoupled per n).  Normalise mu so that sum W mu = 1.
Also reports eigenvalues of chi_max*Sym(G_n) (the obstruction: H contains D_mu - chi_max Sym(G^H D_mu)).
"""
import sys, json, numpy as np
from scipy.optimize import minimize
sys.path.insert(0, '.')
from vie import nodes, build

k, a, b = np.pi / 2, 1.0, 3.0
chimax = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
nsub = int(sys.argv[2]) if len(sys.argv) > 2 else 6
r, w = nodes(a, b, nsub, 4)
ns, ops = build(k, a, b, 6, r, w)
W = w * r
nr = len(r)
def sym(A): return 0.5 * (A + A.conj().T)
def asym(A): return (A - A.conj().T) / 2j

out = {}
for n in range(0, 7):
    G = ops[n]['G']
    # symmetrised in the W-weighted inner product: <x, G y>_W ; use M = W^{1/2} G W^{-1/2}
    Ws = np.sqrt(W)
    M = (Ws[:, None] * G) / Ws[None, :]
    ev = np.linalg.eigvalsh(sym(M))
    def lmin(theta):
        lam = theta[:nr]; mu = np.exp(theta[nr:]); mu = mu / np.sum(W * mu)
        Dl, Dm = np.diag(W * lam), np.diag(W * mu)
        H = -chimax * sym(G.conj().T @ Dm) - asym(G.conj().T @ Dl) + Dm
        # normalise by W to compare scales
        Hn = H / Ws[:, None] / Ws[None, :]
        return np.linalg.eigvalsh(Hn)[0]
    best = -np.inf
    rng = np.random.default_rng(1)
    for t in range(4):
        th0 = np.concatenate([rng.normal(0, 0.3, nr), rng.normal(0, 0.3, nr)])
        res = minimize(lambda t_: -lmin(t_), th0, method='L-BFGS-B', options=dict(maxiter=3000))
        best = max(best, -res.fun)
    out[n] = dict(chimax_symG_max=float(chimax * ev.max()), chimax_symG_min=float(chimax * ev.min()), best_lmin_nodelocal=float(best))
    print(n, out[n], flush=True)
json.dump(out, open(f'phase1_chi{chimax}.json', 'w'), indent=1)
