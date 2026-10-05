"""Verifier for graft_near_6: rich/lean amine tankage + off-peak electric regeneration
for a cycling NGCC with post-combustion capture.

All inputs labelled: [idea] = taken from the idea's own stated basis (not re-verified in
this run; web search budget exhausted), [lit] = literature value from memory of standard
sources (order-of-magnitude, flagged), [assume] = engineering assumption, [calc] = derived.
"""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

print("=" * 78)
print("graft_near_6 verifier: amine tankage + off-peak electric regeneration, cycling NGCC")
print("=" * 78)

# ---------------------------------------------------------------- (a) floor
w = min_separation_work(0.04, 0.90, 0.99)
floor = gj_per_tonne(w)
print(f"\n(a) Thermodynamic floor, 4% CO2 flue, 90% capture, 99% purity: {w/1e3:.2f} kJ/mol = {floor:.3f} GJ/t "
      f"({floor/0.0036:.0f} kWh/t)")
# reboiler duties [lit]: 30 wt% MEA ~3.6 GJ/t (benchmark), Cansolv/advanced ~2.7, PZ advanced flash stripper ~2.3
for name, q in [("PZ advanced flash stripper", 2.3), ("Advanced amine", 2.7), ("30 wt% MEA", 3.6)]:
    print(f"    reboiler heat {name:<28} {q:.1f} GJ_th/t  -> idea's e-boiler claim must be >= floor: "
          f"{'OK' if q/1 > floor else 'BELOW FLOOR'}")
# Work-equivalent of reboiler heat (heat at ~125 C, ambient 25 C): Carnot factor
Tr, Ta = 398.15, 298.15
carnot = 1 - Ta / Tr
print(f"    Carnot factor of 125 C reboiler heat: {carnot:.3f}; exergy of 3.35 GJ_th/t = {3.35*carnot:.2f} GJ/t "
      f"= {3.35*carnot/floor:.1f}x the separation floor (so no floor violation anywhere)")
print(f"    Resistive e-boiler at 3.35 GJ_th/t = {3.35/3.6:.2f} MWh_e/t vs exergy-equivalent {3.35*carnot/3.6:.2f} MWh/t:"
      f" 2nd-law efficiency of resistive regeneration = {floor/3.35:.3f} vs floor")

# ---------------------------------------------------------------- plant basis
P_net = 742.0          # MW [idea] NZT Power scale
cap_tph = 270.0        # t CO2/h captured at full load [idea]
# cross-check 270 t/h: fuel = P/eff; NG emission factor 56.1 kg/GJ (IPCC default) [lit]
for eff in (0.50, 0.53):
    gen = P_net / eff * 3.6 * 56.1e-3  # t/h generated (MWth*3.6 GJ/MWh*t/GJ)
    print(f"    cross-check: net eff {eff:.2f} -> CO2 generated {gen:.0f} t/h, 90% captured {0.9*gen:.0f} t/h "
          f"(idea: {cap_tph:.0f})")
capex_capture = P_net * 1e3 * (1936 - 970) / 1e6   # $M, 2018$ [idea, NETL Rev4A H-class]
print(f"\n    capture capex [idea arithmetic]: 742 MW x ($1936-970)/kW = ${capex_capture:.0f}M (2018$)")

CRF = 0.0707   # [assume] NETL-style 30-yr capital recovery for IOU financing ~7%
for tag, crf in [("NETL-like 7.07%", CRF), ("merchant 10%", 0.10)]:
    pass

# ---------------------------------------------------------------- (b) buffer
print("\n(b) Buffer sizing (one daily run block, stripper sized for daily average)")
def buffer(cf):
    h_on = 24 * cf
    daily = cap_tph * h_on
    avg = daily / 24
    buf = daily - avg * h_on   # = cap_tph*h_on*(1-cf)
    return h_on, daily, avg, buf

