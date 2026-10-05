import sys, itertools
sys.path.insert(0, 'climate')
from physics import *
M_CH4=16.043; M_CO2_=44.01
mass_ratios=[3.2,4.5]          # CO2/CH4 mass in same pore volume (idea's PR-EOS)
WC=[1/0.6,1/1.0]               # working/cushion
fs=[0.3,0.5]
N=30; target=0.95
Lmax=1-target**(1/N)
print(f"allowed annual loss for {target:.0%} after {N} cycles: {Lmax*100:.3f}%/yr")
xs=[]
for mr,wc,f in itertools.product(mass_ratios,WC,fs):
    R=mr*M_CH4/M_CO2_
    x=Lmax*f*R/wc; xs.append(x)
print(f"max mean withdrawn CO2 mol%: {min(xs)*100:.3f}-{max(xs)*100:.3f}")
# 98% after 30 for strict variant
L98=1-0.98**(1/N)
print("98%:",[round(L98*f*mr*M_CH4/M_CO2_/wc*100,3) for mr,wc,f in [(3.2,1/0.6,0.3),(4.5,1.0,0.5)]])
# check critic numbers
for x in [0.005,0.01,0.025]:
    Ls=[x*wc/(f*mr*M_CH4/M_CO2_) for mr,wc,f in itertools.product(mass_ratios,WC,fs)]
    print(f"x={x*100}%: loss/yr {min(Ls)*100:.1f}-{max(Ls)*100:.1f}%, 30-cycle lost {(1-(1-min(Ls))**N)*100:.0f}-{(1-(1-max(Ls))**N)*100:.0f}%")
# CO2 per bcm at 1 mol%
mol_per_bcm=1e9/0.023645  # std m3 at 15C,1atm
print("kt CO2 per bcm at 1mol%:", 0.01*mol_per_bcm*44.01e-3/1e6)
# Option (b): cleanup unit on withdrawal stream
for x_in in [0.005,0.01,0.025]:
    cf=1-0.0004/x_in  # reduce to 0.04 mol%
    w=min_separation_work(x_in, capture_fraction=cf, purity=0.99)
    print(f"cleanup x_in={x_in*100}% cf={cf:.3f}: floor {gj_per_tonne(w):.2f} GJ/t removed")
# re-handled CO2 per stored tonne over 30 yr, real amine 2.5-4 GJ/t + recompression 0.25
for x in [0.005,0.01]:
    Ls=[x*wc/(f*mr*M_CH4/M_CO2_) for mr,wc,f in itertools.product(mass_ratios,WC,fs)]
    lo,hi=min(Ls)*N,max(Ls)*N
    print(f"x={x*100}%: re-handled {lo:.2f}-{hi:.2f} t/t stored over 30y; energy {lo*2.75:.2f}-{hi*4.25:.2f} GJ/t stored (2.5-4 GJ/t amine +0.25 recompression)")
# Decommissioning baseline: net climate effect of sale variant
# gross stored 1 t CO2 frees m CH4 -> burn emits m*44/16 t CO2
for mr in mass_ratios:
    m=1/mr; e=m*M_CO2_/M_CH4
    print(f"mass ratio {mr}: freed CH4 {m:.3f} t, burn {e:.2f} t CO2; net if never recovered {1-e:.2f}; net if recovered at decommissioning anyway ~{1.0:.2f} minus losses")
# cleanup capacity factor: withdrawal season ~120-150 d
print("capacity factor if sized for withdrawal season:", round(120/365,2), round(150/365,2))
