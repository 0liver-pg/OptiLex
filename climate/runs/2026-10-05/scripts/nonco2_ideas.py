"""Verifier checks for six non-CO2-first ideas (atmospheric chemist generator).

Run: cd . && .venv/bin/python <this file>
All inputs marked ASSUMED are my assumptions; others are from the verified map or standard thermochemistry.
"""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

M_HFC23 = 0.07002   # kg/mol CHF3
M_VDF = 0.06404     # kg/mol CH2=CF2
M_PHENOL = 0.09411
M_BENZENE = 0.07811
M_AA = 0.14614      # adipic acid
M_HNO3 = 0.06301
M_AN = 0.08004      # NH4NO3
GWP100_HFC23 = 14600   # AR6
GWP100_N2O = GWP100['N2O']
GWP_CH4_F = GWP100['CH4_fossil']; GWP_CH4_B = GWP100['CH4_biogenic']
LHV_CH4 = 50.0  # GJ/t

def hdr(s):
    print('\n' + '=' * 90 + '\n' + s + '\n' + '=' * 90)

# ---------------------------------------------------------------- 0. baseline reminder
hdr('0. Baseline: ambient methane processing is energy-expensive (verifier)')
amb = fan_work_gj_per_tonne(1.93e-6, 0.5, 100, molar_mass=M_CH4)
print(f'Ambient CH4 (1.93 ppm, 50% removal, 100 Pa): fan work {amb:,.0f} GJ/t CH4 = {amb/GWP_CH4_F:.2f} GJ/t CO2e (GWP100)')
print('All six ideas below act on concentrated streams or passive fluxes; none processes ambient air.')

# ---------------------------------------------------------------- 1. AlphOx loop
hdr('1. Adipic-acid off-gas N2O as oxidant: benzene + N2O -> phenol + N2 (AlphOx), phenol -> KA oil -> adipic acid')
# Standard gas-phase enthalpies of formation, kJ/mol (NIST WebBook values, rounded)
dHf = {'C6H6': 82.9, 'N2O': 82.05, 'C6H5OH': -96.4, 'N2': 0.0, 'O2': 0.0}
dH_alphox = dHf['C6H5OH'] + dHf['N2'] - dHf['C6H6'] - dHf['N2O']
dH_decomp = dHf['N2'] + 0.5 * dHf['O2'] - dHf['N2O']
print(f'dH AlphOx  = {dH_alphox:.0f} kJ/mol N2O (exothermic; N2O oxygen goes into product)')
print(f'dH N2O decomposition = {dH_decomp:.0f} kJ/mol N2O (destruction route; oxidant wasted)')
# N2O per t adipic acid (IPCC default ~300 kg/t) -> mol ratio
n2o_per_aa = 0.300
mol_ratio = (n2o_per_aa / M_N2O) / (1 / M_AA)
print(f'IPCC default 0.30 t N2O/t AA = {mol_ratio:.2f} mol N2O per mol AA -> phenol from own N2O can supply '
      f'{mol_ratio:.0%} of the KA-oil (C6) feed stoichiometrically (1 phenol -> 1 cyclohexanone -> 1 AA)')
phenol_per_t_n2o = M_PHENOL / M_N2O
benzene_per_t_phenol = M_BENZENE / M_PHENOL
print(f'Phenol per t N2O (100% selectivity) = {phenol_per_t_n2o:.2f} t; benzene per t phenol = {benzene_per_t_phenol:.2f} t')
# Prices ASSUMED (China 2024-26 order of magnitude; to be checked): phenol $950-1150/t, benzene $800-950/t
for ph, bz, sel, capex_per_tpa, crf in [(950, 950, 0.85, 1200, 0.12), (1050, 875, 0.90, 1000, 0.10), (1150, 800, 0.95, 800, 0.10)]:
    gross_per_t_phenol = ph - bz * benzene_per_t_phenol / 0.97  # 97% benzene selectivity ASSUMED
    cap = capex_per_tpa * crf
    opex = 60  # $/t phenol utilities+labour+catalyst ASSUMED
    net = gross_per_t_phenol - cap - opex
    per_t_n2o = net * phenol_per_t_n2o * sel
    print(f'phenol ${ph}, benzene ${bz}, N2O->phenol selectivity {sel:.0%}, capex ${capex_per_tpa}/tpa: '
          f'net ${net:,.0f}/t phenol = ${per_t_n2o:,.0f}/t N2O = ${per_t_n2o/GWP100_N2O:,.2f}/t CO2e')
