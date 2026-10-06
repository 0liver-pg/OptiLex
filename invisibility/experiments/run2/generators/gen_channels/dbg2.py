import numpy as np
import fastvp
from scipy.special import jv,yv
k=np.pi/2; ns=np.arange(3); rg=np.linspace(1,3,5)
src=open('fastvp.py').read().replace("        d=d+np.mod(raw-d+1e-7,np.pi)-1e-7","        print(j, raw, d); d=d+np.mod(raw-d+1e-7,np.pi)-1e-7")
exec(src)
print(lifted_phases(np.zeros(4),rg,k,ns))
