"""Coalition-first generator: sanity checks for six ideas, using the OptiLex verifier.

Every number printed here is either (a) a verifier output, (b) arithmetic on inputs stated
inline with their source, or (c) an explicit ASSUMPTION. Run:
  cd . && .venv/bin/python <this file>
"""
import math
import sys

sys.path.insert(0, 'climate')
from physics import *  # noqa: F401,F403

M_HFC134a = 0.10203  # kg/mol
R_ = 8.314462618
T_ = 298.15


def hdr(s):
    print("\n" + "=" * 78 + "\n" + s + "\n" + "=" * 78)


def crf(rate, years):
    return rate * (1 + rate) ** years / ((1 + rate) ** years - 1)


# ---------------------------------------------------------------------------
hdr("IDEA 1  Methane-intensity price escalator in gas/LNG contracts")
GJ_PER_MMBTU = 1.055056
HHV_CH4 = 55.5   # MJ/kg (gas is priced on HHV)
LHV_CH4 = 50.0
kg_ch4_per_mmbtu = GJ_PER_MMBTU * 1e3 / HHV_CH4
print(f"kg CH4 per MMBtu (HHV, pure CH4): {kg_ch4_per_mmbtu:.1f}")
for i_hi, i_lo in [(0.005, 0.002), (0.01, 0.002), (0.02, 0.002), (0.03, 0.002)]:
    d_kg = (i_hi - i_lo) * kg_ch4_per_mmbtu
    co2e100 = d_kg * GWP100["CH4_fossil"]
    co2e20 = d_kg * GWP20["CH4_fossil"]
    prem = {p: co2e100 / 1000 * p for p in (10, 20, 50)}
    print(f"intensity {i_hi:.1%} -> {i_lo:.1%}: {d_kg:.3f} kg CH4/MMBtu = {co2e100:.2f} kg CO2e (GWP100), "
          f"{co2e20:.2f} (GWP20); escalator to pay $10/$20/$50 per t CO2e = "
          f"${prem[10]:.3f}/${prem[20]:.3f}/${prem[50]:.3f} per MMBtu")
# Global LNG trade ~411 Mt in 2024 (IGU World LNG Report 2025, from memory - verify)
LNG_MT = 411
MMBTU_PER_T_LNG = 54.4 / GJ_PER_MMBTU   # LNG HHV ~54.4 GJ/t (assumption)
mmbtu = LNG_MT * 1e6 * MMBTU_PER_T_LNG
print(f"LNG trade {LNG_MT} Mt = {mmbtu/1e9:.1f} bn MMBtu/yr; a $0.10/MMBtu escalator = ${mmbtu*0.10/1e9:.2f} bn/yr")
for p_ton in (20, 50):
    tco2e = mmbtu * 0.10 / p_ton
    print(f"  -> buys {tco2e/1e6:.0f} Mt CO2e/yr (GWP100) at ${p_ton}/t = {tco2e/GWP100['CH4_fossil']/1e6:.2f} Mt CH4")
for price in (10, 12):
    print(f"  $0.10/MMBtu is {0.10/price:.1%} of a ${price}/MMBtu LNG price")
# Value of the recovered gas itself
for hh in (3.0, 11.0):
    print(f"Recovered gas value at ${hh}/MMBtu: ${hh/kg_ch4_per_mmbtu*1000:.0f}/t CH4 = "
          f"${hh/kg_ch4_per_mmbtu*1000/GWP100['CH4_fossil']:.1f}/t CO2e (GWP100)")
fan_ch4 = fan_work_gj_per_tonne(1.93e-6, 0.5, 100, molar_mass=M_CH4)
print(f"Contrast, removing the same CH4 from ambient air: fan work alone {fan_ch4:.0f} GJ/t CH4 "
      f"= {fan_ch4/GWP100['CH4_fossil']:.1f} GJ/t CO2e; source abatement is energy-POSITIVE "
      f"({LHV_CH4} GJ/t CH4 recovered when sold)")
