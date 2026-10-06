import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

print("=== shared: fade rate -> sorbent cost (OptiLex sorbent_cost_per_tonne, 20% end-of-life loss, life-average capacity 90%) ===")
def fade_cost(fade_pct_per_cycle, price=20.0, wc=1.04, eol=20.0):
    cycles = eol / fade_pct_per_cycle
    return cycles, sorbent_cost_per_tonne(price, wc * (1 - eol / 200.0), cycles)
for f in (5.1e-3, 3.5e-3, 2.2e-3, 1.1e-3, 7.3e-4, 2.2e-4):
    c, cost = fade_cost(f)
    c50, cost50 = fade_cost(f, price=50.0)
    print(f"  fade {f:.1e} %/cycle -> {c:,.0f} cycles to 20% loss -> ${cost:.0f}/t at $20/kg, ${cost50:.0f}/t at $50/kg (wc 1.04 mol/kg)")

print("\n=== IDEA A: ppb acid gases as a lifetime floor; sacrificial bicarbonate guard layer ===")
cap = 0.75
V = air_volume_per_tonne(X_AIR, cap)
n_air = P0 / (R * T0)  # mol/m3
mol_co2_per_t = 1e3 / M_CO2  # 1 t = 1000 kg
print(f"air per tonne CO2 at {cap:.0%} capture: {V:,.0f} m3 ({V*n_air/1e3:,.0f} kmol)")
acid_capture = 0.95
per_ppb = 1e-9 * n_air * V * acid_capture  # mol acid per t CO2 per ppb
per_ppb_per_mol = per_ppb / mol_co2_per_t
print(f"1 ppb of a strong acid gas captured at {acid_capture:.0%}: {per_ppb:.3f} mol per t CO2 = {per_ppb_per_mol:.2e} mol per mol CO2")
print(f"  -> fraction of WORKING capacity neutralised per cycle (1 site per eq, independent of capacity): {per_ppb_per_mol*100:.1e} %/cycle per ppb-eq")
# scenarios: (SO2 ppb, HNO3 ppb, HCl ppb, NO2 ppb, NO2 uptake fraction relative to SO2-like capture)
scen = {
    "rural US 2022-24 (CASTNET total nitrate 0.6-1.2 ug/m3 ~0.25-0.5 ppb; SO2 0.3; HCl 0.1; NO2 2 @5%)": (0.3, 0.4, 0.1, 2.0, 0.05),
    "suburban US/EU 2020s (SO2 1, HNO3 1, HCl 0.3, NO2 10 @5%)": (1.0, 1.0, 0.3, 10.0, 0.05),
    "industrial / port (SO2 5, HNO3 2, HCl 0.5, NO2 20 @5%)": (5.0, 2.0, 0.5, 20.0, 0.05),
    "geothermal-type site, SO2-equivalent 10 ppb from H2S oxidation (illustrative)": (10.0, 0.5, 0.1, 2.0, 0.05),
}
for name, (so2, hno3, hcl, no2, f_no2) in scen.items():
    # SO2 ends as sulfite/sulfate: 2 eq (sulfate) upper, 1 eq (bisulfite/sulfonamide) lower
    eq_hi = 2 * so2 + hno3 + hcl + f_no2 * no2
    eq_lo = 1 * so2 + hno3 + hcl + f_no2 * no2
    rate_hi = eq_hi * per_ppb_per_mol * 100
    rate_lo = eq_lo * per_ppb_per_mol * 100
    # mild bound: acids neutralise N at random among total N (PEI-type 10 mol N/kg, working 1.04)
    mild = rate_lo * 1.04 / 10.0
    c_hi, cost_hi = fade_cost(rate_hi)
    print(f"  {name}: {eq_lo:.2f}-{eq_hi:.2f} ppb-eq -> {rate_lo:.1e}-{rate_hi:.1e} %/cycle if acids take working sites "
          f"(mild bound, random N among 10 mol N/kg: {mild:.1e}); acid-only life to 20% loss {20/rate_hi:,.0f}-{20/rate_lo:,.0f} cycles")
