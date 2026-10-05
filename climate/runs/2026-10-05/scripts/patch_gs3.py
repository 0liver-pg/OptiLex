import sys, math; sys.path.insert(0,'climate')
from physics import *
def fo_rate(T_C,pH):
    T=T_C+273.15; f=lambda Ea: math.exp(-Ea/8.314*(1/T-1/298.15))
    return 10**-6.85*f(67200)*(10**-pH)**0.47+10**-10.64*f(79000)
mol_fo=1e6/44.01/2; target=0.1e6; mol_s=target*mol_fo/3.156e7; geo=40*2*100*50*2
print("geo area",geo, "required kg CO2/m2/yr", target*1e3/geo)
for T in (60,90,110,130,150):
    need=mol_s/fo_rate(T,5.0); print(f"T {T} C pH5: area {need:.2e} m2 = {need/geo:.0f}x geometric face")
# bench sample: 50x100 mm saw-cut, two faces
A=0.05*0.1*2
for d in (60,90):
    print(f"{d} d: target {125*A*d/365*1e3:.0f} g; 1/3 {125/3*A*d/365*1e3:.0f} g; kill 1/10 {12.5*A*d/365*1e3:.1f} g")
# depth for initial rock T, surface 25 C (Oman ~30 C), gradients
for Tr in (90,130,150):
    for g in (25,30):
        z=(Tr-25)/g; sv=z*1e3*3000*9.81/1e6; pp=z*1e3*1050*9.81/1e6
        print(f"rock {Tr} C at {g} C/km: depth {z:.1f} km, Sv {sv:.0f} MPa, Pp {pp:.0f} MPa, Sv-Pp {sv-pp:.0f} MPa")
# crystallisation pressure magnesite, Vm 28.0 cm3/mol
for T in (90,150):
    for lnO in (0.25,0.5,1.0):
        print(f"T {T} C lnOmega {lnO}: Pc {8.314*(T+273.15)/28.0e-6*lnO/1e6:.0f} MPa")
