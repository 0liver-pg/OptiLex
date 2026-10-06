import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
C = 273.15
def kj(j): return j/1e3

print("=== Reference check ===")
ref = reference_amine_cycle()
print(f"ref wc {ref.working_capacity:.2f} mol/kg heat {ref.heat_gj_per_t:.2f} GJ/t (rxn {gj_per_tonne(ref.reaction_heat):.2f} sens {gj_per_tonne(ref.sensible_heat):.2f} water {gj_per_tonne(ref.water_heat):.2f}) work-eq {ref.work_equivalent_gj_per_t:.2f} eff {ref.second_law_efficiency:.0%}")
floor = gj_per_tonne(min_separation_work(420e-6, 0.75, 0.99)); print(f"floor {floor:.3f} GJ/t")

print("\n=== IDEA 1: water swing ratio (hydrophobic host) ===")
for w in (8, 6, 4.4, 2.4, 1.1, 0):
    c = TVSACycle(dH=-70e3, dS=-165, q_max=2.0, T_des=373.15, p_des=1e3, water_coads=w)
    print(f"water {w:>4} mol/mol: heat {c.heat_gj_per_t:5.2f} GJ/t  work-eq {c.work_equivalent_gj_per_t:4.2f}  eff {c.second_law_efficiency:.0%}")
# with realistic inert mass 1.0 kg/kg (laminate+housing share) and 50% capacity use? keep simple
for w in (8, 2.4):
    c = TVSACycle(dH=-70e3, dS=-165, q_max=2.0, T_des=373.15, p_des=1e3, water_coads=w, inert_mass_ratio=1.0)
    print(f"  with inert 1.0 kg/kg: water {w}: heat {c.heat_gj_per_t:.2f} GJ/t")
print("  heat cost at $5.6/GJ per mol H2O avoided:", round(gj_per_tonne(DH_VAP_WATER)*5.6,2), "$/t per mol/mol")

print("\n=== IDEA 2: climate-matched binding (epoxide-capped PEI, dH -66) ===")
for dH in (-66e3, -70e3, -80e3):
    print(f" dH {kj(dH):.0f} kJ/mol:")
    for Tc in (35, 25, 15, 10, 5, 0, -10, -20):
        th = loading(P_CO2_AIR, C+Tc, dH, -165, 1.0)
        print(f"   T_ads {Tc:>4} C fill {th:6.1%}", end="")
        for pdes in (1e3, 1e2):
            td = desorption_temperature(dH, -165, pdes, 0.2)
            print(f" | T_des({pdes/1e3:.1f} kPa) {td-C:5.0f} C", end="")
        print()
# cycle heat for -66 at T_ads 0 C vs 25 C, q_max 3 (epoxide-PEI 1.95 mmol/g working at 50%RH suggests q_max>=2.5)
for Tc, Td in ((25, 75), (10, 75), (0, 75), (0, 70), (-10, 65)):
    c = TVSACycle(dH=-66e3, dS=-165, q_max=3.0, T_ads=C+Tc, T_des=C+Td, p_des=1e3, water_coads=2.0)
    try:
        print(f" -66: T_ads {Tc} T_des {Td}: wc {c.working_capacity:.2f} mol/kg heat {c.heat_gj_per_t:.2f} GJ/t work-eq {c.work_equivalent_gj_per_t:.2f} eff {c.second_law_efficiency:.0%}")
    except ValueError as e: print(" ", Tc, Td, e)
for Tc, Td in ((25, 100), (0, 100), (0, 75)):
    c = TVSACycle(dH=-70e3, dS=-165, q_max=2.0, T_ads=C+Tc, T_des=C+Td, p_des=1e3, water_coads=2.0)
    try: print(f" -70: T_ads {Tc} T_des {Td}: wc {c.working_capacity:.2f} heat {c.heat_gj_per_t:.2f} work-eq {c.work_equivalent_gj_per_t:.2f}")
    except ValueError as e: print(" ", Tc, Td, e)
# sorbent cost: epoxide-PEI fade 50x slower claim -> cycles
for cyc in (2000, 5000, 20000):
    print(f"  $20/kg, 1.5 mol/kg, {cyc} cycles: ${sorbent_cost_per_tonne(20,1.5,cyc):.0f}/t")

print("\n=== IDEA 3: moisture-swing capture + MnO2 proton-sponge release ===")
# carbonate liquor loading capacity vs resin wet-release ceiling
K = 10**(10.33-6.35); H = 0.034  # M/atm
for pk in (1, 2, 5, 10):
    co2aq = pk/101.325*H
    for c0 in (0.5, 1.0):  # M K2CO3
        # x^2*c0^2... define [HCO3]=2 c0 x, [CO3]=c0(1-x): co2aq = (2c0x)^2/(K c0 (1-x))
        a = 4*c0/K/co2aq  # x^2/(1-x) = co2aq*K/(4 c0) -> solve
        r = co2aq*K/(4*c0)
        x = (-r + math.sqrt(r*r+4*r))/2
        print(f"  resin ceiling {pk:>2} kPa, {c0} M K2CO3: bicarbonate conversion {x:.0%} -> {2*c0*x/2:.2f} mol CO2 absorbed per L (CO2 per L = c0*x)")
