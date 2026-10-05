"""Checks for six single-graft ideas (refinery/petrochemical generator).

All inputs marked ASSUMPTION are mine; everything else is either from the verifier
(physics.py) or from sources named in comments. Run:
  cd . && .venv/bin/python <this file>
"""
import math
import sys

sys.path.insert(0, 'climate')
from physics import *  # noqa: F401,F403


def crf(rate, years):
    return rate * (1 + rate) ** years / ((1 + rate) ** years - 1)


def hdr(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)


# ---------------------------------------------------------------------------
hdr("IDEA 1  Cement: MVR / heat-pump top-up from waste-heat-capped 50% to 90% capture")
x = 0.25
w50 = min_separation_work(x, 0.50)
w90 = min_separation_work(x, 0.90)
marg = (w90 * 0.90 - w50 * 0.50) / 0.40
print(f"Separation floor at 25% CO2: 50% capture {gj_per_tonne(w50):.3f} GJ/t, 90% {gj_per_tonne(w90):.3f} GJ/t,"
      f" marginal tonne 50->90% {gj_per_tonne(marg):.3f} GJ/t")
comp = gj_per_tonne(R * T0 * math.log(150e5 / P0))  # isothermal ideal-gas compression floor
print(f"Isothermal compression floor 1->150 bar (ideal gas): {comp:.3f} GJ/t")

plant_co2 = 0.80e6     # t/yr, Brevik-like (400 kt = ~50%)
inc = plant_co2 * 0.40  # t/yr extra captured going 50 -> 90 %
for duty in (2.6, 3.0, 3.5):  # GJ heat per t, ASSUMPTION range (amine reboiler, map gives 2.4-3.6)
    mwth = inc * duty * 1e9 / (8000 * 3600) / 1e6
    print(f"  reboiler duty {duty} GJ/t -> extra heat {inc*duty/1e6:.2f} PJ/yr = {mwth:.0f} MWth at 8000 h/yr")

# Heat-pump COP: Carnot x second-law efficiency
for t_src, t_sink in ((60, 130), (95, 130), (100, 125)):
    carnot = (t_sink + 273.15) / (t_sink - t_src)
    print(f"  Carnot COP {t_src}C->{t_sink}C = {carnot:.1f}; at 45-55% of Carnot = {0.45*carnot:.1f}-{0.55*carnot:.1f}")
cop_lit = 100 / 26.9  # CCST 2025 (doi 10.1016/j.ccst.2025.100446): 100 MWth replaced by 26.9 MWe (modelled)
print(f"  Literature (modelled) effective COP for MVR+LVC+HTHP at a cement plant: {cop_lit:.2f}")

duty = 3.0
for cop in (2.5, cop_lit, 5.0):
    e_gj = duty / cop
    kwh = e_gj / 0.0036
    print(f"  COP {cop:.2f}: {e_gj:.2f} GJe/t = {kwh:.0f} kWh/t; electricity cost at $40/$60/$80 per MWh = "
          f"${kwh*0.04:.0f}/${kwh*0.06:.0f}/${kwh*0.08:.0f} per t;"
          f" separation 2nd-law eff vs marginal floor {gj_per_tonne(marg)/e_gj:.0%}")
    for g in (30, 250, 450):  # gCO2/kWh grid, ASSUMPTION (Norway / EU-ish / coal-heavy)
        print(f"      grid {g} g/kWh -> indirect {kwh*g/1e6*1000:.0f} kg CO2 per t captured ({kwh*g/1e6:.1%})")

# Gas-boiler alternative for the same increment
gas_gj = duty / 0.90
boiler_co2 = gas_gj * 0.0561  # t CO2 per GJ natural gas (IPCC default 56.1 kg/GJ)
print(f"  Gas boiler alternative: {gas_gj:.2f} GJ gas/t -> {boiler_co2:.3f} t CO2 per t captured "
      f"(uncaptured unless the boiler flue also goes to the absorber); gas at $8-12/GJ = ${gas_gj*8:.0f}-{gas_gj*12:.0f}/t")
