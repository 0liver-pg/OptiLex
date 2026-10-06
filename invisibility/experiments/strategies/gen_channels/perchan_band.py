# Band version: pointwise-in-k per-channel floor, uniform window, Gauss-Legendre 24 nodes (prototype; final needs k-interval enclosures)
import numpy as np, json
from fastvp import lifted_phases
def fl_k(k,ba,em,ns=np.arange(0,25)):
    rg=np.linspace(1,ba,int(160*(ba-1))+1); N=len(rg)-1; g=np.where(ns==0,1.,2.)
    d0=lifted_phases(np.zeros(N),rg,k,ns); dm=lifted_phases(np.full(N,em-1.),rg,k,ns)
    m=np.ceil(d0/np.pi-1e-12)*np.pi
    fl=np.where(m<=dm,0.0,np.minimum(np.sin(d0)**2,np.sin(dm)**2))
    return 4/k*np.sum(g*fl), 4/k*np.sum(g*np.sin(d0)**2)
x,w=np.polynomial.legendre.leggauss(24)
out=[]
for ka,ba,em in [(np.pi/2,1.25,6),(np.pi/2,1.5,4),(np.pi/2,1.5,6),(np.pi/2,2.0,2),(np.pi/2,2.0,4),(1.0,2.0,2),(1.0,3.0,2),(3.0,1.5,2),(0.5,3.0,2),(np.pi/2,3.0,2)]:
  for B in [0.0,0.1,0.3]:
    if B==0: F,Bb=fl_k(ka,ba,em); r=F/Bb
    else:
        ks=ka*(1+B/2*x); vals=np.array([fl_k(kk,ba,em) for kk in ks]); r=np.sum(w*vals[:,0])/np.sum(w*vals[:,1])
    out.append(dict(ka=ka,ba=ba,eps_max=em,B=B,floor_ratio=r)); print(f"ka={ka:.3f} b/a={ba} em={em} B={B}: floor {r:.4f}",flush=True)
json.dump(out,open('perchannel_floor_band.json','w'),indent=1)
