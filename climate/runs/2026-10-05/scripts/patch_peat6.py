import sys; sys.path.insert(0,'climate')
from physics import *
# BACI paid-tonnes estimator, per ha/yr. Subsidence cm/yr -> t CO2/ha/yr
def t_co2(sub_cm, bd=0.09, cf=0.56, ox=0.85):   # bd t/m3
    return sub_cm/100*1e4*bd*cf*ox*44/12
CH4=0.041*28  # 41 kg CH4/ha/yr IPCC default, GWP100 AR5=28 -> t CO2e
def paid(pre,post,wt,leak,buf=0.2,bd=0.09):
    pre_e=t_co2(pre,bd)
    post_e=max(t_co2(post,bd), 98*wt)   # conservative: larger of InSAR post-trend and dipwell residual (no double count)
    return (pre_e-post_e-CH4)*(1-leak)*(1-buf), pre_e, post_e
res=[]
for pre in (3,4,5):
  for post in (0.5,1.0):
    for wt in (0.15,0.30):
      for leak in (0.2,0.3):
        for bd in (0.08,0.10):
          res.append(paid(pre,post,wt,leak,bd=bd)[0])
print("paid t/ha/yr range %.1f-%.1f"%(min(res),max(res)))
c,pe,po=paid(4,1,0.2,0.25)
print("central pre %.1f post %.1f paid %.1f"%(pe,po,c))
lo=paid(3,1,0.3,0.3,bd=0.08)[0]; hi=paid(5,0.5,0.15,0.2,bd=0.10)[0]
print("low %.1f high %.1f"%(lo,hi))
for m in (300,900): print("margin",m,"breakeven $/t: central %.0f, range %.0f-%.0f"%(m/c,m/hi,m/lo))
print("MRV $2-5/ha/yr = $%.2f-%.2f/t"%(2/c,5/c))
for A in (0.5,1,2): print(A,"Mha -> paid %.0f Mt/yr (range %.0f-%.0f)"%(A*c,A*lo,A*hi))
# gross physical abatement (pre undeducted for leakage/buffer)
print("physical avoided central %.0f t/ha/yr"%(pe-po-CH4))
# control-gaming exposure under old design vs new: 0.7->0.9 m adds 13.8 t (critic); new design pays 0 for control changes