dest_lo, dest_hi = 0.25, 4.0
print(f'Thermal/catalytic destruction cost (NRDC 2026): ${dest_lo}-{dest_hi}/t CO2e = ${dest_lo*GWP100_N2O:,.0f}-{dest_hi*GWP100_N2O:,.0f}/t N2O')
china_n2o_mt = 76 / 265  # map: ~76 Mt CO2e AR5 (GWP 265)
print(f'China adipic N2O (map, 76 Mt CO2e AR5) = {china_n2o_mt:.2f} Mt N2O = {china_n2o_mt*GWP100_N2O:.0f} Mt CO2e (AR6) '
      f'-> phenol {china_n2o_mt*phenol_per_t_n2o*0.9:.2f} Mt/yr at 90% selectivity')
# heat released, useful for steam
heat = -dH_alphox * 1e3 / M_N2O / 1e6
print(f'Reaction heat {heat:.1f} GJ per t N2O converted (recoverable as steam)')

# ---------------------------------------------------------------- 2. CBAM marginal value of N2O abatement
hdr('2. CBAM: marginal value of N2O abatement at non-EU nitric-acid plants exporting nitrate fertiliser')
hno3_per_an = M_HNO3 / M_AN
print(f'HNO3 per t ammonium nitrate = {hno3_per_an:.3f} t')
gwp_ets = 265  # EU ETS uses AR5 for N2O since 2021 (ASSUMED; AR6 273 gives +3%)
for ef_unab in (5, 7, 9):           # kg N2O/t HNO3, IPCC 2006 defaults by pressure class
    ef_ab = 0.5                     # kg N2O/t HNO3 with secondary+tertiary catalyst (ASSUMED, EU BAT-range)
    d_co2e_hno3 = (ef_unab - ef_ab) * gwp_ets / 1000
    d_co2e_an = d_co2e_hno3 * hno3_per_an
    for eua in (70, 85):
        print(f'EF {ef_unab} -> {ef_ab} kg/t HNO3: avoid {d_co2e_hno3:.2f} t CO2e/t HNO3 = {d_co2e_an:.2f} t/t AN; '
              f'marginal CBAM saving at EUR{eua}/t = EUR{d_co2e_an*eua:,.0f}/t AN')
ab_cost_an = [c * (7 - 0.5) * gwp_ets / 1000 * hno3_per_an for c in (0.25, 4.0)]
print(f'Abatement cost at $0.25-4/t CO2e = ${ab_cost_an[0]:.2f}-{ab_cost_an[1]:.2f}/t AN (EF 7 -> 0.5)')
print('Contrast: proportional 2.5% reading (map) would give 2.5% x EUR70-85 = EUR1.8-2.1/t CO2e in 2026;'
      ' benchmark-based reading gives full EUA on emissions above the benchmark.')
plant_tpd = 1000
plant_t = plant_tpd * 330
n2o = plant_t * 7 / 1000
print(f'One {plant_tpd} t/d HNO3 plant (330 d) unabated at 7 kg/t: {n2o:,.0f} t N2O = {n2o*GWP100_N2O/1e6:.2f} Mt CO2e/yr (AR6)')
for share in (0.2, 0.5):
    sav = n2o * (6.5 / 7) * gwp_ets * share * 75
    print(f'  if {share:.0%} of output ships to EU as nitrate fertiliser: CBAM saving ~EUR{sav/1e6:.1f}M/yr at EUR75; '
          f'abatement cost ${n2o*(6.5/7)*GWP100_N2O*0.25/1e6:.2f}-{n2o*(6.5/7)*GWP100_N2O*4/1e6:.1f}M/yr for the WHOLE plant')

# ---------------------------------------------------------------- 3. VAM as combustion air
hdr('3. Ventilation-air methane piped into co-located boiler / kiln combustion air')
for x in (0.002, 0.004, 0.007):
    for dp in (500, 1500):
        fw = fan_work_gj_per_tonne(x, 0.98, dp, fan_efficiency=0.7, molar_mass=M_CH4)
        print(f'VAM {x*100:.1f}% CH4, 98% burnout, extra duct dp {dp} Pa: incremental fan work {fw:.2f} GJ/t CH4 '
              f'= {fw/LHV_CH4:.1%} of the CH4 heating value; {fw/GWP_CH4_F*1000:.1f} MJ/t CO2e')
# heat needed by an RTO vs boiler (verify map's autothermal point): adiabatic rise
cp_air = 1.03e-3  # GJ/(t K)
for x in (0.002, 0.004):
    mass_frac = x * M_CH4 / (0.02897)
    dT = mass_frac * LHV_CH4 / cp_air
    print(f'{x*100:.1f}% CH4 adiabatic temperature rise in air = {dT:.0f} K (needs regenerator >~95% in an RTO; '
          f'a boiler flame needs none)')
