import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
CAPTURE = 0.75
air_kg = 1000.0 / (X_AIR * M_CO2 / 0.02897 * CAPTURE)
per_K = air_kg * 1005.0 / 1e9
print(f"L. Heating or cooling the whole air stream: {per_K:.2f} GJ per kelvin per tonne CO2 (75% capture), before recuperation")
for dT, rec in [(10, 0.0), (10, 0.9), (10, 0.95), (45, 0.9), (45, 0.95), (93, 0.95), (93, 0.98), (93, 0.99)]:
    print(f"   dT {dT:>3} K, recuperation {rec:.0%}: {per_K*dT*(1-rec):6.1f} GJ/t")
def p_sat(T):
    if T < 273.15:
        return math.exp(9.550426 - 5723.265 / T + 3.53068 * math.log(T) - 0.00728332 * T)
    tc = T - 273.15
    return 610.94 * math.exp(17.625 * tc / (tc + 243.04))
print("M. Adiabatic temperature rise of the air when a desiccant takes up all its water (50 kJ/mol H2O, air cp 29.1 J/mol/K)")
for tc, rh in [(30, 0.7), (20, 0.5), (0, 0.7), (-20, 0.7), (-40, 0.7)]:
    x = rh * p_sat(tc + 273.15) / P0
    print(f"   {tc:>4} C, {rh:.0%} RH: +{x*50_000/29.1:5.1f} K")
print("N. Fan electricity per 100 Pa of added pressure drop: %.2f GJ/t (%.0f kWh/t)" % (fan_work_gj_per_tonne(X_AIR, CAPTURE, 100.0), fan_work_gj_per_tonne(X_AIR, CAPTURE, 100.0)/3.6e-3))
print("O. LNG-cold DAC vs the LNG's own combustion CO2 (2.75 t CO2 per t LNG): claim of 103-142 Mt/y in 2050")
for lng_mt in (400, 600, 700):
    print(f"   {lng_mt} Mt LNG/y -> combustion {lng_mt*2.75/1000:.2f} Gt CO2/y; 103-142 Mt/y captured = {103/(lng_mt*2.75):.1%}-{142/(lng_mt*2.75):.1%} of it; "
          f"implied {lng_mt/142:.1f}-{lng_mt/103:.1f} t LNG per t CO2")
