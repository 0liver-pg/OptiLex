import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
C = 273.15
NA = 6.02214076e23
def hr(s): print("\n" + "=" * 8 + " " + s + " " + "=" * 8)

ref = reference_amine_cycle()
hr("0. Reference cycle (verifier)")
print(f"wc {ref.working_capacity:.3f} mol/kg | heat {ref.heat_gj_per_t:.2f} GJ/t | work-eq {ref.work_equivalent_gj_per_t:.2f} | eff {ref.second_law_efficiency:.0%}")
floor = gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99))
print(f"floor {floor:.3f} GJ/t")

# ---------------------------------------------------------------------------------------------
hr("IDEA 1. Trace reactive gases (O3, NO2, HCHO, SO2, H2S) delivered to an amine bed: flux accounting")
def air_mol_per_mol_co2(x=X_AIR, f=0.75): return 1.0 / (x * f)
n_air = air_mol_per_mol_co2()
n_co2_t = 1e3 / M_CO2  # mol per tonne (1000 kg / 0.04401 kg/mol)
print(f"air processed: {n_air:,.0f} mol air per mol CO2 (420 ppm, 75% capture) = {air_volume_per_tonne(X_AIR,0.75):,.0f} m3/t")
print(f"trace dose per tonne CO2: {n_co2_t*n_air*1e-9:.4f} mol per ppb")
species = {"O3 (outdoor mean 30-50, summer peaks 60-80)": 40, "NO2 (suburban 5-20)": 10, "HCHO (outdoor 1-5)": 3, "SO2 (1-5)": 2}
tot = 0
for k, c in species.items():
    d = n_co2_t * n_air * c * 1e-9; tot += c
    print(f"  {k:<45} {c:>3} ppb -> {d:.2f} mol per t CO2")
print(f"  total {tot} ppb -> {n_co2_t*n_air*tot*1e-9:.2f} mol per t CO2")
# amine inventory consumed per tonne over sorbent life
for wc, L, Nkg in ((1.04, 20000, 9.3), (1.04, 5000, 9.3), (0.9, 20000, 5.0)):
    kg_per_t = 1e3 / (wc * M_CO2 * L)
    print(f"  wc {wc} mol/kg, life {L} cycles: {kg_per_t:.2f} kg sorbent per t CO2 -> {kg_per_t*Nkg:.1f} mol N per t (N {Nkg} mol/kg)")
print("Per-cycle fractional site loss at yield Y = 1 (every trace molecule kills one site):")
budget = 20.0 / 20000  # %/cycle for 20% at 20k cycles
for label, Nsites in (("uniform over all N (40 wt% PEI, 9.3 mol N/kg)", 9.3), ("accessible sites only (wc/0.5 = 2.08 mol/kg)", 2.08)):
    for c in (10, 40, 55):
        loss = ref.working_capacity * n_air * c * 1e-9 / Nsites * 100
        print(f"  {label:<48} {c:>3} ppb: {loss:.2e} %/cycle = {loss/budget:.1f} x the 20k-cycle budget ({budget:.1e} %/cycle); Y needed to equal budget {budget/loss:.2f}")
# assumption-free metric: Y_cap = mol CO2 working capacity destroyed per mol trace gas consumed
print("Y_cap metric (mol CO2 capacity lost per mol trace gas consumed): fractional capacity loss per cycle = Y_cap * c / (x_CO2 * f)")
for c in (10, 40, 55):
    per_unit = n_air * c * 1e-9
    print(f"  outdoor {c} ppb, 420 ppm, 75% capture: loss/cycle = {per_unit:.2e} x Y_cap; Y_cap that uses the whole 20%/20,000-cycle budget = {1e-5/per_unit:.3f}; Y_cap matching 3.5e-3 %/cycle = {3.5e-5/per_unit:.3f}")
for c in (25, 55):
    per_unit = 1/(500e-6*0.19) * c * 1e-9
    print(f"  TDA indoor {c} ppb, 500 ppm, 19% capture: Y_cap that explains the measured 2.2e-3 %/cycle = {2.2e-5/per_unit:.3f}")
