import numpy as np
from scipy.special import jv, yv, jvp, yvp
a=1.0; b=3.0
def lifted_phases(chi_sub, rgrid, k, ns):
    """exact layered propagation (piecewise-constant chi on sublayers rgrid) of all channels, returns lifted variable phase at b.
    Lift assumes per-sublayer increment in [0, pi) (monotone phase, chi>=0)."""
    ns=np.asarray(ns)[:,None]
    # free functions at grid points
    x=k*rgrid[None,:]
    J=jv(ns,x); Y=yv(ns,x); Jp=jvp(ns,x); Yp=yvp(ns,x)
    # start at r=a: u=0, u'=1
    u=np.zeros(ns.shape[0]); up=np.ones(ns.shape[0])
    d=np.arctan2(J[:,0],Y[:,0])
    for j in range(len(rgrid)-1):
        r0,r1=rgrid[j],rgrid[j+1]; c=chi_sub[j]; q=k*np.sqrt(1+c)
        if c!=0:
            j0,y0,jp0,yp0=jv(ns[:,0],q*r0),yv(ns[:,0],q*r0),q*jvp(ns[:,0],q*r0),q*yvp(ns[:,0],q*r0)
            W=j0*yp0-jp0*y0
            A=(u*yp0-up*y0)/W; B=(j0*up-jp0*u)/W
            u,up=A*jv(ns[:,0],q*r1)+B*yv(ns[:,0],q*r1), q*(A*jvp(ns[:,0],q*r1)+B*yvp(ns[:,0],q*r1))
        else:
            j0,y0,jp0,yp0=J[:,j],Y[:,j],k*Jp[:,j],k*Yp[:,j]
            W=j0*yp0-jp0*y0
            A=(u*yp0-up*y0)/W; B=(j0*up-jp0*u)/W
            u,up=A*J[:,j+1]+B*Y[:,j+1], A*k*Jp[:,j+1]+B*k*Yp[:,j+1]
        # variable phase at r1: u ∝ cos d J - sin d Y ; up ∝ k(cos d J' - sin d Y')
        Jr,Yr,Jpr,Ypr=J[:,j+1],Y[:,j+1],k*Jp[:,j+1],k*Yp[:,j+1]
        W=Jr*Ypr-Jpr*Yr
        cc=(u*Ypr-up*Yr)/W; ss=-(Jr*up-Jpr*u)/W
        raw=np.arctan2(ss,cc)
        d=d+np.mod(raw-d+1e-7,np.pi)-1e-7
        # renormalise
        nrm=np.hypot(u,up/k); u/=nrm; up/=nrm
    return d
