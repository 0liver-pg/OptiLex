# Patch check for non_co2_6: input-side HCFC-22 balance, penalty sizing, gap-based scale
M={'CHCl3':119.377,'HF':20.006,'CHClF2':86.468,'HCl':36.461,'CHF3':70.014}
GWP=14600  # AR6 GWP100 HFC-23
print("Per t HCFC-22: CHCl3 %.3f t, HF %.3f t, HCl %.3f t" % (M['CHCl3']/M['CHClF2'],2*M['HF']/M['CHClF2'],2*M['HCl']/M['CHClF2']))
# by-product ratio sensitivity: inferred HCFC-22 from HF purchases (HF also consumed to make HFC-23: CHCl3+3HF->CHF3+3HCl)
for r in (0.015,0.02,0.03,0.04):
    hf_per_t22 = 2*M['HF']/M['CHClF2'] + r*3*M['HF']/M['CHF3']
    print(f" by-product {r:.3f}: HF per t HCFC-22 incl. HFC-23 route = {hf_per_t22:.4f} t; expected HFC-23 per t HF = {r/hf_per_t22*1000:.1f} kg")
# penalty sizing ($/kg HFC-23) vs $/t CO2e
for p in (1,2,5,10):
    print(f" penalty ${p}/kg HFC-23 = ${p*1000/GWP:.3f}/t CO2e")
# CDM comparison: CER ~$10-20/t CO2e (2005-08) -> $/kg HFC-23
for c in (10,20): print(f" CDM CER ${c}/t CO2e = ${c*GWP/1000:.0f}/kg HFC-23")
# gap-based scale: measured 14.0 kt (Adam 2024, 2023 global), reported ~1/5
meas=14.0; rep=meas/5; gap=meas-rep
print(f"gap = {gap:.1f} kt = {gap*GWP/1000:.0f} Mt CO2e")
for f in (0.25,0.5,0.75):
    print(f" recover {f:.0%} of gap: {gap*f:.1f} kt = {gap*f*GWP/1000:.0f} Mt CO2e/yr")
# VDF from what is recovered, if converted (60% selectivity, 0.914 t/t stoich)
print("VDF stoich t/t HFC-23 =", round(64.035/M['CHF3'],3))