# Sholl / Jamdade 2025 upper bound mass-balance check
print("Mass-balance check of the published ozone upper bound (Jamdade, Cai, Sholl 2025):")
co2_cycle = 552.0; o3_pub = 2.4e21 / NA
air_implied = o3_pub / 10e-9
print(f"  published O3 per cycle at 10 ppb: {o3_pub:.4f} mol -> implies {air_implied:,.0f} mol air -> contains {air_implied*X_AIR:.0f} mol CO2, but {co2_cycle:.0f} mol were captured")
o3_min = co2_cycle / X_AIR * 10e-9; o3_75 = co2_cycle / (X_AIR*0.75) * 10e-9
sites = 1.33e27 / NA
print(f"  minimum O3 passing (100% capture) {o3_min:.4f} mol ({o3_min/o3_pub:.1f}x published); at 75% capture {o3_75:.4f} mol ({o3_75/o3_pub:.1f}x)")
for c in (10, 40):
    o3 = co2_cycle / (X_AIR*0.75) * c * 1e-9
    per = o3 / sites
    print(f"  corrected at {c} ppb, 75% capture, {sites:,.0f} mol amine sites: {per*100:.1e} %/cycle -> after 40,000 cycles {1-math.exp(-per*40000):.0%} of sites (paper: 0.0002 %/cycle, ~8%)")
# TDA/GE indoor bench test: how much trace gas reached the sorbent per cycle vs measured fade
print("TDA/GE sub-bench (500 ppm, 19% capture, 0.18 mol/kg coating, lab air, 2.2e-3 %/cycle fade):")
n_air_tda = 1/(500e-6*0.19)
air_kg_cycle = 0.18 * n_air_tda
lost_cap = 0.18 * 2.2e-5  # mol CO2 capacity lost per kg per cycle
for c_in in (25, 55):
    dose = air_kg_cycle * c_in * 1e-9
    for spc in (1.0, 2.0):  # sites per CO2 of capacity (bicarbonate 1, carbamate 2)
        print(f"  indoor trace total {c_in} ppb: dose {dose:.1e} mol/kg/cycle; capacity lost {lost_cap:.1e} mol/kg/cycle = {lost_cap*spc:.1e} sites -> yield needed Y = {lost_cap*spc/dose:.2f} ({spc:.0f} site/CO2)")
# Guard costs
print("Inlet guard costs:")
for dp in (25, 50, 75):
    g = fan_work_gj_per_tonne(X_AIR, 0.75, dp)
    print(f"  +{dp} Pa: {g:.3f} GJ/t = {g/0.0036:.0f} kWh/t = ${g/0.0036*0.05:.1f}/t at $50/MWh")
cons = n_co2_t*n_air*15e-9
for cap_mol_kg, price in ((3.0, 5.0), (1.0, 10.0), (3.0, 0.0)):
    print(f"  consumable acid gases+HCHO 15 ppb = {cons:.2f} mol/t; guard capacity {cap_mol_kg} mol/kg at ${price}/kg -> {cons/cap_mol_kg:.2f} kg/t = ${cons/cap_mol_kg*price:.1f}/t")
o3t = n_co2_t*n_air*40e-9
print(f"  if O3 (40 ppb) is also consumed stoichiometrically by a sacrificial amine layer: {o3t:.2f} mol/t -> {o3t/3:.2f} kg/t of spent sorbent (3 mol/kg reactive)")
print("Value of halving fade (verifier sorbent cost, wc 1.04 mol/kg, 20% end-of-life):")
for rate in (5.1e-3, 3.5e-3, 2.2e-3):
    for price in (20, 50):
        c1 = sorbent_cost_per_tonne(price, ref.working_capacity, 20/rate)
        c2 = sorbent_cost_per_tonne(price, ref.working_capacity, 20/(rate/2))
        print(f"  fade {rate:.1e} %/cycle, ${price}/kg: ${c1:.0f}/t -> halved fade ${c2:.0f}/t (saves ${c1-c2:.0f}/t)")