for V, CE in ((0.4, 0.8), (0.5, 0.8), (0.4, 1.0)):
    w = electrochemical_work(1, V, CE); print(f"  1 e-/CO2 at {V} V, CE {CE:.0%}: {w/1e3:.0f} kJ/mol = {gj_per_tonne(w):.2f} GJ/t = {gj_per_tonne(w)/0.0036:.0f} kWh/t")
print(f"  pH floor: 2.6 units x 5.7 kJ = {2.6*5.7:.1f} kJ/mol = {gj_per_tonne(2.6*5.7e3):.2f} GJ/t")
meas = 2.1; print(f"  measured MnO2 stage 2.1 GJ/t = {2.1/0.0036:.0f} kWh/t = ${2.1/0.0036*0.05:.0f}/t at $50/MWh; + ASU conveyor 490 kWh/t -> {2.1+490*0.0036:.2f} GJ/t electric; 2nd-law {floor/(2.1+490*0.0036):.0%}")
for j in (30, 10, 100):
    for e, ce in ((1, 0.8),):
        mol_s_m2 = j*10/FARADAY/e*ce  # j mA/cm2 -> A/m2 = j*10
        t_m2_yr = mol_s_m2*M_CO2*3.156e7/1000
        for cap in (300, 1000):
            charge = cap*0.14/t_m2_yr
            print(f"  {j} mA/cm2, {e} e-, CE {ce}: {t_m2_yr:.2f} t/m2/yr -> capital charge ${charge:.0f}/t at ${cap}/m2 (14%/yr)")
print("  MnO2 air cell measured 0.0084 t/m2/yr -> capital charge at $300/m2:", round(300*0.14/0.0084), "$/t")
print("  moisture latent heat from air at 20 mol H2O/mol CO2:", round(gj_per_tonne(moisture_swing_water_heat(20)),1), "GJ/t (free, from air)")
for cyc,wc,price in ((1380,0.675,54),(5000,0.9,20),(15000,0.9,20),(15000,0.9,7)):
    print(f"  resin ${price}/kg, {wc} mol/kg, {cyc} cycles: ${sorbent_cost_per_tonne(price,wc,cyc):.0f}/t")

print("\n=== IDEA 4: hydroxide-stable cation moisture-swing resin ===")
for cyc in (1380, 3000, 5000, 15000, 30000):
    print(f"  {cyc:>6} cycles: $54/kg,0.675: ${sorbent_cost_per_tonne(54,0.675,cyc):6.0f}/t | $20/kg,1.0: ${sorbent_cost_per_tonne(20,1.0,cyc):5.0f}/t | $50/kg,1.0: ${sorbent_cost_per_tonne(50,1.0,cyc):5.0f}/t")
print("  productivity at 1 mol/kg, 8 cycles/day:", round(productivity(1.0, 8),2), "kg/kg/day; 2 cycles/day:", round(productivity(1.0,2),3))

print("\n=== IDEA 5: CO2-blanketed cool-down ===")
qa = loading(P_CO2_AIR, T0, -70e3, -165, 2.0)
print(f"  q_ads 25 C 420 ppm: {qa:.2f} mol/kg")
for Tc in (100, 80, 70, 60, 55, 50, 45, 40):
    for p in (1e3, 3e2, 1e2):
        q = loading(p, C+Tc, -70e3, -165, 2.0)
        print(f"   {Tc} C, {p/1e3:.1f} kPa CO2: loading {q:.2f} mol/kg = {q/qa:.0%} of q_ads", end=" |")
    print()
# cycle at 1 kPa 100C: wc 1.04. If cool-down under 1 kPa to 50 C re-adsorbs to q(50C,1kPa): product lost per cycle = q(50,1kPa)-q(100,1kPa)
q100 = loading(1e3, C+100, -70e3, -165, 2.0)
for Tc, p in ((50,1e3),(50,3e2),(50,1e2),(45,1e2)):
    q = loading(p, C+Tc, -70e3, -165, 2.0)
    print(f"  cool to {Tc} C under {p/1e3:.1f} kPa: re-adsorbed {q-q100:.2f} mol/kg = {(q-q100)/(qa-q100):.0%} of working capacity (recoverable next cycle, not lost; it costs CO2 inventory + mass of CO2 gas)")
# fade economics
for rate in (5.1e-3, 3.5e-3, 2.3e-3, 1.1e-3, 5e-4):
    cyc = 20/rate
    print(f"  fade {rate:.1e} %/cycle -> 20% loss at {cyc:,.0f} cycles -> sorbent $20/kg,1.04: ${sorbent_cost_per_tonne(20,1.04,cyc):.0f}/t ; $50/kg: ${sorbent_cost_per_tonne(50,1.04,cyc):.0f}/t")