# cyclic capacity, mol CO2/kg solution: Rochelle-group definition ~0.47-0.5 (7 m MEA), 0.79-0.86 (8 m/5 m PZ) [lit];
# operating range up to ~1.2 for MEA (dLoading 0.25 x 4.9 mol MEA/kg) [calc]
solv = {"MEA 30wt%": dict(cap=(0.5, 0.8, 1.2), wfrac=0.30, price=(1.6, 2.0, 2.5)),   # $/kg MEA [assume]
        "PZ 5 m":    dict(cap=(0.86, 0.86, 1.0), wfrac=0.30, price=(3.0, 4.0, 5.5))}  # $/kg PZ [assume]
tank_cost = (150, 250, 500)    # $/m3 installed: lined CS crude-type tank -> stainless [assume]
eboiler_cost = (60, 100, 150)  # $/kWth electrode boiler incl. connection [lit, Danish Energy Agency catalogue order]
q_reb = {"MEA 30wt%": 3.6, "PZ 5 m": 2.5}  # GJ/t [lit]
regen_share = (0.45, 0.35, 0.25)   # share of capture capex in stripper/reboiler/X-exch/compression [idea=0.35]
n_scale = 0.65

results = {}
for cf in (0.25, 0.40, 0.60):
    h_on, daily, avg, buf = buffer(cf)
    print(f"  CF {cf:.0%}: on {h_on:.1f} h/d, captured {daily:.0f} t/d, stripper avg {avg:.0f} t/h, buffer {buf:.0f} t CO2")
    for s, d in solv.items():
        for i, lab in enumerate(("lo-inv", "base", "hi-inv")):
            pass
        cap_b = d["cap"][1] if s.startswith("MEA") else d["cap"][0]
        mass = buf * 1e6 / 44.01 / cap_b / 1e3 / 1e3   # kt solution
        print(f"     {s}: cyclic {cap_b} mol/kg -> {mass:.0f} kt solution (~{mass*1e3/1.05:.0f} m3 per tank); "
              f"at 0.5/{d['cap'][2]} mol/kg: {buf*1e6/44.01/d['cap'][0]/1e6:.0f}/{buf*1e6/44.01/d['cap'][2]/1e6:.0f} kt")
    # capex bands
    rows = []
    for k in range(3):   # k=0 favourable, 1 base, 2 unfavourable
        s = "PZ 5 m" if k == 0 else "MEA 30wt%"
        d = solv[s]
        capk = {0: d["cap"][2] if s.startswith("MEA") else d["cap"][2], 1: d["cap"][1], 2: d["cap"][0]}[k]
        mass_t = buf * 1e6 / 44.01 / capk / 1e3          # t solution
        vol = mass_t / 1.05                               # m3
        amine = mass_t * d["wfrac"] * 1e3 * d["price"][k] / 1e6   # $M
        tanks = 2 * vol * tank_cost[k] / 1e6 * 1.0
        eb_mw = avg * q_reb[s] / 3.6                      # MWth
        eb = eb_mw * 1e3 * eboiler_cost[k] / 1e6
        added = amine + tanks + eb
        saving = capex_capture * regen_share[k] * (1 - cf ** n_scale)
        rows.append((added, saving, amine, tanks, eb, eb_mw, vol))
        lab = ("favourable", "base", "unfavourable")[k]
        print(f"     capex {lab:<12}: amine ${amine:.0f}M + 2 tanks ${tanks:.0f}M ({vol/1e3:.0f}k m3 each) + "
              f"e-boiler {eb_mw:.0f} MWth ${eb:.0f}M = added ${added:.0f}M vs regen-train saving ${saving:.0f}M "
              f"-> net ${saving-added:+.0f}M")
    results[cf] = rows