# Settlement test: measurement disagreement
print("Settlement feasibility: Permian 0.44% (aircraft, 2024) vs 3.2% (TROPOMI inversion, 2023) "
      f"= {3.2/0.44:.1f}x disagreement; an escalator band 0.2-1% needs method agreement within ~0.2 pp")

# ---------------------------------------------------------------------------
hdr("IDEA 2  Montreal-Protocol N2O annex for adipic/nitric acid (incremental-cost fund)")
dH_dec = -82.05e3  # J/mol N2O, N2O -> N2 + 1/2 O2 (std enthalpy of formation of N2O = +82.05 kJ/mol)
print(f"N2O decomposition is exothermic: {abs(dH_dec)/M_N2O/1e6:.2f} GJ released per t N2O "
      f"= {abs(dH_dec)/M_N2O/1e6/GWP100["N2O"]*1e3:.1f} MJ per t CO2e abated")
w_offgas = min_separation_work(0.35, 0.9)
print(f"(For reference) min work to separate N2O from 35% adipic off-gas: {gj_per_tonne(w_offgas, M_N2O):.3f} GJ/t N2O "
      f"= {gj_per_tonne(w_offgas, M_N2O)/GWP100['N2O']*1e3:.2f} MJ/t CO2e - not needed, decomposition is in situ")
fan_n2o = fan_work_gj_per_tonne(336e-9, 0.5, 100, molar_mass=M_N2O)
print(f"Contrast, removing N2O from ambient air (336 ppb, 50%, 100 Pa): fan work {fan_n2o:.0f} GJ/t N2O "
      f"= {fan_n2o/GWP100['N2O']:.2f} GJ/t CO2e (> the 0.47 GJ/t DAC floor)")
CHINA_ADIPIC_MT_CO2E = 76  # NRDC 2026 via verified map (AR5 GWP)
for c in (0.25, 1.0, 4.0):
    print(f"Abating China adipic N2O ({CHINA_ADIPIC_MT_CO2E} Mt CO2e) at ${c}/t: ${CHINA_ADIPIC_MT_CO2E*c:.0f} M/yr")
EF_AA = 0.30  # t N2O per t adipic acid unabated (IPCC 2006 default)
co2e_per_t_aa = EF_AA * GWP100["N2O"]
print(f"Unabated adipic acid: {co2e_per_t_aa:.0f} t CO2e per t product (AR6 GWP 273)")
for pay in (0.5, 1, 4, 10, 20):
    print(f"  payment ${pay}/t CO2e at 95% abatement = ${pay*co2e_per_t_aa*0.95:,.0f} per t adipic acid "
          f"({pay*co2e_per_t_aa*0.95/1700:.0%} of a ~$1,700/t product price - ASSUMPTION)")
MLF_2024_26 = 965e6 / 3  # USD/yr, MLF replenishment 2024-26 (from memory - verify)
print(f"Multilateral Fund replenishment ~${MLF_2024_26/1e6:.0f} M/yr (2024-26, unverified) vs $19-304 M/yr needed")

# ---------------------------------------------------------------------------
hdr("IDEA 3  Kigali-linked deposit-refund for refrigerant recovery at end of life")
gwp_ar4 = {"R-410A": 2088, "R-22": 1810, "R-404A": 3922, "HFC-134a": 1430, "CFC-12": 10900, "R-32": 675}
for gas, g in gwp_ar4.items():
    for cost_kg in (5, 15, 40):
        pass
    print(f"{gas:9s} GWP100(AR4) {g:>6}: a $10/kg refund = ${10/g*1000:.2f}/t CO2e; $40/kg = ${40/g*1000:.2f}/t CO2e")
# Labour-cost basis for the refund (ASSUMPTIONS)
for region, wage, hours, charge in [("OECD", 60, 0.75, 2.0), ("Article 5", 6, 0.75, 1.5)]:
    per_kg = wage * hours / charge
    print(f"{region}: technician ${wage}/h x {hours} h per unit / {charge} kg recovered = ${per_kg:.1f}/kg "
          f"= ${per_kg/gwp_ar4['R-410A']*1000:.2f}/t CO2e for R-410A")
