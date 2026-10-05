"""Critic checks for bottleneck_thermo_1 (solar collector-adsorber DAC panel). All modelled."""
import sys, math
sys.path.insert(0, 'climate')
from physics import *
MW = 44.01e-3
crf = lambda i, n: i*(1+i)**n/((1+i)**n-1)

# 1. K2CO3: steam is a reaction PRODUCT (2KHCO3 -> K2CO3 + CO2 + H2O), so a steam sweep is not an inert diluent.
Hf = {"K2CO3": -1151.02, "KHCO3": -963.2, "CO2": -393.51, "H2O": -241.82}
S = {"K2CO3": 155.52, "KHCO3": 115.5, "CO2": 213.74, "H2O": 188.83}
dH = (2*Hf["KHCO3"]-Hf["K2CO3"]-Hf["CO2"]-Hf["H2O"])*1e3; dS = 2*S["KHCO3"]-S["K2CO3"]-S["CO2"]-S["H2O"]
Kd = lambda T: math.exp((dH - T*dS)/(R*T))   # decomposition Kp = pCO2*pH2O (bar^2)
print("1. K2CO3 release at 1 atm total: required steam:CO2 in product gas vs bed temperature")
for Tc in (105, 110, 120, 130, 141):
    K = Kd(Tc+273.15)
    # pCO2 + pH2O = 1, pCO2*pH2O = K -> pCO2 = (1 - sqrt(1-4K))/2
    if 4*K >= 1: print(f"  {Tc} C: K={K:.3f}, self-pressurises (no sweep needed)"); continue
    pc = (1-math.sqrt(1-4*K))/2; ratio = (1-pc)/pc
    print(f"  {Tc} C: Kp={K:.4f} bar2 -> max pCO2 {pc:.3f} bar, steam/CO2 {ratio:.0f} mol/mol, "
          f"latent {ratio*44:.0f} kJ/mol CO2 = {ratio*44/MW/1e6:.1f} GJ/t on top of 140 kJ/mol")

# 2. Sorbent charge per tonne = price / (capacity x lifetime cycles): independent of cycles/day if life is cycle-limited.
print("\n2. Sorbent charge ($/t CO2) vs lifetime cycles (8% discount ignored; simple $/kg / kg-CO2-per-kg-life)")
for name, w, price in (("amine", 0.8, 20), ("amine", 1.0, 20), ("K2CO3", 0.6, 4)):
    per_cycle = w*1e-3*MW*1e3   # kg CO2 per kg sorbent per cycle (w mmol/g = mol/kg)
    for n in (45, 300, 1500, 3000):
        print(f"  {name} {w} mmol/g ${price}/kg, {n:5d} cycles: ${price/(per_cycle*n)*1000:,.0f}/t")
    print(f"  {name}: cycles needed for <=$100/t sorbent charge: {price/(per_cycle*0.1):,.0f}")

# 3. What the proposed kill thresholds let through
print("\n3. Cost of a design that just PASSES the proposed kill criteria (base stack: $200/m2, BOS $350, 8%/20yr, O&M 3%)")
L = 0.15; m2 = 1/(L*300/1000); capex = 200*m2+350
cap = capex*(crf(0.08,20)+0.03)
print(f"  0.15 kg/m2/day -> {m2:.1f} m2 per t/yr, capex ${capex:,.0f} per t/yr, capital+O&M ${cap:,.0f}/t before sorbent, energy, T&S")
# 20% loss in 30 cycles, linear fade, replace at 30% loss -> 45 cycles, mean capacity 85%
per_cycle = 0.8e-3*MW*1e3*0.85
print(f"  20% fade per 30 cycles (amine 0.8 mmol/g, replace at 30% loss = 45 cycles): sorbent ${20/(per_cycle*45)*1000:,.0f}/t")

# 4. Wang et al. 2024 measured cycle: ~3 h adsorption + ~40 min solar desorption, 3.7-3.9 kg CO2/h/m3 resin.
print("\n4. Multi-cycle patch (calendar-limited life case): inventory per t/yr at 0.35 kg/m2/day (amine base)")
for n in (1, 2, 3, 4):
    m_s = 0.35/MW/0.8/n; m2 = 1/(0.35*300/1000)
    print(f"  {n} cycle(s)/day: {m_s:.1f} kg/m2, {m_s*m2:.0f} kg per t/yr, sorbent charge (5-yr calendar life, $20/kg, 8%) "
          f"${m_s*m2*20*crf(0.08,5):.0f}/t")
