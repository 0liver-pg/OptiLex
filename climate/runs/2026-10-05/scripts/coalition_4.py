"""coalition_4 verifier: clinker process-CO2 phasedown with storage-only compliance.

Every input is labelled: [MEAS] measured/realized, [SRC] published source read this session,
[MOD] modelled literature estimate, [MEM] from memory (verify before quoting), [ASSUME] assumption.
"""
import sys, math
sys.path.insert(0, 'climate')
from physics import *
sys.path.append('climate/runs/2026-10-05/scripts/pylib')
try:
    from CoolProp.CoolProp import PropsSI
except Exception:
    PropsSI = None

def hdr(s): print("\n" + "=" * 100 + "\n" + s + "\n" + "=" * 100)
def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)

# ---------------------------------------------------------------------------------------------
hdr("1. PROCESS CO2 STOICHIOMETRY AND GLOBAL TARGET")
cao, mgo = 0.65, 0.015            # [MEM] typical clinker oxide content (IPCC default ~0.52-0.525 t/t)
proc = cao * 44.01 / 56.08 + mgo * 44.01 / 40.30
print(f"Process CO2 per t clinker: {proc:.3f} t (CaO {cao:.0%}, MgO {mgo:.1%}); IPCC/CSI default ~0.525 [MEM]")
for cr in (0.71, 0.63, 0.57, 0.50):
    print(f"  clinker ratio {cr:.2f}: {proc*cr:.3f} t process CO2/t cement")
# IEA NZR 2023 milestones table [SRC nzr.txt]: cement Mt and clinker ratio
iea = {2022: (4160, 0.71), 2030: (4260, 0.65), 2035: (4140, 0.61), 2050: (3930, 0.57)}
iea_captured = {2022: 0, 2030: 170, 2035: 480, 2050: 1310}  # Mt CO2 captured, all cement CO2 (process+fuel) [SRC]
for y, (mt, cr) in iea.items():
    print(f"  IEA NZE {y}: cement {mt} Mt, clinker {cr} -> process CO2 {mt*cr*proc/1e3:.2f} Gt; "
          f"NZE CO2 captured (all cement CO2) {iea_captured[y]} Mt")
base_proc = 4.0 * 0.71 * proc
print(f"Idea's target: 4.0 Gt cement x 0.71 x {proc:.3f} = {base_proc:.2f} Gt/yr (claim 1.50) -> CONSISTENT")

# ---------------------------------------------------------------------------------------------
hdr("2. THERMODYNAMIC FLOORS (verifier, ideal gas) + real-gas compression check")
floors = {}
for label, x, f, p in [("kiln flue 25% CO2", 0.25, 0.9, 0.99), ("kiln flue 20% CO2", 0.20, 0.9, 0.99),
                       ("kiln flue 15% CO2 (air in-leak, low end)", 0.15, 0.9, 0.99),
                       ("Leilac-type stream 95% CO2", 0.95, 0.9, 0.999)]:
    floors[label] = gj_per_tonne(min_separation_work(x, f, p))
    print(f"  separation floor {label}, 90% capture: {floors[label]:.4f} GJ/t")
comp_ideal = R * T0 * math.log(150e5 / P0) / M_CO2 / 1e6
print(f"  isothermal ideal-gas compression 1.013->150 bar at 25C: {comp_ideal:.3f} GJ/t")
comp_real = None
if PropsSI:
    h0, s0 = PropsSI('H', 'T', T0, 'P', P0, 'CO2'), PropsSI('S', 'T', T0, 'P', P0, 'CO2')
    h1, s1 = PropsSI('H', 'T', T0, 'P', 150e5, 'CO2'), PropsSI('S', 'T', T0, 'P', 150e5, 'CO2')
    comp_real = ((h1 - h0) - T0 * (s1 - s0)) / 1e6  # J/kg -> GJ/t (flow exergy change)
    print(f"  real-gas (Span-Wagner, CoolProp) flow-exergy rise to 150 bar/25C: {comp_real:.3f} GJ/t "
          f"({comp_real/comp_ideal:.0%} of ideal-gas value; CO2 condenses, so ideal gas OVERSTATES the floor)")
floor_total_ideal = floors["kiln flue 25% CO2"] + comp_ideal
floor_total_real = floors["kiln flue 25% CO2"] + (comp_real if comp_real else comp_ideal)
print(f"  Floor sep(25%)+compression: ideal {floor_total_ideal:.3f} GJ/t (claim 0.39); real-gas {floor_total_real:.3f} GJ/t")

