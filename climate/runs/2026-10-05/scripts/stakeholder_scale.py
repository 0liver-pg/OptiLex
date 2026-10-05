# Scale comparisons for stakeholder analysis of the solar collector-adsorber DAC idea (modelled inputs from the idea card)
ivanpah_km2 = 14.2  # 3,500 acres, Wikipedia
for land_per_Mt in (11, 22):
    print(f"land {land_per_Mt} km2/Mt/yr = {land_per_Mt/ivanpah_km2:.1f} Ivanpah footprints per Mt/yr; 1 Gt/yr = {land_per_Mt*1000:,} km2")
# 45Q DAC credit vs modelled LCOR
for lcor in (150, 230, 290, 520):
    print(f"LCOR ${lcor}/t vs 45Q DAC $180/t -> margin {180-lcor:+} $/t")
# electricity: 129 kWh/t ; Climeworks stated 650 kWh/t electric
for Mt in (1, 100, 1000):
    print(f"{Mt} Mt/yr: solar-panel DAC {Mt*1e6*129/1e9:.2f} TWh vs grid-DAC at 650 kWh/t {Mt*1e6*650/1e9:.1f} TWh (+heat)")
