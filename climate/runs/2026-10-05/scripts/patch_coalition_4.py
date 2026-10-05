import sys
sys.path.insert(0,'climate')
from physics import *
pf=0.65*44/56+0.015*44/40.3
print("process factor t/t clinker",round(pf,3))
for cr in (0.71,0.60,0.50):
    print("CR",cr,"process t/t binder",round(pf*cr,3))
base=pf*0.71
print("CR .71->.50 cut %",round(100*(1-0.50/0.71),1))
print("CR needed for -30% w/o CCS",round(0.71*0.7,3))
# post-combustion allocation
fuel=3.4*0.095  # t CO2/t clinker
share=pf/(pf+fuel)
print("fuel CO2 t/t ck",round(fuel,3),"process share",round(share,3))
for cap in (0.5,0.6,0.9):
    tot=cap*(pf+fuel)
    naive=min(tot/pf,1.0)
    prorata=tot*share/pf
    print(f"flue cap {cap}: naive process claim {100*tot/pf:.0f}%  pro-rata {100*prorata:.0f}%")
# phase 2: -90% per binder at CR 0.50 -> stored fraction of remaining process CO2
target=0.1*base
rem=pf*0.50
print("phase2 target t/t binder",round(target,4),"process at CR.5",round(rem,3),"needed abatement of remaining %",round(100*(1-target/rem),1))
# global 2050: 4.0 Gt cement (hold), CR .52 
G=4.0
print("global process Gt at CR .71",round(G*base,2),"at .52",round(G*pf*0.52,2))
print("storage needed for -90% target at CR .52 Gt/yr",round(G*(pf*0.52-target),2))
# cost per t cement at CR.5 phase2 storing
for c in (100,150):
    print("cost €/t binder storing remaining at CR.5:",c,round(c*(pf*0.5-target)/share*share,1))
