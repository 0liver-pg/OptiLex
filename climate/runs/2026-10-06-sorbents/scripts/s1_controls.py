import json, re, collections, numpy as np, os
HERE=os.path.dirname(os.path.abspath(__file__)); EV=96.485
N={'CO2':1,'H2O':1,'CO2_H2O':2,'CO2_2H2O':3}
E=collections.defaultdict(lambda: collections.defaultdict(list))
for line in open(os.path.join(HERE,'adsorption_energy.txt')):
    n,e=line.split(); e=float(e)
    m=re.match(r'(.+)_w_(CO2_2H2O|CO2_H2O|CO2|H2O)(_random)?_(\d+|new)$',n)
    if not m: continue
    h,a,r,_=m.groups()
    if abs(e/N[a])>2: continue
    E[h][a].append((e*EV, bool(r)))
def row(h):
    d=E.get(h)
    if not d or not d['CO2'] or not d['H2O'] or not d['CO2_H2O']: return None
    c=min(x for x,_ in d['CO2']); w=min(x for x,_ in d['H2O']); cw=min(x for x,_ in d['CO2_H2O'])
    return c,w,cw,cw-w,cw-c-w,len(d['H2O']),len(d['CO2_H2O'])
CTRL={'Mg-MOF-74':['VOGTIV_clean_h'],'Ni-MOF-74':['ORIVUI'],'Co-MOF-74':['ORIWAP'],'Mn-MOF-74':['ORIWET'],'Zn-MOF-74':['FIJDOS','WOBHEB','WOBHEB01'],
      'HKUST-1':['FIQCEN','XAMDUM','XAMDUM02','XAMDUM04','XAMDUM05','XAMDUM06','XAMDUM07'],'UiO-66':['RUBTAK01_SL','RUBTAK02_SL','RUBTAK03_auto'],'SIFSIX-3-Zn':['FUDQIF']}
print(f"{'material':<12}{'host':<16}{'E_CO2':>8}{'E_H2O':>8}{'E_CO2+H2O':>11}{'CO2|H2O':>9}{'coop':>8}  nH2O nCO2H2O")
for k,hs in CTRL.items():
    for h in hs:
        r=row(h)
        if r: print(f"{k:<12}{h:<16}{r[0]:8.1f}{r[1]:8.1f}{r[2]:11.1f}{r[3]:9.1f}{r[4]:8.1f}  {r[5]:>4} {r[6]:>6}")
        else: print(f"{k:<12}{h:<16} missing")
# sampling-artifact test: does the 'water-assisted' signal persist if CO2+H2O minimum must be no lower than (min CO2 + min H2O) - gas-dimer? i.e. how many hosts have min E(CO2+H2O) found in a placement where H2O-alone sampling missed the water site?
# proxy: hosts where min E(H2O) differs strongly between non-random and random placement sets (poor water sampling)
res=json.load(open(os.path.join(HERE,'s1_results.json')))
def wsamp(h):
    d=E[h]; a=[x for x,r in d['H2O'] if not r]; b=[x for x,r in d['H2O'] if r]
    return (min(a)-min(b)) if a and b else None
for key in ('as113','as165'):
    sp=[wsamp(r['host']) for r in res[key]]
    sp=[abs(x) for x in sp if x is not None]
    print(key, 'n',len(res[key]),'| |minH2O(heuristic)-minH2O(random)| median %.1f kJ/mol, >10: %d of %d'%(np.median(sp),sum(x>10 for x in sp),len(sp)))
# overall: E_CO2|H2O vs dry E_CO2 shift distribution for hosts with strong water (E_H2O<=-45)
pr=[r for r in res['pr'] if r['E_H2O']<=-45]
sh=np.array([r['cond']-r['E_CO2'] for r in pr])
print('hosts with water present at 50%%RH: %d; shift E_CO2|H2O - E_CO2 (kJ/mol): median %+.1f, 25th %+.1f, 75th %+.1f; stronger by >10: %d (%.0f%%); weaker by >10: %d (%.0f%%)'%(
  len(pr),np.median(sh),np.percentile(sh,25),np.percentile(sh,75),(sh<-10).sum(),100*(sh<-10).mean(),(sh>10).sum(),100*(sh>10).mean()))
