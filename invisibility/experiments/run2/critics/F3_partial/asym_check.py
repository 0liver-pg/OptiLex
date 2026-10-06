# Check: Asym(z^2 g_n) on annulus a<r<b (PEC at r=a, TM, harmonic n) is PSD for z in first quadrant,
# and Asym(g_n) alone (no z^2) or z-weighted variants are not necessarily PSD.
import numpy as np
from scipy.special import jv, hankel1
a,b=1.0,3.0; kc=np.pi/2
def gn(n,z,r):
    rl=np.minimum.outer(r,r); rg=np.maximum.outer(r,r)
    # 2D outgoing Green fn of (-lap - z^2) with Dirichlet at r=a, harmonic n (per 2pi normalisation)
    return (1j/4)*(jv(n,z*rl)-jv(n,z*a)/hankel1(n,z*a)*hankel1(n,z*rl))*hankel1(n,z*rg)
N=400; r=np.linspace(a,b,N+1); r=0.5*(r[1:]+r[:-1]); w=(b-a)/N*r*2*np.pi
sq=np.sqrt(w)
out={}
for z in [kc*(1+0.05j), kc*(1+0.005j), kc*(0.95+0.15j), kc*(1.3+0.3j), kc*(0.2+1j)]:
    worst={'z2g':np.inf,'g':np.inf,'zg':np.inf}
    for n in range(0,13):
        M=sq[:,None]*gn(n,z,r)*sq[None,:]
        for key,fac in [('z2g',z**2),('g',1.0),('zg',z)]:
            A=fac*M; As=(A-A.conj().T)/2j
            ev=np.linalg.eigvalsh(As); worst[key]=min(worst[key],ev.min()/np.abs(ev).max())
    out[str(z)]=worst
    print(z, {k:f"{v:.2e}" for k,v in worst.items()})
