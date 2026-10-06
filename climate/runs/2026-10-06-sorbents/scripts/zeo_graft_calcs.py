import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

def psat(Tc):  # Buck equation, Pa, over liquid water
    return 611.21*math.exp((18.678 - Tc/234.5)*(Tc/(257.14+Tc)))

ref = reference_amine_cycle()
def show(label, c):
    print(f"{label}: wc {c.working_capacity:.3f} mol/kg | heat {c.heat_gj_per_t:.2f} GJ/t (rxn {gj_per_tonne(c.reaction_heat):.2f}, "
          f"sens {gj_per_tonne(c.sensible_heat):.2f}, water {gj_per_tonne(c.water_heat):.2f}) | work-eq {c.work_equivalent_gj_per_t:.2f} | 2nd-law {c.second_law_efficiency:.0%}")
show("REFERENCE", ref)
fade_budget = 20.0/20000  # %/cycle for 20% loss over 20,000 cycles
print(f"fade budget for 20% over 20,000 cycles: {fade_budget:.2e} %/cycle\n")

print("=== IDEA 1: OZONE DOSE (mass balance, capacity- and cycle-time-independent) ===")
phi = 0.75
for ppb in (10, 30, 40, 60):
    r = ppb*1e-9/(X_AIR*phi)       # mol O3 per mol CO2 captured
    g_per_t = r/M_CO2*1e3*0.048     # g O3 per tonne CO2 (1 t CO2 = 1e3/M mol)
    mol_per_t = r*1e3/M_CO2
    print(f"O3 {ppb:>3} ppb: {r:.2e} mol O3/mol CO2 = {mol_per_t:.2f} mol ({g_per_t:.0f} g) O3 per t CO2; fade = Y x {r*100:.4f} %/cycle;"
          f" Y that uses whole budget = {fade_budget/(r*100):.3f}")
# field fade bound: Climeworks Gen2 target ~10%/3000 cycles = 3.3e-3 %/cycle (map says ~3.5e-3)
for ppb in (30, 40):
    r = ppb*1e-9/(X_AIR*phi)
    print(f"  at {ppb} ppb, observed field fade 3.5e-3 %/cycle bounds Y <= {3.5e-3/(r*100):.2f} (if O3 were the only cause and fully deposited)")
# sorbent cost implied (replace at 20% loss), 1.04 mol/kg, $20 and $50/kg
print("Sorbent replacement cost attributable to O3 (replace at 20% loss; wc 1.04 mol/kg):")
for ppb in (30, 40):
    r = ppb*1e-9/(X_AIR*phi)
    for Y in (0.03, 0.1, 0.28):
        fade = Y*r*100
        cyc = 20.0/fade
        print(f"  {ppb} ppb, Y={Y}: fade {fade:.2e} %/cycle alone -> life {cyc:,.0f} cycles -> ${sorbent_cost_per_tonne(20,1.04,cyc):.0f}/t at $20/kg, ${sorbent_cost_per_tonne(50,1.04,cyc):.0f}/t at $50/kg")
# Combined: other causes 2.2e-3 (TDA-like) plus ozone
for Y in (0.05, 0.1, 0.2):
    r = 40e-9/(X_AIR*phi); oz = Y*r*100
    base = 2.2e-3
    c1 = sorbent_cost_per_tonne(20,1.04,20/(base+oz)); c0 = sorbent_cost_per_tonne(20,1.04,20/base)
    print(f"  40 ppb, Y={Y}: total fade {base+oz:.2e} vs {base:.1e} without O3 -> ${c1:.0f}/t vs ${c0:.0f}/t at $20/kg (guard worth ${c1-c0:.0f}/t)")
