"""Verifier for anti_availability_3: dredged reservoir sediment as calcined clay for LC3.

Not a gas separation, so the CO2 separation floor does not apply. The relevant
thermodynamic floors are (a) kaolinite dehydroxylation enthalpy and (b) latent heat of
evaporating the sediment's water (if dried thermally). Everything else is techno-economics.

Sources (web search budget was exhausted in this run; values are from standard
literature, recalled, NOT re-verified, and labelled as such):
  [RH95]  Robie & Hemingway 1995 (USGS Bull. 2131): kaolinite dHf = -4119.6 kJ/mol.
  [MK]    metakaolin dHf ~ -3210 kJ/mol (amorphous; uncertain +/- ~50 kJ/mol).
  [AVET16] Avet, Snellings, Alujas, Ben Haha, Scrivener 2016 CCR: LC3-50 reaches OPC-like
          strength from ~7 d when calcined kaolinite content >= ~40%.
  [LP63]  Lara & Pemberton 1963 / USBR: initial dry bulk density of clay deposits
          ~0.4-1.0 t/m3 depending on reservoir operation.
  [GCCA]  Global clinker-to-cement ratio ~0.70-0.72 (GCCA GNR / IEA, ~2020-22).
  [USGS]  World cement ~4.1 Gt (2023-24, USGS MCS).
  [SYV05] Syvitski et al. 2005 Science: reservoirs trap a large share of river sediment;
          global pre-dam river flux ~14 Gt/yr.  Reservoir trapping taken as 3-10 Gt/yr
          (wide range, flagged uncertain).
  [UNU23] UNU-INWEH 2023: ~47k large dams, ~6,300 km3 initial storage.
  Calciner energy 2.5-4 GJ/t calcined clay (flash vs rotary; industrial reports, modelled).
  Industrial dryers 2.8-3.5 GJ per t water evaporated (latent 2.26 + losses).
"""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

M_KAO = 258.16  # g/mol Al2Si2O5(OH)4
H2O_LATENT = 2.26  # GJ/t water at 100 C (2.44 at 25 C)
SCEN = ("low", "base", "high")   # low = favourable to the idea, high = unfavourable


def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


print("=" * 78)
print("1. THERMODYNAMIC FLOORS (no gas separation involved)")
print("=" * 78)
dHf_kao, dHf_mk, dHf_h2o_g = -4119.6, -3210.0, -241.8
dH_dehyd = dHf_mk + 2 * dHf_h2o_g - dHf_kao   # kJ/mol kaolinite, water leaves as vapour
dH_dehyd_gj_t = dH_dehyd / M_KAO               # kJ/g = GJ/t kaolinite
print(f"Kaolinite dehydroxylation dH (water as vapour): {dH_dehyd:.0f} kJ/mol = {dH_dehyd_gj_t:.2f} GJ/t kaolinite")
print("  (metakaolin dHf uncertain +/-50 kJ/mol -> +/-0.19 GJ/t; literature DSC values often lower, ~0.6-1.0)")
print(f"Latent heat floor for thermal drying: {H2O_LATENT:.2f} GJ/t water (mechanical dewatering can avoid part)")
print(f"Separation floor (CO2 capture) not applicable; for reference the verifier's cement-flue floor is "
      f"{gj_per_tonne(min_separation_work(0.25, 0.9, 0.99)):.3f} GJ/t CO2")

print()
print("=" * 78)
print("2. CO2 ACCOUNTING per t calcined clay (CC)")
print("=" * 78)
CaO = 0.65
clinker_process = CaO * 44.01 / 56.08
kiln_fuel_gj, ef_coal = 3.4, 0.095
clinker_co2 = clinker_process + kiln_fuel_gj * ef_coal
print(f"Clinker: process {clinker_process:.3f} + fuel {kiln_fuel_gj*ef_coal:.3f} = {clinker_co2:.3f} t CO2/t clinker "
      f"(65% CaO, 3.4 GJ/t, 0.095 t/GJ coal/petcoke; excludes electricity) -- matches idea's 0.51/0.83")

