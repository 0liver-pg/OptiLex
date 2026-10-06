import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
floor = gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99))
print(f"floor GJ/t {floor:.3f}; as 1e- voltage {min_separation_work(X_AIR,0.75,0.99)/FARADAY*1000:.0f} mV")
# 1. reported energies -> GJ/t, kWh/t, second-law eff, $ at 50 $/MWh
rep = {
 "Jin/Aziz 2025 phenazine hybrid flow, DAC (cell only)":104,
 "Hemmatifar 2022 PVAQ ESA 400ppm in N2 (elec+pneumatic)":113,
 "Seo/Hatton 2023 neutral red, air (CV-estimated min work)":65,
 "Sabatino 2020 KOH+BPMED (model)":236,
 "BMED 2025 TA paper @1000 A/m2":290.61,
 "BMED 2025 TA paper @100 A/m2":161.2,
 "pH-swing Nernst bound 0.83 V x 2e (Liu 2026 text)":2*FARADAY*0.83/1000,
}
for k,v in rep.items():
    g=gj_per_tonne(v*1000)
    print(f"{k:60s} {v:6.1f} kJ/mol = {g:5.2f} GJ/t = {g/3.6*1000:5.0f} kWh/t; 2nd-law {floor/g*100:4.1f}% ; ${energy_cost_floor(g,50):.0f}/t @50$/MWh")
for name,g in [("Liu/Sargent 2026 MnO2 DAC optimised (cell only)",3.9),("Liu/Sargent released into pure CO2",4.1),("  + 1-2 GJ/t vacuum/compression (their note), mid",4.1+1.5),
               ("Mission Zero claim <800 kWh/t",0.8*3.6),("RepAir claim 600 kWh/t",0.6*3.6),("Verdox claim 1.5 GJ/t",1.5),("OptiLex ref TVSA work-equivalent",1.88)]:
    print(f"{name:60s} {g*44.01:6.1f} kJ/mol = {g:5.2f} GJ/t = {g/3.6*1000:5.0f} kWh/t; 2nd-law {floor/g*100:4.1f}% ; ${energy_cost_floor(g,50):.0f}/t @50$/MWh")
# check electrochemical_work helper
print("check 1e-,1.0V,FE 1:", gj_per_tonne(electrochemical_work(1,1.0)), "GJ/t")
print("Liu MnO2: 3.9 GJ/t = %.0f kJ/mol; at ~1 V mean cell voltage implies ~%.1f e- per CO2 (CE ~%.0f%%)"%(3.9*44.01, 3.9*44.01e3/FARADAY, 100*FARADAY/(3.9*44.01e3)))
# 2. areal productivity: t CO2 per m2 cell per year vs current density & electrons(incl. FE) per CO2, duty
def areal(j_mA_cm2, e_per_co2_eff, duty=0.5, util=0.9):
    j=j_mA_cm2*10.0 # A/m2
    mol_s = j/FARADAY/e_per_co2_eff
    return mol_s*M_CO2*3600*8760*duty*util/1000.0  # t/m2/yr (M_CO2 in kg/mol)
print("\nareal productivity t/m2/yr (duty 0.5 for swing cells =capture half, release half; util 0.9)")
for j in (0.5,1,5,10,50,100):
    row=[areal(j,n) for n in (1,2,4)]
    print(f" j={j:5.1f} mA/cm2: 1e-:{row[0]:7.3f}  2e-:{row[1]:7.3f}  4e-(e.g. FE 25%):{row[2]:7.3f}")
# 3. cell capex $/t: installed cell cost per m2, CRF
def crf(r,n): return r*(1+r)**n/((1+r)**n-1)
print(f"\ncell capital charge $/t (CRF 7pct/10y={crf(0.07,10):.3f})")
for cost in (100,300,1000):
    for j,n,duty in ((1,4,0.5),(1,1,0.5),(10,1,0.5),(100,2,1.0),(300,2,1.0)):
        a=areal(j,n,duty)
        print(f"  ${cost}/m2, j={j} mA/cm2, {n} e-/CO2, duty {duty}: {a:7.3f} t/m2/yr -> ${cost*crf(0.07,10)/a:8.0f}/t")
# 4. Liu/Sargent measured areal productivity
mol=15.2e-6; area=5e-4; tc=1.4
a_meas=mol*M_CO2/area/tc*8760/1000
print(f"\nLiu 2026 measured: {a_meas*1000:.1f} kg CO2/m2/yr (5 cm2, 15.2 umol/cycle, 1.4 h) -> m2 per t/yr = {1/a_meas:.0f}")
mol=1230e-6; area=20e-4; 
for tc in (1.4,1.7):
    a=mol*M_CO2/area/tc*8760/1000
    print(f"Liu high-loading 20 cm2 1230 umol/cycle, tc={tc} h (assumed): {a*1000:.0f} kg/m2/yr -> {1/a:.1f} m2 per t/yr; $/m2 allowed for $50/t cell charge: {50*a/crf(0.07,10):.0f}")
# 5. O2 competition: flux ratio O2/CO2 in air; parasitic if fraction f of O2 reaching electrode is reduced
print("\nO2:CO2 molar ratio in air:", 0.2095/X_AIR)
# 6. energy cost comparison heat vs electricity: TVSA 6.04 GJ/t heat at $5-10/GJ vs electro 100 kJ/mol
for kj in (65,104,113,160,236):
    g=gj_per_tonne(kj*1000)
    print(f"{kj} kJ/mol: {g:.2f} GJ/t -> ${energy_cost_floor(g,30):.0f}/t @30, ${energy_cost_floor(g,60):.0f}/t @60 $/MWh")
print("TVSA ref: heat 6.04 GJ/t at $4/GJ = $%.0f/t; via heat pump COP 3 at $50/MWh = $%.0f/t"%(6.04*4, energy_cost_floor(6.04/3,50)))
# 7. lifetime: electrode replacement cost. capacity per m2 & cycles
# sorbent-equivalent: MnO2 0.42 mmol/g, 1000 h/1.4 h = 714 cycles demonstrated
print("\nsorbent cost $/t at 0.42 mol/kg:")
for price in (5,20):
    for cyc in (714,5000,50000):
        print(f"  ${price}/kg, {cyc} cycles: ${sorbent_cost_per_tonne(price,0.42,cyc):.0f}/t")
