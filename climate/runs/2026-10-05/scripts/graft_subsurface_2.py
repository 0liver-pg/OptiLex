"""Verifier for graft_subsurface_2: CO2 replaces spent-brine reinjection in Smackover Li/Br brine fields.
Run: cd OptiLex && .venv/bin/python <this file>
Labels: [src] sourced, [recall] from pre-cutoff knowledge, not re-verified this session, [assume] my assumption, [calc] derived."""
import sys, math
sys.path.insert(0, 'climate')
sys.path.insert(0, 'climate/runs/2026-10-05/scripts')
from physics import *  # noqa
from co2_brine import kg_co2_per_m3_brine, co2_density, CP

BBL = 0.158987
YR = 3.156e7
LCE_PER_LI = 5.323
def hdr(s): print('\n' + '=' * 96 + '\n' + s + '\n' + '=' * 96)
def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)

# ------------------------------------------------------------------ 1. thermodynamic floors
hdr('1. Thermodynamic floors (verifier)')
floors = {}
for name, x in [('Gas-processing acid gas, 95% CO2', 0.95), ('Ammonia/SMR process CO2, 98%', 0.98),
                ('Coal-flue comparison, 12%', 0.12), ('Air comparison, 420 ppm', 420e-6)]:
    f, p = (0.75, 0.99) if x < 1e-3 else (0.90, 0.999 if x > 0.5 else 0.99)
    g = gj_per_tonne(min_separation_work(x, f, p)); floors[name] = g
    print(f'  {name:<38} separation floor {g:.4f} GJ/t ({g/0.0036:.1f} kWh/t)')
comp_floor = R * T0 * math.log(150 / 1.0) / M_CO2 / 1e6
print(f'  Ideal isothermal compression 1->150 bar: {comp_floor:.3f} GJ/t (ideal gas; not a separation floor, an '
      f'unavoidable transport/injection cost)')
print('  CLAIM CHECK: idea says separation floor 0.002-0.007 GJ/t for these sources -> consistent with above.')

# ------------------------------------------------------------------ 2. voidage per tonne and Li per tonne
hdr('2. Reservoir voidage per tonne CO2 (CoolProp Span-Wagner) and Li content of that voidage')
for T, P in [(100, 250), (115, 280), (130, 320)]:   # [assume] Smackover 2.3-3 km, hydrostatic brine gradient
    rho = co2_density(T, P)
    mu = CP.PropsSI('V', 'T', T + 273.15, 'P', P * 1e5, 'CO2')
    print(f'  {T} C, {P} bar: rho {rho:.0f} kg/m3, voidage {1000/rho:.3f} m3/t, CO2 viscosity {mu*1e3:.4f} cP')
rho = co2_density(115, 280); vt = 1000 / rho
mu_co2 = CP.PropsSI('V', 'T', 388.15, 'P', 280e5, 'CO2')
# [src] USGS MCS 2026: 2025 US contract battery-grade Li2CO3 avg $9,000/t; China spot ~$9,300 (Jan) -> $10,300 (Nov 2025)
for li in (150, 300, 400):   # [src] USGS Knierim 2024: >400 mg/L in S. Arkansas Smackover (claim; not re-fetched)
    kg_li = vt * li / 1000 * 0.8         # [assume] 80% DLE recovery
    lce = kg_li * LCE_PER_LI
    print(f'  Li {li} mg/L: {kg_li:.2f} kg Li = {lce:.2f} kg LCE per t CO2 -> ${lce*9:.0f}/t at 2025 avg $9k/t LCE, '
          f'${lce*20:.0f}/t at $20k/t; {1000/lce:.0f} t CO2 per t LCE')
print('  NOTE: this lithium is produced whether the voidage is filled by CO2 or by spent brine. It is NOT a credit')
print('  per tonne of CO2; it is a co-location ratio. Only the storage fee and avoided costs are incremental.')

