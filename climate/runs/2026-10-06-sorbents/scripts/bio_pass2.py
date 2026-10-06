import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
# Generation pass 2 (Opus 5.5), biology single-graft ideas. Screening arithmetic only.
import math
from scipy.optimize import brentq

GJ = gj_per_tonne
floor = GJ(min_separation_work(X_AIR, 0.75, 0.99, T0))
ref = reference_amine_cycle()
print("=== 0. Reference (verifier)")
print(f"floor {floor:.3f} GJ/t; ref wc {ref.working_capacity:.3f} mol/kg, heat {ref.heat_gj_per_t:.2f} GJ/t "
      f"(rxn {GJ(ref.reaction_heat):.2f}, sens {GJ(ref.sensible_heat):.2f}, water {GJ(ref.water_heat):.2f}), "
      f"work-eq {ref.work_equivalent_gj_per_t:.2f}, 2nd-law {ref.second_law_efficiency:.0%}")

def cycle_with_wc(wc_target, water_per_co2, dH=-70e3, dS=-165.0, T_des=373.15, p_des=1e3,
                  inert=0.0, recovery=0.0):
    """Verifier TVSACycle whose q_max is scaled so the working capacity equals wc_target."""
    unit = TVSACycle(dH=dH, dS=dS, q_max=1.0, T_des=T_des, p_des=p_des).working_capacity
    return TVSACycle(dH=dH, dS=dS, q_max=wc_target / unit, T_des=T_des, p_des=p_des,
                     water_coads=water_per_co2, inert_mass_ratio=inert, heat_recovery=recovery)

# ------------------------------------------------------------------------------------------
print("\n=== A. Red-cell carbonic anhydrase in a moisture-swing (quaternary ammonium) resin")
# Uncatalysed CO2/HCO3- interconversion, 25 C (literature constants: k_h 0.037 /s, k_OH 8.5e3 /M/s, pK1 6.35)
k_h, k_OH, K1, Kw = 0.037, 8.5e3, 10**-6.35, 1e-14
for Ea_label, Ea_h, Ea_oh in [("25 C", 0, 0)]:
    pass
print(" uncatalysed first-order release rate per HCO3- (HCO3- -> CO2), 25 C:")
for pH in (8.5, 9.0, 9.5, 10.0, 10.5):
    H = 10**-pH
    k_dOH = k_OH * Kw / K1          # HCO3- -> CO2 + OH-   (pH independent)
    k_dH = k_h * H / K1             # HCO3- + H+ -> CO2 + H2O
    k = k_dOH + k_dH
    print(f"   pH {pH:4.1f}: k = {k:.2e} /s  (t1/2 {math.log(2)/k/60:5.1f} min); OH-path {k_dOH:.1e}, H-path {k_dH:.1e}")
k_unc = k_OH * Kw / K1 + k_h * 10**-9.5 / K1
print(f" measured IRA-900 LDF coefficients (Wade 2026, TGA, 400 ppm, 25 C): wetting/release 4.5e-4 /s, drying/capture 14e-4 /s")
print(f"   -> release LDF is {4.5e-4/k_unc:.1f}x the uncatalysed intrinsic dehydration rate at pH 9.5; capture is {14e-4/4.5e-4:.1f}x faster than release")
# Catalysed: Haldane, (kcat/KM)_dehyd = (kcat/KM)_hyd * [H+]/K1 ; CA II (kcat/KM)_hyd ~1.2e8 /M/s at pH>8
for conc_uM in (0.3, 1, 3, 10, 34):
    for pH in (9.0, 10.0):
        kd = 1.2e8 * 10**-pH / K1 * conc_uM * 1e-6
        print(f"   CA II {conc_uM:5.1f} uM in hydrated phase, pH {pH}: catalysed release k = {kd:.2e} /s ({kd/k_unc:,.0f}x uncatalysed)")
print("   (1 mg CA II per g resin in ~1 mL sorbed water = 34 uM; 0.1 mg/g = 3.4 uM)")
# Cycle-time consequence: Wade 2026 measured 0.9 mmol/g on ~2 h drying and ~3 h wetting.
for t_dry, t_wet, label in [(2.0, 3.0, "measured (uncatalysed)"), (2.0, 1.0, "release made capture-limited (k 14e-4)"),
                            (2.0, 1.5, "half the release time")]:
    cpd = 24.0 / (t_dry + t_wet)
    prod = productivity(0.9, cpd)
    print(f"   cycle {t_dry}+{t_wet} h = {cpd:.1f} cycles/day: {prod:.3f} kg CO2/kg/day ({label}); "
          f"sorbent inventory {1000/365/prod:.1f} kg per t/yr")
