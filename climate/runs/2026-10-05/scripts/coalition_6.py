"""Verifier for coalition_6: CBAM-revenue + buyer-club funded reverse auctions for green HBI / ammonia
from renewable-rich exporting countries (Montreal-MLF-style co-governance).

All inputs are labelled: [SRC] = cited in the idea or prior OptiLex scratch scripts (heavy_industry.py),
[MEM] = recalled literature value not re-fetched in this run, [ASSUMP] = analyst assumption.
"""
import sys, math
sys.path.insert(0, 'climate')
from physics import *

EUR_USD = 1.16   # [ASSUMP] 2026 approx

def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)

def hdr(s):
    print("\n== " + s + " ==")

# ---------------------------------------------------------------- 1. Thermodynamic floors
hdr("1. Thermodynamic floors (no gas separation involved; floors are reduction / synthesis work)")
dGf_Fe2O3 = 742.2e3   # J/mol, -ΔfG°298 hematite (NIST-JANAF / CRC) [MEM]
dHf_Fe2O3 = 824.2e3   # J/mol, -ΔfH°298 [MEM]
M_Fe = 0.055845
g_floor = dGf_Fe2O3 / (2 * M_Fe) / 1e6      # GJ/t Fe  (J/kg -> GJ/t is /1e6)
h_floor = dHf_Fe2O3 / (2 * M_Fe) / 1e6
print(f"Fe2O3 -> 2Fe + 1.5O2: Gibbs floor {g_floor:.2f} GJ/t Fe = {g_floor/3.6:.2f} MWh/t; "
      f"enthalpy {h_floor:.2f} GJ/t = {h_floor/3.6:.2f} MWh/t")
for mwh in (3.2, 3.6, 4.0):
    print(f"  H2-DRI-EAF at {mwh} MWh/t steel: {mwh/(g_floor/3.6):.2f}x Gibbs floor, {mwh/(h_floor/3.6):.2f}x enthalpy floor")
print("  Idea claim (4) '3.6 MWh/t = 1.76x the 2.05 MWh/t floor' -> arithmetic correct vs enthalpy; vs Gibbs (true work floor) 1.95x."
      " NOT below floor.")
# Ammonia from water + N2: N2 + 3H2O(l) -> 2NH3 + 1.5O2
dG_h2o, dGf_nh3 = 237.1e3, -16.4e3
g_nh3 = (3 * dG_h2o + 2 * dGf_nh3) / 2 / 0.017031 / 1e6   # GJ/t NH3
print(f"Green NH3 from water + air: Gibbs floor {g_nh3:.1f} GJ/t = {g_nh3/3.6:.2f} MWh/t; claim 9.5 MWh/t = "
      f"{9.5/(g_nh3/3.6):.2f}x floor (air-separation work for N2 negligible: "
      f"{gj_per_tonne(min_separation_work(0.78,0.9,0.999), 0.028)*0.82:.3f} GJ/t NH3)")

# ---------------------------------------------------------------- 2. Revenue arithmetic (claims 1-3)
hdr("2. Funding pool (claims 1-3)")
CBAM_OWN = 1.4e9   # [SRC idea] EUR/yr, 75% of CBAM revenue, 2028-34 avg, 2025 prices (Commission own-resources page)
cbam_total = CBAM_OWN / 0.75
print(f"Total CBAM revenue {cbam_total/1e9:.2f} bn EUR/yr; member-state 25% {cbam_total*0.25/1e9:.2f} bn")
# bottom-up plausibility cross-check (order of magnitude only)
emb = {"iron&steel": 33 * 1.9, "fertiliser/NH3": 12, "aluminium(direct)": 10, "cement": 3, "H2/elec": 2}  # Mt CO2 embedded [ASSUMP]
E = sum(emb.values())
for eua, factor, net in [(75, 0.25, 0.5), (90, 0.64, 0.4), (100, 0.64, 0.3)]:
    # factor = average CBAM phase-in 2028-34 ≈ mean(10,22.5,48.5,61,73.5,86,100)% = 57%; net = share of embedded
    # emissions above benchmark & not exempt/deducted (de minimis, foreign carbon price, decarbonised imports) [ASSUMP]
    print(f"  bottom-up: {E:.0f} Mt embedded x EUR{eua} x phase {factor:.0%} x chargeable {net:.0%} = EUR{E*eua*factor*net/1e3:.1f} bn/yr")
