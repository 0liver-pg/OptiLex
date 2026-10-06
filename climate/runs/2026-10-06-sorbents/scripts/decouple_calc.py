import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
from scipy.optimize import brentq

GJ = gj_per_tonne
F = FARADAY
floor_j = min_separation_work(X_AIR, 0.75, 0.99, T0); floor = GJ(floor_j)
FAN100 = fan_work_gj_per_tonne(X_AIR, 0.75, 100.0)

def psat(T):
    """Water saturation pressure, Pa (IAPWS Wagner equation)."""
    Tc, pc = 647.096, 22.064e6
    tau = 1 - T / Tc
    a = (-7.85951783, 1.84408259, -11.7866497, 22.6807411, -15.9618719, 1.80122502)
    s = a[0]*tau + a[1]*tau**1.5 + a[2]*tau**3 + a[3]*tau**3.5 + a[4]*tau**4 + a[5]*tau**7.5
    return pc * math.exp(Tc / T * s)

def T_dew(p):
    return brentq(lambda T: psat(T) - p, 200.0, 640.0)

def vac_work(p_des, T=T0, eff=0.7):
    return R * T * math.log(P0 / p_des) / eff if p_des < P0 else 0.0

def workeq(heat_j, T_des, p_des):
    return GJ(heat_j * (1 - T0 / T_des) + vac_work(p_des)) + FAN100

print("=== 0. Reference reproduction")
ref = reference_amine_cycle()
print(f"ref: wc {ref.working_capacity:.2f} mol/kg, heat {ref.heat_gj_per_t:.2f} GJ/t, work-eq {ref.work_equivalent_gj_per_t:.2f}, eta {ref.second_law_efficiency:.0%}; floor {floor:.3f} GJ/t ({floor_j/1e3:.1f} kJ/mol); fan(100 Pa) {FAN100:.2f} GJ/t")
print(f"check psat: 25 C {psat(298.15):.0f} Pa, 60 C {psat(333.15)/1e3:.1f} kPa, 100 C {psat(373.15)/1e3:.1f} kPa")

print("\n=== 1. ENTROPY-STEEP STEP: step pressure 10 Pa at 25 C (capture ceiling 1-10/42.5 = 76%), vary dS")
print("   dH chosen so that dG(25 C) = -RT ln(P_REF/10 Pa); T_des = T at which p_step = p_des; wc = 0.9 q_max")
print(f"{'dS':>6}{'dH kJ':>8}{'T@1kPa':>8}{'T@10kPa':>9}{'T@1atm':>8}{'cap35C':>8}{'cap45C':>8}{'heat2':>7}{'weq2':>6}{'eta2':>6}{'heat6':>7}{'weq6':>6}{'eta6':>6}")
p_step25 = 10.0
rows1 = {}
for dS in (-165.0, -200.0, -250.0, -300.0, -350.0, -400.0):
    dH = T0 * dS - R * T0 * math.log(P_REF / p_step25)
    Ts = [dH / (dS - R * math.log(P_REF / p)) for p in (1e3, 1e4, P0)]
    caps = []
    for Tc in (308.15, 318.15):
        pstep = P_REF * math.exp((dH - Tc * dS) / (R * Tc))
        caps.append(max(0.0, 1 - pstep / P_CO2_AIR))
    out = [f"{dS:>6.0f}{dH/1e3:>8.1f}{Ts[0]-273.15:>8.0f}{Ts[1]-273.15:>9.0f}{Ts[2]-273.15:>8.0f}{caps[0]:>8.0%}{caps[1]:>8.0%}"]
    T_des = Ts[0]
    for qmax in (2.0, 6.0):
        wc = 0.9 * qmax
        heat = -dH + 1500.0 * (T_des - T0) / wc
        we = workeq(heat, T_des, 1e3)
        out.append(f"{GJ(heat):>7.2f}{we:>6.2f}{floor/we:>6.0%}")
        rows1[(dS, qmax)] = (dH, T_des, heat, we)
    print("".join(out))
print("   (heatN / weqN / etaN = heat GJ/t, work-equivalent GJ/t, second-law efficiency for q_max = N mol/kg; dry, no water, no inert mass)")
# exergy split for dS=-300, q=6
dH, T_des, heat, we = rows1[(-300.0, 6.0)]
print(f"   dS -300, q 6: reaction {GJ(-dH):.2f} + sensible {GJ(heat + dH):.2f} = {GJ(heat):.2f} GJ/t at {T_des-273.15:.0f} C; "
      f"heat exergy {GJ(heat*(1-T0/T_des)):.2f}, vacuum {GJ(vac_work(1e3)):.2f}, fan {FAN100:.2f} GJ/t")
