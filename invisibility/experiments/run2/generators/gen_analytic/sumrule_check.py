# Check: (A) 2D free-space f-sum rule  (2/pi) int_0^inf sigma_ext dk = int omega_p^2 dA   (c = 1)
#        (B) PEC-difference sum rule   (2/pi) int_0^inf (sigma_d - sigma_bare) dk = int g(x) omega_p^2 dA ,
#            conjectured g = unshadowed fraction 1 - (2/pi) arcsin(a/r) for a ring at radius r.
import sys, json, numpy as np
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d as C
from scipy.integrate import quad

def eps_lor(k, wp2, w0, g):
    return 1 + wp2 / (w0**2 - k**2 - 1j*g*k)

def sig_ext(mlayers, radii, k, core='pec', m_core=None):
    N = int(np.ceil(k*radii[-1]*2 + 4*(k*radii[-1])**(1/3) + 12))
    _, b = C.coeffs(mlayers, radii, k, pol='TM', core=core, m_core=m_core, nmax=N)
    return -4/k*np.sum(b.real)

def integ(f, K, pts):
    tot = 0; edges = np.concatenate([[1e-6], pts, [K]])
    for lo, hi in zip(edges[:-1], edges[1:]):
        v, e = quad(f, lo, hi, limit=400, epsrel=1e-9, epsabs=1e-10)
        tot += v
    return tot

out = {}
# (A) free-space Lorentz cylinder radius R
R, wp2, w0, gam = 1.0, 1.0, 1.0, 0.2
f = lambda k: sig_ext([], [R], k, core='dielectric', m_core=np.sqrt(eps_lor(k, wp2, w0, gam)))
for K in (20, 40, 80):
    I = integ(f, K, [0.5, 0.9, 1.1, 2, 5, 10, 20, 40][:])
    out[f'A_K{K}'] = (2/np.pi)*I
print('A predicted', wp2*np.pi*R**2, out)

# (B) PEC core a=1, Lorentz shell 1..b
a = 1.0
for (b, wp2, w0, gam) in [(1.5, 1.0, 1.0, 0.2), (2.0, 0.5, 2.0, 0.3), (3.0, 0.3, 0.5, 0.1)]:
    fd = lambda k: sig_ext([np.sqrt(eps_lor(k, wp2, w0, gam))], [a, b], k) - sig_ext([], [a], k)
    res = {}
    for K in (20, 40, 80):
        I = integ(fd, K, [0.3, 0.5*w0, 0.9*w0, 1.1*w0, 2*w0, 5, 10, 20, 40, 80][:])
        res[K] = (2/np.pi)*I
    gint = quad(lambda r: (1 - 2/np.pi*np.arcsin(a/r))*2*np.pi*r, a, b)[0]
    print(f'B b={b} wp2={wp2} w0={w0} g={gam}: integrals', res, ' pred(g=shadow)', wp2*gint, ' full area', wp2*np.pi*(b*b-a*a))
    out[f'B_{b}_{wp2}_{w0}'] = dict(res=res, pred_shadow=wp2*gint, pred_full=wp2*np.pi*(b*b-a*a))
json.dump(out, open('sumrule_check.json','w'), indent=1, default=str)
