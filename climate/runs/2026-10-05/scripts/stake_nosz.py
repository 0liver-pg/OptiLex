import sys; sys.path.insert(0,'climate')
from physics import *
gwp = 273  # N2O GWP100 (AR6), as used in idea
def per_ha(N=150, ef=0.01): return N*ef*44/28*gwp/1000  # t CO2e/ha/yr
print("emis t/ha:", {ef: round(per_ha(ef=ef),3) for ef in (0.005,0.01,0.016)})
# breakeven cost per ha at reference carbon prices (USD/t); DKK->USD ~6.9 (approx, 2025)
prices = {"DK livestock tax 2030 eff (DKK120)":120/6.9, "DK 2035 eff (DKK300)":300/6.9,
          "EU ETS ~EUR75":75*1.08, "45Q point-source":85}
for name,p in prices.items():
    for ef in (0.005,0.01,0.016):
        for cut in (0.3,0.6):
            pass
    print(name, round(p,1), "$/t -> max $/ha payable at EF1%, cut 30/60%:",
          round(p*per_ha()*0.3,1), round(p*per_ha()*0.6,1))
