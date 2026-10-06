import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
from scipy.optimize import brentq
from scipy.integrate import quad

GJ = gj_per_tonne
kWh = lambda gj: gj * 277.78
floor_j = min_separation_work(X_AIR, 0.75, 0.99, T0)
ref = reference_amine_cycle()
print("=== 0. reference")
print(f"floor {floor_j/1e3:.1f} kJ/mol = {GJ(floor_j):.3f} GJ/t; ref heat {ref.heat_gj_per_t:.2f} GJ/t, wc {ref.working_capacity:.2f} mol/kg, "
      f"work-eq {ref.work_equivalent_gj_per_t:.2f} GJ/t, 2nd law {ref.second_law_efficiency:.0%}")

# ---------------------------------------------------------------------------------------------
print("\n=== IDEA 1. CA-mimic (Zn-cyclen) in a supported K2CO3 brine film: bicarbonate swing")
# thermochemistry (NIST-JANAF / CRC, kJ/mol): 2 KHCO3(s) -> K2CO3(s) + CO2(g) + H2O(g)
dHf = {"KHCO3": -963.2, "K2CO3": -1151.0, "CO2": -393.5, "H2Og": -241.8, "H2Ol": -285.8,
       "NaHCO3": -950.8, "Na2CO3": -1130.7}
dGf = {"KHCO3": -863.5, "K2CO3": -1063.5, "CO2": -394.4, "H2Og": -228.6, "H2Ol": -237.1,
       "NaHCO3": -851.0, "Na2CO3": -1044.4}
for M in ("K", "Na"):
    dH = dHf[M+"2CO3"] + dHf["CO2"] + dHf["H2Og"] - 2 * dHf[M+"HCO3"]
    dG = dGf[M+"2CO3"] + dGf["CO2"] + dGf["H2Og"] - 2 * dGf[M+"HCO3"]
    dGl = dGf[M+"2CO3"] + dGf["CO2"] + dGf["H2Ol"] - 2 * dGf[M+"HCO3"]
    dS = (dH - dG) / T0 * 1e3
    Tdec = dH * 1e3 / dS
    pco2_eq = math.exp(-dG * 1e3 / (R * T0)) / 0.015  # bar, at p_H2O = 0.015 bar (50% RH, 25 C)
    print(f"  {M}: decomposition dH {dH:.1f} kJ/mol, dG298 {dG:.1f} (H2O gas) / {dGl:.1f} (H2O liq), dS {dS:.0f} J/mol/K, "
          f"T(1 bar CO2 + 1 bar H2O) = {Tdec-273.15:.0f} C; equilibrium p_CO2 at 50% RH, 25 C = {pco2_eq*1e5:.2f} Pa (air: 42.6 Pa)")
    print(f"     effective capture free energy per CO2 at unit water activity: {-dGl:.1f} kJ/mol vs -19.2 needed; "
          f"min work of regeneration rxn = {dGl:.1f} kJ/mol = {GJ(dGl*1e3):.2f} GJ/t = {dGl*1e3/floor_j:.1f} x floor")
# cycle heat: Langmuir surrogate with dH = -140, dS chosen so dG298 = -32 (K, liquid water, 50% RH)
dH_K, dG_K = -140.1e3, -(40.5 - 8.5 + R*T0*math.log(0.5)/1e3) * 1e3   # liquid-water basis, 50% RH
dS_K = (dH_K - dG_K) / T0
print(f"  Langmuir surrogate: dH {dH_K/1e3:.0f}, dG298 {dG_K/1e3:.1f}, dS {dS_K:.0f} J/mol/K; fill at 420 ppm "
      f"{loading(P_CO2_AIR, T0, dH_K, dS_K, 1.0):.3f}; T_des(1 bar, 20% residual) {desorption_temperature(dH_K, dS_K, 1e5)-273.15:.0f} C")
