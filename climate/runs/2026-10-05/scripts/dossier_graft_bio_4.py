"""Dossier check for graft_bio_4 (patched): does reduced recovered capacity r also dilute
capex, O&M and energy per tonne? The patch model charges 1/r only on the sorbent line.
Labels: [verifier] physics.py; [graft] graft_bio_4.py inputs; [assume] judgement; [mem] unverified literature recall."""
import sys
sys.path.insert(0, 'climate')
from physics import *

floor = gj_per_tonne(min_separation_work(420e-6, 0.75, 0.99))
print(f"floor {floor:.3f} GJ/t [verifier]")

def crf(i, n): return i*(1+i)**n/((1+i)**n-1)
M = 0.04401
H_DES = 80e3/M/1e9   # GJ/t: PEI heat of adsorption ~70-90 kJ/mol [mem] -> ~1.8 GJ/t, fixed per tonne
# cases copied from graft_bio_4.py section 5 [graft]
cases = {
 "low":  dict(capex=500, i=.06, n=25, om=.03, heat=4.0, elec=1.0, ph=4.0,  pe=40,  sorb=69.2,  life=2.0, ts=10),
 "base": dict(capex=1500,i=.08, n=20, om=.04, heat=5.5, elec=1.5, ph=8.0,  pe=60,  sorb=290.5, life=1.5, ts=20),
 "high": dict(capex=3000,i=.10, n=15, om=.05, heat=8.0, elec=2.5, ph=15.0, pe=100, sorb=1037.9,life=1.0, ts=40),
}
a, o = 0.25, 0.12   # patched idea mid inputs [graft]
def costs(d, N, r, dilute=True, avg=True):
    cap = d["capex"]*crf(d["i"], d["n"]); om = d["capex"]*d["om"]
    heat_fix = min(H_DES, d["heat"]); heat_var = d["heat"]-heat_fix
    base = cap+om + d["heat"]*d["ph"] + d["elec"]/3.6*d["pe"] + d["sorb"] + d["ts"]
    if r is None: return base
    reff = (1+(N-1)*r)/N if avg else r          # first life fresh, N-1 reloaded lives at r
    f = a + (1-a)/N + o
    s = d["sorb"]*f/reff
    down = 2/(365*d["life"])                    # 2 days per reload [assume, as graft]
    k = 1/reff if dilute else 1.0
    tot = (cap+om)*k/(1-down) + heat_fix*d["ph"] + heat_var*d["ph"]*k + d["elec"]/3.6*d["pe"]*k + s + d["ts"]
    return base, tot
print("Total-cost saving vs no-reload (a=0.25, o=0.12). cols r=1.0/0.9/0.85/0.8/0.7")
for name, d in cases.items():
    for N in (3, 5):
        for dil, avg, lab in ((False, False, "patch model (sorbent-only 1/r)"),
                              (True,  False, "all costs dilute, every life at r"),
                              (True,  True,  "all costs dilute, first life fresh")):
            row = []
            for r in (1.0, .9, .85, .8, .7):
                b, t = costs(d, N, r, dil, avg); row.append(f"{100*(1-t/b):5.1f}")
            # breakeven r
            lo, hi = 0.05, 1.0
            for _ in range(60):
                mid = (lo+hi)/2; b, t = costs(d, N, mid, dil, avg)
                lo, hi = (lo, mid) if t < b else (mid, hi)
            print(f"  {name:4} N={N} {lab:38}: {row}  breakeven r={hi:.2f}  base ${b:.0f}/t")
# Li et al. 2026 measured ~10% capacity loss after one pyrolysis reuse (r~0.90): what is it worth?
for name, d in cases.items():
    b, t = costs(d, 5, 0.90, True, False)
    print(f"Li-2026-like r=0.90, N=5, all dilute, {name}: ${b:.0f} -> ${t:.0f}/t ({100*(1-t/b):.0f}%)")
# energy per tonne incl. dilution at r=0.85 (base), plus reload solvent 0.02-0.24 GJ/t [graft]
d = cases["base"]; reff = 0.85
e = min(H_DES, d["heat"]) + (d["heat"]-min(H_DES,d["heat"]))/reff + d["elec"]/reff
print(f"base energy at r=0.85: {e:.2f} GJ/t vs {d['heat']+d['elec']:.1f}; second-law eff {100*floor/e:.1f}% vs {100*floor/(d['heat']+d['elec']):.1f}%")
# Pilot-scale context: methanol/ethanol cycled per 1 Mt/yr plant at 4 kg solvent/kg sorbent
for q in (48.2, 120.5, 289.1):
    sorb_t = 1e9/q/1000  # t sorbent reloaded per yr per Mt CO2
    print(f"  {q:5.1f} kg/kg: {sorb_t/1e3:.1f} kt sorbent/yr reloaded per Mt CO2; solvent cycled {4*sorb_t/1e3:.0f} kt/yr")
