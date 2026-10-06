import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
GJ = gj_per_tonne; F = FARADAY
floor_j = min_separation_work(X_AIR, 0.75, 0.99, T0); floor = GJ(floor_j)
FAN100 = fan_work_gj_per_tonne(X_AIR, 0.75, 100.0)
def vac(p): return R*T0*math.log(P0/p)/0.7

print("=== 1b. Swing width when the step is placed at the hottest adsorption temperature (p_step = 10 Pa at T_max)")
print(f"{'dS':>6}{'Tmax C':>8}{'dH kJ':>8}{'T_des@1kPa':>12}{'dT swing':>10}{'p_step@15C Pa':>15}{'heat6 GJ/t':>12}{'weq6':>7}{'eta6':>6}{'T_des@10kPa':>13}")
for Tmax_c in (25, 35, 45):
    Tm = Tmax_c + 273.15
    for dS in (-165.0, -250.0, -300.0, -400.0):
        dH = Tm*dS - R*Tm*math.log(P_REF/10.0)
        Td = dH/(dS - R*math.log(P_REF/1e3)); Td10 = dH/(dS - R*math.log(P_REF/1e4))
        p15 = P_REF*math.exp((dH - 288.15*dS)/(R*288.15))
        heat = -dH + 1500.0*(Td - T0)/5.4
        we = GJ(heat*(1-T0/Td) + vac(1e3)) + FAN100
        print(f"{dS:>6.0f}{Tmax_c:>8}{dH/1e3:>8.1f}{Td-273.15:>12.0f}{Td-Tm:>10.0f}{p15:>15.3f}{GJ(heat):>12.2f}{we:>7.2f}{floor/we:>6.0%}{Td10-273.15:>13.0f}")
print("   approx: dT = T_max * R ln(p_des/p_step) / (|dS| + R ln(P_REF/p_des)); low-grade heat: 2.8 GJ/t at 60 C from a heat pump at COP 5 = "
      f"{2.8/3.6/5*1000:.0f} kWh/t; + vacuum {GJ(vac(1e3))/0.0036:.0f} kWh/t + fan {FAN100/0.0036:.0f} kWh/t")

print("\n=== 2b. Humidity trigger worth in kelvin: T for 1 kPa release at ambient p_H2O vs desiccant p_H2O (dS_tot -285 site, theta 0.75 at 42.5 Pa/50%RH/25C)")
pw_amb = 0.5*3169.0
dS_tot = -285.0; Kn = 3.0/(P_CO2_AIR*pw_amb); dG25 = -R*T0*math.log(Kn*P_REF**2); dH_tot = dG25 + T0*dS_tot
from scipy.optimize import brentq
def T_release(pw, pco2=1e3, theta=0.2):
    f = lambda T: math.exp(-(dH_tot - T*dS_tot)/(R*T))/P_REF**2 * pco2 * pw - theta/(1-theta)
    return brentq(f, 250, 500)
for name, pw in (("ambient 50%RH", pw_amb), ("arid 15%RH/30C", 0.15*4247.0), ("silica 5%RH", 0.05*3169.0), ("3A 13 Pa", 13.0)):
    print(f"   p_H2O {name:>16} ({pw:6.0f} Pa): 1 kPa release at {T_release(pw)-273.15:.0f} C; 10 kPa at {T_release(pw,1e4)-273.15:.0f} C")

print("\n=== 6. PROTON-PUMP (pH) SWING on a weak-base chemisorbent: Nernst floor = n_H+ x F x 59.2 mV x dpH")
for dpH, n, label in ((3.0, 1, "amine pKa~10 -> bicarbonate release, 1 H+/CO2"), (4.0, 1, "same, 4 pH units"), (7.0, 1, "hydroxide ionomer, bicarbonate, 1 H+"), (7.0, 2, "hydroxide, carbonate, 2 H+"), (14.0, 2, "full water-dissociation swing (BPMED floor)")):
    w = n*F*0.05916*dpH
    print(f"   dpH {dpH:>4.0f}, {n} H+: {w/1e3:5.1f} kJ/mol = {GJ(w):.2f} GJ/t  ({label})")
print("   same floor from the Langmuir side (shift needed at 25 C to go from 95% fill at 42.5 Pa to 20% fill at 1 kPa):", end=" ")
dG_cap = -R*T0*math.log(19.0*P_REF/P_CO2_AIR); dG_rel = -R*T0*math.log(0.25*P_REF/1e3)
print(f"{(dG_rel-dG_cap)/1e3:.1f} kJ/mol = {(dG_rel-dG_cap)/F*1e3:.0f} mV")
for shift_mV, eta_mV, FE in ((190, 200, 0.9), (190, 400, 0.7), (130, 200, 0.9)):
    w = F*(shift_mV+eta_mV)/1e3/FE
    print(f"   practical: shift {shift_mV} mV + {eta_mV} mV losses, FE {FE:.0%}: {w/1e3:.0f} kJ/mol = {GJ(w):.2f} GJ_e/t ({GJ(w)/0.0036:.0f} kWh/t); + vacuum from 1 kPa {GJ(vac(1e3)):.2f} + fan {FAN100:.2f} -> total {GJ(w+vac(1e3))+FAN100:.2f} GJ/t, eta {floor/(GJ(w+vac(1e3))+FAN100):.0%}")
