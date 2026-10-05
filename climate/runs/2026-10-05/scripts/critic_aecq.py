# Critic check: can a 6-month field rig resolve fade well enough to test a +/-30% prediction?
import itertools
hours=0.5*8760*0.9
for cyc_h,N in itertools.product([2,6],[1000,5000,20000]):
    n=hours/cyc_h
    fade=min(0.2*n/N,1.0)  # EOL = 20% capacity loss at N cycles, linear
    for sigma in [0.02,0.03]:  # capacity measurement repeatability (abs fraction, 1-sigma) assumed
        # relative error on fade from differencing two capacity measurements
        rel=(2**0.5*sigma)/fade if fade>0 else float('inf')
        print(f"cycle {cyc_h}h N={N:>6} cycles_in_6mo={n:6.0f} field_fade={fade*100:5.1f}%  meas_sigma={sigma*100:.0f}% -> 1-sigma rel err on fade {rel*100:6.0f}%")
