"""Verifier for graft_subsurface_2_patched: Class VI storage sited/phased around Smackover Li/Br brine units.
Run: cd OptiLex && .venv/bin/python <this file>
Labels: [src] sourced this session or in prior OptiLex scripts, [recall] pre-cutoff knowledge not re-verified,
[assume] my assumption, [calc] derived. Subsurface parameters are literature-range assumptions, NOT site data."""
import sys, math
import numpy as np
from scipy.special import exp1
sys.path.insert(0, 'climate')
sys.path.insert(0, 'climate/runs/2026-10-05/scripts')
from physics import *  # noqa
from co2_brine import co2_density, CP

YR = 3.156e7
LCE_PER_LI = 5.323
def hdr(s): print('\n' + '=' * 100 + '\n' + s + '\n' + '=' * 100)
def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)
CRF = crf(0.08, 20)
RHO = co2_density(115, 280)          # [calc] CoolProp Span-Wagner, [assume] 115 C / 280 bar (~2.7 km Smackover)
VT = 1000 / RHO                      # m3 per t CO2
MU_CO2 = CP.PropsSI('V', 'T', 388.15, 'P', 280e5, 'CO2')

# ---------------------------------------------------------------------------------------------- 1
hdr('1. Thermodynamic floors')
for name, x, f, p in [('Gas-processing acid gas, 95% CO2', 0.95, 0.90, 0.999),
                      ('Ammonia / SMR process CO2, 98%', 0.98, 0.90, 0.999),
                      ('Coal flue, 12% (comparison)', 0.12, 0.90, 0.99),
                      ('Air 420 ppm, 75% (comparison)', 420e-6, 0.75, 0.99)]:
    g = gj_per_tonne(min_separation_work(x, f, p))
    print(f'  {name:<36} separation floor {g:.4f} GJ/t ({g/0.0036:.1f} kWh/t)')
comp_floor = R * T0 * math.log(150 / 1.0) / M_CO2 / 1e6
print(f'  Ideal isothermal compression 1->150 bar: {comp_floor:.3f} GJ/t ({comp_floor/0.0036:.0f} kWh/t)')
print(f'  CO2 at 115 C / 280 bar: {RHO:.0f} kg/m3, {VT:.3f} m3/t, viscosity {MU_CO2*1e3:.4f} cP')
print('  CLAIM CHECK: separation floor 0.002-0.007 GJ/t and compression floor ~0.28 GJ/t -> consistent.')

# ---------------------------------------------------------------------------------------------- 2
hdr('2. Reproduce the card: plume stand-off, pressure reach, Phase-2 stranding')
for Q in (0.5, 1.0):
    for h, phi, Sg, ovr in [(30, 0.15, 0.5, 1.0), (30, 0.15, 0.3, 2.0), (60, 0.2, 0.4, 1.5)]:
        r = [math.sqrt(Q * 1e9 / 580 * t / (math.pi * h * phi * Sg)) * ovr / 1e3 for t in (10, 25)]
        print(f'  Q {Q} Mt/yr h {h} phi {phi} Sg {Sg} override x{ovr}: plume edge {r[0]:.1f} km (10 y), {r[1]:.1f} km (25 y)'
              f'{"   <-- 7 km stand-off leaves %.1f km < 2 km margin" % (7 - r[1]) if 7 - r[1] < 2 else ""}')
# high-permeability streak (thief zone) case: a share of injection channelled into a thin grainstone layer
for share, hs, phis, Sgs in [(0.5, 8, 0.20, 0.4), (0.7, 5, 0.22, 0.4)]:
    for Q in (0.5, 1.0):
        r = math.sqrt(share * Q * 1e9 / RHO * 25 / (math.pi * hs * phis * Sgs)) / 1e3
        print(f'  THIEF-ZONE case: {share:.0%} of {Q} Mt/yr into {hs} m streak (phi {phis}, Sg {Sgs}): {r:.1f} km at 25 y')
for k_md, phi, mu, ct in [(50, 0.15, 4e-4, 1.5e-9), (100, 0.15, 4e-4, 1e-9), (300, 0.2, 4e-4, 1e-9)]:
    D = k_md * 9.87e-16 / (phi * mu * ct)
    print(f'  k {k_md} mD: diffusivity {D:.2f} m2/s, sqrt(4Dt) 1 y {math.sqrt(4*D*YR)/1e3:.1f} km, 25 y {math.sqrt(4*D*25*YR)/1e3:.0f} km')