print(f"  mean CBAM factor 2028-34 = {sum([10,22.5,48.5,61,73.5,86,100])/7:.1f}% -> Commission EUR1.87 bn total is within the bottom-up band")
cars_lo, cars_hi = 10.7e6, 12.0e6   # [MEM] ACEA EU27 new cars ~10.6-10.8 M (2024-25); 12 M in idea ~ EU+EFTA+UK-ish
for cars, lbl in [(cars_lo, "EU27 ~10.7 M"), (cars_hi, "idea 12 M")]:
    for p in (150, 200):
        print(f"  buyer club {lbl} x EUR{p} = EUR{cars*p/1e9:.2f} bn/yr")
for avg_price in (30000, 45000):  # [MEM] JATO/ACEA-scale EU average new-car price range
    print(f"  EUR150-200/car on EUR{avg_price:,}: {150/avg_price:.2%}-{200/avg_price:.2%} (idea claims 0.5-0.8%)")

# ---------------------------------------------------------------- 3. Bottom-up green-HBI premium
hdr("3. Bottom-up premium: imported green HBI -> EU EAF vs EU BF-BOF (no carbon price), per t liquid steel")
cases = {
    #           capex$/kW  CF   $/MWh  kWh/kg  WACC  kgH2/tHBI  storage$/kg  DRpellet$/t  ship$/t  EAFextra$/tLS
    "low":  dict(cap=900,  cf=0.65, pe=22, eff=50, r=0.07, h2=55, sto=0.25, pel=140, ship=15, eaf=10),
    "base": dict(cap=1700, cf=0.55, pe=35, eff=53, r=0.09, h2=60, sto=0.50, pel=155, ship=25, eaf=30),
    "high": dict(cap=2500, cf=0.45, pe=50, eff=56, r=0.12, h2=65, sto=0.80, pel=175, ship=35, eaf=50),
}
# Sources/justification: electrolyser system capex - Chinese alkaline ~$750-1,200/kW vs Western installed ~$2,000-2,600/kW
#   (IEA Global Hydrogen Review 2024, [MEM]); hybrid solar+wind CF 45-65% at best sites [ASSUMP];
#   PPA $22-50/MWh for Brazil/MENA/Australia hybrids [ASSUMP]; 50-56 kWh/kg system [MEM, IEA];
#   WACC 7-12% for emerging-market project finance [ASSUMP]; 55-65 kg H2/t HBI incl. heating (stoich 54) [SRC heavy_industry.py];
#   DR-grade pellet $140-175/t vs BF blend ~$110/t [ASSUMP from 2024-25 pellet premia]; shipping HBI to EU $15-35/t [ASSUMP].
ref = dict(ore_bf=1.55 * 110, coal=0.50 * 230, bf_capex=25)   # per t hot metal: ore blend, coking coal+PCI [ASSUMP], reline
gas_ref_h2_cost = None
prem_eur = {}
for k, c in cases.items():
    capex_kg = c["cap"] * (crf(c["r"], 20) + 0.025) / (8760 * c["cf"] / c["eff"])
    elec_kg = c["eff"] * c["pe"] / 1000
    lcoh = capex_kg + elec_kg + c["sto"]
    shaft = 350 * (crf(c["r"], 25)) + 20 + 0.3 * c["pe"]           # $/t HBI: shaft capex $350/t-yr [ASSUMP], O&M, heating power
    hbi = c["pel"] * 1.42 + c["h2"] * lcoh + shaft + c["ship"]
    hm = ref["ore_bf"] + ref["coal"] + 60 + ref["bf_capex"]        # 60 = BF/coke/sinter O&M [ASSUMP]
    # per t liquid steel, both routes charging ~0.17 t scrap (cancels): 0.92 t HBI (EAF) vs 0.94 t HM (BOF) [ASSUMP]
    prem_t_ls = 0.92 * hbi - 0.94 * hm + c["eaf"]
    prem_eur[k] = prem_t_ls / EUR_USD
    print(f"  {k:4s}: LCOH ${lcoh:.2f}/kg (capex {capex_kg:.2f}, power {elec_kg:.2f}, storage {c['sto']:.2f}); "
          f"green HBI ${hbi:.0f}/t vs BF hot metal ${hm:.0f}/t -> premium ${prem_t_ls:.0f}/t LS = EUR{prem_eur[k]:.0f}/t")