print("  cycle heat at 150 C, release at 1 bar (steam-swept), cp 1000 J/kg/K; q_max = mol CO2/kg at given K2CO3 loading, 70% utilised")
for wt in (0.06, 0.20, 0.40):
    qmax = wt / 0.1382 * 1e3 * 0.70   # mol/kg: 1 CO2 per K2CO3 (138.2 g/mol)
    for wco in (0.0, 2.0, 5.0):
        c = TVSACycle(dH=dH_K, dS=dS_K, q_max=qmax, T_des=423.15, p_des=1e5, cp_sorbent=1000.0, water_coads=wco)
        print(f"    K2CO3 {wt:.0%} wt ({qmax:.2f} mol/kg), extra film water {wco:.0f} mol/mol: wc {c.working_capacity:.2f}, heat {c.heat_gj_per_t:.2f} GJ/t "
              f"(rxn {GJ(c.reaction_heat):.2f} incl. 1 H2O, sens {GJ(c.sensible_heat):.2f}, water {GJ(c.water_heat):.2f}); work-eq {c.work_equivalent_gj_per_t:.2f}; 2nd law {c.second_law_efficiency:.0%}")
# kinetics in the brine film: CO2 hydration rate constant vs conversion; film theory flux ~ sqrt(D k1)
kOH, kw, D = 8.4e3, 0.037, 1.9e-9
pK2 = 10.33
def pH_of(x):   # carbonate->bicarbonate conversion x of a 2 M K2CO3 brine (Henderson-Hasselbalch; activity ignored)
    x = min(max(x, 1e-4), 0.9999)
    return pK2 + math.log10((1 - x) / (2 * x)) if x < 1 else 7
def k1(x, kcat=0.0, conc=0.0):
    return kOH * 10 ** (pH_of(x) - 14) + kw + kcat * conc
for label, kcat, conc in (("uncatalysed", 0, 0), ("Zn-cyclen 0.05 M in film (k 3.3e3 /M/s)", 3.3e3, 0.05),
                          ("Zn-cyclen 0.2 M in film", 3.3e3, 0.2), ("hCA II 1 g/L (1.5e8 /M/s), for scale", 1.5e8, 1/30000)):
    t_rel = quad(lambda x: 1 / math.sqrt(D * k1(x, kcat, conc)), 0.0, 0.9)[0]
    print(f"  {label:<45} k1 at x=0.05: {k1(0.05,kcat,conc):7.1f} /s, at x=0.5: {k1(0.5,kcat,conc):7.1f} /s, at x=0.9: {k1(0.9,kcat,conc):7.1f} /s; "
          f"relative time to 90% conversion (film-limited) {t_rel:.3g}")
t0 = quad(lambda x: 1 / math.sqrt(D * k1(x)), 0.0, 0.9)[0]
for conc in (0.05, 0.2):
    t = quad(lambda x: 1 / math.sqrt(D * k1(x, 3.3e3, conc)), 0.0, 0.9)[0]
    print(f"  -> speed-up to 90% conversion with Zn-cyclen {conc} M: x{t0/t:.1f} (only if the brine-film hydration step is rate-limiting)")
print("  sorbent cost: K2CO3 ~$1/kg, carbon felt ~$5/kg -> composite ~$4/kg;",
      f"at 1.0 mol/kg: ${sorbent_cost_per_tonne(4, 1.0, 2000):.0f}/t at 2,000 cycles, ${sorbent_cost_per_tonne(4, 1.0, 20000):.0f}/t at 20,000; "
      f"Zn-cyclen at 0.3 wt% of composite and $2,000/kg adds ~${0.003*2000:.0f}/kg -> ${sorbent_cost_per_tonne(6, 1.0, 5000):.0f}/t at $10/kg-equiv, 5,000 cycles")

# ---------------------------------------------------------------------------------------------
print("\n=== IDEA 2. Carboxysome-style carbonate loop: CA in a K2CO3/KHCO3 contactor at pH 10.5-11 + 1 e-/CO2 proton-sponge release")
K1, K2, H = 4.45e-7, 4.69e-11, 0.034   # M, M, M/atm at 25 C
def pco2_atm(x, Ctot):   # carbonate->bicarbonate conversion x of Ctot M K2CO3 (ideal)
    hco3, co3 = 2 * x * Ctot, (1 - x) * Ctot
    hplus = K2 * hco3 / co3
    co2aq = hco3 * hplus / K1
    return co2aq / H, -math.log10(hplus)
