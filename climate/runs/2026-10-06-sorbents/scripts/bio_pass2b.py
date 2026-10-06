import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
GJ = gj_per_tonne
Rg = R
print("=== A/B addendum: where is CO2 hydration/dehydration chemistry slow enough to matter? (uncatalysed, per HCO3-)")
# k_OH' = k_OH*Kw/K1 ; Ea(k_OH) ~55 kJ/mol, dH(Kw) ~ +56 kJ/mol, dH(K1) ~ +9 kJ/mol -> apparent ~102 kJ/mol
# k_H'  = k_h*[H+]/K1 ; Ea(k_h) ~ 70 kJ/mol (hydration), minus dH(K1) 9 -> ~61 kJ/mol at fixed pH
def k_release(T, pH):
    f = lambda Ea: math.exp(-Ea / Rg * (1 / T - 1 / 298.15))
    return 1.9e-4 * f(102e3) + 0.037 * f(61e3) * 10**-pH / 10**-6.35
for T_C in (5, 25, 40, 60, 80, 100):
    T = T_C + 273.15
    k9, k10 = k_release(T, 9.0), k_release(T, 10.0)
    print(f"   {T_C:3d} C: k(pH 9) {k9:.1e} /s (t1/2 {math.log(2)/k9:7.0f} s), k(pH 10) {k10:.1e} /s (t1/2 {math.log(2)/k10:7.0f} s)")
print("   COF-999 humid desorption at 60 C took ~44 min for 80% -> not reaction-limited at 60 C (t1/2 ~1 min);"
      " moisture swing at 25-27 C sits where t1/2 ~ 40-60 min, the same order as the measured release LDF.")

print("\n=== E addendum: Mg bonus as mixed enthalpy/entropy (ddG = -4 kJ/mol at 25 C)")
for ddH, ddS in [(-4e3, 0.0), (-10e3, -20.1), (-16e3, -40.2)]:
    dH, dS = -66e3 + ddH, -165.0 + ddS
    fill = loading(P_CO2_AIR, T0, dH, dS, 1.0)
    cyc = TVSACycle(dH=dH, dS=dS, q_max=2.0, T_des=373.15, p_des=1e3, water_coads=2.0)
    print(f"   ddH {ddH/1e3:+.0f}, ddS {ddS:+.1f}: fill {fill:.0%}, T_des {desorption_temperature(dH, dS, 1e3)-273.15:.0f} C, "
          f"wc {cyc.working_capacity:.2f}, heat {cyc.heat_gj_per_t:.2f} GJ/t, work-eq {cyc.work_equivalent_gj_per_t:.2f}")

print("\n=== F. Wyman linkage (Bohr-type heterotropic coupling) in moisture-swing resins: linked vs unlinked water")
# d ln p50(CO2) / d ln a_w = n_w (waters released per CO2 bound). Minimum water per CO2 for a given pressure swing.
for a_dry, a_wet in [(0.20, 0.95), (0.20, 0.60), (0.30, 0.90), (0.15, 0.80)]:
    for swing in (100, 500):
        n_link = math.log(swing) / math.log(a_wet / a_dry)
        print(f"   RH {a_dry:.0%}->{a_wet:.0%}, equilibrium pCO2 x{swing}: linked water >= {n_link:.1f} mol/mol")
# measured: VMS IRA-900 water swing 23-24 mmol/g for 0.9-1.1 mmol/g CO2 (TGA 20<->95% RH); ASU liquid 244 mol/mol
for water, co2, label in [(23.5, 1.0, "IRA-900 vapour swing (Wade 2026)"), (21.0, 1.27, "IRA-900 20->50% RH (Lively 2025)"),
                          (244.0, 1.0, "A501 liquid wetting (ASU 2025, mol/mol)")]:
    ratio = water / co2
    print(f"   {label}: {ratio:.0f} mol H2O per mol CO2 -> linked share {3.0/ratio:.0%}-{4.0/ratio:.0%} if 3-4 waters are linked")
print("   latent heat moved by the water swing (ambient-supplied, recovered or lost), GJ/t:")
for ratio in (24, 12, 6, 4):
    print(f"     {ratio:3d} mol/mol: {GJ(moisture_swing_water_heat(ratio)):.1f} GJ/t latent; water mass {ratio*18/44:.1f} t/t")
# drying-limited cycle time scales with water to remove (if water transport out of resin limits)
print("   drying-limited cycle (2 h drying at 24 mol/mol, 3 h wetting): productivity vs water swing at 0.9 mmol/g")
for ratio in (24, 12, 6):
    t_dry = 2.0 * ratio / 24; t_wet = 3.0 * ratio / 24
    cpd = 24 / (t_dry + t_wet)
    print(f"     {ratio:2d} mol/mol: cycle {t_dry+t_wet:.2f} h, {cpd:.1f} cycles/day, {productivity(0.9, cpd):.2f} kg/kg/day, "
          f"resin $/t at $10/kg & 15,000 cycles {sorbent_cost_per_tonne(10, 0.9, 15000):.0f} (time-independent)")
