import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
GJ = gj_per_tonne
PB = 1.0e5
PSAT = lambda T: 610.94*math.exp(17.625*(T-273.15)/(T-273.15+243.04))
floor60 = GJ(min_separation_work(X_AIR, 0.6, 0.99, T0)); floor75 = GJ(min_separation_work(X_AIR, 0.75, 0.99, T0))
# NBS (Wagman 1982) dHf kJ/mol, S J/mol/K
D = {'NaHCO3': (-950.81, 101.7), 'Na2CO3': (-1130.68, 134.98), 'Na2CO3.H2O': (-1431.26, 168.11),
     'Na2CO3.10H2O': (-4081.32, 562.7), 'trona': (-2682.1, 303.3),
     'CO2': (-393.51, 213.74), 'H2O_g': (-241.82, 188.83)}
def rxn(r, p, shift_trona=0.0):
    dH = sum(n*D[s][0] for s,n in p.items()) - sum(n*D[s][0] for s,n in r.items())
    dS = sum(n*D[s][1] for s,n in p.items()) - sum(n*D[s][1] for s,n in r.items())
    # shift_trona: raise trona Gibbs energy by this many kJ/mol (entropic, i.e. applied to S)
    nt = p.get('trona',0) - r.get('trona',0)
    return dH*1e3, dS - nt*shift_trona*1e3/298.15
def lnK(dH, dS, T): return -(dH - T*dS)/(R*T)

# Jagniecki et al. 2015 (Geology): minimum CO2 for nahcolite vs trona, NaCl-saturated brine: 170*exp(0.0713 T_C) ppm
def jag_ppm(Tc, aw=0.75): return 170*math.exp(0.0713*Tc)*aw/0.75   # trona + CO2 = 3 nahcolite + H2O  => p_b proportional to a_w
# anchor the trona shift so NBS reproduces Jagniecki at 25 C, aw 0.75
r_tn = ({'trona':1,'CO2':1}, {'NaHCO3':3,'H2O_g':1})
def p_tn(Tc, aw, shift):
    dH, dS = rxn(*r_tn, shift_trona=shift); T = Tc+273.15
    # K = p_w/p_CO2 (bar) -> p_CO2 = p_w/K
    return aw*PSAT(T)/math.exp(lnK(dH,dS,T))
from scipy.optimize import brentq
shift = brentq(lambda s: p_tn(25, 0.75, s) - 1010e-6*PB, -20, 20)
print(f"NBS trona/nahcolite boundary at 25 C, a_w 0.75: {p_tn(25,0.75,0)/PB*1e6:.0f} ppm; Jagniecki measured 1010 ppm -> trona destabilised by {-shift:.2f} kJ/mol? (shift {shift:.2f})")
print(f"check Jagniecki-anchored at 19.5 C: {p_tn(19.5,0.75,shift)/PB*1e6:.0f} ppm vs calibration {jag_ppm(19.5):.0f}")

print("\n=== A. Sodium phase windows at 420 ppm CO2: which solid is the capture product? ===")
r_mn = ({'Na2CO3.H2O':1,'CO2':1}, {'NaHCO3':2})               # p* indep of RH
r_mt = ({'Na2CO3.H2O':3,'CO2':1,'H2O_g':2}, {'trona':2})        # p* ~ 1/p_w^2
r_hyd = ({'Na2CO3':1,'H2O_g':1}, {'Na2CO3.H2O':1})
r_nat = ({'Na2CO3.H2O':1,'H2O_g':9}, {'Na2CO3.10H2O':1})
print(" T C  RH  | thermonatrite stable? natron stable? | p*(mono->nahcolite) ppm | p_b trona/nahcolite ppm (Jagniecki) | p*(mono->trona) ppm NBS / anchored | product at 420 ppm | nahcolite capture ceiling")
for Tc in (-10, 0, 5, 10, 15, 20, 25, 30, 35):
    T = Tc+273.15
    for rh in (0.2, 0.4, 0.6, 0.8):
        pw = rh*PSAT(T)
        mono_ok = pw > PB/math.exp(lnK(*rxn(*r_hyd), T))
        nat = (pw/PB)**9 > 1/math.exp(lnK(*rxn(*r_nat), T))
        pmn = PB/math.exp(lnK(*rxn(*r_mn), T))/PB*1e6
        pb = jag_ppm(Tc, rh)
        dH, dS = rxn(*r_mt); pmt = 1/(math.exp(lnK(dH,dS,T))*(pw/PB)**2)*1e6
        dH2, dS2 = rxn(*r_mt, shift_trona=shift); pmt2 = 1/(math.exp(lnK(dH2,dS2,T))*(pw/PB)**2)*1e6
        if 420 > pb and 420 > pmn: prod = "NAHCOLITE"
        elif 420 > pmt2 or 420 > pmt: prod = "trona" if 420 > pmt2 else "trona(NBS only)"
        else: prod = "none"
        ceil = max(0.0, 1 - max(pb, pmn)/420)
        if rh in (0.2, 0.6) or Tc in (5, 25):
            print(f"{Tc:4d} {rh*100:3.0f}% | {str(mono_ok):5s} {str(nat):5s} | {pmn:7.0f} | {pb:7.0f} | {pmt:9.1f} / {pmt2:9.1f} | {prod:16s} | {ceil:4.0%}")

