"""Critic check for bottleneck_thermo_4: hybrid = 1x flat heat pump + cheap e-boiler + store charged only in
very-low-price hours (interruptible tariff). Per 100 kt/yr plant, CF 0.95, DE-LU 2025 SMARD prices.
Compares heat $/t and grid CO2 per t captured vs flat HP and vs the idea's 8h-charging e-boiler."""
import sys, os, json, glob, datetime as dt
from collections import defaultdict
sys.path.insert(0, 'climate')
from physics import *
SM = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'smard')
def load(prefix):
    s = {}
    for f in glob.glob(os.path.join(SM, f'{prefix}_*.json')):
        for t, v in json.load(open(f))['series']:
            if v is not None: s[t] = v
    return {t: v for t, v in s.items() if dt.datetime.fromtimestamp(t/1000, dt.timezone.utc).year == 2025}
EUR = 1.13
p = load('4169')
EF = {'1223': 1.10, '4069': 0.85, '4071': 0.40, '1227': 0.70}
zero = ['1225','1226','1228','4066','4067','4068','4070']
gen = {k: load('g'+k) for k in list(EF)+zero}
hrs = sorted(set.intersection(*[set(s) for s in gen.values()]) & set(p))
ci = {t: sum(gen[k][t]*EF[k] for k in EF)/max(1e-9, sum(gen[k][t] for k in gen)) for t in hrs}
N = len(hrs)
Q = 7.2  # GJth/t
plant = 100e3; CF = 0.95; t_yr = plant*CF
D = plant*Q*1e9/3.1536e7/1e6   # MW_th average demand (nameplate)
AUX = 0.65  # MWh_e/t continuous
COP = 1.8; HP_CAPEX = 900; CRF = 0.10; OM = 0.02
GRIDF = 15  # EUR/MWh network charge on firm HP
avg_ci = sum(ci.values())/N
# flat HP baseline
e_hp = D/COP  # MW_e
hp_energy = sum((p[t]+GRIDF)*e_hp for t in hrs)/N*8760*EUR/t_yr
hp_capex = D*1e3*HP_CAPEX*(CRF+OM)/t_yr
hp_cap_chg = e_hp*1e3*40*EUR/t_yr
hp_co2 = sum(ci[t]*e_hp for t in hrs)/N*8760/t_yr
print(f'Avg demand {D:.1f} MW_th; flat HP: energy {hp_energy:.0f} + capex {hp_capex:.0f} + capacity {hp_cap_chg:.0f} = {hp_energy+hp_capex+hp_cap_chg:.0f} $/t heat; heat CO2 {hp_co2:.3f} t/t; aux CO2 {AUX*avg_ci:.3f}')
# hybrid: in hours with price < thr, e-boiler (interruptible, no network charge, rated X*D MW_e) supplies demand + charges store
# (16 h store); HP throttles down and store discharges when HP is cheaper. Greedy hourly sim.
for thr in (-5, 0, 10, 20):
  for X in (1.0, 2.0):
    EB_CAPEX = 100; TANK = 400; store_h = 16
    cap = D*store_h  # MWh_th
    s = 0.0; cost = 0.0; co2 = 0.0; eb_mwh = 0.0
    for t in hrs:
        need = D
        if p[t] < thr:
            eb = min(X*D, need + (cap - s))
            take = min(eb, need); s += (eb - take)*0.99; need -= take
            cost += eb/0.99*p[t]; co2 += eb/0.99*ci[t]; eb_mwh += eb
        else:
            d = min(s, need); s -= d; need -= d
        s *= (1-0.01/24)
        if need > 0:
            cost += need/COP*(p[t]+GRIDF); co2 += need/COP*ci[t]
    scale = 8760/N/t_yr
    energy = cost*scale*EUR
    capex = (D*1e3*HP_CAPEX + X*D*1e3*EB_CAPEX + cap*3.6e3/(4.19*0.92*45)*TANK)*(CRF+OM)/t_yr
    tot = energy + capex + hp_cap_chg
    print(f'thr {thr:>3} EUR, EB {X:.0f}xD: EB share {eb_mwh/(D*N):.1%}; heat {tot:.0f} $/t (energy {energy:.0f}, capex {capex:.0f}); heat CO2 {co2*scale:.3f} t/t')
neg = [t for t in hrs if p[t] < 0]
print(f'Negative hours {len(neg)}; mean CI there {sum(ci[t] for t in neg)/len(neg):.3f} vs mean {avg_ci:.3f}')
