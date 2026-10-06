import numpy as np, sys, time, json
from scipy.special import jv, yv
from scipy.ndimage import map_coordinates
k=float(sys.argv[1]) if len(sys.argv)>1 else np.pi/2
chans=[int(c) for c in sys.argv[2].split(',')] if len(sys.argv)>2 else [0,1]
G=int(sys.argv[3]) if len(sys.argv)>3 else 256
nr=int(sys.argv[4]) if len(sys.argv)>4 else 400
epsmax=float(sys.argv[5]) if len(sys.argv)>5 else 6.0
a,b=1.0,3.0; chi=epsmax-1
m=len(chans); g=np.array([1 if n==0 else 2 for n in chans])
d=np.arange(G)*np.pi/G
grids=np.meshgrid(*([d]*m),indexing='ij')
V=sum(4/k*g[i]*np.sin(grids[i])**2 for i in range(m))
rs=np.linspace(a,b,nr+1); dr=rs[1]-rs[0]
def K(n,r,dl):
    phi=np.cos(dl)*jv(n,k*r)-np.sin(dl)*yv(n,k*r); return 0.5*np.pi*k**2*r*phi**2
mus=np.linspace(0,chi,5)
t0=time.time()
for j in range(nr-1,-1,-1):
    r0=rs[j]; rm=r0+dr/2
    best=V.copy()  # mu=0
    for mu in mus[1:]:
        # RK2 per channel
        newc=[]
        for i,n in enumerate(chans):
            k1=K(n,r0,grids[i]); k2=K(n,rm,grids[i]+0.5*dr*mu*k1)
            newc.append((grids[i]+dr*mu*k2)*G/np.pi)
        Vi=map_coordinates(V,newc,order=1,mode='grid-wrap')
        best=np.minimum(best,Vi)
    V=best
d0=[np.arctan2(jv(n,k*a),yv(n,k*a))%np.pi for n in chans]
val=map_coordinates(V,[[x*G/np.pi] for x in d0],order=1,mode='grid-wrap')[0]
bare=sum(4/k*g[i]*np.sin(d0[i])**2 for i in range(m))
print(json.dumps(dict(k=k,chans=chans,G=G,nr=nr,epsmax=epsmax,value=float(val),bare_subset=float(bare),secs=round(time.time()-t0,1))))
