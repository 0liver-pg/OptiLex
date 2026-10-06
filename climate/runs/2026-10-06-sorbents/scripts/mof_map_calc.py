import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

R_ = 8.314462618
T0_ = 298.15
P_AIR = 40.0  # Pa, ~0.4 mbar (400 ppm), the condition used in the cited papers

def cc_pressure(p1, T1, T2, qst):
    """Clausius-Clapeyron: CO2 pressure at T2 holding loading constant, given isosteric heat qst (J/mol, positive)."""
    return p1 * math.exp(qst / R_ * (1.0 / T1 - 1.0 / T2))

print("=== 1. COF-999: what CO2 pressure can a 60 C swing deliver? (Qst = 53 kJ/mol, dry isotherm, Zhou 2024) ===")
for T in (60, 80, 100, 120):
    p = cc_pressure(P_AIR, T0_, T + 273.15, 53e3)
    print(f"  T_des {T:3d} C: equilibrium CO2 pressure at the full 400 ppm loading = {p:7.1f} Pa = {p/100:5.2f} mbar")
# Langmuir fit of COF-999 dry isotherm: 0.91 mmol/g at 0.4 mbar, ~2.9 mmol/g near 1 bar (Fig 3a), Qst 53
qmax = 2.9
theta = 0.91 / qmax
b25 = theta / (1 - theta) / P_AIR
dG = -R_ * T0_ * math.log(b25 * 1e5)
dS = (-53e3 - dG) / T0_
print(f"  single-site Langmuir fit: theta(0.4 mbar)={theta:.2f}, dG={dG/1e3:.1f} kJ/mol, implied dS={dS:.0f} J/mol/K")
for T, pdes in ((60, 1e3), (60, 100.0), (60, 10.0), (80, 1e3), (100, 1e3)):
    c = TVSACycle(dH=-53e3, dS=dS, q_max=qmax, T_des=T + 273.15, p_des=pdes, water_coads=0.0)
    print(f"  T_des {T} C, p_CO2,des {pdes:6.0f} Pa: q_ads={c.q_ads:.2f}, q_des={c.q_des:.2f}, working capacity={c.working_capacity:.2f} mol/kg")
print("  -> at 60 C the sorbent only unloads if the CO2 partial pressure is held at ~0.1-1 mbar: purge gas or deep vacuum.")

print()
print("=== 2. Water penalty for COF-999 (0.09 g H2O/g at 50% RH; 2.05 mmol CO2/g at 50% RH) ===")
h2o = 0.09 / 0.018  # mol/kg
ratio = h2o / 2.05
print(f"  H2O co-adsorbed {h2o:.1f} mol/kg -> {ratio:.2f} mol H2O per mol CO2; latent heat = {gj_per_tonne(moisture_swing_water_heat(ratio)):.2f} GJ/t")
c = TVSACycle(dH=-53e3, dS=dS, q_max=2.05/ (0.91/2.9), T_des=333.15, p_des=100.0, water_coads=ratio)
# simple heat budget at measured humid working capacity 1.28 mol/kg (outdoor average), dT = 35 K
wc = 1.28
sens = 1500.0 * 35.0 / wc
tot = 53e3 + sens + ratio * 44.0e3
print(f"  heat budget at measured outdoor working capacity {wc} mol/kg, 25->60 C: reaction {gj_per_tonne(53e3):.2f} + sensible {gj_per_tonne(sens):.2f} + water {gj_per_tonne(ratio*44e3):.2f} = {gj_per_tonne(tot):.2f} GJ/t (thermal, powder only, no contactor mass)")
print(f"  for comparison the reference amine cycle: {reference_amine_cycle().heat_gj_per_t:.2f} GJ/t")
carnot = 1 - 298.15 / 333.15
print(f"  Carnot factor at 60 C = {carnot:.3f} -> exergy of that heat = {gj_per_tonne(tot)*carnot:.2f} GJ/t; vacuum work to pump CO2 from 1 mbar to 1 atm at 70% eff = {gj_per_tonne(R_*298.15*math.log(101325/100.0)/0.7):.2f} GJ/t")

print()
print("=== 3. Sorbent replacement cost per tonne CO2: demonstrated cycle counts vs needed ===")
cases = [
    ("COF-999 outdoor, 1.28 mol/kg, 100 cycles demonstrated", 1.28, 100),
    ("COF-999, 1.28 mol/kg, 2,000 cycles", 1.28, 2000),
    ("COF-999, 1.28 mol/kg, 20,000 cycles", 1.28, 20000),
    ("COF-1000 outdoor, 1.33 mol/kg, 50 cycles demonstrated", 22.1 / (50 / 3.0), 50),
    ("mmen-Mg2(dobpdc), 1.5 mol/kg, 50 cycles demonstrated", 1.5, 50),
    ("MOF-808-Lys, 0.696 mol/kg, 2,000 cycles (hypothetical)", 0.696, 2000),
]
for name, wcap, n in cases:
    row = ", ".join(f"${price}/kg -> ${sorbent_cost_per_tonne(price, wcap, n):,.0f}/t" for price in (20, 50, 200))
    print(f"  {name}: {row}")
