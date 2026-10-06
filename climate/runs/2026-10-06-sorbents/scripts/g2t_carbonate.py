import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
# NBS (Wagman 1982) standard data: (dHf kJ/mol, S J/mol/K)
D = {
 'NaHCO3': (-950.81, 101.7), 'Na2CO3': (-1130.68, 134.98), 'Na2CO3.H2O': (-1431.26, 168.11),
 'KHCO3': (-963.2, 115.5), 'K2CO3': (-1151.02, 155.52),
 'CO2': (-393.51, 213.74), 'H2O_g': (-241.82, 188.83),
}
# K2CO3.1.5H2O from heat-storage data: dehydration 65.8 kJ/mol H2O (Mazur 2022 ref [6]);
# entropy set so p_eq = 12 mbar at 62 C (Mazur/Sogutoglu: dehydration at 12 mbar begins near 60-65 C)
dHw, Tq, pq = 65.8, 335.15, 1200.0
dSw = (dHw*1e3 + R*Tq*math.log(pq/1.013e5))/Tq
D['K2CO3.1.5H2O'] = (D['K2CO3'][0] + 1.5*D['H2O_g'][0] - 1.5*dHw, D['K2CO3'][1] + 1.5*D['H2O_g'][1] - 1.5*dSw)
print(f"K2CO3.1.5H2O dehydration: dH {dHw} kJ/mol H2O, dS {dSw:.1f} J/mol/K; p_eq(25C) = {1013*math.exp(-(dHw*1e3-298.15*dSw)/(R*298.15)):.2f} mbar")

def rxn(reac, prod):
    dH = sum(n*D[s][0] for s, n in prod.items()) - sum(n*D[s][0] for s, n in reac.items())
    dS = sum(n*D[s][1] for s, n in prod.items()) - sum(n*D[s][1] for s, n in reac.items())
    return dH*1e3, dS
def K(dH, dS, T): return math.exp(-(dH - T*dS)/(R*T))  # bar-based
PSAT = lambda T: 610.94*math.exp(17.625*(T-273.15)/(T-273.15+243.04))  # Pa (Magnus)
P0b = 1.0e5

# Capture reactions written as forward capture
cap_Na_mono = rxn({'Na2CO3.H2O':1,'CO2':1}, {'NaHCO3':2})             # p_CO2* = 1/K  (no water)
cap_Na_anh  = rxn({'Na2CO3':1,'CO2':1,'H2O_g':1}, {'NaHCO3':2})       # p_CO2* p_w = 1/K
hyd_Na      = rxn({'Na2CO3':1,'H2O_g':1}, {'Na2CO3.H2O':1})
cap_K_sesq  = rxn({'K2CO3.1.5H2O':1,'CO2':1}, {'KHCO3':2,'H2O_g':0.5}) # p_CO2* = p_w^0.5 / K
cap_K_anh   = rxn({'K2CO3':1,'CO2':1,'H2O_g':1}, {'KHCO3':2})
for name, (dH, dS) in [('Na2CO3.H2O + CO2 -> 2NaHCO3', cap_Na_mono), ('Na2CO3 + CO2 + H2O -> 2NaHCO3', cap_Na_anh),
                       ('Na2CO3 + H2O -> Na2CO3.H2O', hyd_Na), ('K2CO3.1.5H2O + CO2 -> 2KHCO3 + 0.5H2O', cap_K_sesq),
                       ('K2CO3 + CO2 + H2O -> 2KHCO3', cap_K_anh)]:
    print(f"{name:42s} dH {dH/1e3:8.1f} kJ  dS {dS:7.1f} J/K")

print("\nEquilibrium CO2 over the capture product (ppm) vs T and RH:")
print(" T C  RH%   Na(mono-field) p*ppm  Na mono stable?  K(sesqui) p*ppm  K sesqui stable?  capture ceiling Na / K at 420 ppm")
for Tc in (5, 15, 25, 35):
    T = Tc + 273.15
    for rh in (0.2, 0.5, 0.8):
        pw = rh*PSAT(T)
        pNa = P0b/K(*cap_Na_mono, T)                      # Pa
        mono_stable = pw > P0b/K(*hyd_Na, T)
        pK = P0b*math.sqrt(pw/P0b)/K(*cap_K_sesq, T)
        pKeq = 1.013e5*math.exp(-(dHw*1e3 - T*dSw)/(R*T))
        print(f"{Tc:4d} {rh*100:4.0f}   {pNa/1e5*1e6:10.0f}           {str(mono_stable):5s}            {pK/1e5*1e6:8.0f}        {str(pw>pKeq):5s}            {max(0,1-pNa/42.5):.0%} / {max(0,1-pK/42.5):.0%}")

