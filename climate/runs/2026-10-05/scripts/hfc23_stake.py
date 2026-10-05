# Stakeholder-relevant scale checks for HFC-23 -> VDF idea
M_CHF3=70.014; M_VDF=64.035; M_HF=20.006
GWP=14600  # AR6 GWP100
pool_t=14000  # measured t/yr HFC-23 (per brief)
print("Pool CO2e Mt/yr:", pool_t*GWP/1e6)
for sel in (0.4,0.6,0.8):
    vdf=pool_t*sel*M_VDF/M_CHF3
    hf=pool_t*sel*M_HF/M_CHF3
    print(f"sel {sel}: VDF {vdf/1e3:.1f} kt/yr, HF co-product {hf/1e3:.1f} kt/yr")
# Revenue per tCO2e vs carbon prices
for p in (3000,7000):
    for sel in (0.4,0.8):
        r=sel*M_VDF/M_CHF3*p
        print(f"VDF ${p}/t sel {sel}: ${r:.0f}/t HFC-23 = ${r/GWP:.3f}/tCO2e")
# CDM-era comparison: CERs at ~20 EUR/t vs destruction 0.2-0.5 EUR/t => ~40-100x margin; here revenue / CO2e
print("CDM-era credit per t HFC-23 at 20 EUR/tCO2e (GWP 11700 used then):", 20*11700, "EUR")
# Consumer price effect: PVDF binder ~1-2% of cathode mass; trivial