print("  cycles needed for <= $20/t sorbent cost at 1.28 mol/kg:")
for price in (20, 50, 200, 1000):
    n = price / (20.0 / 1000.0) / (1.28 * M_CO2)
    print(f"    ${price}/kg -> {n:,.0f} cycles ({n/16.7/365:.1f} years at COF-1000's 16.7 cycles/day; {n/5.0/365:.1f} years at 5 cycles/day)")

print()
print("=== 4. Productivity (kg CO2 per kg sorbent per day) and sorbent inventory per t/yr ===")
for name, wcap, cpd in (("COF-999 outdoor (100 cycles / 20 days)", 1.28, 5.0),
                        ("COF-1000 outdoor (50 cycles / 3 days)", 22.1 / (50 / 3.0), 50 / 3.0),
                        ("reference amine cycle, 6 cycles/day", 1.04, 6.0)):
    pr = productivity(wcap, cpd)
    print(f"  {name}: {pr:.2f} kg/kg/day -> {1000.0/(pr*365):.1f} kg sorbent per t/yr")

print()
print("=== 5. Step-isotherm sorbents: capture-fraction ceiling 1 - p_step/p_feed and temperature sensitivity ===")
for dH_step in (-60e3, -71e3, -80e3):
    for p_step25 in (5.0, 10.0, 20.0):  # Pa at 25 C
        out = []
        for T in (0, 15, 25, 35, 45):
            ps = cc_pressure(p_step25, T0_, T + 273.15, -dH_step)
            ceil = max(0.0, 1 - ps / P_AIR)
            out.append(f"{T}C:{ceil*100:3.0f}%")
        print(f"  dH_step {dH_step/1e3:.0f} kJ/mol, p_step(25C) {p_step25/100:.2f} mbar: " + "  ".join(out))

print()
print("=== 6. Degradation rates expressed per cycle and as sorbent lifetime ===")
# TIFSIX-3-Ni: 36% loss in 50 ambient-air TSA cycles (Low 2024); e-2-Mg2(dobpdc): 15% loss in 60 days dry air at 25 C (Xiong 2025)
for name, loss, n in (("TIFSIX-3-Ni pellets, 160 C regen in air", 0.36, 50),):
    k = -math.log(1 - loss) / n
    print(f"  {name}: {loss*100:.0f}% in {n} cycles -> {k*100:.2f}%/cycle; cycles to 50% capacity = {math.log(2)/k:.0f}")
k_day = -math.log(1 - 0.15) / 60
print(f"  e-2-Mg2(dobpdc) in dry air at 25 C: 15% in 60 days -> {k_day*100:.2f}%/day; time to 50% = {math.log(2)/k_day:.0f} days ({math.log(2)/k_day/365:.2f} yr), before any hot-regeneration O2 exposure")
# allowed fade for 20,000 cycles to 80% capacity
print(f"  fade allowed to keep 80% capacity after 20,000 cycles: {(-math.log(0.8)/20000)*100:.4f}%/cycle; a 100-cycle test would show only {(1-math.exp(math.log(0.8)*100/20000))*100:.2f}% loss -> below the +/-3% scatter of reported cycle data")

print()
print("=== 7. CALF-20 at 400 ppm: Langmuir estimate from 2.6 mmol/g at 0.15 bar and ~4.07 mmol/g at 1.2 bar ===")
# solve two-point single-site Langmuir
q1, p1, q2, p2 = 2.6, 0.15e5, 4.07, 1.2e5
# q = qm*b*p/(1+b*p): two equations -> solve by bisection on b
lo, hi = 1e-7, 1e-2
for _ in range(200):
    b = math.sqrt(lo * hi)
    qm = q1 * (1 + b * p1) / (b * p1)
    f = qm * b * p2 / (1 + b * p2) - q2
    if f > 0: lo = b
    else: hi = b
print(f"  fit: q_max={qm:.2f} mmol/g, b={b*1e5:.1f} /bar -> loading at 0.4 mbar = {qm*b*P_AIR/(1+b*P_AIR):.3f} mmol/g (dry, 25 C; ~{qm*b*P_AIR/(1+b*P_AIR)/0.91*100:.0f}% of COF-999's dry uptake)")
print(f"  dG needed for half filling at 420 ppm: {dG_for_half_loading()/1e3:.1f} kJ/mol; CALF-20 fit dG = {-R_*T0_*math.log(b*1e5)/1e3:.1f} kJ/mol")
