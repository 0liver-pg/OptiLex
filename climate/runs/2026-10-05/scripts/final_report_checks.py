"""Final-report cross-checks: Pareto front from the scored table, overlap-aware scale, headline physics."""
import sys
sys.path.insert(0, 'climate')
from physics import *

# (short name, cost base $/t CO2e, scale Gt/yr, TRL, coalition /11, n_opposing, status)
ideas = [
 ("Li-unit storage sequencing", 38.1, 0.01, 7, 7.75, 0, "front"),
 ("Permian SWD dissolved CO2", 55, 0.016, 4, 6.5, 0, "front"),
 ("HCFC-22 fenceline audit", 0.444, 0.114, 6, 6.25, 0, "front"),
 ("Tailrace methane hood", 23.9, 0.0015, 4, 5.5, 0, "alive"),
 ("Sulfate-recharged AWD", 89, 0.0167, 4, 5.0, 0, "alive"),
 ("Store heat not sorbent", 673, 0.3, 5, 7.5, 0, "front"),
 ("Solar collector-adsorber", 584, 0.05, 3, 5.75, 0, "alive"),
 ("Repair-cycle sorbent", 474, 0.5, 3, 7.25, 0, "front"),
 ("AEC-Q100 sorbent qual", 663, 0.01, 4, 6.75, 0, "alive"),
 ("Tailings forced aeration", 543, 0.002, 3, 7.0, 0, "alive"),
 ("Fracture doublets", 86, 0.05, 3, 7.0, 0, "dropped"),
 ("Retire-and-store", 155, 0.02, 5, 5.25, 0, "alive"),
 ("SOFC capture-ready", 48.8, 0.03, 5, 6.0, 1, "alive"),
 ("HFC-23 to VDF + balance", 0.252, 0.069, 6, 5.75, 0, "front"),
 ("CH4-intensity differential", 6.8, 0.128, 6, 5.75, 0, "front"),
 ("Clinker phasedown", 235, 0.13, 8, 4.75, 0, "front"),
 ("Green-iron compact", 145, 0.031, 7, 5.5, 1, "alive"),
 ("CO2 cushion gas UGS", 129, 0.02, 4, 6.25, 1, "alive"),
 ("Dredged sediment LC3", 60.4, 0.009, 4, 7.25, 0, "alive"),
 ("NosZ slurry inoculum", 331, 0.007, 4, 6.5, 0, "alive"),
 ("Aglime->silicate swap", 234, 0.0011, 4, 5.25, 0, "dropped"),
 ("Dairy ration MIR", 43, 0.0037, 4, 7.75, 0, "alive"),
 ("Peat rewetting InSAR", 34.3, 0.032, 6, 4.75, 1, "alive"),
 ("Amine tankage cycling", 116, 0.1, 4, 5.75, 1, "alive"),
]

def dominates(a, b):
    ge = (a[1] <= b[1], a[2] >= b[2], a[3] >= b[3], a[4] >= b[4])
    gt = (a[1] < b[1], a[2] > b[2], a[3] > b[3], a[4] > b[4])
    return all(ge) and any(gt)

cand = [i for i in ideas if i[6] != "dropped"]
front = [i for i in cand if not any(dominates(j, i) for j in cand if j is not i)]
print("Pareto front on (min cost, max scale, max TRL, max coalition):")
for i in front: print("  ", i[0], "| table status:", i[6])
tagged = {i[0] for i in ideas if i[6] == "front"}
print("Mismatch vs table tags:", tagged.symmetric_difference({i[0] for i in front}))
for i in cand:
    if i[0] not in tagged:
        doms = [j[0] for j in cand if j is not i and dominates(j, i)]
        print(f"  {i[0]:<28} dominated by: {', '.join(doms[:3])}")

print("\nOverlap-aware scale of front (Gt CO2e/yr, GWP100):")
hfc = max(0.114, 0.069)        # fenceline and VDF/balance act on the same HFC-23 gap
dac = 0.5                      # heat buffer + repair-cycle are cost levers on the SAME DAC fleet, not extra tonnes
others = 0.01 + 0.016 + 0.128 + 0.13
print(f"  abatement ideas (HFC-23 pool counted once {hfc}, CH4 0.128, clinker 0.13, Li 0.01, SWD 0.016): {hfc+others:.3f}")
print(f"  share of 53 Gt total GHG: {(hfc+others)/TOTAL_GHG_GT_CO2E:.2%}; of 37.4 Gt fossil CO2: {(hfc+others)/FOSSIL_CO2_GT:.2%}")
print(f"  DAC levers apply to a hypothetical {dac} Gt/yr fleet; they lower cost, they add no tonnes themselves")

print("\nHeadline physics (verifier):")
for lab, x, f in [("air 420ppm 75%", 420e-6, .75), ("NGCC 4% 90%", .04, .9), ("coal 12% 90%", .12, .9),
                  ("cement 25% 90%", .25, .9), ("NGCC 4% 99%", .04, .99), ("coal 12% 99%", .12, .99)]:
    print(f"  floor {lab}: {gj_per_tonne(min_separation_work(x, f)):.3f} GJ/t")
for gj in (0.47, 2.36, 6, 10, 19.8):
    s = ScaleCheck(1.0, gj)
    print(f"  1 Gt/yr DAC at {gj} GJ/t: {s.ej_per_year:.2f} EJ = {s.share_of_world_primary_energy:.2%} of primary")
fan_ch4 = fan_work_gj_per_tonne(1.93e-6, 0.5, 100, molar_mass=M_CH4)
print(f"  ambient CH4 fan work: {fan_ch4:.0f} GJ/t CH4 = {fan_ch4/GWP100['CH4_fossil']:.1f} GJ/t CO2e GWP100")
print(f"  ambient CH4 separation floor: {gj_per_tonne(min_separation_work(1.93e-6,0.5),M_CH4)/GWP100['CH4_fossil']:.3f} GJ/t CO2e")
# methane abatement vs all CCS
ch4_free = 35e6 * GWP100['CH4_fossil'] / 1e9
print(f"  35 Mt CH4 no-net-cost = {ch4_free:.2f} Gt CO2e = {ch4_free/0.064:.0f}x 64 Mtpa CCS capacity")
# storage commons vs continued fossil use
print(f"  prudent storage 1460 Gt / 37.4 Gt/yr = {1460/37.4:.0f} yr; vs 1.5 Gt/yr cement process = {1460/1.5:.0f} yr")
# gas value
for p in (3.5, 11):
    print(f"  recovered CH4 at ${p}/MMBtu: ${p*1e3/(1.055056*1e3/55.5)/29.8:.1f}/t CO2e GWP100")
