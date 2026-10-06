import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
# Min et al. 2018: calorimetric heat of adsorption PEI/SiO2 80.5 kJ/mol vs EB-PEI/SiO2 66.2 kJ/mol (measured at flue-gas CO2 pressure).
# Single-site Langmuir with dS=-165 J/mol/K (OptiLex reference): what would those enthalpies imply at 420 ppm?
for dH in (-80.5e3, -70e3, -66.2e3, -60e3):
    th = loading(P_CO2_AIR, T0, dH, -165.0, 1.0)
    Td = desorption_temperature(dH, -165.0, 1.0e3) - 273.15
    print(f"dH {dH/1e3:6.1f} kJ/mol: fractional loading at 420 ppm, {T0-273.15:.0f} C = {th*100:5.1f}%; unloads to 20% at {Td:5.1f} C under 1 kPa CO2")
# Arrhenius leverage of cooling before air exposure: ratio of oxidation rate at T vs 100 C for Ea = 60-100 kJ/mol
for Ea in (60e3, 80e3, 100e3):
    row = []
    for Tc in (100, 80, 70, 55, 40, 25):
        row.append(f"{Tc}C:{math.exp(-Ea/R*(1/(Tc+273.15)-1/373.15)):.3g}")
    print(f"Ea {Ea/1e3:.0f} kJ/mol rate relative to 100 C -> " + "  ".join(row))
# Li 2024 data: 18 h dry 0.04% CO2-air: ~2% at 55 C, 15% at 60 C -> apparent Ea if first-order (very rough, 2 points)
k55 = -math.log(1-0.02)/18; k60 = -math.log(1-0.15)/18
Ea = R*math.log(k60/k55)/(1/328.15-1/333.15)
print(f"apparent Ea from 55->60 C step (Li 2024, 2 points): {Ea/1e3:.0f} kJ/mol (implausibly high => onset/induction behaviour, not simple Arrhenius)")
