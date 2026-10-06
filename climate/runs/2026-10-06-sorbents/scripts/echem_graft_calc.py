"""Electrochemical-graft worker: electron budget (n e-/CO2), Nernst pH-swing floors and cell energies
for six 'conventional capture core + one battery/flow-cell/ED/CDI graft' ideas.
Run from repo root: .venv/bin/python <this file>
"""
import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
import numpy as np
from scipy.optimize import brentq

FLOOR_J = min_separation_work(X_AIR, 0.75, 0.99)
FLOOR = gj_per_tonne(FLOOR_J)
NERNST = R*T0*math.log(10)/FARADAY          # V per pH unit at 25 C (0.05916)
print(f"floor {FLOOR:.3f} GJ/t = {FLOOR_J/1e3:.1f} kJ/mol; Nernst slope {NERNST*1000:.2f} mV/pH")

# ---------------------------------------------------------------- aqueous speciation (ideal, 25 C)
K1, K2, KH, KW = 4.45e-7, 4.69e-11, 0.034, 1e-14      # carbonate pKa 6.35/10.33, Henry M/atm, water

def speciate(K, CT, CA=0.0, pKa=10.0, Kc=0.0):
    """Charge-balance pH for K+ (M), total inorganic C (M), amino-acid salt CA (M; carboxylate anion, K+ counted in K),
    amine pKa, carbamate stability Kc=[carb]/([amine][HCO3-]). Ideal activities. Returns dict."""
    Ka = 10**-pKa
    def state(pH):
        h = 10**-pH
        denom = (h/K1 + 1 + K2/h)
        if CA > 0 and Kc > 0:
            # CT = hco3*denom + Kc*hco3*CA/(1 + h/Ka + Kc*hco3)  -> solve for hco3 in [0, CT/denom]
            g = lambda x: x*denom + Kc*x*CA/(1 + h/Ka + Kc*x) - CT
            hco3 = brentq(g, 0.0, CT/denom + 1e-30) if CT > 0 else 0.0
            A = CA/(1 + h/Ka + Kc*hco3)
        else:
            hco3 = CT/denom
            A = CA/(1 + h/Ka) if CA > 0 else 0.0
        co2 = hco3*h/K1; co3 = hco3*K2/h; carb = Kc*A*hco3; AH = A*h/Ka
        pos = K + h
        neg = KW/h + hco3 + 2*co3 + A + 2*carb      # sar- (-1), zwitterion (0), carbamate dianion (-2)
        return pos - neg, dict(pH=pH, co2=co2, hco3=hco3, co3=co3, carb=carb, A=A, AH=AH, pco2=max(co2/KH, 1e-30))
    pH = brentq(lambda x: state(x)[0], 0.0, 15.0)
    return state(pH)[1]

def find_CT_for_pco2(K, pco2, CA=0.0, pKa=10.0, Kc=0.0, lo=1e-9, hi=None):
    hi = hi if hi else max(K, CA)*1.5 + 1.0
    g = lambda CT: math.log(speciate(K, CT, CA, pKa, Kc)['pco2']) - math.log(pco2)
    return brentq(g, lo, hi)