P = {  # low (favourable) / base / high (unfavourable)
    "kaolinite_frac":   (0.50, 0.35, 0.20),   # reservoir fines; >=0.40 needed for LC3-50 parity [AVET16]
    "rho_dry":          (1.0, 0.75, 0.5),     # t/m3 in situ fine deposit [LP63]
    "calc_gj":          (2.5, 3.0, 4.0),      # GJ/t CC calcination fuel
    "calc_ef":          (0.056, 0.080, 0.095),# t CO2/GJ: gas / mix / coal-petcoke
    "moist_after_dewater_wb": (0.30, 0.40, 0.50),  # wet-basis moisture after geotube/filter press
    "dryer_gj_per_t_water": (2.8, 3.1, 3.5),
    "waste_heat_share": (1.0, 0.5, 0.0),      # share of drying covered by kiln/calciner waste heat
    "org_C":            (0.005, 0.015, 0.03), # organic C mass fraction of reservoir fines (burns off)
    "haul_km":          (100, 200, 300),
    "dredge_kwh_m3":    (2, 4, 8),            # dredge + slurry pumping, per m3 in situ (modelled)
    "dredge_usd_m3":    (5, 10, 20),          # idea used 5-10; reservoir jobs often higher (assumed)
    "dewater_usd_t":    (3, 8, 15),           # geotube / filter press per t dry solids (assumed)
    "fuel_usd_gj":      (3, 5, 8),            # cement-plant fuel
    "elec_usd_mwh":     (50, 80, 120),
    "truck_usd_tkm":    (0.05, 0.07, 0.10),
    "calciner_capex_per_tpa": (100, 150, 250),# $ per t/yr CC capacity (modelled)
    "calc_om_usd_t":    (5, 7, 10),
    "clinker_var_usd_t":(45, 35, 28),         # clinker variable cost displaced (fuel+power+raw+maint.)
    "quarry_clay_usd_t":(10, 7, 4),           # alternative quarried clay, delivered (assumed)
    "dam_benefit_usd_m3": (2.0, 0.5, 0.0),    # value to dam owner per m3 removed (storage/intake), assumed
}
ef_diesel_kwh = 0.27e-3  # t CO2 per kWh diesel-electric
truck_kg_tkm = 0.08

results = {}
for i, s in enumerate(SCEN):
    g = {k: v[i] for k, v in P.items()}
    k = g["kaolinite_frac"]
    loi = 0.1395 * k + g["org_C"] * 1.5      # dehydroxylation water + organic matter (~1.5x C)
    raw_per_cc = 1 / (1 - loi)               # t dry sediment per t CC
    vol_m3 = raw_per_cc / g["rho_dry"]
    m = g["moist_after_dewater_wb"]
    water_t = raw_per_cc * m / (1 - m)
    dry_gj = water_t * g["dryer_gj_per_t_water"]
    dry_fired_gj = dry_gj * (1 - g["waste_heat_share"])
    # CO2 debits per t CC
    co2_calc = g["calc_gj"] * g["calc_ef"]
    co2_dry = dry_fired_gj * g["calc_ef"]
    co2_org = raw_per_cc * g["org_C"] * 44.01 / 12.01
    co2_haul = raw_per_cc * (1 + water_t / raw_per_cc) * g["haul_km"] * truck_kg_tkm / 1e3
    co2_dredge = vol_m3 * g["dredge_kwh_m3"] * ef_diesel_kwh
    debit = co2_calc + co2_dry + co2_org + co2_haul + co2_dredge
    # Credits under three attributions
    a_lc3 = 1.5 * clinker_co2 - debit           # LC3-50 vs OPC-95; clay credited with limestone
    a_clay = 1.0 * clinker_co2 - debit          # clay replaces clinker 1:1
    # vs realistic baseline cement (clinker factor 0.72): LC3-50 removes 0.22 t clinker/t cement
    # for 0.30 t CC -> 0.733 t clinker per t CC
    a_base = (0.72 - 0.50) / 0.30 * clinker_co2 - debit
    # quality penalty: below 40% kaolinite LC3-50 loses strength; need more clinker.
    # crude: clinker factor needed rises linearly to 0.65 at 20% kaolinite
    if k < 0.40:
        cf = 0.50 + (0.40 - k) / 0.20 * 0.15
        clinker_disp = (0.95 - cf) / 0.30
        a_qual = clinker_disp * clinker_co2 - debit
    else:
        a_qual = a_lc3
    # energy (gross added) per t CC
    e_gj = (g["calc_gj"] + dry_fired_gj + dry_gj * g["waste_heat_share"] * 0  # waste heat free
            + vol_m3 * g["dredge_kwh_m3"] * 0.0036 / 0.35   # primary energy of dredge diesel
            + raw_per_cc * (1 + water_t / raw_per_cc) * g["haul_km"] * 1.0e-3)  # ~1 MJ/t-km
    kiln_fuel_saved = 1.5 * kiln_fuel_gj
    # costs per t CC (dam route)
    c_dredge = vol_m3 * g["dredge_usd_m3"]
    c_dewater = raw_per_cc * g["dewater_usd_t"]
    c_dry = dry_fired_gj * g["fuel_usd_gj"]
    c_haul = (raw_per_cc + water_t) * g["haul_km"] * g["truck_usd_tkm"]
    c_calc = g["calc_gj"] * g["fuel_usd_gj"] + g["calciner_capex_per_tpa"] * crf(0.08, 20) + g["calc_om_usd_t"]
    c_grind = 0.04 * g["elec_usd_mwh"]           # ~40 kWh/t extra grinding/blending
    c_dam_credit = vol_m3 * g["dam_benefit_usd_m3"]
    cc_cost_dam = c_dredge + c_dewater + c_dry + c_haul + c_calc + c_grind - c_dam_credit
    # quarry route: clay delivered + drying 12% moisture fuel (calciner exhaust usually covers)
    cc_cost_quarry = raw_per_cc * g["quarry_clay_usd_t"] + c_calc + c_grind
    limestone = 0.5 * 6.0
    clinker_saved_usd = 1.5 * g["clinker_var_usd_t"]
    net_cost_dam = cc_cost_dam + limestone - clinker_saved_usd   # $/t CC, LC3 vs OPC
    net_cost_quarry = cc_cost_quarry + limestone - clinker_saved_usd
    results[s] = dict(loi=loi, raw=raw_per_cc, vol=vol_m3, water=water_t, dry_gj=dry_gj,
                      dry_fired=dry_fired_gj, co2_calc=co2_calc, co2_dry=co2_dry, co2_org=co2_org,
                      co2_haul=co2_haul, co2_dredge=co2_dredge, debit=debit, a_lc3=a_lc3,
                      a_clay=a_clay, a_base=a_base, a_qual=a_qual, e_gj=e_gj, kiln_saved=kiln_fuel_saved,
                      c_dredge=c_dredge, c_dewater=c_dewater, c_dry=c_dry, c_haul=c_haul,
                      c_calc=c_calc, c_dam_credit=c_dam_credit, cc_dam=cc_cost_dam,
                      cc_quarry=cc_cost_quarry, net_dam=net_cost_dam, net_quarry=net_cost_quarry,
                      k=k, rho=g["rho_dry"])

