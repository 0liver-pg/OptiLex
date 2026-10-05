"""Verifier for idea bottleneck_thermo_4: "Store heat, not the loaded sorbent".

Checks: (1) thermodynamic floor and exergy of the regeneration route; (2) the idea's own
arithmetic; (3) a temperature-feasibility correction to the hot-water store; (4) the missing
cost of 3x-rated charging equipment and grid capacity; (5) the price spread in REAL 2025
hourly day-ahead data (SMARD, Bundesnetzagentur: DE-LU, DK1, FR); (6) full heat-cost comparison
of flat vs stored options; (7) gross and net cost per tonne, including grid CO2 in charging hours
(2025 German hourly generation mix, SMARD); (8) scale and resources.

Data files: ./smard/*.json downloaded 2025-10-05 from www.smard.de/app/chart_data
(filter 4169 = DE-LU day-ahead, 252 = DK1, 254 = FR; generation filters 1223 lignite,
4069 hard coal, 4071 gas, 1227 other conventional, others zero-emission; 410 = load).
"""
import sys, json, glob, os, math, datetime as dt
from collections import defaultdict
sys.path.insert(0, 'climate')
from physics import *

HERE = os.path.dirname(os.path.abspath(__file__))
SM = os.path.join(HERE, 'smard')
USD_PER_EUR = 1.13          # ~2025 average (assumption, ECB reference rate order of magnitude)
L, B, H = 'low', 'base', 'high'

def hdr(s):
    print('=' * 92); print(s); print('-' * 92)

# ---------------------------------------------------------------------------------------------
hdr('1. THERMODYNAMIC FLOOR AND EXERGY OF THE REGENERATION ROUTE')
w_air = min_separation_work(420e-6, 0.75, 0.99)
floor = gj_per_tonne(w_air)
print(f'Floor, air 420 ppm, 75% capture, 99% pure: {w_air/1e3:.1f} kJ/mol = {floor:.3f} GJ/t ({floor/0.0036:.0f} kWh/t)')
Q_TH = {L: 5.5, B: 7.2, H: 9.0}        # GJ_th/t; base = Climeworks Gen2 nominal ~2,000 kWh_th/t (idea's figure);
                                        # low ~ newer solid-sorbent claims; high ~ field-reported higher heat use
E_EL = {L: 0.5, B: 0.65, H: 0.8}       # MWh_e/t fans+vacuum+aux, continuous (assumption, literature 0.2-0.9 MWh/t)
T_REGEN_C = 100.0
for k in (L, B, H):
    ex_heat = Q_TH[k] * (1 - T0 / (T_REGEN_C + 273.15))
    gj_e_boiler = Q_TH[k] + E_EL[k] * 3.6
    print(f'  {k:4s}: heat {Q_TH[k]:.1f} GJ_th/t (exergy at {T_REGEN_C:.0f} C = {ex_heat:.2f} GJ/t) + elec {E_EL[k]*3.6:.2f} GJ_e/t; '
          f'all-electric via e-boiler = {gj_e_boiler:.2f} GJ_e/t -> 2nd-law eff {second_law_efficiency(gj_e_boiler, floor):.1%}')
print('  -> No claim is below the floor; storing heat changes WHEN energy is bought, not how much (plus storage losses).')

# ---------------------------------------------------------------------------------------------
hdr("2. RE-RUN OF THE IDEA'S OWN ARITHMETIC (100 kt/yr plant, 7.2 GJ_th/t, 16 h store, dT 50 K)")
plant = 100_000
mw_th = plant * Q_TH[B] * 1e9 / 3.1536e7 / 1e6
mwh_store = mw_th * 16
m3 = mwh_store * 3.6e9 / (4180 * 1000 * 50)
print(f'  average heat {mw_th:.1f} MW_th; 16 h store {mwh_store:.0f} MWh_th = {m3:,.0f} m3 at dT 50 K (rho*cp 4.18 MJ/m3K)')
for c in (150, 400):
    print(f'  store at ${c}/m3: ${m3*c/1e6:.2f}M = ${m3*c/plant:.0f} per t/yr')
buf = plant / 8760 * 16
for wcap, price in ((1.5, 20), (1.0, 40)):
    st = buf / (wcap * 44.01e-3)
    print(f'  loaded-sorbent buffer: {buf:.0f} t CO2 -> {st:,.0f} t sorbent at {wcap} mmol/g, ${price}/kg = ${st*price*1e3/1e6:.0f}M = ${st*price*1e3/plant:,.0f} per t/yr')
