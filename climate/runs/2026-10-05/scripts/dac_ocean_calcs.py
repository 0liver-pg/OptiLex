import sys, math
sys.path.insert(0, 'climate')
from physics import *

KWH = 0.0036  # GJ
floor_air = gj_per_tonne(min_separation_work(420e-6, 0.75))
comp_min = gj_per_tonne(R*T0*math.log(150))          # isothermal 1 -> 150 bar, ideal gas
comp_min_25 = gj_per_tonne(R*T0*math.log(25))
print(f"Air floor 75% capture: {floor_air:.3f} GJ/t; isothermal compression 1->150 bar: {comp_min:.3f} GJ/t; 1->25 bar: {comp_min_25:.3f}")

def carnot(TC): return 1 - T0/(TC+273.15)

print("\n== 1. Energy-basis vs exergy-basis second-law efficiency ==")
cases = [
 # name, heat GJ/t, heat temp C, elec GJ/t, delivered pressure bar, evidence
 ("Climeworks Gen2 nominal (2000 kWh_th@100C + 650 kWh_e), ~1 bar", 2000*KWH, 100, 650*KWH, 1, "company-stated"),
 ("Mammoth CEO 5000-6000 kWh/t (midpoint 5500, all as energy; split unknown)", None, None, 5500*KWH, 1, "CEO statement 2025"),
 ("Climeworks Gen3 claim: half Gen2 energy", 1000*KWH, 100, 325*KWH, 1, "claim"),
 ("Keith 2018 CE design, 8.81 GJ gas (HHV), CO2 at 150 bar", None, None, None, 150, "modelled design"),
 ("Calcination floor only (CaCO3, dH=178 kJ/mol @900C), Heirloom-type", gj_per_tonne(178e3), 900, 0.0, 1, "thermochem floor"),
 ("BPMED direct ocean capture, lab 155.4 kJ/mol (Digdaya 2020)", 0, 25, gj_per_tonne(155.4e3), 1, "lab measured"),
 ("Verdox electro-swing claim 1.5 GJ/t", 0, 25, 1.5, 1, "claim"),
 ("RepAir claim <1 MWh/t", 0, 25, 3.6, 1, "claim"),
]
for name, q, TC, e, p, ev in cases:
    need = floor_air + (gj_per_tonne(R*T0*math.log(p)) if p > 1 else 0)
    if name.startswith("Keith"):
        energy = 8.81; exergy = 8.81*0.90*1.04  # HHV->LHV ~0.90, chemical exergy ~1.04 x LHV for CH4
        print(f"{name}\n   energy basis eta={need/energy:.1%}; exergy basis (gas exergy ~{exergy:.2f} GJ) eta={need/exergy:.1%}  [Long-Innes&Struchtrup 2022: 7.8%] ({ev})")
        continue
    if q is None:
        print(f"{name}\n   energy basis eta={need/e:.1%} (if all heat at 100C: exergy eta~{need/(e*carnot(100)):.0%} upper bound) ({ev})")
        continue
    energy = q + e
    exergy = q*carnot(TC) + e
    print(f"{name}\n   energy {energy:.2f} GJ/t -> eta={need/energy:.1%}; exergy {exergy:.2f} GJ/t -> eta={need/exergy:.1%}; "
          f"electricity share of exergy {e/exergy if exergy else 0:.0%} ({ev})")

print("\n== 2. Fan work vs pressure drop and capture fraction (60% fan eff.) ==")
for cf in (0.5, 0.75, 0.9):
    row = [f"{fan_work_gj_per_tonne(420e-6, cf, dp):.2f}" for dp in (30, 100, 300, 1000)]
    print(f"capture {cf:.0%}: air {air_volume_per_tonne(420e-6, cf):,.0f} m3/t; fan GJ/t at 30/100/300/1000 Pa: {row}; "
          f"min sep {gj_per_tonne(min_separation_work(420e-6, cf)):.3f}")
print(f"Climeworks 650 kWh_e = {650*KWH:.2f} GJ/t; equivalent dp at 75% capture, 60% fan if all to fans: {650*KWH/fan_work_gj_per_tonne(420e-6,0.75,1):.0f} Pa")

