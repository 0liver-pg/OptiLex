import sys
sys.path.insert(0, 'climate')
from physics import *

GWP = 273.0  # N2O GWP100 (verifier)
try:
    print("verifier GWP100 N2O =", GWP100.get('N2O') if isinstance(GWP100, dict) else GWP100)
except Exception as e:
    print("gwp lookup note:", e)

# --- Electron-acceptor demand to grow Hiis-density inoculum BY N2O RESPIRATION ---
cell_mass_pg = 0.3                 # pg dry mass/cell (TEA assumption)
cells_per_mL = 6e9                 # Hiis et al. 2024 measured density
VSS = cells_per_mL * cell_mass_pg * 1e-12 * 1e3   # g VSS / L
print(f"\nbiomass target: {VSS:.2f} g VSS/L")

for Y in (0.25, 0.30, 0.40):        # g VSS / g COD consumed (anoxic heterotroph)
    cod_tot = VSS / Y
    cod_bio = VSS * 1.42            # COD stored in cells
    cod_cat = cod_tot - cod_bio     # COD oxidised -> electrons
    e_eq = cod_cat / 8.0            # 8 g COD per electron equivalent
    mol_n2o = e_eq / 2.0            # N2O + 2e- + 2H+ -> N2 + H2O
    kg_n2o_m3 = mol_n2o * 44.0      # g/L == kg/m3
    print(f"  Y={Y}: COD {cod_tot:.2f} g/L (cat {cod_cat:.2f}) -> "
          f"N2O {kg_n2o_m3:.2f} kg/m3 = {kg_n2o_m3*GWP/1000:.2f} t CO2e/m3 handled")

# --- compare with abatement delivered per m3 of slurry (TEA base case) ---
Y = 0.30
kg_n2o_m3 = ((VSS/Y - VSS*1.42)/8.0/2.0)*44.0
slurry_m3_per_ha = 43.0             # TEA base (pig/cattle mix, 3.5 kg N/m3)
abate_t_per_ha = 0.290              # TEA base NET saving after NH3 debit
abate_t_per_m3 = abate_t_per_ha / slurry_m3_per_ha
handled_t_per_m3 = kg_n2o_m3*GWP/1000
print(f"\nabated      : {abate_t_per_m3*1000:.2f} kg CO2e / m3 slurry")
print(f"N2O handled : {handled_t_per_m3*1000:.0f} kg CO2e / m3 slurry")
print(f"ratio handled/abated = {handled_t_per_m3/abate_t_per_m3:.0f}x")
print(f"max tolerable N2O loss from the reactor = {100/(handled_t_per_m3/abate_t_per_m3):.3f}% of supply")
print(f"per hectare: {kg_n2o_m3*slurry_m3_per_ha:.0f} kg N2O routed through the vessel "
      f"({kg_n2o_m3*slurry_m3_per_ha*GWP/1000:.0f} t CO2e) to abate {abate_t_per_ha:.2f} t CO2e")

# --- cost of that N2O as a purchased gas, vs whole TEA system cost ---
for p in (0.5, 1.0, 3.0):           # $/kg N2O, bulk industrial/medical
    print(f"  N2O at ${p}/kg -> ${p*kg_n2o_m3:.2f}/m3 slurry "
          f"= ${p*kg_n2o_m3/abate_t_per_m3:,.0f}/t CO2e  (TEA whole system: $0.74-4.76/m3)")

# --- dose-response leverage: cost scales linearly with target cell density ---
print("\nif a lower cell dose works (N2O demand is linear in cells):")
for cpm in (6e9, 1e9, 1e8, 1e7):
    v = cpm*cell_mass_pg*1e-12*1e3
    kg = ((v/Y - v*1.42)/8.0/2.0)*44.0
    print(f"  {cpm:.0e} cells/mL -> {kg:.3f} kg N2O/m3, ${1.0*kg:.2f}/m3 at $1/kg")

# --- soluble-COD feasibility of growing to 6e9 in slurry at all ---
print("\nCOD check: need %.1f g COD/L consumed; soluble COD of raw cattle/pig slurry"
      " is ~10-25 g/L (total 40-120 g/L, mostly particulate)." % (VSS/Y))

# --- campaign duty cycle: spreading windows are weeks, not a year ---
print("\nduty cycle: TEA sizes tanks on ANNUAL throughput.")
for ann in (4000, 7000, 12000):
    for window_d, batch_d in ((21, 4),):
        cycles = window_d/batch_d
        print(f"  {ann} m3/yr spread in a {window_d}-day window, {batch_d}-day batch "
              f"-> {cycles:.1f} cycles -> working volume {ann/cycles:,.0f} m3 "
              f"(not the ~50-100 m3 implied by $30-70k)")
