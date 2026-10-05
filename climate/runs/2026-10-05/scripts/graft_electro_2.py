"""Verifier for graft_electro_2: SOFCs on stranded / negative-price Permian associated gas, with the
N2-free anode exhaust CO2 compressed and stored in saline formations under 45Q.

Every input is labelled: [MEAS] measured/realised, [SRC] published estimate (named), [ASSUMED] my
assumption with reason, [CLAIM] the generator's claim, unverified here. Web search budget was exhausted
during this run, so several values come from recollection and are flagged [RECALL, unverified].
"""
import math, sys
sys.path.insert(0, 'climate')
sys.path.insert(0, 'climate/runs/2026-10-05/scripts/pylib')
from physics import *
from CoolProp.CoolProp import PropsSI

H = 8760.0
def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)
def hdr(s):
    print("\n" + "=" * 92 + "\n" + s + "\n" + "=" * 92)

# ------------------------------------------------------------------------------------------------
hdr("A. Fuel: CO2 per GJ and per m3 for pure CH4 and a rich Permian-type associated gas")
# LHV (kJ/mol, standard tables) and carbon/oxygen demand per mol
SPEC = {  # name: (LHV kJ/mol, C atoms, O atoms needed for full oxidation)
    "CH4": (802.3, 1, 4), "C2H6": (1428.6, 2, 7), "C3H8": (2043.1, 3, 10), "C4H10": (2657.3, 4, 13),
    "N2": (0.0, 0, 0), "CO2": (0.0, 1, 0)}
GASES = {
    "pure CH4": {"CH4": 1.0},
    # [ASSUMED] rich wellhead associated gas, typical of Permian before NGL extraction (C2+ ~20%), with
    # 2% N2 and 1% CO2. Real compositions vary widely by well; N2 matters for CO2 purity (see B).
    "rich assoc. gas": {"CH4": 0.75, "C2H6": 0.13, "C3H8": 0.06, "C4H10": 0.03, "N2": 0.02, "CO2": 0.01},
}
MOL_PER_M3 = 101325 / (8.314462618 * 288.15)  # standard m3 at 15 C, 1 atm
fuel = {}
for name, comp in GASES.items():
    lhv = sum(x * SPEC[s][0] for s, x in comp.items())          # kJ per mol gas
    nC = sum(x * SPEC[s][1] for s, x in comp.items())
    nO = sum(x * SPEC[s][2] for s, x in comp.items())
    nN2 = comp.get("N2", 0.0)
    kg_per_gj = nC * 44.01 / lhv * 1e3
    kg_per_m3 = nC * MOL_PER_M3 * 0.04401
    fuel[name] = dict(lhv=lhv, nC=nC, nO=nO, nN2=nN2, kg_gj=kg_per_gj)
    print(f"  {name:<16} LHV {lhv:7.1f} kJ/mol = {lhv*MOL_PER_M3/1e3:5.1f} MJ/m3; {kg_per_gj:5.1f} kg CO2/GJ_LHV; "
          f"{kg_per_m3:4.2f} kg CO2/m3 (claim used 1.9)")

# ------------------------------------------------------------------------------------------------
hdr("B. Anode exhaust composition and separation floor (dry basis)")
PHI_CO = 0.3  # [ASSUMED] share of residual fuel equivalents present as CO (rest H2) after shift on cooling
for name in GASES:
    f = fuel[name]
    for uf in (0.80, 0.85, 0.90, 0.95):
        r = (1 - uf) * f["nO"]                    # mol O-equivalents of unburnt fuel per mol feed gas
        n_co = PHI_CO * r / 1.0                   # CO consumes 1 O to become CO2
        n_h2 = (1 - PHI_CO) * r
        n_co2 = f["nC"] - n_co
        dry = n_co2 + n_co + n_h2 + f["nN2"]
        x = n_co2 / dry
        w = gj_per_tonne(min_separation_work(x, 0.98, 0.99))
        o2_t = (r / 2) * 32.0 / (f["nC"] * 44.01)  # t O2 per t CO2 to oxidise residual fuel
        n2_after_oxy = f["nN2"] / (f["nC"] + f["nN2"])
        print(f"  {name:<16} Uf {uf:.0%}: dry CO2 {x:5.1%} (H2 {n_h2/dry:4.1%}, CO {n_co/dry:4.1%}, N2 {f['nN2']/dry:3.1%}); "
              f"sep. floor to 99% {w:.3f} GJ/t; O2 for oxy-polish {o2_t:.3f} t/t CO2; "
              f"N2 left after oxy-polish {n2_after_oxy:.1%}")
