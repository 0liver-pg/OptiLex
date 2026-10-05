import sys
sys.path.insert(0, 'climate')
from physics import *
for name,x in (("aluminium smelter 1%",0.01),("NGCC 4%",0.04),("coal 12%",0.12),("cement 25%",0.25)):
    row=[]
    for f in (0.5,0.9,0.95,0.99):
        row.append(f"{f:.0%}:{gj_per_tonne(min_separation_work(x,f,0.99)):.3f}")
    # marginal work for the last 9 points (90->99%) per tonne of extra CO2
    w90 = min_separation_work(x,0.90,0.99)*0.90; w99=min_separation_work(x,0.99,0.99)*0.99
    marg = gj_per_tonne((w99-w90)/0.09)
    print(f"{name}: avg GJ/t {row}; marginal 90->99% {marg:.3f} GJ/t")