# Heat-pump capex per tonne
mwth = inc * duty * 1e9 / (8000 * 3600) / 1e6
for capex_kw in (400, 900):  # EUR/$ per kWth delivered, ASSUMPTION for large MVR/HTHP
    ann = mwth * 1e3 * capex_kw * crf(0.08, 20)
    print(f"  heat-pump capex {capex_kw}/kWth x {mwth:.0f} MWth = {mwth*capex_kw/1e3:.0f} M; annualised {ann/1e6:.1f} M/yr"
          f" = {ann/inc:.1f} per incremental t")
sector = ScaleCheck(0.4, duty / cop_lit)  # per 1 Gt/yr of cement CO2 treated, 0.4 Gt increment
print(f"  Per 1 Gt/yr cement CO2 lifted 50->90%: 0.4 Gt extra, {sector.ej_per_year:.2f} EJ elec ="
      f" {sector.share_of_world_electricity_if_electric:.2%} of world electricity")

# ---------------------------------------------------------------------------
hdr("IDEA 2  Cycling NGCC: rich/lean solvent tankage + off-peak electric regeneration")
print(f"Separation floor 4% CO2, 90%: {gj_per_tonne(min_separation_work(0.04, 0.90)):.3f} GJ/t")
peak = 270.0  # t CO2/h captured at full load, ASSUMPTION for ~740 MW NGCC (NZT: up to 2 Mt/yr)
capex_capture = 742e3 * 966  # $ : NETL Rev4A H-class overnight cost rise $970->$1,936/kW (2018$), x 742 MW
share_regen = 0.35            # ASSUMPTION: stripper+reboiler+compression+drying share of capture capex
for cf in (0.25, 0.40, 0.60):
    hours_on = 24 * cf
    avg = peak * cf
    stored = (peak - avg) * hours_on          # t CO2 buffered per daily cycle
    scale = (avg / peak) ** 0.65              # six-tenths-ish rule, ASSUMPTION exponent 0.65
    save = capex_capture * share_regen * (1 - scale)
    ebo_mw = avg * 3.0 * 1e9 / 3600 / 1e6     # MWth if regenerated on electricity (3.0 GJ/t)
    print(f"\n CF {cf:.0%}: plant on {hours_on:.1f} h/day; stripper sized for avg {avg:.0f} t/h vs peak {peak:.0f};"
          f" buffer {stored:,.0f} t CO2/day; regen-train capex saving ${save/1e6:.0f}M")
    for cap_mol_kg, label, amine_frac, amine_price in ((0.5, "30wt% MEA", 0.30, 1800), (0.86, "5 m PZ", 0.30, 4000)):
        sol_t = stored * 1e6 / (cap_mol_kg * 44.01) / 1e3   # t of solvent
        vol = sol_t / 1.05
        inv = sol_t * amine_frac * amine_price
        tank_lo, tank_hi = 2 * vol * 150, 2 * vol * 300     # two tanks, $/m3 ASSUMPTION
        extra_lo = inv + tank_lo + ebo_mw * 1e3 * 120
        extra_hi = inv + tank_hi + ebo_mw * 1e3 * 200
        print(f"   {label} (cyclic {cap_mol_kg} mol/kg): {sol_t/1e3:,.0f} kt solvent ({vol/1e3:,.0f} k m3);"
              f" amine inventory ${inv/1e6:.0f}M; tanks ${tank_lo/1e6:.0f}-{tank_hi/1e6:.0f}M;"
              f" e-boiler {ebo_mw:.0f} MWth; total added ${extra_lo/1e6:.0f}-{extra_hi/1e6:.0f}M vs saving ${save/1e6:.0f}M")
    # Energy arbitrage per tonne: steam extraction at peak vs e-boiler at off-peak
    lost_peak = 0.30  # MWh_e lost per t from steam extraction + compression at peak, ASSUMPTION (BD3 ~0.37 incl. aux)
    for p_peak, p_off in ((100, 20), (150, 0)):
        conv = lost_peak * p_peak
        shifted = (3.0 / 3.6) * p_off + 0.1 * p_off   # e-boiler COP 1 + compression off-peak
        print(f"   energy per t: conventional (lost peak output) ${conv:.0f}/t vs off-peak e-boiler ${shifted:.0f}/t "
              f"at peak ${p_peak}/off-peak ${p_off} per MWh -> ${conv-shifted:.0f}/t x {avg*8760/1e6:.2f} Mt/yr"
              f" = ${(conv-shifted)*avg*8760/1e6:.0f}M/yr")
