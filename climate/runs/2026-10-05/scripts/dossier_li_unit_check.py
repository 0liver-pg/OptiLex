"""Independent spot-checks for the lithium-unit storage sequencing dossier."""
import sys, math
sys.path.insert(0, 'climate')
from physics import *
sys.path.insert(0, 'climate/runs/2026-10-05/scripts')
from co2_brine import co2_density
from scipy.special import exp1

# 1. CO2 density / voidage at Smackover conditions
for T, P in [(100, 250), (115, 280), (130, 320)]:
    rho = co2_density(T, P)
    print(f"CO2 {T} C {P} bar: {rho:.0f} kg/m3, {1000/rho:.3f} m3/t")

# 2. Theis dP at r, t for Q (reservoir volume rate), single-phase brine-equivalent
def theis_dp(Qmt, k_md, h, r_km, years, rho=575, mu=4e-4, phi=0.17, ct=1e-9):
    k = k_md * 9.869e-16
    q = Qmt * 1e9 / rho / (365.25 * 86400)  # m3/s
    D = k / (mu * phi * ct)
    t = years * 365.25 * 86400
    u = (r_km * 1e3) ** 2 / (4 * D * t)
    return q * mu / (4 * math.pi * k * h) * exp1(u) / 1e5, D
for k, h in [(50, 30), (100, 40), (300, 60)]:
    dp5, D = theis_dp(1.0, k, h, 5, 25)
    dp7, _ = theis_dp(1.0, k, h, 7, 25)
    print(f"k {k} mD h {h} m: D {D:.2f} m2/s; dP(5 km,25 y, 1 Mt/yr) {dp5:.1f} bar -> cap at 40 bar {40/dp5:.1f} Mt/yr; dP(7 km) {dp7:.1f} bar")

# 3. Net storage after compression electricity emissions
for kwh in [97, 122, 166]:
    for ef in [0.35, 0.45]:  # t CO2/MWh, Gulf Coast grid range [assume]
        print(f"{kwh} kWh/t at {ef} t/MWh: {kwh*ef/1000*100:.1f}% of stored CO2 re-emitted; net {1-kwh*ef/1000:.3f}")

# 4. Energy vs DAC separation floor alone
w_dac = gj_per_tonne(min_separation_work(420e-6, 0.75, 0.99)); w_amm = gj_per_tonne(min_separation_work(0.98, 0.90, 0.999))
print(f'verifier: DAC floor {w_dac:.3f} GJ/t; ammonia CO2 floor {w_amm:.4f} GJ/t')
print("DAC floor (from task statement) 0.47 GJ/t; this pathway total base 0.44 GJ/t incl. compression")

# 5. 45Q vs lithium per t LCE, and per t CO2
for tco2_per_tlce in [337, 900]:
    print(f"{tco2_per_tlce} t CO2/t LCE x $85 = ${tco2_per_tlce*85/1e3:.1f}k per t LCE")

# 6. Stranded Li value at full grade (critic's claim), Swr 0.25-0.45 of 1.74 m3 voidage... critic gives 0.57-1.41 m3/t
for vol in [0.57, 1.41]:
    for c in [150, 400]:
        li_kg = vol * c / 1000 * 0.8
        lce = li_kg * 5.323
        print(f"stranded {vol} m3/t at {c} mg/L: {li_kg:.3f} kg Li, {lce:.2f} kg LCE, ${lce*9:.1f}/t at $9k/t LCE")