print("  References: GEI 2024 modelled $167-231/t at H2 ~$5/kg; Fastmarkets EU low-carbon flat premium EUR150-200/t (2026 assessed)")
print("  CONFOUND: the Fastmarkets premium prices mostly scrap-EAF / mass-balance 'green' steel, not primary H2-DRI;"
      " it understates the primary-iron cost gap that the fund must pay.")

# ---------------------------------------------------------------- 4. Avoided CO2 and cost per tonne
hdr("4. Avoided CO2 per t steel and fund cost per t CO2")
# BF-BOF EU ~1.9-2.0 t CO2/t (worldsteel global avg 2.33) [MEM]; green route residual: pellets, lime, EAF electrodes,
# EAF grid power 0.6 MWh x EU grid 0.2-0.25 t/MWh, shipping -> 0.15-0.45 [ASSUMP]
avoid = {"low": 1.85, "base": 1.65, "high": 1.50}   # keyed by cost case (low cost <-> high avoidance)
prem_case = {"low": 100, "base": 200, "high": 350}  # EUR/t LS: low=market floor; base=bottom-up base & top of Fastmarkets; high=Western-capex tail (bottom-up high is higher still)
admin = 0.03                                         # 3% MRV/fund administration [ASSUMP]
cost = {}
for k in ("low", "base", "high"):
    eur = prem_case[k] * (1 + admin) / avoid[k]
    cost[k] = eur * EUR_USD
    print(f"  {k:4s}: premium EUR{prem_case[k]}/t LS, avoided {avoid[k]} t/t -> EUR{eur:.0f}/t CO2 = ${cost[k]:.0f}/t CO2")
print("  Claim (2) used 1.7 t/t avoided; base here 1.65 (EAF grid power + pellet induration residuals).")

# ---------------------------------------------------------------- 5. ETS phase-out shrinks the gap
hdr("5. Gap to grey INCLUDING EU ETS carbon cost (free allocation phase-out = CBAM factor)")
sched = {2026: .025, 2027: .05, 2028: .10, 2029: .225, 2030: .485, 2031: .61, 2032: .735, 2033: .86, 2034: 1.0}
for eua_path, lbl in [((75, 80, 85, 90, 95, 100, 105, 110, 115), "EUA 75->115"), ((70,) * 9, "EUA flat 70")]:
    row = []
    for (yr, f), eua in zip(sched.items(), eua_path):
        gap = prem_case["base"] - eua * 1.65 * f
        row.append(f"{yr}:{gap:.0f}")
    print(f"  {lbl}: net gap EUR/t LS (base premium 200) " + " ".join(row))
print("  -> fund is a BRIDGE (2027-2033); after 2034 the ETS alone closes a EUR200 gap at EUA>=EUR121.")
print(f"     breakeven EUA at full phase-out: low {100/1.85:.0f}, base {200/1.65:.0f}, high {350/1.5:.0f} EUR/t")

# ---------------------------------------------------------------- 6. Scale
hdr("6. Scale funded per year (CBAM all + buyer club)")
for k in ("low", "base", "high"):
    pool = cbam_total + {"low": 12.0e6 * 200, "base": 10.7e6 * 175, "high": 10.7e6 * 150}[k]
    mt = pool / prem_case[k] / 1e6
    print(f"  {k:4s}: pool EUR{pool/1e9:.2f} bn / EUR{prem_case[k]} = {mt:.1f} Mt steel -> {mt*avoid[k]:.1f} Mt CO2/yr")
print("  Idea claim (3): 24-28 Mt steel, 42-48 Mt CO2/yr (at EUR150/t, 1.7 t/t, 12 M cars) -> reproduced arithmetic, optimistic inputs.")
print(f"  EU BF ironmaking ~70 Mt HM [SRC] x 1.65 = {70*1.65:.0f} Mt CO2; global BF-BOF ~1,350 Mt x 1.65 = {1350*1.65/1e3:.2f} Gt (ceiling)")
print("  Falsification threshold in idea: premium > EUR250/t -> < 30 Mt CO2/yr. Base (EUR200) sits ~at the line; high is below.")