for Ctot in (1.0, 2.0):
    xs = {}
    for frac in (0.1, 0.25, 0.5):
        x = brentq(lambda x: pco2_atm(x, Ctot)[0] - frac * 420e-6, 1e-6, 0.999)
        xs[frac] = x
        print(f"  {Ctot} M K2CO3: p_eq = {frac:.2f} x ambient at conversion {x:.3f} (pH {pco2_atm(x,Ctot)[1]:.2f}); loading {x*Ctot:.3f} mol CO2/L")
    wc = (xs[0.5] - xs[0.1]) * Ctot
    print(f"     cyclic loading between p_eq 0.1 and 0.5 x ambient: {wc:.3f} mol/L -> {1e6/M_CO2/1e3/wc/1e3:.0f} m3 liquor per t CO2 "
          f"(Keith 2018 KOH loop: ~0.25 mol/L)")
# contactor kinetics: K_L = sqrt(D k1); enzyme k_cat/K_M
for pH in (10.5, 11.0):
    k_un = kOH * 10 ** (pH - 14) + kw
    for name, kk in (("thermostable CA 1e7 /M/s", 1e7), ("hCA II 1.5e8 /M/s", 1.5e8)):
        for gL in (0.3, 1.0):
            E = gL / 30000.0
            kc = k_un + kk * E
            print(f"  pH {pH}: uncatalysed K_L {math.sqrt(D*k_un)*1e3:.3f} mm/s; + {gL} g/L {name}: K_L {math.sqrt(D*kc)*1e3:.2f} mm/s "
                  f"(x{math.sqrt(kc/k_un):.0f}); KOH contactor measured 1.3 mm/s")
# release: 1 e-/CO2 proton-sponge stage
for V, ce in ((0.3, 0.8), (0.4, 0.8), (0.6, 0.8)):
    w = electrochemical_work(1, V, ce)
    print(f"  release cell 1 e-/CO2 at {V} V, {ce:.0%} charge eff: {w/1e3:.0f} kJ/mol = {GJ(w):.2f} GJ_e/t = {kWh(GJ(w)):.0f} kWh/t")
dpH_floor = {3: 3*0.0592*FARADAY, 4: 4*0.0592*FARADAY}
for d, w in dpH_floor.items():
    print(f"  Nernst floor for a {d}-unit pH gap, 1 charge/CO2: {w/1e3:.0f} kJ/mol = {GJ(w):.2f} GJ/t")
fan = fan_work_gj_per_tonne(X_AIR, 0.75, 100.0)
pump = 151 * 3e5 / 0.7 / 1e9 * 1e3 / 1e3   # 151 m3/t at 3 bar, 70% pump eff -> GJ/t
comp = R * T0 * math.log(150.0 / 1.0) / 0.6   # crude isothermal 1 -> 150 bar at 60%
tot = 2.1 + fan + 0.065 + GJ(comp)
print(f"  measured anchor: PNAS 2026 MnO2 stage 2.1 GJ_e/t at 30 mA/cm2 on pH 8.9 bicarbonate. Add fans {fan:.2f} (100 Pa) + liquor pumping ~0.07 + compression {GJ(comp):.2f} "
      f"-> ~{tot:.1f} GJ_e/t = {kWh(tot):.0f} kWh/t; 2nd-law {GJ(floor_j)/tot:.0%}. KOH-calciner design: 8.81 GJ gas/t.")
for j in (10, 30, 100):
    tpm2 = j * 10 / FARADAY * 0.8 * 3.156e7 * M_CO2 / 1000   # A/m2 -> t CO2 / m2 / yr
    print(f"  cell at {j} mA/cm2, 1 e-/CO2, 80% CE: {tpm2:.2f} t CO2/m2/yr -> capital charge at $500/m2, 15%/yr: ${500*0.15/tpm2:.0f}/t")

# ---------------------------------------------------------------------------------------------
print("\n=== IDEA 3. Hydration-linked allosteric collapse (Hb water linkage): LCST polymer carrying the amine")
dH, dS = -70e3, -165.0
def dG_needed(T, p, theta):      # dG at which Langmuir loading = theta at (T, p)
    return -R * T * math.log(P_REF / p * theta / (1 - theta))
for Tdes in (323.15, 333.15, 343.15, 365.15):
    dG_site = dH - Tdes * dS
    need = dG_needed(Tdes, 1e3, 0.2)
    print(f"  T_des {Tdes-273.15:.0f} C: site dG {dG_site/1e3:.1f} kJ/mol; unloading to 20% at 1 kPa needs dG {need/1e3:.1f} -> collapse must weaken binding by "
          f"{(need-dG_site)/1e3:.1f} kJ/mol (Langmuir site alone unloads to 20% at {desorption_temperature(dH,dS,1e3)-273.15:.0f} C)")
