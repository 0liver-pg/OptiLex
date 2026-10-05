"""Sanity checks for six subsurface (petroleum-engineering) climate ideas.
Run: cd OptiLex && .venv/bin/python <this file>
All inputs are labelled: [src] = sourced, [assume] = my assumption, [calc] = derived here."""
import sys, math
sys.path.insert(0, 'climate')
sys.path.insert(0, 'climate/runs/2026-10-05/scripts')
from physics import *  # noqa
from co2_brine import solubility_brine, tds_to_molality, kg_co2_per_m3_brine, co2_density

BBL = 0.158987  # m3
G = 9.81


def comp_floor_gj(p1_bar, p2_bar, T=298.15):
    """Ideal isothermal compression work, GJ/t CO2 (ideal gas; real CO2 slightly lower at high P)."""
    return R * T * math.log(p2_bar / p1_bar) / M_CO2 / 1e6


def hdr(s):
    print('\n' + '=' * 100 + '\n' + s + '\n' + '=' * 100)


# ---------------------------------------------------------------- reference floors from the verifier
hdr('0. Verifier floors used below')
for name, x, f, p in [('Gas-processing/amine-acid-gas CO2 (~95%)', 0.95, 0.90, 0.999),
                      ('Ammonia/SMR process CO2 (~98%)', 0.98, 0.90, 0.999),
                      ('Cement flue 25%', 0.25, 0.90, 0.99), ('Air 420 ppm', 420e-6, 0.75, 0.99)]:
    w = min_separation_work(x, f, p)
    print(f'{name:<45} separation floor {gj_per_tonne(w):.3f} GJ/t')
print(f'Isothermal compression floor 1->150 bar: {comp_floor_gj(1,150):.3f} GJ/t; 1->55 bar: {comp_floor_gj(1,55):.3f}; '
      f'1.5->55 bar: {comp_floor_gj(1.5,55):.3f}')

# ---------------------------------------------------------------- IDEA 1: carbonated produced-water disposal
hdr('IDEA 1: dissolve CO2 into Class II produced-water disposal (SWD) streams')
# [src] GWPC 2021 report: US produced water 25.86e9 bbl in 2021; disposal injection 9.28e9 (operator) + 2.52e9 (commercial)
us_disp_bbl = 9.284e9 + 2.519e9
tx_disp_bbl = 8.108e9 * (0.4368 + 0.2418)       # [src] Texas 2021: operator 43.68% + commercial 24.18%
nm_disp_bbl = 0.717e9                            # [src] NM 2021 operator disposal (conservative; table inconsistent)
print(f'US disposal 2021: {us_disp_bbl/1e9:.2f} bn bbl = {us_disp_bbl*BBL/1e9:.2f} km3/yr; '
      f'TX {tx_disp_bbl/1e9:.2f} + NM {nm_disp_bbl/1e9:.2f} bn bbl = {(tx_disp_bbl+nm_disp_bbl)*BBL/1e9:.2f} km3/yr')
# Dissolution point: CO2 sparged into the downflowing water at depth (Carbfix-style) or at a surface mixer.
for tds in (80, 130, 200):          # [assume/src] Permian PW 120-140 g/L (Water 2020 MDPI study); range 80-200
    for (T, P) in [(30, 40), (35, 55), (40, 80)]:
        m = tds_to_molality(tds)
        sat = kg_co2_per_m3_brine(T, P, tds)
        print(f'  TDS {tds:>3} g/L (m~{m:.2f}) mix at {T} C, {P} bar: saturation {sat:5.1f} kg CO2/m3 brine')
# Design loading: 85% of saturation at 35 C / 55 bar, TDS 130 -> check stays dissolved at reservoir conditions
tds = 130
load = 0.85 * kg_co2_per_m3_brine(35, 55, tds)
print(f'Design loading (85% of sat at 35 C/55 bar, TDS 130): {load:.1f} kg/m3')
for name, T, P in [('Delaware Mtn Grp ~1.3 km', 40, 125), ('Ellenburger ~4.5 km', 110, 450)]:
    print(f'  reservoir {name}: solubility {kg_co2_per_m3_brine(T, P, tds):.1f} kg/m3 -> stays dissolved: '
          f'{kg_co2_per_m3_brine(T, P, tds) > load}')
