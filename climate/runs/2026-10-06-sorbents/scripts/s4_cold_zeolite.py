"""Screen 4 pilot: is cold-loaded commodity zeolite regenerable at <=100 C? Dual-site Langmuir (DSL) fits to measured
multi-temperature CO2 isotherms (ISODB; J. Chem. Eng. Data 2009 set, 228-448 K, dry pure CO2) vs the verifier's single site.
Cycle rule (fixed before results): adsorb at 253 K (-20 C) or 298 K from 42.56 Pa CO2 (dry); desorb at T_des under 1 kPa or 0.1 kPa CO2.
Heat per mol = loading-weighted site enthalpy + sensible (cp 900 J/kg/K zeolite, no inert, no recovery) + water term (from desiccant guard: see text)."""
import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import pickle, re, collections, math, os, numpy as np
from scipy.optimize import least_squares
HERE=os.path.dirname(os.path.abspath(__file__))
D=pickle.load(open(os.path.join(HERE,'..','co2_h2o_isotherms.pkl'),'rb')); ISO=D['isotherms']
V_STP=22.414
def to_molkg(q,u,M=44.0095):
    return {'mmol/g':q,'mol/kg':q,'cm3(STP)/g':q/V_STP,'ml(STP)/g':q/V_STP,'mg/g':q/M,'g/g':q*1000/M,'wt%':q*10/M}.get(u)
def get(doi,name):
    out=[]
    for k in ISO:
        if k['gas']=='CO2' and k['doi'].lower()==doi.lower() and k['name']==name and isinstance(k['T'],(int,float)) and not (k['file'] or '').endswith('Desorption'):
            pts=[(p*1e5,to_molkg(q,k['q_units'])) for p,q in k['pts'] if p>0 and q>0]
            out.append((float(k['T']),np.array(pts)))
    return out
def dsl(p,T,th):
    q1,lb1,E1,q2,lb2,E2=th
    b1=math.exp(lb1)*np.exp(E1*1e3/(R*T)); b2=math.exp(lb2)*np.exp(E2*1e3/(R*T))
    return q1*b1*p/(1+b1*p)+q2*b2*p/(1+b2*p)
def fit(data, pmax=1e5, two=True):
    P=np.concatenate([d[:,0] for T,d in data if True]); 
    rows=[(p,q,T) for T,d in data for p,q in d if p<=pmax]
    p=np.array([r[0] for r in rows]); q=np.array([r[1] for r in rows]); T=np.array([r[2] for r in rows])
    if two:
        f=lambda th: (np.log(dsl(p,T,th)+1e-9)-np.log(q))
        best=None
        for E1 in (30,40,50):
            for E2 in (20,30):
                x0=[2.0,math.log(1e-12),E1,3.0,math.log(1e-10),E2]
                r=least_squares(f,x0,bounds=([0.01,-60,15,0.01,-60,5],[10,0,80,10,0,60]))
                if best is None or r.cost<best.cost: best=r
        return best.x, math.sqrt(2*best.cost/len(q)), len(q)
    else:
        f=lambda th: (np.log(dsl(p,T,[th[0],th[1],th[2],0,0,0])+1e-9)-np.log(q))
        r=least_squares(f,[4.0,math.log(1e-10),40],bounds=([0.01,-60,10],[15,0,80]))
        return [r.x[0],r.x[1],r.x[2],0,0,0], math.sqrt(2*r.cost/len(q)), len(q)
def site_load(p,T,th):
    q1,lb1,E1,q2,lb2,E2=th
    b1=math.exp(lb1)*math.exp(E1*1e3/(R*T)); b2=math.exp(lb2)*math.exp(E2*1e3/(R*T))
    return q1*b1*p/(1+b1*p), q2*b2*p/(1+b2*p)
def cycle(th,Ta,Td,pd,cp=900.0):
    a1,a2=site_load(P_CO2_AIR,Ta,th); d1,d2=site_load(pd,Td,th)
    wc=(a1+a2)-(d1+d2)
    if wc<=0: return wc,None,None
    rxn=((a1-d1)*th[2]+(a2-d2)*th[5])*1e3/wc
    sens=cp*(Td-Ta)/wc
    return wc,gj_per_tonne(rxn),gj_per_tonne(sens)
SETS=[('10.1021/Je800900a','Zeolite 13X'),('10.1021/Je800900a','Zeolite 5A')]
for doi,name in SETS:
    data=get(doi,name)
    Ts=sorted(T for T,_ in data)
    lowpts=sum(int((d[:,0]<=2000).sum()) for T,d in data)
    print(f"\n=== {name} ({doi}); temperatures {Ts}; points <=2 kPa: {lowpts}; p range {min(d[:,0].min() for T,d in data):.0f}-{max(d[:,0].max() for T,d in data):.0f} Pa")
    for lab,pmax in (('fit to p<=10 kPa',1e4),):
        th2,rm2,n2=fit(data,pmax,True); th1,rm1,n1=fit(data,pmax,False)
        print(f"  {lab}: DSL q1 {th2[0]:.2f} mol/kg E1 {th2[2]:.1f} kJ/mol | q2 {th2[3]:.2f} E2 {th2[5]:.1f} | rms log-err {rm2:.3f} (n={n2});  single site q {th1[0]:.2f} E {th1[2]:.1f} rms {rm1:.3f}")
        # check: measured points near 42.56 Pa
        for T,d in sorted(data,key=lambda x:x[0]):
            if T in (248.0,273.0,298.0) or abs(T-248)<1 or abs(T-273)<1 or abs(T-298)<1:
                lo=d[d[:,0]<=300]
                if len(lo): print(f"    T {T:.0f}: lowest measured points (Pa, mol/kg) {[(round(a),round(b,3)) for a,b in lo[:4]]}; DSL at 42.56 Pa {dsl(P_CO2_AIR,T,th2):.3f}, single {dsl(P_CO2_AIR,T,th1):.3f}")
        print(f"  {'cycle':<34}{'model':<8}{'wc mol/kg':>10}{'rxn GJ/t':>9}{'sens GJ/t':>10}{'dry heat':>9}")
        for Ta in (253.15,298.15):
            for Td,pd in ((333.15,1e3),(353.15,1e3),(373.15,1e3),(373.15,1e2),(473.15,1e3)):
                for mn,th in (('DSL',th2),('1-site',th1)):
                    wc,rx,se=cycle(th,Ta,Td,pd)
                    s=f"{wc:10.3f}"+(f"{rx:9.2f}{se:10.2f}{rx+se:9.2f}" if rx else "        -         -        -")
                    print(f"  ads {Ta-273.15:+4.0f} C -> {Td-273.15:3.0f} C/{pd:5.0f} Pa      {mn:<8}{s}")
    globals()['TH_'+name.split()[-1]]=th2
# verifier cross-check: single-site TVSACycle with matching parameters for 13X (dS from fitted b0) at -20 -> 100 C/100 Pa
th=TH_13X
