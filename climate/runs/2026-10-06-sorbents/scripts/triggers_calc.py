import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
from scipy.optimize import brentq

GJ = lambda j_per_mol: gj_per_tonne(j_per_mol)
print("=== 0. reference check")
ref = reference_amine_cycle()
print(f"ref heat {ref.heat_gj_per_t:.2f} GJ/t, wc {ref.working_capacity:.2f}, work-eq {ref.work_equivalent_gj_per_t:.2f}")
floor = min_separation_work(X_AIR, 0.75, 0.99, T0)
print(f"floor {floor/1e3:.1f} kJ/mol = {GJ(floor):.2f} GJ/t")

print("\n=== 1. Photo-swing photon budget")
h, c, NA = 6.62607e-34, 2.99792e8, 6.02214e23
for lam in (365, 405, 450, 520):
    E = h * c / (lam * 1e-9) * NA  # J per mol photons
    for phi in (1.0, 0.125, 0.04):
        print(f"  {lam} nm: {E/1e3:.0f} kJ/einstein; CO2/photon {phi:>5}: {E/phi/1e3:7.0f} kJ/mol = {GJ(E/phi):6.1f} GJ/t light; "
              f"photon-to-separation efficiency {floor/(E/phi):.2%}")
# solar area: annual insolation 2000 kWh/m2/yr (good site), usable band fraction f
for (lam, phi, frac, label) in ((365, 0.04, 0.05, "UV photobase QY 4% (PyDIG-like), ~5% of solar is UV"),
                                (450, 0.125, 0.25, "visible photoacid 0.125 CO2/photon (pyranine-like), ~25% of solar usable"),
                                (450, 1.0, 0.25, "ideal visible, 1 CO2/photon")):
    E = h * c / (lam * 1e-9) * NA / phi
    per_t = E / M_CO2 * 1000.0 / 3.6e6  # kWh light per tonne   (M_CO2 kg/mol)
    area = per_t / (2000.0 * frac)
    print(f"  {label}: {per_t:,.0f} kWh light/t -> {area:,.1f} m2-yr per t CO2 ({1/area*1e4/1:,.0f} t/ha/yr)")
print("  PV + heat pump comparison: 2000 kWh/m2/yr * 22% PV = 440 kWh_e/m2/yr; reference cycle work-eq "
      f"{ref.work_equivalent_gj_per_t:.2f} GJ/t = {ref.work_equivalent_gj_per_t*277.8:.0f} kWh/t -> "
      f"{ref.work_equivalent_gj_per_t*277.8/440:.1f} m2-yr/t; at a realistic 2000 kWh_e/t -> {2000/440:.1f} m2-yr/t")

print("\n=== 2. Cooperative (Hill) isotherm vs Langmuir, same dH/dS")
def hill_loading(p, T, dH, dS, n):
    bp = langmuir_b(dH, dS, T) * p
    return bp**n / (1 + bp**n)
def T_for_loading(target, p, dH, dS, n):
    return brentq(lambda T: hill_loading(p, T, dH, dS, n) - target, 250, 700)
dS = -165.0
for n in (1, 2, 4, 8):
    # choose dH so that the sorbent is 90% full at 420 ppm, 25 C
    dH = brentq(lambda x: hill_loading(P_CO2_AIR, T0, x, dS, n) - 0.9, -120e3, -40e3)
    for p_des in (1e3, 1e4, 1e5):
        Td = T_for_loading(0.1, p_des, dH, dS, n)
        wc = 0.8 * 2.0  # mol/kg, q_max 2
        sens = 1500.0 * (Td - T0) / wc
        print(f"  n={n}: dH for 90% fill = {dH/1e3:6.1f} kJ/mol; unload to 10% at p_des {p_des/1e3:5.0f} kPa needs {Td-273.15:5.0f} C; "
              f"sensible {GJ(sens):.2f} GJ/t; reaction {GJ(-dH):.2f} GJ/t; sum {GJ(sens-dH):.2f} GJ/t")