print("  NOTE: feed-gas N2 passes straight to the anode product. With 2% N2 in the feed the polished CO2 is "
      "~1-2% N2 before any O2-borne Ar/N2; still within typical >=95% CO2 pipeline specs, but N2 >~4-5% in "
      "the feed would need a cryogenic flash.")

# ------------------------------------------------------------------------------------------------
hdr("C. Compression floor: ideal gas vs real CO2 (CoolProp), 1 bar 25 C -> 110/150 bar")
T0_ = 298.15
h1 = PropsSI('H', 'T', T0_, 'P', 1e5, 'CO2'); s1 = PropsSI('S', 'T', T0_, 'P', 1e5, 'CO2')
for p in (110e5, 150e5):
    h2 = PropsSI('H', 'T', T0_, 'P', p, 'CO2'); s2 = PropsSI('S', 'T', T0_, 'P', p, 'CO2')
    ex = (h2 - h1 - T0_ * (s2 - s1)) / 1e6
    ig = gj_per_tonne(R * T0 * math.log(p / 1e5))
    print(f"  to {p/1e5:.0f} bar: real-CO2 exergy floor {ex:.3f} GJ/t ({ex/0.0036:.0f} kWh/t); ideal-gas isothermal "
          f"{ig:.3f} GJ/t (claim's 0.28 is the ideal-gas value: conservative, not wrong)")
COMP_FLOOR = (PropsSI('H', 'T', T0_, 'P', 150e5, 'CO2') - h1 - T0_ * (PropsSI('S', 'T', T0_, 'P', 150e5, 'CO2') - s1)) / 1e6
# [SRC, typical engineering values] multistage intercooled CO2 compression + pumping to ~110-150 bar
# is ~90-120 kWh/t in capture-plant studies (e.g. NETL baseline reports); I use 100/110/125 kWh/t.
COMP_REAL = {"low": 100 * 0.0036, "base": 110 * 0.0036, "high": 125 * 0.0036}
for k, v in COMP_REAL.items():
    print(f"  real compression {k}: {v:.3f} GJe/t -> second-law efficiency {second_law_efficiency(v, COMP_FLOOR):.0%}")

# ------------------------------------------------------------------------------------------------
hdr("D. Energy per tonne stored (electric parasitic), low/base/high, vs thermodynamic floor")
# Residual-fuel handling options:
#   low  : 'scavenger' high-Uf stage or cryogenic CO2 condensation with H2/CO recycle to anode inlet;
#          oxidation is electrochemical or recycled, so its net electric cost is ~refrigeration only [ASSUMED 0.03 GJe/t]
#   base : oxy-polish with O2 from a small cryogenic ASU at 225 kWh/t O2 [CLAIM's value; large ASUs ~200]
#   high : oxy-polish with VPSA O2 at 380 kWh/t O2 [ASSUMED; small VPSA units ~0.3-0.4 kWh/kg, 90-93% O2]
f = fuel["rich assoc. gas"]
def o2_need(uf):
    return ((1 - uf) * f["nO"] / 2) * 32.0 / (f["nC"] * 44.01)