# uptake of a reactive trace gas in a laminate channel (half-gap 0.5 mm, 2 m/s, 0.15 m deep)
print("Fraction of a trace gas removed in one pass of a parallel-plate laminate (1 mm gap, 0.15 m, 2 m/s), by uptake coefficient gamma:")
h=0.5e-3; Dg=1.5e-5; km=4*Dg/(2*h); tres=0.15/2.0; SV=1/h
for gamma in (1e-6, 1e-5, 1e-4, 1e-3):
    vs = gamma*360/4
    keff = 1/(1/km+1/vs)
    print(f"  gamma {gamma:.0e}: removal {1-math.exp(-keff*SV*tres):.0%} (gas-film limit {1-math.exp(-km*SV*tres):.0%})")
print("Poison front: if the bed removes the trace gas near-completely, dead sorbent advances from the inlet:")
for c in (10, 40, 55):
    per = ref.working_capacity*n_air*c*1e-9/9.3  # fraction of total N consumed per cycle at Y=1
    print(f"  {c} ppb, Y=1: {per*1000*100:.1f}% of bed N per 1,000 cycles -> {per*20000:.0%} of the bed (inlet side) consumed after 20,000 cycles")
# COF-999 olefin linkage dose (side note)
wc_cof = 1.28
print(f"COF-999 (wc 1.28): O3 at 40 ppb delivers {wc_cof*n_air*40e-9:.1e} mol per kg per cycle; over 17,752 cycles {wc_cof*n_air*40e-9*17752:.1f} mol/kg")

# ---------------------------------------------------------------------------------------------
hr("IDEA 2. Binderless powdered-resin precoat for moisture swing: kinetics, pressure drop, productivity")
R_bead = 307e-6  # IRA-900 614 um diameter
for name, k in (("drying", 14e-4), ("wetting", 4.5e-4)):
    D = k * R_bead**2 / 15
    print(f"  measured {name} LDF k {k:.1e}/s on 614 um beads -> D_eff {D:.1e} m2/s")
    for r in (150e-6, 50e-6, 25e-6, 10e-6):
        kp = 15 * D / r**2
        print(f"     particle {2*r*1e6:>4.0f} um: k {kp:.1e}/s, t90 {math.log(10)/kp/60:.2f} min")
print("  Shi 2017 sheet: binder D 6.5e-12, 100 um sheet -> L^2/D = %.0f min (measured half-time 31.8 min)" % (1e-8/6.5e-12/60))
# productivity: adsorption LDF approach to equilibrium wc_eq; air supply limit
def prod(wc_eq, k_ads, k_des, t_ads, t_des):
    u = (1-math.exp(-k_ads*t_ads)) * (1-math.exp(-k_des*t_des))  # crude: both steps must complete
    cyc = 86400/(t_ads+t_des)
    return wc_eq*u, productivity(wc_eq*u, cyc)
for label, ka, kd in (("614 um beads (measured k)", 14e-4, 4.5e-4), ("50 um powder (scaled k)", 14e-4*(R_bead/25e-6)**2, 4.5e-4*(R_bead/25e-6)**2)):
    best = max(((prod(1.0, ka, kd, ta*60, td*60), ta, td) for ta in range(2, 241, 2) for td in range(2, 241, 2)), key=lambda z: z[0][1])
    (wc_used, p), ta, td = best
    print(f"  {label:<28}: best productivity {p:.2f} kg/kg/day at {ta}+{td} min (wc used {wc_used:.2f} of 1.0 mol/kg)")
# but air supply sets a floor on adsorption time: air needed per kg per cycle
air_m3 = air_volume_per_tonne(X_AIR, 0.75) / 1e3 * M_CO2  # m3 per mol CO2... compute per mol
air_m3_per_mol = air_volume_per_tonne(X_AIR, 0.75) * M_CO2 / 1e3
print(f"  air needed: {air_m3_per_mol:.1f} m3 per mol CO2 at 75% capture")
for wc in (0.8, 1.0):
    for t_ads_min in (10, 20):
        q = wc * air_m3_per_mol / (t_ads_min*60)
        print(f"   wc {wc} mol/kg, adsorption {t_ads_min} min: {q*1000:.0f} L/s of air per kg resin")
