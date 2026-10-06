import numpy as np
from scipy.special import jv,yv,jvp,yvp
k=np.pi/2;n=0
for r in [1.0,1.5,2.0]:
    J,Y,Jp,Yp=jv(n,k*r),yv(n,k*r),k*jvp(n,k*r),k*yvp(n,k*r)
    # take u = cos d0 J - sin d0 Y with d0=0.3
    d0=0.3; u=np.cos(d0)*J-np.sin(d0)*Y; up=np.cos(d0)*Jp-np.sin(d0)*Yp
    W=J*Yp-Jp*Y; cc=(u*Yp-up*Y)/W; ss=-(J*up-Jp*u)/W
    print(r, cc, ss, np.arctan2(ss,cc))