# exsolution (bubble-point) pressure for that loading at 25 C: find P where saturation == load
lo, hi = 1.5, 55.0
for _ in range(60):
    mid = 0.5 * (lo + hi)
    if kg_co2_per_m3_brine(25, mid, tds) > load:
        hi = mid
    else:
        lo = mid
pb = 0.5 * (lo + hi)
print(f'  bubble point of loaded brine at 25 C: ~{pb:.0f} bar -> would degas if it rose above ~{pb*1e5/(1090*G):.0f} m depth '
      f'(e.g. via a leaking orphan well)')
for label, vol_bbl in [('US disposal', us_disp_bbl), ('TX+NM disposal', tx_disp_bbl + nm_disp_bbl)]:
    mt = vol_bbl * BBL * load / 1e9
    print(f'  ceiling if ALL {label} carried {load:.0f} kg/m3: {mt:.0f} Mt CO2/yr')
for frac in (0.1, 0.25):
    print(f'  realistic {frac:.0%} of TX+NM disposal volume: {(tx_disp_bbl+nm_disp_bbl)*BBL*load/1e9*frac:.0f} Mt/yr')
well_bpd = 20000  # [assume] large Permian SWD well rate
per_well = well_bpd * BBL * 365 * load / 1e3  # t/yr
print(f'  per 20,000 bbl/d SWD well: {per_well/1e3:.1f} kt CO2/yr; wells per Mt/yr: {1e6/per_well:.0f} '
      f'(vs ~1.4 dedicated wells per Mt/yr at P50 0.7 Mt/yr/well, Ringrose & Meckel 2019)')
# volume added (partial molar volume ~35 cm3/mol [assume, literature 32-37])
mol = load / 0.04401
dv = mol * 35e-6
print(f'  volume added to the disposal stream: {dv*100:.1f}% (pressure impact ~ that fraction of today\'s SWD pressure build-up)')
print(f'  brine per tonne CO2: {1000/load:.0f} m3 = {1000/load/BBL:.0f} bbl')
e_comp_real = comp_floor_gj(1.5, 55) / 0.65   # [assume] 65% isothermal efficiency
e_pump = (1000 / load) * 5.0e6 / 0.75 / 1e9   # [assume] if brine must be raised by 50 bar at surface
print(f'  energy: CO2 compression 1.5->55 bar real ~{e_comp_real:.2f} GJ/t; extra brine pumping if surface mixing '
      f'{e_pump:.2f} GJ/t; total {e_comp_real:.2f}-{e_comp_real+e_pump:.2f} GJ/t vs dense-phase 1->150 bar real '
      f'~{comp_floor_gj(1,150)/0.65:.2f} GJ/t')
print(f'  electricity cost at $60/MWh: {energy_cost_floor(e_comp_real,60):.0f}-{energy_cost_floor(e_comp_real+e_pump,60):.0f} $/t')
kw = e_comp_real * 1e9 * per_well / 3.156e7 / 1e3
for capex_kw in (2000, 4000):            # [assume] small reciprocating CO2 compressor installed $/kW
    for workover in (0.5e6, 1.0e6):       # [assume] CRA/lined tubing + sparger workover per SWD well
        crf = 0.10
        capex_t = (kw * capex_kw + workover) * crf / per_well
        print(f'  per-well compressor {kw:.0f} kW at ${capex_kw}/kW + ${workover/1e6:.1f}M workover: capex ${capex_t:.0f}/t; '
              f'+ energy ${energy_cost_floor(e_comp_real,60):.0f}/t + MRV $3-8/t [assume] -> '
              f'${capex_t+energy_cost_floor(e_comp_real,60)+3:.0f}-{capex_t+energy_cost_floor(e_comp_real,60)+8:.0f}/t')

# ---------------------------------------------------------------- IDEA 2: lithium-brine voidage swap
hdr('IDEA 2: Smackover lithium/bromine brine production as pressure relief for CO2 storage (voidage swap)')
for (T, P) in [(100, 250), (115, 280), (130, 320)]:  # [assume] Smackover 2.3-3 km, hydrostatic brine gradient
    rho = co2_density(T, P)
    print(f'  CO2 density at {T} C, {P} bar: {rho:.0f} kg/m3 -> reservoir voidage {1000/rho:.2f} m3 per t CO2')
