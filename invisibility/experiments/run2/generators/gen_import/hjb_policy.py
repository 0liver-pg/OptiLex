import numpy as np, sys, time, json
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d
from scipy.special import jv, yv
from scipy.ndimage import map_coordinates
k=float(sys.argv[1]); chans=[int(c) for c in sys.argv[2].split(',')]; G=int(sys.argv[3]); nr=int(sys.argv[4]); epsmax=float(sys.argv[5])
a,b=1.0,3.0; chi=epsmax-1; m=len(chans); g=np.array([1 if n==0 else 2 for n in chans])
d=np.arange(G)*np.pi/G; grids=np.meshgrid(*([d]*m),indexing='ij')
V=sum(4/k*g[i]*np.sin(grids[i])**2 for i in range(m))
rs=np.linspace(a,b,nr+1); dr=rs[1]-rs[0]
JY={n:(lambda r,n=n:(jv(n,k*r),yv(n,k*r))) for n in chans}
def K(n,r,dl):
    J,Y=JY[n](r); phi=np.cos(dl)*J-np.sin(dl)*Y; return 0.5*np.pi*k**2*r*phi**2
mus=np.linspace(0,chi,5); pol=np.zeros((nr,)+V.shape,np.uint8); t0=time.time()
def step(gr,r0,mu):
    out=[]
    for i,n in enumerate(chans):
        k1=K(n,r0,gr[i]); k2=K(n,r0+dr/2,gr[i]+0.5*dr*mu*k1); out.append(gr[i]+dr*mu*k2)
    return out
for j in range(nr-1,-1,-1):
    best=V.copy(); arg=np.zeros(V.shape,np.uint8)
    for q,mu in enumerate(mus[1:],1):
        Vi=map_coordinates(V,[x*G/np.pi for x in step(grids,rs[j],mu)],order=1,mode='grid-wrap')
        better=Vi<best; best=np.where(better,Vi,best); arg[better]=q
    V=best; pol[j]=arg
d0=np.array([np.arctan2(jv(n,k*a),yv(n,k*a))%np.pi for n in chans])
val=float(map_coordinates(V,[[x*G/np.pi] for x in d0],order=1,mode='grid-wrap')[0])
# forward rollout with nearest-node policy
dl=d0.copy(); eps=[]
for j in range(nr):
    idx=tuple(int(round(x*G/np.pi))%G for x in dl); mu=mus[pol[j][idx]]; eps.append(1+mu)
    dl=np.array(step([np.array(x) for x in dl],rs[j],mu)).ravel()
eps=np.array(eps); sub=4/k*np.sum(g*np.sin(dl)**2)
w=cloak2d.widths(np.sqrt(eps.astype(complex)),list(rs),k,pol='TM',core='pec')
bare=cloak2d.widths([], [a], k, pol='TM', core='pec')[1]
nn,bb=cloak2d.coeffs(np.sqrt(eps.astype(complex)),list(rs),k,pol='TM',core='pec')
chw={n:float(4/k*(np.abs(bb[nn==n])**2+(np.abs(bb[nn==-n])**2 if n else 0)).sum()) for n in range(5)}
sw=np.flatnonzero(np.diff(eps)!=0)
print(json.dumps(dict(k=k,chans=chans,G=G,nr=nr,epsmax=epsmax,dp_value=val,rollout_subset_vp=float(sub),rollout_design_ext_cloak2d=float(w[1]),bare=float(bare),R_design=float(w[1]/bare),R_dp_floor=val/bare,channel_widths_design=chw,switch_radii=[float(rs[i+1]) for i in sw][:20],eps_at_switches=[float(eps[i+1]) for i in sw][:20],secs=round(time.time()-t0,1))))
