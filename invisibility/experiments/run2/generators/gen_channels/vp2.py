import numpy as np, sys
from scipy.special import jv, yv
from scipy.integrate import solve_ivp
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d
k=np.pi/2; a=1.0; b=3.0; chimax=5.0
NC=np.arange(0,13); g=np.where(NC==0,1.0,2.0)
def flow(chi_of_r, kk=k, ns=NC, rtol=1e-10):
    d0=np.arctan2(jv(ns,kk*a), yv(ns,kk*a))
    def f(r,d): return 0.5*np.pi*kk**2*r*chi_of_r(r)*(np.cos(d)*jv(ns,kk*r)-np.sin(d)*yv(ns,kk*r))**2
    s=solve_ivp(f,(a,b),d0,method='Radau',rtol=rtol,atol=1e-12,max_step=0.02)
    return s.y[:,-1]
def sig(d,kk=k): return 4/kk*np.sum(g*np.sin(d)**2)
if __name__=='__main__':
    eps=np.array([6,6,6,1.9236435417033926]+[1]*12); edges=np.linspace(1,3,17)
    chi=lambda r: eps[min(int((r-1)/0.125),15)]-1
    d=flow(chi); m=np.sqrt(eps); print('vp',sig(d),'cloak2d',cloak2d.widths(list(m),list(edges),k,core='pec')[1])
    d0=flow(lambda r:0.0); dm=flow(lambda r:chimax)
    print('bare',sig(d0), 'full eps6 shell', sig(dm), cloak2d.widths([np.sqrt(6)],[1,3],k,core='pec')[1])
    for n,lo,hi in zip(NC,d0,dm): print(n, round(lo,4), round(hi,4), round((hi-lo)/np.pi,3))