print("\n(annualise at CRF 8%/25 yr =", f"{crf(0.08,25):.4f})")
for g in (0, 100, 400, 900):
    print(f"   off-peak marginal grid {g} g/kWh x 0.93 MWh/t (e-boiler+compression) = {0.93*g/1000:.2f} t CO2 per t captured")
for cop in (1.0, 2.5):
    print(f"   regen electricity at COP {cop}: {3.0/3.6/cop + 0.1:.2f} MWh/t incl. 0.1 MWh/t compression")

# ---------------------------------------------------------------------------
hdr("IDEA 3  Ethanol fermentation CO2 by liquid-CO2 unit train (LPG/NGL rail graft)")
gal = 15.5e9
eth_t = gal * 3.785 * 0.789 / 1e3
co2_pool = eth_t * 0.955
print(f"US ethanol {gal/1e9:.1f} bn gal = {eth_t/1e6:.1f} Mt -> {co2_pool/1e6:.1f} Mt CO2/yr fermentation pool")
plant = 100e6 * 3.785 * 0.789 / 1e3 * 0.955
print(f"100 Mgal/yr plant: {plant/1e6:.3f} Mt CO2/yr = {plant/365:.0f} t/d")
car_payload = 80.0  # t liquid CO2 per DOT-105J500W car (83 m3; 286k lb GRL) ASSUMPTION ~78-82 t
print(f"  cars/day at {car_payload:.0f} t: {plant/365/car_payload:.1f}; 100-car unit trains per year: {plant/(100*car_payload):.0f}")
# Liquefaction energy (ideal): isothermal compression 1->20 bar + refrigeration of latent heat at -20 C
comp20 = gj_per_tonne(R * T0 * math.log(20e5 / P0))
latent = 0.282  # GJ/t latent heat of CO2 at about -20 C (approx. 282 kJ/kg)
cop_ref = 0.5 * (253.15 / (308.15 - 253.15))  # 50% of Carnot, -20 C evaporator, 35 C condensing
liq = comp20 + latent / cop_ref
print(f"  liquefaction (ideal compression 1->20 bar {comp20:.3f} + refrigeration {latent/cop_ref:.3f}) ~ {liq:.2f} GJ/t;"
      f" real plants ~0.36-0.47 GJ/t (100-130 kWh/t, ASSUMPTION) vs pipeline compression floor {comp:.2f} GJ/t")
for miles in (300, 500, 700):
    rail_lo, rail_hi = 0.039 * miles, 0.115 * miles  # Frontiers 2024 competitive unit-train pricing $/t-mi
    co2_lo, co2_hi = 0.020 * miles, 0.045 * miles     # kg CO2 per payload t-mi incl. empty return, ASSUMPTION
    cycle_days = 2 * miles / 250 + 3                  # 250 mi/day + 3 days terminal time, ASSUMPTION
    cars_per_mt = 1e6 / car_payload * cycle_days / 365
    car_cost = cars_per_mt * 212e3 * crf(0.08, 30) / 1e6  # $/t ownership cost, $200-225k per car
    liq_cost = (10, 20)                                    # $/t liquefaction capex+opex ASSUMPTION
    stor = (10, 20)                                        # $/t Class VI storage incl. MRV ASSUMPTION
    tot_lo = rail_lo + car_cost + liq_cost[0] + stor[0]
    tot_hi = rail_hi + car_cost + liq_cost[1] + stor[1]
    print(f"  {miles} mi: rail ${rail_lo:.0f}-{rail_hi:.0f}/t, car ownership ${car_cost:.1f}/t ({cars_per_mt:.0f} cars per Mt/yr),"
          f" total delivered+stored ${tot_lo:.0f}-{tot_hi:.0f}/t vs 45Q $85; transport emissions {co2_lo:.0f}-{co2_hi:.0f} kg/t"
          f" ({co2_lo/1000:.1%}-{co2_hi/1000:.1%})")
fleet = co2_pool / car_payload * (2 * 500 / 250 + 3) / 365
print(f"  Whole pool at 500 mi: fleet ~{fleet:,.0f} DOT-105 cars (~${fleet*212e3/1e9:.1f}bn)")

