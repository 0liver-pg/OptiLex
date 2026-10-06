import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
"""Mass-transfer and air-supply limits of a laminar-channel DAC contactor (screening level).

Laminar channel with a perfect-sink wall: Sh = 3.66 (constant wall concentration).
NTU = 4 Sh D L / (d^2 u);  dP = 32 mu L u / d^2  (Hagen-Poiseuille)
=> dP = 8 mu u^2 NTU / (Sh D): the gas-film-limited pressure drop depends only on channel velocity and NTU.
"""
import math

MU = 1.8e-5      # Pa s, air
D = 1.6e-5       # m2/s, CO2 in air
SH = 3.66
c_in = P0 / (R * T0) * X_AIR    # mol/m3

print(f"CO2 concentration in air: {c_in*1000:.2f} mmol/m3")
print("\n== A. Gas-film-limited pressure drop for a given capture fraction ==")
for cf in (0.5, 0.75, 0.9):
    ntu = -math.log(1 - cf)
    for u in (1, 2, 3, 5):
        dp = 8 * MU * u**2 * ntu / (SH * D)
        fan = fan_work_gj_per_tonne(X_AIR, cf, dp)
        print(f"  capture {cf:.0%} (NTU {ntu:.2f}), channel velocity {u} m/s: dP {dp:6.1f} Pa, fan {fan:.3f} GJ_e/t")

print("\n== B. Measured / assumed contactor pressure drops vs the film limit at 60% capture, 2.5 m/s ==")
ntu = -math.log(1 - 0.6); dp_film = 8 * MU * 2.5**2 * ntu / (SH * D)
print(f"  film-limit dP: {dp_film:.0f} Pa")
for dp, tag in ((150, "Global Thermostat monolith claim (<150 Pa at 5 m/s, L 0.15 m)"),
                (220, "Wu 2026 rotary honeycomb (measured, <=220 Pa)"),
                (295.5, "NETL Rev1 monolith bed (assumed)"),
                (900, "Climeworks/Svante Gen2 laminate field target 800-1000 Pa"),
                (550, "Climeworks/Svante Gen3 target 400-700 Pa"),
                (2000, "granular packed bed (Wu 2026 comparison, >2000 Pa)")):
    print(f"  {tag:<62} {dp:>6.0f} Pa = {dp/dp_film:5.1f}x film limit; fan {fan_work_gj_per_tonne(X_AIR, 0.6, dp):.2f} GJ_e/t")

print("\n== C. Gas-film-limited uptake rate of a thin coating vs field-measured uptake ==")
for d_mm in (0.5, 1.0, 2.0):
    kg = SH * D / (d_mm * 1e-3)          # m/s
    flux = kg * c_in                      # mol/m2/s at inlet concentration
    for delta_um, rho in ((50, 500), (100, 500), (300, 500)):
        areal = delta_um * 1e-6 * rho     # kg sorbent per m2 wall
        rate = flux / areal * 60          # mol/kg/min at inlet concentration
        print(f"  channel {d_mm} mm (k_g {kg*100:.1f} cm/s), coating {delta_um} um: "
              f"film-limited uptake {rate:5.2f} mol/kg/min (inlet), ~{rate*0.6:4.2f} log-mean at 60% capture")
print("  field-measured laminate KPI (Climeworks/Svante IDS, 2023): 0.05-0.07 mol/kg/min")

print("\n== D. Air-supply (stoichiometric) adsorption time: t = areal sorbent loading x wc / (v c capture) ==")
for rho_bed, L, wc_used, v, cf, tag in ((200, 0.30, 0.6, 2.0, 0.6, "laminate-like, 0.3 m deep"),
                                        (200, 0.15, 0.6, 2.5, 0.6, "laminate-like, 0.15 m deep"),
                                        (135, 0.29, 0.8, 2.48, 0.6, "NETL Rev1 monolith (24 lb/ft3 x 0.35 solid, 0.95 ft, 8.14 ft/s)"),
                                        (500, 0.02, 1.0, 0.5, 0.6, "thin packed sheet 22 mm (Zheng 2026 style)"),
                                        (600, 0.50, 1.0, 0.3, 0.9, "deep packed bed 0.5 m at 0.3 m/s")):
    areal = rho_bed * L
    t = areal * wc_used / (v * c_in * cf)
    print(f"  {tag:<64} {areal:6.1f} kg/m2-face -> t_ads {t/60:6.1f} min; "
          f"productivity ceiling {wc_used*M_CO2*86400/t:5.2f} kg/kg/day (adsorption only)")

print("\n== E. Fraction of time adsorbing: productivity penalty of slow regeneration ==")
for t_ads, t_reg in ((30, 10), (30, 30), (33, 15), (180, 18), (5, 5), (20, 60)):
    print(f"  ads {t_ads:>3} min + regen/cool {t_reg:>3} min: on-stream fraction {t_ads/(t_ads+t_reg):.0%}")