def row(label, key, fmt="{:>10.3f}"):
    print(f"{label:<52}" + "".join(fmt.format(results[s][key]) for s in SCEN))

print(f"{'(per t calcined clay)':<52}{'low':>10}{'base':>10}{'high':>10}")
row("kaolinite fraction of sediment fines", "k", "{:>10.2f}")
row("loss on ignition (dehydroxylation + organics)", "loi")
row("t dry sediment per t CC", "raw")
row("m3 in-situ sediment per t CC", "vol")
row("t water to evaporate after dewatering", "water")
row("drying heat demand, GJ", "dry_gj")
row("  of which fuel-fired, GJ", "dry_fired")
row("CO2 debit: calcination fuel", "co2_calc")
row("CO2 debit: fired drying", "co2_dry")
row("CO2 debit: sediment organic C burned off", "co2_org")
row("CO2 debit: haul (wet mass)", "co2_haul")
row("CO2 debit: dredging", "co2_dredge")
row("CO2 debit total", "debit")
row("AVOIDED A: LC3-50 vs OPC-95 (clay gets limestone credit)", "a_lc3")
row("AVOIDED B: clay replaces clinker 1:1", "a_clay")
row("AVOIDED C: LC3-50 vs today's 0.72-clinker cement", "a_base")
row("AVOIDED D: A with strength penalty for low kaolinite", "a_qual")
row("gross energy added, GJ (calcine+fired dry+dredge+haul)", "e_gj")
row("kiln fuel saved, GJ (1.5 t clinker x 3.4)", "kiln_saved")