# cooperativity from the transition: n monomers per CO2 site, demixing enthalpy per monomer
print("  apparent van't Hoff enthalpy near T_c if release is linked to a transition with n monomers x dH_tr per CO2:")
for n in (5, 10, 20):
    for dHtr in (4e3, 6e3):
        app = -dH + n * dHtr
        # width of a 90%->10% release window for a two-state (Hill-like) process with that enthalpy, centred at 333 K
        width = R * 333.15**2 * 2 * math.log(9) / app
        print(f"    n={n:>2}, dH_tr {dHtr/1e3:.0f} kJ/mol: apparent dH {app/1e3:.0f} kJ/mol, 90->10% window ~{width:.0f} K (Langmuir -70 kJ/mol: {R*333.15**2*2*math.log(9)/70e3:.0f} K); "
              f"transition heat {GJ(n*dHtr):.2f} GJ/t")
print("  heat budget, q_max 2 mol/kg, 420 ppm -> p_des 1 kPa (verifier Langmuir with a 6 kJ/mol collapse penalty applied as dH shift at T_des):")
base = TVSACycle(dH=dH, dS=dS, q_max=2.0, T_des=365.15, p_des=1e3, water_coads=6.0)
print(f"    conventional, 92 C, measured-like 6 mol H2O/mol CO2 co-desorbed: heat {base.heat_gj_per_t:.2f} GJ/t (water {GJ(base.water_heat):.2f})")
for Tdes, w in ((333.15, 6.0), (333.15, 2.0), (333.15, 1.0)):
    # emulate collapse: evaluate q_des with dH weakened by 6 kJ/mol (dS unchanged) at T_des; q_ads at 25 C with full dH
    q_ads = loading(P_CO2_AIR, T0, dH, dS, 2.0)
    q_des = loading(1e3, Tdes, dH + 6e3, dS, 2.0)
    wc = q_ads - q_des
    sens = 1500 * (Tdes - T0) / wc
    tr = 10 * 5e3   # 10 monomers x 5 kJ/mol transition heat per CO2
    heat = -dH + sens + w * DH_VAP_WATER + tr
    print(f"    collapse at {Tdes-273.15:.0f} C, {w:.0f} mol H2O evaporated/CO2 (rest expelled as liquid): wc {wc:.2f} mol/kg, heat {GJ(heat):.2f} GJ/t "
          f"(rxn {GJ(-dH):.2f}, sens {GJ(sens):.2f}, water {GJ(w*DH_VAP_WATER):.2f}, transition {GJ(tr):.2f}); exergy of heat at {Tdes-273.15:.0f} C: {GJ(heat*(1-T0/Tdes)):.2f} GJ/t")

# ---------------------------------------------------------------------------------------------
print("\n=== IDEA 4. Hb carbamate salt bridge: primary amine + co-tethered guanidinium proton acceptor (1:1 stoichiometry)")
for qmax, lab in ((2.0, "reference PEI-like, 0.17 CO2/N at ~12 mmol N/g -> q_max 2"), (4.0, "1:1 site pair at 8 mmol N/g (4 sites/g) -> q_max 4"),
                  (3.0, "arginine on silica 3 mmol Arg/g, 1 CO2 per Arg -> q_max 3")):
    c = TVSACycle(dH=-72e3, dS=-165.0, q_max=qmax, T_des=373.15, p_des=1e3, water_coads=2.0)
    print(f"  {lab}: wc {c.working_capacity:.2f} mol/kg, heat {c.heat_gj_per_t:.2f} GJ/t (sens {GJ(c.sensible_heat):.2f}); "
          f"sorbent $/t at $20/kg: {sorbent_cost_per_tonne(20, c.working_capacity, 5000):.0f} (5,000 cycles)")
print("  binding window the pair must land in (dS -165): dH -66 -> fill", f"{loading(P_CO2_AIR,T0,-66e3,-165,1):.0%};",
      "-72 ->", f"{loading(P_CO2_AIR,T0,-72e3,-165,1):.0%};", "-78 ->", f"{loading(P_CO2_AIR,T0,-78e3,-165,1):.0%};",
      f"T_des at 1 kPa: {desorption_temperature(-66e3,-165,1e3)-273.15:.0f} / {desorption_temperature(-72e3,-165,1e3)-273.15:.0f} / {desorption_temperature(-78e3,-165,1e3)-273.15:.0f} C")