for tmin in (2,3,5):
    pen = tmin/40
    print(f"  {tmin} min cool-down on 40 min cycle: productivity -{pen:.1%} -> capital +${274*0.6*pen/(1-pen):.0f}/t (60% of $274/t scales)")
# Guta 2023 cyclic: 1-2.4 %/cycle unprotected -> cost
for rate in (1.0, 2.4):
    print(f"  unprotected PEI {rate}%/cycle: 20% loss in {20/rate:.0f} cycles -> ${sorbent_cost_per_tonne(20,1.0,20/rate):,.0f}/t")

print("\n=== IDEA 6: alpha-substituted (hindered) primary amine resin ===")
print(f"  dG for half fill at 25 C: {dG_for_half_loading()/1e3:.1f} kJ/mol")
for dS in (-165, -140, -120):
    for dH in (-55e3,-60e3,-65e3,-70e3,-75e3):
        th = loading(P_CO2_AIR, T0, dH, dS, 1.0)
        td = desorption_temperature(dH, dS, 1e3, 0.2)-C
        print(f"  dS {dS} dH {kj(dH):.0f}: fill {th:6.1%} T_des(1kPa) {td:5.0f} C")
for cyc in (8700, 20000, 50000):
    print(f"  $15/kg, 1.0 mol/kg, {cyc} cycles: ${sorbent_cost_per_tonne(15,1.0,cyc):.0f}/t")
# bicarbonate 1:1 vs carbamate 0.5: amine efficiency doubling at same N density halves sensible heat
for wc in (0.6, 1.2):
    c = TVSACycle(dH=-70e3, dS=-165, q_max=wc/0.52, T_des=373.15, p_des=1e3, water_coads=2.0)
    print(f"  wc {c.working_capacity:.2f}: heat {c.heat_gj_per_t:.2f} GJ/t (sens {gj_per_tonne(c.sensible_heat):.2f})")

print("\n=== IDEA 1 addendum: Lewatit GAB water isotherm (Low et al. 2023, Table 9; Young 2021 form) ===")
qm, Cp, D, F, G = 3.23, 46.83e3, 0.02446, 53.31e3, -0.03268e3
def gab(a, T=298.15):
    E1 = Cp - math.exp(D*T); E29 = F + G*T; E10 = 57220 - 44.38*T
    c = math.exp((E1-E29)/(R*T)); k = math.exp((E29-E10)/(R*T))
    return qm*c*k*a/((1-k*a)*(1+(c-1)*k*a))
for rh, co2 in ((0.2, 1.2), (0.5, 1.8), (0.8, 2.0)):
    w = gab(rh); print(f"  Lewatit 25 C {rh:.0%} RH: H2O {w:.2f} mmol/g; CO2 ~{co2} mmol/g (map) -> {w/co2:.1f} mol H2O per mol CO2")
print("  Twente pilot (Lewatit): 1.12 GJ/t at 20% RH and 4.4 GJ/t at 82% RH = 1.1 and 4.4 mol/mol -> consistent")
print("  PEI/silica hollow fibre (GT 2026): 6/0.72 = 8.3 mol/mol at 45% RH; amine-alumina: 4.2/0.55 = 7.6 at 50% RH; COF-999: 5.0/2.05 = 2.4 at 50% RH")
print("  per-N view: Lewatit ~5.5 mmol N/g -> 0.6 H2O/N and 0.33 CO2/N; PEI/silica 0.7 H2O/N and 0.12-0.29 CO2/N -> ratio set mainly by amine efficiency")

print("\n=== IDEA 5 addendum: evaporative (flash) cooling under sealed vacuum ===")
for inert in (0.0, 1.0, 3.0):
    cp_tot = 1.5 + inert*0.9  # kJ/kg/K per kg sorbent
    for dT in (50, 60):
        Q = cp_tot*dT; m_w = Q/2260  # kg water per kg sorbent
        print(f"  inert {inert} kg/kg, cool {dT} K: {Q:.0f} kJ/kg sorbent -> {m_w*1000:.0f} g water flashed per kg sorbent; condenser duty {Q/1.04/44.01*1e3/1e6*1e3:.2f} GJ/t if dumped", end="")
        # vapour at 50 C 12.3 kPa -> pump to 1 atm if no condenser
        wv = R*323*math.log(101325/12300)/0.7  # J/mol
        print(f"; if pumped instead of condensed: {gj_per_tonne(wv*(m_w/0.018)/1.04):.2f} GJ_e/t")
print("  steam condensed to heat 1 kg laminate (cp 2.4, 25->100 C): 180 kJ = 80 g; plus co-adsorbed water 2-8 mol/mol x 1.04 mol/kg = 37-150 g/kg -> water on hand exceeds the 53-80 g needed")
print("  CO2 re-adsorption during sealed cool-down: only the void gas (~1 bed volume at <=1 kPa) is available, i.e. negligible vs 1.04 mol/kg")
