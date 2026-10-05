"""Critic check for graft_near_6 (rich/lean amine tankage + off-peak electric regen).
Labels: [idea] from idea/report, [lit] literature (from memory, order of magnitude), [assume], [calc]."""
import sys
sys.path.insert(0, 'climate')
from physics import *

floor = gj_per_tonne(min_separation_work(0.04, 0.9))
print(f"[calc] floor 4% / 90%: {floor:.3f} GJ/t")

Q = 3.35          # GJ_th/t reboiler duty [idea]
steam_pen = 0.30  # MWh_e/t lost from turbine via steam extraction (incl. compression?) [idea]
comp = 0.10       # MWh/t compression, same in all options [physics report]
res = Q/3.6       # resistive MWh_e/t
print(f"[calc] resistive regen {res:.3f} MWh_e/t vs steam extraction {steam_pen} MWh_e/t -> ratio {res/steam_pen:.2f}")

# Heat-pump COP sanity: lift from plant low-grade rejects (stripper condenser / lean cooler /
# compressor intercoolers, ~60-90 C) to ~130 C reboiler steam side; real ~45-55% of Carnot [lit]
for Tsrc in (40, 60, 80, 90):
    Th = 130 + 273.15; Tc = Tsrc + 273.15
    carnot = Th/(Th-Tc)
    print(f"  source {Tsrc} C -> 130 C: Carnot COP {carnot:.1f}, real (0.5x) {0.5*carnot:.1f}")

# System-emissions comparison against the RIGHT counterfactual: conventional steam extraction,
# whose lost peak output is replaced by the peak-hour marginal unit.
print("\n[calc] incremental system CO2 per t captured (regen energy only; compression identical in both)")
print(" off-peak MEF | peak MEF | steam-extr | resistive | HP COP2.5 | HP COP3.5")
for mef_off, mef_peak in [(0.05, 0.45), (0.1, 0.45), (0.25, 0.45), (0.37, 0.45), (0.40, 0.40), (0.40, 0.55)]:
    se = steam_pen*mef_peak
    r = res*mef_off
    h25 = Q/3.6/2.5*mef_off
    h35 = Q/3.6/3.5*mef_off
    print(f"   {mef_off:.2f}      |  {mef_peak:.2f}    |  {se:.3f}     |  {r:.3f}    |  {h25:.3f}    |  {h35:.3f}")
print("[calc] break-even off-peak/peak MEF ratio: resistive "
      f"{steam_pen/res:.2f}, HP2.5 {steam_pen/(res/2.5):.2f}, HP3.5 {steam_pen/(res/3.5):.2f}")

# Hours-availability consistency: stripper sized for daily average runs 8760 h. If e-boiler may run
# only in qualifying (surplus / <100 g) hours H, boiler+stripper must scale 8760*(1-CF)/H relative to
# 'average' sizing and storage must span the gaps.
CF = 0.4
for H in (300, 600, 1500, 3000, 5256):
    scale = 8760*(1-CF)/H
    print(f"[calc] qualifying hours {H:5d}: regen equipment {scale:4.1f}x the off-hour-average size")
print("[lit] GB/DE negative-price hours 2024-25 are O(100s) per year (from memory, unverified) -> "
      "true-surplus hours far below 5,256 off-hours")

# Patch economics: heat pump replaces 90 MWth e-boiler
t_day = 1555; t_yr = t_day*365*1.0  # approx 0.57 Mt? use idea's 0.95 Mt/yr at 40% CF
t_yr = 0.95e6
MWth = Q*1e3*t_yr/8760/3600  # GJ->MWh: Q GJ/t * t/h / 3.6
MWth = Q/3.6*t_yr/8760
print(f"\n[calc] average regen duty {MWth:.0f} MWth (24 h)")
for capex_kw in (400, 700, 1000):  # $/kWth industrial HTHP 120-150 C, [lit] wide range, FOAK
    hp_capex = capex_kw*MWth*1e3/1e6
    eb_capex = 100*MWth*1e3/1e6
    print(f"  HP @ ${capex_kw}/kWth: ${hp_capex:.0f}M vs e-boiler ${eb_capex:.0f}M -> extra ${hp_capex-eb_capex:.0f}M "
          f"(= ${(hp_capex-eb_capex)*0.0707e6/t_yr:.1f}/t at CRF 7.07%)")
# off-peak energy saving from HP vs resistive at delivered $35/MWh, 60% of tonnes shifted
for cop in (2.5, 3.5):
    for p_off, p_peak in [(35, 110), (60, 80)]:
        e = res/cop
        arb = steam_pen*p_peak - e*p_off
        print(f"  COP {cop} off ${p_off} peak ${p_peak}: arbitrage per shifted t = ${arb:.1f}; x0.6 = ${0.6*arb:.1f}/t")
