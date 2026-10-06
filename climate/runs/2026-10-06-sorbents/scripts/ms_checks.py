import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
M_H2O = 0.018015
# 1. diffusion time scale L^2/D with D_water in resin binder = 6.503e-12 m2/s (Shi 2017 PLoS ONE)
D = 6.503e-12
for name, L in (("20 um powder (radius 10 um)", 10e-6), ("100 um sheet (half 50 um)", 50e-6), ("0.6 mm bead (radius 300 um)", 300e-6), ("640 um sheet (half 320 um)", 320e-6)):
    print(f"{name:30s}: L^2/D = {L*L/D:9.0f} s = {L*L/D/60:7.1f} min")
# 2. water per CO2 implied by measured uptakes
print("Flory A501 liquid wetting: 3.3 g water/g, 0.675 mmol CO2/g ->", 3.3/(0.675e-3*44.01), "g/g;", 3.3/M_H2O/1000/0.675e-3, "mol/mol")
print("  hydration: ", 3.3/0.018015, "mmol H2O/g")
print("Lively IRA-900 vapour swing 20->85% RH: (28.4-7.1) mmol H2O/g over 0.88-1.27 mmol CO2/g ->", (28.4-7.1)/1.27, "-", (28.4-7.1)/0.88, "mol/mol =", (28.4-7.1)/1.27*M_H2O/M_CO2, "-", (28.4-7.1)/0.88*M_H2O/M_CO2, "kg/kg")
print("Wade IRA-900 20<->95% RH: 23-24 mmol H2O/g per 0.9-1.1 mmol CO2/g ->", 23/1.1, "-", 24/0.9, "mol/mol =", 23/1.1*M_H2O/M_CO2, "-", 24/0.9*M_H2O/M_CO2, "kg/kg")
# 3. Avnos water claims
gal = 475000*3.78541/1000
print("Avnos Brighton: 475,000 gal =", gal, "t water / 450 t CO2 =", gal/450, "t/t; Cedar 6000/3000 =", 2.0, "; pilot 150/30 =", 5.0)
# 4. Flory energy: 490 kWh/t practical, 350 aspirational -> GJ/t and 2nd-law
floor = gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99, T0))
for k in (490, 350):
    print(f"{k} kWh/t = {k*3.6/1000:.2f} GJ/t electric -> second-law {floor/(k*3.6/1000):.0%} (to 15 MPa, so floor should add compression)")
# 5. Shu 2022 electrochemical: 537 kJ/mol
print("Shu 2022: 537 kJ/mol =", gj_per_tonne(537e3), "GJ/t; theoretical 164 kJ/mol =", gj_per_tonne(164e3), "GJ/t")
# 6. stoichiometric ceiling
for iec in (4.18, 5.0, 8.0):
    print(f"IEC {iec} mmol N+/g -> carbonate/bicarbonate swing ceiling {iec/2:.2f} mmol CO2/g")
# 7. outdoor trial throughput
print("782 g CO2 in 7 days =", 782/7, "g/day")
