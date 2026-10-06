# Check on exact layered designs: (a) reciprocity formula for b_m; (b) ellipsoid constraint holds.
import sys, numpy as np
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d as c
from scipy.special import jv, hankel1, jvp, h1vp
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
rng = np.random.default_rng(1)
def field_channel(m, k, radii, eps, r_eval):
    # E_z channel m (coefficient of e^{im phi}) with incident i^m J_m; integrate u'' = -u'/r - (k^2 eps - m^2/r^2) u from r=1, u(1)=0,u'(1)=1
    def epsf(r): return eps[min(np.searchsorted(radii, r, side='right')-1, len(eps)-1)]
    sol = solve_ivp(lambda r, y: [y[1], -y[1]/r - (k**2*epsf(r) - m**2/r**2)*y[0]], [1, radii[-1]], [0, 1],
                    t_eval=r_eval, rtol=1e-11, atol=1e-13, max_step=0.01)
    solb = solve_ivp(lambda r, y: [y[1], -y[1]/r - (k**2*epsf(r) - m**2/r**2)*y[0]], [1, radii[-1]], [0, 1], rtol=1e-11, atol=1e-13, max_step=0.01)
    ub, dub = solb.y[0, -1], solb.y[1, -1]; b = radii[-1]
    # match alpha*u = i^m (J + bm H) and derivative
    M = np.array([[ub, -hankel1(m, k*b)], [dub, -k*h1vp(m, k*b)]]); rhs = (1j)**m*np.array([jv(m, k*b), k*jvp(m, k*b)])
    alpha, cb = np.linalg.solve(M, rhs); bm = cb/(1j)**m
    return alpha*sol.y[0], bm
def check(k, b, em, L=6, mmax=12, nq=150):
    radii = np.linspace(1, b, L+1); eps = rng.uniform(1, em, L); eps[0] = em
    x, w = leggauss(nq); r = 1 + (b-1)*(x+1)/2; w = w*(b-1)/2; s = np.sqrt(2*np.pi*r*w)
    chi = np.array([eps[min(np.searchsorted(radii, ri, side='right')-1, L-1)] for ri in r]) - 1
    n, bref = c.coeffs(np.sqrt(eps.astype(complex)), list(radii), k, pol='TM', core='pec'); N = len(n)//2
    lhs = 0; rhsv = 0; maxerr = 0
    for m in range(-mmax, mmax+1):
        am = abs(m); cc = jv(am, k)/hankel1(am, k)
        E, bm = field_channel(am, k, radii, eps, r)            # radial profile of channel m (incident i^|m| J)
        E = E*(1j)**(m-am) if False else E*((1j)**m/(1j)**am)  # adjust i^m factor for negative m
        p = chi*E
        psi = jv(am, k*r) - cc*hankel1(am, k*r)
        bm_rec = -cc + (1j*k**2/4)*(1j)**(-m)*np.sum(2*np.pi*r*w*psi*p)
        maxerr = max(maxerr, abs(bm_rec - bref[N+m]))
        R1, R2 = np.meshgrid(r, r, indexing='ij'); rl = np.minimum(R1, R2); rg = np.maximum(R1, R2)
        G = 0.25j*(jv(am, k*rl) - cc*hankel1(am, k*rl))*hankel1(am, k*rg)
        K = k**2*s[:, None]*G*s[None, :]; H = (K + K.conj().T)/2
        y = s*p; Ed = (1j)**m*psi*s
        lhs += np.real(np.conj(y) @ (y/(em-1)) - np.conj(y) @ (H @ y)); rhsv += np.real(np.conj(y) @ Ed)
    print(f"ka={k:.3f} b={b} eps_max={em} eps={np.round(eps,2)}: max|b_m(recip)-b_m(cloak2d)|={maxerr:.2e}; constraint lhs={lhs:.5f} <= rhs={rhsv:.5f}: {lhs <= rhsv+1e-9}")
for args in [(np.pi/2, 1.5, 2), (np.pi/2, 1.5, 6), (0.5, 3.0, 4), (np.pi/2, 3.0, 6)]:
    check(*args)