for cf in (0.95, 0.33):
    print(f'  capital charge $2,600 per t/yr, CRF 0.10, CF {cf:.0%}: ${2600*0.10/cf:,.0f}/t')
print('  -> Arithmetic reproduces. Caveat: $2,600 per t/yr is a Stratos (liquid KOH + calciner) proxy, not a solid-sorbent TSA plant.')

# ---------------------------------------------------------------------------------------------
hdr('3. TEMPERATURE FEASIBILITY: usable dT must sit ABOVE the regeneration temperature')
def psat_bar(t_c):  # Antoine (water, 99-374 C range constants; adequate to ~+-3%)
    A, Bc, C = 8.14019, 1810.94, 244.485
    return 10 ** (A - Bc / (C + t_c)) / 750.06
def rho_cp(t_c):   # MJ/m3K, liquid water, crude fit 20-180 C
    rho = 1000 - 0.0036 * (t_c - 4) ** 2 * 0.9  # approx: 958 at 100 C, 917 at 150 C
    cp = 4.18 + 0.0000045 * (t_c - 35) ** 2 * 10  # ~4.22 at 100 C, 4.31 at 150 C
    return rho * cp / 1e3
cases = [('idea as written (dT 50 K, unspecified temps) e.g. 120->70 C', 120, 70),
         ('feasible: 150 -> 105 C (regen ~100 C, 5 K approach)', 150, 105),
         ('feasible: 130 -> 105 C', 130, 105),
         ('cascade: 150 -> 70 C (sorbent sensible preheat uses <100 C heat; assume 30% of duty)', 150, 70)]
for name, th, tc in cases:
    vc = rho_cp((th + tc) / 2)
    vol = mwh_store * 3.6e3 / (vc * (th - tc))
    print(f'  {name}: dT {th-tc} K, top pressure {psat_bar(th):.1f} bar abs, {vol:,.0f} m3 '
          f'({"BELOW regen temp for part of swing" if tc < T_REGEN_C and "cascade" not in name else "ok"})')
print('  -> As written (100-120 C, dT 50 K) the bottom of the swing is below ~100 C regeneration; a valid design')
print('     needs ~150 C top (~4.8 bar) or a smaller dT (25-45 K => 1.1-2x the volume). Store cost stays small (see 6).')
# COP of an air-source heat pump that must charge the store top temperature
def cop_carnot_frac(t_src, t_sink, frac):
    return frac * (t_sink + 273.15) / (t_sink - t_src)
print('  heat-pump COP (fraction of Carnot) for sink = store top temperature:')
for t_src, lab in ((10, 'ambient air 10 C (C-European annual mean)'), (-5, 'winter air -5 C'), (50, 'DAC condenser/exhaust heat ~50 C')):
    print('    ' + lab + ': ' + ', '.join(f'sink {ts} C: COP {cop_carnot_frac(t_src, ts, 0.5):.2f}' for ts in (110, 130, 150)))
print("  -> The idea's COP 2.2 'air-source to 100 C' is 57% of Carnot at 10->110 C; at a feasible 150 C top it is ~1.4-1.6.")
COP = {L: 1.5, B: 1.8, H: 2.5}   # store-charging HP COP; high case only with a ~50 C waste-heat source

# ---------------------------------------------------------------------------------------------
hdr('4. 2025 HOURLY DAY-AHEAD PRICES (SMARD): mean of cheapest N hours vs daily mean')
def load_series(prefix):
    ser = {}
    for f in glob.glob(os.path.join(SM, f'{prefix}_*.json')):
        for t, v in json.load(open(f))['series']:
            if v is not None:
                ser[t] = v
    return {t: v for t, v in ser.items() if dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).year == 2025}
markets = {'DE-LU': '4169', 'DK1': '252', 'FR': '254'}
prices = {m: load_series(fid) for m, fid in markets.items()}
def by_day(ser):
    d = defaultdict(list)
    for t, v in sorted(ser.items()):
        d[dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).date()].append((t, v))
    return {k: v for k, v in d.items() if len(v) >= 23}
spread = {}
for m, ser in prices.items():
    days = by_day(ser)
    vals = list(ser.values())
    out = {}
    for n in (6, 8, 12):
        cheap = [sum(sorted(v for _, v in hrs)[:n]) / n for hrs in days.values()]
        flat = [sum(v for _, v in hrs) / len(hrs) for hrs in days.values()]
        out[n] = (sum(flat) / len(flat), sum(cheap) / len(cheap))
    spread[m] = out
    neg = sum(1 for v in vals if v < 0)
    print(f'  {m}: {len(vals)} h, mean EUR {sum(vals)/len(vals):.1f}/MWh, negative hours {neg}; ' +
          '; '.join(f'cheapest {n} h/day mean EUR {c:.1f} (spread {f-c:.1f})' for n, (f, c) in out.items()))