# ------------------------------------------------------------------ 3. system voidage / scale
hdr('3. Scale: voidage-matched CO2 (Mt/yr)')
def co2_from_lce(lce_tpy, li):
    brine = lce_tpy / LCE_PER_LI * 1e6 / (li * 0.8); return brine, brine / vt / 1e6
for label, lce, li in [('3 first-wave Arkansas DLE projects (Malone 2026 claim, 53,100 t/yr LCE)', 53100, 300),
                       ('Same at 400 mg/L', 53100, 400), ('One 22.5 kt/yr LCE plant at 437 mg/L [recall SWA DFS]', 22500, 437),
                       ('One 25 kt/yr plant at 400 mg/L', 25000, 400)]:
    b, c = co2_from_lce(lce, li)
    print(f'  {label}: brine {b/1e6:.1f} Mm3/yr ({b/BBL/365/1e3:.0f} kbbl/d) -> {c:.1f} Mt CO2/yr')
for li in (200, 350):   # [src, claim] USGS: ~5,000 t Li brought to surface 2022 by oil/gas/bromine brine handling
    b = 5000e6 / li
    print(f'  2022 brine handling (5,000 t Li at {li} mg/L): {b/1e6:.0f} Mm3/yr -> {b/vt/1e6:.0f} Mt CO2/yr')
# global ceiling: all world lithium from 300 mg/L brine with CO2 voidage replacement
glob = 263e3   # [src] USGS MCS 2026: 2025 global consumption 263,000 t Li
b = glob * 1e6 / (300 * 0.8)
print(f'  CEILING: if ALL 2025 world Li demand ({glob/1e3:.0f} kt Li) came from 300 mg/L brine: {b/1e9:.2f} bn m3/yr '
      f'-> {b/vt/1e9:.2f} Gt CO2/yr ({b/vt/1e9/FOSSIL_CO2_GT:.1%} of fossil CO2)')
for share, li in [(0.05, 300), (0.15, 300)]:
    b = glob * 2.5 * share * 1e6 / (li * 0.8)   # [assume] demand x2.5 by ~2035
    print(f'  2035-ish: {share:.0%} of 2.5x-2025 Li demand from voidage-swap brine fields -> {b/vt/1e9:.3f} Gt/yr')

# ------------------------------------------------------------------ 4. breakthrough, buoyancy and pressure reach
hdr('4. Reservoir screening: pressure reach vs CO2 plume, buoyant up-dip creep, dissolved-CO2 recycle')
k, phi, h, ct, mu_b = 100e-15, 0.17, 40.0, 1.0e-9, 0.45e-3   # [assume] Smackover grainstone 100 mD, 17%, 40 m net,
#                                                              total compressibility 1e-9/Pa, brine 0.45 cP at 115 C
D = k / (phi * mu_b * ct)
for yrs in (1, 5, 20):
    print(f'  pressure diffusion length sqrt(4Dt) after {yrs:>2} yr: {math.sqrt(4*D*yrs*YR)/1e3:.1f} km '
          f'(D = {D:.2f} m2/s)')
print(f'  viscosity ratio brine/CO2 = {mu_b/mu_co2:.1f} (adverse mobility -> fingering, early breakthrough)')
for rate_mt, yrs, Eloc in [(0.5, 20, 0.10), (0.5, 20, 0.25), (1.0, 20, 0.10)]:
    V = rate_mt * 1e6 * yrs * vt
    r = math.sqrt(V / (math.pi * h * phi * Eloc))
    print(f'  plume radius, {rate_mt} Mt/yr x {yrs} yr, local sweep {Eloc:.0%}: {r/1e3:.1f} km')
# single 5-spot style: producer at L from injector, breakthrough at E_bt of pattern pore volume
for L, Ebt in [(1000, 0.03), (1500, 0.05), (3000, 0.05), (5000, 0.05)]:
    pv = math.pi * L ** 2 * h * phi
    mt = Ebt * pv / vt / 1e6
    print(f'  injector-producer distance {L/1e3:.1f} km, breakthrough at {Ebt:.0%} of PV within that radius: '
          f'{mt:.2f} Mt stored before breakthrough = {mt/0.5:.1f} yr at 0.5 Mt/yr')
