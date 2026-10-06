import numpy as np,time,sys
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim'); import cloak2d
from fastvp import *
k=np.pi/2; ns=np.arange(13); g=np.where(ns==0,1,2)
rg=np.linspace(1,3,81)
eps=np.array([6,6,6,1.9236435417033926]+[1]*12)
chi=np.repeat(eps-1,5)
t=time.time(); d=lifted_phases(chi,rg,k,ns); print(time.time()-t)
print(4/k*np.sum(g*np.sin(d)**2))
d0=lifted_phases(np.zeros(80),rg,k,ns); dm=lifted_phases(np.full(80,5.),rg,k,ns)
print(np.round(d0,4)); print(np.round(dm,4))