fan20 = fan_work_gj_per_tonne(X_AIR, 0.75, 20.0)
print(f"Guard face at 20 Pa adds fan work {fan20:.3f} GJ/t = {fan20/3.6*1000:.0f} kWh/t = ${energy_cost_floor(fan20,50):.2f}/t at $50/MWh")
# stoichiometric sacrificial carbon need: 1 C per O3 upper-ish
r = 40e-9/(X_AIR*phi); print(f"Sacrificial scavenger at 1 mol C per mol O3: {r*1e3/M_CO2*12:.0f} g C per t CO2 at 40 ppb")
# Literature dose check: Zorrilla-Valtierra 2026: 50 ppm, 50 mL/min, 8 h, 80 mg
n = 50e-6*0.050*480/24.45; per_kg = n/80e-6
print(f"IECR 2026 exposure dose: {n:.2e} mol O3 on 80 mg = {per_kg:.2f} mol/kg = {per_kg/(40e-9/(X_AIR*phi)*1.04):,.0f} cycle-equivalents at 40 ppb, wc 1.04 (if fully absorbed)\n")

print("=== IDEA 2: O2 EXPOSURE BUDGET PER CYCLE (residual void O2 and warm-air re-entry) ===")
# Measured rates (dry 0.04% CO2 air, PEI/Al2O3): 60 C: 15%/18 h at 21 kPa O2; 70 C: 17%/3 h (Guta 2023)
k60 = 15.0/(21.0*18*3600)   # % per kPa.s
k70 = 17.0/(21.0*3*3600)
print(f"Linear exposure coefficients: 60 C {k60:.2e} %/(kPa.s); 70 C {k70:.2e} %/(kPa.s)")
print(f"O2 exposure allowed per cycle for whole budget ({fade_budget:.1e} %): {fade_budget/k60:.1f} kPa.s at 60 C, {fade_budget/k70:.1f} kPa.s at 70 C")
for label, pO2, t in [("warm-air re-entry, bed 60-70 C for 60 s", 21.0, 60), ("residual void air, p_evac 10 kPa, 60 s hot", 2.1, 60),
                      ("residual void air, p_evac 2 kPa, 60 s hot", 0.42, 60), ("residual void air, p_evac 0.5 kPa, 60 s hot", 0.105, 60)]:
    E = pO2*t
    print(f"  {label}: {E:.0f} kPa.s -> {E*k60:.2e} %/cycle (60 C rate) / {E*k70:.2e} %/cycle (70 C rate)")
for V in (1.0, 2.5):
    for pev in (10e3, 2e3, 0.5e3):
        nO2 = 0.21*pev*V*1e-3/(R*T0)
        print(f"  void {V} L/kg, evacuated to {pev/1e3:.1f} kPa: {nO2:.2e} mol O2/kg/cycle = {nO2/1.04:.1e} mol O2 per mol CO2 working capacity")
# vacuum work to evacuate void deeper (isothermal, 70% efficient), per mol CO2
for V in (2.5,):
    nair = P0*V*1e-3/(R*T0)
    for p in (10e3, 2e3, 0.5e3):
        w = nair*R*T0*math.log(P0/p)/0.7/1.04   # crude upper bound: all void gas compressed from p to 1 atm
        print(f"  evac void {V} L/kg to {p/1e3} kPa: <= {w/1e3:.2f} kJ/mol CO2 = {gj_per_tonne(w):.3f} GJ/t")
print()

print("=== IDEA 3: HYDROPHOBIC END-CAPPING (Kelvin cut-off) ===")
gam, Vm = 0.072, 1.807e-5
for r_nm in (1.5, 3.0, 5.0):
    for theta in (0, 60, 75, 90):
        c = math.cos(math.radians(theta))
        rk = (r_nm-0.35)*1e-9   # subtract ~1 monolayer film
        rh = math.exp(-2*gam*Vm*c/(rk*R*T0)) if c > 1e-9 else float('nan')
        print(f"  pore radius {r_nm} nm, contact angle {theta:>2} deg: capillary condensation at RH {rh:.0%}" if c > 1e-9 else f"  pore radius {r_nm} nm, contact angle 90: no capillary condensation")
