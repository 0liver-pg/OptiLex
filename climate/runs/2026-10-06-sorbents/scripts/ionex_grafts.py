import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

print("=== IDEA 1: hydration number of a moisture-swing resin vs the AEM stability threshold ===")
IEC = 4.18            # mmol N+/g, IRA-900 (Wang/Lively 2025)
w20, w85 = 7.1, 28.4  # mmol H2O/g at 20% and 85% RH, 25 C (same source)
lam20, lam85 = w20/IEC, w85/IEC
print(f"lambda (H2O per N+): {lam20:.2f} at 20% RH, {lam85:.2f} at 85% RH; Dekel threshold ~4 -> dry half-cycle sits at lambda<4")
# how much of a vapour cycle is spent below lambda 4: linear interpolate RH where lambda=4
rh_lam4 = 20 + (4 - lam20) / (lam85 - lam20) * 65
print(f"lambda=4 reached near {rh_lam4:.0f}% RH (linear interpolation) -> capture step (<=50% RH) is the degradation window")
print("Sorbent replacement cost, $/t CO2, working capacity 0.9 mol/kg (lab) and 0.675 (ASU outdoor):")
for wc in (0.9, 0.675):
    for price in (7, 20, 54):
        row = [f"{sorbent_cost_per_tonne(price, wc, c):7.0f}" for c in (1380, 5000, 15000, 50000)]
        print(f"  wc {wc} price ${price}/kg: cycles 1380/5000/15000/50000 -> " + " ".join(row))

print("\n=== IDEA 2: thin reinforced AEM film: diffusion scaling, air-supply limit, productivity ===")
D = 6.5e-12   # m2/s, water diffusivity fitted to P-100 sheet (Shi/Lackner 2017)
t100 = 31.8   # min half-time for 100 um sheet, 400 ppm, 30% RH (measured)
print(f"empirical scaling t_half ~ L^2/D: 100 um -> {1e-8/D/60:.0f} min (measured {t100} min)")
for L in (50, 25, 15):
    print(f"  {L} um film: t_half ~ {t100*(L/100)**2:.1f} min")
r_bead = 614e-6/2
k_glk = 15*D/r_bead**2
print(f"Glueckauf LDF for 614 um bead: k = 15D/r^2 = {k_glk:.1e} /s (measured 4.5e-4 to 14e-4 /s)")
# air-supply-limited adsorption time for a film stack
film_um, channel_mm, depth_m, u = 25, 1.0, 0.3, 2.0
rho = 1100.0
kg_per_m3 = (film_um*1e-6*rho) / ((film_um*1e-6) + channel_mm*1e-3)
kg_per_m2 = kg_per_m3*depth_m
c_co2 = P0/(R*T0)*420e-6  # mol/m3
cap = 0.5
wc2 = 0.9
t_ads = kg_per_m2*wc2/(u*c_co2*cap)
dp = 12*1.8e-5*u*depth_m/(channel_mm*1e-3)**2
print(f"stack: {film_um} um films, {channel_mm} mm channels, {depth_m} m deep: {kg_per_m3:.1f} kg/m3, {kg_per_m2:.1f} kg/m2 face")
print(f"  air-supply-limited adsorption time at {u} m/s, 50% capture, wc {wc2} mol/kg: {t_ads/60:.1f} min; laminar dP ~ {dp:.0f} Pa")
# water carried by the drying air: 20 -> 60 % RH at 20 C
psat20 = 2339.0
dy = 0.4*psat20/P0
water_flux = u*(P0/(R*293.15))*dy
for w_per_co2 in (17, 27):
    n_w = kg_per_m2*wc2*w_per_co2
    print(f"  drying air for {w_per_co2} mol H2O/mol CO2: {n_w/water_flux/60:.1f} min (20->60% RH, 20 C)")
for cyc_min in (15, 20, 30):
    cpd = 1440/cyc_min
    print(f"  {cyc_min}-min cycle: {cpd:.0f}/day -> productivity {productivity(wc2, cpd):.2f} kg CO2/kg/day (beads 0.19-0.27; amine ref 0.55; Gen3 target 1.0-1.4)")
print("sorbent cost, 0.9 mol/kg (sheet mass incl. 25% ePTFE -> 0.68 mol/kg sheet):")
for price in (20, 50, 100, 300):
    row = [f"{sorbent_cost_per_tonne(price, 0.68, c):6.0f}" for c in (5000, 20000, 50000)]
    print(f"  ${price}/kg: 5k/20k/50k cycles -> " + " ".join(row))
