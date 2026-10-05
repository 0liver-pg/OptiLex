"""Verifier for graft_subsurface_6: retire-and-store covenant (dedicated CO2 storage in depleted oil fields whose
hydrocarbon rights are permanently extinguished).
Run: cd OptiLex && .venv/bin/python <this file>
Labels: [src] fetched this session, [recall] pre-cutoff knowledge not re-verified, [assume] my assumption, [calc] derived."""
import sys, math
sys.path.insert(0, 'climate')
sys.path.insert(0, 'climate/runs/2026-10-05/scripts')
from physics import *  # noqa
from co2_brine import co2_density
import numpy as np

def hdr(s): print('\n' + '=' * 100 + '\n' + s + '\n' + '=' * 100)
def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)

T_BBL = 0.43          # [src] EPA GHG equivalencies: 0.43 t CO2/bbl crude combusted (5.80 MMBtu/bbl x 20.31 kg C/MMBtu x 44/12)
MCF_T = 0.0529        # [calc] 1 Mcf CO2 at 60 F, 14.696 psia ~ 1.87 kg/m3 x 28.32 m3 = 52.9 kg
Q45_PS, Q45_DAC = 85.0, 180.0   # [src] 26 USC 45Q (Cornell LII): post-P.L.119-21 single $17 base (x5 = $85) for storage AND
#                                 utilisation (EOR) for facilities placed in service after 4 Jul 2025; DAC $36 base -> $180 [recall x5]
DAC_CREDIT = 500.0    # [assume, idea's figure] voluntary DAC removal price; CDR.fyi-type range ~$400-700/t [recall]

# ------------------------------------------------------------------ 1. thermodynamic floors
hdr('1. Thermodynamic floors (verifier) - the covenant itself does no separation')
w_air = min_separation_work(420e-6, 0.75, 0.99); g_air = gj_per_tonne(w_air)
w_eth = min_separation_work(0.98, 0.90, 0.999); g_eth = gj_per_tonne(w_eth)
comp_floor = R * T0 * math.log(150 / 1.0) / M_CO2 / 1e6
print(f'  DAC source (420 ppm, 75% capture): {w_air/1e3:.2f} kJ/mol = {g_air:.3f} GJ/t  [upstream, paid by DAC chain]')
print(f'  BECCS-ethanol source (98% CO2): {g_eth:.4f} GJ/t  [upstream]')
print(f'  Ideal isothermal compression 1 -> 150 bar: {comp_floor:.3f} GJ/t ({comp_floor/0.0036:.0f} kWh/t)  '
      f'CLAIM 0.28 GJ/t -> {"OK" if abs(comp_floor-0.28) < 0.01 else "MISMATCH"}')
print('  (Real CO2 is non-ideal: above ~74 bar it is dense-phase and is pumped, so the true reversible work 1->150 bar')
print('   is somewhat BELOW the ideal-gas value; 0.28 is a conservative floor, not a violated one.)')

# ------------------------------------------------------------------ 2. energy per tonne stored (storage step)
hdr('2. Energy per tonne for the storage step (compression + pipeline boost + injection), electricity')
# [recall] real multistage intercooled compression + dense-phase pumping to 110-150 bar: ~90-120 kWh/t (IPCC SRCCS 2005,
#  NETL baseline studies); pipeline boosters over <100 km ~0-10 kWh/t; injection pumps ~0-5 kWh/t.
E = {'low': (85 + 0 + 0) * 0.0036, 'base': (105 + 5 + 3) * 0.0036, 'high': (125 + 15 + 8) * 0.0036}
for k, v in E.items():
    print(f'  {k:<4}: {v:.2f} GJ_e/t stored  (second-law eff. vs ideal compression floor {comp_floor/v:.0%})')
# EOR counterfactual: purchased CO2 is recycled; gross injection typically 2-3x net purchase [recall]; recycle
#  compression from ~2-20 bar separator pressure to ~150 bar ~60-90 kWh per recycled t [assume]
for ratio in (2.0, 3.0):
    extra = (ratio - 1) * 75 * 0.0036
    print(f'  EOR counterfactual: gross/net injection {ratio:.0f}x -> extra recycle compression ~{extra:.2f} GJ_e per t net '
          f'purchased; dedicated storage SAVES this energy')
print(f'  Full chain incl. DAC (real 5-10 GJ/t) + storage: {5+E["low"]:.1f}-{10+E["high"]:.1f} GJ/t; covenant adds ~0 energy.')

# ------------------------------------------------------------------ 3. forgone-EOR premium: idea vs full estate
hdr('3. Covenant premium per t stored: idea (operator netback only) vs all estate holders (WI + royalty + state)')
for b in (2.0, 3.0):
    for m in (15, 25):
        print(f'  IDEA: {b} bbl/t x ${m}/bbl = ${b*m:.0f}/t -> {b*m/Q45_PS:.0%} of $85 45Q, {b*m/DAC_CREDIT:.0%} of $500 DAC credit')
