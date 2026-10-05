import sys, math
sys.path.insert(0, 'climate')
from physics import *
BBL=0.158987; YR=365.25
def crf(r,n): return r*(1+r)**n/((1+r)**n-1)
E=0.325; elec=60; r,n=0.08,20; om=0.035; chem=1.0
def cost(Q, bbl_well, load, util, retro, per_well_perm, spur_km, spur_m, trunk_km, mrv_cap, mrv_opex, comp_kw=3000):
    pw=bbl_well*BBL*YR*util*load/1000
    nw=math.ceil(Q/pw)
    mw=Q*E*1e9/(YR*86400)/1e6/0.9
    capex=mw*1000*comp_kw+trunk_km*1.0e6+nw*spur_km*spur_m+nw*(retro+per_well_perm)+mrv_cap
    c=capex*crf(r,n)/Q+E/3.6*elec+capex*om/Q+(mrv_opex+nw*0.1e6)/Q+chem
    return nw,pw,capex,c
print("A. Original base hub (0.3 Mt/yr, 20k bbl/d wells, 15 kg/m3) with and without per-well Class VI-type burden")
for perm in (0,2e6,4e6):
    nw,pw,cx,c=cost(0.3e6,20000,15,0.75,2e6,perm,2.5,0.4e6,10,10e6,1.0e6)
    print(f"  per-well permit/AoR/monitoring ${perm/1e6:.0f}M: {nw} wells, capex ${cx/1e6:.0f}M, ${c:.0f}/t")
print("B. Right-sized: source sized to one commercial SWD pad (wells on one pad, no spurs, short trunk)")
for Q,bbl,nload in ((0.05e6,40000,15),(0.1e6,40000,15),(0.1e6,60000,20),(0.2e6,60000,20)):
    for perm in (0,2e6):
        nw,pw,cx,c=cost(Q,bbl,nload,0.8,2e6,perm,0.2,0.4e6,3,4e6,0.6e6)
        print(f"  Q {Q/1e6:.2f} Mt/yr, {bbl/1e3:.0f}k bbl/d/well, {nload} kg/m3, perm ${perm/1e6:.0f}M: {nw} wells, ${c:.0f}/t")
print("C. Baseline dedicated well for small sources (same trunk 3 km)")
for Q in (0.05e6,0.1e6,0.2e6):
    e=0.217/0.65+0.02; mw=Q*e*1e9/(YR*86400)/1e6/0.9
    cx=mw*1000*3000+3*1e6+12e6+4e6
    c=cx*crf(r,n)/Q+e/3.6*elec+cx*om/Q+0.6e6/Q+chem
    print(f"  Q {Q/1e6:.2f} Mt/yr: 1 new $12M well, ${c:.0f}/t")
print("D. Vacuum-well liquid level: release depth below surface")
for depth,grad in ((3500,0.43),(3500,0.38),(4000,0.35)):
    fl=depth*(1-grad/0.47)  # static fluid level below surface for sub-hydrostatic reservoir, 0.47 psi/ft brine
    for rel in (324,556):
        print(f"  zone {depth} m at {grad} psi/ft: fluid level ~{fl:.0f} m; release at >= {fl+rel:.0f} m for {rel} m submergence")
print("E. Free-gas void fraction at release (60 bar, 40C, 15 kg/m3 water)")
rho=60e5*0.044/(8.314*313)/0.8  # Z~0.8 rough
print(f"  CO2 gas density ~{rho:.0f} kg/m3 -> gas/water volume ratio {15/rho:.2f}")
