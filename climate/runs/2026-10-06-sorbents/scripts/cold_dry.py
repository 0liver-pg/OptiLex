import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

def p_sat(T):
    """Saturation vapour pressure, Pa. Over ice below 273.15 K (Murphy & Koop 2005), over water above (Magnus)."""
    if T < 273.15:
        return math.exp(9.550426 - 5723.265 / T + 3.53068 * math.log(T) - 0.00728332 * T)
    tc = T - 273.15
    return 610.94 * math.exp(17.625 * tc / (tc + 243.04))

CAPTURE = 0.75
print("A. Water load on a dry-air physisorbent process (all water in the processed air must be removed first)")
print(f"{'T C':>6}{'RH':>6}{'pH2O Pa':>10}{'H2O ppm':>10}{'H2O/CO2 in air':>16}{'mol H2O per mol CO2 captured':>30}"
      f"{'dry heat GJ/t @50kJ/mol':>25}{'min work GJ/t (~RT/mol)':>25}")
for tc, rh in [(30, 0.7), (20, 0.5), (10, 0.7), (0, 0.7), (-10, 0.7), (-20, 0.7), (-30, 0.7), (-40, 0.7), (-58, 0.7)]:
    T = tc + 273.15
    pw = rh * p_sat(T)
    ratio = pw / P_CO2_AIR
    per_captured = ratio / CAPTURE
    heat = gj_per_tonne(per_captured * 50_000.0)     # desiccant regeneration heat ~50 kJ/mol H2O (silica gel; zeolites 55-65)
    wmin = gj_per_tonne(per_captured * R * T)        # exergy of dried air relative to ambient ~ RT per mol water removed
    print(f"{tc:>6}{rh:>6.0%}{pw:>10.1f}{pw/P0*1e6:>10.0f}{ratio:>16.1f}{per_captured:>30.1f}{heat:>25.2f}{wmin:>25.2f}")
print(f"   CO2 separation floor for comparison: {gj_per_tonne(min_separation_work(X_AIR, CAPTURE, 0.99)):.2f} GJ/t")

print("\nB. Sensible-heat check of Wilson 2022 (Na-X, 420 ppm, pre-dried air, desorb at 200 C)")
cp = 920.0  # J/kg/K zeolite
for tc, q in [(20, 0.30), (0, 0.65), (-20, 1.1), (-40, 1.9), (-58, 2.5)]:
    sens = cp * (200 - tc) / q                     # J per mol CO2, full regeneration, no recovery, no binder/vessel
    rxn = 45_000.0
    tot = sens + rxn
    carnot = 1 - (tc + 273.15) / 473.15
    print(f"  T_ads {tc:>4} C  q {q:.2f} mol/kg  sensible {gj_per_tonne(sens):5.2f} GJ/t ({gj_per_tonne(sens)/3.6:4.2f} MWh/t)"
          f"  + reaction {gj_per_tonne(rxn):.2f} = {gj_per_tonne(tot):5.2f} GJ/t heat; work-equivalent of that heat {gj_per_tonne(tot*carnot):5.2f} GJ/t")
ref = reference_amine_cycle()
print(f"  reference amine cycle: heat {ref.heat_gj_per_t:.2f} GJ/t, work-equivalent {ref.work_equivalent_gj_per_t:.2f} GJ/t")
print(f"  Wilson total 1.1-1.23 MWh/t = {1.1*3.6:.2f}-{1.23*3.6:.2f} GJ/t (if supplied as resistive electricity this IS work)")

print("\nC. Apparent temperature dependence of Na-X uptake at 420 ppm (Wilson 2022) vs single-site Langmuir")
import numpy as np
Ts = np.array([20, 0, -20, -40, -58]) + 273.15
qs = np.array([0.30, 0.65, 1.1, 1.9, 2.5])
slope = np.polyfit(1 / Ts, np.log(qs), 1)[0]
print(f"  apparent van't Hoff slope of ln(q) vs 1/T: {slope*R/1e3:.1f} kJ/mol (isosteric heat measured: 44-49 kJ/mol)")
# single-site Langmuir with dH=-45 kJ/mol, q_max 6 mol/kg anchored at 0.30 mol/kg at 20 C
dH = -45_000.0; qmax = 6.0
bp20 = 0.30 / (qmax - 0.30)
for T, q in zip(Ts, qs):
    bp = bp20 * math.exp(-dH / R * (1 / T - 1 / 293.15))
    print(f"  {T-273.15:>5.0f} C  measured {q:.2f}  single-site Langmuir (dH -45, q_max 6) {qmax*bp/(1+bp):.2f} mol/kg")

print("\nD. Sorbent replacement cost, zeolite vs amine (verifier formula)")
for name, price, wc, cycles in [("13X cold (-20 C), 15 y at 4 cycles/day", 3.0, 1.0, 15*365*4), ("13X ambient dry, same life", 3.0, 0.30, 15*365*4),
                                ("amine reference, 2,000 cycles", 20.0, ref.working_capacity, 2000), ("amine reference, 20,000 cycles", 20.0, ref.working_capacity, 20000)]:
    print(f"  {name:<42} ${sorbent_cost_per_tonne(price, wc, cycles):7.2f}/t CO2")

print("\nE. Near-cryogenic (195 K) DAC with LNG cold: air-cooling duty and scale cap")
air_kg_per_t = 1000.0 / (X_AIR * M_CO2 / 0.02897 * CAPTURE)   # kg air per t CO2 captured
print(f"  air processed: {air_kg_per_t/1e6:.2f} kt air per t CO2 at {CAPTURE:.0%} capture")
dT = 288.15 - 195.0
duty = air_kg_per_t * 1005.0 * dT / 1e9  # GJ/t
lng_cold = 0.83  # GJ per t LNG (latent ~0.51 + sensible to ambient ~0.32), typical literature value
for rec in (0.0, 0.90, 0.95, 0.98):
    net = duty * (1 - rec)
    t_lng = net / lng_cold
    print(f"  recuperation {rec:.0%}: cold duty {net:7.1f} GJ/t CO2 -> {t_lng:6.1f} t LNG regasified per t CO2;"
          f" burning that LNG emits {t_lng*2.75:6.0f} t CO2; 400 Mt LNG/y supports {400/t_lng:6.1f} Mt CO2/y")
nf = 0.6*p_sat(288.15)/P_CO2_AIR/CAPTURE
print(f"  frost load at 15 C, 60 pct RH: {nf:.0f} mol H2O per mol CO2 captured = {nf*18.015/44.01:.1f} t water (ice) per t CO2")
for dp in (100, 300, 600):
    print(f"  fan work at {dp} Pa total pressure drop: {fan_work_gj_per_tonne(X_AIR, CAPTURE, dp):.2f} GJ/t")

print("\nF. Water co-production: water in the processed air per t CO2 (upper bound on harvest)")
for tc, rh in [(30, 0.7), (20, 0.5), (20, 0.2), (0, 0.7), (-20, 0.7)]:
    T = tc + 273.15
    n = rh * p_sat(T) / P_CO2_AIR / CAPTURE
    print(f"  {tc:>4} C {rh:.0%} RH: {n*18.015/44.01:6.1f} t H2O per t CO2")
