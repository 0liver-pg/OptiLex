"""Supergradient (Danskin) ascent on the concave Lagrange dual g(lam, mu), mu >= 0, lossless chi in [0, chi_max],
single frequency, node-local angle-constant multipliers (valid for free-form designs; |n|<=N Nystrom discretisation).
g = sum_n [c_n - h_n^H H_n^{-1} h_n] when all H_n > 0;  dg/dlam_i = -W_i sum_n Im(conj(E_n,i) p_n,i),
dg/dmu_i = -W_i sum_n [chi_max Re(conj(E)p) - |p|^2]_i at the Lagrangian minimiser p* = -H^{-1} h.
Starts from the max-margin feasible point (joint_dual stage 1). Any iterate with H > 0 is a certified (discretised) bound.
metric: 'ext' (total, lossless) or 'sector' (backward half-plane).
"""
import sys, json, numpy as np
from scipy.optimize import minimize
sys.path.insert(0, '.')
from vie import nodes, build

k, a, b = np.pi / 2, 1.0, 3.0
chimax = float(sys.argv[1]); N = int(sys.argv[2]); nsub = int(sys.argv[3]); metric = sys.argv[4] if len(sys.argv) > 4 else 'ext'
iters = int(sys.argv[5]) if len(sys.argv) > 5 else 400
r, w = nodes(a, b, nsub, 4)
ns, ops = build(k, a, b, N, r, w)
W = w * r; Ws = np.sqrt(W); nr = len(r); nb = len(ns)
def sym(A): return 0.5 * (A + A.conj().T)
def asym(A): return (A - A.conj().T) / 2j

bare = np.array([ops[n]['bare'] for n in ns])
if metric == 'ext':
    Kmat = np.eye(nb) * (4 / k)
else:
    d = ns[None, :] - ns[:, None]
    with np.errstate(invalid='ignore', divide='ignore'):
        Kk = np.where(d == 0, np.pi, 2 * np.exp(1j * d * np.pi) * np.sin(d * np.pi / 2) / np.where(d == 0, 1, d))
    Kmat = 2 / (np.pi * k) * Kk
bare_val = float(np.real(bare.conj() @ Kmat @ bare))
F = np.zeros((nb, nb * nr), complex)
for j, n in enumerate(ns):
    F[j, j * nr:(j + 1) * nr] = ops[n]['F']
Hc = F.conj().T @ Kmat @ F; hc = F.conj().T @ Kmat @ bare
Gs = [ops[n]['G'] for n in ns]; Eds = [ops[n]['Ed'] for n in ns]


def assemble(lam, mu):
    Dl, Dm = np.diag(W * lam), np.diag(W * mu)
    H = Hc.copy(); h = hc.copy()
    for j in range(nb):
        sl = slice(j * nr, (j + 1) * nr); G, Ed = Gs[j], Eds[j]
        H[sl, sl] += -chimax * sym(G.conj().T @ Dm) - asym(G.conj().T @ Dl) + Dm
        h[sl] += -(chimax / 2) * Dm @ Ed - 0.5j * Dl @ Ed
    return H, h


def evaluate(lam, mu):
    H, h = assemble(lam, mu)
    try:
        L = np.linalg.cholesky(H)
    except np.linalg.LinAlgError:
        return None
    x = -np.linalg.solve(L.conj().T, np.linalg.solve(L, h))
    g = bare_val + np.real(h.conj() @ x)       # c - h^H H^-1 h
    gl = np.zeros(nr); gm = np.zeros(nr)
    for j in range(nb):
        p = x[j * nr:(j + 1) * nr]; E = Eds[j] + Gs[j] @ p
        f = np.conj(E) * p
        gl += -W * f.imag
        gm += -W * (chimax * f.real - np.abs(p) ** 2)
    return g, gl, gm


# stage 1: feasible start = maximise min eigenvalue (normalised)
def margin(th):
    th = np.clip(th, -12, 12)
    H, _ = assemble(th[:nr], np.exp(th[nr:]))
    try:
        return np.linalg.eigvalsh(H / np.repeat(Ws, nb)[:, None] / np.repeat(Ws, nb)[None, :])[0]
    except np.linalg.LinAlgError:
        return -1e3
rng = np.random.default_rng(3)
res = minimize(lambda t: -margin(t), np.concatenate([rng.normal(0, .3, nr), rng.normal(0, .3, nr)]), method='L-BFGS-B', options=dict(maxiter=800))
th = np.clip(res.x, -12, 12); lam, mu = th[:nr].copy(), np.exp(th[nr:])
print('margin', -res.fun, flush=True)
def negg(t):
    t = np.clip(t, -14, 14)
    l, m = t[:nr], np.exp(t[nr:])
    ev = evaluate(l, m)
    if ev is None:
        return 1e8, np.zeros_like(t)
    g, gl, gm = ev
    return -g, -np.concatenate([gl, gm * m])
best = -np.inf; bt = th
starts = [th] + [np.concatenate([rng.normal(0, .3, nr), np.log(np.exp(th[nr:]) * s_)]) for s_ in (1e-2, 1e-1, 1.0)]
for t0 in starts:
    if evaluate(np.clip(t0,-14,14)[:nr], np.exp(np.clip(t0,-14,14)[nr:])) is None:
        print('start infeasible'); continue
    r_ = minimize(negg, t0, jac=True, method='L-BFGS-B', options=dict(maxiter=iters, maxfun=4*iters))
    print('start done g', -r_.fun, 'ratio', -r_.fun / bare_val, flush=True)
    if -r_.fun > best: best, bt = -r_.fun, r_.x
out = dict(chimax=chimax, N=N, nsub=nsub, metric=metric, bare=bare_val, bound=float(best), ratio=float(best / bare_val), iters=iters)
print(json.dumps(out))
json.dump(out, open(f'ascent_{metric}_{chimax}_{N}_{nsub}.json', 'w'), indent=1)
