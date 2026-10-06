import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

floor = gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99))
print(f"floor 75%/99%: {floor:.3f} GJ/t")
comp = gj_per_tonne(R*T0*math.log(150))  # ideal isothermal 0.1 -> 15 MPa
print(f"ideal compression 0.1->15 MPa: {comp:.3f} GJ/t ; floor incl compression {floor+comp:.3f}")

kWh = 3.6e-3  # GJ
print("\n--- 1. KOH/Ca loop (Keith 2018 design) ---")
dH_calc = 178.3e3
print(f"CaCO3->CaO+CO2 dH: {gj_per_tonne(dH_calc):.2f} GJ/t")
carnot900 = 1 - T0/1173.15
print(f"Carnot factor at 900C: {carnot900:.3f}; exergy of calcination heat alone: {gj_per_tonne(dH_calc)*carnot900:.2f} GJ/t "
      f"-> chemistry-capped 2nd-law eff {floor/(gj_per_tonne(dH_calc)*carnot900):.1%}")
for name, gas, el in [("A all-gas 15MPa", 8.81, 0), ("C gas+elec 15MPa", 5.25, 366), ("D gas+elec 0.1MPa", 5.25, 77)]:
    for eta in (0.45, 0.60):
        w = gas*eta + el*kWh
        tgt = floor + (comp if '15MPa' in name else 0)
        print(f"  {name}: gas {gas} GJ + {el} kWh; work-eq (gas->work at {eta:.0%}) {w:.2f} GJ/t; 2nd-law eff {tgt/w:.1%}")
    print(f"    primary energy total {gas+el*kWh:.2f} GJ/t (elec counted 1:1)")
print(f"calciner design 5.25 GJ/t vs dH 4.05 => thermal eff {4.05/5.25:.0%}")

print("\n--- 2. Contactor kinetics ---")
c_co2 = P_CO2_AIR/(R*293.15)
KL = 1.3e-3
flux = KL*c_co2
print(f"gas CO2 conc at 20C: {c_co2:.4f} mol/m3; flux at KL=1.3 mm/s (inlet, upper bound): {flux:.2e} mol/m2/s = {flux*M_CO2*3.156e7:.1f} kg CO2/m2/yr")
# log-mean driving force for 74.5% capture
lm = (1-0.255)/math.log(1/0.255)
print(f"log-mean factor for 74.5% capture: {lm:.3f} -> {flux*lm*M_CO2*3.156e7:.1f} kg/m2/yr; wetted area for 1 Mt/yr: {1e9/(flux*lm*M_CO2*3.156e7):.2e} m2; packing vol at 210 m2/m3: {1e9/(flux*lm*M_CO2*3.156e7)/210:.2e} m3")
v_air = air_volume_per_tonne(X_AIR, 0.745)
print(f"air per tonne at 74.5% capture: {v_air:.3e} m3")
print(f"fan work at 9.7 Pa/m*7m=68 Pa, 70% eff: {fan_work_gj_per_tonne(X_AIR,0.745,68,0.70)/kWh:.0f} kWh/t (Keith reports 61)")

print("\n--- 3. Solvent volatility ceiling for open air contact ---")
for cap, label in [(0.745, 'KOH-style 74.5%'), (0.5, 'Kiani MEA 50%')]:
    v = air_volume_per_tonne(X_AIR, cap)
    for loss_kg in (0.28, 2.0, 53.4):
        MW = 0.061 if 'MEA' in label else 0.150
        mol_m3 = loss_kg/MW/v
        p = mol_m3*R*T0
        print(f"  {label}: loss {loss_kg} kg/t (MW {MW*1e3:.0f}) <-> exhaust vapour {p:.4f} Pa = {p/133.32:.2e} Torr = {p/P0*1e6:.3f} ppmv")
# allowed vapour pressure for $10/t make-up at $5/kg, MW 150, saturated exhaust
v = air_volume_per_tonne(X_AIR, 0.745)
for price in (2, 5, 20):
    kg = 10/price
    p = kg/0.150/v*R*T0
    print(f"  $10/t make-up budget at ${price}/kg, MW150: max {kg:.2f} kg/t -> vapour pressure <= {p:.4f} Pa ({p/133.32:.1e} Torr)")
print(f"  PNNL benchmark 'order of magnitude below 3 Torr at 80C' ~0.3 Torr = {0.3*133.32:.0f} Pa")

print("\n--- 4. Water loss ---")
w = 4.7  # t water / t CO2, Keith 2018 at 20C 64% RH
print(f"4.7 t H2O/t CO2 = {4.7e6/18.015/(1e6/44.01):.1f} mol H2O/mol CO2; latent heat taken from air {gj_per_tonne(moisture_swing_water_heat(4.7e6/18.015/(1e6/44.01))):.1f} GJ/t")
print(f"  1 Mt/yr plant: {4.7:.1f} Mt water/yr = {4.7e6/365:.0f} m3/day")

print("\n--- 5. pH-swing / electrochemical regeneration floors ---")
V_w = R*T0*math.log(10)*14/FARADAY
print(f"water-splitting voltage across dpH=14: {V_w:.3f} V -> {electrochemical_work(1,V_w)/1e3:.1f} kJ per mol H+")
for n,label in [(2,'carbonate feed (2 H+/CO2)'),(1,'bicarbonate feed (1 H+/CO2)')]:
    e = electrochemical_work(n, V_w)
    print(f"  {label}: {e/1e3:.0f} kJ/mol = {gj_per_tonne(e):.2f} GJ/t = {gj_per_tonne(e)/kWh:.0f} kWh/t; 2nd-law eff {floor/gj_per_tonne(e):.0%}")