drho = 1150 - rho   # [assume] Smackover brine ~1,150 kg/m3 in situ (very saline Ca-Na-Cl)
for sin_t in (0.01, 0.03):   # [assume] regional dip ~0.6-1.7 degrees
    v = k * 0.3 * drho * 9.81 * sin_t / (mu_co2 * phi)
    print(f'  buoyant up-dip CO2 creep, dip sin={sin_t}, krCO2 0.3: {v*YR:.0f} m/yr -> {v*YR*20/1e3:.1f} km in 20 yr')
print('  -> Buoyant up-dip creep is slow (tens of m/yr) at 100 mD; the breakthrough risk is the viscous drive toward')
print('     producers (adverse mobility ~10) plus gravity override in the top of the zone. Pressure travels ~10x')
print('     farther than fluid: CO2 injectors 3-5+ km from producers give pressure support with >10 yr to breakthrough.')
for tds in (200, 300):   # [assume] Smackover brines ~200-350 g/L TDS; NaCl proxy (CaCl2 salts out more)
    c = kg_co2_per_m3_brine(115, 280, tds, 1.15 if tds > 250 else 1.13)
    print(f'  dissolved CO2 at saturation, 115 C 280 bar, TDS {tds} g/L: {c:.1f} kg/m3 -> if produced brine were '
          f'saturated: {c*vt:.0f} kg CO2 recycled per t stored ({c*vt/10:.1f}%)')

# ------------------------------------------------------------------ 5. energy per tonne
hdr('5. Energy per tonne CO2 stored (GJ/t)')
sep = floors['Ammonia/SMR process CO2, 98%']
cases = {}
for lab, comp_kwh, dehy, brine_dp_bar, pump_eta, recyc in [('low', 95, 0.005, 30, 0.75, 0.0),
                                                          ('base', 115, 0.01, 60, 0.70, 0.01),
                                                          ('high', 140, 0.02, 100, 0.65, 0.03)]:
    # [src-ish] compression ~90-130 kWh/t to 150 bar for low-pressure high-purity CO2 (NETL/IEAGHG ranges, recall)
    comp = comp_kwh * 0.0036
    brine = vt * brine_dp_bar * 1e5 / pump_eta / 1e9   # spent brine to new disposal zone (incremental only)
    rec = recyc * comp                                  # recompress dissolved/breakthrough CO2
    tot = comp + dehy + brine + rec
    cases[lab] = tot
    print(f'  {lab:>4}: compression {comp:.3f} + dehydration {dehy:.3f} + spent-brine disposal pumping {brine:.3f} '
          f'+ recycle {rec:.3f} = {tot:.3f} GJ/t (separation floor {sep:.4f})')
print(f'  second-law check: actual base / compression floor = {cases["base"]/comp_floor:.2f}x ; nothing below a floor.')

# ------------------------------------------------------------------ 6. cost per tonne
hdr(f'6. Cost per tonne CO2 stored ($/t, 2025$): capex annualised at CRF(8%, 20 yr) = {crf(0.08, 20):.4f}')
CRF = crf(0.08, 20)
def cost(case):
    p = case
    power_mw = 1e6 * p['kwh'] / 1e3 / 8000          # MW for 1 Mt/yr
    comp_capex = power_mw * 1e3 * p['comp_usd_kw']
    comp = (comp_capex * (CRF + 0.04)) / 1e6 + p['kwh'] / 1e3 * p['elec']
    pipe = p['km'] * p['usd_per_km'] * (CRF + 0.025) / (p['pipe_mt'] * 1e6)
    wells = p['inj_wells_per_mt'] * p['well_usd'] * (CRF + 0.05) / 1e6
    mrv = p['mrv']
    brine = vt / BBL * p['disp_bbl']
    recycle = p['recycle']
    li_fee_share = 0.0
    tot = comp + pipe + wells + mrv + brine + recycle + p['dehy']
    return dict(compression=comp, dehydration=p['dehy'], pipeline=pipe, injection_wells=wells, MRV_site=mrv,
                spent_brine_disposal=brine, recycle=recycle, total=tot)