# water/CO2 ratios from amine-alumina data (map): water 3.2 (40%), 4.2 (50%), 9.9 (80%) mmol/g; CO2 ~0.55 mmol/g humid
co2 = 0.55
for rh, w in ((40,3.2),(50,4.2),(80,9.9)):
    print(f"  amine-alumina {rh}% RH: {w/co2:.1f} mol H2O per mol CO2")
for w in (2.0, 3.0, 7.6, 18.0):
    c = TVSACycle(dH=-70e3, dS=-165.0, q_max=2.0, water_coads=w)
    show(f"  ref cycle with {w} mol H2O/mol CO2", c)
# capillary water removed if 80% RH condensate capped at the 40% RH value
print(f"  Capping 80%-RH water at the 40%-RH level removes {(9.9-3.2)/co2:.1f} mol/mol = {gj_per_tonne((9.9-3.2)/co2*DH_VAP_WATER):.1f} GJ/t; at 50% RH removes {(4.2-3.2)/co2:.1f} mol/mol = {gj_per_tonne((4.2-3.2)/co2*DH_VAP_WATER):.1f} GJ/t")
# Heat-pump electricity value of 6 GJ/t heat at COP 3, $50/MWh
print(f"  6.0 GJ/t heat saved = ${energy_cost_floor(6.0/3,50):.0f}/t via COP-3 heat pump at $50/MWh, ${6.0*5:.0f}/t at $5/GJ steam\n")

print("=== IDEA 4: PROMOTED SUPPORTED K2CO3 (step chemistry) ===")
dH = 140.06e3; dS = 327.13   # 2KHCO3 -> K2CO3 + CO2 + H2O(g), NBS 298 K values
def Keq(T): return math.exp(-(dH - T*dS)/(R*T))   # bar^2
for rh in (20, 50, 80):
    pw = rh/100*psat(25)/1e5
    print(f"  25 C, {rh}% RH: equilibrium CO2 over K2CO3/KHCO3 = {Keq(T0)/pw*1e6:.1f} ppm (anhydrous salt)")
for pc, pw in ((1e3,1e3),(2e3,2e3),(5e3,5e3),(2e3,10e3)):
    T = dH/(dS - R*math.log(pc/1e5*pw/1e5))
    print(f"  regeneration onset at p_CO2 {pc/1e3:.0f} kPa, p_H2O {pw/1e3:.0f} kPa: {T-273.15:.0f} C")
T = dH/(dS - R*math.log(0.25)); print(f"  1 bar total (0.5/0.5): {T-273.15:.0f} C")
M_K2CO3 = 0.13821
for wt, u in ((0.30,0.9),(0.40,0.7),(0.40,0.9)):
    nK = wt/M_K2CO3; wc = nK*u
    sens = 950*(363.15-T0)/wc            # composite cp ~950 J/kg/K, 25 -> 90 C
    brine = (1-u)*nK*6.9/wc              # >= 6.9 mol water per mol unconverted K2CO3 above 43% RH (saturated-solution bound)
    phys = 0.5                            # mol physisorbed water per mol CO2 on hydrophobic carbon (assumption)
    q = dH + sens + (brine+phys)*DH_VAP_WATER
    carnot = 1 - T0/363.15
    vac = R*T0*math.log(P0/2e3)/0.7
    weq = gj_per_tonne(q*carnot + vac) + fan_work_gj_per_tonne(X_AIR,0.75,100)
    print(f"  {wt:.0%} K2CO3, {u:.0%} conversion: wc {wc:.2f} mol/kg | heat {gj_per_tonne(q):.2f} GJ/t (rxn incl. 1 H2O {gj_per_tonne(dH):.2f}, sens {gj_per_tonne(sens):.2f}, brine water {gj_per_tonne(brine*DH_VAP_WATER):.2f}, phys water {gj_per_tonne(phys*DH_VAP_WATER):.2f}) | work-eq {weq:.2f} GJ/t")
    for price in (4, 8):
        print(f"     sorbent cost at ${price}/kg: ${sorbent_cost_per_tonne(price,wc,2000):.0f}/t @2,000 cyc, ${sorbent_cost_per_tonne(price,wc,10000):.0f}/t @10,000")
