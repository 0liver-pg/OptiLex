import sys, math
sys.path.insert(0, 'climate')
from physics import *
yr=3.156e7
# 1) pressure diffusion reach (Smackover-like, assumed ranges)
for k_md,phi,mu,ct in [(50,0.15,4e-4,1.5e-9),(100,0.15,4e-4,1e-9),(300,0.2,4e-4,1e-9)]:
    Dh=k_md*9.87e-16/(phi*mu*ct)
    print(f"k={k_md} mD: diffusivity {Dh:.2f} m2/s, sqrt(4Dt) at 1 yr {math.sqrt(4*Dh*yr)/1e3:.1f} km")
# 2) plume radius (volumetric, cylinder, with gravity-override multiplier) per injector
rho=580.
for Q in [0.5,1.0]:   # Mt/yr per injector
  for h,phi,Sg,ovr in [(30,0.15,0.5,1.0),(30,0.15,0.3,2.0),(60,0.2,0.4,1.5)]:
    for t in [10,25]:
        V=Q*1e9/rho*t
        r=math.sqrt(V/(math.pi*h*phi*Sg))*ovr
        print(f"Q={Q} Mt/yr h={h} phi={phi} Sg={Sg} override x{ovr} t={t}y: plume edge ~{r/1e3:.1f} km")
# 3) stranded Li once a pattern is flushed to <=30% grade
for g in [150,300,400]:
  for Swr_vol in [0.57,1.41]:   # stranded m3 brine / t CO2 (critic)
    li=Swr_vol*g*0.3/1e3*0.8   # kg Li at 30% grade, 80% recovery
    lce=li*5.323
    print(f"grade {g} -> 30%: stranded {Swr_vol} m3/t => ${lce*9:.1f}/t CO2 undiscounted at $9k/t LCE")
# 4) avoided Class VI characterisation + pore-space aggregation, $/t (assumed ranges, order-of-magnitude)
for avoided_M, Mt_life in [(15,15),(30,20),(50,30),(60,15)]:
    print(f"avoided ${avoided_M}M over {Mt_life} Mt stored -> ${avoided_M/Mt_life:.1f}/t (undiscounted)")