def ph_swing_cycle(name, K, CA=0.0, pKa=10.0, Kc=0.0, p_release=1.0, strip_fraction=1.0, nq=200):
    """Rich = equilibrium with 420 ppm. Release: remove K+ (1 e- each, H+ in) at constant product pressure
    p_release (atm) until carbon drops by strip_fraction of (CT_rich - CT_at_full_strip). Regenerate: add K+/OH-
    back. Returns n e-/CO2, average Nernst dpH, Nernst work kJ/mol."""
    CT_rich = find_CT_for_pco2(K, 420e-6, CA, pKa, Kc)
    st_rich = speciate(K, CT_rich, CA, pKa, Kc)
    # anode trajectory: remove charge q, solution at pco2 = p_release once reached; before that pco2 < p_release
    qs = np.linspace(0, K*0.999, nq)
    pH_an, CT_an = [], []
    for q in qs:
        Kq = K - q
        # carbon at this q: if the closed solution (CT_rich) has pco2 < p_release keep CT_rich, else drop CT to hit p_release
        s = speciate(Kq, CT_rich, CA, pKa, Kc)
        if s['pco2'] <= p_release:
            CT = CT_rich
        else:
            CT = find_CT_for_pco2(Kq, p_release, CA, pKa, Kc, hi=CT_rich)
            s = speciate(Kq, CT, CA, pKa, Kc)
        pH_an.append(s['pH']); CT_an.append(CT)
    pH_an, CT_an = np.array(pH_an), np.array(CT_an)
    CT_min = CT_an[-1]
    CT_lean_target = CT_rich - strip_fraction*(CT_rich - CT_min)
    # charge needed to reach lean target
    idx = np.where(CT_an <= CT_lean_target)[0]
    q_need = qs[idx[0]] if len(idx) else qs[-1]
    dCO2 = CT_rich - CT_an[idx[0]] if len(idx) else CT_rich - CT_min
    n = q_need/dCO2
    # cathode trajectory: the stripped solution (K-q_need, CT_lean) gets K+/OH- back from q_need to 0
    qc = np.linspace(q_need, 0, nq)
    pH_ca = np.array([speciate(K - q, CT_an[idx[0]] if len(idx) else CT_min, CA, pKa, Kc)['pH'] for q in qc])
    # pair them as a rocking chair: at charge step k the anode is at q_k and the cathode at q_need - q_k
    m = min(len(qs[qs<=q_need]), nq)
    qa = qs[:m]; pa = pH_an[:m]
    pc = np.interp(q_need - qa, qc[::-1], pH_ca[::-1])
    dpH = pc - pa
    w_nernst = FARADAY*NERNST*np.trapezoid(dpH, qa)/dCO2   # J per mol CO2
    print(f"\n[{name}] K+={K} M CA={CA} M pKa={pKa} Kc={Kc}: rich pH {st_rich['pH']:.2f}, CT_rich {CT_rich:.3f} M "
          f"(HCO3 {st_rich['hco3']:.3f}, CO3 {st_rich['co3']:.3f}, carb {st_rich['carb']:.3f}), fully stripped CT {CT_min:.3f}")
    print(f"   release at {p_release} atm: dCO2 {dCO2:.3f} mol/L, charge {q_need:.3f} mol e-/L -> n = {n:.2f} e-/CO2; "
          f"anode pH {pa[0]:.1f}->{pa[-1]:.1f}; cathode pH {pc[0]:.1f}->{pc[-1]:.1f}; mean dpH {dpH.mean():.2f}; "
          f"Nernst work {w_nernst/1e3:.1f} kJ/mol = {gj_per_tonne(w_nernst):.2f} GJ/t")
    return dict(n=n, dpH=dpH.mean(), w_nernst=w_nernst, dCO2=dCO2, CT_rich=CT_rich, pH_rich=st_rich['pH'])

print("\n=== A. ELECTRON BUDGET OF AQUEOUS CAPTURE LIQUORS (ideal activities; rich = equilibrium with 420 ppm) ===")
res = {}
res['KOH1']   = ph_swing_cycle("KOH/K2CO3 liquor, full strip to KOH", 1.0)
res['KOH1v']  = ph_swing_cycle("KOH/K2CO3 liquor, release at 0.1 atm", 1.0, p_release=0.1)
res['KOH2']   = ph_swing_cycle("KOH/K2CO3 liquor 2 M K+, full strip", 2.0)
res['KOH1h']  = ph_swing_cycle("KOH/K2CO3 liquor, half strip (carbonate-only cycle)", 1.0, strip_fraction=0.5)
for Kc in (5.0, 30.0):
    res[f'sar{Kc}'] = ph_swing_cycle(f"3 M K-sarcosinate, pKa 10.0, Kc {Kc}, release 1 atm", 3.0, CA=3.0, pKa=10.0, Kc=Kc)
    res[f'sar{Kc}v'] = ph_swing_cycle(f"3 M K-sarcosinate, pKa 10.0, Kc {Kc}, release 0.01 atm (vacuum)", 3.0, CA=3.0, pKa=10.0, Kc=Kc, p_release=0.01)