print("\n=== B. Release energetics and pressures ===")
rel_nah = ({'NaHCO3':2}, {'Na2CO3':1,'CO2':1,'H2O_g':1})
dH, dS = rxn(*rel_nah)
print(f"2 NaHCO3 -> Na2CO3 + CO2 + H2O: dH {dH/1e3:.1f} kJ/mol ({GJ(dH):.2f} GJ/t), dS {dS:.0f} J/mol/K")
for Tc in (60, 70, 80, 90):
    T=Tc+273.15; K=math.exp(lnK(dH,dS,T))
    s = f"  {Tc} C: vacuum 1:1 p_each {math.sqrt(K)*100:.2f} kPa"
    for pw_kpa, lab in ((1.0,'7 C condenser'), (0.26,'-10 C air-cooled condenser (winter)')):
        s += f" | p_w {pw_kpa} kPa ({lab}): p_CO2 {K/(pw_kpa/100)*100:.1f} kPa"
    print(s)
for pw_kpa in (1.0, 0.26):
    T1 = brentq(lambda T: math.exp(lnK(dH,dS,T))/(pw_kpa/100) - 1.0, 300, 500)
    print(f"  NaHCO3: T for 1 bar CO2 with p_w pinned at {pw_kpa} kPa: {T1-273.15:.0f} C")
for sh, lab in ((0.0,'NBS trona'), (shift,'Jagniecki-anchored trona')):
    dHt, dSt = rxn({'trona':2}, {'Na2CO3.H2O':3,'CO2':1,'H2O_g':2}, shift_trona=sh)
    out = f"2 trona -> 3 Na2CO3.H2O + CO2 + 2 H2O ({lab}): dH {dHt/1e3:.1f} kJ/mol ({GJ(dHt):.2f} GJ/t), dS {dSt:.0f};"
    for pw_kpa in (1.0, 0.26):
        T1 = brentq(lambda T: math.exp(lnK(dHt,dSt,T))/((pw_kpa/100)**2) - 1.0, 250, 500)
        out += f" 1 bar CO2 at p_w {pw_kpa} kPa: {T1-273.15:.0f} C;"
    for Tc in (40, 50, 60):
        T=Tc+273.15; K=math.exp(lnK(dHt,dSt,T)); out += f" {Tc} C p_w 1 kPa -> p_CO2 {min(K/1e-4,99)*100:.1f} kPa;"
    # monohydrate must remain stable at release T with p_w pinned (else dehydrates: extra 58.8 kJ per mono)
    print(out)
print(f"  thermonatrite dehydration p_eq: 40 C {PB/math.exp(lnK(*rxn(*r_hyd),313.15))/1e3:.1f} kPa, 60 C {PB/math.exp(lnK(*rxn(*r_hyd),333.15))/1e3:.1f} kPa, 70 C {PB/math.exp(lnK(*rxn(*r_hyd),343.15))/1e3:.1f} kPa  (pinning p_w at 1 kPa dehydrates it -> +58.8 kJ per Na2CO3 unit unless p_w kept above p_eq)")
# Trona capture ceiling vs RH at 25 and 35 C with anchored data
for Tc in (25, 30, 35):
    T=Tc+273.15
    row=[]
    for rh in (0.5,0.7,0.85):
        pw=rh*PSAT(T)
        dH2, dS2 = rxn(*r_mt, shift_trona=shift); p2 = 1/(math.exp(lnK(dH2,dS2,T))*(pw/PB)**2)*1e6
        dH1, dS1 = rxn(*r_mt); p1 = 1/(math.exp(lnK(dH1,dS1,T))*(pw/PB)**2)*1e6
        row.append(f"RH {rh:.0%}: p* {p1:.0f}/{p2:.0f} ppm ceiling {max(0,1-p1/420):.0%}/{max(0,1-p2/420):.0%}")
    print(f"  trona capture {Tc} C (NBS/anchored): " + "; ".join(row))