# cake pressure drop (Kozeny-Carman), cake loading
def kc_dp(d, eps, L, v, mu=1.81e-5):
    k = d**2 * eps**3 / (180*(1-eps)**2)
    return mu * v * L / k
for d in (50e-6, 25e-6):
    for L in (0.2e-3, 0.5e-3):
        load = L * 600  # kg/m2 at 0.6 g/cm3 cake density
        for wc, tads in ((1.0, 20*60),):
            v = wc*air_m3_per_mol/tads / (1/load)  # m3/s per kg * kg/m2 = m/s face velocity
            v = wc*air_m3_per_mol/tads * load
            dp = kc_dp(d, 0.40, L, v)
            print(f"   precoat {d*1e6:.0f} um particles, {L*1e3:.1f} mm cake ({load:.2f} kg/m2): face velocity {v*1000:.1f} mm/s, dP {dp:.0f} Pa, fan {fan_work_gj_per_tonne(X_AIR,0.75,dp):.3f} GJ/t")
# drying air vs CO2 air (vapour-mode water swing)
psat25 = 3169.0
w_air = (0.6-0.2)*psat25/P0
for wpm in (17, 24):
    print(f"  water swing {wpm} mol/mol: drying needs {wpm/w_air:,.0f} mol air per mol CO2 (20%->60% RH at 25 C) vs {n_air:,.0f} for CO2 supply")
print(f"  latent heat carried by ambient air: {gj_per_tonne(moisture_swing_water_heat(17)):.1f}-{gj_per_tonne(moisture_swing_water_heat(24)):.1f} GJ/t (free if air is dry enough)")
for cyc, price, wc in ((1380, 15, 0.8), (15000, 15, 0.8), (50000, 15, 0.8), (50000, 10, 1.0)):
    print(f"  resin ${price}/kg, wc {wc}, {cyc} cycles: ${sorbent_cost_per_tonne(price, wc, cyc):.0f}/t")
for label, ka, kd in (("614 um beads", 14e-4, 4.5e-4), ("50 um precoat", 14e-4*(R_bead/25e-6)**2, 4.5e-4*(R_bead/25e-6)**2)):
    for ta, td in ((5,5),(10,10),(20,20),(60,60)):
        wcu, pr = prod(0.9, ka, kd, ta*60, td*60)
        print(f"   {label:<14} {ta}+{td} min (wc_eq 0.9): wc used {wcu:.2f} mol/kg, {pr:.2f} kg/kg/day")
print(f"  productivity at wc 0.8 and 36 cycles/day: {productivity(0.8,36):.2f} kg/kg/day; measured beads 0.19-0.27")

# ---------------------------------------------------------------------------------------------
hr("IDEA 3. Tethered amino-acid (alpha-amino carboxylate) sites: binding window, heat, value of slower oxidation")
# liquid-phase oxidation rate ratio from Kiani 2024 as cited by ORNL: MEA >90% in 500 h, sarcosine <=2%
k_mea = -math.log(0.10)/500; k_sar = -math.log(0.98)/500
print(f"  first-order rates under O2: MEA >= {k_mea:.1e}/h, sarcosine <= {k_sar:.1e}/h -> ratio >= {k_mea/k_sar:.0f}x")
k_pei60 = -math.log(0.85)/18
print(f"  PEI/Al2O3 dry 0.04% CO2-air at 60 C: {k_pei60:.1e}/h (15% in 18 h)")
for N in (3.0,):
    for mode, perN in (("carbamate 0.5 CO2/N", 0.5), ("bicarbonate 1 CO2/N (humid)", 1.0)):
        qmax = N * perN
        for dH in (-65e3, -70e3, -75e3):
            for w in (2.0, 4.0, 6.0):
                c = TVSACycle(dH=dH, dS=-165, q_max=qmax, T_des=C+95, p_des=1e3, water_coads=w)
                if c.working_capacity <= 0: continue
                print(f"  N {N} mmol/g, {mode:<28} dH {dH/1e3:.0f}: fill {loading(P_CO2_AIR,T0,dH,-165,1.0):.0%}, wc {c.working_capacity:.2f}, water {w:.0f} -> heat {c.heat_gj_per_t:.2f} GJ/t, work-eq {c.work_equivalent_gj_per_t:.2f}")
