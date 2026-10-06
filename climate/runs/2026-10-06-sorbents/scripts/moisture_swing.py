import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

T = 298.15
M_H2O = 0.018015
PSAT_25 = 3169.0  # Pa, water saturation pressure at 25 C

def w_water(rh, T=T):
    """Free energy released per mol water evaporating into air at relative humidity rh, J/mol."""
    return -R * T * math.log(rh)

def w_co2(p_out, p_in=P_CO2_AIR, T=T):
    """Ideal isothermal work to raise CO2 from p_in to p_out, J/mol."""
    return R * T * math.log(p_out / p_in)

print("== 1. Thermodynamic water budget: min mol H2O evaporated per mol CO2 ==")
print(f"P_CO2 in air = {P_CO2_AIR:.1f} Pa")
for rh in (0.15, 0.2, 0.3, 0.5, 0.65, 0.8):
    row = [f"RH {rh:.0%}: {w_water(rh)/1e3:5.2f} kJ/mol H2O |"]
    for p_out in (1e3, 5e3, 2.1e4, P0):
        n = w_co2(p_out) / w_water(rh)
        row.append(f"to {p_out/1e3:6.1f} kPa: {n:5.1f} mol/mol ({n*M_H2O/M_CO2:5.2f} kg/kg)")
    print("  ".join(row))

print("\n== 2. Compression ratio achievable with n waters per CO2 (ideal) ==")
for rh in (0.15, 0.2, 0.5):
    for n in (1, 2, 3):
        ratio = (1.0 / rh) ** n
        print(f"RH {rh:.0%}, n={n}: ratio {ratio:8.1f}x -> p_CO2 = {P_CO2_AIR*ratio/1e3:7.2f} kPa")

print("\n== 3. Latent heat drawn from ambient air per tonne CO2, for measured water use ==")
for label, kgkg in (("thermo limit 3:1 molar (Flory)", 3 * M_H2O / M_CO2), ("VMS model low (Wade 2026)", 1.4),
                    ("VMS model high (Wade 2026)", 3.5), ("Shu 2022 humid air", 6.65), ("Shu 2022 dry air", 18.0),
                    ("Flory 2025 outdoor practical", 100.0), ("Flory aspirational 50 wt% uptake", 100.0 / 6.6)):
    molmol = kgkg * M_CO2 / M_H2O
    heat = moisture_swing_water_heat(molmol)
    print(f"{label:36s}: {kgkg:6.1f} kg/kg = {molmol:6.1f} mol/mol -> latent {gj_per_tonne(heat):7.1f} GJ/t (ambient, free)")

print("\n== 4. Air needed: drying vs CO2 supply ==")
# air at 25 C; water vapour pickup = psat*(rh_out - rh_in); CO2 pickup = 420 ppm * capture fraction
for rh_in, rh_out in ((0.15, 0.5), (0.2, 0.6), (0.5, 0.8)):
    dpw = PSAT_25 * (rh_out - rh_in)
    for cap in (0.25, 0.5):
        dpc = P_CO2_AIR * cap
        ceiling = dpw / dpc
        print(f"RH {rh_in:.0%}->{rh_out:.0%}, CO2 capture frac {cap:.0%}: one volume of air can carry {ceiling:6.1f} mol H2O per mol CO2 it supplies")
print("  measured practical water use 100 kg/kg = %.0f mol/mol; VMS 1.4-3.5 kg/kg = %.1f-%.1f mol/mol" % (100*M_CO2/M_H2O, 1.4*M_CO2/M_H2O, 3.5*M_CO2/M_H2O))

print("\n== 5. Work to compress a dilute moisture-swing product to 1 atm and to 150 bar ==")
for p in (500.0, 1e3, 2e3, 5e3, 2.1e4):
    ideal = w_co2(P0, p)
    real = ideal / 0.6   # 60% isothermal efficiency vacuum pump (optimistic for deep vacuum)
    print(f"p_CO2 = {p/1e3:5.1f} kPa: ideal {gj_per_tonne(ideal):.3f} GJ/t, at 60% eff {gj_per_tonne(real):.3f} GJ/t ({gj_per_tonne(real)/3.6*1000:.0f} kWh/t)")