# boiler air demand and VAM absorption capacity
air_m3_per_gj_coal = 300.0  # ASSUMED: ~9.5 t air/t coal at 25 GJ/t, 1.27 kg/m3
for mwth in (300, 1500):
    air = mwth * 1e-3 * air_m3_per_gj_coal  # m3/s (MW = 1e-3 GJ/s)
    for x in (0.003, 0.005):
        ch4_heat = air * x * 0.668e-3 * LHV_CH4 / (mwth * 1e-3)  # share of heat input
        print(f'{mwth} MWth boiler draws ~{air:,.0f} m3/s air; at {x*100:.1f}% CH4 VAM supplies {ch4_heat:.1%} of heat input')
shaft = 300.0  # m3/s, ASSUMED typical large shaft
for x in (0.003, 0.006):
    t_ch4 = shaft * x * 0.668e-3 * 3.156e7 * 0.98
    print(f'One {shaft:.0f} m3/s shaft at {x*100:.1f}%: {t_ch4:,.0f} t CH4/yr destroyed = {t_ch4*GWP_CH4_F/1e6:.2f} Mt CO2e (GWP100), '
          f'{t_ch4*GWP20["CH4_fossil"]/1e6:.2f} Mt (GWP20); fuel {t_ch4*LHV_CH4/1e6:.2f} PJ = ${t_ch4*LHV_CH4*4/1e6:.1f}M/yr at $4/GJ coal')
fanpow = shaft * 1000 / 0.7 / 1e6
print(f'Incremental fan power at 1000 Pa: {fanpow:.2f} MW')
for capex in (8e6, 20e6):
    ann = capex * 0.11
    t = shaft * 0.004 * 0.668e-3 * 3.156e7 * 0.98 * 0.85  # 85% boiler availability
    fuel = t * LHV_CH4 * 4
    print(f'Duct+safety capex ${capex/1e6:.0f}M (CRF 11%): ${ann/1e6:.1f}M/yr vs fuel value ${fuel/1e6:.1f}M/yr -> '
          f'net ${(ann-fuel)/ (t*GWP_CH4_F):.2f}/t CO2e (negative = profit), at 0.4% CH4 and 85% availability')
print('Compare RTO (map, MATEC 2025 design): EUR8.5-9.8/t CO2e GWP100 with no product value')

# ---------------------------------------------------------------- 4. Methane slip default design
hdr('4. Marine methane slip: conservative default + measured opt-in (FuelEU / IMO)')
gwp_fueleu = 25  # FuelEU Annex uses AR4-style GWP100 for CH4 (ASSUMED from memory)
lcv = 49.1  # MJ/kg LNG
cf_co2 = 2.750  # g CO2/g LNG
wtt = 18.5  # gCO2e/MJ, ASSUMED FuelEU LNG default
def ghgie(slip):
    ttw = ((1 - slip) * cf_co2 + slip * gwp_fueleu) / (lcv / 1000)  # gCO2e per MJ
    return wtt + ttw
for s in (0.002, 0.0135, 0.031, 0.064):
    print(f'slip {s*100:.2f}% of fuel -> WtW ~{ghgie(s):.1f} gCO2e/MJ (approx, combustion CH4/N2O omitted)')
pen = lambda g: 2400 * 1e6 / (g * 41000)
print(f'FuelEU penalty-equivalent value of 1 t CO2e of surplus at GHGIE 85-90: EUR{pen(90):.0f}-{pen(85):.0f}/t CO2e')
lng = 30000  # t/yr, ASSUMED large cruise ship
for actual in (0.0135, 0.064):
    d = (0.031 - actual) * lng
    print(f'{lng:,} t LNG/yr ship, actual slip {actual*100:.2f}% vs default 3.1%: accounting gap {d:,.0f} t CH4 = '
          f'{d*gwp_fueleu:,.0f} t CO2e (FuelEU GWP) -> worth EUR{abs(d)*gwp_fueleu*200/1e6:.1f}-{abs(d)*gwp_fueleu*pen(88)/1e6:.1f}M/yr '
          f'at EUR200 pool price .. penalty level; sign {"surplus (opt-in)" if d > 0 else "deficit (stays on default)"}')
# fleet scale, ASSUMED gas burned in marine engines 15-25 Mt/yr
for gas in (15, 25):
    for s in (0.03, 0.06):
        ch4 = gas * s
        print(f'Marine gas {gas} Mt/yr x slip {s:.0%} = {ch4:.2f} Mt CH4 = {ch4*GWP_CH4_F:.0f} Mt CO2e (GWP100), {ch4*GWP20["CH4_fossil"]:.0f} Mt (GWP20)')
print('Load-management physics: unburned CH4 rises at low load; the preprint (2026) reports 1.95 g/kWh at 60-90% load and an '
      'annual ELM slip coefficient of ~1.35% on a new-generation DF engine.')
