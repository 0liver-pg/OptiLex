"""Lagrange dual, lossless class chi in [0, chi_max], single frequency, ring-constant multipliers (valid for FREE-FORM designs).
Constraints per ring i (integrated over phi): Im<E,p>_i = 0 ; chi_max Re<E,p>_i - |p|^2_i >= 0.
Objective: total sigma_sca (=sigma_ext, lossless) or sector width. Decouples per harmonic n for ring-constant multipliers.
Any (lam, mu>=0) with all H_n > 0 gives a valid lower bound (for the Nystrom-discretised, |n|<=N problem).
"""
import sys, json, numpy as np
from scipy.optimize import minimize
sys.path.insert(0, '.')
from vie import nodes, build

k, a, b, chimax = np.pi / 2, 1.0, 3.0, 5.0
N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
nsub = int(sys.argv[2]) if len(sys.argv) > 2 else 8
metric = sys.argv[3] if len(sys.argv) > 3 else 'ext'
grouping = sys.argv[4] if len(sys.argv) > 4 else 'rings'
r, w = nodes(a, b, nsub, 4)
ns, ops = build(k, a, b, N, r, w)
W = w * r
nr = len(r)
# group nodes into constraint regions
if grouping == 'global':
    groups = [np.arange(nr)]
else:
    groups = [np.arange(i * 4, (i + 1) * 4) for i in range(nsub)]
ng = len(groups)
P = np.zeros((ng, nr))
for j, gidx in enumerate(groups):
    P[j, gidx] = 1


def sym(A): return 0.5 * (A + A.conj().T)
def asym(A): return (A - A.conj().T) / 2j


bare = np.array([ops[n]['bare'] for n in ns])
if metric == 'ext':
    Kmat = np.eye(len(ns)) * (4 / k)          # sigma = (4/k) sum |b_n|^2 (lossless => = ext)
else:  # backward half-plane sector width: (2/(pi k)) b^H K b
    d = ns[None, :] - ns[:, None]
    hw, c0 = np.pi / 2, np.pi
    with np.errstate(invalid='ignore', divide='ignore'):
        Kk = np.where(d == 0, 2 * hw, 2 * np.exp(1j * d * c0) * np.sin(d * hw) / np.where(d == 0, 1, d))
    Kmat = 2 / (np.pi * k) * Kk
bare_val = float(np.real(bare.conj() @ Kmat @ bare))


def g(theta, ret=False):
    lam = P.T @ theta[:ng]
    mu = P.T @ np.exp(theta[ng:])           # mu > 0
    Dl, Dm = np.diag(W * lam), np.diag(W * mu)
    # sector objective couples harmonics: assemble block matrices
    blocks_H, blocks_h = [], []
    nb = len(ns)
    F = np.zeros((nb, nb * nr), complex)
    for j, n in enumerate(ns):
        F[j, j * nr:(j + 1) * nr] = ops[n]['F']
    Hc = F.conj().T @ Kmat @ F
    hc = F.conj().T @ Kmat @ bare
    H = Hc.copy(); h = hc.copy()
    for j, n in enumerate(ns):
        G, Ed = ops[n]['G'], ops[n]['Ed']
        sl = slice(j * nr, (j + 1) * nr)
        H[sl, sl] += -chimax * sym(G.conj().T @ Dm) - asym(G.conj().T @ Dl) + Dm
        h[sl] += -(chimax / 2) * Dm @ Ed - 0.5j * Dl @ Ed
    try:
        L = np.linalg.cholesky(H)
    except np.linalg.LinAlgError:
        return -1e3
    y = np.linalg.solve(L, h)
    val = bare_val - np.real(y.conj() @ y)
    return val


best = None
rng = np.random.default_rng(0)
for trial in range(6):
    th0 = np.concatenate([rng.normal(0, 1, ng), np.log(rng.uniform(0.5, 50, ng))])
    res = minimize(lambda t: -g(t), th0, method='Nelder-Mead' if ng < 3 else 'Powell', options=dict(maxiter=40000, xtol=1e-6, ftol=1e-10))
    v = -res.fun
    if best is None or v > best[0]:
        best = (v, res.x)
    print('trial', trial, 'bound', v, 'ratio', v / bare_val, flush=True)
print(json.dumps(dict(N=N, nsub=nsub, metric=metric, grouping=grouping, bare=bare_val, bound=best[0], ratio=best[0] / bare_val)))