rho = co2_density(115, 280)
vt = 1000 / rho
for li in (150, 250, 400):          # [src] USGS (Knierim 2024): >400 mg/L observed in S. Arkansas Smackover
    for rec in (0.8,):
        li_kg = vt * li / 1000 * rec
        lce = li_kg * 5.323
        print(f'  Li {li} mg/L, {rec:.0%} recovery: {li_kg:.2f} kg Li = {lce:.2f} kg LCE per t CO2 of voidage; '
              f'value ${lce*8:.0f}-{lce*20:.0f}/t CO2 at $8-20k/t LCE; t CO2 per t LCE = {1000/lce:.0f}')
# whole-system sizing
for label, lce_tpy, li in [('Three initial Arkansas DLE projects (Malone 2026)', 53100, 300),
                           ('One 25 kt/yr LCE plant', 25000, 400)]:
    brine = lce_tpy / 5.323 / (li / 1e6 * 0.8) / 1000  # t Li / (t Li per m3) -> m3; li mg/L = g/m3
    brine_m3 = (lce_tpy / 5.323 * 1e6) / (li * 0.8)     # g Li / (g/m3)
    co2 = brine_m3 / vt / 1e6
    print(f'  {label}: brine {brine_m3/1e6:.1f} Mm3/yr ({brine_m3/BBL/365/1e3:.0f} kbbl/d) -> voidage-matched CO2 '
          f'{co2:.1f} Mt/yr')
# USGS: 5,000 t dissolved Li brought to surface in 2022 by oil, gas and bromine industries
for li in (200, 350):
    brine_m3 = 5000e6 / li
    print(f'  2022 existing Smackover brine handling (5,000 t Li at {li} mg/L): {brine_m3/1e6:.0f} Mm3/yr -> '
          f'{brine_m3/vt/1e6:.0f} Mt CO2/yr of voidage if CO2 replaced spent-brine reinjection')
# spent brine must go elsewhere (shallower disposal)
for usd_bbl in (0.5, 1.0):
    print(f'  spent-brine disposal elsewhere at ${usd_bbl}/bbl: ${vt/BBL*usd_bbl:.1f}/t CO2')
heat = vt * 1000 * 3.5e3 * (115 - 60) / 1e9     # [assume] cp 3.5 kJ/kgK brine, cooled 115->60 C
print(f'  side check (map open problem "storage + geothermal from produced brine"): heat in voidage brine '
      f'{heat:.2f} GJ_th/t CO2; at 10% binary efficiency {heat*0.1/0.0036:.0f} kWh_e/t vs compression ~120 kWh/t '
      f'-> geothermal co-product is minor')

# ---------------------------------------------------------------- IDEA 3: fracture-stimulated mineralization doublets
hdr('IDEA 3: multistage-fractured horizontal doublets for in-situ mineralization of olivine-rich rock')
# Palandri & Kharaka (2004) forsterite: acid log k25 = -6.85, Ea 67.2 kJ/mol, n=0.47; neutral -10.64, Ea 79.0
def forsterite_rate(T_C, pH):
    T = T_C + 273.15
    f = lambda Ea: math.exp(-Ea / 8.314 * (1 / T - 1 / 298.15))
    return 10 ** -6.85 * f(67200) * (10 ** -pH) ** 0.47 + 10 ** -10.64 * f(79000)