# ---------------------------------------------------------------------------
hdr("IDEA 4  Adipic-acid N2O used as the oxidant (benzene -> phenol / cyclododecene -> CDON)")
M_N2O_true = 0.044013
n2o_per_phenol = M_N2O_true / 0.09411
bz_per_phenol = 0.07811 / 0.09411
print(f"Stoichiometry: {n2o_per_phenol:.3f} t N2O and {bz_per_phenol:.3f} t benzene per t phenol")
w_n2o = min_separation_work(0.35, 0.90, 0.99)
print(f"Floor to enrich 35% N2O off-gas to 99% (if needed): {w_n2o/1e3:.2f} kJ/mol = {gj_per_tonne(w_n2o, M_N2O_true):.3f} GJ/t N2O"
      f" = {gj_per_tonne(w_n2o, M_N2O_true)/273*1000:.2f} MJ/t CO2e")
china_co2e = 76e6
china_n2o = china_co2e / 273
phenol_pot = china_n2o / n2o_per_phenol
print(f"China unabated adipic N2O ~{china_co2e/1e6:.0f} Mt CO2e = {china_n2o/1e6:.3f} Mt N2O -> up to {phenol_pot/1e6:.2f} Mt phenol/yr")
for ph, bz in ((1000, 1000), (1150, 875), (1300, 750)):  # $/t, ASSUMPTION price band
    gm = ph - bz_per_phenol * bz
    print(f"  phenol ${ph}, benzene ${bz}: gross margin ${gm:.0f}/t phenol = ${gm/n2o_per_phenol:.0f}/t N2O"
          f" = ${gm/n2o_per_phenol/273:.2f}/t CO2e; per t adipic acid (0.30 t N2O) ${0.30*gm/n2o_per_phenol:.0f}")
# Plant-scale economics for a 100 kt/yr adipic plant
aa = 100e3
n2o = aa * 0.30
phen = n2o / n2o_per_phenol * 0.85  # 85% N2O utilisation/selectivity ASSUMPTION
for capex in (60e6, 150e6):  # $ for small phenol unit, ASSUMPTION
    for gm in (170, 424):
        net = phen * gm - capex * crf(0.10, 15) - phen * 60  # $60/t phenol other opex ASSUMPTION
        print(f"  100 kt AA plant -> {phen/1e3:.0f} kt phenol/yr; capex ${capex/1e6:.0f}M, gm ${gm}: net ${net/1e6:+.1f}M/yr"
              f" = ${net/(n2o*0.85*273):+.2f}/t CO2e abated")
cdm = 0.30 * 310 * 15
print(f"  For comparison CDM-era credit value: 0.30 t N2O x GWP(SAR) 310 x $15 = ${cdm:.0f}/t adipic acid")
print(f"  Thermal destruction cost $0.25-4/t CO2e (NRDC 2026) = ${0.25*273:.0f}-{4*273:.0f}/t N2O")

# ---------------------------------------------------------------------------
hdr("IDEA 5  Ultramafic tailings: forced aeration with mine power-station exhaust (bio-heap-leach graft)")
tail = 11e6  # t/yr tailings, Mt Keith order of magnitude ASSUMPTION
mine_em = 0.360e6  # t CO2/yr (map: 39.8 kt = 11%)
for br in (0.005, 0.01, 0.02, 0.03):  # brucite wt%, ASSUMPTION range
    hmg = tail * br * (4 * 44.01) / (5 * 58.32)   # hydromagnesite 5Mg(OH)2 + 4CO2
    print(f"  brucite {br:.1%}: full carbonation to hydromagnesite = {hmg/1e3:.0f} kt CO2/yr = {hmg/mine_em:.0%} of mine emissions"
          f" (passive today: 39.8 kt, 11%)")