print('  Phase-2 stranding (card: 30% of original grade, 0.57-1.41 m3 stranded brine per t, 80% recovery):')
cutoff = 150
for g in (150, 300, 400):
    for sv in (0.57, 1.41):
        usd = sv * g * 0.3 / 1e3 * 0.8 * LCE_PER_LI * 9
        print(f'    orig {g} mg/L -> flushed {g*0.3:.0f} mg/L ({"BELOW" if g*0.3 < cutoff else "above"} {cutoff} mg/L cut-off): '
              f'{sv} m3/t -> ${usd:.2f}/t undiscounted at $9k/t LCE, ${usd*20/9:.2f}/t at $20k/t')
print('  TIMING CHECK: the card multiplies Phase-2 stranding by PV factors 0.15-0.32 (yr 15-25 from today). But the')
print('  CO2 tonnes (and their storage revenue) occur at the SAME future date, so like-for-like the discount applies only')
print('  to the gap between storage and the date the lithium would otherwise have been produced:')
for gap in (0, 5, 10):
    pv = 1 / 1.08 ** gap
    print(f'    gap {gap:>2} y: PV factor {pv:.2f} -> 400 mg/L case ${6.49*pv:.2f}/t, 150 mg/L case ${2.43*pv:.2f}/t')
print('  BUT: flushed grade 45-120 mg/L is below the card\'s own ~150 mg/L cut-off, so the stranded lithium has ~zero')
print('  economic value at today\'s prices; Phase-2 stranding passes for that reason, not because of discounting.')

# ---------------------------------------------------------------------------------------------- 3
hdr('3. Pressure (Theis line source, infinite-acting, single-phase brine-equivalent): what DLE producers see')
mu_b, ct = 0.45e-3, 1.0e-9    # [assume] brine 0.45 cP at 115 C; total compressibility 1e-9 /Pa
def dP_bar(Q_mt, r_m, t_yr, k_md, h, phi):
    q = Q_mt * 1e9 / RHO / YR                 # reservoir m3/s
    k = k_md * 9.87e-16
    D = k / (phi * mu_b * ct)
    return q * mu_b / (4 * math.pi * k * h) * exp1(r_m ** 2 / (4 * D * t_yr * YR)) / 1e5
for k_md, h, phi in [(50, 30, 0.15), (100, 40, 0.17), (300, 60, 0.20)]:
    out = [f'{dP_bar(Q, r, t, k_md, h, phi):5.1f}' for Q in (0.5, 1.0) for r, t in [(7000, 10), (7000, 25)]]
    print(f'  k {k_md:>3} mD h {h} m: dP at a producer 7 km away [0.5 Mt/yr 10y, 25y | 1 Mt/yr 10y, 25y] = '
          f'{out[0]}, {out[1]} | {out[2]}, {out[3]} bar')
# hub limit: dP at 5 km from hub centre after 25 y must stay below an allowance
depth = 2700.0
p_hyd = 1150 * 9.81 * depth / 1e5      # [assume] brine 1,150 kg/m3
p_frac = 15.8e3 * depth / 1e5         # [assume] ~0.7 psi/ft fracture gradient
margin = 0.9 * p_frac - p_hyd
print(f'  Depth {depth:.0f} m: hydrostatic {p_hyd:.0f} bar, 90% frac {0.9*p_frac:.0f} bar -> regional margin {margin:.0f} bar')
print('  Max hub rate so that dP(5 km, 25 y) <= 40 bar (half the margin; rest for well-skin and interference):')
hub_caps = {}
for k_md, h, phi in [(50, 30, 0.15), (100, 40, 0.17), (300, 60, 0.20)]:
    unit = dP_bar(1.0, 5000, 25, k_md, h, phi)
    cap = 40 / unit
    hub_caps[k_md] = cap
    D = k_md * 9.87e-16 / (phi * mu_b * ct)
    print(f'    k {k_md:>3} mD h {h} m: {unit:.1f} bar per Mt/yr -> hub cap {cap:.1f} Mt/yr; hubs for 25 Mt/yr '
          f'{25/cap:.0f}; pressure reach sqrt(4Dt) 25 y {math.sqrt(4*D*25*YR)/1e3:.0f} km -> spacing ~2x that to avoid interference')