sfc = 160  # g LNG/kWh ASSUMED at 75% load
print(f'1.95 g/kWh at ~{sfc} g LNG/kWh = {1.95/sfc:.2%} of fuel (consistent with the 1.35% annual coefficient)')

# ---------------------------------------------------------------- 5. Dumpsite compost biocover
hdr('5. Open-dump compost biocover (passive methanotroph oxidation) with satellite-verified payment')
for flux_g_m2_d, eff, cost_m2, life in [(50, 0.4, 25, 5), (150, 0.6, 15, 7), (300, 0.7, 10, 8)]:
    ox = flux_g_m2_d * 365 * eff / 1e6  # t CH4/m2/yr
    co2e = ox * GWP_CH4_B
    usd = cost_m2 / (co2e * life)
    print(f'flux {flux_g_m2_d} g/m2/d, {eff:.0%} oxidised, ${cost_m2}/m2, {life} yr: {ox*1e3:.1f} kg CH4/m2/yr = '
          f'{co2e:.2f} t CO2e/m2/yr -> ${usd:.2f}/t CO2e (GWP100 biogenic; ${usd*GWP_CH4_B/GWP20["CH4_biogenic"]:.2f} GWP20)')
site_t_h = 3.0  # t CH4/h ASSUMED large satellite-visible dump
area_ha = 40
flux = site_t_h * 1e6 * 24 / (area_ha * 1e4)
print(f'Example: {site_t_h} t/h over {area_ha} ha = {flux:.0f} g CH4/m2/d average (hotspots higher)')
for eff in (0.3, 0.6):
    t = site_t_h * 8760 * eff
    print(f'  {eff:.0%} oxidised -> {t:,.0f} t CH4/yr = {t*GWP_CH4_B/1e6:.2f} Mt CO2e/yr GWP100')
print(f'Fan work: zero (landfill gas pressure + diffusion). For contrast, processing ambient air: {amb:,.0f} GJ/t CH4.')
det = 0.1  # t/h, ASSUMED point-source imager detection threshold ~100 kg/h
print(f'Satellite check: a {site_t_h} t/h site is {site_t_h/det:.0f}x a ~100 kg/h point-source detection limit; '
      f'a 30% cut ({site_t_h*0.3:.1f} t/h) exceeds it {site_t_h*0.3/det:.0f}x, but single-overpass plume error is often +/-30-50%.')
# N2O side effect from compost covers (ASSUMED up to 1% of oxidised-CH4 CO2e as N2O)
print('N2O penalty to check: if a cover emitted 0.1 g N2O/m2/d it would offset '
      f'{0.1*365*GWP100_N2O/1e6:.3f} t CO2e/m2/yr vs {150*365*0.6/1e6*GWP_CH4_B:.2f} gained in the mid case.')

# ---------------------------------------------------------------- 6. HFC-23 -> VDF
hdr('6. HFC-23 by-product converted with CH4 to vinylidene fluoride (PVDF monomer)')
dHf6 = {'CHF3': -697.0, 'CH4': -74.6, 'VDF': -345.2, 'HF': -273.3, 'H2': 0.0}
dH6 = dHf6['VDF'] + dHf6['HF'] + dHf6['H2'] - dHf6['CHF3'] - dHf6['CH4']
print(f'dH CHF3 + CH4 -> CH2=CF2 + HF + H2 = {dH6:+.0f} kJ/mol (endothermic)')
e_t = dH6 * 1e3 / M_HFC23 / 1e6
print(f'Reaction enthalpy {e_t:.2f} GJ/t HFC-23 = {e_t/GWP100_HFC23*1e6:.0f} kJ/t CO2e abated -> energy is irrelevant at GWP 14,600')
vdf_per_t = M_VDF / M_HFC23
for sel, price in ((0.4, 3000), (0.6, 5000), (0.8, 7000)):
    rev = vdf_per_t * sel * price
    print(f'VDF selectivity {sel:.0%}, VDF ${price}/t: revenue ${rev:,.0f}/t HFC-23 = ${rev/GWP100_HFC23:.3f}/t CO2e')
excess = 14.0  # Gg/yr measured 2023 (map)
print(f'Measured HFC-23 {excess} kt/yr = {excess*GWP100_HFC23/1e3:.0f} Mt CO2e; as VDF at 60% selectivity '
      f'{excess*vdf_per_t*0.6:.1f} kt/yr VDF')
print('HCFC-22 plant co-produces ~1.5-4% HFC-23 (ASSUMED literature range); a 100 kt/yr HCFC-22 plant -> 1.5-4 kt HFC-23 '
      f'= {1.5*GWP100_HFC23/1e3:.0f}-{4*GWP100_HFC23/1e3:.0f} Mt CO2e/yr')