print()
print("=" * 78)
print("3. COSTS per t calcined clay (USD)")
print("=" * 78)
row("dredging", "c_dredge", "{:>10.1f}")
row("dewatering", "c_dewater", "{:>10.1f}")
row("fired drying", "c_dry", "{:>10.1f}")
row("haul (wet mass)", "c_haul", "{:>10.1f}")
row("calcination (fuel + annualised capex 8%/20y + O&M)", "c_calc", "{:>10.1f}")
row("credit to dam owner (storage/intake value)", "c_dam_credit", "{:>10.1f}")
row("CC delivered cost, DAM route", "cc_dam", "{:>10.1f}")
row("CC delivered cost, QUARRY route", "cc_quarry", "{:>10.1f}")
row("net cost of LC3 vs OPC per t CC, DAM route", "net_dam", "{:>10.1f}")
row("net cost of LC3 vs OPC per t CC, QUARRY route", "net_quarry", "{:>10.1f}")

print()
print("Cost per t CO2 avoided (attribution D for the scenario's kaolinite):")
for s in SCEN:
    r = results[s]
    a = r["a_qual"]
    dam = r["net_dam"] / a if a > 0 else float('inf')
    q = r["net_quarry"] / a if a > 0 else float('inf')
    extra = (r["cc_dam"] - r["cc_quarry"]) / a if a > 0 else float('inf')
    print(f"  {s:<5} avoided {a:.3f} t/t CC | DAM route ${dam:7.1f}/t | QUARRY route ${q:7.1f}/t | "
          f"dam-vs-quarry premium ${extra:7.1f}/t CO2")
    r["usd_t_dam"], r["usd_t_quarry"], r["premium"] = dam, q, extra
print("Gross added energy per t CO2 avoided (D):")
for s in SCEN:
    r = results[s]
    print(f"  {s:<5} {r['e_gj']/r['a_qual']:.2f} GJ/t CO2 gross; net of kiln fuel saved "
          f"{(r['e_gj']-r['kiln_saved'])/r['a_qual']:.2f} GJ/t CO2")
    r["e_per_t"] = r["e_gj"] / r["a_qual"]

print()
print("Check of idea's claim (5): 'net SCM value $30-45/t => $33-50/m3'")
for rho in (1.1, 0.75, 0.5):
    print(f"  rho_dry {rho:.2f} t/m3: $30-45/t dry => ${30*rho:.0f}-{45*rho:.0f}/m3")
print("  But raw dam sediment competes with quarried clay at ~$4-10/t (assumed); the SCM value accrues to")
print("  calcined clay whatever its source, so the dam's clay is worth ~quarry price x quality factor:")
for rho in (1.0, 0.75, 0.5):
    print(f"  rho_dry {rho:.2f}: quarry-parity value $4-10/t => ${4*rho:.1f}-{10*rho:.1f}/m3 vs dredging $5-20/m3")

print()
print("=" * 78)
print("4. SCALE")
print("=" * 78)
cement = 4.1
lc3_share = 0.25
cc_lc3 = cement * lc3_share * 0.30
print(f"Idea's LC3 lever: {cement} Gt cement x {lc3_share:.0%} LC3 x 30% CC = {cc_lc3:.2f} Gt CC/yr")
storage_km3 = 6300
for loss in (0.005, 0.01):
    print(f"  Consistency: {storage_km3} km3 x {loss:.1%}/yr x 0.8 t/m3 = {storage_km3*1e9*loss*0.8/1e9:.0f} Gt/yr "
          f"(vs ~14 Gt/yr global pre-dam river sediment flux [SYV05]) -> 0.5-1%/yr can't be the volume-weighted global rate")
trap = (10.0, 5.0, 3.0)       # Gt/yr trapped in reservoirs (favourable -> unfavourable)
fine = (0.4, 0.3, 0.2)        # clay-size fraction
near_dam = (0.3, 0.15, 0.05)  # share of fines in dredgeable near-intake zone
kaol_ok = (0.3, 0.15, 0.07)   # share of that in reservoirs with >=~35-40% kaolinite fines
in_range = (0.6, 0.4, 0.25)   # within ~300 km of a cement plant with demand
print(f"{'':<52}{'low':>10}{'base':>10}{'high':>10}")
gt_cc = []
for i, s in enumerate(SCEN):
    sup = trap[i] * fine[i] * near_dam[i] * kaol_ok[i] * in_range[i]
    cc = min(sup / results[s]["raw"], cc_lc3)
    gt_cc.append(cc)
