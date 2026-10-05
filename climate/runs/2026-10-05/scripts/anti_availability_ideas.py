"""Executed checks for six anti-availability climate ideas (OptiLex idea engine, 2026-10-05).

Every number printed here is either stoichiometry, the OptiLex physics verifier, or an
explicitly labelled ASSUMPTION. Run:
  cd . && .venv/bin/python <this file>
"""
import math
import sys

import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, 'climate')
from physics import *  # noqa: F401,F403

R_ = 8.314462618


def hdr(t):
    print('\n' + '=' * 78 + '\n' + t + '\n' + '=' * 78)


# ---------------------------------------------------------------------------------
hdr('IDEA 1  Super-pollutant default factors in product footprints (PA66 N2O, PTFE HFC-23)')
M_AA, M_N2O_, M_PA66 = 146.14, 44.013, 226.32      # g/mol: adipic acid, N2O, PA66 repeat unit
M_HCFC22, M_TFE, M_HFC23 = 86.47, 100.02, 70.01
GWP_HFC23 = 14_600  # AR6 GWP100
n2o_per_aa = M_N2O_ / M_AA                          # 1 mol N2O per mol AA (stoichiometric, IPCC default 0.300 t/t)
co2e_per_aa = n2o_per_aa * GWP100['N2O']
aa_per_pa66 = M_AA / M_PA66
co2e_per_pa66 = aa_per_pa66 * co2e_per_aa
print(f'N2O per t adipic acid (1:1 molar): {n2o_per_aa:.3f} t  -> {co2e_per_aa:.1f} t CO2e (GWP100 273)')
print(f'Adipic acid per t PA66: {aa_per_pa66:.3f} t -> unabated by-product N2O = {co2e_per_pa66:.1f} t CO2e per t PA66')
for typical in (6.5, 8.0):  # ASSUMPTION: abated cradle-to-gate PA66 PCF, kg CO2e/kg (eco-profile order of magnitude)
    print(f'  vs an abated PA66 footprint of {typical} t CO2e/t: unabated adds {co2e_per_pa66/typical:.1f}x')
for usd_t in (0.25, 1.0, 4.0):   # NRDC 2026 abatement cost range, $/t CO2e (map)
    cost = 0.95 * co2e_per_pa66 * usd_t
    print(f'  abating 95% at ${usd_t}/t CO2e costs ${cost:,.0f} per t PA66 '
          f'= {cost/2000:.1%}-{cost/3500:.1%} of a $2,000-3,500/t price (price ASSUMED)')
for kg_car in (3, 8):  # ASSUMPTION: PA66 per light vehicle
    print(f'  per car with {kg_car} kg PA66: unabated N2O = {kg_car*co2e_per_pa66:,.0f} kg CO2e; '
          f'abatement cost ${kg_car/1000*0.95*co2e_per_pa66*1:.2f}-{kg_car/1000*0.95*co2e_per_pa66*4:.2f}')
# PTFE: 2 CHClF2 -> C2F4 + 2 HCl
hcfc_per_tfe_stoich = 2 * M_HCFC22 / M_TFE
for yld in (1.0, 0.9):
    hcfc = hcfc_per_tfe_stoich / yld
    for w in (0.015, 0.03, 0.04):   # HFC-23 generation as mass fraction of HCFC-22 (IPCC-style 1.5-4% range)
        hfc23 = hcfc * w * 1000
        print(f'  PTFE: yield {yld:.0%}, HFC-23 rate {w:.1%}: {hcfc:.2f} t HCFC-22 -> {hfc23:.0f} kg HFC-23 '
              f'= {hfc23*GWP_HFC23/1000:,.0f} t CO2e per t PTFE')
# destruction cost per kg HFC-23 from a CDM-style incinerator (ASSUMPTIONS: $10M capex, 10%/10yr CRF, $0.5M/yr opex, 350 t/yr)
crf = 0.10 / (1 - 1.10 ** -10)
per_kg = (10e6 * crf + 0.5e6) / 350e3
print(f'Incinerator cost ~${per_kg:.1f}/kg HFC-23 = ${per_kg/GWP_HFC23*1000:.2f}/t CO2e '
      f'-> ${per_kg*28:.0f}-{per_kg*77:.0f} per t PTFE')