print("\nRelease of NaHCO3 under vacuum to anhydrous Na2CO3 (p_CO2 = p_H2O, 1:1), and to monohydrate:")
dHr, dSr = -cap_Na_anh[0], -cap_Na_anh[1]
for Tc in (50, 60, 70, 80, 90, 100, 120):
    T = Tc+273.15
    p_each = math.sqrt(K(dHr, dSr, T))*P0b
    pmono_eq = P0b/K(*hyd_Na, T)
    print(f"  {Tc:4d} C: p_CO2 = p_H2O = {p_each/1e3:6.2f} kPa ; monohydrate dehydration p_eq {pmono_eq/1e3:6.1f} kPa")
print(f"  release reaction heat (to anhydrous + H2O(g)): {dHr/1e3:.1f} kJ/mol = {gj_per_tonne(dHr):.2f} GJ/t")
print(f"  release to monohydrate only: {-cap_Na_mono[0]/1e3:.1f} kJ/mol = {gj_per_tonne(-cap_Na_mono[0]):.2f} GJ/t")
dHk, dSk = -cap_K_anh[0], -cap_K_anh[1]
for Tc in (70, 80, 90, 100):
    T=Tc+273.15; print(f"  KHCO3 -> K2CO3 vacuum {Tc} C: p_each {math.sqrt(K(dHk,dSk,T))*100:.2f} kPa")

print("\nSupported Na2CO3 cycle: heat per tonne vs loading and conversion (release 70 C under vacuum, adsorb 25 C)")
M_Na2CO3 = 0.10599
cp_support, cp_salt = 800.0, 1100.0  # J/kg/K activated carbon, Na2CO3/NaHCO3
dHmono = -hyd_Na[0]
for wt in (0.2, 0.4, 0.6):
    for x in (0.3, 0.5, 0.8):
        nNa = wt/M_Na2CO3            # mol Na2CO3 per kg composite
        wc = x*nNa                    # mol CO2 per kg per cycle
        cp = (1-wt)*cp_support + wt*cp_salt
        sens = cp*45.0/wc             # J/mol, 25->70 C, no recovery
        resid_water = (1-x)/x*dHmono  # dehydrating unreacted monohydrate
        Q = dHr + resid_water + sens
        print(f"  {wt:.0%} Na2CO3, conversion {x:.0%}: wc {wc:.2f} mol/kg  heat {gj_per_tonne(Q):.2f} GJ/t "
              f"(rxn {gj_per_tonne(dHr):.2f} + residual hydrate {gj_per_tonne(resid_water):.2f} + sensible {gj_per_tonne(sens):.2f})  "
              f"water released {1+(1-x)/x:.2f} mol/mol")
# work-equivalent and second law at 70C
T_des = 343.15
for wt,x in ((0.4,0.5),(0.4,0.8)):
    nNa=wt/M_Na2CO3; wc=x*nNa; cp=(1-wt)*cp_support+wt*cp_salt
    Q = dHr + (1-x)/x*dHmono + cp*45/wc
    pdes = math.sqrt(K(dHr,dSr,T_des))*P0b
    vac = R*T0*math.log(P0/pdes)/0.7          # CO2 only (water condensed)
    weq = gj_per_tonne(Q*(1-T0/T_des) + vac) + fan_work_gj_per_tonne(X_AIR, 0.6, 100.0)
    print(f"  work-eq ({wt:.0%},{x:.0%}): {weq:.2f} GJ/t ; second-law {floor_ if (floor_:=gj_per_tonne(min_separation_work(X_AIR,0.6,0.99,T0)))/weq else 0:.0%} ; heat-pump elec (COP 0.5 Carnot) {gj_per_tonne(Q)/(0.5*(T_des+5)/(T_des+5-293.15)):.2f} GJ/t")
print("\nSorbent cost: Na2CO3 $0.3/kg + carbon support $3/kg, 40 wt% salt -> $1.9/kg composite")
for cyc in (500, 2000, 10000):
    print(f"  wc 1.9 mol/kg, {cyc} cycles: ${sorbent_cost_per_tonne(1.92, 1.89, cyc):.1f}/t ; wc 0.5: ${sorbent_cost_per_tonne(1.92, 0.5, cyc):.1f}/t")