CASES = {
    "low":  dict(uf=0.90, resid=0.03, comp=COMP_REAL["low"], dry=0.01),
    "base": dict(uf=0.85, resid=o2_need(0.85) * 225 * 0.0036, comp=COMP_REAL["base"], dry=0.02),
    "high": dict(uf=0.80, resid=o2_need(0.80) * 380 * 0.0036, comp=COMP_REAL["high"], dry=0.03),
}
FLOOR_ROUTE = COMP_FLOOR + gj_per_tonne(min_separation_work(0.70, 0.98, 0.99))
E = {}
for k, c in CASES.items():
    tot = c["resid"] + c["comp"] + c["dry"]
    E[k] = tot
    print(f"  {k:<4}: residual handling {c['resid']:.3f} + compression {c['comp']:.3f} + drying/cooling {c['dry']:.3f} "
          f"= {tot:.3f} GJe/t ({tot/0.0036:.0f} kWh/t); floor {FLOOR_ROUTE:.3f}; eta_II {FLOOR_ROUTE/tot:.0%}"
          f"{'  ** BELOW FLOOR **' if tot < FLOOR_ROUTE else ''}")
print(f"  claim 0.5-0.65 GJe/t: {'consistent' if 0.5 >= E['low'] and 0.65 <= E['high'] + 0.1 else 'check'}; "
      f"amine on NGCC flue (map, real plants) 1.0-1.4 GJe/t-equivalent")
print(f"  route floor vs NGCC 4% flue floor: {FLOOR_ROUTE:.3f} vs "
      f"{gj_per_tonne(min_separation_work(0.04, 0.9)) + COMP_FLOOR:.3f} GJ/t (sep + compression)")

# ------------------------------------------------------------------------------------------------
hdr("E. SOFC plant: emissions, heat rate, parasitic share")
ETA = {"low": 0.60, "base": 0.54, "high": 0.50}   # electrical LHV efficiency, BOL-to-average
# [MEAS] Bloom fleet, Delaware 2014 data: 823 lb CO2/MWh (Wikipedia, citing state data) -> implied eta below
implied = 3.6 * fuel["pure CH4"]["kg_gj"] / (823 * 0.4536)
print(f"  Bloom Delaware 2014 measured 823 lb/MWh = {823*0.4536/1e3:.3f} t/MWh -> implied LHV efficiency on CH4 "
      f"{implied:.1%} (older generation, realised fleet average)")
CAPT = 0.97  # [ASSUMED] share of fuel carbon stored (cathode exhaust carries no CO2; losses = vents, start-up, purge)
plant = {}
for k, eta in ETA.items():
    gj = 3.6 / eta
    t = gj * f["kg_gj"] / 1e3
    mmbtu_hhv = gj / 1.055 * 1.09   # [ASSUMED] HHV/LHV 1.09 for rich gas
    para = E[k] * t / 3.6
    plant[k] = dict(t=t, hr=mmbtu_hhv, para=para, eta=eta)
    print(f"  {k:<4} eta {eta:.0%}: {t:.3f} t CO2/MWh gross, heat rate {mmbtu_hhv:.2f} MMBtu_HHV/MWh, capture "
          f"parasitic {para:.1%} of gross output, stored {t*CAPT:.3f} t/MWh_gross")

# ------------------------------------------------------------------------------------------------
hdr("F. Incremental (attributable) capture cost vs a vent-to-air SOFC, $/t CO2 stored")
CRF = crf(0.08, 20)   # [ASSUMED] 8% real WACC, 20-yr life
print(f"  CRF(8%, 20 yr) = {CRF:.4f}")
# capex for compression+dehydration+purification, reference $ per (t/yr) at 1 Mt/yr, scaled with exponent 0.65
# [ASSUMED from typical CCS compression+conditioning costs: ~$40-90M per Mt/yr capacity at Mt scale]
CAP_REF = {"low": 45e6, "base": 65e6, "high": 95e6}
TS = {"low": 10.0, "base": 18.0, "high": 35.0}     # transport+storage $/t [SRC-ish: NETL onshore saline $7-15/t at
                                                    #  Mt scale; small single-site Class VI higher. ASSUMED range]
