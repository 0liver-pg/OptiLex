import sys; sys.path.insert(0,'climate')
GWP=27
# absolute per-animal reduction: CH4 50-70 kg/yr; absolute cut range
# low: intensity cut 15% but milk +14% => absolute = 1-(0.85*1.14)= 3%; high: 20% cut, milk +2% => 18.4%
for ch4 in (50,70):
    for cut,dm in ((0.15,0.14),(0.20,0.02),(0.175,0.08)):
        absr=1-(1-cut)*(1+dm)
        print(ch4,cut,dm,'abs frac %.3f'%absr,'tCO2e %.3f'%(ch4*absr*GWP/1000))
lo=50*(1-0.85*1.14)*GWP/1000; hi=70*(1-0.80*1.02)*GWP/1000; mid=60*(1-0.825*1.08)*GWP/1000
print('range t/animal-yr',round(lo,3),round(hi,3),'mid',round(mid,3))
print('scale Mt: 10M lo',10e6*lo/1e6,'30M hi',30e6*hi/1e6,'10M mid',10e6*mid/1e6,'30M mid',30e6*mid/1e6)
# MRV weekly sealed sample
for c in (0.5,1.5):
    for n in (200,500):
        print('MRV $/animal-yr',c,n,round(52*c/n,3))
# pooled signal at 60% enrolment
for e in (0.6,):
    print('pooled', e*0.15, e*0.20)
# carbon value
for p in (15,30): print('value',p, round(lo*p,2), round(hi*p,2))
