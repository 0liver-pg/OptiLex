import numpy as np, sys, json
from scipy.optimize import differential_evolution
from scipy.integrate import solve_ivp
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
import fastcyl
exec(open('perchan_floor.py').read().split('for ka in')[0])
def theta_ode(eps, n, k, a, b):
    f = lambda r, th: [np.cos(th[0])**2/r + (k**2*eps*r - n**2/r)*np.sin(th[0])**2]
    return solve_ivp(f, (a, b), [0.0], rtol=1e-11, atol=1e-12, max_step=0.005).y[0, -1]
res = {}
for (k, ba, emax) in [(np.pi/2, 3.0, 2.0), (np.pi/2, 1.5, 6.0), (np.pi/2, 2.0, 4.0), (3.0, 1.25, 6.0)]:
    a, b = 1.0, ba
    print(f"k={k:.3f} b/a={ba} emax={emax}: theta const vs ode:",
          [(round(theta_const(e, n, k, a, b), 5), round(theta_ode(e, n, k, a, b), 5)) for n in (0, 1, 2) for e in (1.0, emax)])
    bare = fastcyl.widths_pec([], [1.0], k)[1]
    L = 8; radii = list(np.linspace(a, b, L + 1))
    f = lambda e: fastcyl.coeffs_pec_real_tm(np.asarray(e)[:, None], radii, np.array([k])) and \
        (lambda nb: (4/k)*np.sum(np.abs(nb[1][:, 0])**2))(fastcyl.coeffs_pec_real_tm(np.asarray(e)[:, None], radii, np.array([k])))
    r = differential_evolution(f, [(1, emax)]*L, seed=0, maxiter=150, popsize=15, tol=1e-9)
    N = int(k*b*np.sqrt(emax)) + 6
    floor = sum(sig(np.linspace(theta_const(1.0, n, k, a, b), theta_const(emax, n, k, a, b), 4001), n, k, b).min() for n in range(N + 1))
    print(f"   per-channel floor R >= {floor/bare:.4f};  DE (L=8) best R = {r.fun/bare:.4f}  eps={np.round(r.x,2).tolist()}  gap={r.fun/floor:.3f}", flush=True)
    res[f"k{k:.3f}_ba{ba}_e{emax}"] = dict(floor_R=floor/bare, de_R=r.fun/bare, eps=r.x.tolist())
json.dump(res, open('perchan_verify.json', 'w'), indent=1)
