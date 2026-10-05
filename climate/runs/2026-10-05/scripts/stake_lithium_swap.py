# Stakeholder-relevant revenue split for the Smackover lithium voidage swap
# Inputs from idea card (CoolProp results) + 45Q $85/t (dedicated storage, 2025 base) + 45X (10% of production cost, assumption)
for t_per_tLCE in (337, 900):           # t CO2 stored per t LCE (idea card)
    for lce_price in (8e3, 20e3):
        q45 = 85*t_per_tLCE
        print(f"{t_per_tLCE} tCO2/tLCE, LCE ${lce_price/1e3:.0f}k/t: 45Q ${q45/1e3:.1f}k per t LCE "
              f"= {q45/lce_price:.1f}x lithium value; Li value per tCO2 ${lce_price/t_per_tLCE:.0f}")
# Arkansas 2.5% gross royalty on lithium (AOGC May 2025) per t CO2
for li_val in (9, 59):
    print(f"royalty to brine owners per t CO2 at Li value ${li_val}/t: ${0.025*li_val:.2f}")
# Scale vs Arkansas 3 projects: 24 Mt/yr at $85 = 
print("45Q outlay for 24 Mt/yr: $%.1fbn/yr; for 8.4 Mt/yr: $%.2fbn/yr" % (24*85/1e3, 8.4*85/1e3))