mol_fo_per_t = 1e6 / 44.01 / 2     # 2 CO2 per Mg2SiO4 if all Mg -> MgCO3 (upper bound)
print(f'  stoichiometry: {mol_fo_per_t*0.1407/1e3:.2f} t forsterite per t CO2 (max)')
target = 0.1e6  # [assume] t CO2/yr per doublet (1/7 of a sandstone injector)
mol_s = target * mol_fo_per_t / 3.156e7
lat, stages, xf, h = 2000, 40, 100, 50   # [assume] Fervo-like: 2 km lateral, 40 stages, 100 m half-length, 50 m height
geo_area = stages * 2 * xf * h * 2       # two wings, two faces each
print(f'  geometric fracture-face area per well: {geo_area:.2e} m2')
for T, pH in [(40, 5.0), (60, 5.0), (90, 5.0), (90, 4.0), (150, 5.0)]:
    r = forsterite_rate(T, pH)
    need = mol_s / r
    print(f'  {T:>3} C pH {pH}: rate {r:.1e} mol/m2/s -> reactive area for 0.1 Mt/yr {need:.1e} m2 = '
          f'{need/geo_area:.0f}x geometric face area; at 1e4 m2/m3 grain surface, wall-rock depth needed '
          f'{need/(geo_area*1e4)*100:.1f} cm')
rock_m3 = target * mol_fo_per_t * 0.1407 / 1e3 / 3.3 / 0.7   # [assume] 70% olivine rock, 3.3 t/m3
print(f'  rock consumed per 0.1 Mt/yr: {rock_m3:.0f} m3/yr -> reaction front {rock_m3/geo_area*100:.1f} cm/yr into each face')
for m in (0.6, 0.9):
    w = 1 / (m * 0.04401)
    print(f'  carrier water at {m} mol/kg: {w:.0f} t water per t CO2; per 0.1 Mt/yr doublet {w*target/365/1e3:.1f} kt/d '
          f'(= {w*target/365/BBL/1e3:.0f} kbbl/d, recirculated in a closed loop)')
for dp in (5, 10):
    e = (1 / (0.8 * 0.04401)) * dp * 1e6 / 0.75 / 1e9
    print(f'  circulation pump energy at {dp} MPa loop pressure drop: {e:.2f} GJ/t; plus CO2 compression to ~60 bar '
          f'~{comp_floor_gj(1,60)/0.65:.2f} GJ/t')

# ---------------------------------------------------------------- IDEA 4: EGS heat-not-power
hdr('IDEA 4: horizontal-EGS doublets sold as industrial steam/heat instead of electricity')
capex_kwe = 7000; mwe = 50   # [src] Fervo S-1/A: ~$7,000/kW for a 50 MW GeoBlock (2025 est.)
eff = 0.12                    # [assume] binary/flash net efficiency
wellfield_share = (0.55, 0.70)  # [assume]
mwth = mwe / eff
crf = 0.08 * 1.08 ** 25 / (1.08 ** 25 - 1)
for ws in wellfield_share:
    capex_th = capex_kwe * mwe * 1e3 * ws / (mwth * 1e3)       # $/kWth wellfield
    capex_th_total = capex_th + 100                              # [assume] +$100/kWth heat exchangers/steam
    usd_gj = capex_th_total * crf / (8000 * 3.6e-3) + 1.0        # [assume] 8,000 h; +$1/GJ O&M
    print(f'  wellfield share {ws:.0%}: {capex_th_total:.0f} $/kWth -> heat ~${usd_gj:.1f}/GJ (Fervo-site, high gradient)')
for depth_mult in (2, 3):
    print(f'  normal-gradient site, drilling cost x{depth_mult}: heat ~${(capex_kwe*mwe*1e3*0.65/(mwth*1e3)*depth_mult+100)*crf/(8000*3.6e-3)+1.0:.1f}/GJ')
for hh in (3.5, 11.0):
    gas_steam = hh / 1.055 / 0.85
    print(f'  gas boiler steam at ${hh}/MMBtu: ${gas_steam:.1f}/GJ steam; CO2 {56.1/0.85:.0f} kg/GJ steam')
print(f'  heat-vs-power per doublet: Fervo Project Red-like flow 60 kg/s, 190->70 C: '
      f'{60*4.2*(190-70)/1e3:.0f} MWth vs ~{60*4.2*(190-70)/1e3*eff:.1f} MWe')
mwth_field = 100
gj = mwth_field * 8000 * 3.6
print(f'  100 MWth heat field at 8,000 h: {gj/1e6:.2f} PJ/yr -> {gj*56.1/0.85/1e6/1e3:.2f} Mt CO2/yr avoided vs gas steam')
for gjt in (2.5, 3.5):
    for usd in (3, 8):
        print(f'  amine reboiler duty {gjt} GJ/t at ${usd}/GJ geothermal heat: ${gjt*usd:.0f}/t CO2 (no fuel CO2)')
