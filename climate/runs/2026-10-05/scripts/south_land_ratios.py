import sys
sys.path.insert(0, 'climate')
from physics import *
C2 = 44.01/12.011
# biochar: foregone fuel energy per tonne CO2 stored (husk)
for y, c in [(0.35,0.40),(0.38,0.45),(0.42,0.50)]:
    e_char = y*c*32.8            # MJ/kg husk = GJ/t husk
    co2 = y*c*C2*0.8             # t CO2/t husk at permanence 0.8
    print(f"husk char y={y} C={c}: foregone fuel {e_char:.1f} GJ/t husk -> {e_char/co2:.1f} GJ per t CO2 stored "
          f"(DAC real 5-10, floor {gj_per_tonne(min_separation_work(420e-6,0.75)):.2f})")
# AWD: energy saved per t CO2e avoided
for gj_ha, t_ha in [(1.31,1.03),(2.62,1.24),(1.63,1.48),(3.27,1.78)]:
    print(f"AWD: {gj_ha} GJ/ha saved / {t_ha} t CO2e/ha = {-gj_ha/t_ha:.2f} GJ per t CO2e (negative = net saving)")
# charcoal: energy gain per t charcoal from yield 24->34/40% (wood LHV 15.5 GJ/t dry, ASSUME)
for y1 in (0.34,0.40):
    print(f"kiln yield 24%->{y1:.0%}: wood input per t charcoal falls {1/0.24-1/y1:.2f} t = {(1/0.24-1/y1)*15.5:.0f} GJ wood saved per t charcoal")
