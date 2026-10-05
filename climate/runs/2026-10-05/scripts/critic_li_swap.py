# Critic check: does CO2 as voidage fluid help or hurt the lithium owner vs spent-brine reinjection?
import numpy as np
LCE_PER_LI = 5.323
vol_per_t = 1.72          # m3 CO2 per t (CoolProp, physics report)
rec = 0.80                # DLE recovery
price = 9000.0            # $/t LCE, USGS 2025 US average
for grade in (150, 300, 400):            # mg/L Li
    li_val = lambda m3: m3*grade*1e-6*rec*LCE_PER_LI*price  # $ (grade mg/L * m3 -> kg ->t... ) 
    # grade mg/L = g/m3 -> kg = m3*grade/1000 ; t = /1e6 -> m3*grade*1e-6 t Li
    for Swr in (0.25, 0.35, 0.45):
        # brine contacted by CO2 per tonne: CO2 occupies (1-Swr) of contacted pore space (ignoring dissolution)
        contacted = vol_per_t/(1-Swr)
        stranded = contacted - vol_per_t     # residual brine left at full grade, unrecoverable by later CO2 flood
        print(f"grade {grade} mg/L Swr {Swr}: stranded brine {stranded:.2f} m3/t CO2, "
              f"stranded Li value ${li_val(stranded):.1f}/t CO2 (undiscounted), produced-voidage Li ${li_val(vol_per_t):.1f}/t")
# Dilution avoided under spent-brine reinjection: spent brine carries (1-rec) of grade.
# If fraction f of produced brine over life is recycled spent brine, average grade = 1 - f*rec
for f in (0.1, 0.3, 0.5):
    print(f"recycled fraction {f}: brine-reinjection grade factor {1-f*rec:.2f} -> CO2 case avoids loss of {f*rec*100:.0f}% of Li per m3")
# Discount: stranded resource would otherwise be produced late in life (yr 15-30)
for yr in (15, 25, 30):
    print(f"PV factor 8% at yr {yr}: {1/1.08**yr:.3f}")
# Disposal-zone scale context: 25 Mt/yr -> spent brine bbl/d
bbl = 0.158987
print("spent brine at 25 Mt/yr:", 25e6*vol_per_t/bbl/365/1e6, "Mbbl/d")
print("spent brine at 8.4 Mt/yr:", 8.4e6*vol_per_t/bbl/365/1e3, "kbbl/d")
