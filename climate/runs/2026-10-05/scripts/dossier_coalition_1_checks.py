"""Dossier extension checks for coalition_1 (methane-intensity differential in gas/LNG contracts).
Tags: [meas] measured/published, [assume] assumption, [MEM] from memory, unverified.
"""
import sys, math, random, statistics as st
sys.path.insert(0, 'climate')
from physics import *
G100 = GWP100["CH4_fossil"]
KG_PER_MMBTU = 1.055056e3 / 55.5          # kg CH4 per MMBtu (HHV), as coalition_1.py
SLOPE = 30.0                               # $/t CO2e
def usd_per_mmbtu(dpp): return SLOPE * G100 * KG_PER_MMBTU * dpp / 100 / 1000
KG_PER_SCF_CH4 = 0.0283168 * 0.678         # kg CH4 per scf at ~15 C, 1 atm

print("=== A. Decomposing the 7.3x Permian 'disagreement' (3.2% vs 0.44%) ===")
# [meas] S&P Global CI / Insight M 2025-07-24: 2024 intensity 0.44% per BOE (energy basis), 96.4 bcf CH4 (2024),
#        ~117.7 bcf (2023), 3.9 bn BOE produced 2024; >68% of emissions observed by aircraft, rest modelled (Rutherford).
# [meas] Varon et al. (IMI/TROPOMI): Permian O&G 4.0 +/- 1.1 Tg/yr avg 2019-2023; intensity per CH4 produced 5.2% -> 3.2% (2023).
sp24_mt = 96.4e9 * KG_PER_SCF_CH4 / 1e9
sp23_mt = 117.7e9 * KG_PER_SCF_CH4 / 1e9
print(f"S&P aircraft+model: 2024 {sp24_mt:.2f} Mt CH4, 2023 {sp23_mt:.2f} Mt CH4 [calc from meas]")
# Denominator: per-BOE (oil+gas energy) vs per-gas. Oil ~6.3 mb/d in 2024 [MEM]; BOE total 3.9 bn [meas]
oil_bbl = 6.3e6 * 366
gas_boe = 3.9e9 - oil_bbl
gas_share = gas_boe / 3.9e9
print(f"Gas share of Permian BOE 2024 ~{gas_share:.0%} (oil 6.3 mb/d [MEM]) -> per-gas intensity ~ 0.44%/{gas_share:.2f} = {0.44/gas_share:.2f}% [calc]")
year_factor = sp23_mt / sp24_mt
per_gas_2023 = 0.44 / gas_share * year_factor
print(f"Year factor 2023/2024 = {year_factor:.2f}; S&P-based per-gas intensity 2023 ~ {per_gas_2023:.2f}% vs IMI 3.2% [calc]")
resid = 3.2 / per_gas_2023
print(f"Decomposition of 7.27x: denominator {1/gas_share:.2f}x * year {year_factor:.2f}x * residual method gap {resid:.2f}x "
      f"= {1/gas_share*year_factor*resid:.2f}x")
# cross-check with absolute masses: IMI 2023 ~ 4.0 +/- 1.1 Mt (avg; 2023 value assumed ~ avg) [assume]
F = 4.0 / sp23_mt
for s_air in (0.15, 0.25):
    s_inv = 1.1 / 4.0
    sF = math.sqrt(s_inv**2 + s_air**2)
    print(f"Permian F_b (IMI 4.0 / S&P 2023 {sp23_mt:.2f}) = {F:.2f}; 1-sigma rel. uncertainty with aircraft sigma {s_air:.0%}: "
          f"{sF:.0%} -> {'PASSES' if sF <= 0.25 else 'FAILS'} the +/-25% test [calc on assumed aircraft sigma]")

print("\n=== B. Disciplinary dead zone of the significance gate (one-sided 95%) ===")
for s in (0.15, 0.25, 0.35):
    Fmin = 1 + 1.645 * s
    print(f"F_b rel. sigma {s:.0%}: gate triggers only if F_b > {Fmin:.2f} -> up to {1-1/Fmin:.0%} of true emissions can go unreported undetected")

