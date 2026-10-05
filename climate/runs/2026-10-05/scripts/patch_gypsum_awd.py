import sys; sys.path.insert(0,'climate')
from physics import *
MW_G=172.17; MW_CH4=16.04
g100=GWP100["CH4_biogenic"]; g20=GWP20["CH4_biogenic"]
def ch4_avoided(dose_t, eff, passes, cap_kg):
    mol=dose_t*1e6/MW_G
    kg=mol*eff*passes*MW_CH4/1000
    return min(kg,cap_kg), mol
print("Per-ha per-season CH4 avoided (kg), capped at 40% of AWD residual (55-150 kg)")
for dose in (0.15,0.75):
    for eff in (0.3,1.0):
        for passes in (1,3):
            for res in (55,150):
                kg,mol=ch4_avoided(dose,eff,passes,0.4*res)
                print(f" dose {dose} t ({mol:.0f} mol SO4, S {dose*1e6/MW_G*32.06/1000:.0f} kg) eff {eff} passes {passes} residual {res}: {kg:.1f} kg CH4 = {kg*g100/1000:.2f} tCO2e100 / {kg*g20/1000:.2f} tCO2e20")
# Re-scoped scale: ASSUMED areas (harvested, Mha) India 47, China 30, Bangladesh 11.5, Vietnam 7.2 (FAO-order, from memory)
area=47+30+11.5+7.2
irr=0.65   # assumed irrigated share
awd=(0.3,0.5)  # assumed AWD-feasible share of irrigated
donor=(0.1,0.3) # assumed donor-limited share (straw removed + low SOC) -- to be mapped
adopt=(0.1,0.3)
per_ha=(4.2,42)  # kg CH4/ha/season co-benefit range at agronomic dose from above (low eff 1 pass .. high eff 3 passes, capped)
lo=area*irr*awd[0]*donor[0]*adopt[0]*per_ha[0]*1e6/1000/1e6  # kt->Mt
hi=area*irr*awd[1]*donor[1]*adopt[1]*per_ha[1]*1e6/1000/1e6
print(f"Target area {area:.1f} Mha harvested; donor-limited AWD area {area*irr*awd[0]*donor[0]:.1f}-{area*irr*awd[1]*donor[1]:.1f} Mha")
print(f"Scale: {lo*1000:.2f}-{hi*1000:.1f} kt CH4/yr = {lo*g100:.3f}-{hi*g100:.2f} Mt CO2e100 ({lo*g20:.3f}-{hi*g20:.2f} GWP20)")
# Agronomic economics: 0.15 t gypsum at $15-40/t + $10/ha spreading
print(f"Agronomic dose cost ${0.15*15+10:.0f}-{0.15*40+10:.0f}/ha; yield value of 3.1% on 5 t/ha at $300/t = ${0.031*5*300:.0f}/ha")