print("  -> pressure-ratio term alone (infinitely sharp step): T at which step pressure reaches p_des")
dHs = dG_for_half_loading() + T0 * dS
for p_des in (1e3, 1e4, 1e5):
    Td = -dHs / (R * math.log(P_REF / p_des) - dS)
    print(f"     dH_step = {dHs/1e3:.1f} kJ/mol; p_des {p_des/1e3:.0f} kPa -> {Td-273.15:.0f} C")

print("\n=== 3. Carbonic anhydrase: liquid-film mass transfer K_L = sqrt(D*k1)")
D = 1.9e-9      # m2/s CO2 in water 25 C
kOH = 8.4e3     # 1/M/s, CO2 + OH- at 25 C (Pinsent et al. 1956)
k_h2o = 0.037   # 1/s uncatalysed hydration
kcat_KM = {"hCA II (1.5e8 /M/s, Khalifah 1971)": 1.5e8, "engineered/thermostable (assume 1e7 /M/s)": 1e7}
print(f"  1 M OH-: k1 = {kOH:.0f} /s, K_L = {math.sqrt(D*kOH)*1e3:.2f} mm/s (ideal, no ionic-strength correction; "
      "Holmes & Keith 2012 measured ~1.3 mm/s for a real contactor solution)")
for pH in (10.0, 11.0):
    oh = 10 ** (pH - 14)
    k1 = kOH * oh + k_h2o
    print(f"  carbonate buffer pH {pH}: k1 = {k1:.2f} /s, K_L = {math.sqrt(D*k1)*1e3:.3f} mm/s (uncatalysed)")
    for name, kk in kcat_KM.items():
        for gL in (0.1, 1.0):
            E = gL / 30000.0
            k1e = k1 + kk * E
            print(f"     + {gL} g/L {name}: k1 = {k1e:.0f} /s, K_L = {math.sqrt(D*k1e)*1e3:.2f} mm/s, enhancement x{math.sqrt(k1e/k1):.0f}")
# carbonate loading limit at DAC back-pressure
K1, K2, H = 4.45e-7, 4.69e-11, 0.034  # M, M, M/atm at 25 C
Keq = K1 / K2
for Ctot in (1.0, 2.0):
    for frac_of_ambient in (0.25, 0.5):
        target = frac_of_ambient * 420e-6
        x = brentq(lambda x: (2*x*Ctot)**2 / ((1-x)*Ctot * Keq * H) - target, 1e-6, 0.999)
        print(f"  {Ctot} M K2CO3: carbonate->bicarbonate conversion at which p_CO2,eq = {frac_of_ambient:.2f} x ambient: {x:.3f} "
              f"-> cyclic loading <= {x*Ctot:.3f} mol CO2/L (ideal activity)")

print("\n=== 4. Direct electrical heating (Joule / induction / microwave) vs heat-pump or waste heat")
price = 50.0  # $/MWh
kwh = lambda gj: gj * 277.78
for label, gj_e in (("N5-dGA Joule heat duty, reported 3.4 GJ_e/t (Nat Commun 2026)", 3.4),
                    ("charged-sorbent Joule, reported 6.5 GJ_e/t at 11% RH", 6.5),
                    ("charged-sorbent Joule, reported 11.4 GJ_e/t at 38% RH", 11.4),
                    ("reference cycle heat 6.04 GJ_th via heat pump COP 3", ref.heat_gj_per_t / 3),
                    ("reference cycle heat 6.04 GJ_th via heat pump COP 2", ref.heat_gj_per_t / 2),
                    ("reference cycle heat 6.04 GJ_th all resistive", ref.heat_gj_per_t)):
    print(f"  {label}: {kwh(gj_e):,.0f} kWh_e/t -> ${kwh(gj_e)*price/1000:,.0f}/t at $50/MWh; 2nd-law eff vs floor {GJ(floor)/gj_e:.0%}")