carnot = lambda Tc: 1 - 298.15 / (Tc + 273.15)
print(f'  exergy factor: 150 C {carnot(150):.2f}, 120 C {carnot(120):.2f}, 100 C {carnot(100):.2f}')

# ---------------------------------------------------------------- IDEA 5: reverse-auction retirement of marginal wells
hdr('IDEA 5: reverse-auction buyout + plugging of high-emitting low-production well sites')
sites = 565000; tg = 4.0     # [src] Omara et al. 2022 Nat Commun: 565,000 sites, 4 (3-6) Tg CH4/yr, 2019, modelled from n=240
mean_t = tg * 1e6 / sites
print(f'  mean emission {mean_t:.1f} t CH4/site/yr = {mean_t*1e3/8760:.2f} kg/h (paper: 0.8) = '
      f'{mean_t*GWP100["CH4_fossil"]:.0f} t CO2e/yr GWP100')
# production per site: 5.6% of US O&G output 2019 [src]; US 2019 ~12.3 mb/d oil + ~93 bcf/d dry gas [assume ~15.5 mboe/d]
boe_site = 0.056 * (12.3e6 + 15.5e6) / sites
print(f'  production per site ~{boe_site:.1f} boe/d; CH4 loss rate >10% (paper)')
for top_frac, share in [(0.10, 0.4), (0.10, 0.6), (1.0, 1.0)]:
    n = sites * top_frac
    cut = tg * share
    for cost in (50e3, 150e3):   # [assume] buyout (forgone net cash flow) + plugging, $ per site
        yrs = 10
        usd_t = n * cost / (cut * 1e6 * GWP100['CH4_fossil'] * yrs)
        print(f'  retire top {top_frac:.0%} sites holding {share:.0%} of emissions, ${cost/1e3:.0f}k/site, {yrs} yr credit: '
              f'{cut:.1f} Tg CH4/yr = {cut*GWP100["CH4_fossil"]:.0f} Mt CO2e/yr; ${usd_t:.0f}/t CO2e (GWP100), '
              f'${usd_t*GWP100["CH4_fossil"]/GWP20["CH4_fossil"]:.0f}/t (GWP20); program ${n*cost/1e9:.1f}bn; '
              f'output lost {n*boe_site/1e3:.0f} kboe/d')
# compare with orphan-well plugging (Townsend-Small & Hoschouer 2021, Permian: mean 6.2 g/h over 37 wells)
orphan_t = 6.2 * 8760 / 1e6
for cost in (30e3, 76e3):
    print(f'  orphan/shut-in well at 6.2 g/h: {orphan_t*GWP100["CH4_fossil"]:.2f} t CO2e/yr; plugging ${cost/1e3:.0f}k over 30 yr '
          f'-> ${cost/(orphan_t*GWP100["CH4_fossil"]*30):.0f}/t CO2e (methane only; ignores brine/groundwater benefits)')

# ---------------------------------------------------------------- IDEA 6: retire-and-store covenant
hdr('IDEA 6: dedicated storage in depleted oil fields with permanently extinguished hydrocarbon rights')
for bbl_per_t in (2.0, 3.0):   # [assume] net CO2-EOR utilisation ~0.33-0.5 t CO2 per incremental bbl
    for margin in (15, 25):     # [assume] $/bbl operator netback on incremental EOR oil
        print(f'  forgone EOR margin {bbl_per_t} bbl/t x ${margin}/bbl = ${bbl_per_t*margin:.0f}/t CO2; '
              f'as share of 45Q point-source $85: {bbl_per_t*margin/85:.0%}; of $500/t DAC credit: {bbl_per_t*margin/500:.0%}')
for bbl_per_t in (2.0, 3.0):
    gross = bbl_per_t * 0.43     # [assume] ~0.43 t CO2 per bbl combusted
    for leak in (0.5, 0.8):      # [assume] fraction of retired barrels replaced by other supply
        print(f'  EOR oil emissions avoided per t stored: {gross:.2f} t gross; net of {leak:.0%} market replacement '
              f'{gross*(1-leak):.2f} t')
