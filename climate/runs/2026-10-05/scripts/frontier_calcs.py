import sys, math
sys.path.insert(0, 'climate')
from physics import *
F=96485.0; KWH=0.0036
floor75=gj_per_tonne(min_separation_work(420e-6,0.75)); floor80=gj_per_tonne(min_separation_work(420e-6,0.80))
floor_flue=gj_per_tonne(min_separation_work(0.12,0.90))
print(f"Floors: air75 {floor75:.3f}, air80 {floor80:.3f}, coal flue 90% {floor_flue:.3f} GJ/t")
print("\n== 1. Measured/claimed capture energies vs floor (energy basis, electricity is pure exergy) ==")
rows=[("Aziz/Gordon phenazine hybrid flow cell DAC, lab 2025 (104 kJ/mol, electricity)",gj_per_tonne(104e3),floor75,"lab_measured"),
      ("same cell, simulated flue gas (73 kJ/mol)",gj_per_tonne(73e3),floor_flue,"lab_measured"),
      ("MnO2 surface mineralization DAC, Nature Energy 2026, 4.1 GJ/t, 80% single pass",4.1,floor80,"lab_measured, 20 cm2"),
      ("Kanan Ca/Mg exchange 'less than 1 MWh/t' (modelled)",3.6,floor75,"modelled"),
      ("Liquid-carbonate DAC per MnO2 paper 6-10 GJ/t (low end)",6.0,floor75,"literature"),
      ("Mammoth CEO 5000-6000 kWh/t (2025, early operation)",5500*KWH,floor75,"company statement")]
for n,e,f,ev in rows:
    print(f"  {n}: {e:.2f} GJ/t -> {e/KWH:,.0f} kWh/t; eta_II={f/e:.1%}; x floor={e/f:.1f} [{ev}]")
for n,e in [("phenazine 2.36 GJ/t",gj_per_tonne(104e3)),("MnO2 4.1 GJ/t",4.1)]:
    twh=e*1e9/3.6/1e3  # GJ per Gt -> TWh: e GJ/t *1e9 t = e*1e9 GJ ; 1 TWh = 3.6e6 GJ
    twh=e*1e9/3.6e6
    print(f"  1 Gt/yr at {n}: {twh:,.0f} TWh = {twh/WORLD_ELECTRICITY_TWH:.1%} of world electricity (stack energy only; excludes fans, compression)")
print("\n== 2. Mammoth realized vs nameplate (Heimildin May 2025 citing Puro.earth) ==")
name=36000; got=105; months=10
print(f"  pro-rated nameplate {name*months/12:,.0f} t; realized {got} t = {got/(name*months/12):.2%} (confound: partially commissioned)")
print(f"  Climeworks lifetime capture ~2,400 t vs own 2023 footprint 1,700 t; cited run-rate 860 t/yr -> Morgan Stanley 40,000 t would take {40000/860:.0f} yr")
print("\n== 3. Durable CDR market delivery ratio (CDR.fyi homepage, Oct 2026) ==")
print(f"  delivered/contracted = 1.7/50.5 = {1.7/50.5:.1%}; contracted is {50.5e6/37.4e9:.2%} of one year of fossil CO2 (37.4 Gt)")
print(f"  WEF (data to Aug 2024): DAC sold <1.5 Mt vs delivered >2,000 t (750:1); biochar 4:1; ERW 200:1")
print("\n== 4. Enhanced weathering measured rates -> land per Gt/yr ==")
crop_ha=1.56e9
for n,r in [("Swiss vineyards 2025, 20 t/ha basalt, measured+model 0.10 t/ha/yr",0.10),("Scotland 2025, 78-126 t/ha, 0.33-0.53 t/ha over 1.5 yr -> ~0.29 t/ha/yr mid",0.29),("upper modelled/experimental rates ~1-3 t/ha/yr",2.0)]:
    ha=1e9/r; print(f"  {n}: {ha/1e9:.2f} Gha per Gt/yr = {ha/crop_ha:.1f}x global cropland (~1.56 Gha)")
print("\n== 5. CO2 electroreduction to ethylene energy (In/Cu, 20 bar, 85% FE, Nat Catal 2025) ==")
M=28.05e-3; dG=1331e3  # 2CO2+2H2O->C2H4+3O2, deltaG ~ +1331 kJ/mol (std)
Emin=dG/(12*F); print(f"  equilibrium cell voltage {Emin:.2f} V; thermodynamic min {dG/M/1e6:.1f} GJ/t C2H4")
for V in (2.5,3.0,3.5):  # ASSUMED cell voltages (not reported in abstract)
    e=12*F*V/0.85/M/1e6  # GJ/t
    mwh=e/3.6
    print(f"  assumed V={V}: {e:.0f} GJ/t = {mwh:.0f} MWh/t C2H4; elec cost at $30/MWh = ${mwh*30:,.0f}/t; CO2 fed 3.14 t/t; grid break-even vs ~1.5 tCO2/t cracker process emissions = {1.5/mwh*1000:.0f} gCO2/kWh")
print("\n== 6. SOEC CO2->CO (Nature 2025, 90% energy efficiency, 2,000 h at 1 A/cm2, 800C) ==")
e=283e3/0.90; print(f"  ~{gj_per_tonne(e):.1f} GJ per t CO2 converted ({gj_per_tonne(e)/3.6:.2f} MWh/t CO2); per t CO: {e/28.01e-3/1e6:.1f} GJ")
print("\n== 7. Sorbent productivity: COF-1000 outdoor 22.1 mmol/g/day (Nat Sustain 2026) ==")
molpt=1e6/44.01; prod=22.1e-3*365
print(f"  {prod:.2f} mol/g/yr -> {molpt/prod/1e3:.2f} kg sorbent per (t CO2/yr); 1 Mt/yr plant -> {molpt/prod*1e6/1e6:,.0f} t sorbent if lab cycling holds")
