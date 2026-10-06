import time,numpy as np
from vp2 import *
M=8; edges=np.linspace(1,3,M+1)
def pw(vals):
    return lambda r: vals[min(int((r-1)/(2/M)),M-1)]
t=time.time()
for i in range(5): flow(pw(np.random.rand(M)*5),rtol=1e-8)
print((time.time()-t)/5)