print("\n== 3. Temperature-swing sorbent heat budget (illustrative model, assumed parameters) ==")
dT = 75   # 25 -> 100 C
for wc in (0.5, 1.0, 2.0):          # working capacity mmol CO2/g sorbent
    for mass_ratio in (1.0, 3.0):   # g of (sorbent+support+structure) heated per g sorbent
        cp = 1.2                    # J/gK
        sens = cp*mass_ratio*dT/(wc*1e-3)/1e3   # kJ/mol CO2
        for h2o in (1, 5):          # mol H2O desorbed per mol CO2
            total = sens + 75 + h2o*44
            print(f"wc={wc} mmol/g, heated mass x{mass_ratio}, H2O/CO2={h2o}: sensible {sens:.0f} + ads 75 + water {h2o*44} = {total:.0f} kJ/mol = {gj_per_tonne(total*1e3):.1f} GJ_th/t")

print("\n== 4. Energy cost vs capex at different capacity factors ==")
for gj, label in ((floor_air, "floor"), (2000*KWH*0.25+650*KWH, "Gen2 w/ heat as 25%-cost"), (9.54, "Gen2 all at elec price")):
    print(f"{label}: energy cost at $50/MWh = ${energy_cost_floor(gj, 50):.0f}/t")
capex_per_annual_t = 1.3e9/0.5e6   # Stratos reported total ~$1.3bn for 500 kt/yr design (2023 reporting)
crf = 0.10
for cf in (0.95, 0.6, 0.3):
    print(f"capex ${capex_per_annual_t:,.0f} per t/yr capacity, CRF 10%, CF {cf:.0%}: capital charge ${capex_per_annual_t*crf/cf:,.0f}/t")

print("\n== 5. Climeworks realized utilization (net CDR / nameplate) ==")
print(f"Mammoth H1 2025: 119 t -> annualized {119*2} t = {119*2/36000:.2%} of 36,000 t/yr")
print(f"Mammoth H1 2026: 675 t -> annualized {675*2} t = {675*2/36000:.2%}")
print(f"Orca May-Aug 2025: 357.6 t net in 4 months -> {357.6*3:.0f} t/yr = {357.6*3/4000:.0%} of 4,000")
print(f"Mammoth Mar-Aug 2025: 278.3 t net in 6 months -> {278.3*2:.0f} t/yr = {278.3*2/36000:.2%}")
print(f"Global DAC ~0.01 Mt/yr vs fossil {FOSSIL_CO2_GT} Gt: gap factor {FOSSIL_CO2_GT*1e9/1e4:,.0f}x")

print("\n== 6. Direct ocean capture: floor and fluid handling ==")
w0 = R*T0*math.log(1/420e-6)  # infinitesimal extraction from seawater equilibrated with 420 uatm, product 1 atm
Rv = 10.0
def doc_floor(f, n=2000):
    s = 0
    for i in range(n):
        x = (i+0.5)/n*f
        p = 420e-6*(1-x)**Rv
        s += R*T0*math.log(1/p)
    return s/n
for f in (0.01, 0.1, 0.3):
    print(f"Remove {f:.0%} of DIC (Revelle~10 approx): floor {doc_floor(f)/1e3:.1f} kJ/mol = {gj_per_tonne(doc_floor(f)):.2f} GJ/t (air 75%: {floor_air:.2f})")
dic = 2.1  # mol/m3
for frac in (0.9, 0.5):
    vol = 1e6/44.01/(dic*frac)
    for dp in (10e3, 50e3):
        print(f"extract {frac:.0%} DIC: {vol:,.0f} m3 seawater/t; pump work at {dp/1e3:.0f} kPa, 70% eff: {vol*dp/0.7/1e9:.2f} GJ/t")
print(f"air volume per t at 75%: {air_volume_per_tonne(420e-6,0.75):,.0f} m3 -> ratio air/seawater(90%) {air_volume_per_tonne(420e-6,0.75)/(1e6/44.01/(dic*0.9)):.0f}x")

print("\n== 7. OAE: Planetary Tufts Cove credits vs alkalinity ==")
alk_t = 1103.2; cred = 625.6
mgoh2 = 2*44.01/58.32
print(f"credits/t 'alkalinity' = {cred/alk_t:.2f}; Mg(OH)2 stoichiometric max {mgoh2:.2f} t CO2/t, x0.8 ocean efficiency = {mgoh2*0.8:.2f}; realized/ideal = {cred/alk_t/(mgoh2*0.8):.0%} (if 'alkalinity' = Mg(OH)2 mass; unit ambiguous)")

print("\n== 8. Scale: share of world energy for 1 Gt/yr ==")
for gj in (floor_air, 3.5, 6.0, 10.0, 20.0):
    s = ScaleCheck(1.0, gj)
    print(f"1 Gt/yr at {gj:.2f} GJ/t = {s.ej_per_year:.1f} EJ = {s.share_of_world_primary_energy:.2%} primary; if electric {s.share_of_world_electricity_if_electric:.1%} of world electricity")
