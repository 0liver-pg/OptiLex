"""Patch of idea 5: hood the turbulence that already exists (draft-tube outlet / tailrace boil /
stilling basin) at OLD persistently emitting reservoirs. Zero added head base case, <=1 m cap.
Net abatement = captured * (1 - f_ox)."""
import sys
sys.path.insert(0,'climate')
from physics import *
GWP=27.0; rho_ch4=0.668  # kg/m3 at ~20C,1 atm (approx)
def crf(r,n): return r*(1+r)**n/((1+r)**n-1)
Q=600; H=22.0  # Balbina-like (critic's figures, head from memory - unverified)
price=60.0     # $/MWh
y_target=0.01  # sweep CH4 vol fraction (20% LEL), well above ~0.2% RTO autothermal
dp_hood=500; eta_fan=0.6
rows=[]
print("c mg/L | months | phi(hooded share) | dh m | f_ox | net Mt CO2e/yr | sweep m3/s | lost+fan MW | energy $/t | capex $M | capex $/t | total $/t")
for c in (0.5,1.0,2.0):
  for months in (6,12):
    for phi in (0.15,0.3,0.5):
      for dh in (0.0,1.0):
        for fox in (0.0,0.4):
          frac_yr=months/12
          ch4_kg_s=Q*c/1000*phi            # CH4 degassing in hooded zone, captured ~all of it
          t_ch4=ch4_kg_s*3.1536e7*frac_yr/1000
          net=t_ch4*GWP*(1-fox)
          G=ch4_kg_s/rho_ch4/y_target       # m3/s sweep air
          fan_MW=G*dp_hood/eta_fan/1e6
          head_MW=rho_ch4 and 1000*9.81*Q*dh*0.9/1e6
          E=(fan_MW+head_MW)*8760*frac_yr
          e_cost=E*price/net if net else 0
          n_rto=max(G/100,0.5)
          capex=n_rto*9.5e6*1.08 + 15e6     # RTO (MATEC unit cost) + hood/ducting (assumed $15M)
          capex_t=capex*crf(0.08,20)/net
          tot=e_cost+capex_t
          rows.append((c,months,phi,dh,fox,net,tot))
          if (phi in (0.15,0.5)) or (c==1.0 and phi==0.3):
            print(f"{c:4} | {months:2} | {phi:.2f} | {dh:.0f} | {fox:.1f} | {net/1e6:.3f} | {G:5.0f} | {fan_MW+head_MW:5.2f} | {e_cost:5.1f} | {capex/1e6:4.0f} | {capex_t:5.1f} | {tot:5.1f}")
print(f"\n1 m of head = {1/H*100:.1f}% of output at H={H} m")
ok=[r for r in rows if r[5]>=0.1e6 and r[6]<30]
print(f"cases meeting kill-screen (net>=0.1 Mt/yr, <$30/t): {len(ok)} of {len(rows)}")
for r in ok:
    if r[3]==0 and r[4]==0.4: print("  pass (dh0,fox0.4):",r[:5],f"net {r[5]/1e6:.2f}Mt ${r[6]:.0f}/t")
# minimum concentration-share product for screen at months=6, fox=0.4, dh=0
for months in (6,12):
  for target in (0.1e6,):
    cphi=target/(GWP*0.6*Q/1000*3.1536e7*months/12/1000)
    print(f"months {months}: need c*phi >= {cphi:.3f} mg/L (Q=600) for net 0.1 Mt CO2e/yr at f_ox 0.4")
