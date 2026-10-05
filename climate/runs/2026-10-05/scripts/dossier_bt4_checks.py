"""Dossier checks for bottleneck_thermo_4 (patched hybrid). All modelled.
(1) store volume with saturated-liquid enthalpies (steam-table values, 105/150 C) and a 24 h store;
(2) HP COP for 110 C delivery (hybrid: HP feeds the plant directly; e-boiler charges the 150 C store);
(3) hybrid vs flat HP on 2025 day-ahead prices for DE-LU, DK1, FR (SMARD), same cost assumptions as
    critic_bt4_hybrid.py (German-style network/capacity charges = assumption, not French/Danish tariffs);
(4) hybrid electricity per gross t and net removal at FR grid intensity (RTE eco2mix taux_co2, direct
    production-based: 2024 mean 19.0 g/kWh, Jan-Aug 2026 mean 17.4 g/kWh; fetched 2026-10-05)."""
import sys, os, json, glob, datetime as dt
sys.path.insert(0, 'climate')
from physics import *
HERE = os.path.dirname(os.path.abspath(__file__)); SM = os.path.join(HERE, 'smard')
def load(prefix):
    s = {}
    for f in glob.glob(os.path.join(SM, f'{prefix}_*.json')):
        for t, v in json.load(open(f))['series']:
            if v is not None: s[t] = v
    return {t: v for t, v in s.items() if dt.datetime.fromtimestamp(t/1000, dt.timezone.utc).year == 2025}
EUR=1.13; Q=7.2; plant=100e3; CF=0.95; t_yr=plant*CF; AUX=0.65
D = plant*Q*1e9/3.1536e7/1e6
print(f'(1) avg heat demand {D:.1f} MW_th')
h105, h150, v150 = 440.2, 632.2, 0.001091   # kJ/kg, m3/kg (saturated liquid, steam tables)
for hrs_store in (16, 24):
    E = D*hrs_store*3.6e6  # kJ (MWh -> kJ)
    m = E/(h150-h105); V = m*v150
    print(f'    {hrs_store} h store: {D*hrs_store:.0f} MWh_th, {V:,.0f} m3 (150->105 C); '
          f'cost ${V*150/1e6:.1f}-{V*400/1e6:.1f}M = ${V*150/plant:.0f}-{V*400/plant:.0f} per t/yr')
# loaded-sorbent buffer for comparison (16 h)
co2_16 = plant/8760*16; mol = co2_16*1e6/44.01
for cap, price in ((1.5, 20), (1.0, 40)):
    sorb_t = mol/cap/1e3/1e3*1e3/1e3  # t sorbent: mol/(mmol/g) -> g ... convert
    sorb_t = mol/(cap*1e-3)/1e6
    print(f'    16 h loaded-sorbent buffer at {cap} mmol/g: {sorb_t:,.0f} t, ${sorb_t*1e3*price/1e6:.0f}M = ${sorb_t*1e3*price/plant:.0f} per t/yr')
for Tc in (283.15, 268.15, 323.15):
    for Th in (383.15, 423.15):
        print(f'(2) COP at 50% Carnot, source {Tc-273.15:.0f} C -> {Th-273.15:.0f} C: {0.5*Th/(Th-Tc):.2f}')
COP=1.8; HP_CAPEX=900; CRF=0.10; OM=0.02; GRIDF=15; CAPCHG=40
def run(p, thr, X, store_h=16, loss_day=0.01):
    hrs = sorted(p); N=len(hrs); cap=D*store_h; s=0; cost=0; ebm=0; ebp=0
    for t in hrs:
        need=D
        if p[t] < thr:
            eb=min(X*D, need+(cap-s)); take=min(eb,need); s+=(eb-take)*0.99; need-=take
            cost+=eb/0.99*p[t]; ebm+=eb/0.99
        else:
            d=min(s,need); s-=d; need-=d
        s*=(1-loss_day/24)
        if need>0: cost+=need/COP*(p[t]+GRIDF)
    sc=8760/N/t_yr
    V=cap*3.6e6/(h150-h105)*v150
    capex=(D*1e3*HP_CAPEX + X*D*1e3*100 + V*400)*(CRF+OM)/t_yr if X>0 else D*1e3*HP_CAPEX*(CRF+OM)/t_yr
    capc=D/COP*1e3*CAPCHG*EUR/t_yr
    return cost*sc*EUR+capex+capc, ebm/(D*N), ebm*sc
print('(3) heat cost $/t (flat HP vs hybrid 2xD e-boiler, 16 h store)')
for name, code in (('DE-LU','4169'),('DK1','252'),('FR','254')):
    p=load(code); flat,_,_=run(p,-1e9,0)
    neg=sum(1 for v in p.values() if v<0); low=sum(1 for v in p.values() if v<20)
    out=[f'{name}: n={len(p)}, hours<0: {neg}, hours<20: {low}; flat HP ${flat:.0f}']
    for thr in (0,10,20,30):
        tot,share,ebm=run(p,thr,2.0); out.append(f'thr{thr}: ${tot:.0f} (save {flat-tot:+.0f}, EB share {share:.0%})')
    tot24,_,_=run(p,20,2.0,store_h=24); out.append(f'thr20/24h store: ${tot24:.0f} (save {flat-tot24:+.0f})')
    print('    '+'; '.join(out))
    if name=='FR':
        _,share,ebm=run(p,20,2.0)
        e_heat = (1-share)*Q/COP/3.6 + ebm   # MWh_e per gross t: HP part + boiler part
        e_t = e_heat + AUX
        for ci in (0.017, 0.019, 0.030, 0.050):
            net=1-ci*e_t
            print(f'(4) FR hybrid thr20: {e_t:.2f} MWh_e/gross t; grid {ci} t/MWh -> net {net:.3f} t/t; $673 gross -> ${673/net:.0f}/net t')