t90 = math.log(10) / 14e-4 / 3600
print(f"   t90 at k = 14e-4 /s: {t90:.2f} h; at 4.5e-4 /s: {math.log(10)/4.5e-4/3600:.2f} h")
for price, wc, cyc in [(10, 0.9, 3000), (10, 0.9, 15000), (54, 0.675, 15000)]:
    print(f"   resin cost ${price}/kg, wc {wc}, {cyc} cycles: ${sorbent_cost_per_tonne(price, wc, cyc):.0f}/t")
for enz_price in (50, 500):
    for load_mg in (0.1, 1.0):
        per_kg = enz_price * load_mg / 1000
        # enzyme replaced each time resin is replaced (worst) or every 1000 cycles
        per_t_1000 = per_kg / (0.9 * M_CO2 * 1000) * 1000
        print(f"   CA at ${enz_price}/kg protein, {load_mg} mg/g: ${per_kg:.3f} per kg resin; if re-dosed every 1,000 cycles: ${per_t_1000:.2f}/t CO2")

# ------------------------------------------------------------------------------------------
print("\n=== B. Zn(II)-polyamine CA-mimic sites in humid supported PEI: unlocking the slow bicarbonate route")
# (1) equilibrium bicarbonate share at 420 ppm in a hydrated PEI phase (ideal-solution, order of magnitude)
H_CO2 = 0.034  # M/atm, water at 25 C
p_atm = X_AIR
N_T = 15.0     # mol N per L of PEI phase (pure PEI ~23 M; diluted by water/void)
def speciate(Kc, Kb, aw):
    """Solve carbamate (2Am + CO2 = C- + AmH+) and bicarbonate (Am + CO2 + H2O = AmH+ + HCO3-) equilibria.
    Kc in 1/(M atm) for [C][AmH]/([Am]^2 p) ; Kb in M/atm for [AmH][HCO3]/([Am] p aw)."""
    def f(x):  # x = free amine
        # unknowns: C, B (bicarb). AmH = C + B. C*(C+B) = Kc x^2 p ; B*(C+B) = Kb x p aw
        r = Kc * x**2 * p_atm; s = Kb * x * p_atm * aw
        tot = math.sqrt(r + s)           # (C+B)^2 = r + s
        C, B = r / tot, s / tot
        return x + 2 * C + B - N_T, C, B
    x = brentq(lambda x: f(x)[0], 1e-12, N_T)
    _, C, B = f(x)
    return C, B, x
# calibrate Kc to a dry amine efficiency of 0.15 CO2/N at 420 ppm (laminate PEI 35 C: 0.12-0.17)
Kc = brentq(lambda K: speciate(K, 0.0, 0.0)[0] / N_T - 0.15, 1e-6, 1e6)
print(f" Kc calibrated to 0.15 CO2/N dry at 420 ppm: {Kc:.3g} /(M atm)")
for pKa in (9.0, 9.5, 10.0, 10.5):
    Kb = H_CO2 * K1 / 10**-pKa
    for aw in (0.3, 0.5, 0.8):
        C, B, x = speciate(Kc, Kb, aw)
        # sorbent with 45 wt% PEI, PEI phase density ~1.05 kg/L incl. water ~ 1 L per 1.05 kg PEI
        per_kg_sorbent = lambda m: m / 1.05 * 0.45
        print(f"   pKa_eff {pKa}, a_w {aw}: carbamate {C/N_T:.3f}/N, bicarbonate {B/N_T:.3f}/N "
              f"-> total {(C+B)/N_T:.3f} CO2/N; bicarbonate = {per_kg_sorbent(B):.2f} mol/kg sorbent (45 wt% PEI)")
# (2) rates: free CO2 in the hydrated amine phase is at most Henry-equilibrium with 42 Pa
C_free = H_CO2 * p_atm
print(f" free CO2 at 420 ppm (Henry, aqueous-like): {C_free:.2e} M")
paths = {"water (k_h)": k_h, "OH- at pH 10 (1e-4 M)": k_OH * 1e-4,
         "tertiary-amine base catalysis (~7 /M/s x 4 M)": 7 * 4,
         "Zn-polyamine mimic 0.1 M x 700 /M/s": 0.1 * 700, "Zn-polyamine mimic 0.3 M x 700 /M/s": 0.3 * 700,
         "CA II 10 uM x 1.2e8 /M/s": 10e-6 * 1.2e8}