# areal current for a laminate
wc, cycle_min, kg_per_m2 = 1.0, 30.0, 2.0
I = wc*F*kg_per_m2/(cycle_min*60)  # A per m2 face, 1 e-/CO2
print(f"   laminate face current for 1 e-/CO2 at {wc} mol/kg, {kg_per_m2} kg/m2 face, {cycle_min:.0f} min release: {I:.0f} A/m2 = {I/1e4*1e3:.1f} mA/cm2 (vs 1-2 mA/cm2 for MnO2 and Ni(OH)2 air cells)")
print("   measured comparators: Ni(OH)2 HEMCC 1.15 MWh/t avg = 4.1 GJ/t, 0.46 MWh/t end = 1.66 GJ/t (N2 sweep product); Seo/Hatton redox-active amine 101 kJ/mol = 2.3 GJ/t (aqueous, air feed, e-util 0.78)")

print("\n=== X. Other non-thermal triggers, order-of-magnitude floors")
h, c, NA = 6.62607e-34, 2.99792e8, 6.02214e23
dG_ratio = R*T0*math.log(1e3/P_CO2_AIR)
print(f"   free energy to lift CO2 from 42.5 Pa to 1 kPa at 25 C: {dG_ratio/1e3:.1f} kJ/mol; from 95% fill to 20% fill incl. isotherm width: {(dG_rel-dG_cap)/1e3:.1f} kJ/mol")
for name, stored in (("azobenzene trans->cis stored enthalpy ~49 kJ/mol", 49e3), ("norbornadiene->quadricyclane ~89-100 kJ/mol", 95e3)):
    print(f"   {name}: max CO2 per switching event = {stored/dG_ratio:.1f} (pressure-ratio only) or {stored/(dG_rel-dG_cap):.1f} (incl. isotherm width)")
for lam, label, frac in ((365, "UV", 0.05), (450, "blue", 0.25)):
    E = h*c/(lam*1e-9)*NA
    for n in (1.0, 3.0, 10.0):
        per_t = E/n/M_CO2*1000/3.6e6  # kWh light per tonne
        area = per_t/(2000.0*frac)
        print(f"   {lam} nm ({label}), {n:.0f} CO2 per absorbed photon: {GJ(E/n):.1f} GJ light/t; collector {area:.1f} m2-yr per t (usable band {frac:.0%} of 2,000 kWh/m2/yr)", end="; ")
    print()
print(f"   PV + heat pump reference: 2000 kWh/m2/yr x 22% = 440 kWh_e/m2/yr; entropy-steep cycle at ~340 kWh_e/t -> {340/440:.1f} m2-yr/t; reference amine via heat pump ~700 kWh_e/t -> {700/440:.1f} m2-yr/t")
mu = 3.0*3.336e-30; E_field = 1e8
print(f"   electric field: dipole 3 D in 1e8 V/m (near breakdown) = {mu*E_field*NA/1e3:.2f} kJ/mol; magnetic: 1 Bohr magneton in 10 T = {9.274e-24*10*NA/1e3:.2f} kJ/mol -> both << 8 kJ/mol needed")

print("\n=== 5b. Sodium carbonate monohydrate route (water stays in the solid): 2 NaHCO3 -> Na2CO3.H2O + CO2  [CRC values, verify]")
dHf = {"NaHCO3": -950.8, "Na2CO3.H2O": -1431.3, "CO2": -393.5}; S = {"NaHCO3": 101.7, "Na2CO3.H2O": 168.1, "CO2": 213.8}
dH = (dHf["Na2CO3.H2O"] + dHf["CO2"] - 2*dHf["NaHCO3"])*1e3; dS = S["Na2CO3.H2O"] + S["CO2"] - 2*S["NaHCO3"]
print(f"   dH {dH/1e3:.1f} kJ/mol, dS {dS:.0f} J/mol/K; p_CO2,eq at 25 C = {P_REF*math.exp(-(dH-T0*dS)/(R*T0)):.1f} Pa; 1 kPa release at {dH/(dS - R*math.log(P_REF/1e3))-273.15:.0f} C; 10 kPa at {dH/(dS - R*math.log(P_REF/1e4))-273.15:.0f} C")
print("   -> whichever carbonate phase (anhydrous vs monohydrate) is stable at the regeneration humidity sets the release temperature: 57 C (anhydrous, water leaves) vs this (hydrate keeps it). Both are below the amine reference's 92 C.")