# Energy of recovery and destruction (ASSUMPTIONS: 0.5 kWh per unit recovered; 5-10 kWh/kg plasma destruction)
rec_kwh_per_tco2e = 0.5 / (2.0 * gwp_ar4["R-410A"] / 1000)
for d in (5, 10):
    dest = d / (gwp_ar4["R-410A"] / 1000)
    print(f"Energy: recovery {rec_kwh_per_tco2e:.2f} kWh/t CO2e + destruction {dest:.1f} kWh/t CO2e "
          f"= {(rec_kwh_per_tco2e+dest)*0.0036:.3f} GJ/t CO2e vs DAC floor 0.47 GJ/t CO2")
fan_hfc = fan_work_gj_per_tonne(120e-12, 0.5, 100, molar_mass=M_HFC134a)
print(f"Contrast, removing HFC-134a from air (~120 ppt, 50%, 100 Pa): fan work {fan_hfc:,.0f} GJ/t "
      f"= {fan_hfc/1430:.0f} GJ/t CO2e - once released, F-gases are effectively unrecoverable")
# Australia RRA scale reference (measured, RRA website fetched 2026-10-05)
print("RRA (Australia) FY2024-25: 485.4 t returned (347.6 t HFC); cumulative 10,727 t")
for flow_kt, gwp in [(200, 2000), (400, 2000)]:
    print(f"SCALE ASSUMPTION: global EOL refrigerant flow {flow_kt} kt/yr at mean GWP {gwp} = {flow_kt*gwp/1e6:.1f} Gt CO2e/yr; "
          f"raising recovery by 50 pp captures {flow_kt*gwp/1e6*0.5:.2f} Gt CO2e/yr")

# ---------------------------------------------------------------------------
hdr("IDEA 4  Process-CO2 phasedown for clinker + process-first storage priority")
# Process CO2 per t clinker from CaO (~65%) and MgO (~1.5%) from carbonates
cao, mgo = 0.65, 0.015
proc = cao * 44.01 / 56.08 + mgo * 44.01 / 40.30
print(f"Process CO2: {proc:.3f} t per t clinker (CaO {cao:.0%}, MgO {mgo:.1%})")
for cr in (0.71, 0.5):
    print(f"  clinker ratio {cr}: {proc*cr:.3f} t process CO2 per t cement")
CEMENT_GT = 4.0
print(f"Global process CO2 at 4.0 Gt cement, ratio 0.71: {CEMENT_GT*0.71*proc:.2f} Gt/yr (IEA ~1.5 Gt)")
for x in (0.20, 0.25, 0.95):
    w = min_separation_work(x, 0.9)
    print(f"Separation floor {x:.0%} CO2, 90% capture: {gj_per_tonne(w):.3f} GJ/t")
comp = R_ * T_ * math.log(150) / M_CO2 / 1e6
print(f"Isothermal compression 1->150 bar floor: {comp:.3f} GJ/t")
sep25 = gj_per_tonne(min_separation_work(0.25, 0.9))
print(f"Kiln floor sep+compression: {sep25+comp:.2f} GJ/t; Brevik-type ~3 GJ_th/t at 120C "
      f"(exergy ~{3*(1-298.15/393.15):.2f} GJ/t) -> second-law ~{(sep25)/(3*(1-298.15/393.15)):.0%} (separation only)")
for cost in (100, 150):
    per_t_cem = cost * proc * 0.71
    for cem_m2 in (0.15, 0.30):
        print(f"  capture+storage EUR{cost}/t on process CO2 only: EUR{per_t_cem:.0f}/t cement; "
              f"{cem_m2} t cement/m2 -> EUR{per_t_cem*cem_m2:.0f}/m2 = {per_t_cem*cem_m2/2000:.2%} of EUR2,000/m2")
# Storage commons
PRUDENT = 1460
for yrs in (50, 80, 100):
    used = CEMENT_GT * 0.71 * proc * yrs
    print(f"Storing ALL cement process CO2 for {yrs} yr = {used:.0f} Gt = {used/PRUDENT:.1%} of prudent 1,460 Gt")