print("\n=== C. Reward per TRUE tonne under asset settlement (I_i = L5_i x F_b), 50% clause coverage ===")
for Fb in (1.0, 1.8, 2.5):
    print(f"F_b {Fb}: fixing a source inside the L5 inventory earns ${SLOPE*Fb*0.5:.1f}/t; fixing a source L5 misses earns "
          f"~$0 privately (only a basin-shared F_b drop) [calc]")

print("\n=== D. Baseline gaming: reference = prior-year settled intensity ===")
for delay_pp in (0.2, 0.5):
    d = usd_per_mmbtu(delay_pp)
    yrs = 10; vol = 1e6 * 52  # 1 Mtpa contract ~ 52 million MMBtu/yr [calc: 1 t LNG ~ 52 MMBtu]
    print(f"Seller who postpones a {delay_pp} pp cut until after signing gains ${d:.3f}/MMBtu for the term "
          f"= ${d*vol*yrs/1e6:.0f} M over 10 yr per 1 Mtpa contract [calc]")

print("\n=== E. Scale made consistent with clause share, adoption and reshuffling (year 10, GWP100) ===")
# Upstream CH4 tied to LNG 1.8/3.7/7.2 Mt (coalition_1.py, [MEM] supplier table)
# EU pipeline imports 2024 [MEM]: Norway 87 bcm @0.02%, Algeria 30 @1/2/4%, Azerbaijan 12 @0.5/1/2% (Russia excluded: EU phase-out by 2027 [MEM])
MT_CH4_PER_BCM = 0.678 * 0.92
pipe = {"Norway": (87, (0.0002,)*3), "Algeria": (30, (0.01, 0.02, 0.04)), "Azerbaijan": (12, (0.005, 0.01, 0.02))}
for k, lab in enumerate(("low", "base", "high")):
    lng_ch4 = (1.8, 3.7, 7.2)[k]
    pipe_ch4 = sum(b * MT_CH4_PER_BCM * i[k] for b, i in pipe.values())
    clause = (0.35, 0.425, 0.50)[k]       # clause-buyer share of LNG [assume, MEM]
    adopt = (0.61, 0.69, 0.77)[k]          # coverage after 10 yr (coalition_1.py sec 8)
    low = (0.30, 0.25, 0.20)[k]            # share of LNG supply already <~0.2% [assume, MEM]
    abate = (0.40, 0.60, 0.75)[k]
    naive = lng_ch4 * clause * adopt
    resh = lng_ch4 * max(0, clause * adopt - low) / (1 - low)   # low-leak cargoes steered to clause buyers first
    tot_naive = (naive + pipe_ch4 * adopt) * abate
    tot_resh = (resh + pipe_ch4 * adopt) * abate
    print(f"{lab}: EU pipeline upstream CH4 {pipe_ch4:.2f} Mt; LNG CH4 under clause {naive:.2f} Mt (volume share) / {resh:.2f} Mt "
          f"(after reshuffling); abated {tot_naive:.2f} / {tot_resh:.2f} Mt CH4 = {tot_naive*G100/1e3:.3f} / {tot_resh*G100/1e3:.3f} Gt CO2e "
          f"(no spillover) vs TEA {(0.036,0.128,0.417)[k]} Gt")

print("\n=== F. Price effect at 2026 prices ===")
for p, lab in ((14.75, "JKM 2026 forecast [meas: EIA STEO via EIA TIE Apr 2026]"), (10.8, "JKM 2027 forecast")):
    for i in (0.2, 1.0, 2.0):
        d = usd_per_mmbtu(0.5 - i)
        print(f"  {lab}: settled {i}% vs 0.5% ref -> {d:+.3f} $/MMBtu = {d/p:+.2%} of price")
print(f"  0.1 pp = ${usd_per_mmbtu(0.1):.4f}/MMBtu; MiQ/RSG premia reported 0.01-0.05 $/MMBtu [meas, press] = {0.01/usd_per_mmbtu(0.1)*0.1:.2f}-{0.05/usd_per_mmbtu(0.1)*0.1:.2f} pp-equivalent")