# melting kink
print("   Melting kink: an amine that melts at T_m just above adsorption T steepens the release curve above T_m by dH_fus")
dS1, dHfus, Tm = -250.0, 20e3, 318.15
dH1 = T0 * dS1 - R * T0 * math.log(P_REF / p_step25)
dSfus = dHfus / Tm
dH2, dS2 = dH1 - dHfus, dS1 - dSfus
T_no = dH1 / (dS1 - R * math.log(P_REF / 1e3)); T_kink = dH2 / (dS2 - R * math.log(P_REF / 1e3))
print(f"   dS -250: T@1kPa without melting {T_no-273.15:.0f} C; with amine melting at 45 C (dH_fus 20 kJ/mol): {T_kink-273.15:.0f} C")
# TriH check
print("   TriH check: if release at 105 C under N2 purge were thermodynamic (dS -300), implied step pressure at 25 C:")
for p_purge in (10.0, 100.0, 1000.0):
    dHx = 378.15 * (-300.0 - R * math.log(P_REF / p_purge))
    pst = P_REF * math.exp((dHx - T0 * (-300.0)) / (R * T0))
    print(f"     p_CO2 during purge {p_purge:>5.0f} Pa -> dH {dHx/1e3:.0f} kJ/mol, p_step(25 C) = {pst:.2e} Pa ({pst/P0*1e6:.3f} ppm)")

print("\n=== 2. HUMIDITY ('Bohr') TRIGGER on tethered-amine bicarbonate sites: R-NH2 + CO2 + H2O(g) <-> salt")
print("   theta/(1-theta) = K p_CO2 p_H2O; dH_tot chosen for theta = 0.75 at 42.5 Pa CO2, 50% RH, 25 C; release endpoint theta = 0.20")
pH2O_amb = 0.5 * psat(T0)
desic = [("ambient 50%RH 25C", pH2O_amb), ("arid 15%RH 30C", 0.15 * psat(303.15)), ("CaCl2 ~30%RH", 0.30 * psat(T0)),
         ("LiCl ~11%RH", 0.11 * psat(T0)), ("silica gel ~5%RH", 0.05 * psat(T0)), ("3A zeolite ~13 Pa", 13.0)]
for dS_tot in (-250.0, -285.0, -320.0):
    K_need = 3.0 / (P_CO2_AIR * pH2O_amb)  # theta 0.75
    dG25 = -R * T0 * math.log(K_need * P_REF**2)
    dH_tot = dG25 + T0 * dS_tot
    print(f"  dS_tot {dS_tot:.0f} J/mol/K -> dH_tot {dH_tot/1e3:.1f} kJ/mol (dG25 {dG25/1e3:.1f}); p_CO2,eq at theta=0.2 [kPa]:")
    hdr = f"{'':>22}" + "".join(f"{tc:>8}C" for tc in (25, 40, 50, 60))
    print(hdr)
    for name, pw in desic:
        vals = []
        for tc in (25, 40, 50, 60):
            T = tc + 273.15
            K = math.exp(-(dH_tot - T * dS_tot) / (R * T)) / P_REF**2
            pco2 = 0.25 / (K * pw)
            vals.append(pco2 / 1e3)
        print(f"{name:>22}" + "".join(f"{v:>9.2f}" for v in vals))