hfc23_gap_gg = 14.0 - 41e6 / GWP_HFC23 / 1e3   # measured 14.0 Gg (2023) minus ~41 Mt CO2e reported (map)
print(f'HFC-23 measured-minus-reported gap: {hfc23_gap_gg:.1f} Gg = {hfc23_gap_gg*GWP_HFC23/1e3:.0f} Mt CO2e/yr')
china_aa_n2o_mt = 76 / 265            # map: ~76 Mt CO2e at AR5 GWP 265
print(f'China adipic N2O: {china_aa_n2o_mt:.3f} Mt N2O = {china_aa_n2o_mt*273:.0f} Mt CO2e (AR6) '
      f'= {china_aa_n2o_mt/n2o_per_aa:.2f} Mt/yr of fully unabated adipic acid equivalent')
total = hfc23_gap_gg * GWP_HFC23 / 1e3 + china_aa_n2o_mt * 273
hfc_cost = hfc23_gap_gg * 1e6 * per_kg / 1e6      # $M/yr to destroy the gap
print(f'Destroying the HFC-23 gap at ${per_kg:.1f}/kg: ${hfc_cost:.0f}M/yr (x0.5-x2 range: ${hfc_cost*0.5:.0f}-{hfc_cost*2:.0f}M)')
cost_lo = hfc_cost * 0.5 + 19
cost_hi = hfc_cost * 2 + 304
print(f'Combined addressable: ~{total:.0f} Mt CO2e/yr for ~${cost_lo:.0f}-{cost_hi:.0f}M/yr '
      f'(=${cost_lo/total:.2f}-{cost_hi/total:.2f}/t); same tonnage by DAC at $400/t = ${total*0.4:.0f}bn/yr')

# ---------------------------------------------------------------------------------
hdr('IDEA 2  CO2 as the voidage-replacement fluid in Smackover lithium/bromine brine fields')


def pr_density_co2(P_pa, T_k):
    """Peng-Robinson CO2 density, kg/m3 (approx, +/- ~5-10% in the dense supercritical region)."""
    Tc, Pc, w = 304.13, 7.3773e6, 0.2239
    a = 0.45724 * R_**2 * Tc**2 / Pc
    b = 0.07780 * R_ * Tc / Pc
    k = 0.37464 + 1.54226 * w - 0.26992 * w**2
    alpha = (1 + k * (1 - math.sqrt(T_k / Tc)))**2
    A = a * alpha * P_pa / (R_ * T_k)**2
    B = b * P_pa / (R_ * T_k)
    roots = np.roots([1, -(1 - B), A - 3 * B**2 - 2 * B, -(A * B - B**2 - B**3)])
    Z = min(r.real for r in roots if abs(r.imag) < 1e-9 and r.real > B)
    return P_pa * M_CO2 / (Z * R_ * T_k)


# Peneloux-free PR underpredicts liquid-like density; check against a known point
print(f'PR check: CO2 at 15 MPa, 35 C = {pr_density_co2(15e6, 308.15):.0f} kg/m3 (NIST ~815); '
      f'at 10 MPa, 50 C = {pr_density_co2(10e6, 323.15):.0f} (NIST ~384)')
cases = [(25e6, 383.15), (30e6, 393.15), (33e6, 408.15)]   # ASSUMED Smackover (2.4-3.3 km) P,T
dens = [pr_density_co2(P, T) for P, T in cases]
for (P, T), d in zip(cases, dens):
    print(f'  CO2 at {P/1e6:.0f} MPa, {T-273.15:.0f} C: {d:.0f} kg/m3 -> {d/1000:.2f} t CO2 per m3 of brine voidage')