MRV = {"low": 2.0, "base": 4.0, "high": 8.0}       # [ASSUMED] Class VI monitoring, $/t
PWR = {"low": 40.0, "base": 55.0, "high": 75.0}    # [ASSUMED] value of parasitic electricity, $/MWh
OM_FRAC = 0.04                                      # [ASSUMED] fixed O&M 4%/yr of capture capex
inc_cost = {}
for mw in (10, 50, 200):
    row = []
    for k in ("low", "base", "high"):
        tpy = mw * H * 0.9 * plant["base"]["t"] * CAPT
        capex = CAP_REF[k] * (tpy / 1e6) ** 0.65
        cap = capex * (CRF + OM_FRAC) / tpy
        en = E[k] / 3.6 * PWR[k]
        tot = cap + en + TS[k] + MRV[k]
        inc_cost[(mw, k)] = tot
        row.append(f"{k}: ${tot:5.1f}/t (capex ${capex/1e6:5.1f}M -> ${cap:4.1f}, energy ${en:4.1f}, T&S {TS[k]:.0f}, MRV {MRV[k]:.0f})")
    print(f"  {mw:>3} MW site ({mw*H*0.9*plant['base']['t']*CAPT/1e3:,.0f} kt/yr): " + " | ".join(row))
# 45Q levelised: $85/t for 12 years over a 20-yr asset
q45_lev = 85 * (1 - (1.08) ** -12) / 0.08 / ((1 - (1.08) ** -20) / 0.08)
print(f"  45Q $85/t nominal for 12 yr only -> levelised over 20 yr at 8%: ${q45_lev:.1f}/t "
      f"(claim used full $85 every year)")

# ------------------------------------------------------------------------------------------------
hdr("G. Full-system LCOE ($/MWh net) with gas-price scenarios, net of 45Q")
SOFC_CAPEX = {"low": 2500.0, "base": 3500.0, "high": 5000.0}  # $/kW installed [ASSUMED; claim 2,500-4,500.
#   Vendor list prices are not public; historic Bloom installs were well above $5,000/kW; DOE targets ~$900/kW]
STACK = {"low": 600.0, "base": 1000.0, "high": 1500.0}        # $/kW per stack swap [ASSUMED]
STACK_LIFE_YR = {"low": 6.0, "base": 5.0, "high": 4.0}        # [ASSUMED; 5-yr stack life commonly cited]
FOM = {"low": 8.0, "base": 12.0, "high": 18.0}                # $/MWh non-stack O&M [ASSUMED]
CF = 0.90
GAS = {"Waha constrained (-2.38, CLAIM, transient)": -2.38, "zero": 0.0,
       "Waha after debottleneck (+1.5)": 1.5, "Waha ~HH-0.9 (+2.5)": 2.5}
# EIA STEO Sep 2026 [SRC]: Henry Hub 2026 forecast $3.43/MMBtu; Hugh Brinson (Permian) began flowing June 2026,
# ramping through early 2027 -> negative Waha prices are not bankable over a 20-yr asset.
lcoe = {}
for k in ("low", "base", "high"):
    p = plant[k]
    net = 1 - p["para"]
    cap = SOFC_CAPEX[k] * 1e3 * CRF / (H * CF)
    stack = STACK[k] * 1e3 / (STACK_LIFE_YR[k] * H * CF)
    capt = inc_cost[(50, k)] * p["t"] * CAPT
    q = q45_lev * p["t"] * CAPT
    for gname, g in GAS.items():
        fuelc = g * p["hr"]
        tot = (cap + stack + FOM[k] + capt + fuelc) / net
        lcoe[(k, gname)] = dict(gross=tot, net=(cap + stack + FOM[k] + capt + fuelc - q) / net, noq=tot)
    print(f"  {k:<4}: capital ${cap:.0f} + stacks ${stack:.0f} + O&M ${FOM[k]:.0f} + capture ${capt:.0f} per MWh_gross; "
          f"45Q credit -${q:.0f}; parasitic {p['para']:.1%}")
    for gname, g in GAS.items():
        d = lcoe[(k, gname)]
        print(f"        gas {gname:<42}: LCOE ${d['noq']:6.1f}/MWh before 45Q, ${d['net']:6.1f} after 45Q")