res['sar_part'] = ph_swing_cycle("3 M K-sarcosinate, Kc 30, release 1 atm, strip only 50%", 3.0, CA=3.0, pKa=10.0, Kc=30.0, strip_fraction=0.5)

print("\n=== B. SOLID SORBENT ELECTRON BUDGET: n = (basic groups protonated at release)/CO2 ===")
print("  carbamate pair: n = 2 + f ; bicarbonate (humid 1:1): n = 1 + f ; f = free N per CO2 = N/CO2 - (2 or 1)")
for name, N, q, mode in [("PEI/silica 45 wt%, dry carbamate", 10.5, 1.5, 2), ("PEI/silica humid (bicarbonate share)", 10.5, 2.0, 1),
                        ("Lewatit benzylamine resin dry (1.0 mmol/g, 3.6 N)", 3.6, 1.0, 2), ("Lewatit humid 55% RH 1.8 mmol/g carbamate", 3.6, 1.8, 2),
                        ("Lewatit humid, bicarbonate regime", 3.6, 1.8, 1), ("MOF-808-Lys bicarbonate 1 CO2/N (1.2 mmol/g)", 1.2, 1.2, 1),
                        ("N5-dGA proton-trap 1:1 (6.6 mmol/g)", 6.6, 6.6, 1), ("QA resin IRA-900 HCO3- form", 4.18, 1.9, 1)]:
    f = max(N/q - mode, 0.0); n = mode + f
    print(f"  {name:55s} N/CO2={N/q:4.1f}  n={n:4.1f} e-/CO2")

print("\n=== C. CELL ENERGY vs n, Nernst dpH, overpotential eta (V), faradaic eff ===")
def cell(name, n, dpH, eta, fe=0.9, j=10):
    V = NERNST*dpH + eta
    w = electrochemical_work(n, V, fe); g = gj_per_tonne(w)
    print(f"  {name:62s} n={n:4.2f} dpH={dpH:4.1f} V={V:5.2f} FE={fe:.2f}: {w/1e3:6.1f} kJ/mol = {g:5.2f} GJ/t = {g/3.6*1000:5.0f} kWh/t; "
          f"2nd-law {FLOOR/g*100:4.1f}%; ${energy_cost_floor(g,50):4.0f}/t @50$/MWh")
    return g
E = {}
print(" Idea 1 solid amine between Ni(OH)2 proton electrodes (release pH ~7.8 vs pKa 9.3-10: dpH ~2):")
E['i1_bic']  = cell("  1:1 bicarbonate sorbent, f=0 (n=1), eta 0.25 V", 1.0, 2.0, 0.25, 0.85)
E['i1_lew']  = cell("  Lewatit humid carbamate n=2, eta 0.25 V", 2.0, 2.0, 0.25, 0.85)
E['i1_lew2'] = cell("  Lewatit humid n=2, eta 0.40 V (higher j)", 2.0, 2.0, 0.40, 0.85)
E['i1_pei']  = cell("  PEI/silica carbamate n=7, eta 0.25 V  (KILL)", 7.0, 2.0, 0.25, 0.85)
print(" Idea 2 KOH liquor + NiMH metal-hydride rocking chair (n, dpH from section A):")
r = res['KOH1']
E['i2'] = cell("  1 M K+, full strip, MH eta 2x0.06 + ohmic 0.10", r['n'], r['dpH'], 0.22, 0.92)
E['i2b'] = cell("  same, eta 0.35 (50 mA/cm2 class)", r['n'], r['dpH'], 0.35, 0.90)
E['i2c'] = cell("  2 M K+, full strip, eta 0.22", res['KOH2']['n'], res['KOH2']['dpH'], 0.22, 0.92)
print(" Idea 3 QA resin wafer + EDI (n=1, OH- regeneration pH 14 vs release 7.8: dpH 6.2; junction+ohmic eta):")
E['i3'] = cell("  eta 0.5 V (BPM-junction class), FE 0.8", 1.0, 6.2, 0.50, 0.80)
E['i3b'] = cell("  eta 0.8 V incl. end-electrode share, FE 0.7", 1.0, 6.2, 0.80, 0.70)
print(" Idea 4 K-sarcosinate + isolated solid PCET electrode (n, dpH from A):")
r = res['sar30.0']; E['i4'] = cell("  Kc 30, release 1 atm, eta 0.25", r['n'], r['dpH'], 0.25, 0.9)
r = res['sar30.0v']; E['i4v'] = cell("  Kc 30, release 0.01 atm (+vacuum), eta 0.25", r['n'], r['dpH'], 0.25, 0.9)
r = res['sar5.0']; E['i4k5'] = cell("  Kc 5, release 1 atm, eta 0.25", r['n'], r['dpH'], 0.25, 0.9)
print(" Idea 5 MnO2 surface mineralisation (1 e-/CO2 nominal; measured CE 22-33% at ~1 V):")
E['i5_meas'] = cell("  measured-like: n=1, dpH 0, V 1.0, FE 0.25", 1.0, 0.0, 1.0, 0.25)
E['i5_tgt'] = cell("  target birnessite: n=1, V 0.8, FE 0.7", 1.0, 0.0, 0.8, 0.70)
print(" Idea 6 membrane-free NiHCF(K+)/MnO2(H+) desalination-battery on carbonate liquor:")
r = res['KOH1']; E['i6'] = cell("  1 M K+, full strip, eta 0.15 (no membrane, 2 insertion electrodes)", r['n'], r['dpH'], 0.15, 0.9)
E['i6b'] = cell("  same, eta 0.30", r['n'], r['dpH'], 0.30, 0.85)
print(f"\n reference thermal TVSA work-equivalent {reference_amine_cycle().work_equivalent_gj_per_t:.2f} GJ/t; heat {reference_amine_cycle().heat_gj_per_t:.2f} GJ/t")