for name, k1 in paths.items():
    rate = k1 * C_free  # M/s of bicarbonate formed
    t_half_mol = 0.25 / rate  # time to form 0.25 M bicarbonate in PEI phase (~0.1 mol/kg sorbent)
    print(f"   {name:45s}: k1 {k1:9.3g} /s -> {rate:.2e} M/s; 0.25 M bicarbonate in {t_half_mol/60:8.1f} min")
print("   (uncatalysed sum ~ k_h + OH- + base ~ 29 /s: ~10 min per 0.25 M; mimic at 0.3 M Zn: ~1.2 min)")
# Zn cost and amine tie-up
for zn_per_N in (0.005, 0.01, 0.02):
    zn_mol_per_kg = zn_per_N * 0.45 * 23.2  # PEI ~23.2 mmol N/g
    print(f"   Zn/N {zn_per_N:.3f}: {zn_mol_per_kg*1000:.0f} mmol Zn/kg sorbent, ties up ~{3*zn_per_N:.1%} of N (3 N per Zn); "
          f"Zn mass {zn_mol_per_kg*65.4:.1f} g/kg; Zn salt cost ~${zn_mol_per_kg*0.2*3:.2f}/kg sorbent at $3/kg salt")
# (3) energy and productivity consequence with the verifier
print(" energy per tonne if catalysis converts slow bicarbonate into within-cycle capacity (water swing fixed per kg):")
base_wc = 0.60
water_swing = 6.0 * base_wc  # mol H2O/kg cycled, from the measured 6-8 mol/mol at ~0.6 mol/kg
for dwc in (0.0, 0.1, 0.2, 0.3):
    wc = base_wc + dwc
    w = water_swing / wc
    cyc = cycle_with_wc(wc, w, inert=0.5)
    print(f"   wc {wc:.2f} mol/kg, water {w:.1f} mol/mol: heat {cyc.heat_gj_per_t:5.2f} GJ/t (sens {GJ(cyc.sensible_heat):.2f}, "
          f"water {GJ(cyc.water_heat):.2f}); work-eq {cyc.work_equivalent_gj_per_t:.2f}; productivity at 36 cycles/day "
          f"{productivity(wc, 36):.2f} kg/kg/day; sorbent $/t at $20/kg, 10,000 cycles {sorbent_cost_per_tonne(20, wc, 10000):.0f}")

# ------------------------------------------------------------------------------------------
print("\n=== C. Ligase-like reductive re-amination: repairing C-N cleavage products in oxidised PEI")
# Damage arithmetic: each C-N cleavage turns a secondary amine into a primary amine + aldehyde fragment;
# condensation of the aldehyde with a nearby primary amine gives an imine (C=N) that is non-capturing at 420 ppm.
# Reductive amination reduces the imine to a secondary amine, re-joining the fragments.
for dq in (0.1, 0.2, 0.3):  # capacity lost, mol CO2/kg
    sites = 2 * dq            # basic N lost (2 N per CO2 for dry carbamate)
    nabh4_kg = sites / 4 * 0.03783 * 3   # 4 hydride per BH4-, 3x excess, kg NaBH4 per kg sorbent
    for nab_price in (20, 40):
        print(f"   capacity lost {dq:.1f} mol/kg -> {sites:.1f} mol imine/carbonyl sites/kg; NaBH4 (3x excess) {nabh4_kg*1000:.1f} g/kg "
              f"= ${nabh4_kg*nab_price:.2f}/kg sorbent per repair at ${nab_price}/kg")
print(" sorbent replacement cost vs repairable fraction rho (life multiplied by 1/(1-rho)); repair every time 10% capacity is lost:")
for price in (20, 50):
    for wc in (1.04, 0.6):
        base_cycles = 5000
        row = []
        for rho in (0.0, 0.3, 0.5, 0.7):
            life = base_cycles / (1 - rho)
            n_rep = rho > 0 and (life / (base_cycles / 2) - 1) or 0  # repairs at each 10% loss of a 20% budget
            reagent = 0.30 * n_rep  # $/kg per repair incl. wash, see above (0.2 mol/kg case at $20-40/kg ~ $0.11-0.23; take $0.30 with labour-free wash)
            cost = (price + reagent) / (wc * M_CO2 * life) * 1000
            row.append(f"rho {rho:.1f}: ${cost:5.1f}/t")
        print(f"   ${price}/kg, wc {wc}: " + "; ".join(row))
print("   fade budget: 20% over 5,000 cycles = 4.0e-3 %/cycle (TDA/GE measured 2.2e-3, Climeworks Gen2 target 3.5e-3);"
      " rho 0.5 halves the effective irreversible rate to 2.0e-3")

