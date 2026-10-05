import sys, math
sys.path.insert(0, 'climate')
from physics import *
bbl=0.158987
for rate in (20e3,40e3,60e3):
    q=rate*bbl/86400
    for load in (10,15,20):
        print(f"{rate/1e3:.0f}k bbl/d load {load} kg/m3 -> {q*86400*365*load/1e6:.1f} kt/yr per well")
    for name,idm in (("3.5in",0.076),("4.5in",0.0995),("5.5in",0.1245),("7in",0.159)):
        v=q/(math.pi*idm**2/4); print(f"   {name} tubing: {v:.1f} m/s")
# wells needed per pad
for src in (50,100,150,200):
    for per in (35,52,70):
        print(src,"kt/yr at",per,"kt/well ->",math.ceil(src/per),"wells")