fan = fan_work_gj_per_tonne(420e-6, cap, dp)
print(f"fan work at {dp:.0f} Pa and 50% capture: {fan:.2f} GJ/t; drying air adds ~{fan*0.0:.2f} (same air stream)")

print("\n=== IDEA 3: hydrophobic membrane envelope: water uptake, bicarbonate brine equilibrium, membrane flux ===")
w_liq = 3.3                    # g/g on liquid immersion (ASU packet)
w_vap = 28.4*18e-3             # g/g at 85% RH vapour equilibrium (IRA-900)
w_vap98 = 0.7                  # g/g assumed near-saturation (extrapolated; to be measured)
wc3 = 0.675e-3*44.01           # g CO2 per g resin per cycle (ASU effective)
for label, w in (("liquid immersion", w_liq), ("vapour 85% RH", w_vap), ("vapour ~98% RH (assumed)", w_vap98)):
    print(f"  {label}: {w:.2f} g/g -> {w/wc3:.0f} g H2O per g CO2 ({w/18e-3/0.675e-3:.0f} mol/mol); drying time ~ {30*w/w_liq:.0f} min if proportional to water")
print(f"  thermodynamic minimum at 20% RH for 1 atm product: 4.8 mol/mol = {4.8*18/44:.1f} g/g")
# CO2 pressure over K2CO3/KHCO3 brine at 25 C: p = [HCO3]^2 / ([CO3] K), K = KH*K1/K2 (ideal)
KH, K1, K2 = 3.4e-2, 4.45e-7, 4.69e-11   # M/atm, M, M
Keq = KH*K1/K2
for C in (0.5, 1.0):
    for conv in (0.5, 0.8, 0.9, 0.95):
        hco3 = 2*C*conv; co3 = C*(1-conv)
        p = hco3**2/(co3*Keq)
        print(f"  {C} M K2CO3 at {conv:.0%} bicarbonate conversion: p_CO2 = {p*101.325:.2f} kPa (ideal-solution estimate)")
print("  resin wet-state p_CO2: ~4 kPa (100x, vapour) to ~21 kPa (500x, liquid) -> brine can reach ~85-95% bicarbonate")
# membrane-contactor flux: film theory, k_L = 1e-5 m/s, E ~ Hatta for pseudo-first-order OH- reaction
kL, D_co2, kOH = 1e-5, 1.9e-9, 8.0e3   # m/s, m2/s, M^-1 s^-1
H = 3.4e-2/101.325   # mol/L/kPa
for name, pH in (("10 mM Na2CO3 pond (pH ~10.5)", 10.5), ("0.5 M K2CO3 (pH ~11.6)", 11.6), ("1 M KOH/K2CO3 start (pH 13)", 13.0)):
    OH = 10**(pH-14)
    k1 = kOH*OH
    Ha = math.sqrt(k1*D_co2)/kL
    for p in (5.0, 15.0):
        Cstar = H*p*1e3  # mol/m3
        Einf = 1 + 2.0*OH/(2*Cstar/1e3) if Cstar > 0 else 1
        E = min(max(Ha, 1.0), Einf)
        flux = E*kL*Cstar
        print(f"  {name}, p_CO2 {p:.0f} kPa: Ha {Ha:.1f}, E_inf {Einf:.1f}, E {E:.1f}, flux {flux*3600:.2f} mol/m2/h")
load = 10e-3*0.675  # mol CO2 in 10 g resin bag (0.02 m2 both faces) = 0.34 mol/m2
print(f"  10 g resin in a 10x10 cm bag: {load/0.02:.2f} mol CO2 per m2 membrane -> time = that / flux")

print("\n=== IDEA 4: value of slower oxidative fade (cost side) ===")
for fade in (2.2e-3, 1.1e-3, 5e-4):   # % per cycle
    cycles = 20/fade/100*100  # cycles to 20% loss
    cycles = 20/fade
    for price in (20, 50):
        print(f"  fade {fade:.1e} %/cycle -> {cycles:,.0f} cycles to 20% loss; 1.0 mol/kg avg 0.9: ${sorbent_cost_per_tonne(price, 0.9, cycles):.0f}/t at ${price}/kg")
print("  Cu effect (Kuspangaliyeva 2026, 4.5 h 120 C air): retained 72% -> 63% at ~4 ppm Cu: rate ratio "
      f"{math.log(0.63)/math.log(0.72):.2f}x; 2 wt% CeO2 costs 2% of capacity")

