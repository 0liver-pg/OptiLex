import sys
sys.path.insert(0, 'climate')
import physics
print([n for n in dir(physics) if not n.startswith('_')][:60])
# IPCC AR6 WGIII SPM (2022) figures
GHG_2019 = 59.0          # GtCO2e, AR6 WGIII B.1 (59 +/- 6.6)
fossil_ch4_share_ghg = 0.06   # C.4.5: 6% [4-8%] of global GHG
fossil_ch4_share_ch4 = 0.32   # C.4.5: 32% [22-42%] of global CH4
avoid_lo, avoid_hi = 0.5, 0.8 # C.4.5: 50-80% avoidable <USD50/tCO2e
fossil_ch4 = GHG_2019*fossil_ch4_share_ghg
print(f"Fossil CH4 (GWP100) ~{fossil_ch4:.2f} GtCO2e/yr (range {GHG_2019*0.04:.1f}-{GHG_2019*0.08:.1f})")
print(f"Avoidable <$50/t: {fossil_ch4*avoid_lo:.2f}-{fossil_ch4*avoid_hi:.2f} GtCO2e/yr")
print(f"As share of global CH4: {fossil_ch4_share_ch4*avoid_lo:.0%}-{fossil_ch4_share_ch4*avoid_hi:.0%} vs 1.5C pathway cut of 34% [21-57%] by 2030 (C.1.2)")
# compare to engineered removal/capture actually realized
cdr_delivered_cum = 1.7e-3  # Gt, cdr.fyi cumulative durable CDR delivered (all time, as of 2026)
cdr_contracted_cum = 50.5e-3
print(f"Fossil CH4 avoidable per yr / cumulative durable CDR delivered = {fossil_ch4*avoid_lo/cdr_delivered_cum:.0f}x - {fossil_ch4*avoid_hi/cdr_delivered_cum:.0f}x")
# value of recovered methane as gas
LHV = 50.0 # GJ/t CH4
GJ_per_MMBtu = 1.055
for price in (3, 6, 10):  # $/MMBtu (US Henry Hub ~3, EU/Asia LNG ~10)
    v = price*LHV/GJ_per_MMBtu
    print(f"gas ${price}/MMBtu -> ${v:.0f}/t CH4 -> ${v/29.8:.1f}/tCO2e (GWP100) / ${v/82.5:.1f}/tCO2e (GWP20)")
# CDR market spend implied
print(f"Contracted durable CDR value at $337/t avg: ${cdr_contracted_cum*1e9*337/1e9:.1f} bn")
# IPCC stranded asset value vs annual oil and gas revenue context
print("IPCC C.4.4 stranded value USD1-4 trn (2015-2050, discounted, ~2C)")
