# Frequency/angular-momentum (FAH) line check for radial TM cloaks around a PEC core (a=1, b=3).
# Pruefer angle theta = atan2(u, r u') at r=b for -(r u')' + (lam/r - E eps r) u = 0, u(a)=0.
# Along the line E = E0 + zeta/a^2, lam = n0^2 + zeta, d/dzeta of the potential = 1/r - eps r/a^2 <= 0 on r>=a (eps>=1),
# so theta_design(b) is non-decreasing in zeta (scalar ODE comparison); the free disk (r from 0) has no such sign.
import json, numpy as np
from scipy.integrate import solve_ivp
from scipy.special import jv, jvp
a, b = 1.0, 3.0
def theta_shell(E, lam, epsf):
    f = lambda r, th: [np.cos(th[0])**2/r - (lam/r - E*epsf(r)*r)*np.sin(th[0])**2]
    return solve_ivp(f, (a, b), [0.0], rtol=1e-10, atol=1e-12).y[0, -1]
def theta_free(E, lam):
    k = np.sqrt(E); nu = np.sqrt(lam); r0 = 1e-3
    th0 = np.arctan2(jv(nu, k*r0), k*r0*jvp(nu, k*r0)) if nu > 0 else np.arctan2(jv(0, k*r0), k*r0*jvp(0, k*r0))
    f = lambda r, th: [np.cos(th[0])**2/r - (lam/r - E*r)*np.sin(th[0])**2]
    return solve_ivp(f, (r0, b), [th0], rtol=1e-10, atol=1e-12).y[0, -1]
def _main():
  out = {}
  for k0 in (1.45, 1.57, 3.0):
    E0 = k0**2; zs = np.linspace(0, 1, 11)
    tf = [theta_free(E0+z, z) for z in zs]
    t1 = [theta_shell(E0+z, z, lambda r: 1.0) for z in zs]
