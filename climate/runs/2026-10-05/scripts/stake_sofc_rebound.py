"""Stakeholder-relevant rebound check for graft_electro_2 (SOFC on stranded Permian associated gas).
All inputs ASSUMED unless noted; order-of-magnitude only."""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

GOR_mcf_per_bbl = (3.5, 4.2, 5.0)   # ASSUMED Permian associated-gas/oil ratio (~27 bcf/d gas vs ~6.5 mb/d oil, 2025 order of magnitude)
gas_bcfd = 1.0                       # idea's constrained-gas tranche
t_co2_per_bbl = 0.43                 # ASSUMED combustion CO2 of a barrel of crude (EPA ~0.43 t/bbl)
captured_mt = 20.0                   # idea's claim

print("Worst case: the gas outlet is what lets the oil flow (i.e., oil would otherwise be shut in)")
for g in GOR_mcf_per_bbl:
    oil_bpd = gas_bcfd * 1e6 / g     # mcf/d / (mcf/bbl)
    co2 = oil_bpd * 365 * t_co2_per_bbl / 1e6
    print(f"  GOR {g}: {oil_bpd/1e3:.0f} kb/d oil -> {co2:.0f} Mt CO2/yr downstream vs {captured_mt} Mt captured (ratio {co2/captured_mt:.1f}x)")

print("\nMarginal case: outlet only removes a disposal cost; oil supply responds via netback")
waha = -2.38  # $/MMBtu, 2026 YTD avg (from idea)
for g in GOR_mcf_per_bbl:
    netback_gain = -waha * g * 1.05  # $/bbl, ~1.05 MMBtu/mcf
    print(f"  GOR {g}: netback gain ${netback_gain:.1f}/bbl")
# ASSUMED medium-run Permian supply elasticity 0.1-0.5 vs a ~$60-70/bbl price; 1 bcf/d tranche of ~27 bcf/d basin
for elas in (0.1, 0.3, 0.5):
    for g in (4.2,):
        gain = -waha * g * 1.05
        base_oil_bpd = gas_bcfd * 1e6 / g          # oil tied to the tranche
        d_oil = base_oil_bpd * elas * gain / 65.0  # fractional price-equivalent change
        co2 = d_oil * 365 * t_co2_per_bbl / 1e6
        print(f"  elasticity {elas}: +{d_oil/1e3:.1f} kb/d -> +{co2:.1f} Mt CO2/yr (gross, before global oil-market leakage offset) vs {captured_mt} captured")

print("\n45Q fiscal cost at $85/t:", f"${captured_mt*85/1e3:.2f} bn/yr per {captured_mt} Mt")
print("Flaring baseline cross-check: GGFR 2024 151 bcm flared globally; 1 bcf/d = ", f"{1*0.0283168*365:.1f} bcm/yr")
