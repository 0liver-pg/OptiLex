# Critic check: counterfactual passive uptake + binder, using PHYSICS/TEA case outputs
cases = {  # stored kt, $/t stored, binder kt, energy kt (from TEA)
 'low':  dict(stored=180.9, cost=53,  binder=0.0,  energy=180.9-176.8),
 'base': dict(stored=74.7,  cost=543, binder=44.0, energy=10.2),
}
for passive in (0, 20, 39.8):  # kt/yr of baseline atmospheric uptake displaced
  for k,c in cases.items():
    tot = c['stored']*c['cost']/1e3  # $M/yr
    net = c['stored']-c['binder']-c['energy']-passive
    print(f"passive_lost={passive:5.1f} {k:4s} cost=${tot:5.1f}M net_incr={net:6.1f} kt "
          f"$/t_incr={'n/a' if net<=0 else round(tot*1e3/net)}")
  # base, binder-free (carbonation-cured agglomerates), dry stack already justified ($248/t)
  net = 74.7-10.2-passive; tot=74.7*248/1e3
  print(f"passive_lost={passive:5.1f} base_binderfree_drystack cost=${tot:.1f}M net_incr={net:.1f} $/t={round(tot*1e3/net)}")
# water films vs forced gas drying: gas per mol CO2 stored at 5% CO2, 30% uptake
import math
def psat(T): return 0.61094*math.exp(17.625*T/(T+243.04))  # kPa
n_gas = 1/(0.05*0.3)
for Tin,Tout in ((30,35),(30,40),(25,45)):
  dw = (psat(Tout)-psat(Tin))/101.3*n_gas  # mol H2O per mol CO2
  print(f"saturated gas warming {Tin}->{Tout}C picks up {dw:.2f} mol H2O/mol CO2 = {dw*18/44:.2f} t/t")