print(f"{'reservoir trapping, Gt/yr (uncertain)':<52}" + "".join(f"{x:>10.1f}" for x in trap))
print(f"{'usable dam-sourced CC, Gt/yr':<52}" + "".join(f"{x:>10.3f}" for x in gt_cc))
gt_co2 = [gt_cc[i] * results[s]["a_qual"] for i, s in enumerate(SCEN)]
print(f"{'Gt CO2/yr avoided (attribution D)':<52}" + "".join(f"{x:>10.3f}" for x in gt_co2))
print(f"{'Share of idea claim 0.3 Gt/yr':<52}" + "".join(f"{x/0.3:>10.1%}" for x in gt_co2))
print(f"{'Share of total GHG 53 Gt':<52}" + "".join(f"{x/TOTAL_GHG_GT_CO2E:>10.2%}" for x in gt_co2))
print("Incremental (additional to LC3 with quarried clay): ~0 where quarry clay is available;")
print("  only clay-scarce cement markets count, so additional Gt is a fraction of the row above.")

print()
print("=" * 78)
print("5. RESOURCES at base scale")
print("=" * 78)
s = "base"; r = results[s]
cc = gt_cc[1]
ej = cc * 1e9 * r["e_gj"] / 1e9
sc = ScaleCheck(gt_per_year=cc * r["a_qual"], gj_per_tonne=r["e_per_t"])
print(f"Dam-sourced CC {cc*1e3:.0f} Mt/yr; gross energy {ej:.3f} EJ/yr = {sc.share_of_world_primary_energy:.3%} of world primary")
print(f"  (net energy is NEGATIVE: kiln fuel saved {cc*r['kiln_saved']:.3f} EJ/yr)")
print(f"Sediment moved: {cc*r['vol']*1e3:.0f} Mm3/yr in situ; water evaporated {cc*r['water']*1e3:.0f} Mt/yr;"
      f" haul mass {(cc*(r['raw']+r['water']))*1e3:.0f} Mt/yr")
print(f"Full-LC3 lever for comparison: {cc_lc3*1e3:.0f} Mt CC/yr -> {cc_lc3*results['base']['a_qual']:.2f} Gt CO2 at base D")
print("Land: dewatering lagoons/geotube yards ~ ha per Mt/yr (small); water: returned to reservoir.")

print()
print("=" * 78)
print("6. SENSITIVITY: base case with ONE parameter at its high (unfavourable) value")
print("=" * 78)
def run(over):
    g = {k: v[1] for k, v in P.items()}; g.update(over)
    k = g["kaolinite_frac"]; loi = 0.1395 * k + g["org_C"] * 1.5; raw = 1 / (1 - loi)
    vol = raw / g["rho_dry"]; m = g["moist_after_dewater_wb"]; w = raw * m / (1 - m)
    dryf = w * g["dryer_gj_per_t_water"] * (1 - g["waste_heat_share"])
    debit = (g["calc_gj"] * g["calc_ef"] + dryf * g["calc_ef"] + raw * g["org_C"] * 44.01 / 12.01
             + (raw + w) * g["haul_km"] * truck_kg_tkm / 1e3 + vol * g["dredge_kwh_m3"] * ef_diesel_kwh)
    cf = 0.50 + max(0.0, 0.40 - k) / 0.20 * 0.15
    a = (0.95 - cf) / 0.30 * clinker_co2 - debit
    cost = (vol * g["dredge_usd_m3"] + raw * g["dewater_usd_t"] + dryf * g["fuel_usd_gj"]
            + (raw + w) * g["haul_km"] * g["truck_usd_tkm"]
            + g["calc_gj"] * g["fuel_usd_gj"] + g["calciner_capex_per_tpa"] * crf(0.08, 20) + g["calc_om_usd_t"]
            + 0.04 * g["elec_usd_mwh"] - vol * g["dam_benefit_usd_m3"] + 3.0 - 1.5 * g["clinker_var_usd_t"])
    return a, cost
a0, c0 = run({})
print(f"{'base':<28} avoided {a0:.3f} t/t CC, ${c0/a0:.1f}/t CO2")
for key in P:
    a, c = run({key: P[key][2]})
    print(f"{key:<28} avoided {a:.3f} t/t CC, " + (f"${c/a:.1f}/t CO2" if a > 0 else "no net avoidance"))
a, c = run({k: P[k][2] for k in P if k not in ("kaolinite_frac", "org_C")})
print(f"{'all high except kaolinite/orgC':<28} avoided {a:.3f} t/t CC, " + (f"${c/a:.1f}/t CO2" if a > 0 else "no net avoidance"))
a, c = run({"haul_km": 50, "waste_heat_share": 1.0})
print(f"{'base, 50 km haul, all waste heat':<28} avoided {a:.3f} t/t CC, ${c/a:.1f}/t CO2")
