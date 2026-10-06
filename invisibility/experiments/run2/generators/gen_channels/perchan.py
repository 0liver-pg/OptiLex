# Rigorous-in-principle per-channel reachable-phase floor (Kamke comparison): delta_n in [delta_n(chi=0), delta_n(chi=chimax shell)]
import numpy as np, json, sys
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim'); import cloak2d
from fastvp import lifted_phases
def floors(ka,ba,em,ns=np.arange(0,30)):
    k=ka; rg=np.linspace(1,ba,int(200*(ba-1))+1); N=len(rg)-1
    g=np.where(ns==0,1.,2.)
    d0=lifted_phases(np.zeros(N),rg,k,ns); dm=lifted_phases(np.full(N,em-1.),rg,k,ns)
    m=np.ceil(d0/np.pi-1e-12)*np.pi
    fl=np.where(m<=dm,0.0,np.minimum(np.sin(d0)**2,np.sin(dm)**2))
    bare=4/k*np.sum(g*np.sin(d0)**2); full=cloak2d.widths([np.sqrt(em)],[1,ba],k,core='pec')[1]
    return 4/k*np.sum(g*fl)/bare, bare, full/bare, [(int(n),round(float(x),3),round(float(y),3)) for n,x,y in zip(ns[:4],d0[:4],dm[:4])]
out=[]
for ka in [0.5,1.0,np.pi/2,3.0]:
  for ba in [1.25,1.5,2.0,3.0]:
    for em in [2,4,6,12]:
      r,bare,full,ph=floors(ka,ba,em)
      out.append(dict(ka=ka,ba=ba,eps_max=em,floor_ratio=r,bare=bare,full_shell_ratio=full,phases=ph))
      print(f"ka={ka:.3f} b/a={ba} em={em}: per-channel floor R>={r:.4f}  (full eps_max shell R={full:.3f}) ch0..3 [d0,dmax]={ph}")
json.dump(out,open('perchannel_floor_sweep.json','w'),indent=1)