print("  compare: target fade 1.1e-3 %/cycle (20% over 20,000 cycles); best measured engineered amine 2.2e-3 (TDA/GE, lab air, 500 ppm)")
print("  moisture-swing QA (carbonate<->bicarbonate, 0.5 CO2 per N+): each eq removes 0.5 mol CO2 of capacity -> half the rates above")
# guard layer sizing and cost
for eq_ppb in (2.0, 5.0, 12.0):
    eq_per_t = eq_ppb * per_ppb
    for guard_cap, price in ((1.5, 2.0), (3.0, 5.0)):
        kg = eq_per_t / guard_cap
        print(f"  guard for {eq_ppb:>4} ppb-eq: {eq_per_t:.2f} eq/t CO2 -> {kg*1e3:.0f} g guard/t at {guard_cap} eq/kg usable, "
              f"${kg*price:.2f}/t at ${price}/kg (single use)")
for dp in (10, 20, 40):
    gj = fan_work_gj_per_tonne(X_AIR, cap, dp)
    print(f"  guard pressure drop {dp} Pa -> fan {gj:.3f} GJ/t = ${energy_cost_floor(gj, 50):.2f}/t at $50/MWh")
c_now, cost_now = fade_cost(2.2e-3); c_minus, cost_minus = fade_cost(2.2e-3 - 1.0e-3)
print(f"  if 1.0e-3 of a measured 2.2e-3 %/cycle were acid-driven: guard saves ${cost_now-cost_minus:.0f}/t at $20/kg, 1.04 mol/kg")
print(f"  field-sorbent mass balance test: S and N found per kg after M cycles; expected S at 1 ppb SO2, 10,000 cycles, wc 1 mol/kg: "
      f"{1.0*per_ppb_per_mol*1.0*10000*1000:.1f} mmol/kg = {1.0*per_ppb_per_mol*1.0*10000*32.06:.3f} g S/kg ({1.0*per_ppb_per_mol*1.0*10000*32.06/10:.3f} wt%) -> easily seen by combustion S analysis / IC of a water extract")

print("\n=== IDEA B: replenishable radical trap delivered in regeneration steam (N-alkylhydroxylamine) ===")
ref = reference_amine_cycle()
wc = ref.working_capacity
steam_t_per_t = 2.0
steam_g_per_kg_cycle = steam_t_per_t * wc * M_CO2 * 1e3  # g steam per kg sorbent per cycle
print(f"reference wc {wc:.2f} mol/kg -> {wc*M_CO2*1e3:.1f} g CO2 per kg sorbent per cycle; steam at {steam_t_per_t} t/t = {steam_g_per_kg_cycle:.0f} g per kg per cycle")
for fade in (2.2e-3, 1.6):
    sites_lost = fade / 100 * wc  # mol working sites per kg per cycle
    for chain in (1, 10):
        trap_demand = sites_lost / chain / 2.0  # 2 radicals trapped per hydroxylamine
        for M_ao, name in ((89.14, "DEHA"), (75.11, "N-isopropylhydroxylamine")):
            g = trap_demand * M_ao
            for retention in (1.0, 0.1):
                ppm = g / retention / steam_g_per_kg_cycle * 1e6
                per_t = g / retention / (wc * M_CO2) * 1e3 / 1e3  # kg per t CO2
                if fade < 1 and name == "DEHA":
                    print(f"  fade {fade:.1e} %/cycle, chain length {chain:>2}, {name}: demand {trap_demand:.1e} mol/kg/cycle; "
                          f"retention {retention:.0%} -> {ppm:,.1f} ppm in steam, {per_t*1e3:,.1f} g/t CO2 (${per_t*6:.2f}/t at $6/kg)")
        if fade > 1:
            print(f"  unprotected-PEI case fade {fade} %/cycle, chain {chain}: demand {sites_lost/chain/2:.1e} mol/kg/cycle "
                  f"-> {sites_lost/chain/2*89.14/(wc*M_CO2)*1e3:.0f} g DEHA per t CO2 at full retention")
