import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
from scipy.optimize import brentq
GJ = gj_per_tonne
floor75 = GJ(min_separation_work(X_AIR, 0.75, 0.99, T0))

print("=== 1. Frumkin (interacting-site) isotherm: theta/(1-theta) = b p exp(J theta / RT); J<0 anti-cooperative (polyelectrolyte), J>0 cooperative ===")
def theta_frumkin(p, T, dH, dS, J):
    # solve; for J > 4RT pick the branch by continuation from low theta (adsorption) - here report equilibrium (Maxwell) branch
    lbp = -(dH - T*dS)/(R*T) + math.log(p/P_REF)
    f = lambda th: math.log(th/(1-th)) - lbp - J*th/(R*T)
    lo, hi = 1e-300, 1-1e-16
    if f(lo) > 0: return 0.0
    if f(hi) < 0: return 1.0
    if J <= 4*R*T:
        return brentq(f, lo, hi)
    # Maxwell construction: symmetric Frumkin -> transition where ln(bp) + J/(2RT) = 0
    x = lbp + J/(2*R*T)
    roots = []
    grid = [i/2000 for i in range(1,2000)]
    for a, c in zip(grid[:-1], grid[1:]):
        if f(a)*f(c) < 0: roots.append(brentq(f, a, c))
    if not roots: return brentq(f, lo, hi)
    return max(roots) if x > 0 else min(roots)
def T_for(p, dH, dS, J, th):
    return brentq(lambda T: theta_frumkin(p, T, dH, dS, J) - th, 250, 700)
print(f"{'J kJ/mol':>9}{'dH set for 65% @420ppm':>24}{'T(10% @1kPa) C':>16}{'wc(q2)':>8}{'heat GJ/t':>10}{'work-eq':>9}")
for J in (-15e3, -8e3, 0.0, 6e3, 9.5e3):
    dS = -165.0
    # choose dH so ambient fill = 0.65 (adsorption branch)
    dH = brentq(lambda h: theta_frumkin(P_CO2_AIR, T0, h, dS, J) - 0.65, -120e3, -40e3)
    Td = T_for(1e3, dH, dS, J, 0.10)
    q = 2.0; wc = q*(theta_frumkin(P_CO2_AIR, T0, dH, dS, J) - theta_frumkin(1e3, Td, dH, dS, J))
    sens = 1500*(Td-T0)/wc; heat = -dH + sens + 2*44e3
    weq = GJ(heat*(1-T0/Td) + R*T0*math.log(P0/1e3)/0.7) + fan_work_gj_per_tonne(X_AIR,0.75,100.0)
    print(f"{J/1e3:9.0f}{dH/1e3:24.1f}{Td-273.15:16.1f}{wc:8.2f}{GJ(heat):10.2f}{weq:9.2f}")
print("  (water 2 mol/mol, cp 1500; J>4RT=9.9 kJ/mol gives a first-order step)")
for J in (12e3, 16e3):
    dS = -165.0
    # step (Maxwell) at 10 Pa and 25 C: -(dH - T dS)/RT + ln(p/PREF) = -J/(2RT)
    dH = T0*dS + R*T0*(math.log(10/P_REF) + J/(2*R*T0))
    Td = brentq(lambda T: -(dH - T*dS)/(R*T) + math.log(1e3/P_REF) + J/(2*R*T), 280, 600)
    th_hi = theta_frumkin(P_CO2_AIR, T0, dH, dS, J); th_lo = theta_frumkin(1e3, Td+3, dH, dS, J)
    wc = 2*(th_hi - th_lo); sens = 1500*(Td+3-T0)/wc; heat = -dH + sens + 2*44e3
    weq = GJ(heat*(1-T0/(Td+3)) + R*T0*math.log(P0/1e3)/0.7) + fan_work_gj_per_tonne(X_AIR,0.75,100.0)
    print(f"  J {J/1e3:.0f} kJ (first-order step at 10 Pa, 25 C): dH {dH/1e3:.1f}, step reaches 1 kPa at {Td-273.15:.1f} C; fill {th_hi:.2f}->{th_lo:.2f}; heat {GJ(heat):.2f} GJ/t, work-eq {weq:.2f}")

print("\n=== 2. LCST / volume-phase-transition pKa switch for bicarbonate capture in a hydrated amine gel ===")
def KH(T): return 0.034*math.exp(2400*(1/T - 1/298.15))       # M/atm
def pKa1(T): return 6.35 + (-9.2e3/(2.303*R))*(1/T - 1/298.15)*(-1)  # small T-dependence (dH_ion ~ +9 kJ)
def loading(pKa_am, T, p_pa, C=3.0):
    co2aq = KH(T)*p_pa/101325
    K = 10**(pKa_am - pKa1(T))
    # alpha^2 C /(1-alpha) = K co2aq
    a = C; b = K*co2aq; c = -K*co2aq
    return (-b + math.sqrt(b*b - 4*a*c))/(2*a)