pre_fuel_claim_check = [(c * 0.10 / (H * 0.9) * 1e3 + om) for c, om in ((2500, 15), (4500, 30))]
print(f"  claim check: pre-fuel ${pre_fuel_claim_check[0]:.0f}-{pre_fuel_claim_check[1]:.0f}/MWh reproduces the claim's "
      f"$47-87, but omits capture-train capex, T&S and MRV (~${inc_cost[(50,'low')]*0.35:.0f}-"
      f"{inc_cost[(50,'high')]*0.38:.0f}/MWh) and uses undiscounted full-life 45Q.")

# ------------------------------------------------------------------------------------------------
hdr("H. Cost per t CO2e AVOIDED, three counterfactuals (no subsidy = social cost; 45Q is a transfer)")
# Counterfactual 1: the same firm load served by on-site unabated gas engines/turbines (the Permian data-centre case)
GEN_CAPEX = {"low": 1500.0, "base": 2000.0, "high": 2500.0}   # $/kW [ASSUMED, 2025-26 turbine/recip market]
GEN_HR = {"low": 8.5, "base": 9.0, "high": 9.8}                # MMBtu_HHV/MWh [ASSUMED recip/aero range]
GEN_OM = 10.0                                                  # $/MWh [ASSUMED]
KG_MMBTU = 53.06 * 1.03                                        # EPA natural gas 53.06 kg/MMBtu, +3% for rich gas
cost_avoided = {}
for k in ("low", "base", "high"):
    p = plant[k]
    gname = "Waha after debottleneck (+1.5)"
    g = GAS[gname]
    gen = GEN_CAPEX[k] * 1e3 * CRF / (H * CF) + GEN_OM + g * GEN_HR[k]
    e_gen = GEN_HR[k] * KG_MMBTU / 1e3
    e_sofc = p["t"] * (1 - CAPT) / (1 - p["para"])
    d = (lcoe[(k, gname)]["noq"] - gen) / (e_gen - e_sofc)
    cost_avoided[("genset", k)] = d
    print(f"  CF1 vs on-site gas genset, {k}: genset ${gen:.0f}/MWh, {e_gen:.3f} t/MWh; SOFC+CCS "
          f"${lcoe[(k, gname)]['noq']:.0f}/MWh, {e_sofc:.3f} t/MWh -> ${d:.0f}/t CO2e avoided (gas +$1.5)")
# sensitivity: with the claim's negative gas price the SOFC's higher efficiency earns LESS (it takes less paid gas)
k = "base"; gname = "Waha constrained (-2.38, CLAIM, transient)"
gen = GEN_CAPEX[k] * 1e3 * CRF / (H * CF) + GEN_OM + GAS[gname] * GEN_HR[k]
e_gen = GEN_HR[k] * KG_MMBTU / 1e3
print(f"  CF1 base at -$2.38 gas: genset ${gen:.0f}/MWh vs SOFC+CCS ${lcoe[(k, gname)]['noq']:.0f} -> "
      f"${(lcoe[(k, gname)]['noq'] - gen)/(e_gen - plant[k]['t']*(1-CAPT)):.0f}/t avoided "
      f"(negative gas price rewards BURNING MORE gas, so it favours the inefficient genset)")