# acid by-product risk
for acid_per_ao in (0.1, 0.5, 1.0):
    demand = 2.2e-3 / 100 * wc / 10 / 2.0 / 0.1  # chain 10, 10% retention dose
    acid = demand * acid_per_ao  # mol acid per kg per cycle, if all dose ends as acid in sorbent
    print(f"  if {acid_per_ao} carboxylic acid per dosed DEHA stays on the amine: {acid/wc*100:.1e} %/cycle of working sites "
          f"(vs 2.2e-3 fade it is meant to cut) -> needs ketone-forming N-isopropyl type or <{2.2e-3/(acid/wc*100)*acid_per_ao*0.3:.2f} acid per dose")

print("\n=== IDEA C: cerium (CeOx / Ce3+) regenerative radical scavenger, PEM fuel-cell import ===")
for wt in (0.25, 0.5, 1.0, 2.0):
    q = ref.q_max * (1 - wt / 100)
    cyc = TVSACycle(dH=-70e3, dS=-165, q_max=q, water_coads=2.0, cp_sorbent=1500 * (1 - wt/100) + 460 * wt/100)
    ce_cost = wt / 100 * 8.0  # $/kg sorbent at $8/kg CeO2 (bulk) 
    print(f"  {wt} wt% CeO2: wc {cyc.working_capacity:.3f} mol/kg, heat {cyc.heat_gj_per_t:.2f} GJ/t (ref {ref.heat_gj_per_t:.2f}); "
          f"adds ${ce_cost:.2f}/kg sorbent; Ce per amine N (PEI 45 wt%, 10.4 mol N/kg): {wt/100/0.1721/10.4*1e3:.2f} mmol/mol N")
for base, factor in ((2.2e-3, 3), (2.2e-3, 1/1.5), (3.5e-3, 3)):
    c0, k0 = fade_cost(base); c1, k1 = fade_cost(base / factor)
    print(f"  fade {base:.1e} -> {base/factor:.1e} %/cycle: sorbent ${k0:.0f} -> ${k1:.0f}/t at $20/kg (change ${k0-k1:+.0f}/t)")

print("\n=== IDEA D: metered low-wet-pickup wetting (textile foam / kiss-roll) for moisture swing ===")
Tamb = 293.15
def psat(T):  # Pa, Magnus over water
    t = T - 273.15
    return 610.94 * math.exp(17.625 * t / (t + 243.04))
dw = (0.60 - 0.20) * psat(Tamb) / (R * Tamb)  # mol water carried per m3 of drying air 20 -> 60% RH
co2_per_m3 = X_AIR * P0 / (R * Tamb) * 0.5     # mol CO2 delivered per m3 at 50% capture
Wstar = dw / co2_per_m3
print(f"drying air 20->60% RH at 20 C carries {dw:.3f} mol H2O/m3; CO2 supply at 50% capture {co2_per_m3:.4f} mol/m3")
print(f"  -> drying no longer needs more air than CO2 supply below W* = {Wstar:.0f} mol H2O per mol CO2 ({Wstar*18/44:.0f} kg/kg)")
wcap = 0.9e-3  # mol CO2 per g resin per cycle (lab working capacity, IRA-900 class)
for label, g_per_g in (("liquid immersion in mesh packet (ASU field, 3.3 g/g)", 3.3), ("immersion of bare resin sheet (~1.2 g/g, assumed)", 1.2),
                       ("metered foam/kiss-roll 0.6 g/g", 0.6), ("metered 0.4 g/g", 0.4), ("vapour 20->95% RH (measured 23-24 mmol/g)", 0.42)):
    W = g_per_g / 0.018 / wcap / 1e3
    air_ratio = W / Wstar
    lat = gj_per_tonne(moisture_swing_water_heat(W))
    print(f"  {label}: {W:.0f} mol/mol = {W*18/44:.0f} kg H2O/kg CO2; drying-air/CO2-air ratio {air_ratio:.1f}; "
          f"latent heat drawn from ambient {lat:.1f} GJ/t; water at $1.5/m3 ${W*18/44*1.5:.0f}/t")