# ---------------------------------------------------------------------------------------------
hdr("3. REAL ENERGY PER TONNE CAPTURED (low/base/high) AND SECOND-LAW EFFICIENCY")
# Reboiler duty: [MOD] advanced solvents 2.4-2.7 GJ/t; MEA 3.4-3.7 GJ/t (CEMCAP/IEAGHG modelled); Brevik not published [MEM]
# Electricity: compression to ~110-150 bar + blowers + pumps [MOD/MEM] ~90-140 kWh/t
cases = {"low": dict(q=2.4, T=393.15, kwh=90), "base": dict(q=3.0, T=393.15, kwh=115), "high": dict(q=3.7, T=403.15, kwh=140)}
energy = {}
for k, c in cases.items():
    ex_heat = c['q'] * (1 - T0 / c['T'])
    el = c['kwh'] * 0.0036
    tot_final = c['q'] + el
    tot_ex = ex_heat + el
    energy[k] = (c['q'], el, tot_final, tot_ex)
    print(f"  {k:4s}: heat {c['q']:.1f} GJ_th/t @ {c['T']-273.15:.0f}C (exergy {ex_heat:.2f}) + elec {c['kwh']} kWh ({el:.2f} GJ_e) "
          f"= {tot_final:.2f} GJ final/t, {tot_ex:.2f} GJ exergy/t; eta_II(sep+comp, ideal floor) {floor_total_ideal/tot_ex:.0%}; "
          f"sep-only eta_II {floors['kiln flue 25% CO2']/ex_heat:.0%}")
print(f"  Claim (3): 3 GJ_th at 120C -> exergy {3*(1-T0/393.15):.2f} GJ/t, separation eta_II "
      f"{floors['kiln flue 25% CO2']/(3*(1-T0/393.15)):.0%} -> CONSISTENT (claim ~0.72, ~15%)")
any_below = any(e[3] < floor_total_real for e in energy.values())
print(f"  Any case below thermodynamic floor? {any_below}")

# ---------------------------------------------------------------------------------------------
hdr("4. COST PER TONNE (capture + T&S), low/base/high")
CF = 0.90           # [ASSUME] kiln availability ~330 d/yr
r, n = 0.08, 25     # [ASSUME] WACC 8%, 25 yr
# Capex per (t/yr): Brevik FOAK ~EUR421m / 400 kt/yr = ~EUR1,050 per t/yr [prior-session figure, MEM, verify];
# NOAK modelled lower. Low 450, base 750, high 1,100.
capex = {"low": 450, "base": 750, "high": 1100}
fom = 0.04          # fixed O&M share of capex/yr [ASSUME]
waste_heat_share = {"low": 0.5, "base": 0.3, "high": 0.1}   # Brevik covers ~50% capture from waste heat [MEM];
                                                            # at 90% capture the share falls [ASSUME]
heat_price = {"low": 8, "base": 13, "high": 22}             # EUR/GJ_th: gas boiler ~25 EUR/MWh gas / heat pump / e-boiler @70 EUR/MWh [ASSUME]
el_price = {"low": 50, "base": 75, "high": 110}             # EUR/MWh [ASSUME, EU industrial 2025-26 range]
solvent = {"low": 2, "base": 4, "high": 8}                  # EUR/t makeup + waste [MOD]
ts = {"low": 15, "base": 45, "high": 80}                    # EUR/t: low = onshore pipeline + Class VI/Porthos-type;
                                                            # base = ship to North Sea (Northern Lights-type; tariffs undisclosed) [MOD/MEM]
mrv = {"low": 1, "base": 2, "high": 4}
cost_capt = {}
for k in ("low", "base", "high"):
    cc = capex[k] * crf(r, n) / CF
    om = capex[k] * fom / CF
    q, el, _, _ = energy[k]
    heat = q * (1 - waste_heat_share[k]) * heat_price[k]
    elc = el / 3.6 * el_price[k]
    tot = cc + om + heat + elc + solvent[k] + ts[k] + mrv[k]
    # avoided vs captured: heat/electricity emissions (if fossil) reduce net; base assumes low-carbon power/heat
    em_kg = {"low": 0.0, "base": 0.03, "high": 0.10}[k]  # t CO2 emitted per t captured by energy supply [ASSUME]
    cost_capt[k] = (tot, tot / (1 - em_kg))
    print(f"  {k:4s}: capex EUR{capex[k]}/(t/yr) -> capital {cc:.0f} + FOM {om:.0f} + heat {heat:.0f} + elec {elc:.0f} "
          f"+ solvent {solvent[k]} + T&S {ts[k]} + MRV {mrv[k]} = EUR{tot:.0f}/t captured; "
          f"EUR{cost_capt[k][1]:.0f}/t avoided (energy-supply emissions {em_kg:.2f} t/t)")