print("  fade value (wc 0.9 mol/kg):")
for rate in (3.5e-3, 3.5e-3/10, 3.5e-3/30):
    print(f"   fade {rate:.1e} %/cycle -> {20/rate:,.0f} cycles: $20/kg ${sorbent_cost_per_tonne(20,0.9,20/rate):.0f}/t, $40/kg ${sorbent_cost_per_tonne(40,0.9,20/rate):.0f}/t")
print("  hygroscopic K-carboxylate penalty: each extra mol H2O per mol CO2 = %.2f GJ/t" % gj_per_tonne(DH_VAP_WATER))

# ---------------------------------------------------------------------------------------------
hr("IDEA 4. Alkali-hydroxide shuttle (soda-lime chemistry) on passive Ca(OH)2 trays for arid air")
# causticisation equilibrium from solubility products (ideal activities)
Ksp_CaOH2 = 5.0e-6; Ksp_CaCO3 = 3.4e-9
K = Ksp_CaOH2/Ksp_CaCO3
print(f"  Ca(OH)2 + CO3-- -> CaCO3 + 2 OH-: K = Ksp(Ca(OH)2)/Ksp(CaCO3) = {K:.0f} M (ideal)")
for oh in (1, 5, 10, 14):
    print(f"   [OH-] {oh} M: equilibrium [CO3--] {oh**2/K:.3f} M (ideal activities; real activity coefficients at >5 M are large, so this is a lower bound)")
# Fick shrinking-front flux (passive bed, supply limited): flux ~ sqrt(2 D c0 rho_reactive / t)
c0 = X_AIR*P0/(R*T0)  # mol/m3
D_eff = 1.6e-5 * 0.5/2.0  # porosity/tortuosity guess for loose powder
rho_ca = 0.5*1000/0.074  # mol Ca(OH)2 per m3 at 0.5 g/cm3 bulk density -> mol/m3
for days in (1, 3, 14):
    t = days*86400
    z = math.sqrt(2*D_eff*c0*t/rho_ca)
    flux = rho_ca*z/t * M_CO2*3.156e7  # kg/m2/yr
    print(f"   {days:>2}-day cycle: front {z*1e3:.1f} mm, {flux:.0f} kg CO2/m2/yr (gas-supply limited; humidity- and passivation-free)")
for L in (5, 10):
    pass
dHcalc = 178.3e3
print(f"  calcination reaction heat {gj_per_tonne(dHcalc):.2f} GJ/t; map estimate 7.1 GJ/t without heat recovery, 5.8 with 50% recovery")
for w_koh in (0.02, 0.04):
    caoh2_per_t = 74.09/44.01/0.85  # t Ca(OH)2 cycled per t CO2 at 85% conversion
    koh = caoh2_per_t*w_koh
    for loss in (0.05, 0.2):
        print(f"   KOH {w_koh:.0%} of Ca(OH)2 ({koh*1e3:.0f} kg/t CO2), {loss:.0%} lost per calcination -> make-up {koh*loss*1e3:.1f} kg KOH/t = ${koh*loss*1e3*1.0:.1f}/t at $1/kg")
    film_water = koh*1.5  # t water held by film at ~30-40% RH (assume 1.5 g/g KOH)
    print(f"   film water carried to kiln ~{film_water*1e3:.0f} kg/t -> {film_water*1e6/18.015*DH_VAP_WATER/1e9:.2f} GJ/t extra latent")
print(f"  limestone sorbent cost at $0.15/kg, 10 cycles: ${0.15/(11.5*M_CO2*0.85*10)*1e3:.0f}/t (map: ~$22/t)")
print(f"  humidifying 20%->80% RH instead (map): ~37 t water/t CO2")

# ---------------------------------------------------------------------------------------------
hr("IDEA 5. Moisture-swing resin as a passive pre-concentrator for an O2-tolerant MnO2 electro-swing cell")
def t_per_m2_yr(j_mA_cm2, ce, e_per_co2=1.0, duty=0.5):
    mol_s = j_mA_cm2*10/FARADAY*ce/e_per_co2*duty
    return mol_s*M_CO2*3.156e7/1000
