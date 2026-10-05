# Patch check for AEC-Q DAC sorbent qualification: capped acceleration, coupon resolution, falsifier informativeness
import sys, math, itertools
sys.path.insert(0,'climate')
from physics import *
R=8.314
def arr(Ea,T1,T2): return math.exp(Ea*1e3/R*(1/(T1+273.15)-1/(T2+273.15)))
print("Thermal AF only (O2 held at plant hot-step pO2):")
for Ea in [60,75,90]:
    print(f" Ea={Ea}: 100->110C {arr(Ea,100,110):.2f}x, 100->120C {arr(Ea,100,120):.2f}x")
# Time compression from duty cycle: stress cell holds hot continuously; plant is hot 15-30% of cycle
print("\nStress hours to emulate field hot-exposure, AF = duty-cycle compression x thermal, capped at 50x:")
for cyc_h,hot,Ea in itertools.product([2,6],[0.15,0.30],[60,90]):
    af=min((1/hot)*arr(Ea,100,120),50)  # note duty compression assumes no cold-step degradation
    for N in [5000,20000]:
        life_hot_h=N*cyc_h*hot
        stress_h=life_hot_h/arr(Ea,100,120)  # hot-time-equivalent at 120C
        print(f" cyc {cyc_h}h hot {hot:.2f} Ea {Ea}: N={N:>5} life={N*cyc_h/8760/0.9:4.1f} yr, hot-h {life_hot_h:7.0f}, stress-h at 120C {stress_h:6.0f} ({stress_h/24/7:4.1f} wk) -> full-life demo {'feasible <=12wk' if stress_h<=12*168 else 'NOT feasible: report lower bound'}")
# Coupon resolution: chemical fingerprint vs capacity
print("\nCoupon 12-mo resolution, 20% fade at EOL, assume fingerprint ~ fade (oxidized amine fraction):")
for cyc_h,N in itertools.product([2,6],[5000,20000]):
    n12=8760*0.9/cyc_h; fade=0.2*n12/N
    for sig_cap,sig_N in [(0.025,0.003)]:   # ASSUMED: capacity +/-2.5% abs; N-loss/FTIR +/-0.3% of amine N abs
        print(f" cyc {cyc_h}h N={N:>5}: 12-mo fade {fade*100:4.1f}%, rel err capacity {2**.5*sig_cap/fade*100:5.0f}%, rel err N-loss/FTIR {2**.5*sig_N/fade*100:4.0f}%")
# Is ratio(6mo/12mo) informative? linear kinetics ->0.5; deceleration (sqrt t) ->0.71; autocatalytic (t^2)->0.25
print("\nRatio 6mo/12mo growth by kinetic form: linear 0.50, diffusion-limited t^0.5 %.2f, autocatalytic t^2 %.2f"%(0.5**0.5,0.25))
print(" -> ratio alone is uninformative for a linear-in-time model; absolute growth vs prediction must be tested too.")