print('  NOT computed (no data fetched): ERCOT, CAISO, SE3. The idea named them; treat as open.')

# ---------------------------------------------------------------------------------------------
hdr('5. GRID CO2 INTENSITY IN CHARGING HOURS (DE, 2025, production-based, direct combustion only)')
EF = {'1223': 1.10, '4069': 0.85, '4071': 0.40, '1227': 0.70}   # t CO2/MWh_e (assumed typical fleet values)
zero = ['1225', '1226', '1228', '4066', '4067', '4068', '4070']
gen = {k: load_series('g' + k) for k in list(EF) + zero}
hours = sorted(set.intersection(*[set(s) for s in gen.values()]) & set(prices['DE-LU']))
ci = {}
for t in hours:
    tot = sum(gen[k][t] for k in gen)
    ci[t] = sum(gen[k][t] * EF[k] for k in EF) / tot if tot > 0 else 0
avg_ci = sum(ci.values()) / len(ci)
days = by_day({t: prices['DE-LU'][t] for t in hours})
ci_cheap = {}
for n in (8, 12):
    sel = []
    for hrs in days.values():
        sel += [t for t, _ in sorted(hrs, key=lambda x: x[1])[:n]]
    ci_cheap[n] = sum(ci[t] for t in sel) / len(sel)
print(f'  DE 2025 mean generation intensity {avg_ci:.3f} t/MWh; cheapest-8h {ci_cheap[8]:.3f}; cheapest-12h {ci_cheap[12]:.3f}')
print('  (ignores imports and life-cycle emissions; marginal intensity of an added load is higher than average)')

# ---------------------------------------------------------------------------------------------
hdr('6. LEVELISED REGENERATION-HEAT COST, $/t CO2 (100 kt/yr plant, CF 0.95), flat vs stored')
CRF = {L: 0.08, B: 0.10, H: 0.12}
HP_CAPEX = {L: 600, B: 900, H: 1500}      # $/kW_th, high-temp industrial HP (assumption; DEA catalogue-range)
EB_CAPEX = {L: 60, B: 100, H: 200}        # $/kW_e electrode boiler incl. install (assumption; DEA catalogue-range)
TANK = {L: 150, B: 400, H: 1000}          # $/m3 pressurised hot-water store (atmospheric DH tanks ~150-250)
GRID_FIXED = {L: 0, B: 15, H: 30}         # EUR/MWh energy-based network charge (DE industrial, assumption)
GRID_CAP = {L: 0, B: 40, H: 100}          # EUR/kW/yr capacity charge on extra connection (0 = interruptible tariff)
LOSS = {L: 0.005, B: 0.01, H: 0.03}       # fraction of stored heat lost per cycle
OM = 0.02                                 # fixed O&M, fraction of capex per year
CF = 0.95
def heat_cost(market, k, tech, n_charge):
    q = Q_TH[k]; t_yr = plant * CF
    mw_avg = plant * q * 1e9 / 3.1536e7 / 1e6        # sized on nameplate
    cop = COP[k] if tech == 'hp' else 0.99
    flat, cheap = spread[market][n_charge if n_charge else 8]
    if n_charge is None:                               # continuous, flat purchase
        price, mw_th_rated, store, loss = flat, mw_avg, 0.0, 0.0
    else:
        price, mw_th_rated = cheap, mw_avg * 24 / n_charge
        store_h = 24 - n_charge
        vol = mw_avg * store_h * 3.6e3 / (rho_cp(127) * 45)   # 150 -> 105 C
        store, loss = vol * TANK[k], LOSS[k]
    mwh_e_per_t = q / 3.6 / cop * (1 + loss)
    equip = mw_th_rated * 1e3 * (HP_CAPEX[k] if tech == 'hp' else EB_CAPEX[k] / 0.99)
    capex = equip + store
    mw_e_rated = mw_th_rated / cop
    energy = mwh_e_per_t * (price + GRID_FIXED[k]) * USD_PER_EUR
    cap_chg = mw_e_rated * 1e3 * GRID_CAP[k] * USD_PER_EUR / t_yr
    fixed = capex * (CRF[k] + OM) / t_yr
    return energy + cap_chg + fixed, energy, cap_chg, fixed, store / plant