print("  reversible minimum to reach 1 atm product: 4.8 mol/mol at 20% RH (map)")
# productivity: cycle time = max(drying, CO2 loading) + wetting/release
for W, rel_min in ((244, 15), (37, 15), (25, 15)):
    # thin sheet 0.5 kg/m2 face-equivalent; air at 2 m/s across 0.25 m deep stack: air per kg per s
    face_air = 2.0  # m3/s per m2 face
    kg_per_m2 = 20.0  # kg sorbent per m2 of face in a 0.25 m deep sheet stack (assumed)
    air_per_kg = face_air / kg_per_m2
    t_co2 = wcap * 1e3 / (co2_per_m3 * air_per_kg) / 60
    t_dry = W * wcap * 1e3 / (dw * air_per_kg) / 60
    cyc = max(t_co2, t_dry) + rel_min
    print(f"  W {W}: air-supply-limited CO2 loading {t_co2:.0f} min, drying {t_dry:.0f} min, + {rel_min} min release -> "
          f"{1440/cyc:.1f} cycles/day -> {productivity(0.9, 1440/cyc):.2f} kg CO2/kg/day (kinetic limits ignored)")

print("\n=== IDEA E: ammonia / volatile-amine emission rate as a fast fade metric (PEM fluoride-emission-rate import) ===")
for fade in (1e-3, 2.2e-3):
    for Y in (0.3, 1.0):
        for mass_g in (1.0, 10.0):
            nmol = fade / 100 * wc * 1e-3 * mass_g * Y * 1e9  # nmol NH3 per cycle
            # condensate 10 mL per 10 cycles; IC LOD 0.01 mg/L NH4+
            lod_nmol = 0.01e-3 / 18.04 * 0.010 * 1e9
            print(f"  fade {fade:.1e}, yield {Y} NH3 per lost site, {mass_g:>4} g: {nmol:.1f} nmol NH3/cycle; IC LOD in 10 mL = {lod_nmol:.1f} nmol -> "
                  f"{max(1, math.ceil(lod_nmol/nmol*3))} cycles for 3x LOD")
for noise in (1.0, 3.0):
    print(f"  capacity-based detection with +/-{noise}% scatter (2 sigma): needs {2*noise/1e-3:,.0f} cycles at 1e-3 %/cycle")

print("\n=== IDEA F: photothermal self-heated moisture-swing sheet (solar-desalination interfacial heating) ===")
for Ta_C, RHa in ((25, 0.5), (25, 0.7), (30, 0.8), (15, 0.8)):
    Ta = Ta_C + 273.15
    # sheet temperature needed for 20% local RH
    target = RHa * psat(Ta) / 0.20
    lo, hi = Ta, Ta + 80
    for _ in range(60):
        mid = (lo + hi) / 2
        if psat(mid) < target: lo = mid
        else: hi = mid
    dT = hi - Ta
    for G, h in ((800, 25), (500, 25)):
        dT_av = 0.9 * G / h
        rh_loc = RHa * psat(Ta) / psat(Ta + dT_av)
        print(f"  air {Ta_C} C/{RHa:.0%} RH: sheet must run +{dT:.0f} K for 20% local RH; {G} W/m2 absorbed at h={h} W/m2K gives +{dT_av:.0f} K "
              f"-> local RH {rh_loc:.0%}")
# compare: heating the air instead
print(f"  heating the whole air stream costs {gj_per_tonne(1.0) if False else 0:.0f}", end="")
cp_air = 29.1  # J/mol/K
air_mol_per_t = V * n_air
print(f"\r  heating the air stream instead: {air_mol_per_t*cp_air/1e9:.2f} GJ per K per t CO2 (75% capture) -> 20 K = {20*air_mol_per_t*cp_air/1e9:.0f} GJ/t")
print(f"  solar area at 5 kWh/m2/day absorbed, 30% of it into sheet heating during capture: (illustrative) "
      f"{20*air_mol_per_t*cp_air/1e9*1e9/(5*3.6e6*0.3*365)/1e3:.1f} m2-yr... not used; sheet heats boundary layer only")


