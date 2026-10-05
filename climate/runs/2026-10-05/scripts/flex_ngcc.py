"""Idea 5: NGCC amine capture + CSP-style two-tank rich/lean solvent storage + off-peak electric regeneration.
Cost model anchored to NETL Rev 4A F-class 90% ($60.7/t at 85% CF, 2018$) as summarised in the OptiLex map.
Run: cd . && .venv/bin/python <this file>
"""
import math, sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

# Decompose NETL cost into variable + fixed (fixed scales with 85/CF). Map: ~$61 at 85%, ~$99-110 at 40%.
c85, c40 = 60.7, 105.0
fixed85 = (c40 - c85) / (85 / 40 - 1)
var = c85 - fixed85
print(f"NETL-anchored split: variable ${var:.1f}/t, fixed ${fixed85:.1f}/t at 85% CF")
cost = lambda cf: var + fixed85 * 85 / cf
for cf in (85, 60, 40, 25):
    print(f"  baseline capture cost at {cf}% CF: ${cost(cf):.0f}/t")

# Storage design for a 2 Mt/yr-design plant (NZT-like): peak 2e6/(0.9*8760) t/h
peak = 2e6 / (0.9 * 8760)
for hours_on, regen_frac in ((10, 0.45), (14, 0.60)):
    stored = hours_on * peak * (1 - regen_frac)   # t CO2 accumulated while GT runs
    for m3_per_t in (15, 20):                      # rich solvent volume per t CO2 cycled (ASSUMPTION; 30wt% MEA, d-alpha 0.25 ~18.5)
        vol = stored * m3_per_t
        tank = vol * 2 * (300, 500)[0], vol * 2 * 500   # two tanks $300-500/m3 installed (ASSUMPTION)
        solvent = vol * 700, vol * 1600                # extra inventory $700-1600/m3 (ASSUMPTION)
        capex = (tank[0] + solvent[0], tank[1] + solvent[1])
        co2_yr = peak * hours_on * 365
        ann = [c * 0.10 / co2_yr for c in capex]
        print(f"GT {hours_on} h/d (CF {hours_on/24:.0%}), regen train {regen_frac:.0%} of peak: store {stored:.0f} t CO2 "
              f"= {vol/1e3:.0f}k m3 per tank; storage capex ${capex[0]/1e6:.0f}-{capex[1]/1e6:.0f}M -> "
              f"${ann[0]:.1f}-{ann[1]:.1f}/t at 10% CRF ({co2_yr/1e6:.2f} Mt/yr)")

# Capex saving from smaller regeneration train (stripper, reboiler, X-HX, compressor, dehydration)
for share in (0.35, 0.45):
    for regen_frac in (0.45, 0.60):
        cf = 40
        save = fixed85 * 85 / cf * share * (1 - regen_frac) * 0.8   # 0.8: scale exponent ~0.6-0.7 erodes saving (ASSUMPTION)
        print(f"  regen-train share {share:.0%}, sized {regen_frac:.0%}: fixed-cost saving ~${save:.0f}/t at 40% CF")

# Energy arbitrage
for cop in (2.0, 3.0, 4.0):
    q = 2.6   # GJ_th/t reboiler (ASSUMPTION, Cansolv-class 2.4-3.2 per map)
    e = q / cop / 3.6   # MWh_e/t
    print(f"  heat-pump regen COP {cop}: {e:.2f} MWh_e/t; at $10-30/MWh = ${e*10:.0f}-{e*30:.0f}/t "
          f"vs peak steam-extraction penalty 0.25-0.30 MWh/t at $80-150 = $20-45/t")
T_h, T_c = 125 + 273.15, 25 + 273.15
print(f"  Carnot COP 25->125C {T_h/(T_h-T_c):.2f}; 95->125C (stripper overhead MVR) {T_h/30:.1f}")
# Second-law check
sep = gj_per_tonne(min_separation_work(0.04, 0.9))
comp = gj_per_tonne(R * T0 * math.log(150))
for cop in (2.0, 3.0):
    actual = 2.6 / cop + 0.35
    print(f"  floor sep {sep:.2f} + comp {comp:.2f} GJ/t; actual elec {actual:.2f} GJ_e/t (COP {cop}, +0.35 compression) "
          f"-> 2nd-law {(sep+comp)/actual:.0%}")