rho_lo, rho_hi = min(dens), max(dens)
lce_per_li = 5.323
for li_mgL in (200, 400, 582):           # 582 mg/L = 2025 Lafayette Co. average (Wikipedia, Smackover Formation)
    for price in (8, 15, 20):            # ASSUMPTION: $/kg LCE
        rev = li_mgL / 1000 * 0.85 * lce_per_li * price
        print(f'  Li {li_mgL} mg/L, 85% recovery, ${price}/kg LCE: ${rev:5.1f} per m3 brine | '
              f'45Q $85/t on the same voidage: ${85*rho_lo/1000:.0f}-{85*rho_hi/1000:.0f} per m3')
swa_lce = 22_500  # t/yr LCE (SWA project, Wikipedia)
for li_mgL in (400, 582):
    brine = swa_lce / lce_per_li * 1000 / (li_mgL / 1000 * 0.85)   # m3/yr
    print(f'SWA-size project at {li_mgL} mg/L: {brine/1e6:.1f} Mm3/yr brine -> voidage = '
          f'{brine*rho_lo/1e9:.1f}-{brine*rho_hi/1e9:.1f} Mt CO2/yr if fully replaced by CO2')
for disp in (3, 15):  # ASSUMPTION: $/m3 cost to dispose spent brine in a separate saline zone
    print(f'  spent-brine disposal at ${disp}/m3 costs ${disp/(rho_hi/1000):.0f}-{disp/(rho_lo/1000):.0f} per t CO2 stored')
w_comp = R_ * T0 * math.log(300e5 / P0) / M_CO2 / 1e6
print(f'Ideal isothermal compression floor 1->300 bar: {w_comp:.2f} GJ/t (separation floor for ammonia/ethanol CO2 ~0)')
# Dissolved-CO2 variant: CO2 dissolved in the reinjected spent brine (ASSUMED 0.4-0.8 mol/kg solubility in 4-5 m brine)
for sol in (0.4, 0.8):
    print(f'  dissolved variant at {sol} mol/kg: {sol*44.01:.0f} kg CO2 per t brine -> {1000/(sol*44.01):.0f} t brine per t CO2;'
          f' a 10 Mm3/yr reinjection stream (~1.2 t/m3) carries {10e6*1.2*sol*44.01/1e9:.2f} Mt CO2/yr')

# ---------------------------------------------------------------------------------
hdr('IDEA 3  Mine combustion exhaust scrubbed by brucite-bearing tailings slurry (wet-FGD reactor, no capture plant)')
dGf = {'brucite': -833.5, 'CO2g': -394.4, 'magnesite': -1029.5, 'H2Ol': -237.1}   # kJ/mol, standard tables
dHf = {'brucite': -924.5, 'CO2g': -393.5, 'magnesite': -1113.3, 'H2Ol': -285.8}
dG = dGf['magnesite'] + dGf['H2Ol'] - dGf['brucite'] - dGf['CO2g']
dH = dHf['magnesite'] + dHf['H2Ol'] - dHf['brucite'] - dHf['CO2g']
for y in (0.05, 0.10):
    print(f'Brucite + CO2 -> magnesite + H2O: dG0 = {dG:.1f} kJ/mol; at {y:.0%} CO2 dG = {dG + R_*T0*math.log(y)/1000:.1f} kJ/mol '
          f'(min separation work at {y:.0%}, 70% capture = {min_separation_work(y, 0.7)/1000:.1f} kJ/mol -> paid by the mineral)')
print(f'Reaction enthalpy {dH:.1f} kJ/mol (exothermic)')
cap_mag = 44.01 / 58.32
cap_hmg = 4 * 44.01 / (5 * 58.32)
print(f'CO2 per t brucite: {cap_mag:.3f} (magnesite/nesquehonite) or {cap_hmg:.3f} (hydromagnesite)')
for tails_mt in (5, 10):
    for b in (0.01, 0.03, 0.05):
        print(f'  {tails_mt} Mt/yr tailings at {b:.0%} brucite: {tails_mt*1e6*b*cap_hmg/1e3:,.0f}-'
              f'{tails_mt*1e6*b*cap_mag/1e3:,.0f} kt CO2/yr capacity')