for gt in (8.7, 15):
    print(f"Storage at {gt} Gt/yr (IPCC pathway) exhausts 1,460 Gt in {PRUDENT/gt:.0f} yr")
heat = 3.0 * CEMENT_GT * 0.71 * proc * 0.9
print(f"Heat for 90% capture of all process CO2 at 3 GJ/t: {heat:.1f} EJ/yr = {heat/WORLD_PRIMARY_ENERGY_EJ:.1%} of primary")
s = ScaleCheck(CEMENT_GT * 0.71 * proc * 0.9, sep25 + comp)
print(f"At the floor: {s.ej_per_year:.2f} EJ/yr = {s.share_of_world_primary_energy:.2%} of primary")

# ---------------------------------------------------------------------------
hdr("IDEA 5  Ethanol CO2: on-site Class VI wells + pore-space royalties, no eminent domain")
gal = 100e6
kg_eth = gal * 3.78541 * 0.789
co2 = kg_eth / 1000 * (2 * 44.01 / (2 * 46.07))  # C6H12O6 -> 2 EtOH + 2 CO2: 0.955 t CO2/t EtOH
print(f"100 Mgal/yr plant: {kg_eth/1e9:.3f} Mt ethanol -> {co2/1e6:.3f} Mt CO2/yr")
w_ferm = min_separation_work(0.98, 0.9, 0.999)
print(f"Separation floor (98% CO2 stream): {gj_per_tonne(w_ferm):.4f} GJ/t; compression floor {comp:.3f} GJ/t; "
      f"real ~0.42 GJ/t at 70% eff -> {0.42/3.6*1000:.0f} kWh/t")
# Wells
for q in (0.33, 0.7, 1.06):
    print(f"  Ringrose well rate {q} Mt/yr -> {co2/1e6/q:.2f} injectors per 100-Mgal plant")
# Plume footprint (ASSUMPTIONS: 50 m net sand, 20% porosity, 3% storage efficiency, rho 700 kg/m3)
h, phi, E, rho = 50, 0.20, 0.03, 700
m3_per_km2 = 1e6 * h * phi * E
t_per_km2 = m3_per_km2 * rho / 1000
life = 20
total = co2 / 1e6 * life
area_km2 = total * 1e6 / t_per_km2
print(f"Storage density {t_per_km2/1e3:.0f} kt CO2/km2 -> {life} yr x {co2/1e6:.2f} Mt = {total:.1f} Mt over {area_km2:.0f} km2 "
      f"({area_km2*247.1:,.0f} acres)")
for roy in (1, 2, 3):
    per_acre = roy * co2 / (area_km2 * 247.1)
    print(f"  royalty ${roy}/t -> ${per_acre:.0f}/acre/yr to plume-area owners (Iowa cash rent ~$250-300/acre, ASSUMPTION)")
# Transport comparison: Summit ~$9bn for 57 plants (verified map); design ~18 Mt/yr (from memory - verify)
for cap in (12, 18):
    per_tyr = 9e9 / (cap * 1e6)
    print(f"Pipeline capex ~${per_tyr:.0f} per t/yr (Summit $9bn / {cap} Mt/yr) -> ${per_tyr*crf(0.08,25):.0f}/t annualised (8%, 25 yr)")
for capex in (30e6, 60e6):
    per_tyr = capex / co2
    print(f"On-site Class VI package ${capex/1e6:.0f}M (ASSUMPTION) -> ${per_tyr:.0f} per t/yr -> "
          f"${per_tyr*crf(0.08,25):.0f}/t annualised")
US_POOL = (43, 46)
print(f"US pool {US_POOL} Mt/yr x 45Q $85 = ${US_POOL[0]*85/1e3:.1f}-{US_POOL[1]*85/1e3:.1f} bn/yr")