print("\n=== IDEA 5: plasticised resin: productivity vs LDF mass-transfer coefficient ===")
wc5 = 0.9
for k_wet, k_dry in ((4.5e-4, 14e-4), (10e-4, 20e-4), (20e-4, 40e-4), (45e-4, 90e-4)):
    t90 = (math.log(10)/k_wet + math.log(10)/k_dry)/60   # min, both half-cycles to 90%
    cpd = 1440/t90
    print(f"  k_wet {k_wet:.1e}, k_dry {k_dry:.1e} /s: t90 cycle {t90:.0f} min -> {cpd:.1f} cycles/day -> {productivity(wc5, cpd):.2f} kg/kg/day;"
          f" with 20% capacity penalty {productivity(0.8*wc5, cpd):.2f}")

print("\n=== IDEA 6: benzylamine-grafted PE/PP microfibre nonwoven: cycle heat, kinetics, cost ===")
ref = reference_amine_cycle()
print(f"reference: wc {ref.working_capacity:.2f}, heat {ref.heat_gj_per_t:.2f} GJ/t, work-eq {ref.work_equivalent_gj_per_t:.2f}")
for label, cyc in (
    ("fibre, dH -70, qmax 1.2, cp 1700, water 3/mol, 100 C/1 kPa", TVSACycle(dH=-70e3, dS=-165.0, q_max=1.2, cp_sorbent=1700.0, water_coads=3.0)),
    ("fibre, same, water 5/mol", TVSACycle(dH=-70e3, dS=-165.0, q_max=1.2, cp_sorbent=1700.0, water_coads=5.0)),
    ("fibre, 50% used capacity (fast cycle), water 3/mol", TVSACycle(dH=-70e3, dS=-165.0, q_max=0.6, cp_sorbent=1700.0, water_coads=3.0)),
    ("PEI/silica laminate-like: qmax 2, cp 1500, inert 1.0, water 6/mol", TVSACycle(dH=-70e3, dS=-165.0, q_max=2.0, cp_sorbent=1500.0, inert_mass_ratio=1.0, water_coads=6.0)),
):
    print(f"  {label}: wc {cyc.working_capacity:.2f} mol/kg, heat {cyc.heat_gj_per_t:.2f} GJ/t "
          f"(reaction {gj_per_tonne(cyc.reaction_heat):.2f}, sensible {gj_per_tonne(cyc.sensible_heat):.2f}, water {gj_per_tonne(cyc.water_heat):.2f}), "
          f"work-eq {cyc.work_equivalent_gj_per_t:.2f}, 2nd law {cyc.second_law_efficiency:.0%}")
r_f = 2.5e-6
for Dp in (1e-13, 1e-12, 1e-11):
    print(f"  fibre radius 2.5 um, D {Dp:.0e} m2/s: Glueckauf k = {15*Dp/r_f**2:.2e} /s, t90 = {math.log(10)/(15*Dp/r_f**2):.0f} s")
m_area, u6 = 5.0, 2.0
wc6 = 0.78
t6 = m_area*wc6/(u6*c_co2*0.6)
print(f"  air-supply-limited adsorption for {m_area} kg/m2 at {u6} m/s, 60% capture: {t6/60:.1f} min")
for cyc_min in (15, 20, 40):
    cpd = 1440/cyc_min
    print(f"  {cyc_min}-min cycle, wc 0.6 mol/kg: {productivity(0.6, cpd):.2f} kg/kg/day")
for price in (10, 20):
    row = [f"{sorbent_cost_per_tonne(price, 0.6, c):6.0f}" for c in (5000, 10000, 20000)]
    print(f"  ${price}/kg, wc 0.6: 5k/10k/20k cycles -> " + " ".join(row))
# PE/PP mass fraction: degree of grafting 100% VBC then EDA amination
M_vbc, M_unit = 152.6, 152.6-36.46+60.1
dog = 1.0
gN = dog*2/ M_unit*1000  # mmol N per g grafted polymer
print(f"  VBC graft (DoG 100%) aminated with ethylenediamine: {gN:.1f} mmol N per g graft -> {gN/(1+dog):.1f} mmol N/g fibre; "
      f"at Lewatit-like efficiency 0.15-0.25 CO2/N: {gN/(1+dog)*0.15:.2f}-{gN/(1+dog)*0.25:.2f} mmol/g")