# energy for dS -285 at 50 C with silica-gel loop
dS_tot = -285.0; K_need = 3.0 / (P_CO2_AIR * pH2O_amb); dG25 = -R * T0 * math.log(K_need * P_REF**2); dH_tot = dG25 + T0 * dS_tot
T = 323.15; K = math.exp(-(dH_tot - T * dS_tot) / (R * T)) / P_REF**2; pco2 = 0.25 / (K * 0.05 * psat(T0))
wc = 1.1  # mol/kg humid-extra capacity (COF-999 2.05-0.96)
sens = 1500.0 * (T - T0) / wc
water_through_desiccant = 2.4  # mol H2O per mol CO2 (stoichiometric 1 + ~1.4 physisorbed, COF-999 0.09 g/g at 50% RH)
desic_heat = water_through_desiccant * (DH_VAP_WATER + 10e3 + 15e3)  # latent + excess binding + desiccant sensible, per mol H2O
comp = R * T0 * math.log(P0 / pco2) / 0.7
print(f"  Energy, dS -285, 50 C, silica-gel loop (p_H2O 80 Pa): p_CO2 {pco2/1e3:.1f} kPa; amine side: reaction {GJ(-dH_tot):.2f} + sensible {GJ(sens):.2f} = {GJ(-dH_tot+sens):.2f} GJ/t at 50 C (exergy {GJ((-dH_tot+sens)*(1-T0/T)):.2f});")
print(f"    desiccant regeneration ~{GJ(desic_heat):.2f} GJ/t at 90-120 C (exergy {GJ(desic_heat*(1-T0/393.15)):.2f} at 120 C); compression from {pco2/1e3:.1f} kPa {GJ(comp):.2f} GJ/t; fan {FAN100:.2f}")
tot_we = GJ((-dH_tot+sens)*(1-T0/T) + desic_heat*(1-T0/393.15) + comp) + FAN100
print(f"    total heat {GJ(-dH_tot+sens+desic_heat):.2f} GJ/t (all <=120 C), work-eq {tot_we:.2f} GJ/t, second-law {floor/tot_we:.0%}; with LiCl liquid desiccant regenerated at 70 C: exergy of desiccant heat {GJ(desic_heat*(1-T0/343.15)):.2f}")
print(f"  Cross-check Clausius-Clapeyron factor 25->50 C for dH_tot {dH_tot/1e3:.0f}: x{math.exp(-dH_tot/R*(1/T0-1/T)):.0f}; humidity factor 1584->80 Pa: x{pH2O_amb/80:.0f}")

print("\n=== 3. REDOX-GATED AMINE: mV of binding-free-energy shift that substitute for degrees")
print("   site dS -165; need dG_req(T) = -RT ln(0.25 * P_REF/1 kPa) to sit at 20% fill under 1 kPa; shift = dG_req - dG_site")
print(f"{'dH':>6}{'fill25':>8}" + "".join(f"{'mV@'+str(tc):>9}" for tc in (25, 40, 60, 80, 100)))
for dH_kj in (-70.0, -80.0, -90.0):
    dH = dH_kj * 1e3; dS = -165.0
    fill = loading(P_CO2_AIR, T0, dH, dS, 1.0)
    cells = []
    for tc in (25, 40, 60, 80, 100):
        T = tc + 273.15
        dG_req = -R * T * math.log(0.25 * P_REF / 1e3)
        shift = dG_req - (dH - T * dS)
        cells.append(max(0.0, shift) / F * 1e3)
    print(f"{dH_kj:>6.0f}{fill:>8.1%}" + "".join(f"{c:>9.0f}" for c in cells))
print("   Electricity: 1 e-/CO2, symmetric two-bed cell, V = shift + 2 x 0.10 V overpotential, 90% faradaic; heat = -dH + sensible (q_max 2, 20->... )")
for dH_kj, tc in ((-80.0, 25), (-80.0, 60), (-90.0, 60), (-70.0, 40)):
    dH = dH_kj * 1e3; dS = -165.0; T = tc + 273.15
    dG_req = -R * T * math.log(0.25 * P_REF / 1e3); shift = max(0.0, dG_req - (dH - T * dS))
    elec = F * (shift / F + 0.2) / 0.9
    wc = loading(P_CO2_AIR, T0, dH, dS, 2.0) - 0.4
    sens = 1500.0 * (T - T0) / wc
    heat = -dH + sens
    we = GJ(elec + heat * (1 - T0 / T) + vac_work(1e3)) + FAN100
    print(f"   dH {dH_kj:.0f}, T_des {tc} C: shift {shift/F*1e3:.0f} mV -> electricity {GJ(elec):.2f} GJ_e/t ({GJ(elec)/0.0036:.0f} kWh/t); heat {GJ(heat):.2f} GJ/t (reaction {GJ(-dH):.2f}, sensible {GJ(sens):.2f}, at {tc} C, exergy {GJ(heat*(1-T0/T)):.2f}); wc {wc:.2f}; work-eq {we:.2f} GJ/t, eta {floor/we:.0%}")
print(f"   For scale: 100 mV = {0.1*F/1e3:.2f} kJ/mol; one Langmuir 'degree' near 92 C for dH -70: d(dG)/dT = -dS - R ln(0.25 P_REF/p_des) = {(165 - R*math.log(0.25*P_REF/1e3)):.0f} J/mol/K -> {(165 - R*math.log(0.25*P_REF/1e3))/F*1e3:.2f} mV per K")