print('  -> 25 Mt/yr into the Smackover is pressure-limited (needs many widely spaced hubs or brine extraction),')
print('     independent of DLE flushing. Compartmentalised (fault-bounded) blocks would be worse than infinite-acting.')
print('     Because DLE produce/reinject is volume-balanced, the DLE unit gives no net pressure relief (card agrees).')

# ---------------------------------------------------------------------------------------------- 4
hdr('4. Long-term buoyant up-dip migration toward the brine unit (down-dip siting)')
for k_md in (50, 100, 300):
    for s in (0.01, 0.03):
        v = k_md * 9.87e-16 * 0.3 * (1150 - RHO) * 9.81 * s / (MU_CO2 * 0.17)
        print(f'  k {k_md:>3} mD, dip sin {s}: {v*YR:.0f} m/yr (free-phase, krCO2 0.3, no trapping) -> {v*YR*50/1e3:.1f} km in 50 y, '
              f'{v*YR*300/1e3:.0f} km in 300 y')
print('  -> Down-dip siting puts the brine unit (and Smackover structural oil traps) UP-dip of the plume: buoyant CO2')
print('     drifts toward them over decades-centuries (residual/dissolution trapping slows this). Class VI AoR and PISC')
print('     must cover it; during the 25 y injection window the drift (<2 km) is small vs the 7 km stand-off.')

# ---------------------------------------------------------------------------------------------- 5
hdr('5. Phase-2 capacity: how fast do flushed patterns become available?')
for lce, g in [(22500, 437), (25000, 300)]:
    brine = lce / LCE_PER_LI * 1e3 / (g / 1e3 * 0.8)       # [calc] t Li*1e3 kg / (kg Li per m3 * rec)
    for h, phi, sweep, E in [(40, 0.17, 0.5, 0.03), (60, 0.20, 0.6, 0.05)]:
        pv_km2 = 1e6 * h * phi
        flushed_km2 = brine / (pv_km2 * sweep * 1.0)      # ~1 swept pore volume to reach <=30% grade [assume]
        cap = flushed_km2 * pv_km2 * E * RHO / 1e3 / 1e6  # Mt per year of new capacity
        print(f'  {lce/1e3:.1f} kt/yr LCE plant at {g} mg/L: brine {brine/1e6:.1f} Mm3/yr; h {h} phi {phi} sweep {sweep}: '
              f'{flushed_km2:.1f} km2/yr flushed -> new Phase-2 capacity {cap:.2f} Mt/yr (storage efficiency {E:.0%})')
print('  -> Phase 2 adds well under 1 Mt/yr of capacity per DLE plant, decades from now; the 25 Mt/yr target is ~all')
print('     Phase-1 plain Class VI storage outside the units.')

# ---------------------------------------------------------------------------------------------- 6
hdr('6. Energy per tonne stored (GJ/t)')
energy = {}
for lab, comp_kwh, dehy, km, boost_kwh_100km in [('low', 95, 0.005, 50, 2), ('base', 115, 0.01, 150, 3),
                                                  ('high', 140, 0.02, 400, 5)]:
    # [recall] 90-130 kWh/t to ~150 bar for near-atmospheric high-purity CO2 (NETL/IEAGHG ranges); booster [assume]
    tot = comp_kwh * 0.0036 + dehy + km / 100 * boost_kwh_100km * 0.0036
    energy[lab] = tot
    print(f'  {lab:>4}: compression {comp_kwh} kWh/t + dehydration {dehy} GJ/t + {km} km pipeline boosting -> {tot:.3f} GJ/t '
          f'({tot/0.0036:.0f} kWh/t); {tot/comp_floor:.2f}x the isothermal compression floor')