for y in (0.05, 0.10):
    for dp in (1500, 4000):   # spray tower ~1-2 kPa; jet-bubbling reactor ~3-5 kPa (ASSUMED)
        v = air_volume_per_tonne(y, 0.7)
        e = fan_work_gj_per_tonne(y, 0.7, dp, fan_efficiency=0.7)
        print(f'  flue {y:.0%} CO2, 70% uptake, {dp} Pa: {v:,.0f} m3 gas per t CO2, blower {e:.2f} GJe/t '
              f'(${energy_cost_floor(e, 150):.0f}/t at $150/MWh remote-site power)')
for lg in (5, 15):   # ASSUMED liquid/gas ratio L/m3, 25 m pump head, slurry 1.3 t/m3, 75% pump eff.
    pump = lg / 1000 * air_volume_per_tonne(0.05, 0.7) * 1300 * 9.81 * 25 / 0.75 / 1e9
    print(f'  recirculation pumping at L/G {lg} L/m3 (5% flue): {pump:.2f} GJe/t')
print('  compare: amine capture at BD3 ~1.0-1.5 GJe-equivalent/t + compression floor 0.23-0.28 GJ/t (map)')
print(f'  Mine emissions ~360 kt/yr (Mt Keith, map) vs 10 Mt/yr tailings at 3% brucite '
      f'= {10e6*0.03*cap_hmg/360e3:.0%}-{10e6*0.03*cap_mag/360e3:.0%} of site emissions')

# ---------------------------------------------------------------------------------
hdr('IDEA 4  Warm-season-only in-storage slurry acidification (Danish NH3 practice re-targeted at CH4)')
months = np.arange(12)
T_c = np.array([3, 2, 3, 6, 10, 14, 17, 18, 15, 11, 7, 4], float)   # ASSUMED Danish outdoor slurry temperatures
# inventory: constant inflow, tank emptied to 10% on 1 Apr and to 30% on 1 Sep (ASSUMED Danish pattern)
inv = np.zeros(12); level = 0.5
for m in range(12):
    if m == 3: level = 0.10
    if m == 8: level = min(level, 0.30)
    level += 1 / 12
    inv[m] = level
warm = (months >= 4) & (months <= 9)     # May-Oct
for Ea in (63e3, 81e3, 112e3):
    rate = np.exp(-Ea / R_ * (1 / (T_c + 273.15) - 1 / 288.15))
    em = inv * rate
    frac = em[warm].sum() / em.sum()
    inflow_share = warm.sum() / 12 + inv[4] - 1 / 12   # warm-season inflow + residual at start of May
    print(f'Ea {Ea/1e3:.0f} kJ/mol: {frac:.0%} of annual CH4 emitted May-Oct; acid needed '
          f'~{inflow_share:.0%} of year-round dose -> CH4 avoided per kg acid {frac/inflow_share:.2f}x year-round')
for ch4_m3 in (0.5, 3.0):          # ASSUMED kg CH4 per m3 slurry produced (MCF ~10-40%)
    for acid_kg in (2, 8):         # ASSUMED kg H2SO4 per m3 to pH ~5.5-6
        for acid_price in (0.08, 0.20):
            avoided = 0.7 * ch4_m3 * GWP100['CH4_biogenic'] / 1000   # t CO2e per m3 at 70% reduction
            usd = acid_kg * acid_price / avoided
            if (acid_kg, acid_price) in ((2, 0.08), (8, 0.20)):
                print(f'  {ch4_m3} kg CH4/m3, {acid_kg} kg acid/m3 @ ${acid_price*1000:.0f}/t: '
                      f'{avoided*1000:.0f} kg CO2e avoided/m3, acid-only ${usd:.1f}/t CO2e (year-round)')
for acid_kg in (2, 8):
    s = acid_kg * 32.06 / 98.08
    print(f'  S load at {acid_kg} kg acid/m3, 40 m3/ha: {s*40:.0f} kg S/ha (crop need ~15-40; ASSUMED)')
global_manure_ch4 = (9, 10)  # Mt CH4/yr, ASSUMED FAO/EDGAR order of magnitude; liquid share 50-70% ASSUMED
print(f'Scale: liquid-system manure CH4 ~{9*0.5:.1f}-{10*0.7:.1f} Mt CH4 -> 70% cut = '
      f'{9*0.5*0.7*27:.0f}-{10*0.7*0.7*27:.0f} Mt CO2e/yr (GWP100)')