for label, j, ce in (("air, 1 mA/cm2, CE 0.25 (measured air case)", 1, 0.25), ("4% CO2, 50 mA/cm2, CE 0.30", 50, 0.30), ("4% CO2, 50 mA/cm2, CE 0.80", 50, 0.80)):
    a = t_per_m2_yr(j, ce)
    for price in (300, 1000):
        print(f"  {label:<45}: {a:.3f} t/m2/yr -> cell capital ${price*0.14/a:,.0f}/t at ${price}/m2 (14%/yr)")
print("  measured MnO2 areal productivity in air 0.0084 t/m2/yr")
# gas-film supply cap for air-breathing electrode
for kg in (0.01, 0.05):
    for pk in (0.0426, 3.0):
        flux = kg * pk*1e3/(R*T0)  # mol/m2/s
        j = flux*FARADAY/10  # mA/cm2 at 1 e-/CO2
        print(f"  gas-film supply k_g {kg} m/s at {pk:.3g} kPa CO2: {flux:.1e} mol/m2/s -> max {j:.1f} mA/cm2 at 1 e-/CO2")
e_cell_air, e_cell_4 = 4.1, 1.7
print(f"  cell energy (measured): air release into pure CO2 {e_cell_air} GJ/t; 4% CO2 at 50 mA/cm2 {e_cell_4} GJ/t")
fan_loop = fan_work_gj_per_tonne(0.03, 0.5, 300)
print(f"  loop blower (3% CO2, 50% stripped per pass, 300 Pa): {fan_loop:.3f} GJ/t")
fan_air = fan_work_gj_per_tonne(X_AIR, 0.75, 100)
for e_cell in (1.7, 2.5):
    tot = e_cell + fan_loop + fan_air
    print(f"  total electricity {e_cell}+{fan_loop:.2f}+{fan_air:.2f} = {tot:.2f} GJ/t = {tot/0.0036:.0f} kWh/t; 2nd-law {floor/tot:.0%}; ${tot/0.0036*0.05:.0f}/t at $50/MWh")
print(f"  compare: VMS modelled ~2.5 GJ/t electric; MnO2 air cell 3.9-4.1 + 1-2 GJ/t vacuum/compression")
for pk in (2, 4):
    w = R*T0*math.log(P0/(pk*1e3))/0.7
    print(f"  alternative: vacuum-compress {pk} kPa CO2 to 1 atm: {gj_per_tonne(w):.2f} GJ/t (plus vapour handling)")

# ---------------------------------------------------------------------------------------------
hr("IDEA 6. Reductive repair of oxidised amine sites (imine -> amine), value per tonne")
for rate, rshare, every, cost_kg in ((3.5e-3, 0.5, 2000, 1.5), (3.5e-3, 0.3, 2000, 1.5), (2.2e-3, 0.5, 3000, 1.5), (3.5e-3, 0.5, 2000, 4.0)):
    base_cycles = 20/rate
    life = 20/(rate*(1-rshare))
    n_rep = life/every
    base = sorbent_cost_per_tonne(20, ref.working_capacity, base_cycles)
    new = sorbent_cost_per_tonne(20, ref.working_capacity, life)
    rep = sorbent_cost_per_tonne(n_rep*cost_kg, ref.working_capacity, life)
    print(f"  fade {rate:.1e}, repairable {rshare:.0%}, repair every {every} cycles at ${cost_kg}/kg: life {base_cycles:,.0f} -> {life:,.0f} cycles; sorbent ${base:.0f}/t -> ${new:.0f}/t + repair ${rep:.0f}/t = net saving ${base-new-rep:.0f}/t")
N_lost = 9.3*0.10
print(f"  reagent stoichiometry: restoring 10% of 9.3 mol N/kg = {N_lost:.2f} mol C=N/kg -> 0.25-1 mol borohydride each = {N_lost*0.25*37.8:.0f}-{N_lost*37.8:.0f} g/kg")