# Counterfactual 2: gas otherwise flared. [MEAS] Plant et al. 2022 (Science): flares in Permian, Eagle Ford, Bakken
# had an effective destruction efficiency ~91% incl. unlit/malfunctioning flares (aerial survey, measured).
DE = 0.911
for k in ("low", "base", "high"):
    p = plant[k]
    # per MWh net of SOFC output, gas use = heat rate; flare same gas instead
    gas_gj = 3.6 / p["eta"] / (1 - p["para"])
    nC = f["nC"]
    co2_full = gas_gj * f["kg_gj"] / 1e3
    # unburnt hydrocarbon slip as CH4-equivalent mass: approx slip fraction of carbon as CH4
    ch4_slip_t = co2_full * (1 - DE) * 16.04 / 44.01
    flare_e = co2_full * DE + ch4_slip_t * GWP100["CH4_fossil"]
    grid = {"low": 0.30, "base": 0.37, "high": 0.42}[k]  # [ASSUMED] ERCOT marginal/avg t/MWh, 2024-26 range
    avoided = flare_e + grid - co2_full * (1 - CAPT)
    power_value = {"low": 70.0, "base": 55.0, "high": 40.0}[k]  # [ASSUMED] realised $/MWh for firm power sold
    for gname in ("zero", "Waha after debottleneck (+1.5)"):
        c = (lcoe[(k, gname)]["noq"] - power_value) / avoided
        cost_avoided[("flare", k, gname)] = c
    print(f"  CF2 flare (DE {DE:.1%}), {k}: flare {flare_e:.2f} t CO2e/MWh-equiv (of which CH4 slip "
          f"{ch4_slip_t*GWP100['CH4_fossil']:.2f}) + grid {grid:.2f} -> avoided {avoided:.2f} t/MWh; "
          f"cost ${cost_avoided[('flare', k, 'zero')]:.0f}/t at $0 gas, ${cost_avoided[('flare', k, 'Waha after debottleneck (+1.5)')]:.0f}/t at +$1.5 "
          f"(power sold at ${power_value:.0f}/MWh)")

# Counterfactual 3: gas would otherwise reach market and be burned unabated anyway; SOFC power displaces grid power.
for k in ("low", "base", "high"):
    p = plant[k]
    grid = {"low": 0.42, "base": 0.37, "high": 0.30}[k]
    gas_gj = 3.6 / p["eta"] / (1 - p["para"])
    co2_full = gas_gj * f["kg_gj"] / 1e3
    # avoided = CO2 stored (the gas's carbon is now sequestered instead of burned elsewhere) + nothing for grid,
    # because the same gas no longer burns elsewhere means elsewhere burns other gas: count stored CO2 only,
    # plus the grid displacement minus the gas the plant diverts (assume the diverted gas would have made
    # electricity at 0.37 t/MWh-equivalent efficiency elsewhere): net ~ stored CO2.
    stored = co2_full * CAPT
    power_value = {"low": 70.0, "base": 55.0, "high": 40.0}[k]
    c = (lcoe[(k, "Waha after debottleneck (+1.5)")]["noq"] - power_value) / stored
    cost_avoided[("market", k)] = c
    print(f"  CF3 gas would reach market, {k}: stored {stored:.3f} t/MWh; net cost ${c:.0f}/t stored at +$1.5 gas, "
          f"power sold at ${power_value:.0f}/MWh")

# ------------------------------------------------------------------------------------------------
hdr("I. Rebound: oil production unlocked by a local gas outlet (confound the idea flags)")
GOR = 27e9 / 6.6e6   # [ASSUMED from EIA-scale figures: Permian ~27 bcf/d gas, ~6.6 Mb/d oil in 2025-26] cf/bbl
print(f"  Permian GOR ~{GOR:,.0f} cf/bbl")
for frac in (0.0, 0.1, 0.3, 1.0):
    bbl_d = frac * 1e9 / GOR
    co2 = bbl_d * 365 * 0.43 / 1e6        # 0.43 t CO2/bbl combusted [SRC: EPA GHG equivalencies]
    net = co2 * 0.5                        # [SRC, modelled] ~0.5 bbl consumption per extra bbl supplied
    print(f"  share of 1 bcf/d that unlocks otherwise-curtailed oil {frac:>4.0%}: {bbl_d/1e3:,.0f} kb/d oil -> "
          f"{co2:5.1f} Mt CO2 combusted, ~{net:5.1f} Mt net of market leakage (vs ~20 Mt stored)")

