import sys
sys.path.insert(0, 'climate')
from physics import *

GWP_N2O = 273.0
M_N2O, M_N = 44.013, 28.014

def per_ha_abatement(N_kg_ha, EF, cut):
    n2o_n = N_kg_ha*EF
    n2o = n2o_n*M_N2O/M_N
    co2e_t = n2o*GWP_N2O/1000.0
    return co2e_t, co2e_t*cut

print("=== 1. per-hectare baseline & abatement (GWP100 N2O=273) ===")
for N in (150,):
    for EF in (0.005, 0.01, 0.016):
        base,_ = per_ha_abatement(N, EF, 0)
        print(f"  N={N} kg/ha EF={EF*100:.1f}%  base={base:.3f} tCO2e/ha", end="  ")
        for cut in (0.0, 0.3, 0.6):
            _,ab = per_ha_abatement(N,EF,cut)
            print(f"cut{int(cut*100)}%={ab:.3f}", end=" ")
        print()

print("\n=== 2. N-cap-limited slurry rate (EU Nitrates 170 kg manure-N/ha) ===")
for Nslurry in (3.0,4.0,5.0):
    print(f"  slurry {Nslurry} kg N/m3 -> {170/Nslurry:.1f} m3/ha")

print("\n=== 3. demonstrated cell loading, re-expressed ===")
dose_m2 = 6.6e13            # cells/m2 (critic: 480 mL of 6e9/mL on 0.043 m2)
chk = 0.480*1000*6e9/0.043
print(f"  check: 480 mL x 6e9/mL / 0.043 m2 = {chk:.2e} cells/m2 (critic 6.6e13)")
dose_ha = dose_m2*1e4
m_cell = 108e-15            # g dry per cell (paper, 108 fg)
print(f"  dose = {dose_ha:.2e} cells/ha = {dose_ha*m_cell/1000:.1f} kg dry biomass/ha")
print("  broth volume needed per ha at various titres:")
for titre in (6e9, 2e10, 1e11, 5e11, 1e12):
    vol_m3 = dose_ha/(titre*1e6)
    print(f"    {titre:.0e} cells/mL -> {vol_m3:8.2f} m3/ha")

print("\n=== 4. in-slurry route: what titre the N cap demands ===")
for Nslurry in (3.0,5.0):
    v = 170/Nslurry
    print(f"  {v:.0f} m3/ha -> need {dose_ha/(v*1e6):.2e} cells/mL  "
          f"({dose_ha/(v*1e6)/6e9:.1f}x the 6e9 achieved in sterile digestate)")
print("  conversely, at 6e9 cells/mL the N cap allows only:")
for Nslurry in (3.0,4.0,5.0):
    v=170/Nslurry
    print(f"    {v:.0f} m3/ha x 6e9 = {v*1e6*6e9:.2e} cells/ha = {v*1e6*6e9/dose_ha*100:.0f}% of demonstrated dose")

print("\n=== 5. side-stream fraction feasibility (decoupled inoculum) ===")
load = 170/4.0   # m3/ha of slurry at 4 kg N/m3
print(f"  field load {load:.1f} m3/ha")
for frac in (0.01,0.02,0.05,0.10):
    v = load*frac
    print(f"  side-stream {frac*100:4.1f}% = {v:.2f} m3/ha -> titre needed {dose_ha/(v*1e6):.2e} cells/mL")

print("\n=== 6. heat treatment energy, GJ per t CO2e abated ===")
cp, rho, dT = 4.0, 1000.0, 60.0     # kJ/kg.K, kg/m3, 10->70 C
E_m3 = cp*rho*dT/1000.0             # MJ/m3
print(f"  sensible heat 10->70 C = {E_m3:.0f} MJ/m3")
ab = per_ha_abatement(150,0.01,0.40)[1]   # t CO2e/ha at EF1%, 40% cut
print(f"  reference abatement {ab:.3f} t CO2e/ha (EF 1%, 40% cut)")
for frac,label in ((1.0,'whole load'),(0.05,'5% side-stream'),(0.02,'2% side-stream')):
    for rec in (0.0,0.5,0.8):
        gj_ha = E_m3*load*frac*(1-rec)/1000.0
        print(f"    {label:16s} recovery {int(rec*100):2d}% -> {gj_ha:6.3f} GJ/ha = {gj_ha/ab:7.2f} GJ/t CO2e")

print("\n=== 7. aeration O2 and energy (paper yield 4e14 cells/mol O2) ===")
Y = 4e14
for titre in (6e9,1e11):
    molO2 = titre*1e6/Y       # mol O2 per m3 broth
    kgO2 = molO2*0.032
    print(f"  titre {titre:.0e}/mL -> {molO2:.1f} mol O2/m3 = {kgO2:.2f} kg O2/m3", end="  ")
    print("energy " + ", ".join(f"{kgO2/oe:.2f} kWh/m3 @{oe} kgO2/kWh" for oe in (0.5,1.0,2.0)))
print("  (TEA had assumed 1.94 kg O2/m3 -> overstated ~4x at 6e9/mL)")

print("\n=== 8. concentration step (disc-stack centrifuge 1-4 kWh/m3 feed) ===")
feed = dose_ha/(6e9*1e6)   # m3 of 6e9/mL broth per ha
print(f"  feed to concentrate = {feed:.1f} m3/ha")
for e in (1,2,4):
    gj = feed*e*3.6/1000.0
    print(f"    {e} kWh/m3 -> {feed*e:.0f} kWh/ha = {gj:.3f} GJ/ha = {gj/ab:.2f} GJ/t CO2e")
print("  same, if minimum effective dose is 10x / 100x lower:")
for div in (10,100):
    f2 = feed/div
    for e in (2,):
        gj=f2*e*3.6/1000
        print(f"    dose/{div}: feed {f2:.2f} m3/ha, {e} kWh/m3 -> {gj:.4f} GJ/ha = {gj/ab:.3f} GJ/t CO2e")

print("\n=== 9. vessel duty cycle (contractor, 3-week campaign, 48 h batches) ===")
for ha in (500,2000):
    cells = ha*dose_ha
    for titre,lab in ((6e9,'6e9/mL'),(1e11,'1e11/mL concentrate')):
        total = cells/(titre*1e6)         # m3 broth for season
        batches = 21/2.0                  # 48 h batches in 3 weeks
        print(f"  {ha} ha, {lab}: {total:,.0f} m3 broth/season -> working volume {total/batches:,.1f} m3")
    print(f"  {ha} ha, dose/100 at 1e11/mL: working volume {ha*dose_ha/100/(1e11*1e6)/10.5:,.2f} m3")

print("\n=== 10. cost per t CO2e, explicit build-up ===")
for cost_ha in (10,30,60,150):
    for EF,cut in ((0.005,0.3),(0.01,0.4),(0.016,0.6)):
        a = per_ha_abatement(150,EF,cut)[1]
        print(f"  ${cost_ha:3d}/ha, EF {EF*100:.1f}%, cut {int(cut*100)}% -> ${cost_ha/a:7.0f}/t CO2e", end="")
    print()

print("\n=== 11. global reach, slurry-specific ===")
# authors' own liquid-manure scenario anchor; plus bottom-up
print("  bottom-up: global direct soil N2O 0.48-0.72 Gt CO2e/yr (task verifier)")
for share,adopt,cut in ((0.25,0.2,0.3),(0.35,0.4,0.5)):
    for base in (0.48,0.72):
        print(f"    slurry-spread share {share:.0%} x adoption {adopt:.0%} x cut {cut:.0%} on {base} Gt -> {base*share*adopt*cut*1000:.1f} Mt CO2e/yr")
