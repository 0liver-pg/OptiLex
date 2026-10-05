import sys, math
sys.path.insert(0, 'climate')
from physics import *

# Minimum separation work at 90% capture
cases = {"NGCC 4%":0.04, "coal 12%":0.12, "cement 25%":0.25, "SMR syngas ~15-20% (use 0.18)":0.18}
mins = {k: gj_per_tonne(min_separation_work(x,0.9,0.99)) for k,x in cases.items()}
for k,v in mins.items(): print(f"min sep {k}: {v:.3f} GJ/t ({v/0.0036:.0f} kWh/t)")

# Minimum isothermal compression of pure CO2 (ideal gas) from stripper ~1.8 bar or 1 atm to 110 bar
for p1 in (1.013, 1.8):
    w = R*T0*math.log(110/p1)
    print(f"min compression {p1}->110 bar: {gj_per_tonne(w):.3f} GJ/t")
comp_min = gj_per_tonne(R*T0*math.log(110/1.013))

# Exergy of reboiler heat: amine reboiler duty Q at steam condensing T
print("\nExergy of reboiler steam heat (Carnot factor 1-T0/Ts):")
for Q in (2.4, 2.6, 3.0, 3.6):
    for Ts_C in (120, 135):
        cf = 1 - T0/(Ts_C+273.15)
        ex = Q*cf
        print(f"Q={Q} GJ/t at {Ts_C}C: exergy {ex:.2f} GJ/t; + compression ~0.35 GJ_e/t (~100 kWh/t) + aux 0.1 -> total {ex+0.45:.2f}; "
              f"2nd-law eff vs coal min sep+comp {(mins['coal 12%']+comp_min)/(ex+0.45):.0%}, vs NGCC {(mins['NGCC 4%']+comp_min)/(ex+0.45):.0%}")

# Boundary Dam 3 measured-derived: net output 160 -> 110 MW (CCS+SO2 capture), design 1 Mt/yr ~ 3,240 t/d
for derate_MW, tpd in ((50, 3240), (50, 2826)):
    mwh_per_t = derate_MW*24/tpd
    gj = mwh_per_t*3.6
    eff = (mins['coal 12%']+comp_min)/gj
    print(f"\nBD3: {derate_MW} MW derate at {tpd} t/d -> {mwh_per_t:.3f} MWh_e/t = {gj:.2f} GJ_e/t; "
          f"2nd-law eff (sep+compression min {mins['coal 12%']+comp_min:.2f}) = {eff:.0%}")
    for price in (40, 60, 100):
        print(f"   energy cost at ${price}/MWh: ${mwh_per_t*price:.0f}/t")

# Energy cost floor at thermodynamic minimum
for k,v in mins.items():
    tot = v+comp_min
    print(f"floor energy cost {k} sep+comp {tot:.2f} GJ/t at $60/MWh: ${energy_cost_floor(tot,60):.1f}/t")

# BD3 emission intensity check: 348 t/GWh net (Aug23-Aug24). Unabated lignite ~ 1.1 t/MWh gross-sent-out at 160 MW net
gross_rate = 1.1*160  # t/h at 160 MW net unabated
for unabated in (1.0, 1.1, 1.2):
    gr = unabated*160
    resid = 348*110/1000  # t/h at 110 MW net
    print(f"unabated {unabated} t/MWh: implied capture fraction while running = {1-resid/gr:.0%} (captured {gr-resid:.0f} t/h = {24*(gr-resid):.0f} t/d)")

# Scale: point sources
for gj in (1.0, 1.33, 2.0):
    s = ScaleCheck(gt_per_year=10.0, gj_per_tonne=gj)
    print(f"10 Gt/yr point-source at {gj} GJ_e/t: {s.ej_per_year:.1f} EJ = {s.share_of_world_electricity_if_electric:.0%} of world electricity")