print("\n=== D. AUXILIARIES (GJ/t) ===")
for dp in (100, 150, 400, 700): print(f"  fan at {dp} Pa, 75% capture, 60% fan: {fan_work_gj_per_tonne(X_AIR,0.75,dp):.2f} GJ/t")
for dp,cap in ((60,0.3),(60,0.42)): print(f"  liquid cross-flow contactor {dp} Pa at {cap:.0%} capture: {fan_work_gj_per_tonne(X_AIR,cap,dp):.2f} GJ/t")
w_comp = R*T0*math.log(150)/0.6; print(f"  compression 1 atm -> 150 bar (isothermal/0.6): {gj_per_tonne(w_comp):.2f} GJ/t; from 0.01 atm vacuum pump: {gj_per_tonne(R*T0*math.log(100)/0.6):.2f} GJ/t")
print(f"  liquid pumping (Keith 2018 contactor 21 kWh/t): {21*3.6/1000:.2f} GJ/t")

print("\n=== E. AREAL PRODUCTIVITY AND CELL CAPITAL ===")
def crf(r,n): return r*(1+r)**n/((1+r)**n-1)
def areal(j, n_eff, duty=1.0, util=0.9): return j*10/FARADAY/n_eff*M_CO2*3600*8760*duty*util/1000
for name,j,n,duty,cost in [("Idea1 sandwich 10 mA/cm2, n=2/0.85, duty 0.2 (release 8 of 38 min)",10,2/0.85,0.2,300),
                           ("Idea1 sandwich 10 mA/cm2, n=1/0.85, duty 0.2",10,1/0.85,0.2,300),
                           ("Idea2 MH flow cell 20 mA/cm2, n=2.2/0.92, continuous",20,res['KOH1']['n']/0.92,1.0,300),
                           ("Idea2 MH flow cell 50 mA/cm2",50,res['KOH1']['n']/0.9,1.0,300),
                           ("Idea3 EDI 10 mA/cm2, n=1/0.8, duty 0.5",10,1/0.8,0.5,500),
                           ("Idea4 PCET flow 20 mA/cm2, n from A /0.9",20,res['sar30.0']['n']/0.9,1.0,500),
                           ("Idea5 MnO2 measured 1 mA/cm2, 4 e-eff, duty 0.5",1,4,0.5,300),
                           ("Idea5 MnO2 target 10 mA/cm2, 1/0.7, duty 0.5",10,1/0.7,0.5,300),
                           ("Idea6 desal-battery 20 mA/cm2, n/0.9, continuous (2 cells alternate)",20,res['KOH1']['n']/0.9,1.0,200),
                           ("Yan HEMCC measured 2 mA/cm2 (78 kg/m2/yr reported)",2,2,1.0,300)]:
    a = areal(j,n,duty); print(f"  {name:70s} {a*1000:7.0f} kg/m2/yr -> cell charge ${cost}/m2: ${cost*crf(0.07,10)/a:6.0f}/t")
