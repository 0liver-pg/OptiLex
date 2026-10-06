import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
# A. pH-swing Nernst work: 59.2 mV per pH unit at 298 K, n electrons(=protons) per CO2
for dpH in (14,10,7,5):
    for n in (1,2):
        w=electrochemical_work(n, R*T0*math.log(10)/FARADAY*dpH)
        print(f"pH swing dpH={dpH:2d}, {n} H+/CO2: {w/1000:6.1f} kJ/mol = {gj_per_tonne(w):.2f} GJ/t")
# B. O2 parasitic share for a redox sorbent: electrons to O2 / electrons to CO2 = (O2/CO2 ratio)/selectivity
ratio=0.2095/X_AIR
for S in (500,5000,50000):
    par=ratio/S
    print(f"selectivity CO2:O2 = {S}: parasitic e- per useful e- = {par:.3f} -> FE ceiling {1/(1+par)*100:.0f}%")
# C. Mission Zero 2022 pilot base case
tot=357.84; ech=229.95; mwh_t=2.18
t_yr=130.6/mwh_t
print(f"MZT pilot: {t_yr:.0f} t/yr; electrochem share {ech/tot*100:.0f}% = {ech/tot*mwh_t:.2f} MWh/t = {ech/tot*mwh_t*3.6*44.01:.0f} kJ/mol; + aux 0.47 -> {mwh_t+0.47:.2f} MWh/t = {(mwh_t+0.47)*3.6:.1f} GJ/t; vs claim 0.8 MWh/t ratio {mwh_t/0.8:.1f}x")
# D. convert kWh/t figures
for name,k in (("Vallejo Castano 2024 BPM-ED stack @50 mA/cm2",2444),("Eisaman 2011 low",630),("Eisaman 2011 high",1260),("Phlair claim <1.5 MWh/t",1500),("Shu 2020 H2-recycling 374 kJ/mol",374/44.01/3.6*1000),("Shu 2022 resin+EC 537 kJ/mol @20 mA/cm2",537/44.01/3.6*1000),("Rice PSE bicarbonate 118 kJ/mol @100 mA/cm2 (regen only)",118/44.01/3.6*1000),("Rice ORR/OER reactor ~150 kJ/mol",150/44.01/3.6*1000)):
    print(f"{name:58s} {k:6.0f} kWh/t = {k*3.6/1000:.2f} GJ/t = {k*3.6*44.01/1000:.0f} kJ/mol; 2nd-law {gj_per_tonne(min_separation_work(X_AIR,0.75,0.99))/(k*3.6/1000)*100:.0f}%")
# E. BPM-ED membrane cost: stack 500 EUR/m2, 2e-/CO2 (carbonate) or 1 (bicarbonate), FE 0.7-0.9, replacement every 1.25-2.5 y (70% of stack cost)
def areal(j_mA_cm2, e_eff, util=0.9): return j_mA_cm2*10/FARADAY/e_eff*M_CO2*3600*8760*util/1000
def crf(r,n): return r*(1+r)**n/((1+r)**n-1)
for j,life in ((20,2.5),(50,1.25)):
    for n,fe in ((1,0.7),(2,0.7),(1,0.9)):
        a=areal(j,n/fe)
        capex=500*crf(0.06,20)/a; repl=0.7*500/life/a
        print(f"BPM-ED j={j} mA/cm2, {n} e-/CO2, FE {fe}: {a:.2f} t/m2/yr; stack capex {capex:.0f} EUR/t + membrane replacement every {life} y {repl:.0f} EUR/t")
# F. Liu 2026 TEA sanity: $90/t capex incl contactor; MnO2 utilisation 4%
print("MnO2 theoretical 1 CO2 per Mn: %.1f mmol/g; measured 0.42 mmol/g -> %.1f%%"%(1000/86.94, 0.42/(1000/86.94)*100))
