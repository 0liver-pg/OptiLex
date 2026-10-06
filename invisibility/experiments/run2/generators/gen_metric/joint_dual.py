"""Joint dual (angle-constant, node-local multipliers shared by all harmonics), lossless chi in [0,chi_max], single frequency,
objective = total sigma (ext=sca) restricted to |n|<=N (all channels' |b_n|^2 counted).  Two stages:
 (1) maximise min_n lambda_min(H_n) (feasibility margin); (2) from the best feasible point, maximise the dual value g.
Writes joint_dual_<chi>_<N>.json.
"""
import sys, json, numpy as np
from scipy.optimize import minimize
sys.path.insert(0, '.')
from vie import nodes, build

k, a, b = np.pi / 2, 1.0, 3.0
chimax = float(sys.argv[1]); N = int(sys.argv[2]); nsub = int(sys.argv[3]) if len(sys.argv) > 3 else 6
r, w = nodes(a, b, nsub, 4)
ns, ops = build(k, a, b, N, r, w)
W = w * r; Ws = np.sqrt(W); nr = len(r)
def sym(A): return 0.5 * (A + A.conj().T)
def asym(A): return (A - A.conj().T) / 2j
bare_val = float(4 / k * sum(abs(ops[n]['bare']) ** 2 for n in ns))


def parts(theta):
    theta = np.clip(theta, -12, 12); lam = theta[:nr]; mu = np.exp(theta[nr:])
    Dl, Dm = np.diag(W * lam), np.diag(W * mu)
    res = []
    for n in ns:
        o = ops[n]; G, Ed, F, bb = o['G'], o['Ed'], o['F'], o['bare']
        H = (4 / k) * np.outer(F.conj(), F) - chimax * sym(G.conj().T @ Dm) - asym(G.conj().T @ Dl) + Dm
        h = (4 / k) * F.conj() * bb - (chimax / 2) * Dm @ Ed - 0.5j * Dl @ Ed
        c = (4 / k) * abs(bb) ** 2
        res.append((H, h, c))
    return res


def margin(theta):
    try:
        return min(np.linalg.eigvalsh(H / Ws[:, None] / Ws[None, :])[0] for H, _, _ in parts(theta))
    except np.linalg.LinAlgError:
        return -1e3


def gval(theta):
    tot = 0.0
    for H, h, c in parts(theta):
        try:
            L = np.linalg.cholesky(H)
        except np.linalg.LinAlgError:
            return -1e6
        y = np.linalg.solve(L, h); tot += c - np.real(y.conj() @ y)
    return tot


rng = np.random.default_rng(2)
best_m, best_t = -np.inf, None
for t in range(2):
    th0 = np.concatenate([rng.normal(0, 0.3, nr), rng.normal(0, 0.3, nr)])
    res = minimize(lambda x: -margin(x), th0, method='L-BFGS-B', options=dict(maxiter=1500))
    if -res.fun > best_m: best_m, best_t = -res.fun, res.x
print('feasibility margin', best_m, flush=True)
out = dict(chimax=chimax, N=N, nsub=nsub, bare=bare_val, margin=float(best_m))
if best_m > 0:
    # scale-up search for the dual value
    res = minimize(lambda x: -gval(x), best_t, method='Powell', options=dict(maxiter=6000, xtol=1e-4, ftol=1e-9))
    out.update(bound=float(-res.fun), ratio=float(-res.fun / bare_val))
print(json.dumps(out))
json.dump(out, open(f'joint_dual_{chimax}_{N}.json', 'w'), indent=1)
