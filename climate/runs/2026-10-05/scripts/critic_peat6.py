import sys
sys.path.insert(0, 'climate')
from physics import *
# Hooijer 2012 plantation regression CL = 21 + 69*WD (t CO2/ha/yr), drained-forest CL = 98*WD
plant = lambda wd: 21 + 69*wd
forest = lambda wd: 98*wd
t_per_cm = 13.9  # t CO2/ha per cm subsidence (Hooijer params, from TEA report)
base_net = 32.0
for wd_ctrl in (0.7, 0.8, 0.9, 1.0):
    extra = plant(wd_ctrl) - plant(0.7)
    print(f"control WT {wd_ctrl} m: control emission {plant(wd_ctrl):.1f}, extra vs 0.7 m {extra:.1f} t/ha/yr "
          f"= {extra/t_per_cm:.2f} cm/yr extra subsidence, {100*extra/base_net:.0f}% of base net payable")
# swelling masking: residual oxidation at rewetted WT while surface reads ~0
for wd in (0.05, 0.15, 0.30):
    print(f"rewetted mean WT {wd} m: residual {forest(wd):.1f} t/ha/yr = {forest(wd)/t_per_cm:.2f} cm/yr hidden if swelling offsets")
# hydrological edge effect: fraction of a 100 ha (1 km x 1 km) control within buffer of shared boundary
for buf in (100, 250, 500):
    print(f"edge buffer {buf} m: {100*buf/1000:.0f}% of a 1x1 km control block affected along one shared edge")