best = {}
for m in markets:
    print(f'  {m}:')
    for k in (L, B, H):
        rows = {}
        for tech in ('hp', 'eb'):
            for n in (None, 8, 12):
                rows[(tech, n)] = heat_cost(m, k, tech, n)
        line = ' | '.join(f'{t}{"-flat" if n is None else f"-{n}h"} {v[0]:.0f}' for (t, n), v in rows.items())
        bflat = min(v[0] for (t, n), v in rows.items() if n is None)
        bstore = min(v[0] for (t, n), v in rows.items() if n is not None)
        best[(m, k)] = (bflat, bstore)
        print(f'    {k:4s}: {line}  => best flat {bflat:.0f}, best stored {bstore:.0f}, saving {bflat-bstore:+.0f} $/t')
    eb = heat_cost(m, B, 'eb', 8); hp = heat_cost(m, B, 'hp', 8)
    print(f'    base breakdown eb-8h: energy {eb[1]:.0f}, grid capacity {eb[2]:.0f}, capex+O&M {eb[3]:.1f} (store ${eb[4]:.0f} per t/yr); '
          f'hp-8h: energy {hp[1]:.0f}, grid cap {hp[2]:.0f}, capex+O&M {hp[3]:.0f}')
print('  Low/base/high = favourable/central/unfavourable bundles of the assumptions listed above (applied jointly).')
print("  Idea's falsification line: saving < $15/t in every target market.")

# ---------------------------------------------------------------------------------------------
hdr('7. WHOLE-PLANT COST PER TONNE: gross and net of grid emissions (DE-LU, e-boiler + 8 h charging)')
DAC_CAPEX = {L: 1500, B: 2600, H: 4000}   # $ per t/yr (base = Stratos proxy used by the idea)
DAC_OM = 0.04
SORB = {L: 20, B: 50, H: 100}             # $/t sorbent replacement (assumption)
for k in (L, B, H):
    cap = DAC_CAPEX[k] * (CRF[k] + DAC_OM) / CF
    heat_flat, heat_store = best[('DE-LU', k)]
    el = E_EL[k] * (spread['DE-LU'][8][0] + GRID_FIXED[k]) * USD_PER_EUR
    gross_store = cap + heat_store + el + SORB[k]
    gross_flat = cap + heat_flat + el + SORB[k]
    # net: e-boiler route electricity in cheap hours + continuous aux at average intensity
    mwh_heat = Q_TH[k] / 3.6 / 0.99 * (1 + LOSS[k])
    emis = mwh_heat * ci_cheap[8] + E_EL[k] * avg_ci
    net = 1 - emis
    print(f'  {k:4s}: capital {cap:.0f} + heat {heat_store:.0f} (flat best {heat_flat:.0f}) + aux elec {el:.0f} + sorbent {SORB[k]} '
          f'= gross ${gross_store:.0f}/t (flat ${gross_flat:.0f}); grid CO2 {emis:.2f} t/t -> net removal {net:.2f} t/t -> '
          f'{"NET POSITIVE EMITTER" if net <= 0 else f"${gross_store/net:,.0f} per net t"}')
print('  CO2 storage/transport (~$15-40/t) excluded; a dedicated low-carbon PPA changes the net figure but not the spread logic.')

# ---------------------------------------------------------------------------------------------
hdr('8. SCALE AND RESOURCES (per Gt/yr DAC using this heat route)')
for k in (L, B, H):
    q = Q_TH[k]
    mw_avg = 1e9 * q * 1e9 / 3.1536e7 / 1e6
    tank_m3 = mw_avg * 16 * 3.6e3 / (rho_cp(127) * 45)
    eb_gw = mw_avg * 3 / 1e3
    twh_eb = 1e9 * (q / 3.6 / 0.99 + E_EL[k]) / 1e6
    twh_hp = 1e9 * (q / 3.6 / COP[k] + E_EL[k]) / 1e6
    sc = ScaleCheck(1.0, q + E_EL[k] * 3.6)
    print(f'  {k:4s}: store {tank_m3/1e6:.0f} Mm3 water; e-boiler {eb_gw:.0f} GW_e charging; electricity e-boiler {twh_eb:,.0f} TWh '
          f'({twh_eb/WORLD_ELECTRICITY_TWH:.1%} of world), HP {twh_hp:,.0f} TWh ({twh_hp/WORLD_ELECTRICITY_TWH:.1%}); '
          f'final energy {sc.ej_per_year:.1f} EJ ({sc.share_of_world_primary_energy:.2%} of primary)')
print('  Realistic DAC scale is set by DAC deployment, not by this add-on: ~0.01 Mt/yr operating (2025); IEA NZE-type')
print('  pathways ~1 Gt/yr by 2050 (modelled). Assume 0.05 (low) / 0.3 (base) / 1.0 (high) Gt/yr by 2050 for this route.')