print("  capital lever: $274/t capital charge; if rapid heating multiplies cycles/day by f and capital scales 1/f:")
for f in (1.5, 2, 4):
    print(f"     f={f}: capital charge -> ${274/f:.0f}/t (saves ${274-274/f:.0f}/t) if ALL capital scaled with sorbent throughput; "
          f"if only 50% of capital is contactor/sorbent-bound: saves ${0.5*(274-274/f):.0f}/t")

print("\n=== 5. Moisture swing: water free energy and water use")
for RH in (0.2, 0.3, 0.5, 0.7):
    dG_w = -R * T0 * math.log(RH)   # J per mol water evaporated into air at RH
    for p_prod in (2e3, 1e5):
        wmin = R * T0 * math.log(p_prod / P_CO2_AIR)
        n_min = wmin / dG_w
        print(f"  RH {RH:.0%}: {dG_w/1e3:.2f} kJ/mol H2O available; concentrate 42 Pa -> {p_prod/1e3:.0f} kPa needs >= {wmin/1e3:.1f} kJ/mol CO2 "
              f"-> >= {n_min:.1f} mol H2O/mol CO2 = {n_min*18.015/44.01:.1f} t water/t CO2 (reversible limit)")
for n in (10, 50, 100):
    print(f"  practical {n} mol H2O/mol CO2: {n*18.015/44.01:.0f} t water/t CO2; latent heat {GJ(moisture_swing_water_heat(n)):.0f} GJ/t (from ambient air)")
print(f"  compressing a 2 kPa CO2 product to 1 atm: ideal {GJ(R*T0*math.log(P0/2e3)):.2f} GJ/t, at 70% eff {GJ(R*T0*math.log(P0/2e3)/0.7):.2f} GJ/t")

print("\n=== 6. Electro-swing voltage budget")
for (ne, V, fe, lab) in ((2, 0.5, 0.9, "quinone-like 2e, 0.5 V, 90% FE"), (1, 0.3, 0.9, "PCET 1e, 0.3 V"), (2, 1.3, 0.5, "eDAC-like 2e/CO2, 1.3 V, 50% capture eff")):
    w = electrochemical_work(ne, V, fe)
    print(f"  {lab}: {w/1e3:.0f} kJ/mol = {GJ(w):.2f} GJ_e/t = {kwh(GJ(w)):.0f} kWh/t; 2nd-law {floor/w:.0%}")
print(f"  minimum voltage for 1 e-/CO2 at the floor: {floor/FARADAY:.3f} V; for 2 e-/CO2: {floor/2/FARADAY:.3f} V")

print("\n=== 7. Sorbent lifetime cost for trigger-enabled materials")
for (lab, price_kg, wc, cyc) in (("N5-dGA-like, 6.57 mol/kg, $50/kg, 500 cycles shown", 50, 6.57*0.95, 500),
                                 ("N5-dGA-like, 6.57 mol/kg, $50/kg, 5000 cycles", 50, 6.57*0.95, 5000),
                                 ("charged-sorbent 0.1 mol/kg, $5/kg, 5000 cycles", 5, 0.1, 5000),
                                 ("moisture-swing resin 1.0 mol/kg, $10/kg, 300 diurnal cycles (1 yr)", 10, 1.0, 300),
                                 ("moisture-swing resin 1.0 mol/kg, $10/kg, 3000 cycles", 10, 1.0, 3000),
                                 ("TriH-like 6 mol/kg, $20/kg, 1000 cycles", 20, 6.0, 1000)):
    print(f"  {lab}: ${sorbent_cost_per_tonne(price_kg, wc, cyc):,.0f}/t")
for cpd in (1, 4, 24):
    print(f"  productivity at 1 mol/kg, {cpd} cycles/day: {productivity(1.0, cpd):.3f} kg CO2/kg/day -> {1000/ (productivity(1.0, cpd)*365):.1f} kg sorbent per t/yr")