for dpH in (6, 8, 10):
    V = R*T0*math.log(10)*dpH/FARADAY
    e = electrochemical_work(1, V)
    print(f"  mild swing dpH={dpH}, 1 e-/CO2: {V:.2f} V, {e/1e3:.0f} kJ/mol = {gj_per_tonne(e):.2f} GJ/t")
meas = {
 "Shu 2020 H2-recycling, NaOH/Na2CO3, 5 mA/cm2 (lab)": 374e3,
 "Sabatino 2020 KOH+BPMED base case (simulation)": 24e9*M_CO2/1e3*1e3/1e3,  # 24 MJ/kg
 "Zhu 2023 solid-electrolyte reactor, lowest (lab, low j)": 150e3,
 "Jin 2022 DSPZ pH swing, extrapolated to 0.4 mbar, low": 121e3,
 "Jin 2022 DSPZ extrapolated, high": 237e3,
}
for k,v in meas.items():
    print(f"  {k}: {v/1e3:.0f} kJ/mol = {gj_per_tonne(v):.2f} GJ/t(e) = {gj_per_tonne(v)/kWh:.0f} kWh/t; 2nd-law {floor/gj_per_tonne(v):.1%}")
for k,mwh in {"Mission Zero pilot design (2022 report)":2.18,"Mission Zero claim":0.8,"Phlair target":1.5,"Captura DOC stated":1.8,"Equatic stated low":2.0,"Equatic stated":2.5}.items():
    print(f"  {k}: {mwh} MWh/t = {mwh*3.6:.2f} GJ/t(e) = {mwh*3.6e9*M_CO2/1e3/1e3:.0f} kJ/mol; 2nd-law {floor/(mwh*3.6):.1%}")

print("\n--- 6. BIG crystallisation regeneration ---")
for name, e in [("m-BBIG 360 kJ/mol", 360e3), ("MGBIG 7.0 GJ/t", 7.0*M_CO2*1e6*1e3/1e3)]:
    print(f"  {name}: {e/1e3:.0f} kJ/mol = {gj_per_tonne(e):.2f} GJ/t")
# hydration-water budget: E = dH_CO2 + n*(dH_w) + sensible
for dH_co2 in (60e3, 80e3):
    for dH_w in (44e3, 55e3):
        for sens in (30e3, 60e3):
            n = (360e3 - dH_co2 - sens)/dH_w
            print(f"    if CO2 release {dH_co2/1e3:.0f}, water {dH_w/1e3:.0f}/mol, sensible {sens/1e3:.0f}: implied water released {n:.1f} mol/mol CO2")
for n in (0, 1, 2, 4):
    e = 75e3 + n*50e3 + 40e3
    print(f"    hypothetical crystal releasing {n} H2O per CO2: {e/1e3:.0f} kJ/mol = {gj_per_tonne(e):.2f} GJ/t")
print(f"  K-sarcosinate direct thermal (ORNL DSC): 1.5 + 3.68 = {1.5+3.68:.2f} GJ/t ; desorption enthalpy {3.68*M_CO2*1e3:.0f} kJ/mol")

print("\n--- 7. Ca(OH)2 passive looping (Heirloom-type) ---")
cap = 1/0.05608  # mol CO2/kg CaO
print(f"stoichiometric capacity {cap:.1f} mol CO2/kg CaO; at 85% conversion {0.85*cap:.1f} mol/kg ({0.85*cap*M_CO2:.2f} kg/kg)")
cp_caco3 = 110.0  # J/mol/K mean 25-900C (approx)
sens = cp_caco3*875
dehyd = 109e3  # Ca(OH)2 -> CaO + H2O(g)
for X in (0.85, 0.6):
    e = dH_calc + sens + (1-X)/X*(dehyd + 100*875*0.9)  # unconverted hydroxide dehydrated and heated
    print(f"  conversion {X:.0%}: calcination {dH_calc/1e3:.0f} + sensible {sens/1e3:.0f} + unconverted-hydroxide penalty {(1-X)/X*(dehyd+100*875*0.9)/1e3:.0f} kJ/mol = {e/1e3:.0f} kJ/mol = {gj_per_tonne(e):.2f} GJ/t = {gj_per_tonne(e)/kWh:.0f} kWh/t (no heat recovery)")
cycles_per_year = 365/3
print(f"  3-day cycle: {cycles_per_year:.0f} cycles/yr; CaO inventory per (t CO2/yr): {1000/(0.85*cap*M_CO2*cycles_per_year):.1f} kg; productivity {productivity(0.85*cap, 1/3):.3f} kg CO2/kg CaO/day")
print(f"  sorbent cost at $0.15/kg CaO, 0.85*17.8 mol/kg, 10 cycles before purge: ${sorbent_cost_per_tonne(0.15, 0.85*cap, 10):.2f}/t")
# tray area: 2 t CO2/ha/day (lime-layer field data)
print(f"  at 2 t CO2/ha/day per layer: 1 Mt/yr needs {1e6/(2*365):.0f} ha of exposed layer area (stacked trays divide land footprint)")

print("\n--- 8. Reference comparisons ---")
ref = reference_amine_cycle()
print(f"solid amine reference heat {ref.heat_gj_per_t if hasattr(ref,'heat_gj_per_t') else 'n/a'}")
print(f"Kiani 2020 MEA-DAC (sim): 10.7 GJ/t heat + 1.452 MWh = {1.452*3.6:.2f} GJ/t(e)")
print(f"An 2022 KOH climate sensitivity: 8.3-11.1 GJ/t -> ratio to floor {8.3/floor:.0f}x-{11.1/floor:.0f}x")