# ---------------------------------------------------------------------------------
hdr('IDEA 5  Hydropower tailrace degassing captured under an enclosure and destroyed in a VAM-type RTO')


def kh_ch4(T_k):
    """Henry solubility of CH4, mol/(L atm); 1.4e-3 at 298 K, van 't Hoff 1600 K (Sander compilation, approx)."""
    return 1.4e-3 * math.exp(1600 * (1 / T_k - 1 / 298.15))


Tw = 301.15
for c_mmol in (0.02, 0.05, 0.2, 0.5):    # ASSUMED hypolimnion CH4 at intake depth (tropical reservoirs)
    p_eq = c_mmol * 1e-3 / kh_ch4(Tw)
    for Q in (500, 1000):
        kg_s = Q * c_mmol * 1e-3 * 1000 * M_CH4
        print(f'  C={c_mmol} mmol/L (equil. pCH4 {p_eq:.3f} atm), Q={Q} m3/s: {kg_s:.2f} kg/s = '
              f'{kg_s*3.156e7/1e6:.1f} kt CH4/yr; 50% caught = {kg_s*3.156e7/1e9*0.5*27:.2f} Mt CO2e/yr')
x_rto = 0.005
lhv = 50.0e6; cp = 1.10e3
mass_frac = x_rto * 16.04 / 28.96
print(f'RTO feed {x_rto:.1%} CH4 (LEL 5%): adiabatic rise {mass_frac*lhv/cp:.0f} K (autothermal threshold 0.11-0.18%, map)')
fw = fan_work_gj_per_tonne(x_rto, 0.97, 4000, molar_mass=M_CH4)
print(f'Ventilation fan work at 4 kPa: {fw:.2f} GJ/t CH4 = {fw/GWP100["CH4_biogenic"]:.3f} GJ/t CO2e')
print(f'Compare: ambient-air methane removal fan work (verifier, 1.93 ppm, 50%, 100 Pa) = '
      f'{fan_work_gj_per_tonne(1.93e-6, 0.5, 100, molar_mass=M_CH4)/27:.1f} GJ/t CO2e')
unit_flow = 100.0  # m3/s per MATEC unit (360,000 m3/h)
ch4_per_unit = unit_flow * 3.156e7 * (P0 / (R_ * T0)) * x_rto * 0.97 * M_CH4 / 1000   # t/yr
for r, n in ((0.08, 20), (0.10, 15)):
    crf_ = r / (1 - (1 + r) ** -n)
    eur = 9.52e6 * crf_ + 0.87e6
    print(f'  RTO unit (MATEC capex EUR9.52M, opex 0.87M) at {x_rto:.1%}: {ch4_per_unit:,.0f} t CH4/yr -> '
          f'EUR{eur/(ch4_per_unit*27):.1f}/t CO2e (RTO only; enclosure civil works NOT costed)')
for dh in (0.1, 0.3):
    mw = 9.81 * 1000 * dh * 0.9 / 1e3   # MW per 1000 m3/s
    kg_s = 1000 * 0.05 * 1e-3 * 1000 * M_CH4 * 0.5
    print(f'  backpressure {dh} m on 1000 m3/s: {mw:.1f} MW lost = {mw/kg_s:.1f} MJ/kg CH4 caught at C=0.05, 50% '
          f'({mw/kg_s/27:.2f} GJ/t CO2e)')

# ---------------------------------------------------------------------------------
hdr('IDEA 6  Satellite-verified results-based payment for biocovers on large open dumps')
from scipy.stats import norm
za, zb = norm.ppf(0.975), norm.ppf(0.80)
for cv in (0.5, 0.7, 1.0):          # ASSUMED combined per-overpass CV (retrieval + true temporal variability)
    s = math.sqrt(math.log(1 + cv**2))
    for red in (0.3, 0.5):
        d = math.log(1 - red)
        n = 2 * (za + zb)**2 * s**2 / d**2
        print(f'  CV {cv:.0%}, true cut {red:.0%}: {math.ceil(n)} quantified overpasses per period '
              f'({math.ceil(n/0.4)} attempts at 40% usable, ASSUMED tropical cloud)')