print('  bbl/t check: net CO2 utilisation 5-10 Mcf/bbl [recall, mature Permian floods] =',
      f'{5*MCF_T:.2f}-{10*MCF_T:.2f} t/bbl -> {1/(10*MCF_T):.1f}-{1/(5*MCF_T):.1f} bbl/t  (idea uses 2-3: inside range)')
# Price: [src] EIA STEO Sep 2026: Brent averaged $91/b in Aug 2026, forecast $74/b in 2027. WTI ~Brent - $4 [assume].
ROY = 0.20     # [assume] Permian royalty 1/8-1/4; 20% mid
SEV = 0.046    # [recall] Texas oil production tax 4.6% of market value
def per_bbl(wti, opex_capex):
    gross = wti
    royalty = gross * ROY
    sev = gross * SEV
    wi = gross * (1 - ROY) - sev * (1 - ROY) - opex_capex   # severance borne pro rata
    return wi, royalty, sev, wi + royalty + sev * 0  # rights-holder total excl. state
rows = []
for wti, oc in [(60, 30), (70, 30), (87, 32)]:   # [assume] EOR lifting + CO2 recycle + amortised conversion capex $/bbl
    wi, roy, sev, tot = per_bbl(wti, oc)
    rows.append((wti, wi, roy, sev))
    print(f'  WTI ${wti}: WI netback ${wi:.1f}/bbl, royalty ${roy:.1f}/bbl, severance tax ${sev:.1f}/bbl '
          f'-> owners (WI+royalty) ${wi+roy:.1f}/bbl; incl. state ${wi+roy+sev:.1f}/bbl')
for b in (1.5, 2.5, 3.5):
    s = ', '.join(f'WTI{w}: ${b*(wi+roy):.0f}/t' for w, wi, roy, sev in rows)
    print(f'  owners\' premium at {b} bbl/t: {s}')
print('  -> The idea counts only the operator netback ($15-25). Royalty owners also hold the extinguished estate and')
print('     must be paid (~$12-17/bbl); at Aug-2026 prices the full-estate premium exceeds the $100/t kill line.')

# ------------------------------------------------------------------ 4. incremental climate benefit and $/t avoided
hdr('4. Net avoided emissions per t stored and cost per t CO2e AVOIDED by the covenant (vs DAC CO2 going to EOR)')
for b in (2.0, 3.0):
    for r in (0.5, 0.8):
        print(f'  {b} bbl/t: gross {b*T_BBL:.2f} t; net of {r:.0%} replacement {b*T_BBL*(1-r):.2f} t CO2/t stored  (claim 0.17-0.65)')
print('  Identity: $/t avoided = premium per bbl / (0.43 x (1 - replacement)); independent of bbl/t.')
for pb in (15, 25, 40, 55):
    print(f'    ${pb}/bbl: {pb/(T_BBL*0.5):.0f} $/t at 50% replacement; {pb/(T_BBL*0.2):.0f} $/t at 80% replacement')

# ------------------------------------------------------------------ 5. dedicated storage cost (T&S) for depleted unit
hdr('5. Dedicated Class VI storage cost in a depleted San Andres-type unit (capacity, legacy wells, MRV)')
area = 10_000 * 4046.86   # [assume] 10,000-acre unit
h, phi = 30.0, 0.12       # [assume] net pay 30 m, porosity 12% (San Andres dolomite)
rho = co2_density(40.0, 140.0)   # [assume] ~1,400 m, 40 C, depleted then re-pressured to ~140 bar
print(f'  CO2 density at 40 C, 140 bar (CoolProp): {rho:.0f} kg/m3')
for E_s in (0.10, 0.25, 0.40):   # [assume] fraction of pore volume usable (depleted oil fields: replaces produced voidage)
    cap = area * h * phi * E_s * rho / 1e9
    print(f'  storage efficiency {E_s:.0%}: capacity {cap:.0f} Mt')
cap_base = area * h * phi * 0.25 * rho / 1e9
n_wells = 10_000 / 20    # [assume] 20-acre spacing legacy wellbores
for cpw in (75e3, 150e3, 300e3):  # [assume] re-entry/re-plug per legacy well, $ (Class VI AoR corrective action)
    print(f'  {n_wells:.0f} legacy wells x ${cpw/1e3:.0f}k = ${n_wells*cpw/1e6:.0f}M -> ${n_wells*cpw/(cap_base*1e6):.1f}/t over {cap_base:.0f} Mt')
# Storage-site capex/opex, annualised [recall: US onshore T&S ~$8-25/t, NETL FECM / IEAGHG]
r, n = 0.08, 25
inj_rate = 1.0e6   # t/yr
for label, capex, opex_t, mrv, e_mwh, pipe in [('low', 60e6, 3.0, 1.5, 40, 3), ('base', 120e6, 5.0, 3.0, 60, 6),
                                              ('high', 220e6, 8.0, 5.0, 90, 12)]:
    # capex: injection wells, compression, monitoring wells, legacy-well remediation, permitting
    ann = capex * crf(r, n) / inj_rate
    en = {'low': E['low'], 'base': E['base'], 'high': E['high']}[label] / 3.6 * e_mwh
    tot = ann + opex_t + mrv + en + pipe
    print(f'  {label:<4}: capex ${capex/1e6:.0f}M @8%/25yr = ${ann:.1f}/t; opex ${opex_t}; MRV ${mrv}; energy ${en:.1f} '
          f'(@${e_mwh}/MWh); pipeline ${pipe} -> T&S ${tot:.1f}/t stored')