# ---------------------------------------------------------------------------------------------- 7
hdr(f'7. Cost per tonne, plain Class VI vs coupled (2025$, CRF 8%/20 y = {CRF:.4f})')
C = {
 'low':  dict(kwh=95,  elec=45, ckw=1500, km=50,  ukm=1.0e6, pmt=5,   wpm=1, wcost=10e6, mrv=3,  char=15e6, site_mt=30,
              legacy_n=20,  legacy_c=75e3,  pore=0.5, permit_fr=1.0, mtpy=2.0, dehy=1),
 'base': dict(kwh=115, elec=65, ckw=2500, km=150, ukm=1.5e6, pmt=3,   wpm=2, wcost=15e6, mrv=5,  char=30e6, site_mt=20,
              legacy_n=100, legacy_c=150e3, pore=1.5, permit_fr=2.0, mtpy=1.0, dehy=2),
 'high': dict(kwh=140, elec=90, ckw=3500, km=400, ukm=2.5e6, pmt=1.5, wpm=3, wcost=25e6, mrv=10, char=60e6, site_mt=15,
              legacy_n=400, legacy_c=300e3, pore=3.0, permit_fr=4.0, mtpy=0.75, dehy=3),
}
# Assumption notes [assume/recall]: Gulf Coast industrial power $45-90/MWh; compressor $1.5-3.5k/kW; onshore pipeline
# $1-2.5M/km; Smackover trend is ~150-400 km from the Mississippi River industrial corridor (low case = local N-LA/S-AR/
# E-TX sources e.g. Haynesville gas treating); injector $10-25M; MRV $3-10/t; greenfield characterisation (strat well,
# 3D seismic, core, modelling) $15-60M per site; legacy wells in AoR 20-400 at $75-300k re-plug (south Arkansas is a
# 1920s-era oil province); pore-space lease $0.5-3/t; permitting, financial responsibility, 50-y PISC $1-4/t.
plain = {}
for lab, p in C.items():
    mw = 1e6 * p['kwh'] / 1e3 / 8000
    comp = mw * 1e3 * p['ckw'] * (CRF + 0.04) / 1e6 + p['kwh'] / 1e3 * p['elec']
    boost = energy[lab] * 0 + p['km'] / 100 * {'low': 2, 'base': 3, 'high': 5}[lab] / 1e3 * p['elec']
    pipe = p['km'] * p['ukm'] * (CRF + 0.025) / (p['pmt'] * 1e6)
    wells = p['wpm'] * p['wcost'] * (CRF + 0.05) / 1e6
    inj_years = p['site_mt'] / p['mtpy']
    char = p['char'] * crf(0.08, inj_years) / (p['mtpy'] * 1e6)
    legacy = p['legacy_n'] * p['legacy_c'] * crf(0.08, inj_years) / (p['mtpy'] * 1e6)
    items = dict(compression=comp, boosting=boost, dehydration=p['dehy'], pipeline=pipe, injectors=wells, MRV=p['mrv'],
                 characterisation=char, AoR_corrective=legacy, pore_lease=p['pore'], permit_FR_PISC=p['permit_fr'])
    tot = sum(items.values()); plain[lab] = tot
    print(f'  {lab:>4} (site {p["site_mt"]} Mt at {p["mtpy"]} Mt/yr): ' + ', '.join(f'{k} {v:.1f}' for k, v in items.items())
          + f'  => TOTAL ${tot:.1f}/t')
q45 = 85   # [recall] 45Q $85/t geological storage (prevailing wage), retained by July 2025 OBBBA; 12-y credit period;
#            construction must begin before 1 Jan 2033 [recall]
for lab in plain:
    print(f'  {lab}: margin vs 45Q $85/t during the 12-y credit window: ${q45 - plain[lab]:.0f}/t; after year 12: '
          f'${-plain[lab]:.0f}/t unless another carbon price exists')
print('  POLICY CHECK: Phase 1 (2028-2035) straddles the 45Q construction-start deadline (1 Jan 2033, [recall]);')
print('  Phase 2 (~2045-2055, see section 5) has NO 45Q under current law: it needs a successor carbon price.')

