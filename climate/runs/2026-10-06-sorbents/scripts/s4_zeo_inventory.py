import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import pickle, re, collections, math, os, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
D=pickle.load(open(os.path.join(HERE,'..','co2_h2o_isotherms.pkl'),'rb')); ISO,ADS,BIB=D['isotherms'],D['adsorbents'],D['bib']
V_STP=22.414
def to_molkg(q,u,M=44.0095):
    return {'mmol/g':q,'mol/kg':q,'cm3(STP)/g':q/V_STP,'ml(STP)/g':q/V_STP,'ml/g':q/V_STP,'mg/g':q/M,'g/g':q*1000/M,'wt%':q*10/M,'mol/g':q*1000,'mmol/kg':q/1000}.get(u)
ZEO=re.compile(r'(zeolit|13x|\bnax\b|\bna-x\b|\blix\b|\bkx\b|\bcax\b|5a\b|4a\b|\blta\b|\bfau\b|\bcha\b|chabaz|ssz-13|\bmor\b|mordenit|zsm|\bkfi\b|\brho\b|\bmer\b|\bgis\b|zk-5|clinoptil|\bnay\b|faujas|silicalite|\bbea\b|ferrierit|\bfer\b|heulandit|\bafx\b|\bsapo|\balpo)', re.I)
S=collections.defaultdict(list)
for k in ISO:
    if k['gas']!='CO2' or not isinstance(k['T'],(int,float)): continue
    if k['category'] in ('sim','mod','qua'): continue
    if k['file'] and k['file'].endswith('Desorption'): continue
    nm=k['name'] or ''
    if not ZEO.search(nm): continue
    if to_molkg(1.0,k['q_units']) is None or k['p_units'] not in ('bar',): continue
    pts=[(p*1e5,to_molkg(q,k['q_units'])) for p,q in k['pts'] if p>0 and q>0]
    if len(pts)<4: continue
    S[(k['doi'],k['hashkey'],nm)].append((k['T'],pts))
print('zeolite (doi,adsorbent) sets:',len(S))
units=collections.Counter(k['p_units'] for k in ISO if k['gas']=='CO2'); print('p units',units.most_common(6))
good=[]
for key,L in S.items():
    Ts=sorted(set(round(T) for T,_ in L))
    lowp=[T for T,pts in L if sum(p<=2000 for p,_ in pts)>=2]
    if len(Ts)>=3 and len(set(round(t) for t in lowp))>=3:
        good.append((key,Ts,len(L)))
print('sets with >=3 temperatures each having >=2 points at <=2 kPa:',len(good))
for (doi,h,nm),Ts,n in sorted(good,key=lambda x:min(x[1])):
    print(f"  {nm[:40]:<40} T {Ts}  doi {doi}")