hp = R * T * math.log(150e5 / P0)
print(f"1 atm -> 150 bar ideal isothermal: {gj_per_tonne(hp):.3f} GJ/t; at 65% eff {gj_per_tonne(hp)/0.65:.3f} GJ/t ({gj_per_tonne(hp)/0.65/3.6*1000:.0f} kWh/t)")
# if water vapour must be pumped with CO2 (not condensed before pump) at psat 25C ~3.2 kPa:
for p in (1e3, 2e3, 5e3):
    extra = (PSAT_25 / p)   # mol H2O per mol CO2 in the vapour phase
    work = (1 + extra) * R * T * math.log(P0 / (p + PSAT_25)) / 0.6
    print(f"  if vapour not condensed first: p_CO2 {p/1e3:.0f} kPa carries {extra:.1f} mol H2O/mol CO2 -> pump work {gj_per_tonne(work):.2f} GJ/t")

floor = gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99, T))
print(f"\nThermodynamic floor (75% capture, 99% pure, 1 atm): {floor:.3f} GJ/t")
for e in (1.0, 2.5, 5.0, 15.0):
    print(f"  VMS electricity {e:4.1f} GJ/t -> second-law efficiency {floor/e:.1%}")
ref = reference_amine_cycle()
print(f"Reference amine TVSA: heat {ref.heat_gj_per_t:.2f} GJ/t, work-eq {ref.work_equivalent_gj_per_t:.2f} GJ/t, 2nd-law {ref.second_law_efficiency:.1%}")

print("\n== 6. Sorbent replacement cost ($/t CO2) ==")
cases = [
    ("A501 practical 0.675 mmol/g, $54/kg, 1380 cycles (302 d outdoor, ~10% capacity left)", 54, 0.675, 1380),
    ("A501 0.675 mmol/g, $54/kg, 5 yr x 8 cycles/d = 14,600", 54, 0.675, 14600),
    ("A501 0.675 mmol/g, $7/kg, 14,600 cycles", 7, 0.675, 14600),
    ("IRA-900 1.27 mmol/g (20->50% RH lab), $7/kg, 14,600 cycles", 7, 1.27, 14600),
    ("IRA-900 0.9 mmol/g (VMS kinetics run), $20/kg, 2,000 cycles", 20, 0.9, 2000),
    ("aspirational 4.0 mmol/g, $7/kg, 10 yr x 12/d = 43,800", 7, 4.0, 43800),
    ("QMPR-2 fast-kinetics 0.26 mmol/g, $20/kg, 20,000 cycles", 20, 0.26, 20000),
]
for label, price, wc, n in cases:
    print(f"{label:88s}: ${sorbent_cost_per_tonne(price, wc, n):8.0f}/t")

print("\n== 7. Productivity (kg CO2 / kg sorbent / day) ==")
for label, wc, cpd in (("A501 outdoor 0.675 mmol/g, 2 h day / 4 h night ~ 9 cycles/d", 0.675, 9),
                       ("IRA-900 0.9 mmol/g, measured ~2 h load + ~3 h unload = 4.8 cycles/d", 0.9, 4.8),
                       ("QMPR-2 0.26 mmol/g, half-time 2.9 min -> ~20 min cycle = 72/d", 0.26, 72),
                       ("reference amine 1.04 mol/kg, 12 cycles/d", 1.04, 12)):
    print(f"{label:72s}: {productivity(wc, cpd):.3f}")

print("\n== 8. Mass-transfer: measured LDF constants -> time to 90% ==")
for k in (4.5e-4, 14e-4, 20e-4, 90e-4):
    print(f"k = {k*1e4:5.1f}e-4 1/s: t90 = {math.log(10)/k/60:6.1f} min, half-time {math.log(2)/k/60:5.1f} min")

print("\n== 9. Site utilisation check: QA sites vs CO2 capacity ==")
for label, iec, q in (("IRA-900-C (Lively 2025), 4.18 mmol N/g, 1.92 mmol CO2/g @400ppm 20%RH", 4.18, 1.92),
                      ("QPET claim 6.08 mmol CO2/g: required QA if 1 CO2 per 2 N+ (carbonate->bicarbonate)", None, 6.08)):
    if iec:
        print(f"{label}: CO2 per N+ = {q/iec:.2f}")
    else:
        print(f"{label}: needs >= {q:.1f}-{2*q:.1f} mmol N+/g; pure poly(vinylbenzyl trimethylammonium bicarbonate) has ~{1000/237.3:.1f} mmol N+/g")

print("\n== 10. Water cost per tonne CO2 ==")
for kgkg in (1.4, 3.5, 15, 100):
    for price, lab in ((0.3, "$0.3/m3 process"), (1.5, "$1.5/m3 desal")):
        print(f"water {kgkg:5.1f} t/t at {lab}: ${kgkg*price:6.1f}/t CO2")