print("\n=== C. Cycle heat per tonne (40 wt% Na2CO3 on carbon, cp 800/1100 J/kg/K) ===")
M = 0.10599; wt = 0.40; nNa = wt/M; cp = (1-wt)*800 + wt*1100
# nahcolite cycle: capture at 5 C, release at 75 C with p_w pinned 0.26-1 kPa (thermonatrite dehydrates -> anhydrous)
for x in (0.5, 0.8):
    wc = x*nNa; sens = cp*70/wc; Q = 135.6e3 + (1-x)/x*58.8e3 + sens
    T_des = 348.15
    pdes = 1.0e5  # condenser loop delivers ~1 bar at ~92 C; at 75 C use p_CO2 from K/p_w
    K = math.exp(lnK(*rxn(*rel_nah), T_des)); pco2 = min(K/0.0026*1e5, 1e5)
    vac = R*278.15*math.log(P0/pco2)/0.7 if pco2 < P0 else 0
    chill = 1*44e3/ (0.5*278.15/ (308.15-278.15)) # condensing 1 mol water at 5 C, reject at 35 C, COP 0.5 Carnot
    weq = GJ(Q*(1-278.15/T_des) + vac + chill) + fan_work_gj_per_tonne(X_AIR, 0.6, 100.0)
    print(f" nahcolite, conversion {x:.0%}: wc {wc:.2f} mol/kg, heat {GJ(Q):.2f} GJ/t at 75 C (rxn 3.08 + residual hydrate {GJ((1-x)/x*58.8e3):.2f} + sensible {GJ(sens):.2f}); "
          f"p_CO2 {pco2/1e3:.0f} kPa with -10 C condenser; work-eq {weq:.2f} GJ/t; 2nd-law {floor60/weq:.0%}; HP elec (COP {0.5*353.15/(353.15-278.15):.2f}) {GJ(Q)/(0.5*353.15/(353.15-278.15)):.2f} GJ/t")
# trona cycle: capture 25 C humid; release 60 C, p_w pinned at ~15 kPa? -> must keep thermonatrite (p_eq 8.3 kPa at 60 C)
for sh, lab in ((0.0,'NBS'), (shift,'anchored')):
    dHt, dSt = rxn({'trona':2}, {'Na2CO3.H2O':3,'CO2':1,'H2O_g':2}, shift_trona=sh)
    for Tc in (60, 70):
        T = Tc+273.15; pw = 1.2*PB/math.exp(lnK(*rxn(*r_hyd),T))  # 20% above thermonatrite dehydration line
        K = math.exp(lnK(dHt,dSt,T)); pco2 = K/((pw/PB)**2)*PB
        print(f" trona release {lab} at {Tc} C keeping thermonatrite (p_w {pw/1e3:.1f} kPa): p_CO2 {pco2/1e3:.2f} kPa -> steam:CO2 {pw/pco2:.1f}")
x=0.8; wc_t = x*nNa/3  # 1 CO2 per 3 Na2CO3
sens_t = cp*35/wc_t
for dHt_k in (193.2,):
    Qt = dHt_k*1e3 + sens_t
    print(f" trona cycle 40 wt%, 80% conversion: wc {wc_t:.2f} mol/kg, heat {GJ(Qt):.2f} GJ/t at 60 C (rxn {GJ(dHt_k*1e3):.2f} incl. 2 H2O, sensible {GJ(sens_t):.2f}); HP elec (COP {0.5*338.15/(338.15-293.15):.2f}) {GJ(Qt)/(0.5*338.15/(338.15-293.15)):.2f} GJ/t")

print("\n=== D. Sorbent cost (40 wt% Na2CO3 on activated carbon) ===")
for price in (2.0, 5.0):
    for wc, lab in ((3.0,'nahcolite x0.8'), (1.0,'trona x0.8'), (0.5,'pessimistic')):
        print(f"  ${price}/kg, wc {wc} ({lab}): 1,000 cycles ${sorbent_cost_per_tonne(price, wc, 1000):.1f}/t, 5,000 cycles ${sorbent_cost_per_tonne(price, wc, 5000):.1f}/t")
print(f"  productivity, nahcolite x0.8 at 4 cycles/day: {productivity(3.0,4):.2f} kg/kg/day; trona 1.0 mol/kg at 4/day: {productivity(1.0,4):.2f}")

print("\n=== E. K2CO3 sesquihydrate sink (for the record) ===")
dHw, Tq, pq = 65.8e3, 335.15, 1200.0
dSw = (dHw + R*Tq*math.log(pq/1.013e5))/Tq
dHK = (2*-963.2 - (-1151.02 + 1.5*-241.82 - 1.5*65.8) - (-393.51) + 0.5*-241.82)*1e3   # K2CO3.1.5H2O + CO2 -> 2KHCO3 + 0.5 H2O(g), capture
SK = 155.52 + 1.5*188.83 - 1.5*dSw
dSK = 2*115.5 + 0.5*188.83 - SK - 213.74
for Tc in (5, 25, 35):
    T=Tc+273.15; out=[]
    for rh in (0.2,0.5,0.8):
        pw=rh*PSAT(T); p=math.sqrt(pw/PB)/math.exp(lnK(dHK,dSK,T))*1e6
        out.append(f"RH {rh:.0%} {p:.0f} ppm")
    print(f"  K2CO3.1.5H2O + CO2 equilibrium at {Tc} C: " + ", ".join(out) + f"  (anhydrous-K2CO3 assumption at 50% RH 25 C gives 2 ppm)")
