import sys
sys.path.insert(0, 'climate')
from physics import *  # verifier available; this script is stakeholder arithmetic only
# Inputs (from idea coalition_6 + assumptions flagged)
cbam_total = 1.4e9/0.75          # EUR/yr, Commission own-resource page (75% share) -> total
ms_share   = 0.25*cbam_total
prem_steel = 150.0               # EUR/t steel green premium (idea assumption; Fastmarkets range 150-200)
tco2_per_t = 1.7                 # t CO2 avoided per t steel vs BF-BOF (idea assumption)
bf_hot_metal = 70e6              # t/yr EU blast-furnace hot metal (idea figure)
cars = 12e6                      # EU new cars/yr (assumption)
avg_car = 30000.0                # EUR average new-car price (assumption; range 28-45k)
for label, pool in [("member-state 25% only", ms_share), ("all CBAM", cbam_total),
                    ("all CBAM + club 150", cbam_total+cars*150), ("all CBAM + club 200", cbam_total+cars*200)]:
    t = pool/prem_steel
    print(f"{label:24s} pool EUR{pool/1e9:4.2f}bn -> {t/1e6:5.1f} Mt steel-eq "
          f"({t/bf_hot_metal:5.1%} of EU BF hot metal), {t*tco2_per_t/1e6:5.1f} MtCO2/yr")
for prem in (150,200):
    for price in (30000,45000):
        print(f"car premium EUR{prem} on EUR{price}: {prem/price:.2%}")
# Premium per car vs steel content: ~0.9 t steel per car (assumption)
steel_per_car=0.9
print(f"implied premium per t of car steel at EUR150-200/car: EUR{150/steel_per_car:.0f}-{200/steel_per_car:.0f}/t "
      f"-> club pays ~{150/steel_per_car/prem_steel:.1f}-{200/steel_per_car/prem_steel:.1f}x the green-steel premium on its own steel")
# Budget loss share for S7: CBAM own resource vs EU annual budget (~EUR190bn, 2025-ish, assumption)
print(f"CBAM own resource as share of ~EUR190bn EU budget: {1.4e9/190e9:.2%}")
# EU CO2 scale
print(f"42-48 Mt CO2 vs EU ETS steel ~ (assume ~120-130 Mt/yr iron&steel): {42/130:.0%}-{48/120:.0%}")