# ---------------------------------------------------------------- (c) energy arbitrage
print("\n(c) Energy arbitrage per tonne captured")
# Steam-extraction penalty: 0.06-0.08 MWh_e per GJ of LP steam [lit]; compression to ~150 bar 0.09-0.11 MWh/t [lit]
comp = 0.10
cases = {
    "favourable":   dict(q=2.5, steam_pen=0.075, p_peak=150, p_off=10,  cop=1.0),
    "base":         dict(q=3.35, steam_pen=0.07, p_peak=110, p_off=35, cop=1.0),
    "unfavourable": dict(q=3.6, steam_pen=0.065, p_peak=80,  p_off=60,  cop=1.0),
}
# p_off = DELIVERED off-peak price incl. network/levies (GB non-commodity ~$15-35/MWh) [assume]
arb = {}
for cf in (0.25, 0.40, 0.60):
    shifted = 1 - cf   # stripper at average flow: on-hours share of regeneration stays on steam extraction
    for name, c in cases.items():
        peak_loss = c["q"] * c["steam_pen"] + comp          # MWh_e/t lost at peak in baseline
        offpeak_use = c["q"] / 3.6 / c["cop"] + comp        # MWh_e/t bought off-peak
        # strict reading (100% of tonnes) vs physically consistent (only (1-cf) of tonnes shifted)
        sav_strict = peak_loss * c["p_peak"] - offpeak_use * c["p_off"]
        sav_phys = shifted * sav_strict
        arb[(cf, name)] = (sav_phys, peak_loss, offpeak_use)
        if cf == 0.40:
            print(f"  CF 40% {name:<12}: baseline peak loss {peak_loss:.2f} MWh/t @${c['p_peak']}, e-regen "
                  f"{offpeak_use:.2f} MWh/t @${c['p_off']} -> saving if ALL tonnes shifted ${sav_strict:+.1f}/t; "
                  f"only {shifted:.0%} shiftable -> ${sav_phys:+.1f}/t")
pl, ou = 3.35 * 0.07 + comp, 3.35 / 3.6 + comp
print(f"  break-even peak/off-peak price ratio (resistive, base duties): {ou/pl:.2f}; with heat pump COP 2.5: "
      f"{(3.35/3.6/2.5+comp)/pl:.2f}")

# ---------------------------------------------------------------- (d) climate guard
print("\n(d) Grid emissions from off-peak electric regeneration (t CO2 per t captured, all-electric tonnes)")
for mef in (50, 100, 250, 400, 900):
    res = (3.35 / 3.6 + comp) * mef / 1000
    hp = (3.35 / 3.6 / 2.5 + comp) * mef / 1000
    print(f"  MEF {mef:>4} g/kWh: resistive {res:.2f}, heat pump COP2.5 {hp:.2f}; "
          f"net of baseline steam-extraction penalty* {res - (3.35*0.07+comp)*0:.2f}")
print("  *baseline steam extraction costs gas-plant output, which in on-hours is replaced by the same grid; treated as 0 here")
# hours needed: e-boiler running only below a threshold requires the stripper to cover the day in those hours
for h_clean in (1500, 3000, 5256):
    frac = h_clean / 8760
    print(f"  if only {h_clean} h/yr are below 100 g/kWh, stripper+e-boiler must be sized {0.6/frac:.2f}x the "
          f"60%-off-hours design (CF40) and storage grows from daily to multi-day")

# ---------------------------------------------------------------- (e) degradation from hold-up
print("\n(e) Upper bound on extra oxidative degradation from tank hold-up (dissolved-O2 stoichiometry)")
o2_mg_l = (2.0, 3.0, 4.5)   # dissolved O2 in rich amine leaving absorber, 12-13% O2 flue at 40-50 C [assume]
for s, cap_b in (("MEA", 0.5), ("PZ", 0.86)):
    sol_per_t = 1e6 / 44.01 / cap_b / 1e3   # t solution per t CO2
    for o in o2_mg_l:
        mol_o2 = sol_per_t * o / 32.0        # mol O2 per t CO2 (1 m3 ~1 t)
        amine_kg = mol_o2 * 1.5 * (61.08 if s == "MEA" else 86.14) / 1e3   # 1.5 mol amine per mol O2 [assume]
        print(f"  {s} ({cap_b} mol/kg, {sol_per_t:.0f} t soln/t CO2), O2 {o} mg/L -> <= {amine_kg:.2f} kg amine/t CO2 "
              f"(all dissolved O2 consumed in tank; baseline MEA loss ~1-1.5 kg/t)")

