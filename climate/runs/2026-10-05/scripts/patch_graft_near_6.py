"""Patch check for graft_near_6: heat-pump reboiler fed by capture-train reject heat replaces e-boiler.
Labels: [idea] idea basis, [critic] critic's values, [lit] literature from memory (order of magnitude), [assume], [calc]."""
import sys
sys.path.insert(0, 'climate')
from physics import *

floor = gj_per_tonne(min_separation_work(0.04, 0.90, 0.99))
print(f"[calc] floor 4%/90%: {floor:.3f} GJ/t")
cap_tph, P = 270.0, 742.0                      # [idea]
capex_capture = P*1e3*(1936-970)/1e6           # $M 2018 [idea, NETL Rev4A]
Q = 3.35                                       # GJ_th/t reboiler duty [critic base]
steam_pen = 0.30                               # MWh_e/t turbine output lost to steam extraction [critic]
CRF = 0.0707
n = 0.65

def hp_power(cop): return Q/3.6/cop             # MWh_e/t

# reject-heat availability: HP needs Q*(1-1/COP) source heat
for cop in (2.5, 2.9, 3.0, 4.0):
    print(f"[calc] COP {cop}: HP elec {hp_power(cop):.2f} MWh/t; source heat needed {Q*(1-1/cop):.2f} GJ/t")
print("[lit] stripper overhead condenser in MEA ~ 0.8-1.5 GJ/t; lean-amine trim cooler ~1-2 GJ/t; compressor "
      "intercoolers ~0.3-0.5 GJ/t (orders of magnitude, unverified) -> enough heat in aggregate, but much of it is <60 C: pinch test needed")

# comparative climate guard break-even ratio MEF_off/MEF_peak
for cop in (2.5, 2.9, 3.5, 4.0):
    print(f"[calc] guard break-even MEF_off/MEF_peak at COP {cop}: {steam_pen/hp_power(cop):.2f}")

# economics at CF
cases = {  # (cyclic cap mol/kg, amine $/kg, tank $/m3, HP $/kWth, COP, p_off, p_peak, regen share)
 "favourable":   (1.2, 1.6, 150, 400, 4.0, 35, 110, 0.45),
 "base":         (0.8, 2.0, 250, 700, 2.9, 35, 110, 0.35),
 "unfavourable": (0.5, 2.5, 500, 1000, 2.5, 60, 80, 0.25),
}
for cf in (0.25, 0.40, 0.60):
    h_on = 24*cf; daily = cap_tph*h_on; avg = daily/24; buf = cap_tph*h_on*(1-cf)
    t_yr = cap_tph*8760*cf
    print(f"\nCF {cf:.0%}: buffer {buf:.0f} t CO2/day, avg regen {avg:.0f} t/h, {t_yr/1e6:.2f} Mt/yr")
    for name, (cyc, ap, tc, hpc, cop, poff, ppeak, share) in cases.items():
        mass_t = buf*1e6/44.01/cyc/1e3
        vol = mass_t/1.05
        amine = mass_t*0.30*1e3*ap/1e6
        tanks = 2*vol*tc/1e6
        hp_mw = avg*Q/3.6
        hp = hp_mw*1e3*hpc/1e6
        added = amine + tanks + hp
        saving = capex_capture*share*(1-cf**n)
        capex_t = (saving-added)*1e6*CRF/t_yr
        arb_shift = steam_pen*ppeak - hp_power(cop)*poff        # per off-hours tonne
        arb_on = (steam_pen - hp_power(cop))*ppeak              # on-hours tonnes: HP at peak price vs steam extraction
        arb = (1-cf)*arb_shift + cf*arb_on
        print(f"  {name:<12} amine ${amine:.0f}M tanks ${tanks:.0f}M ({vol/1e3:.0f}k m3 each) HP {hp_mw:.0f} MWth ${hp:.0f}M"
              f" -> added ${added:.0f}M vs saving ${saving:.0f}M net ${saving-added:+.0f}M = ${capex_t:+.1f}/t; "
              f"arbitrage ${arb:+.1f}/t (shifted ${(1-cf)*arb_shift:+.1f}, on-hrs ${cf*arb_on:+.1f}); total ${capex_t+arb:+.1f}/t")

# avoided emissions (system) per t captured, CF40, base COP 2.9
print("\n[calc] system CO2 per t captured, regen energy only (compression identical)")
for moff, mpk in [(0.05,0.45),(0.25,0.45),(0.40,0.45),(0.45,0.40)]:
    print(f"  MEF off {moff} peak {mpk}: steam-extraction {steam_pen*mpk:.3f}; HP COP2.9 shifted {hp_power(2.9)*moff:.3f}")