# ------------------------------------------------------------------------------------------------
hdr("J. Scale and resources")
bcm = 1e9 * 0.0283168 * 365 / 1e9
for gname in ("pure CH4", "rich assoc. gas"):
    # Waha prices PROCESSED residue gas (NGLs removed, ~CH4); rich gas applies only at an unprocessed wellpad
    fg = fuel[gname]
    gj = bcm * 1e9 * fg["lhv"] * MOL_PER_M3 / 1e6
    co2_mt = gj * fg["kg_gj"] / 1e9 * CAPT
    twh = gj * ETA["base"] / 3.6 / 1e6
    print(f"  1 bcf/d {gname}: {bcm:.2f} bcm/yr = {gj/1e9:.3f} EJ_LHV -> {twh:.0f} TWh/yr gross at 54%, "
          f"{twh/8.76:.1f} GW avg; stored {co2_mt:.1f} Mt/yr (claim: ~20 Mt, 58 TWh at 57%)")
# global flaring [RECALL, unverified this session: World Bank GGFR 2025 tracker ~151 bcm flared in 2024]
fl = 151.0
print(f"  ceiling A: all global flared gas ({fl:.0f} bcm/yr, RECALL) -> {co2_mt/bcm*fl:.0f} Mt/yr stored "
      f"(mostly Russia/Iran/Iraq/Algeria/Venezuela/Nigeria, outside 45Q)")
# gas-fired SOFC fleet scenarios (data centres etc.)
for gw in (5, 20, 60):
    mt = gw * 1e3 * H * CF * plant["base"]["t"] * CAPT / 1e6
    print(f"  {gw:>3} GW SOFC+capture fleet at CF 90%: {mt:6.1f} Mt/yr")
gas_power_twh = 6600.0  # [ASSUMED ~Ember 2024 global gas generation]
print(f"  ceiling B: all global gas power ({gas_power_twh:,.0f} TWh) via SOFC+capture: "
      f"{gas_power_twh*1e6*plant['base']['t']*CAPT/1e9:.2f} Gt/yr stored (manufacturing-limited: today ~1-2 GW/yr)")
nH = sum(x * {"CH4":4,"C2H6":6,"C3H8":8,"C4H10":10}.get(sp,0) for sp, x in GASES["rich assoc. gas"].items())
h2o_per_co2 = (nH / 2) * 18.02 / (f["nC"] * 44.01)
print(f"  water produced: {h2o_per_co2:.2f} t H2O per t CO2")
for gt in (0.02, 0.05, 0.15):
    s = ScaleCheck(gt, E["base"])
    water = gt * 1e9 * h2o_per_co2  # mass ratio from fuel H/C, all fuel H leaves as H2O
    print(f"  {gt:.2f} Gt/yr: parasitic {s.ej_per_year:.3f} EJ_e = {s.share_of_world_electricity_if_electric:.3%} of world "
          f"electricity; SOFC output {gt*1e9/plant['base']['t']/1e6:,.0f} TWh/yr; water PRODUCED ~{water/1e9:.2f} Gt/yr; "
          f"Class VI wells at 0.5 Mt/yr each: {gt*1e3/0.5:.0f}")
print("  land: [ASSUMED] ~100-250 m2/MW for packaged SOFC + capture skid -> 20 GW ~ 2-5 km2 (negligible)")
print("  materials: Ni (anode), ZrO2 with Y or Sc dopant (electrolyte), La/Sr/Co/Mn perovskites (cathode), "
      "ferritic steel interconnects; scandium supply (tens of t/yr globally) is a flagged risk if ScSZ is used at GW scale")
