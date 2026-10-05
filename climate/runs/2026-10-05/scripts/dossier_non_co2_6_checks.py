"""Dossier checks for non_co2_6 (HFC-23 -> VDF, input-side balance). Labels: [M] measured, [Mod] modelled, [A] assumption."""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa
M = {'CHF3': 70.014, 'VDF': 64.035, 'C2F4': 100.016, 'HF': 20.006, 'CH4': 16.043}
GWP = 14_600
print("1. VDF offset at MEASURED selectivities (per t HFC-23 converted; revenue only, before capex)")
cases = {"Yu et al. thermal, CH4/CHF3=1.1, 1153 K [M]": 0.154,
         "Yu et al. thermal, CH4/CHF3=2.1, 1153 K [M]": 0.224,
         "Han et al. 2010 promoted (CBrF3) upper [M]": 0.43,
         "idea's assumed band, low/high [A]": 0.40, "idea high [A]": 0.80}
for k, s in cases.items():
    lo, hi = (M['VDF'] / M['CHF3']) * s * 3000, (M['VDF'] / M['CHF3']) * s * 7000
    print(f"  {k:<46} sel {s:.3f}: VDF revenue ${lo:,.0f}-{hi:,.0f}/t HFC-23 = ${lo/GWP:.3f}-{hi/GWP:.3f}/t CO2e")
# marginal opex per t HFC-23 using the critic's base cost terms (disposal $500, energy 7.73 GJ x $8, excess CH4)
opex_base = 500 + 7.73 * 8 + 2 * M['CH4'] / M['CHF3'] * 50 * 8 * 0.3
for s in (0.154, 0.224, 0.43):
    rev = s * M['VDF'] / M['CHF3'] * 3500 + s * M['HF'] / M['CHF3'] * 1500
    print(f"  base price $3,500/t VDF, sel {s:.3f}: margin ${rev - opex_base:+,.0f}/t HFC-23 (critic base opex ${opex_base:,.0f}); vs destruction ~$1,020/t avoided")
print("  -> at measured thermal selectivity the offset roughly breaks even against opex only; TFE (PFAS monomer) is the main co-product")

print("\n2. Eastern China: venting share vs undeclared production that would explain the excess (parametric) [A]")
excess = (3.5, 4.3)  # Gg above China's report, 2021/2022 [M Adam 2024]
for P in (0.6, 0.8, 1.0):        # Mt HCFC-22/yr declared, China [A, not verified]
    for r in (0.02, 0.03):
        G = r * P * 1e3          # kt HFC-23 generated
        print(f"  P={P} Mt, r={r:.0%}: generated {G:4.0f} kt; excess = {excess[0]/G:.0%}-{excess[1]/G:.0%} of generation un-destroyed, "
              f"OR {excess[0]/r:,.0f}-{excess[1]/r:,.0f} kt/yr undeclared HCFC-22 (+{excess[0]/r/(P*1e3):.0%}-{excess[1]/r/(P*1e3):.0%})")
print("  -> both explanations need only modest shares; atmospheric data alone cannot discriminate (motivates desk test)")

print("\n3. Abatement value of the eastern-China excess alone")
for g in excess:
    print(f"  {g} Gg = {g*GWP/1e3:.0f} Mt CO2e/yr GWP100 = {g*GWP/1e3/(FOSSIL_CO2_GT*1e3):.2%} of fossil CO2; "
          f"at $0.25/t total cost = ${g*GWP/1e3*0.25:.0f}M/yr")
print("\n4. Penalty needed with a 20% commissioning bias (detection prob 0.04-0.05 at 20% venting)")
for pdet in (0.05,):
    print(f"  base avoided cost $1.02/kg / {pdet} = ${1.02/pdet:.0f}/kg = ${1.02/pdet*1e3/GWP:.2f}/t CO2e -> bias must be removed, not out-penalised")