for flux_th in (1, 3):              # site emission, t CH4/h (large dumps; ASSUMED)
    area = 50e4                     # m2 of inactive surface covered (ASSUMED 50 ha)
    gm2d = flux_th * 1e6 * 24 / area
    ann = flux_th * 8766 / 1000      # kt CH4/yr
    for eff in (0.3, 0.6):
        cost = area * 0.8 * 12 * 0.16 + 0.3e6   # 0.8 m compost at $12/m3, CRF 0.16 (8 yr), +$0.3M/yr O&M (ASSUMED)
        co2e = ann * 1000 * eff * GWP100['CH4_biogenic']
        print(f'  {flux_th} t/h over 50 ha = {gm2d:.0f} g CH4/m2/d; {eff:.0%} oxidised -> {co2e/1e6:.2f} Mt CO2e/yr, '
              f'~${cost/co2e:.2f}/t CO2e')
print('Map: open dumps underestimated 5.3x (EDGAR v8); conversion+diversion worth ~760 Mt CO2e/yr (modelled)')

# ---------------------------------------------------------------------------------
hdr('IDEA 3 (replacement)  Silted hydropower reservoirs as calcined-clay (LC3) feedstock')
cao_clinker = 0.65                       # ASSUMED CaO mass fraction of clinker
proc_co2 = cao_clinker * 44.01 / 56.08   # t CO2 per t clinker from CaCO3 calcination (stoichiometry)
fuel_co2_clk = 3.4 * 0.095               # ASSUMED 3.4 GJ/t clinker x 0.095 t CO2/GJ (coal/petcoke mix)
clk_co2 = proc_co2 + fuel_co2_clk
print(f'Clinker CO2: process {proc_co2:.3f} + fuel {fuel_co2_clk:.3f} = {clk_co2:.2f} t/t clinker')
opc = 0.95 * clk_co2
for clay_gj in (2.5, 3.0):               # ASSUMED flash/rotary calcination of clay, GJ/t calcined clay
    lc3 = 0.50 * clk_co2 + 0.30 * clay_gj * 0.095
    saved = opc - lc3
    print(f'  LC3-50 (50% clinker, 30% calcined clay, 15% limestone) with clay at {clay_gj} GJ/t: '
          f'{lc3:.2f} vs OPC {opc:.2f} t CO2/t cement -> saves {saved:.2f} t/t cement = {saved/0.30:.2f} t CO2 per t calcined clay')
for moist in (0.3, 0.5):                 # ASSUMED wet-basis moisture of dredged/excavated sediment
    water = moist / (1 - moist)
    gj = water * 2.6                     # evaporation + sensible, GJ per t dry solids (approx)
    print(f'  drying at {moist:.0%} moisture: {water:.2f} t water per t dry = {gj:.1f} GJ/t; '
          f'if fuel-fired {gj*0.095:.2f} t CO2/t; if kiln/cooler waste heat ~0')
for km in (100, 300):
    print(f'  truck haul {km} km at 0.1 kg CO2/t-km (ASSUMED): {km*0.1:.0f} kg CO2 per t dry sediment')
for vol_km3, loss in ((1.0, 0.005), (1.0, 0.01)):
    sed_t = vol_km3 * 1e9 * loss * 1.2
    print(f'  a {vol_km3} km3 reservoir losing {loss:.1%}/yr traps ~{sed_t/1e6:.0f} Mt/yr (bulk 1.2 t/m3); '
          f'one 1 Mt/yr LC3 plant needs {0.30*1e6/0.92/1e6:.2f} Mt dry clay (8% LOI)')
for value, dredge in ((30, 10), (45, 5)):   # ASSUMED $/t SCM net value (clinker displaced minus calcination) and $/m3 dredging
    print(f'  SCM net value ${value}/t x 1.2 t/m3 x 0.92 = ${value*1.2*0.92:.0f} per m3 removed vs dredging ${dredge}/m3')
