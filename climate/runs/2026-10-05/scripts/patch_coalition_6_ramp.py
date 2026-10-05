# Vintage-ramp contracting: sign a new tranche each year (10-yr contracts), payment = calendar-year indexed gap.
# Check cash flow against flat inflow (net of 10% LDC set-aside), premium EUR200/t, 1.65 tCO2/t.
import numpy as np
cbam={2026:.025,2027:.05,2028:.10,2029:.225,2030:.485,2031:.61,2032:.735,2033:.86,2034:1.0}
share=lambda y: cbam.get(y,1.0); avoid=1.65
paths={"flat130":lambda y:130.,"rising75-115":lambda y:min(115,75+40*(y-2026)/8),"flat70":lambda y:70.}
yrs=range(2028,2038)
def run(prem,eua,inflow_bn,tranche,maxvol):
    vol=0; cum=0; worst=0; out=[]
    for y in yrs:
        vol=min(maxvol,vol+tranche)
        pay=vol*1e6*max(0,prem-eua(y)*avoid*share(y))/1e9
        cum+=0.9*inflow_bn-pay; worst=min(worst,cum); out.append((y,vol,round(pay,2)))
    return worst,cum,out
for pn,eua in paths.items():
  for inflow,lab in ((2.27,"pilot lo"),(2.87,"pilot hi"),(3.67,"full lo")):
    # find largest cap volume (ramp 6 Mt/yr) with no deficit at all (no bridge)
    best=0
    for cap in np.arange(5,80,0.5):
        w,c,_=run(200,eua,inflow,6,cap)
        if w>=-1e-9: best=cap
    w,c,o=run(200,eua,inflow,6,best)
    print(f"{pn:13s} {lab:8s} no-bridge cap {best:5.1f} Mt steel ({best*avoid:5.1f} MtCO2/yr at full ramp); end-2037 surplus EUR{c:5.1f}bn")
w,c,o=run(200,paths["rising75-115"],2.27,6,30); print("rising, pilot lo, cap30:",o, "worst",round(w,1),"end",round(c,1))