# Idea 1 storage check: laminate 0.5 kg/m2 at 1.8 mol/kg -> charge per cycle
q_m2 = 0.5*1.8*2/0.85; t_rel = q_m2*FARADAY/(100.0)  # at 100 A/m2
print(f"  Idea1: 0.5 kg laminate/m2 x 1.8 mol/kg, n=2/0.85 -> {q_m2:.2f} mol e-/m2 = {q_m2*FARADAY/3600:.1f} Ah/m2; release time at 10 mA/cm2 {t_rel/60:.0f} min; "
      f"Ni(OH)2 needed at 200 mAh/g: {q_m2*FARADAY/3600/0.2:.0f} g/m2 per electrode; CO2 {0.5*1.8*M_CO2*1000:.0f} g/m2/cycle; "
      f"at 38 cycles/day {0.5*1.8*M_CO2*38*365:.0f} kg/m2/yr")

print("\n=== F. SORBENT / ELECTRODE REPLACEMENT COST ($/t) ===")
for name,price,wc,cyc in [("Lewatit $20/kg, 1.8 mol/kg, 5,000 cyc",20,1.8,5000),("Lewatit $20/kg, 1.8 mol/kg, 20,000 cyc",20,1.8,20000),
                          ("Lewatit $20/kg, 1.0 mol/kg dry, 5,000 cyc",20,1.0,5000),
                          ("AB5 hydride $15/kg, 3.3 mol H/kg (300 mAh/g) /2.2 e- , 1,000 cyc",15,3.3/2.2,1000),
                          ("AB5 hydride $15/kg, 1,000 cyc at 60% utilisation",15,0.6*3.3/2.2,1000),
                          ("NiHCF $10/kg, 2.2 mol K/kg (60 mAh/g) / 1.9 e-, 5,000 cyc",10,2.2/1.9,5000),
                          ("MnO2 $5/kg, 0.42 mol/kg, 700 cyc (measured)",5,0.42,700),("MnO2 $5/kg, 2.0 mol/kg, 5,000 cyc (target)",5,2.0,5000),
                          ("Ni(OH)2 electrode $10/kg, 3.7 mol e-/kg (200 mAh/g)/2 e-, 2,000 cyc",10,3.7/2,2000),
                          ("Ni(OH)2 electrode, 10,000 cyc",10,3.7/2,10000),
                          ("IRA-900 resin $7/kg, 1.5 mol/kg, 1,000 cyc",7,1.5,1000),("IRA-900 resin $7/kg, 1.5 mol/kg, 10,000 cyc",7,1.5,10000)]:
    print(f"  {name:70s} ${sorbent_cost_per_tonne(price,wc,cyc):7.0f}/t")

print("\n=== G. OXYGEN ===")
o2_sat = 0.26e-3   # mol/L dissolved O2 in water at 25 C, air
for name, e_per_L in [("1 M KOH liquor, 2.2 e-/CO2 x 0.75 mol CO2/L", res['KOH1']['n']*res['KOH1']['dCO2']), ("3 M K-sar, Kc 30", res['sar30.0']['n']*res['sar30.0']['dCO2'])]:
    print(f"  {name:55s}: O2 electrons (4 per O2) / CO2 electrons per litre = {4*o2_sat/e_per_L*100:.2f}%")
print(f"  air-fed electrode: O2:CO2 = {0.2095/X_AIR:.0f}:1 -> any air-breathing redox electrode needs >5,000:1 selectivity for FE>90%")
print(f"  MH open-circuit self-discharge in air-saturated liquor: 0.26 mM O2 consumes {4*o2_sat*1000:.1f} mmol H per litre per refill")