# ---------------------------------------------------------------------------------------------- 8
hdr('8. The coupling: avoided Class VI cost from the brine unit (Phase-1 geometry: plume OUTSIDE the unit)')
print('  Structural point: in Phase 1 the plume is, by the card\'s own rule, outside/down-dip of the unit, so the unit\'s')
print('  pore-space aggregation does not cover the plume. What transfers: data near the unit, the legacy-well INVENTORY')
print('  (not the re-plugging cost), and DLE wells usable as in-zone pressure monitors inside the pressure-front AoR.')
rng = np.random.default_rng(7)
N = 200_000
tri = lambda a, b, c: rng.triangular(a, b, c, N)
char = tri(15e6, 30e6, 60e6); char_share = tri(0.05, 0.25, 0.5)          # [assume] share of characterisation avoided
mon_wells = tri(0, 1, 2) * tri(3e6, 5e6, 8e6)                              # [assume] monitoring wells avoided
inventory = tri(0.2e6, 0.5e6, 1.5e6)                                       # [assume] legacy-well survey avoided
agg_txn = tri(2e6, 5e6, 10e6) * tri(0.0, 0.1, 0.3)                         # [assume] aggregation transaction cost x overlap
site_mt = tri(15, 20, 30)
avoided_undisc = (char * char_share + mon_wells + inventory + agg_txn) / (site_mt * 1e6)
# discounted-equivalent: spread over injection years at 1 Mt/yr; capex at t0 vs discounted tonnes
yrs = site_mt / 1.0
disc_t = (1 - 1.08 ** -yrs) / 0.08 * 1e6
avoided_disc = (char * char_share + mon_wells + inventory + agg_txn) / disc_t
# delay avoided (legal premium): if coupling shortens permitting by d years, margin m arrives earlier
d = tri(0.0, 0.5, 2.0); m = tri(20, 42, 60)
delay_val = m * (1 - 1.08 ** -d)
for name, arr in [('avoided cost, undiscounted $/t', avoided_undisc), ('avoided cost, per discounted t', avoided_disc),
                  ('delay value $/t-equivalent', delay_val), ('TOTAL (disc. avoided + delay)', avoided_disc + delay_val)]:
    p5, p50, p95 = np.percentile(arr, [5, 50, 95])
    print(f'  {name:<34} P5 {p5:.2f}  P50 {p50:.2f}  P95 {p95:.2f}   P(>$5/t) {np.mean(arr > 5):.0%}')
print('  Card claim: "$1-4/t undiscounted, likely below the $5/t kill threshold" -> my undiscounted P50 is lower')
print('  (only part of characterisation transfers when the plume is outside the unit). Only a >1 y permitting')
print('  acceleration lifts it over $5/t; Arkansas lacks Class VI primacy (EPA list, fetched 2026-10-05: AZ, LA, ND,')
print('  TX, WV, WY), so Arkansas sites are permitted by EPA Region 6 regardless of the brine unit.')
for lab, avd in [('low', 4.0), ('base', float(np.percentile(avoided_disc + delay_val, 50))), ('high', 0.0)]:
    print(f'  coupled cost {lab}: plain ${plain[lab]:.1f} - coupling ${avd:.1f} = ${plain[lab]-avd:.1f}/t')
# licence revenue vs DLE plant revenue
for avd in (1.0, 2.5, 5.0):
    for mt in (1.0, 2.0):
        lic = avd * mt * 1e6
        rev = 25000 * 9000
        print(f'  licence ${avd}/t x {mt} Mt/yr = ${lic/1e6:.1f}M/yr vs 25 kt/yr LCE plant revenue ${rev/1e6:.0f}M/yr '
              f'at $9k/t -> {lic/rev:.1%}')

# ---------------------------------------------------------------------------------------------- 9
hdr('9. Scale and resources')
for gt in (0.003, 0.01, 0.025):
    s = ScaleCheck(gt, energy['base'])
    E = 0.02
    area = gt * 1e9 * 25 / (RHO / 1e3 * 40 * 0.17 * E) / 1e6   # t / (t/m3) -> m3 -> km2
    print(f'  {gt*1e3:.0f} Mt/yr: {s.ej_per_year*1e3:.1f} PJ/yr = {s.share_of_world_primary_energy:.5%} of world primary, '
          f'{s.share_of_world_electricity_if_electric:.4%} of world electricity; injectors at 0.5-1 Mt/yr: '
          f'{gt*1e3/1:.0f}-{gt*1e3/0.5:.0f}; 25-y plume footprint at 2% storage efficiency ~{area:,.0f} km2')
print(f'  25 Mt/yr = {0.025/FOSSIL_CO2_GT:.3%} of fossil CO2 ({FOSSIL_CO2_GT} Gt) and {0.025/TOTAL_GHG_GT_CO2E:.3%} of total GHG.')
print('  Water: none consumed. Land: pads + pipeline ROW. Materials: steel for 150-400 km pipeline and wells.')
print('  Global analogues of the coupling (DLE unit over a saline storage formation): Smackover, Alberta Leduc, a few')
print('  others -> the concept caps well below 0.1 Gt/yr; the CO2 storage itself is generic point-source Class VI.')
