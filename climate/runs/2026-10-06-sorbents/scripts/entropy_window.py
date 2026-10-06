import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

print("G. Entropy, not just enthalpy, sets the binding window")
# NbOFFIVE-1-Ni: 1.3 mmol/g at 400 ppm, 298 K; Qst 54 kJ/mol; saturation ~2.2 mmol/g (near-full loading at 0.01 bar per Sci. Adv. 2019)
theta = 1.3 / 2.2
p400 = 400e-6 * P0
b = theta / (1 - theta) / p400
dG = -R * 298.15 * math.log(b * P_REF)
dS_implied = (-54_000.0 - dG) / 298.15
print(f"  NbOFFIVE-1-Ni: fill {theta:.0%} at 400 ppm -> dG {dG/1e3:.1f} kJ/mol; with dH -54 kJ/mol the implied dS is {dS_implied:.0f} J/mol/K "
      f"(verifier default for amines: -165)")
for dS in (-165.0, -140.0, -117.0, -100.0):
    print(f"  dS {dS:>6.0f} J/mol/K: dH for half-fill at 420 ppm:  25 C {(dG_for_half_loading(P_CO2_AIR, 298.15)+298.15*dS)/1e3:6.1f} | "
          f"0 C {(dG_for_half_loading(P_CO2_AIR, 273.15)+273.15*dS)/1e3:6.1f} | -20 C {(dG_for_half_loading(P_CO2_AIR, 253.15)+253.15*dS)/1e3:6.1f} | "
          f"-40 C {(dG_for_half_loading(P_CO2_AIR, 233.15)+233.15*dS)/1e3:6.1f} kJ/mol")

print("\nH. Same ambient fill (65%), different enthalpy/entropy: what the swing costs (q_max 2 mol/kg, dry, no water)")
print(f"{'dH':>6}{'dS':>7}{'fill@25C':>10}{'T_des C to 20% @1kPa':>22}{'T_des C @100Pa':>16}{'heat GJ/t @1kPa':>17}{'work-eq GJ/t':>14}")
target = 0.65
for dH_kj in (-45, -54, -60, -70, -80):
    dH = dH_kj * 1e3
    bneed = target / (1 - target) / P_CO2_AIR
    dS = (dH + R * 298.15 * math.log(bneed * P_REF)) / 298.15
    t1 = desorption_temperature(dH, dS, 1.0e3); t2 = desorption_temperature(dH, dS, 1.0e2)
    cyc = TVSACycle(dH=dH, dS=dS, q_max=2.0, T_des=t1, p_des=1.0e3)
    print(f"{dH_kj:>6}{dS:>7.0f}{loading(P_CO2_AIR, 298.15, dH, dS, 1.0):>10.0%}{t1-273.15:>22.0f}{t2-273.15:>16.0f}{cyc.heat_gj_per_t:>17.2f}{cyc.work_equivalent_gj_per_t:>14.2f}")

print("\nI. Cold adsorption with a 13X-like site population: adsorb at -20 C, desorb at modest temperature")
# effective strong-site Langmuir anchored to Wilson's -20 C point: 1.1 mol/kg; take q_max 2.5 (strong-site population), dH -45 kJ/mol
dH = -45_000.0; qmax = 2.5; T_ads = 253.15
th = 1.1 / qmax
dS = (dH + R * T_ads * math.log(th / (1 - th) / P_CO2_AIR * P_REF)) / T_ads
print(f"  implied dS {dS:.0f} J/mol/K")
for tdes_c, pdes in [(25, 100.0), (60, 1000.0), (100, 1000.0), (200, 1000.0), (200, 10_000.0)]:
    cyc = TVSACycle(dH=dH, dS=dS, q_max=qmax, T_ads=T_ads, T_des=tdes_c + 273.15, p_des=pdes, cp_sorbent=920.0)
    if cyc.working_capacity > 0:
        print(f"  T_des {tdes_c:>4} C, p_des {pdes:>7.0f} Pa: working capacity {cyc.working_capacity:.2f} mol/kg, heat {cyc.heat_gj_per_t:.2f} GJ/t, "
              f"work-eq {cyc.work_equivalent_gj_per_t:.2f} GJ/t, 2nd-law eff {cyc.second_law_efficiency:.0%}")
    else:
        print(f"  T_des {tdes_c:>4} C, p_des {pdes:>7.0f} Pa: no working capacity")

print("\nJ. Bare carbon physisorption at 420 ppm (typical dH -25..-30 kJ/mol, dS about -85 J/mol/K, micropore capacity 5 mol/kg)")
for dH_kj in (-25, -30, -35):
    print(f"  dH {dH_kj} kJ/mol: {loading(P_CO2_AIR, 298.15, dH_kj*1e3, -85.0, 5.0):.4f} mol/kg at 25 C; "
          f"{loading(P_CO2_AIR, 253.15, dH_kj*1e3, -85.0, 5.0):.4f} at -20 C; {loading(P_CO2_AIR, 195.0, dH_kj*1e3, -85.0, 5.0):.3f} at 195 K")

print("\nK. Minimum separation work vs temperature (75% capture, 99% purity)")
for tc in (25, 0, -20, -40, -78):
    print(f"  {tc:>4} C: {gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99, tc + 273.15)):.2f} GJ/t")
