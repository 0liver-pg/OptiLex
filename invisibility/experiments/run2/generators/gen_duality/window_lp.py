"""Window-minorant LP (strategy S1 scoping). Find W(t) = sum_j w_j P_{z_j}(t) - sum_l v_l P_{zeta_l}(t) (mirror-symmetrised)
with W(t) <= 1_I(t) for t >= 0, maximising sum_j w_j LB_j - sum_l v_l UB_l.  Then <sigma>_U >= value / |I|.
Here LB_j, UB_l are stand-ins: LB = bare Im F (exact identity) and UB = mult x bare Im F, to measure pure window loss."""
import sys, numpy as np
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d
from scipy.optimize import linprog
from scipy.integrate import quad
kc, B = np.pi / 2, 0.1
k1, k2 = kc * (1 - B / 2), kc * (1 + B / 2); L = k2 - k1
def ImF(z):
    n, b = cloak2d.coeffs([], [1.0], z, core='pec', nmax=int(abs(z) + 30))
    return (-(4j / z) * b.sum()).imag
true = quad(lambda t: ImF(complex(t, 0)), k1, k2)[0] / L
print('bare <sigma_ext>_U = %.4f' % true)
def P(z, t):
    return (z.imag / np.pi) / ((t - z.real) ** 2 + z.imag ** 2)
tg = np.concatenate([np.linspace(0, k1, 400, endpoint=False), np.linspace(k1, k2, 400), np.linspace(k2, 6, 600)[1:], np.geomspace(6, 400, 200)[1:]])
inb = (tg >= k1) & (tg <= k2)
# in-band poles: centres across the band, several heights; out-of-band poles: centres outside, larger heights
zin = [complex(s, h) for s in np.linspace(k1, k2, 9) for h in L * np.array([0.03, 0.06, 0.12, 0.25])]
zout = [complex(s, h) for s in np.concatenate([np.linspace(k1 - 3 * L, k1, 6), np.linspace(k2, k2 + 3 * L, 6)]) for h in L * np.array([0.1, 0.3, 1.0, 3.0])]
LBv = np.array([ImF(z) for z in zin]); UB0 = np.array([ImF(z) for z in zout])
A_in = np.array([P(z, tg) + P(z, -tg) for z in zin]).T
A_out = np.array([P(z, tg) + P(z, -tg) for z in zout]).T
for mult in [1, 3, 10]:
    UBv = mult * UB0
    c = np.concatenate([-LBv, UBv])
    A = np.hstack([A_in, -A_out]); bvec = np.where(inb, 1.0, 0.0)
    r = linprog(c, A_ub=A, b_ub=bvec, bounds=[(0, None)] * len(c), method='highs')
    print('UB = %2dx bare: window-LP floor on <sigma_ext>_U = %.4f  (ratio to true %.3f)' % (mult, -r.fun / L, -r.fun / L / true))