# ---------------------------------------------------------------- cost per tonne
print("\n(f) Cost per tonne CO2 (captured and avoided), CF 40%")
# baseline: NETL $61/t captured at 85% CF [idea]; capital+fixed share 55-65% [assume]
for share in (0.55, 0.65):
    b = 61 * share * 0.85 / 0.40 + 61 * (1 - share)
    print(f"  CF-adjusted baseline (cap+FOM share {share:.0%}): ${b:.0f}/t captured at 40% CF")
base_cost = 61 * 0.60 * 0.85 / 0.40 + 61 * 0.40
annual_t = cap_tph * 8760 * 0.40
print(f"  annual capture at CF40: {annual_t/1e6:.3f} Mt")
mef_case = {"favourable": 50, "base": 250, "unfavourable": 400}
out = {}
for k, name in enumerate(("favourable", "base", "unfavourable")):
    added, saving, *_ = results[0.40][k]
    crf = 0.0707 if k < 2 else 0.10
    capex_per_t = (saving - added) * 1e6 * crf / annual_t
    inv_wc = results[0.40][k][2] * 1e6 * 0.08 / annual_t * 0   # amine already in capex; WC ignored
    sav_e, pl_, ou_ = arb[(0.40, name)]
    cost_capt = base_cost - capex_per_t - sav_e
    # avoided: shifted tonnes (60%) carry grid emissions ou_*MEF; baseline steam penalty emissions ignored
    grid_em = 0.60 * ou_ * mef_case[name] / 1000
    cost_avoid = cost_capt / (1 - grid_em) if grid_em < 1 else float('inf')
    out[name] = (cost_capt, cost_avoid, grid_em, capex_per_t, sav_e)
    print(f"  {name:<12}: capex saving ${capex_per_t:+.1f}/t, arbitrage ${sav_e:+.1f}/t -> ${cost_capt:.0f}/t captured; "
          f"grid emissions {grid_em:.2f} t/t at {mef_case[name]} g/kWh -> ${cost_avoid:.0f}/t net avoided "
          f"(vs baseline ${base_cost:.0f}/t captured)")

# ---------------------------------------------------------------- (g) scale and resources
print("\n(g) Scale and resources")
# gas-fired power CO2 ~3.3 Gt/yr (IEA order) [lit]; CCS on gas power operating today ~0; NZT Power ~2 Mt/yr from 2028 [lit]
for gt, lab in ((0.02, "low (handful of plants by 2040)"), (0.1, "base"), (0.4, "high")):
    sc = ScaleCheck(gt, 3.35 / 0.6 * 0.6)   # e-boiler heat only on shifted 60%: ~2.0 GJ_th/t avg
    e_twh = gt * 1e9 * 0.60 * (3.35 / 3.6 + comp) / 1e6
    amine_kt = gt * 1e9 / (0.95e6) * 71 * 0.3  # kt MEA inventory scaled from one plant (71 kt soln, 30%)
    tank_m3 = gt * 1e9 / 0.95e6 * 2 * 71e3 / 1.05
    print(f"  {lab:<32} {gt:.2f} Gt/yr: off-peak electricity {e_twh:.0f} TWh = {e_twh/WORLD_ELECTRICITY_TWH:.2%} "
          f"of world electricity; MEA inventory {amine_kt:.0f} kt; tankage {tank_m3/1e6:.1f} Mm3")
print(f"  base share of fossil CO2 ({FOSSIL_CO2_GT} Gt): {0.1/FOSSIL_CO2_GT:.2%}")