for C in (1.0, 3.0):
    pk_need = brentq(lambda pk: loading(pk, 298.15, 42.5, C) - 0.5, 5, 16)
    print(f"  local amine {C} M: swollen-state pKa for 50% loading at 420 ppm, 25 C: {pk_need:.2f}")
dHion = 55e3
for pk25 in (11.0, 11.5):
    for Tdes in (333.15, 348.15):
        pk_T = pk25 - dHion/(2.303*R)*(1/298.15 - 1/Tdes)
        a_ads = loading(pk25, 298.15, 42.5)
        for dpk in (0.0, 1.0, 1.8, 2.5):
            a_des = loading(pk_T - dpk, Tdes, 5e3)
            print(f"  pKa25 {pk25}, release {Tdes-273.15:.0f} C into 5 kPa CO2, VPT shift {dpk}: loading {a_ads:.2f} -> {a_des:.2f}  (working {max(0,a_ads-a_des):.2f} CO2/N)")
for dpk in (1.0, 1.8, 2.5):
    shift = 2.303*R*333.15*dpk
    print(f"  dpKa {dpk} at 60 C = {shift/1e3:.1f} kJ/mol = equivalent to {shift/(165+R*math.log(0.25*P_REF/1e3)):.0f} K of Langmuir swing (dS -165, 1 kPa)")
# energy for LCST film: bicarb formation ~ -66 kJ/mol (incl. CO2 dissolution -20, ionisation), transition enthalpy, sensible, water
for nNIPAm_per_N, dHtr in ((2, 5.5e3), (4, 5.5e3)):
    for wcN in (0.4, 0.6):
        Ntot = 1/(0.071*1 + nNIPAm_per_N*0.113)  # mol amine per kg dry polymer (DMAPM-like 0.071? use 71 g/mol amine monomer est.)
        wc = wcN*Ntot  # mol CO2/kg
        tr = nNIPAm_per_N*dHtr/wcN
        sens = 1800*(40)/wc
        for wat in (1.0, 3.0):
            heat = 66e3 + tr + sens + wat*44e3
            print(f"  NIPAm:N {nNIPAm_per_N}, wc {wcN} CO2/N -> {wc:.2f} mol/kg dry: rxn 1.50 + transition {GJ(tr):.2f} + sensible(40 K) {GJ(sens):.2f} + water({wat}) {GJ(wat*44e3):.2f} = {GJ(heat):.2f} GJ/t")

print("\n=== 3. Gibbs-Thomson confinement of the TriH carbamate network (TriH(CO2)1.5.xH2O) ===")
Vm = 258e-3/1300.0   # m3/mol, ~258 g/mol, 1.3 g/cm3 (estimate)
print(f"  Vm {Vm*1e6:.0f} cm3/mol; destabilisation of confined product per mol CO2 = 2 gamma Vm/(r*1.5)")
for gamma in (0.05, 0.1, 0.15):
    s = f"  gamma {gamma} J/m2:"
    for d_nm in (3, 6, 9, 15):
        r = d_nm/2*1e-9
        dmu = 2*gamma*Vm/r/1.5
        s += f" d={d_nm} nm {dmu/1e3:.1f} kJ/mol (p* x{math.exp(dmu/(R*363.15)):.0f});"
    print(s)
# over-binding inference: TriH dry 400 ppm isobar keeps CO2 up to ~87-95 C -> p*(~365 K) <= ~40 Pa
for dH in (-75e3, -100e3):
    T1 = 1/(1/365.0 - R*math.log(1e3/40)/(-dH))
    T25 = 40*math.exp(-(-dH)/R*(1/298.15 - 1/365.0))
    need = R*363.15*math.log(1e3/40)
    print(f"  dH {dH/1e3:.0f}: if p*(365 K) = 40 Pa, purge-free 1 kPa release needs {T1-273.15:.0f} C (TriH volatilises fast at 120 C); p*(25 C) = {T25:.3f} Pa; destabilisation to bring 1 kPa release to 90 C: {need/1e3:.1f} kJ/mol CO2")

print("\n=== 4. Seed retention: cost of leaving fraction f of the loaded phase unregenerated ===")
for f in (0.0, 0.05, 0.1, 0.2):
    # Na nahcolite cycle 40 wt%, x=0.8 -> wc 3.02*(1-f); heat per t: rxn fixed + residual-hydrate term unchanged per CO2 + sensible / (1-f)
    sens = 0.48/(1-f)
    print(f"  f {f:.2f}: working capacity x{1-f:.2f}; Na cycle heat {3.08+0.33+sens:.2f} GJ/t (sensible {sens:.2f}); break-even if cycles/day rise by > {1/(1-f):.2f}x")
