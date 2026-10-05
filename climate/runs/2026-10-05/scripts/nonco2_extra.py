import sys
sys.path.insert(0, 'climate')
from physics import *
# Minimum work to concentrate dilute CH4 to an autothermal concentration (0.5%) or pure
for x in (1.93e-6, 10e-6, 100e-6):
    for p in (0.005, 0.99):
        w = min_separation_work(x, 0.9, p)
        g = gj_per_tonne(w, M_CH4)
        print(f"CH4 {x*1e6:7.2f} ppm -> {p*100:5.1f}%: {w/1e3:5.1f} kJ/mol = {g:5.2f} GJ/t CH4 = {g/GWP100['CH4_biogenic']:.3f} GJ/t CO2e(100)")
# HFC-23 measured emissions in CO2e (AR6 GWP100 HFC-23 = 14,600)
print(f"HFC-23 14.0 Gg/yr x 14,600 = {14.0e3*14600/1e6:.0f} Mt CO2e/yr; reported ~1/5 = {14.0e3*14600/5/1e6:.0f} Mt")