# ---------------------------------------------------------------------------
hdr("IDEA 6  CBAM revenue recycled as Multilateral-Fund-style green-iron/ammonia auctions")
CBAM_OWN = 1.4e9         # EUR/yr, 75% of CBAM revenue, 2028-34 avg, 2025 prices (Commission own-resources page)
cbam_total = CBAM_OWN / 0.75
print(f"Implied total CBAM revenue ~EUR{cbam_total/1e9:.2f} bn/yr; member-state 25% share EUR{cbam_total*0.25/1e9:.2f} bn")
for share, label in [(0.25, "member-state 25%"), (1.0, "all")]:
    for prem in (100, 150, 200):
        mt = cbam_total * share / prem / 1e6
        print(f"  {label}: EUR{prem}/t premium -> {mt:.1f} Mt green steel-equivalent/yr -> "
              f"{mt*1.7:.1f} Mt CO2 avoided (1.7 t/t BF-BOF minus green route, ASSUMPTION)")
# H2-DRI energy vs floor (map: Fe2O3 dissociation enthalpy 2.05 MWh/t Fe)
dH_fe2o3 = 824.2e3  # J/mol Fe2O3, -dHf
floor = dH_fe2o3 / (2 * 0.055845) * 1000 / 3.6e9
print(f"Fe2O3 dissociation enthalpy floor: {floor:.2f} MWh/t Fe; H2-DRI ~3.6 MWh/t -> {3.6/floor:.2f}x floor")
# Green ammonia SECI premium
for green in (570, 745):
    for grey in (400, 490):
        prem = green - grey
        # grey NH3 ~2.0-2.4 t CO2/t (SMR, ASSUMPTION; process+fuel)
        print(f"  SECI green NH3 ${green}/t vs grey ${grey}/t: premium ${prem}/t -> ${prem/2.2:.0f}/t CO2 at 2.2 t CO2/t NH3")
el_nh3 = 9.5  # MWh/t NH3 (literature range 9-10)
print(f"Green NH3 at {el_nh3} MWh/t: 1 Mt/yr needs {el_nh3:.1f} TWh = {el_nh3/WORLD_ELECTRICITY_TWH:.3%} of world electricity")

# ---------------------------------------------------------------------------
hdr("Addenda")
# Idea 3: Australia RRA measured returns -> CO2e, and per-capita scaling (crude)
rra = 347.62 * 2000 + 127.13 * 1810 + 1.27 * 10900 + 9.37 * 2000   # mean HFC GWP ~2000 ASSUMPTION
print(f"RRA FY24-25 returns ~{rra/1e6:.2f} Mt CO2e (HFC mean GWP 2000 assumed)")
print(f"  scaled per capita (27 M -> 8.2 bn): ~{rra/1e6*8.2e9/27e6/1e3:.2f} Gt CO2e/yr if the world matched Australia")
# Norway HFC duty/refund (Skatteetaten, fetched 2026-10-05): NOK 1.639 and 1.405 per kg x GWP
for nok_usd in (10.5, 11.0):
    print(f"Norway 2026: duty NOK1,639/t CO2e = ${1639/nok_usd:.0f}/t; refund NOK1,405/t CO2e = ${1405/nok_usd:.0f}/t "
          f"(R-410A refund ${1.405*2088/nok_usd:.0f}/kg) at {nok_usd} NOK/USD")
# Idea 1: revenue-neutral differential around a reference intensity
ref = 0.005
for i in (0.001, 0.002, 0.005, 0.01, 0.02):
    adj = (ref - i) * kg_ch4_per_mmbtu * GWP100["CH4_fossil"] / 1000 * 30   # $30/t CO2e differential slope
    print(f"  intensity {i:.1%}: differential {adj:+.3f} $/MMBtu around a 0.5% reference at $30/t CO2e slope")
# Idea 6: add an automaker buyer-club pass-through
for cars, prem in [(12e6, 150), (12e6, 200)]:
    pool = cars * prem
    print(f"Buyer club: {cars/1e6:.0f} M EU cars x EUR{prem} = EUR{pool/1e9:.1f} bn/yr; +CBAM EUR1.87 bn -> "
          f"{(pool+1.87e9)/150/1e6:.0f} Mt green steel-eq at EUR150/t -> {(pool+1.87e9)/150*1.7/1e6:.0f} Mt CO2/yr")