CASES = {
 'low':  dict(kwh=95,  elec=45, comp_usd_kw=1500, km=50,  usd_per_km=1.0e6, pipe_mt=5, inj_wells_per_mt=1, well_usd=10e6,
              mrv=3, disp_bbl=0.5, recycle=0.0, dehy=1),
 'base': dict(kwh=115, elec=65, comp_usd_kw=2500, km=150, usd_per_km=1.5e6, pipe_mt=3, inj_wells_per_mt=2, well_usd=15e6,
              mrv=5, disp_bbl=0.75, recycle=1.0, dehy=2),
 'high': dict(kwh=140, elec=90, comp_usd_kw=3500, km=300, usd_per_km=2.0e6, pipe_mt=1.5, inj_wells_per_mt=3, well_usd=25e6,
              mrv=10, disp_bbl=1.0, recycle=3.0, dehy=3),
}
res = {}
for lab, c in CASES.items():
    r = cost(c); res[lab] = r
    print(f'  {lab:>4}: ' + ', '.join(f'{k} {v:.1f}' for k, v in r.items()))
print('  Assumptions: [assume] Gulf Coast industrial power $45-90/MWh; compressor $1.5-3.5k/kW; onshore CO2 pipeline')
print('  $1-2M/km (12-16 in.); Class VI injector $10-25M incl. monitoring well share; spent-brine disposal $0.5-1/bbl.')
swap_increment = {lab: res[lab]['spent_brine_disposal'] + res[lab]['recycle'] for lab in res}
print(f'  Swap-specific increment over a plain Class VI site (brine disposal + recycle): '
      + ', '.join(f'{k} ${v:.1f}' for k, v in swap_increment.items()))
q45 = 85   # [recall] 45Q geological storage $85/t (prevailing wage), retained in the July 2025 OBBBA
for lab in res:
    print(f'  {lab}: net vs 45Q ${q45}/t storage credit: margin ${q45 - res[lab]["total"]:.0f}/t')
# value of pressure relief = avoided dedicated brine-extraction (ACRM) cost for a pressure-limited site
for lab, wells_per_mt, wcost, lift_kwh_m3, disp in [('low', 1, 4e6, 1.0, 0.5), ('base', 2, 6e6, 2.0, 0.75),
                                                    ('high', 3, 10e6, 3.0, 1.0)]:
    v = wells_per_mt * wcost * (CRF + 0.05) / 1e6 + vt * lift_kwh_m3 * 65 / 1e3 + vt / BBL * disp
    print(f'  {lab}: avoided ACRM brine-extraction cost (wells + lift + disposal) if site were pressure-limited: ${v:.1f}/t')

# ------------------------------------------------------------------ 7. resources
hdr('7. Resource needs at scale')
for gt in (0.01, 0.025, 0.1):
    s = ScaleCheck(gt, cases['base'])
    print(f'  {gt*1e3:.0f} Mt/yr: {s.ej_per_year*1e3:.1f} PJ/yr = {s.share_of_world_primary_energy:.4%} of world primary, '
          f'{s.share_of_world_electricity_if_electric:.4%} of world electricity; spent-brine disposal '
          f'{gt*1e9*vt/1e6:.0f} Mm3/yr ({gt*1e9*vt/BBL/365/1e6:.2f} Mbbl/d)')
print('  Water: none consumed (brine is produced and re-disposed). Land: well pads + pipeline ROW only.')
print('  Pore space: the spent brine still needs a disposal formation with ~1.7 m3/t capacity -> the pressure problem')
print('  moves to that zone; net basin-scale pressure relief is zero unless the disposal zone is open/underpressured.')
