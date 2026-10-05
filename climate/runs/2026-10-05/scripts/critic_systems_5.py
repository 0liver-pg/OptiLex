import sys, math
sys.path.insert(0,'climate')
from physics import *
GWP=27.0
# (A) NT2 pulse decay vs build lag. Measured: 10 Gg/yr (2010) -> 2 Gg/yr (2012)
k=math.log(10/2)/2.0  # per yr
print(f"NT2 e-fold time {1/k:.2f} yr")
capex=44e6; crf=0.08*1.08**20/(1.08**20-1)
for lag in [0,1,2,3]:
    for life in [20]:
        tot=0.75*10e3*(math.exp(-k*lag)-math.exp(-k*(lag+life)))/k  # t CH4 captured (whole downstream, optimistic)
        tco2e=tot*GWP
        # levelise capex over life as total capex / total t (undiscounted, lower bound)
        print(f"lag {lag} yr: lifetime capture {tot/1e3:.1f} kt CH4 = {tco2e/1e6:.3f} Mt CO2e; capex-only >= ${capex/tco2e:.0f}/t (undiscounted)")
# (B) Low-head persistent emitter, Balbina-like: head 22 m, Q 600 m3/s, captured 26 kt CH4/yr (TEA base)
rho,g,eta=1000,9.81,0.9
for dh in [1,2,4]:
    P=rho*g*600*dh*eta/1e6
    E=P*8760*0.5  # MWh/yr at ~50% of mean (only flow-weighted); use full-year as upper
    Efull=P*8760
    for fox in [0.0,0.4]:
        net=26e3*(1-fox)*GWP
        print(f"dh {dh} m: {P:.1f} MW = {dh/22*100:.0f}% of output; fox {fox}: net {net/1e6:.2f} Mt CO2e/yr; lost power ${Efull*60/net:.1f}/t @ $60/MWh")
