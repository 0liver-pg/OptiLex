import sys; sys.path.insert(0,'climate')
from physics import *
# per-plant local flows for a 1 Mt/yr solid-sorbent DAC plant (S11 view), using the idea's ranges
for kg_co2_per_kg_sorb in (48, 289):
    sorb = 1e9/kg_co2_per_kg_sorb  # kg sorbent replaced per yr per Mt CO2
    amine = 0.4*sorb
    meoh_evap = 2*sorb  # kg methanol evaporated per kg sorbent per reload (idea's assumption)
    print(f"{kg_co2_per_kg_sorb} kgCO2/kg: sorbent {sorb/1e6:.1f} kt/yr, spent amine ~{amine/1e6:.1f} kt/yr, methanol cycled {meoh_evap/1e6:.1f} kt/yr ({meoh_evap/1e6/365:.0f} t/day)")
# Gt-scale amine demand vs approx global ethyleneamines market (~0.6-0.7 Mt/yr, my recollection, unverified)
for mt in (1.4, 8.3):
    print(f"amine {mt} Mt/yr per Gt = {mt/0.65:.0f}x approx global ethyleneamines output")
# DAC removal value at 45Q $180/t vs reload saving