# ------------------------------------------------------------------------------------------
print("\n=== D. Myoglobin-style facilitated diffusion: a mobile CO2 carrier inside pore-filling PEI")
# Wyman/Scholander: J = (D_CO2 dC_free + D_c dq_c)/L; facilitation factor F = 1 + D_c*q_c/(D_CO2*C_free)
for p_ppm in (420, 4000, 100000):
    C_free = H_CO2 * p_ppm * 1e-6 * 2.0   # amine phase solubility ~2x water (organic), M
    for Dc, qc in [(1e-12, 0.5), (1e-13, 0.5), (1e-12, 0.2)]:
        D_CO2 = 1e-10
        Fac = 1 + Dc * qc / (D_CO2 * C_free)
        print(f"   pCO2 {p_ppm:6d} ppm: C_free {C_free:.1e} M; carrier D {Dc:.0e} m2/s, bound {qc} M -> F = {Fac:7.1f}")
# shrinking-core time to load a PEI domain of thickness L (slab), q = 1.5 M bound
for L_um in (0.5, 1, 2, 5):
    L = L_um * 1e-6
    for Deff_label, Dfree, F in [("free CO2 only", 1e-10, 1.0), ("carrier F=10", 1e-10, 10.0), ("carrier F=50", 1e-10, 50.0)]:
        Cf = H_CO2 * X_AIR * 2.0
        t = 1.5 * L**2 / (2 * Dfree * F * Cf)
        print(f"   L {L_um:3.1f} um, {Deff_label:14s}: front reaches centre in {t/60:9.1f} min")
print(" productivity/heat consequence (verifier): fast-cycle use of equilibrium capacity 1.0 mol/kg")
for frac, cpd in [(0.6, 24), (0.85, 24), (0.6, 36), (0.85, 36)]:
    wc = 1.0 * frac
    cyc = cycle_with_wc(wc, 6.0 * 0.6 / wc, inert=0.5)
    print(f"   used fraction {frac:.2f} at {cpd} cycles/day: wc {wc:.2f}, productivity {productivity(wc, cpd):.2f} kg/kg/day, heat {cyc.heat_gj_per_t:.2f} GJ/t")

# ------------------------------------------------------------------------------------------
print("\n=== E. RuBisCO-style Mg2+-stabilised carbamate to rescue oxidation-resistant (weaker) amines")
dS = -165.0
for dH_kj in (-60, -63, -66, -70):
    dH = dH_kj * 1e3
    fill = loading(P_CO2_AIR, T0, dH, dS, 1.0)
    cyc = TVSACycle(dH=dH, dS=dS, q_max=2.0, T_des=373.15, p_des=1e3, water_coads=2.0)
    wc = cyc.working_capacity
    s = f"   dH {dH_kj} kJ/mol (dS -165): fill at 420 ppm {fill:.0%}, wc(100 C, 1 kPa) {wc:.2f} mol/kg"
    if wc > 0:
        s += f", heat {cyc.heat_gj_per_t:.2f} GJ/t"
    print(s)
print(" Mg2+ pairing as a free-energy bonus ddG on the carbamate (entropy unchanged) for an epoxide-PEI-like site at -66 kJ/mol:")
for ddG in (0, -2, -4, -6, -8):
    dH = -66e3 + ddG * 1e3  # treat as enthalpic bonus (conservative for T_des)
    fill = loading(P_CO2_AIR, T0, dH, dS, 1.0)
    cyc = TVSACycle(dH=dH, dS=dS, q_max=2.0, T_des=373.15, p_des=1e3, water_coads=2.0)
    tdes = desorption_temperature(dH, dS, 1e3) - 273.15
    wc = cyc.working_capacity
    print(f"   ddG {ddG:+d} kJ/mol -> fill {fill:.0%}, T_des(20% residual, 1 kPa) {tdes:.0f} C, wc {wc:.2f} mol/kg, "
          f"heat {cyc.heat_gj_per_t if wc>0 else float('nan'):.2f} GJ/t, sorbent $/t at $20/kg & 10,000 cycles "
          f"{sorbent_cost_per_tonne(20, wc, 10000) if wc>0 else float('nan'):.0f}")
print(" Mg dose: 1 Mg per 2 carbamates; to cover 0.5 mol/kg carbamate needs 0.25 mol Mg/kg = 6 g Mg/kg; as Mg acetate tetrahydrate"
      f" {0.25*0.2145*1000:.0f} g/kg (~${0.25*0.2145*2:.2f}/kg at $2/kg)")
