"""Patch check for bottleneck_thermo_4: (a) net-tonne accounting vs grid intensity, (b) price+carbon gated
hybrid on DE-LU 2025 (reuses critic_bt4_hybrid data loaders). Gross cost $673/t from critic. Modelled."""
import sys, os
sys.path.insert(0, 'climate')
from physics import *
sys.argv=['x']
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import critic_bt4_hybrid as C
Q=7.2; COP=1.8; AUX=0.65
e_per_t = Q/COP/3.6 + AUX  # MWh_e per gross t
print(f'Floor check: heat {Q} GJ/t > floor 0.465 GJ/t: {Q>0.465}')
print(f'Electricity per gross t (flat HP COP {COP}): {e_per_t:.2f} MWh_e')
GROSS=673.0
for ci in (0.316, 0.20, 0.10, 0.05, 0.02, 0.01):
    net = 1 - ci*e_per_t
    print(f'grid {ci:.3f} t/MWh: net removal {net:.2f} t/t -> ${GROSS/net:.0f}/net t; hybrid saving $10-12/gross t = ${10/net:.0f}-{12/net:.0f}/net t')
# carbon+price gated hybrid on DE-LU
hrs, p, ci, D, t_yr = C.hrs, C.p, C.ci, C.D, C.t_yr
for thr, cimax in ((20, 9), (20, 0.15), (20, 0.10), (0, 0.10)):
    cap=D*16; s=0; cost=0; co2=0; eb_mwh=0
    for t in hrs:
        need=D
        if p[t]<thr and ci[t]<cimax:
            eb=min(2*D, need+(cap-s)); take=min(eb,need); s+=(eb-take)*0.99; need-=take
            cost+=eb/0.99*p[t]; co2+=eb/0.99*ci[t]; eb_mwh+=eb
        else:
            d=min(s,need); s-=d; need-=d
        s*=(1-0.01/24)
        if need>0: cost+=need/COP*(p[t]+C.GRIDF); co2+=need/COP*ci[t]
    sc=8760/len(hrs)/t_yr
    capex=(D*1e3*C.HP_CAPEX+2*D*1e3*100+cap*3.6e3/(4.19*0.92*45)*400)*(C.CRF+C.OM)/t_yr
    tot=cost*sc*C.EUR+capex+C.hp_cap_chg
    print(f'gate p<{thr} EUR & ci<{cimax}: EB share {eb_mwh/(D*len(hrs)):.1%}, heat ${tot:.0f}/t, heat CO2 {co2*sc:.3f} t/t (flat HP 0.370, $170)')
