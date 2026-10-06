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
out = {}
for k0 in (1.45, 1.57, 3.0):
    E0 = k0**2; zs = np.linspace(0, 1, 11)
    tf = [theta_free(E0+z, z) for z in zs]
    t1 = [theta_shell(E0+z, z, lambda r: 1.0) for z in zs]
    t6 = [theta_shell(E0+z, z, lambda r: 6.0) for z in zs]
    tL16 = [theta_shell(E0+z, z, lambda r: 6.0 if r < 1.375 else (1.9236 if r < 1.5 else 1.0)) for z in zs]
    rec = dict(k0=k0, k1=float(np.sqrt(E0+1)), zeta=zs.tolist(), theta_free=tf, theta_eps1=t1, theta_eps6=t6, theta_L16opt=tL16,
               free_monotone=bool(np.all(np.diff(tf) >= -1e-9)), eps6_monotone=bool(np.all(np.diff(t6) >= -1e-9)),
               L16_monotone=bool(np.all(np.diff(tL16) >= -1e-9)))
    out[str(k0)] = rec
    print(f'k0={k0} k1={np.sqrt(E0+1):.3f} | free {tf[0]:.3f}->{tf[-1]:.3f} mono={rec["free_monotone"]} | eps=1 {t1[0]:.3f}->{t1[-1]:.3f} | eps=6 {t6[0]:.3f}->{t6[-1]:.3f} mono={rec["eps6_monotone"]} | L16opt {tL16[0]:.3f}->{tL16[-1]:.3f}')
json.dump(out, open('fah_line.json', 'w'), indent=1)
