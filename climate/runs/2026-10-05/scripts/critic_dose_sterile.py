import sys
sys.path.insert(0, 'climate')
from physics import *
GWP = 273.0

print("=== 1. CELL MASS: paper measured vs TEA assumed ===")
m_paper = 0.108  # pg/cell, Hiis et al. Methods: 108 fg/cell +/- 7.5 s.e., n=9
m_tea   = 0.300  # pg/cell, TEA assumption
print(f"TEA overstates cell dry mass by {m_tea/m_paper:.1f}x")
VSS_paper = 6e9*m_paper*1e-12*1e3
print(f"biomass at 6e9 cells/mL = {VSS_paper:.3f} g/L (TEA used {6e9*m_tea*1e-12*1e3:.2f})")

# paper's measured aerobic yield: Y_O2 = 4e14 cells / mol O2
O2_mol_L = 6e12/4e14
O2_kg_m3 = O2_mol_L*32.0
print(f"O2 demand from paper's measured yield = {O2_kg_m3:.2f} kg O2/m3 "
      f"(TEA assumed 1.94 -> overstated {1.94/O2_kg_m3:.1f}x)")
for eff,mix in ((2.0,0.2),(1.5,0.4),(1.0,0.8)):
    print(f"   aeration {O2_kg_m3/eff:.2f} + mixing {mix} = {O2_kg_m3/eff+mix:.2f} kWh/m3")

print("\n=== 2. DOSE GAP: cells per m2, the quantity that actually acted ===")
dig_L_m2 = 0.480/0.043          # 480 mL per 0.043 m2 bucket
cells_m2 = dig_L_m2*1000*6e9
print(f"demonstrated: {dig_L_m2:.1f} L/m2 = {dig_L_m2*10:.0f} m3/ha at 6e9 cells/mL "
      f"-> {cells_m2:.2e} cells/m2 (paper states 6.6e13)")
dig_N = 1.71                     # kg NH4-N/m3 digestate (paper)
print(f"that dose carries {dig_L_m2*10*dig_N:.0f} kg NH4-N/ha, already above the "
      f"EU Nitrates Directive 170 kg N/ha manure ceiling")
for name,N in (("cattle",5.0),("mixed",3.5),("pig",3.0)):
    m3 = 170.0/N
    need = cells_m2/(m3*10*1000)
    print(f"  raw {name} slurry {N} kg N/m3 -> max {m3:.0f} m3/ha under the 170 kg N cap; "
          f"to match 6.6e13 cells/m2 needs {need:.2e} cells/mL = {need/6e9:.1f}x the density grown in sterile digestate")

print("\n=== 3. IF THE VECTOR MUST BE HEAT-TREATED (every reported result did) ===")
cp, rho, dT = 4.0, 1000.0, 60.0   # kJ/kg/K, kg/m3, 10->70 C
MJ_m3 = cp*rho*dT/1000.0
abate_t_m3 = 0.290/43.0           # TEA base net saving per m3 slurry
print(f"pasteurise raw slurry: {MJ_m3:.0f} MJ/m3 = {MJ_m3/3.6:.0f} kWh(th)/m3")
for rec in (0.0,0.5,0.8,0.9):
    net = MJ_m3*(1-rec)
    print(f"  {rec*100:.0f}% heat recovery -> {net:.0f} MJ/m3 = {net/1000/abate_t_m3:.1f} GJ/t CO2e"
          f"   (TEA claimed base 0.90; real DAC 5-10)")
print(f"  -> treating only a 2% side-stream at 50% recovery: "
      f"{MJ_m3*0.5*0.02/1000/abate_t_m3:.2f} GJ/t CO2e")

print("\n=== 4. Europe scale: authors' own slurry-specific scenario ===")
print("Hiis et al. Extended Data Table 3: 60% cut applied to ALL European liquid manure")
print("  -> total European anthropogenic N2O -2.7%; EU27 -4.0%.")
print("  The abstract's '5-20%' is a broader/per-country range, NOT the liquid-manure case")
print("  the idea targets. Idea + reports quoted 5-20% for the slurry case.")
