import sys; sys.path.insert(0,'climate')
from physics import *
# Electron budget per ha per season, plough layer 20 cm, bulk density 1.3 -> 2600 t soil/ha
soil_t=2600.0
# CH4 residual under AWD (base case of TEA): 82 kg -> electrons (8 e-/CH4)
for ch4_kg in (55,82,150):
    print(f"AWD residual {ch4_kg} kg CH4 = {ch4_kg/16.04*8:.1f} kmol e-")
# Gypsum doses (CaSO4.2H2O, 172.17 g/mol), 8 e-/SO4
for dose in (0.15,0.75,1.5):
    print(f"gypsum {dose} t/ha = {dose*1000/172.17*8:.1f} kmol e- per pass; S={dose*1000/172.17*32.06:.0f} kg")
# Native reducible Fe(III): 0.1-0.5% of soil mass, re-oxidised per drying event fraction f
for fe_pct in (0.1,0.5):
    fe_kmol=soil_t*1000*fe_pct/100/55.85
    for f in (0.02,0.1):
        print(f"Fe(III) {fe_pct}% of soil, {f*100:.0f}% re-oxidised per dry = {fe_kmol*f:.1f} kmol e- per cycle (pool {fe_kmol:.0f})")
# straw: 5 t/ha incorporated, 40% C, ~ half degraded anaerobically in season -> electrons (4 e- per C at CH2O)
for straw in (0,3,6):
    c_kmol=straw*1000*0.40/12*0.5
    print(f"straw {straw} t/ha -> ~{c_kmol*4:.0f} kmol e- donor")