print("\n=== H. IDEA-5 utilisation arithmetic ===")
theo = 1000/86.94
for u in (0.037, 0.10, 0.17, 0.25): print(f"  Mn utilisation {u:.0%}: {theo*u:.2f} mmol CO2/g MnO2")
print(f"  energy scaling at fixed 1.0 V: CE 25% -> {gj_per_tonne(electrochemical_work(1,1.0,0.25)):.2f} GJ/t; CE 70% -> {gj_per_tonne(electrochemical_work(1,1.0,0.70)):.2f}; CE 70% at 0.8 V -> {gj_per_tonne(electrochemical_work(1,0.8,0.70)):.2f}")

print("\n=== I. CORRECTIONS AND ADDITIONS (electrode capacities in mol e-/kg; cycle-consistent productivity) ===")
# capacities: 300 mAh/g = 1080 C/g = 11.2 mol e-/kg ; 200 mAh/g = 7.46 ; 60 mAh/g = 2.24 ; MnO2 proton sponge 120 mAh/g = 4.5
cap = {"AB5 hydride 300 mAh/g": 11.2, "AB5 hydride at 60% utilisation": 6.7, "Ni(OH)2 200 mAh/g": 7.46, "NiHCF 60 mAh/g": 2.24, "MnO2 proton sponge 120 mAh/g": 4.5}
n_koh = res['KOH1']['n']
for name, c in cap.items():
    price = 15 if 'hydride' in name else (10 if 'Ni' in name else 5)
    nn = 2.0 if 'Ni(OH)2' in name else n_koh
    for cyc in (1000, 3000, 10000):
        print(f"  {name:32s} ${price}/kg, {nn:.2f} e-/CO2, {cyc:6d} cycles: ${sorbent_cost_per_tonne(price, c/nn, cyc):6.0f}/t")
print("\n Idea 1 cycle-consistent productivity: laminate m kg/m2, 1.8 mol/kg, n=2, FE 0.85, adsorption 30 min, release at j")
for m_lam in (0.5, 1.0):
    for j in (10, 20):
        q = m_lam*1.8*2/0.85*FARADAY            # C/m2 per release
        t_rel = q/(j*10)/60                      # min
        cyc_day = 1440/(30 + t_rel)
        kg = m_lam*1.8*M_CO2*cyc_day*365
        for cost in (150, 300):
            print(f"  m={m_lam} kg/m2 j={j} mA/cm2: release {t_rel:.0f} min, {cyc_day:.0f} cycles/day, {kg:.0f} kg CO2/m2/yr, cell ${cost}/m2 -> ${cost*crf(0.07,10)/(kg/1000):.0f}/t; "
                  f"ohmic drop at 0.5 S/m over {m_lam*2:.0f} mm: {j*10*m_lam*2e-3/0.5:.2f} V")
print("\n Idea 4 sensitivity to overpotential (n=2.76, dpH 1.74 from Kc=30):")
for eta in (0.08, 0.12, 0.25):
    cell(f"  K-sar Kc30 1 atm, eta {eta} V", res['sar30.0']['n'], res['sar30.0']['dpH'], eta, 0.9)
print("\n Idea 6 with MnO2/NiHCF: if the MnO2 proton reservoir limits at 4.5 mol e-/kg and NiHCF at 2.24: electrode mass per m2 for 20 mA/cm2 x 1 h = 7.46 mol e-/m2 ->", f"{7.46/4.5:.1f} kg MnO2/m2 and {7.46/2.24:.1f} kg NiHCF/m2 per cell")
print("\n Real-plant comparison (Climeworks-derived LCA 11.9 GJ heat + 700 kWh/t):", f"{11.9/3.6*1000:.0f} kWh_th + 700 kWh_e per t; electrochemical sandwich ~{E['i1_lew']/3.6*1000:.0f} kWh_e + fans {fan_work_gj_per_tonne(X_AIR,0.75,400)/3.6*1000:.0f}-{fan_work_gj_per_tonne(X_AIR,0.75,700)/3.6*1000:.0f} kWh_e (400-700 Pa laminate)")
print(" Electricity-only comparison: reference TVSA 6.04 GJ heat via COP-3 heat pump =", f"{6.04/3/3.6*1000:.0f} kWh/t; 11.9 GJ/t via COP 3 = {11.9/3/3.6*1000:.0f} kWh/t")
