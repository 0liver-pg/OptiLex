# Patch check for coalition_6: origin-neutral, EUA-indexed CCfD. Volume fundable with same budget,
# cash-flow profile, LDC set-aside, CO2 avoided. Base case premium EUR200/t steel, 1.65 tCO2/t avoided.
import sys; sys.path.insert(0,'climate')
import numpy as np
years=np.arange(2028,2038)
cbam={2026:.025,2027:.05,2028:.10,2029:.225,2030:.485,2031:.61,2032:.735,2033:.86,2034:1.0}
share=lambda y: cbam.get(y,1.0)
avoid=1.65
paths={"flat130":lambda y:130.,"rising75-115":lambda y:min(115,75+40*(y-2026)/8),"flat70":lambda y:70.}
budgets={ # EUR bn/yr inflow (CBAM part + buyer club 12M cars x 150-200)
 "pilot: MS 25% + club(lo)":0.47+1.8, "pilot: MS 25% + club(hi)":0.47+2.4,
 "full: all CBAM + club(lo)":1.87+1.8, "full: all CBAM + club(hi)":1.87+2.4}
for prem in (150,200,250):
  print(f"\n=== strike premium EUR{prem}/t steel ===")
  for pn,eua in paths.items():
    gaps=np.array([max(0,prem-eua(y)*avoid*share(y)) for y in years]); life=gaps.sum()
    fixed=prem*len(years)
    for bn,b in budgets.items():
      tot=b*1e9*len(years)
      mt_idx=tot/life/1e6 if life>0 else float('inf'); mt_fix=tot/fixed/1e6
      # cash flow: constant contracted volume mt_idx, payments by year vs flat inflow -> peak cumulative deficit
      pay=gaps*mt_idx*1e6; cum=np.cumsum(b*1e9-pay); peak_def=-min(0,cum.min())/1e9
      print(f"{pn:14s} {bn:27s} lifetime idx EUR{life:6.0f}/t (fixed {fixed}) | Mt steel/yr idx {mt_idx:6.1f} vs fixed {mt_fix:5.1f} | MtCO2/yr {mt_idx*avoid:6.1f} | peak bridge EUR{peak_def:4.1f}bn")
  print("year-by-year gap (EUR/t), rising path:",[(int(y),round(max(0,prem-paths['rising75-115'](y)*avoid*share(y)))) for y in years])
# Cap volume at a physically/market-plausible level: EU BF hot metal ~70 Mt; contract cap 35 Mt steel-eq
print("\nCap at 35 Mt steel-eq/yr ->",35*avoid,"MtCO2/yr; 25 Mt ->",25*avoid)
print("LDC set-aside 10% of pilot pool (EUR bn/yr):",[round(0.1*b,2) for b in (2.27,2.87)], "full:",[round(0.1*b,2) for b in (3.67,4.27)])