print("  Idea claims EUR100-150/t. Realized anchor: Denmark CCS fund award to Orsted (2023, biogenic CHP, not cement):")
dkk_award, kt, yrs, dkk_eur = 8.0e9, 430e3, 20, 0.134   # [MEM] DKK 8.0bn, 0.43 Mt/yr, 20 yr
print(f"    DKK 8.0bn / ({kt/1e3:.0f} kt x {yrs} yr) = DKK {dkk_award/(kt*yrs):.0f}/t = EUR{dkk_award/(kt*yrs)*dkk_eur:.0f}/t "
      f"public subsidy (undiscounted) on top of any ETS value [MEM]")
print("  Note: Brevik and Northern Lights were largely state-funded (Longship ~NOK 25bn plan, 2021) [SRC Wikipedia] -> "
      "the 'no subsidy' design has no unsubsidized realized precedent yet")

# ---------------------------------------------------------------------------------------------
hdr("5. METRIC CONSISTENCY: per-t-clinker cap vs clinker-substitution credit")
print("  A cap on process CO2 PER TONNE OF CLINKER is unchanged by the clinker ratio (always ~0.526 t/t unabated).")
print("  -> LC3/clinker-ratio compliance (b) needs a conversion rule (credit = clinker avoided x 0.526) or an "
      "absolute/per-t-cement metric. As written, (b) does not move the stated metric.")
for y, target in ((2035, 0.30), (2050, 0.90)):
    mt, cr = iea[y]
    cem_metric = (0.71 * proc)
    via_cr = 1 - cr / 0.71
    need_store_per_t_cement = max(0.0, (1 - target) * 0 + (cr * proc) - (1 - target) * cem_metric)
    stored_global = need_store_per_t_cement * mt / 1e3
    stored_per_clinker_metric = target * mt * cr * proc / 1e3
    print(f"  {y} target -{target:.0%}: clinker 0.71->{cr} alone gives -{via_cr:.0%} per t cement; "
          f"storage needed (per-t-cement metric) {stored_global:.2f} Gt/yr; (per-t-clinker metric) {stored_per_clinker_metric:.2f} Gt/yr "
          f"vs IEA NZE all-cement capture {iea_captured[y]/1e3:.2f} Gt")

# ---------------------------------------------------------------------------------------------
hdr("6. PRICE PASS-THROUGH: cement price and building cost (claim <1%)")
for k in ("low", "base", "high"):
    c = cost_capt[k][1]
    for cr in (0.71, 0.50):
        per_t_cem = c * proc * cr * 0.9
        print(f"  {k:4s} EUR{c:.0f}/t on 90% of process CO2, clinker {cr}: +EUR{per_t_cem:.0f}/t cement")
build = {"EU mid-rise EUR2,000/m2": 2000, "EU low-cost EUR1,200/m2": 1200, "Global South EUR400/m2": 400}
for c in (100, 150, cost_capt["high"][1]):
    per_t_cem = c * proc * 0.71 * 0.9
    for lbl, bc in build.items():
        lo, hi = per_t_cem * 0.15 / bc, per_t_cem * 0.30 / bc
        print(f"  EUR{c:.0f}/t, 0.15-0.30 t cement/m2 [ASSUME], {lbl}: {lo:.2%}-{hi:.2%} of build cost")
cement_price = {"EU ex-works ~EUR120/t [MEM]": 120, "India ~EUR75/t [MEM]": 75}
for c in (100, 150):
    per_t_cem = c * proc * 0.71 * 0.9
    for lbl, p in cement_price.items():
        print(f"  EUR{c}/t -> +EUR{per_t_cem:.0f}/t = +{per_t_cem/p:.0%} on cement price, {lbl}")

# ---------------------------------------------------------------------------------------------
hdr("7. STORAGE COMMONS (Gidden et al. 2025 Nature: 1,460 (1,290-2,710) Gt prudent limit [SRC abstract])")
for lim in (1290, 1460, 2710):
    for yrs in (100,):
        used = base_proc * yrs
        print(f"  ALL process CO2 ({base_proc:.2f} Gt/yr) x {yrs} yr = {used:.0f} Gt = {used/lim:.1%} of {lim} Gt")
used_nze = sum([0.48] * 15 + [1.31] * 50) * 0.6   # process share ~60% of NZE captured [ASSUME]
print(f"  More realistic: process share (~60%) of NZE capture path 2035-2100: ~{used_nze:.0f} Gt = {used_nze/1460:.1%} of 1,460")
for gt in (8.7, 15):
    print(f"  At {gt} Gt/yr total CCS (idea's figure; source not verified this session): limit exhausted in {1460/gt:.0f} yr")

