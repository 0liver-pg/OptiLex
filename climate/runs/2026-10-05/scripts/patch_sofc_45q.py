import sys
sys.path.insert(0,'climate')
from physics import *
def ann(n,r): return (1-(1+r)**-n)/r
r=0.08
lev=85*ann(12,r)/ann(20,r)
print(f"levelised 45Q (12y credit over 20y asset, 8%): ${lev:.1f}/t")
for eff in (0.55,0.60):
    tpm=0.0531*3.6/eff  # natural gas ~53.1 kg CO2/GJ LHV-ish (ASSUMED, CH4-rich)
    for mw in (10,50,200):
        mwh=mw*8760*0.9
        cap=mwh*tpm*0.95
        print(f"eff {eff:.2f} {mw:4d} MW: {tpm:.3f} tCO2/MWh, captured {cap/1e3:7.1f} kt/yr (95% capture), >=18,750 t? {cap>=18750}")
# 45Q value per MWh at 95% capture
for eff in (0.55,0.60):
    tpm=0.0531*3.6/eff
    print(f"eff {eff}: 45Q nominal $85/t -> ${85*tpm*0.95:.1f}/MWh; levelised ${lev*tpm*0.95:.1f}/MWh")
# gas cost per MWh at +1..+2.5 $/MMBtu
for p in (1.0,1.5,2.5):
    for eff in (0.55,0.60):
        print(f"gas ${p}/MMBtu eff {eff}: ${p*3.412/eff:.1f}/MWh")
