import numpy as np, sys
from scipy.special import jv, yv
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d
k=np.pi/2; a=1.0; b=3.0; chimax=5.0
NC=np.arange(0,15)          # channels |n|
g=np.where(NC==0,1.0,2.0)
def flow(chi_seg, edges, nsub=24, ns=NC, kk=k):
    """integrate variable-phase eqs for all channels with piecewise-constant chi on segments (RK4)"""
    d=np.arctan2(jv(ns,kk*a), yv(ns,kk*a))
    for (r0,r1),c in zip(zip(edges[:-1],edges[1:]),chi_seg):
        if c==0: continue
        h=(r1-r0)/nsub; r=r0
        def f(r,d):
            return 0.5*np.pi*kk**2*r*c*(np.cos(d)*jv(ns,kk*r)-np.sin(d)*yv(ns,kk*r))**2
        for _ in range(nsub):
            k1=f(r,d);k2=f(r+h/2,d+h/2*k1);k3=f(r+h/2,d+h/2*k2);k4=f(r+h,d+h*k3)
            d=d+h/6*(k1+2*k2+2*k3+k4); r+=h
    return d
def sig(d,kk=k): return 4/kk*np.sum(g*np.sin(d)**2)
if __name__=='__main__':
    # check vs cloak2d on the L16 optimum
    eps=[6,6,6,1.9236435417033926]+[1]*12
    edges=np.linspace(1,3,17)
    d=flow(np.array(eps)-1,edges,nsub=40)
    m=np.sqrt(np.array(eps,float)); radii=list(edges)
    print('vp sigma',sig(d),'cloak2d',cloak2d.widths(list(m),radii,k,core='pec')[1])
    d0=flow(np.zeros(16),edges); print('bare',sig(d0))
    dmax=flow(np.full(16,chimax),edges,nsub=40)
    for n,lo,hi in zip(NC,d0,dmax):
        print(n, round(lo,4), round(hi,4), 'contains k*pi:', np.floor(hi/np.pi)>=np.ceil(lo/np.pi), 'bare ch width',round((4/k)*(1 if n==0 else 2)*np.sin(lo)**2,5))