target = 100e3  # t CO2/yr to mineralise
for xco2, util in ((0.05, 0.3), (0.05, 0.6), (420e-6, 0.5)):
    mol = target * 1e6 / 44.01 / (xco2 * util)
    vol = mol * R * T0 / P0           # m3/yr at 25 C
    q = vol / (365 * 24 * 3600)
    for k in (1e-13, 1e-12, 1e-11, 1e-10):  # m2 gas permeability: silt / fine sand / agglomerated heap, ASSUMPTION
        area = 2.0e6                  # m2 aerated pad (2 km2), ASSUMPTION
        v = q / area
        dp = 1.8e-5 * v * 8.0 / k     # Darcy, 8 m stack height
        fan = q * dp / 0.6 * 365 * 24 * 3600 / (target) / 1e9   # GJ/t
        print(f"  feed {xco2*1e6 if xco2<0.01 else xco2*100:.4g}{' ppm' if xco2<0.01 else '%'} CO2, {util:.0%} uptake:"
              f" {q:,.0f} m3/s; k={k:.0e}: dP {dp:,.0f} Pa over 2 km2 x 8 m, fan {fan:.3f} GJ/t")
# Why not irrigate with carbonated water: CO2 solubility limit
kh = 0.034  # mol/L/atm at 25 C
for pco2 in (0.05, 1.0):
    gl = kh * pco2 * 44.01
    print(f"  dissolved delivery at pCO2 {pco2} atm: {gl:.2f} g/L -> {target*1e6/gl/1e3/1e6:,.0f} Mm3 water per 100 kt CO2")
print(f"  verifier comparison: DAC floor {gj_per_tonne(min_separation_work(420e-6,0.75)):.2f} GJ/t;"
      f" DAC fan 100 Pa {fan_work_gj_per_tonne(420e-6,0.75,100):.2f} GJ/t")

# ---------------------------------------------------------------------------
hdr("IDEA 6  HFC-23: refinery-style fenceline network at HCFC-22 plants")
def plume(q_gs, x_m, u):
    sy = 0.08 * x_m / math.sqrt(1 + 0.0001 * x_m)   # Briggs rural, class D
    sz = 0.06 * x_m / math.sqrt(1 + 0.0015 * x_m)
    return q_gs / (math.pi * sy * sz * u)          # g/m3, ground-level release, centreline
M_HFC23 = 70.01
bg = 37.0  # ppt, approx. 2023 global background ASSUMPTION
for ef in (0.0019, 0.01, 0.03):     # HFC-23 emitted / HCFC-22 produced; 0.19% = Rust et al. 2024 abated
    q_t = 100e3 * ef                 # t/yr for a 100 kt/yr HCFC-22 plant
    q_gs = q_t * 1e6 / (365 * 24 * 3600)
    for x_m in (500, 2000):
        c = plume(q_gs, x_m, 4.0)
        ppt = c * 1e6 * 24.45 / M_HFC23 * 1e3   # ug/m3 -> ppb -> ppt
        print(f"  EF {ef:.2%} ({q_t:,.0f} t/yr = {q_t*14600/1e6:.1f} Mt CO2e): {x_m} m downwind centreline {ppt:,.0f} ppt;"
              f" 2-week mean if downwind 15% of time ~{0.15*ppt:,.0f} ppt vs background {bg:.0f}")
gap_gg = 14.0 - 41e6 / 14600 / 1e3
print(f"Measured 14.0 Gg vs ~{41e6/14600/1e3:.1f} Gg implied by reports -> gap {gap_gg:.1f} Gg = {gap_gg*1e3*14600/1e6:.0f} Mt CO2e/yr")
for n_plants, cost in ((25, 0.15e6), (40, 0.4e6)):  # plants, $/yr per plant network, ASSUMPTION
    tot = n_plants * cost
    print(f"  {n_plants} plants x ${cost/1e6:.2f}M/yr = ${tot/1e6:.1f}M/yr -> ${tot/(gap_gg*1e3*14600):.3f} per t CO2e of the gap")

hdr("IDEA 4b  Closed loop: N2O -> phenol -> cyclohexanone/ol (KA oil) -> adipic acid")
aa_kmol = 1000 / 146.14
n2o_kmol = 300 / 44.013
ph_t = n2o_kmol * 94.11 / 1000
ka_t = n2o_kmol * 100.16 / 1000   # cyclohexanol basis
print(f"Per t adipic acid: {aa_kmol:.2f} kmol AA; N2O (0.30 t) {n2o_kmol:.2f} kmol -> {ph_t:.3f} t phenol -> {ka_t:.3f} t cyclohexanol"
      f" (KA-oil need ~1 kmol per kmol AA = {aa_kmol*100.16/1000:.3f} t). Molar N2O/AA = {n2o_kmol/aa_kmol:.2f}")