print("\n=== IDEA G: trace-metal budget for amine sorbents (as-made vs steam vs dust) and chelating-IX polishing ===")
co2_life_t = {c: 1.04 * c * M_CO2 / 1e3 for c in (9091, 20000)}  # t CO2 per kg sorbent over life (wc 1.04)
for c, t in co2_life_t.items():
    print(f"  life {c:,} cycles at 1.04 mol/kg: {t*1e3:.0f} kg CO2 per kg sorbent")
print("  as-made: commercial PEI 7-160 ppm Fe, <=47 ppm Cu (PEI basis) -> at 45 wt% PEI: "
      f"{7*0.45:.0f}-{160*0.45:.0f} ppm Fe, <={47*0.45:.0f} ppm Cu on sorbent; threshold effect seen at ~4 ppm Cu (120 C, 4.5 h air test)")
for label, cu_ngm3, dep in (("rural PM Cu 2 ng/m3, 10% deposited", 2, 0.10), ("urban PM Cu 20 ng/m3, 20% deposited", 20, 0.20), ("traffic-heavy 50 ng/m3, 30%", 50, 0.30)):
    mg_per_t = V * cu_ngm3 * 1e-6 * dep
    for c, t in co2_life_t.items():
        print(f"  dust {label}: {mg_per_t:.1f} mg Cu per t CO2 -> {mg_per_t*t:.1f} ppm Cu on sorbent after {c:,} cycles (bed average; inlet face higher)")
for ppb in (1, 5, 10):
    steam = 2.0  # t steam per t CO2
    mg_per_t = steam * 1e3 * ppb * 1e-6 * 1e3  # kg steam * ppb(ug/kg) -> ug; /1e3 -> mg
    for c, t in co2_life_t.items():
        print(f"  steam Cu {ppb} ppb (mass), 2 t steam/t CO2, full retention: {mg_per_t:.0f} mg Cu/t CO2 -> {mg_per_t*t:.1f} ppm after {c:,} cycles")
# chelating resin polishing cost: resin capacity ~1 eq/L for Cu at pH 4-5 (IDA), only ppm loads
cu_ppm, kg_pei_per_kg_sorbent = 47.0, 0.45
cu_mol_per_kg_sorbent = cu_ppm * 1e-6 * kg_pei_per_kg_sorbent * 1e3 / 63.55
print(f"  Cu to remove from PEI at 47 ppm: {cu_mol_per_kg_sorbent*1e6:.0f} umol per kg sorbent; IDA resin at 1 mol Cu/kg working -> "
      f"{cu_mol_per_kg_sorbent*1e3:.2f} g resin per kg sorbent (resin at $15/kg: ${cu_mol_per_kg_sorbent*15:.4f}/kg sorbent); "
      "real cost is the acidify/neutralise/desalt steps, not the resin")

print("\n=== verifier cross-checks used in claims ===")
ref = reference_amine_cycle()
print(f"  reference: wc {ref.working_capacity:.2f} mol/kg, heat {ref.heat_gj_per_t:.2f} GJ/t, work-eq {ref.work_equivalent_gj_per_t:.2f} GJ/t, 2nd-law {ref.second_law_efficiency:.0%}")
for wcoad in (2.0, 6.0, 8.0):
    c = TVSACycle(dH=-70e3, dS=-165, q_max=2.0, water_coads=wcoad)
    print(f"  water co-desorbed {wcoad} mol/mol: heat {c.heat_gj_per_t:.2f} GJ/t")
for q in (0.675, 0.9, 1.27):
    for price, cyc in ((7, 15000), (20, 5000), (54, 1380)):
        print(f"  QA resin wc {q} mol/kg, ${price}/kg, {cyc} cycles: ${sorbent_cost_per_tonne(price, q, cyc):.0f}/t")