print("  risk: guanidinium bicarbonate/carbonate (BIG-type) over-binding; ORNL crystals need 3.4-9.6 GJ/t mostly hydrate water -> falsify if >2 H2O/CO2 or T_des(1 kPa) > 120 C")

# ---------------------------------------------------------------------------------------------
print("\n=== IDEA 5. Protein-turnover analogue: dynamic-covalent anchored amine, refurbished in place")
wc = ref.working_capacity   # 1.04 mol/kg
for amine_life in (3000, 5000, 10000):
    full = sorbent_cost_per_tonne(20, wc, amine_life)
    # refurbish: amine + solvent + labour ~$4/kg-sorbent per refurbish; support ($14/kg share) lasts 10 refurbishes
    refurb = sorbent_cost_per_tonne(4, wc, amine_life) + sorbent_cost_per_tonne(14, wc, 10 * amine_life)
    refurb5 = sorbent_cost_per_tonne(4, wc, amine_life) + sorbent_cost_per_tonne(14, wc, 5 * amine_life)
    print(f"  amine life {amine_life} cycles: replace whole sorbent at $20/kg: ${full:.0f}/t; refurbish at $4/kg, support 10 lives: ${refurb:.0f}/t; support 5 lives: ${refurb5:.0f}/t")
print(f"  structured laminate at $50/kg (Svante-class guess), 5,000-cycle amine life: replace ${sorbent_cost_per_tonne(50, wc, 5000):.0f}/t vs refurbish "
      f"${sorbent_cost_per_tonne(4, wc, 5000) + sorbent_cost_per_tonne(46, wc, 50000):.0f}/t")
print("  break-even: refurbishment pays whenever (refurbish $/kg) < (sorbent $/kg) x (1 - 1/N_support_lives); at $20/kg and 10 lives, up to $18/kg")

# ---------------------------------------------------------------------------------------------
print("\n=== IDEA 6. Catalytic antioxidant + chelator resupply via regeneration steam (SOD-mimic / metallothionein analogue)")
steam_kg_per_kg = 2.0 * 18.015 / 44.01   # 2 mol H2O per mol CO2 (reference) -> kg water per kg CO2
for conc_mM, name, price in ((0.1, "TEMPOL", 200.0), (1.0, "TEMPOL", 200.0), (0.5, "DTPA/HEDP chelator", 5.0)):
    mol_per_t = conc_mM * 1e-3 * steam_kg_per_kg * 1000  # mol per t CO2 (1 L per kg water)
    kg_per_t = mol_per_t * 0.172 if "TEMPOL" in name else mol_per_t * 0.39
    per_cycle_umol_per_kg = conc_mM * 1e-3 * steam_kg_per_kg * (wc * M_CO2) * 1e6   # umol deposited per kg sorbent per cycle
    print(f"  {name} at {conc_mM} mM in {steam_kg_per_kg:.2f} kg condensate/kg CO2: {kg_per_t:.2f} kg/t CO2 = ${kg_per_t*price:.1f}/t at ${price:.0f}/kg; "
          f"deposit {per_cycle_umol_per_kg:.1f} umol/kg sorbent/cycle -> {per_cycle_umol_per_kg*1e4/1e3:.0f} mmol/kg after 10,000 cycles if nothing leaves")
print("  Min et al. 2018 used 2 wt% trisodium phosphate (~50 mmol/kg) with no capacity penalty; Guta 2025 optimum additive 2 mol% of N (~240 mmol/kg at 12 mmol N/g)")
for fade in (2.3e-3, 1.1e-3, 5e-4):
    cyc = 0.2 / (fade / 100)
    print(f"  fade {fade:.1e} %/cycle -> 20% loss after {cyc:,.0f} cycles -> sorbent $/t at $20/kg: {sorbent_cost_per_tonne(20, wc, cyc):.0f}")
print("  Guta 2023 baseline for the cheap test: 30 cycles at 70 C in humid 0.04% CO2-air lost 48-52% (unprotected PEI/Al2O3); pre-stated pass: <=15% with dosing, fail: >=35%")
