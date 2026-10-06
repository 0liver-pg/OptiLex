import sys, numpy as np, json
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d
from scipy.special import jv, yv
from scipy.integrate import solve_ivp
k=np.pi/2; a=1.0; b=3.0
def vp_phase(eps_fn, n, k, radii_breaks):
    d0=np.arctan2(jv(n,k*a), yv(n,k*a))  # tan d = J/Y
    def f(r,d):
        phi=np.cos(d)*jv(n,k*r)-np.sin(d)*yv(n,k*r)
        return 0.5*np.pi*k**2*(eps_fn(r)-1)*r*phi**2
    d=d0
    for r0,r1 in zip(radii_breaks[:-1],radii_breaks[1:]):
        sol=solve_ivp(f,(r0,r1),[d],rtol=1e-12,atol=1e-14)
        d=sol.y[0,-1]
    return d0,d
rng=np.random.default_rng(0); worst=0
for t in range(6):
    L=rng.integers(1,6); radii=list(np.linspace(1,3,L+1)); eps=rng.uniform(1,6,L)
    efn=lambda r,eps=eps,radii=radii: eps[min(np.searchsorted(radii,r,side='right')-1,L-1)]
    nn,bb=cloak2d.coeffs(np.sqrt(eps),radii,k,pol='TM',core='pec')
    for n in range(0,4):
        d0,d=vp_phase(efn,n,k,radii)
        bvp=(np.exp(2j*d)-1)/2
        worst=max(worst,abs(bvp-bb[nn==n][0]))
print('max |b_vp - b_cloak2d| over 6 random designs, n=0..3:',worst)
J=json.load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/de_ext_B0.0_L16.json'))
eps=np.array(J['eps']); radii=J['radii']; L=len(eps)
efn=lambda r: eps[min(np.searchsorted(radii,r,side='right')-1,L-1)]
for n in range(4):
    d0,d=vp_phase(efn,n,k,radii)
    g=1 if n==0 else 2
    print(n,'delta_PEC=%.4f delta_b=%.4f  bare width %.4f  design width %.4f'%(d0,d,4/k*g*np.sin(d0)**2,4/k*g*np.sin(d)**2))
