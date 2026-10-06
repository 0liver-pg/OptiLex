# Two-point FAH-line feasibility: can a monotone design angle hit the free targets (mod pi) at zeta=0 and zeta=1,
# inside the Sturm comparison windows [theta(eps=1), theta(eps=eps_max)]?  Returns the minimal pairwise residual
# sum_n g_n sin^2(delta) proxy: here simply the min over feasible (t0,t1) of sin^2(t0-T0)+sin^2(t1-T1) on a grid.
import json, numpy as np
from fah_lib import theta_shell, theta_free
res = {}
for k0 in (1.40, 1.45, 1.50):
    E0 = k0**2
    T0, T1 = theta_free(E0, 0.0), theta_free(E0+1, 1.0)
    for em in (1.5, 2.0, 3.0, 4.0, 6.0):
        w0 = (theta_shell(E0, 0.0, lambda r: 1.0), theta_shell(E0, 0.0, lambda r: em))
        w1 = (theta_shell(E0+1, 1.0, lambda r: 1.0), theta_shell(E0+1, 1.0, lambda r: em))
        t0 = np.linspace(*w0, 801); t1 = np.linspace(*w1, 801)
        A, Bm = np.meshgrid(t0, t1, indexing='ij')
        cost = np.sin(A-T0)**2 + np.sin(Bm-T1)**2
        cost[Bm < A] = np.inf
        res[f'{k0}_{em}'] = dict(T0=T0, T1=T1, w0=w0, w1=w1, min_pair_residual=float(cost.min()))
        print(f'k0={k0} eps_max={em}: windows {w0[0]:.2f}-{w0[1]:.2f}, {w1[0]:.2f}-{w1[1]:.2f}; targets {T0:.2f},{T1:.2f}; min residual {cost.min():.4f}')
json.dump(res, open('fah_windows.json', 'w'), indent=1)
