"""Dossier checks for coalition_4 (patched): Phase-1 feasibility vs roadmaps, non-ETS pro-rata cost,
pass-through at base cost, Brevik capex anchor, storage build-out. Tags: [SRC] read this session,
[MOD] modelled literature, [MEM] memory, [ASSUME] assumption."""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

def crf(r, n): return r*(1+r)**n/((1+r)**n-1)
pf = 0.65*44.01/56.08 + 0.015*44.01/40.30          # t CO2/t clinker (same as run scripts)
fuel = 3.4*0.095                                    # t CO2/t clinker [ASSUME, as critic]
share = pf/(pf+fuel)
base_int = pf*0.71                                  # t process CO2/t binder at CR 0.71
print(f"process factor {pf:.3f}; fuel {fuel:.3f}; process share {share:.3f}; baseline {base_int:.3f} t/t binder")

print("\n1. PHASE 1 (-25% per t binder by 2035): substitution needed vs published trajectories")
cr_need = 0.71*0.75
print(f"  CR needed for -25% from 0.71: {cr_need:.3f}")
traj = {"IEA NZE 2035 (0.71->0.61) [SRC via run]": (0.71, 0.61),
        "GCCA 2030 (0.63->0.58) [SRC]": (0.63, 0.58),
        "GCCA 2050 (0.63->0.52) [SRC]": (0.63, 0.52)}
for k, (a, b) in traj.items():
    print(f"  {k}: cut {1-b/a:.1%} per t binder")
# gap at IEA NZE 2035 clinker ratio, met by storage
gap = (0.61 - cr_need)*pf                           # t process CO2/t binder still to store
frac = gap/(0.61*pf)
print(f"  At CR 0.61 in 2035, residual to store: {gap:.4f} t/t binder = {frac:.1%} of remaining process CO2")
for name, cem in (("EU+UK+NO+CH 0.19 Gt [MEM]", 0.19), ("base club 0.39 Gt [MEM]", 0.39), ("global 4.14 Gt (IEA 2035)", 4.14)):
    stored = cem*gap*1e3                            # Mt/yr process credited
    captured = stored/share                         # Mt/yr total kiln CO2 captured (post-combustion, pro-rata)
    print(f"  {name}: {stored:.1f} Mt/yr process credit -> {captured:.1f} Mt/yr captured -> "
          f"{captured/0.4:.0f} Brevik-size (0.4 Mt/yr) units by 2035")
print("  Phase 1 'substitution only' is consistent only with a cut of ~14% (IEA NZE CR 0.61) -> patch: Phase 1 = -15%")

print("\n2. NON-ETS JURISDICTION: cost per credited PROCESS tonne under pro-rata rule")
for lbl, c in (("claim low", 100), ("claim high", 150), ("OptiLex base avoided", 204), ("OptiLex high", 382)):
    print(f"  EUR{c}/t captured: EUR{c/share:.0f}/t process credited if fuel CO2 unpriced; "
          f"EUR{c - 0.38*0:.0f} if fuel share sells into an ETS at full value")

print("\n3. PHASE-2 PASS-THROUGH at CR 0.50 (store residual to reach 0.0374 t/t binder)")
stored = pf*0.50 - 0.1*base_int
for lbl, c in (("EUR100", 100), ("EUR150", 150), ("base EUR204", 204), ("high EUR382", 382)):
    ets = c*stored; non = ets/share
    line = f"  {lbl}: EUR{ets:.0f}/t binder (fuel CO2 priced) / EUR{non:.0f} (fuel unpriced)"
    for bc in (2000, 400):
        line += f"; build {bc}/m2: {ets*0.15/bc:.2%}-{non*0.30/bc:.2%}"
    print(line)

print("\n4. BREVIK CAPEX ANCHOR [SRC GCCSI profile May 2026: ~EUR421m, 400 kt/yr; Gassnova NOK1,150 ~EUR100/t]")
cap = 421e6/400e3
for r in (0.04, 0.08):
    print(f"  capex EUR{cap:.0f}/(t/yr): capital charge at {r:.0%}/25y, CF 0.9: EUR{cap*crf(r,25)/0.9:.0f}/t")
print("  -> Gassnova's ~EUR100/t full-cost figure needs a low public discount rate; at 8% capital alone is ~EUR110/t")

print("\n5. STORAGE BUILD-OUT for Phase 2 (club stored process CO2 2050)")
for name, cem in (("EU+UK+NO+CH", 0.19), ("base club", 0.39)):
    st = cem*(pf*0.52 - 0.1*base_int)*1e3          # Mt/yr process stored at CR 0.52
    sub = cem*pf*(0.71-0.52)*1e3
    print(f"  {name}: stored {st:.0f} Mt/yr process (+ substitution {sub:.0f}) -> total {st+sub:.0f} Mt/yr; "
          f"captured incl. fuel share {st/share:.0f} Mt/yr = {st/share/5:.0f} x Northern Lights Phase 2 (5 Mt/yr) [SRC]")

print("\n6. FILLER GAMING: per-binder metric vs per-m3 concrete")
for extra_binder in (0.0, 0.05, 0.10):
    # move CR 0.71->0.61 via filler; if binder per m3 must rise by extra_binder for same strength
    metric_cut = 1-0.61/0.71
    real_cut = 1-(0.61*(1+extra_binder))/0.71
    print(f"  CR 0.71->0.61, binder/m3 +{extra_binder:.0%} [ASSUME]: metric shows -{metric_cut:.1%}, per-m3 concrete -{real_cut:.1%}")
