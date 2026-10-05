"""Idea 5: tropical hydropower. Dissolved CH4 in hypolimnetic turbine water degasses downstream.
Put the degassing in an ENCLOSED cascade/aerating weir just below the tailrace, draw a controlled
air sweep through it, and send that VAM-like air (0.3-2% CH4) to an RTO or boiler."""
from common import *

H_cc = 30.0   # dimensionless Henry gas/liquid concentration ratio for CH4 at ~25-28 C (approx)
print("Air sweep needed: stripping factor S = H_cc * G/L; fraction stripped ~ 1-1/S for a counter-current-like")
print("cascade at high NTU (optimistic) - use S>=4 for ~75% recovery")
for c_mgL in (0.5, 2.0, 5.0):
    for q in (500, 2000):
        ch4_kg_s = q * c_mgL / 1000
        for S in (4,):
            G = S / H_cc * q                     # m3/s air
            y = ch4_kg_s * 0.75 / 0.668 / G       # vol fraction in sweep air
            t_yr = ch4_kg_s * 0.75 * 3.1536e7 / 1000
            print(f"  {c_mgL} mg/L, {q} m3/s: dissolved CH4 {ch4_kg_s:.2f} kg/s; air sweep {G:.0f} m3/s -> sweep CH4 {y:.2%}; "
                  f"recovered {t_yr/1e3:.0f} kt CH4/yr = {t_yr*GWP100['CH4_biogenic']/1e6:.2f} Mt CO2e (GWP100 biogenic)")

print("\nEnergy and cost per t CO2e (cascade head loss is the dominant 'energy' cost = foregone hydropower):")
for c_mgL, q, head in [(2.0, 1000, 2.0), (2.0, 1000, 4.0), (0.5, 1000, 3.0), (5.0, 1000, 3.0)]:
    ch4_kg_s = q * c_mgL / 1000 * 0.75
    p_lost_mw = q * 1000 * 9.81 * head * 0.9 / 1e6    # turbine-equivalent output lost
    G = 4 / H_cc * q
    fan_mw = G * 800 / 0.6 / 1e6
    gj_per_t_ch4 = (p_lost_mw + fan_mw) / ch4_kg_s       # MW / (kg/s) = MJ/kg = GJ/t
    co2e_per_s = ch4_kg_s * GWP100['CH4_biogenic']
    cost = (p_lost_mw + fan_mw) * 50 / (co2e_per_s * 3.6)   # $/t at $50/MWh
    print(f"  {c_mgL} mg/L, {q} m3/s, head loss {head} m: lost output {p_lost_mw:.0f} MW + fans {fan_mw:.1f} MW -> "
          f"{gj_per_t_ch4:.1f} GJ/t CH4 = {gj_per_t_ch4/GWP100['CH4_biogenic']:.2f} GJ/t CO2e; energy cost ${cost*1:.1f}/t CO2e")
print("  (Verifier comparison: fan work alone for ambient-air methane removal = 8.8 GJ/t CO2e GWP100.)")

print("\nRTO viability of the sweep air: autothermal needs >= ~0.18-0.2% CH4 (map), so all cases >= 0.5 mg/L qualify.")
print("Capex sketch: RTO sized like MATEC case (360,000 m3/h = 100 m3/s for EUR 9.5M):")
for c_mgL, q in [(2.0, 1000)]:
    G = 4 / H_cc * q
    n_rto = G / 100
    capex = n_rto * 9.5e6 * 1.08 + 30e6       # + enclosure/cascade structure (assumption $30M)
    ch4 = q * c_mgL / 1000 * 0.75 * 3.1536e7 / 1000
    ann = capex * crf(0.08, 20)
    print(f"  {G:.0f} m3/s sweep -> {n_rto:.1f} MATEC-size RTO units; capex ${capex/1e6:.0f}M -> ${ann/(ch4*GWP100['CH4_biogenic']):.2f}/t CO2e")