# film kinetics in concentrated carbonate brine (order-of-magnitude)
D = 1.9e-9; c_i = 1e-3*1e3*X_AIR*P0/101325  # mol/m3: ~1e-3 M/atm after salting-out x 420 ppm
for label, k1 in (("OH- route early (pH~12.5)", 8500*0.032), ("OH- route at 50% conversion (pH~10.3)", 8500*2e-4), ("+0.5 M glycinate (k2 1.3e4)", 1.3e4*0.5)):
    kL = math.sqrt(D*k1); flux = kL*c_i
    print(f"  {label}: k1 {k1:.3g} 1/s, kL {kL:.2e} m/s, flux {flux:.2e} mol/m2/s -> {flux*10*60*1e3:.3f} mmol/g/min per 10 m2/g film area")
print()

print("=== IDEA 5: MECHANICAL VAPOUR RECOMPRESSION OF PRODUCT (CO2 + H2O) ===")
lat = 40.7e3
for P1_kPa, Tsteam in ((101.3, 100.0), (50.0, 81.3), (20.0, 60.1)):
    for w in (2.0, 4.0, 8.0):
        r = 0.5          # condense to 0.5 mol H2O per mol CO2
        Tcond = Tsteam + 5
        P2 = psat(Tcond)*(1+r)/r/1e3   # kPa
        P2 = max(P2, P1_kPa)
        Tin = Tsteam + 273.15
        W = (1+w)*R*Tin*math.log(P2/P1_kPa)/0.65
        Wco2_needed = R*Tin*math.log(max(P0/1e3, P2)/P1_kPa)/0.65 if P1_kPa < 101.3 else 0.0
        Q = (w-r)*lat
        print(f"  product at {P1_kPa:.0f} kPa ({Tsteam:.0f} C steam), {w} mol H2O/mol CO2: compress to {P2:.0f} kPa, work {W/1e3:.1f} kJ/mol "
              f"({gj_per_tonne(W):.2f} GJ_e/t), latent recovered {gj_per_tonne(Q):.2f} GJ/t, COP {Q/W:.1f}")
for w in (2.0, 8.0):
    c = TVSACycle(dH=-70e3, dS=-165.0, q_max=2.0, water_coads=w)
    W = (1+w)*R*373.15*math.log((psat(105)*1.5/0.5/1e3)/101.3)/0.65; Q = (w-0.5)*lat
    print(f"  ref cycle, {w} mol/mol water: heat {c.heat_gj_per_t:.2f} -> {c.heat_gj_per_t-gj_per_tonne(Q):.2f} GJ/t net heat + {gj_per_tonne(W):.2f} GJ_e/t compressor")
print()

print("=== IDEA 6: STRIP-AND-REIMPREGNATE REJUVENATION ===")
wc = ref.working_capacity
for life in (2000, 5000, 10000):
    for new_price in (20, 50):
        new = sorbent_cost_per_tonne(new_price, wc, life)
        # refresh: PEI 0.4 kg/kg at $5/kg + $3/kg processing; 90% capacity recovery -> life-averaged capacity slightly lower
        refresh_cost = 0.4*5 + 3.0
        support_share = new_price/5   # support replaced every 5 refreshes
        per_life = refresh_cost + support_share
        rej = sorbent_cost_per_tonne(per_life, wc*0.95, life)
        print(f"  life {life:>6} cycles, new laminate ${new_price}/kg: replace ${new:.0f}/t vs rejuvenate ${rej:.0f}/t (refresh ${refresh_cost:.0f}/kg + support amortised ${support_share:.0f}/kg)")
