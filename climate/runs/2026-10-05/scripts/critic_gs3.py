import sys; sys.path.insert(0,'climate')
from physics import *
# 1) Detection: per-ha signals at swap rates vs Larkin background
lime_ha=[1.0,1.5,2.0]; swap=0.3
for L in lime_ha:
    for cce in (0.3,0.1):
        rock=L*swap/cce
        for r in (0.02,0.05):
            print(f"lime {L} t/ha, CCE {cce}: rock {rock:.1f} t/ha/yr, silicate CDR {rock*r:.3f} t/ha/yr")
# Larkin: carbonate-driven background 3.7 +/-0.6 ; with 30% less carbonate, assume uncertainty scales
bg=3.7*(1-swap); sd=0.6*(1-swap); print("bkg after 30% swap",round(bg,2),"+/-",round(sd,2),"; 2-sigma detect needs >",round(2*(sd**2*2)**0.5,2),"t/ha (treated vs control)")
# 2) Durable-basis avoided factor vs script's (2fs-1)
for fs in (0.5,0.6,0.75,0.9):
    print(f"fs {fs}: script EF*(2fs-1)={0.459*(2*fs-1):.3f}; ocean-precip durable basis EF*fs={0.459*fs:.3f}")
# 3) N2O penalty from pH lag vs avoided CO2 per ha
L=1.5; lime_rep=L*swap
for Nrate in (60,120):
    n2o=Nrate*0.01*44/28*273/1000  # t CO2e/ha, EF1 1%
    for incr in (0.1,0.2):
        av_lo=lime_rep*0.229; av_hi=lime_rep*0.459
        print(f"N {Nrate} kg/ha: base N2O {n2o:.3f} t CO2e/ha; +{int(incr*100)}% = {n2o*incr:.3f} vs avoided {av_lo:.3f}-{av_hi:.3f}")