print("\n=== 4. WATER-ACTIVITY-MATCHED (ISOHUMID) REGENERATION: keep the sorbent's water, pump out only CO2")
print("   reference site dH -70, dS -165. p_CO2 over sorbent at 20% and 50% fill vs T; steam dilution p_H2O/p_CO2 at a_w matched to ambient")
print(f"{'T_des':>6}{'pCO2@20%':>10}{'pCO2@50%':>10}{'pH2O(aw.5)':>11}{'dil@20%':>9}{'dil@50%':>9}{'T_cond':>8}{'COP*':>6}{'GJe/t@50%':>10}{'GJ lost':>9}")
for tc in (60, 70, 80, 92, 100, 110, 120):
    T = tc + 273.15
    b = langmuir_b(-70e3, -165.0, T)
    p20 = 0.25 / b; p50 = 1.0 / b
    pw = 0.5 * psat(T)
    dil20, dil50 = pw / p20, pw / p50
    Tc = T_dew(pw)
    cop = 0.5 * T / (T - Tc)
    e_per_co2 = dil50 * DH_VAP_WATER / cop
    print(f"{tc:>6}{p20:>10.0f}{p50:>10.0f}{pw/1e3:>11.1f}{dil20:>9.1f}{dil50:>9.1f}{Tc-273.15:>8.0f}{cop:>6.1f}{GJ(e_per_co2):>10.2f}{GJ(dil50*DH_VAP_WATER):>9.1f}")
print("   (pCO2 in Pa; dil = mol steam per mol CO2 in the pumped gas; T_cond = condenser temperature at that p_H2O; COP* = 0.5 x Carnot for lifting latent heat from T_cond back to T_des; GJe = electricity to recycle that latent heat; GJ lost = latent heat if simply condensed and discarded)")
# evaporative cooling budget
for wc in (0.6, 1.04, 2.0):
    for dT in (50, 75):
        print(f"   evaporative-cooling water budget: cp 1500 x {dT} K / 44 kJ = {1500*dT/DH_VAP_WATER:.2f} mol H2O/kg -> {1500*dT/DH_VAP_WATER/wc:.1f} mol/mol CO2 at wc {wc} mol/kg", end=";")
    print()
print("   Measured swing ratios 6-8 mol/mol (fibres 45% RH, alumina 50% RH) vs this 1.7-3.4 mol/mol: the excess is water that a dry sweep or deep vacuum strips and re-adsorbs each cycle.")
for ratio in (2.0, 4.0, 6.0, 8.0):
    c = TVSACycle(dH=-70e3, dS=-165.0, q_max=2.0, T_des=373.15, p_des=1e3, water_coads=ratio)
    print(f"   verifier: water_coads {ratio:.0f} mol/mol -> heat {c.heat_gj_per_t:.2f} GJ/t, work-eq {c.work_equivalent_gj_per_t:.2f}")

print("\n=== 5. ALKALI BICARBONATE (amine-free, entropy-steep): M2CO3(s) + CO2 + H2O(g) <-> 2 MHCO3(s)")
data = {  # dHf kJ/mol, S J/mol/K at 298 K (NIST-JANAF / CRC values)
    "KHCO3": (-963.2, 115.5), "K2CO3": (-1151.0, 155.5), "NaHCO3": (-950.8, 101.7), "Na2CO3": (-1130.7, 135.0),
    "CO2": (-393.5, 213.8), "H2O": (-241.8, 188.8)}
