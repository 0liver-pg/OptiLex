# Critic check: fixed-gap 10-yr contract vs EUA-indexed CCfD, base case (EUR 200/t premium, 1.65 tCO2/t avoided)
import numpy as np
years=np.arange(2028,2038)
# free-allocation phase-out share (CBAM factor) per regulation: 2028 51.5%,2029 39%,2030 26.5%,2031 14%,2032 2.5%,2033+ 0 free alloc
cbam={2026:.025,2027:.05,2028:.10,2029:.225,2030:.485,2031:.61,2032:.735,2033:.86,2034:1.0}
def share(y): return cbam.get(y,1.0)
premium=200.0; avoid=1.65
for label,eua in [("rising 75->115 then flat",lambda y: min(115,75+(115-75)*(y-2026)/8)),("flat 70",lambda y:70.0),("flat 130",lambda y:130.0)]:
    fixed=0;indexed=0;rows=[]
    for y in years:
        carbon=eua(y)*avoid*share(y)   # carbon cost the BF route faces (net of free allocation)
        gap=max(0,premium-carbon)
        fixed+=premium; indexed+=gap; rows.append((y,round(gap)))
    print(label, "fixed-gap total EUR/t over 10y:",fixed,"indexed:",round(indexed),"overpay %:",round(100*(fixed-indexed)/fixed), rows)
# Fund at 18.7 Mt/yr: overpayment in EUR bn over contract life