# ---------------------------------------------------------------- 7. Resources for base-case volume
hdr("7. Resource needs (base-case funded volume)")
print(f"  funded volume used: {(cbam_total + 10.7e6*175)/200/1e6:.1f} Mt steel-eq/yr")
mt = (cbam_total + 10.7e6 * 175) / 200 / 1e6
for k in ("low", "base", "high"):
    c = cases[k]
    twh_h2 = mt * 0.92 * c["h2"] * c["eff"] / 1e3       # TWh in exporters for electrolysis
    twh_heat = mt * 0.92 * 0.3
    gw_el = twh_h2 * 1e3 / (8760 * c["cf"])               # GW electrolyser
    print(f"  {k:4s}: exporter electricity {twh_h2+twh_heat:.0f} TWh/yr ({(twh_h2+twh_heat)/WORLD_ELECTRICITY_TWH:.2%} world), "
          f"electrolysers {gw_el:.0f} GW at CF {c['cf']}")
twh_eaf = mt * 0.6
print(f"  EU EAF power: {twh_eaf:.0f} TWh/yr ({twh_eaf/2700:.2%} of EU ~2,700 TWh)")
print("  Global installed electrolysis ~2-5 GW (end-2024/25, IEA GHR [MEM]) -> base needs several times today's global fleet.")
dr_pellets = mt * 0.92 * 1.42
print(f"  DR-grade pellets: {dr_pellets:.0f} Mt/yr vs seaborne DR-grade supply ~50-65 Mt "
      f"(IEEFA: 3-4% of ~1.6 Gt seaborne ore [MEM]) -> {dr_pellets/65:.0%}-{dr_pellets/50:.0%} of today's DR-grade supply: BINDING")
twh = mt * 0.92 * (60 * 53 / 1e3 + 0.3)
solar_gwp = twh * 1e3 / 2000 * 0.6                  # 60% of energy from solar at 2,000 kWh/kWp [ASSUMP]
print(f"  Land: ~{solar_gwp:.0f} GWp solar x ~1.5 ha/MWp = {solar_gwp*1.5*10:.0f} km2 (+ wind, low footprint)")
h2_mt = mt * 0.92 * 0.060
print(f"  Water: {h2_mt:.2f} Mt H2 x 15-25 m3/t (incl. treatment) = {h2_mt*15:.0f}-{h2_mt*25:.0f} Mm3/yr; "
      f"desal energy {h2_mt*25*3.5/1e3:.2f} TWh (negligible)")

# ---------------------------------------------------------------- 8. Ammonia lane (claims 5-6)
hdr("8. Ammonia lane")
# t CO2/t NH3: gas-SMR direct ~1.8 to incl. upstream ~2.4 [MEM, IEA]
for green, grey in [(570, 490), (660, 445), (745, 400)]:
    p = green - grey
    print(f"  SECI ${green} vs grey ${grey}: premium ${p}/t -> ${p/2.4:.0f}-{p/1.8:.0f}/t CO2 (1.8-2.4 t CO2/t NH3); "
          f"+$40-80/t India->EU shipping if delivered to EU")
print(f"  1 Mt NH3 x 9.5 MWh = 9.5 TWh = {9.5/WORLD_ELECTRICITY_TWH:.3%} world electricity (claim 6 correct)")
print(f"  EU ammonia ~15-17 Mt/yr capacity [MEM]: full switch at 9.5 MWh/t = {16*9.5:.0f} TWh, avoids ~{16*2.0:.0f} Mt CO2")

# ---------------------------------------------------------------- summary
hdr("SUMMARY")
print(f"floor (Gibbs Fe2O3 reduction per t CO2 avoided, base) = {g_floor*0.98/1.65:.2f} GJ/t CO2")
e = {"low": 3.2 * 3.6 / 1.85, "base": 3.6 * 3.6 / 1.65, "high": 4.0 * 3.6 / 1.50}
print(f"energy (electricity, GJ/t CO2 avoided) low {e['low']:.1f} base {e['base']:.1f} high {e['high']:.1f} "
      "(displaces ~17-20 GJ/t steel of coal in BF-BOF)")
print(f"cost $/t CO2: low {cost['low']:.0f} base {cost['base']:.0f} high {cost['high']:.0f}")