for M in ("K", "Na"):
    bic, carb = data[M + "HCO3"], data[M + "2CO3"]
    dH = (carb[0] + data["CO2"][0] + data["H2O"][0] - 2 * bic[0]) * 1e3   # decomposition, per CO2
    dS = (carb[1] + data["CO2"][1] + data["H2O"][1] - 2 * bic[1])
    def K(T): return math.exp(-(dH - T * dS) / (R * T))   # = (pCO2/P)(pH2O/P)
    print(f"  {M}: decomposition dH {dH/1e3:.1f} kJ/mol CO2, dS {dS:.0f} J/mol/K (capture: {-dH/1e3:.1f}, {-dS:.0f}); dG25 {(dH - T0*dS)/1e3:.1f} kJ/mol")
    pco2_50 = K(T0) * P_REF**2 / pH2O_amb
    pco2_35 = K(308.15) * P_REF**2 / (0.5 * psat(308.15))
    dG_eff = (dH - T0 * dS) * -1 + R * T0 * math.log(pH2O_amb / P_REF)
    print(f"     capture equilibrium p_CO2 at 50% RH: 25 C {pco2_50:.2f} Pa ({pco2_50/P0*1e6:.1f} ppm), 35 C {pco2_35:.2f} Pa; effective CO2 binding dG at 50% RH, 25 C: {dG_eff/1e3:.1f} kJ/mol (needed -19.2)")
    for p in (1e3, 1e4, P0):
        T = brentq(lambda T: K(T) * P_REF**2 - p * p, 280.0, 700.0)
        print(f"     release with p_CO2 = p_H2O = {p/1e3:.0f} kPa: {T-273.15:.0f} C", end="; ")
    print()
    for name, pw in desic:
        T = brentq(lambda T: K(T) * P_REF**2 - 1e3 * pw, 250.0, 700.0)
        print(f"     p_CO2 1 kPa with p_H2O from {name} ({pw:.0f} Pa): {T-273.15:.0f} C", end="; ")
    print()
    if M == "K":
        for wt in (0.06, 0.20, 0.40):
            qcap = wt / 0.1382 * 1.0  # mol CO2 per kg at full carbonation (1 CO2 per K2CO3, M 138.2 g/mol)
            for util in (0.5, 0.8):
                wc = qcap * util
                for tdes in (75.0, 90.0):
                    T = tdes + 273.15
                    sens = 1000.0 * (T - T0) / wc
                    heat = dH + sens
                    we = workeq(heat, T, 1e3)
                    print(f"     {wt:.0%} K2CO3, {util:.0%} used ({wc:.2f} mol/kg), T_des {tdes:.0f} C: reaction {GJ(dH):.2f} (of which water vapour {GJ(DH_VAP_WATER):.2f}) + sensible {GJ(sens):.2f} = {GJ(heat):.2f} GJ/t; work-eq {we:.2f}, eta {floor/we:.0%}")
        print(f"     sorbent cost: K2CO3 at $1/kg on $3/kg carbon, 40 wt% -> ~$2.2/kg; at 1.16 mol/kg and 2,000 cycles: ${sorbent_cost_per_tonne(2.2, 1.16, 2000):.0f}/t; 10,000 cycles ${sorbent_cost_per_tonne(2.2, 1.16, 10000):.0f}/t")

print("\n=== 6. CRYSTALLISATION/DISSOLUTION SWING: slurry regeneration of guanidinium carbonate crystals at 85-95 C, water stays liquid")
cp_w, cp_s = 4186.0, 1300.0
for dHr_kj in (60.0, 90.0, 120.0):
    for solids in (0.10, 0.20, 0.30):
        for rec in (0.0, 0.85):
            qcap = 3.0e-3  # mol CO2 per g crystal
            m_cryst = 1.0 / qcap   # g crystal per mol CO2
            m_w = m_cryst * (1 - solids) / solids
            dT = 90.0 - 25.0
            sens = (m_w * cp_w + m_cryst * cp_s) / 1000.0 * dT * (1 - rec)
            vap = DH_VAP_WATER * psat(363.15) / 50e3 * 0.5   # 1 kPa... water vapour leaving with CO2 at 50 kPa CO2, 50% of its latent heat recovered in condenser
            heat = dHr_kj * 1e3 + sens + vap
            if rec == 0.85:
                print(f"  dH_rxn {dHr_kj:.0f} kJ/mol, {solids:.0%} solids, {rec:.0%} liquid heat recovery: sensible {GJ(sens):.2f} + vapour {GJ(vap):.2f} + reaction {GJ(dHr_kj*1e3):.2f} = {GJ(heat):.2f} GJ/t at 90 C (work-eq {workeq(heat, 363.15, P0):.2f}, eta {floor/workeq(heat, 363.15, P0):.0%})")
            elif solids == 0.20:
                print(f"  dH_rxn {dHr_kj:.0f} kJ/mol, {solids:.0%} solids, NO heat recovery: {GJ(heat):.2f} GJ/t")
print(f"  comparison: measured dry-crystal regeneration 7.0-10.2 GJ/t (MGBIG) and 8.2 GJ/t (m-BBIG) incl. hydrate water; crystal sensible alone (cp 1.3 kJ/kg/K, 65 K, 3 mmol/g) = {GJ(cp_s/1000*65/3e-3*1e-3*1e3/1e3*1e3):.2f} GJ/t")