# ------------------------------------------------------------------ 6. Monte Carlo: buyer cost per t stored and $/t avoided
hdr('6. Monte Carlo (n=200k): covenant premium, T&S, buyer add-on per t stored, $ per t net CO2e avoided')
rng = np.random.default_rng(6)
N = 200_000
tri = lambda a, m, b: rng.triangular(a, m, b, N)
wti = tri(55, 72, 92)                 # [src-anchored] Brent $74 (2027 STEO) / $91 (Aug 2026); WTI ~ -$4
oc = tri(22, 30, 40)                  # [assume] EOR opex + amortised conversion capex $/bbl
bpt = tri(1.5, 2.5, 3.5)              # [recall] 5-10 Mcf/bbl, plus late-life/post-flood fields lower
roy = tri(0.125, 0.20, 0.25)
wi = np.maximum(wti * (1 - roy) * (1 - SEV) - oc, 0)
owners = (wi + wti * roy) * bpt       # $/t stored, all private rights holders
op_only = wi * bpt                    # idea's framing
ts = tri(8, 15, 28)                   # [calc/recall] T&S from section 5
mrv_extra = tri(1, 3, 5)              # [assume] Class VI vs Subpart RR EOR accounting difference
rep = tri(0.5, 0.65, 0.8)             # [assume, unverified] market replacement of retired barrels
avoided = bpt * T_BBL * (1 - rep)
cost_avoided = (owners + mrv_extra) / avoided
pct = lambda x: np.percentile(x, [10, 50, 90])
for name, x in [('operator-only premium $/t stored (idea framing)', op_only), ('owners premium $/t stored (WI+royalty)', owners),
                ('buyer add-on: owners premium + T&S $/t stored', owners + ts),
                ('net avoided t CO2 per t stored', avoided), ('covenant $ per t CO2e avoided', cost_avoided),
                ('owners premium as share of $500 DAC credit', owners / DAC_CREDIT),
                ('owners premium as share of $85 45Q', owners / Q45_PS)]:
    p = pct(x)
    print(f'  {name:<50} P10 {p[0]:8.2f}  P50 {p[1]:8.2f}  P90 {p[2]:8.2f}')
print(f'  P(owners premium > $100/t kill line) = {np.mean(owners > 100):.0%};  P(operator-only > $100/t) = {np.mean(op_only > 100):.0%}')
# Total tonne-of-CO2e view: stored tonne (removal, credited to DAC chain) + avoided
tot_cost_stored = owners + ts
print(f'  Cost per t CO2e of (stored + avoided), storage-side only (excl. capture): P50 '
      f'${np.median(tot_cost_stored/(1+avoided)):.0f}/t')
print(f'  Full chain with DAC capture ~$400-600/t [assume]: P50 ${np.median((450+tot_cost_stored)/(1+avoided)):.0f} per t CO2e')

# ------------------------------------------------------------------ 7. scale and resource needs
hdr('7. Scale: limited by DAC/BECCS CO2 supply near Permian/Gulf depleted fields, not by pore space')
# [recall] Stratos nameplate 0.5 Mt/yr (start-up 2025); US ethanol fermentation CO2 ~45 Mt/yr mostly Midwest (not Permian);
# [recall] US CO2-EOR uses ~60-70 Mt/yr purchased CO2; NATCARB oil+gas reservoir capacity ~186 Gt (US).
for label, mt in [('low 2035 (Stratos + 2-3 DAC/BECCS projects)', 5), ('base 2035', 20), ('high 2035 (DAC hubs + Gulf BECCS)', 80),
                  ('ceiling: all US purchased-CO2 EOR volume converted', 65)]:
    gt = mt / 1e3
    b = 2.5 * T_BBL * 0.35
    s = ScaleCheck(gt, E['base'])
    print(f'  {label:<48}: {gt:.3f} Gt/yr stored + {gt*b:.3f} Gt/yr net avoided (2.5 bbl/t, 65% repl.); '
          f'storage energy {s.ej_per_year*1e3:.1f} PJ/yr = {s.share_of_world_primary_energy:.4%} of world primary; '
          f'retired oil {mt*1e6*2.5/365/1e3:.0f} kbbl/d')
print(f'  Pore space: base unit {cap_base:.0f} Mt -> 20 Mt/yr for 25 yr needs ~{20*25/cap_base:.0f} such units')
print(f'  Land: surface footprint small (wells/pads); covenant area per unit {area/1e6:.0f} km2 subsurface, surface use unchanged')
print('  Water: none incremental (no produced-water handling once production ceases; less than EOR).')
print(f'  Global ceiling of the incremental climate effect: even 0.1 Gt/yr stored -> {0.1*2.5*T_BBL*0.35:.3f} Gt/yr avoided '
      f'= {0.1*2.5*T_BBL*0.35/TOTAL_GHG_GT_CO2E:.2%} of world GHG')