# ---------------------------------------------------------------------------------------------
hdr("8. REALISTIC SCALE (Gt CO2 abated/yr, process CO2 only) BY ADOPTION FOOTPRINT")
# Cement production, approx 2023-24 [MEM, USGS order of magnitude]
blocs = {"EU27+UK+NO+CH": 0.19, "US": 0.09, "Canada+Japan+Korea+Aus": 0.11, "China": 1.9, "India": 0.45, "Rest": 1.26}
print(f"  sum of blocs {sum(blocs.values()):.2f} Gt cement (check vs 4.0)")
scen = {"low (EU-led club only)": ["EU27+UK+NO+CH"],
        "base (EU+US+OECD-Asia club)": ["EU27+UK+NO+CH", "US", "Canada+Japan+Korea+Aus"],
        "high (club + China ETS alignment)": ["EU27+UK+NO+CH", "US", "Canada+Japan+Korea+Aus", "China"]}
for name, bl in scen.items():
    cem = sum(blocs[b] for b in bl)
    for y, target, cr in ((2035, 0.30, 0.61), (2050, 0.90, 0.57)):
        ab = cem * 0.71 * proc * target   # abatement relative to today's per-t-cement process intensity
        print(f"  {name:36s} {y}: {cem:.2f} Gt cement, -{target:.0%} -> {ab:.3f} Gt CO2/yr process abatement")
print("  Border adjustment adds little: global cement trade is a few % of production [MEM]")

# ---------------------------------------------------------------------------------------------
hdr("9. RESOURCE NEEDS at high scale (stored process CO2 S Gt/yr)")
for S in (0.10, 0.45, 1.35):
    q, el, _, _ = energy["base"]
    heat_ej = S * q
    el_twh = S * 1e9 * el / 3.6 / 1e6 * 1e3 / 1e9 * 1e3  # GJ->MWh->TWh
    el_twh = S * 1e9 * el * 1e9 / 3.6e15
    sc = ScaleCheck(S, q + el)
    water = (0.5 * S, 2.0 * S)          # km3/yr at 0.5-2 m3/t cooling+process water [ASSUME]
    amine = (0.3 * S, 1.5 * S)          # Mt/yr amine makeup at 0.3-1.5 kg/t [MOD]
    wells = (S * 1e3 / 1.0, S * 1e3 / 0.5)  # 0.5-1 Mt/yr per injector [MEM, Sleipner ~1 Mt/yr]
    plume = S * 25 * 1e9 / (1e6 * 50 * 0.2 * 0.03 * 0.70)  # km2 plume footprint over 25 yr (50 m, 20% phi, 3% eff) [ASSUME]
    print(f"  S={S:.2f} Gt/yr: heat {heat_ej:.2f} EJ + elec {el_twh:.0f} TWh ({el_twh/WORLD_ELECTRICITY_TWH:.2%} of world elec); "
          f"total {sc.ej_per_year:.2f} EJ = {sc.share_of_world_primary_energy:.2%} of world primary; water {water[0]:.2f}-{water[1]:.2f} km3/yr; "
          f"amine {amine[0]:.2f}-{amine[1]:.2f} Mt/yr; injectors {wells[0]:.0f}-{wells[1]:.0f}; 25-yr plume ~{plume:,.0f} km2 (subsurface)")
fl = ScaleCheck(1.35, floor_total_real)
print(f"  Floor at 1.35 Gt/yr: {fl.ej_per_year:.2f} EJ = {fl.share_of_world_primary_energy:.2%} of world primary")
print(f"  Claim (4): 90% of 1.50 Gt at 3 GJ/t = {0.9*base_proc*3:.1f} EJ = {0.9*base_proc*3/WORLD_PRIMARY_ENERGY_EJ:.2%} -> CONSISTENT; "
      f"ideal floor {0.9*base_proc*floor_total_ideal:.2f} EJ")

hdr("VERDICT FLAGS")
print(f"  Below floor? {any_below}.  Global -30% by 2035 needs ~0.4 Gt/yr stored process CO2 (> IEA NZE 0.48 Gt all-cement "
      f"capture, which IEA says announced projects miss) -> heroic globally; plausible as an EU/OECD club measure.")
EURUSD = 1.15  # [ASSUME] ~2025-26 exchange rate
print("  USD/t CO2 avoided at 1.15 USD/EUR: " + ", ".join(f"{k} ${v[1]*EURUSD:.0f}" for k, v in cost_capt.items()))
print(f"  Process-CO2 share (~60%) of IEA NZE 2035 capture: {0.48*0.6:.2f} Gt vs 0.40 (per-t-clinker) / 0.25 (per-t-cement) needed")
