"""Energy/scale/cost sanity checks for six single-graft ideas (electrochemistry / power electronics /
semiconductor manufacturing). All inputs marked ASSUMED are my assumptions, not sourced values."""
import math, sys
sys.path.insert(0, 'climate')
from physics import *

F = 96485.0
SEC_YR = 3.156e7
MOL_PER_T = 1e3 / M_CO2  # mol CO2 per tonne (kg/mol basis)

def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)

print("=" * 80)
print("IDEA 1  HFC-23 destruction with fab-style abatement interlock")
GWP_HFC23 = 14600  # AR6 GWP100
for gg in (14.0,):
    print(f"  {gg} Gg HFC-23 x GWP100 {GWP_HFC23} = {gg*1e3*GWP_HFC23/1e6:.0f} Mt CO2e/yr")
reported_mt = 41
gap = 14.0e3 * GWP_HFC23 / 1e6 - reported_mt
print(f"  gap vs ~{reported_mt} Mt reported-implied: {gap:.0f} Mt CO2e/yr")
# destruction cost: ASSUMED $5-10M capex per plant incinerator, 8%/15 yr, opex $0.5-2M/yr,
# plant destroys 200-1000 t HFC-23/yr
for capex, opex, t in ((5e6, 0.5e6, 1000), (10e6, 2e6, 200)):
    ann = capex * crf(0.08, 15) + opex
    print(f"  capex ${capex/1e6:.0f}M opex ${opex/1e6:.1f}M, {t} t HFC-23/yr -> "
          f"${ann/t:,.0f}/t HFC-23 = ${ann/(t*GWP_HFC23):.2f}/t CO2e")
# interlock + signed analyzer hardware, ASSUMED $0.3-1M per plant, ~30-40 plants globally
for n, c in ((30, 0.3e6), (40, 1.0e6)):
    print(f"  interlock+analyser fleet: {n} plants x ${c/1e6:.1f}M = ${n*c/1e6:.0f}M one-off; "
          f"per t CO2e over 10 yr of a 160 Mt gap: ${n*c/(gap*1e6*10):.4f}/t")

print("=" * 80)
print("IDEA 2  SOFC on stranded associated gas, N2-free anode CO2 -> injection")
LHV_CH4 = 50.0e-3  # GJ/kg ASSUMED pure-methane basis
CO2_PER_KG_CH4 = 44.01 / 16.04
for eta in (0.55, 0.60):
    gj_fuel = 3.6 / eta
    t_co2 = gj_fuel / LHV_CH4 * CO2_PER_KG_CH4 / 1e3
    mmbtu_hhv = gj_fuel * 1.109 / 1.055
    print(f"  eta_LHV {eta:.0%}: fuel {gj_fuel:.2f} GJ_LHV/MWh ({mmbtu_hhv:.2f} MMBtu HHV), "
          f"CO2 {t_co2:.3f} t/MWh; 45Q $85/t -> ${85*t_co2:.0f}/MWh; "
          f"gas at -$2.38/MMBtu pays ${2.38*mmbtu_hhv:.0f}/MWh, at +$2 costs ${2*mmbtu_hhv:.0f}/MWh")
# anode off-gas dry composition with fuel utilisation Uf (CH4 fully reformed: 1 C, 4 H2-equivalents)
for uf in (0.80, 0.85, 0.90):
    resid = 4 * (1 - uf)  # mol H2+CO equivalents left per mol C
    x_co2 = 1 / (1 + resid)  # treat CO as needing oxidation too; dry basis upper bound on impurity
    w = min_separation_work(x_co2, 0.98, 0.99)
    o2_t_per_t = (resid / 2) * 32 / 44.01
    print(f"  Uf {uf:.0%}: dry anode gas CO2 ~{x_co2:.0%}; separation floor (98% capture) "
          f"{gj_per_tonne(w):.3f} GJ/t; or oxidise residuals with {o2_t_per_t:.3f} t O2/t CO2 "
          f"= {o2_t_per_t*225/1e3*3.6:.3f} GJ_e/t at ASSUMED 225 kWh/t O2")
comp_floor = R * T0 * math.log(150e5 / 1e5)
print(f"  isothermal compression floor 1->150 bar: {gj_per_tonne(comp_floor):.3f} GJ/t; at 70% eff "
      f"{gj_per_tonne(comp_floor)/0.7:.2f} GJ/t -> parasitic per MWh at 0.33-0.36 t/MWh: "
      f"{gj_per_tonne(comp_floor)/0.7*0.33/3.6:.1%}-{gj_per_tonne(comp_floor)/0.7*0.36/3.6:.1%}")
print(f"  compare NGCC flue 4% floor {gj_per_tonne(min_separation_work(0.04,0.9)):.3f} GJ/t")
# LCOE before fuel: ASSUMED capex $2,500-4,500/kW, CRF 10%, CF 90%, O&M+stack $15-30/MWh
for capex, om in ((2500, 15), (4500, 30)):
    cap = capex * 0.10 / (8760 * 0.9) * 1e3
    print(f"  SOFC capex ${capex}/kW -> capital ${cap:.0f}/MWh + O&M/stack ${om} = ${cap+om:.0f}/MWh pre-fuel")
# scale: 1 bcf/d constrained gas
bcm = 1e9 * 0.0283168 * 365 / 1e9
gj = bcm * 1e9 * 0.0353  # ASSUMED 35.3 MJ/m3 LHV
print(f"  1 bcf/d = {bcm:.1f} bcm/yr = {gj/1e9:.2f} EJ LHV; at 57% -> {gj*0.57/3.6/1e6:.0f} TWh "
      f"({gj*0.57/3.6/8760/1e3:.1f} GW avg); CO2 ~{bcm*1e9*1.9/1e9:.0f} Mt/yr at ASSUMED 1.9 kg/m3")

print("=" * 80)
print("IDEA 3  Sorbent lifetime: cost per tonne vs cycles; HAST-style acceleration factors")
for q in (1.0, 2.0):
    for cs in (20, 50):
        row = []
        for n in (1_000, 5_000, 20_000, 100_000):
            row.append(f"N={n:>6}: ${cs*1000/(0.04401*q*n):>6.0f}/t")
        print(f"  q={q} mmol/g, sorbent ${cs}/kg: " + "  ".join(row))
k = 8.617e-5
def af(ea_ev, tu, ts, rh_u=None, rh_s=None, n=2.7, po2_ratio=1.0, order=1.0):
    a = math.exp(ea_ev / k * (1 / (tu + 273.15) - 1 / (ts + 273.15)))
    if rh_u:
        a *= (rh_s / rh_u) ** n
    return a * po2_ratio ** order
for ea_kj in (60, 90):
    ea = ea_kj / 96.485
    a1 = af(ea, 100, 120)
    a2 = af(ea, 100, 120, po2_ratio=100 / 21)
    print(f"  Ea {ea_kj} kJ/mol: 100->120C AF {a1:.1f}x; plus pure O2 (first order) {a2:.0f}x "
          f"-> 1 week of stress = {a2*7/30:.1f} months of 100C regeneration exposure")
# Mammoth-like utilisation sensitivity: capital per tonne scales 1/utilisation
for u in (0.0375, 0.27, 0.9):
    print(f"  utilisation {u:.1%}: capital charge multiplier vs 90% = {0.9/u:.1f}x")

print("=" * 80)
print("IDEA 4  Lithium from CO2-storage pressure-management brine")
for rho in (600, 750):
    print(f"  CO2 at {rho} kg/m3: {1000/rho:.2f} m3 pore per t")
for c in (20, 50, 100, 200, 400):
    out = []
    for r_ratio in (0.3, 1.0):
        li_g = 1.5 * r_ratio * c * 0.85  # m3/t * ratio * g/m3 * recovery
        lce = li_g * 5.323 / 1e3
        out.append(f"R={r_ratio}: {li_g:>4.0f} g Li = {lce:.2f} kg LCE -> ${lce*10:.0f}-{lce*20:.0f}/t CO2 "
                   f"gross (margin ${lce*4:.0f}-{lce*13:.0f})")
    print(f"  Li {c:>3} mg/L | " + " | ".join(out))
# pumping energy for brine lift+reinjection ASSUMED 20 MPa, 70% pump eff
e = 20e6 / 0.7 / 1e9
print(f"  brine pumping ~{e:.3f} GJ/m3 -> {e*1.5*0.5:.3f} GJ/t CO2 at R=0.5 (vs compression floor "
      f"{gj_per_tonne(comp_floor):.2f})")
# Gorgon example: 4 Mt/yr requirement
for c in (20, 100):
    lce_t = 4e6 * 1.5 * 0.5 * c * 0.85 * 5.323 / 1e6
    print(f"  4 Mt/yr site, R=0.5, {c} mg/L: {lce_t:,.0f} t LCE/yr")

print("=" * 80)
print("IDEA 5  Flexible NGCC capture: rich-solvent storage + electrified (heat pump/electrode) stripper")
mw, t_per_mwh, cap = 742, 0.35, 0.90  # ASSUMED NZT-like
peak = mw * t_per_mwh * cap
for on_h in (10, 14):
    avg = peak * on_h / 24
    store = (peak - avg) * on_h
    for dalpha in (0.25, 0.35):
        g_per_kg = 4.91 * dalpha * 44.01  # 30 wt% MEA = 4.91 mol/kg
        solvent_t = store / (g_per_kg / 1000)
        print(f"  on {on_h} h/d: peak {peak:.0f} t/h, stripper avg {avg:.0f} t/h ({avg/peak:.0%} of peak), "
              f"store {store:,.0f} t CO2; dalpha {dalpha}: {g_per_kg:.0f} g/kg -> {solvent_t:,.0f} t solvent per tank")
cf = 10 / 24
tpy = peak * 8760 * cf
print(f"  annual capture at CF {cf:.0%}: {tpy/1e6:.2f} Mt")
base_capex = 742e3 * 966  # NETL H-class capture adder ~$966/kW (2018$)
for strip_share in (0.35, 0.50):
    saving = base_capex * strip_share * (1 - cf)
    for store_cost in (25e6, 60e6):
        net = (saving - store_cost) * crf(0.08, 25)
        print(f"  stripper+compr share {strip_share:.0%}: capex saving ${saving/1e6:.0f}M, storage ${store_cost/1e6:.0f}M"
              f" -> ${net/tpy:.0f}/t CO2 annualised")
# regeneration energy
reb = 2.7  # GJ_th/t ASSUMED
for label, cop, price in (("electrode boiler", 1.0, 25), ("electrode boiler", 1.0, 40),
                          ("heat pump", 2.0, 25), ("heat pump", 2.0, 40)):
    kwh = reb / cop / 0.0036
    print(f"  {label} COP {cop}, ${price}/MWh off-peak: {kwh:.0f} kWh/t -> ${kwh*price/1e3:.0f}/t")
exg = reb * (1 - T0 / (273.15 + 125))
print(f"  steam-extraction alternative: exergy {exg:.2f} GJ/t ~ {exg/0.0036/0.9:.0f} kWh lost at peak"
      f" -> ${exg/0.0036/0.9*90/1e3:.0f}/t at $90/MWh")
carnot = (273.15 + 125) / (125 - 30)
carnot2 = (273.15 + 125) / (125 - 70)
print(f"  heat-pump Carnot COP 30->125C {carnot:.1f}, 70->125C {carnot2:.1f}; real at 45%: "
      f"{0.45*carnot:.1f}, {0.45*carnot2:.1f}")
derate = mw * 0.15
print(f"  peak derate avoided ~{derate:.0f} MW x GBP 60k/MW-yr capacity value = GBP {derate*60e3/1e6:.1f}M/yr"
      f" = GBP {derate*60e3/tpy:.0f}/t")

print("=" * 80)
print("IDEA 6  Electrochemical regeneration: electrode area, optimal current density, gas-side limit")
def area_per_tpy(j, n=1.0, avail=0.9):
    return n * F * MOL_PER_T / (j * SEC_YR * avail)
for j in (100, 300, 1000, 3000):
    print(f"  j={j:>5} A/m2: {area_per_tpy(j):.3f} m2 per t/yr (n=1), {area_per_tpy(j,2):.3f} (n=2); "
          f"1 Mt/yr -> {area_per_tpy(j)*1e6/1e6:.2f} km2 (n=1)")
for cost in (200, 500, 2000):
    print(f"  stack ${cost}/m2: capex per t/yr at 100 A/m2 ${cost*area_per_tpy(100):,.0f}; at 1000 A/m2 "
          f"${cost*area_per_tpy(1000):,.0f} (amine reference $700-2,250 per t/yr)")
# optimal j: cost/mol = Acost*CRF/(j/(nF)*SEC*avail) + p*nF*(V0 + j*ASR)
def cost_per_t(j, cost_m2, asr_ohm_cm2, v0, p_mwh, n=1.0, r=0.10, avail=0.9):
    asr = asr_ohm_cm2 * 1e-4  # ohm m2
    cap = cost_m2 * r / (j / (n * F) * SEC_YR * avail) * MOL_PER_T
    en_j_per_mol = n * F * (v0 + j * asr)
    en = en_j_per_mol * MOL_PER_T / 3.6e9 * p_mwh
    return cap, en, en_j_per_mol / 1e3
for cost_m2, asr, v0, p in ((500, 1.0, 0.8, 40), (500, 10.0, 0.8, 40), (2000, 10.0, 0.8, 40), (500, 3.0, 0.8, 40)):
    js = [10 * 1.1 ** i for i in range(120)]
    best = min(js, key=lambda j: sum(cost_per_t(j, cost_m2, asr, v0, p)[:2]))
    cap, en, kj = cost_per_t(best, cost_m2, asr, v0, p)
    cap100, en100, kj100 = cost_per_t(100, cost_m2, asr, v0, p)
    print(f"  ${cost_m2}/m2, ASR {asr} ohm.cm2, V0 {v0} V, ${p}/MWh: j*={best:.0f} A/m2 -> "
          f"capital ${cap:.0f}/t + energy ${en:.0f}/t ({kj:.0f} kJ/mol, {gj_per_tonne(kj*1e3):.2f} GJ/t); "
          f"at 100 A/m2: ${cap100:.0f}+${en100:.0f}/t ({kj100:.0f} kJ/mol)")
# gas-side mass-transfer ceiling for electrode-contact capture
for x, label in ((420e-6, "air 420 ppm"), (0.01, "smelter 1%"), (0.04, "NGCC 4%")):
    c = P0 / (R * T0) * x
    for kg in (0.01, 0.05):
        flux = c * kg
        print(f"  {label}: C={c:.4f} mol/m3, k_g={kg} m/s -> max flux {flux:.2e} mol/m2/s -> "
              f"j_lim {flux*F:.0f} A/m2 (n=1) -> >= {area_per_tpy(flux*F):.2f} m2 per t/yr")
air_floor = gj_per_tonne(min_separation_work(420e-6, 0.75))
print(f"  floor air {air_floor:.3f} GJ/t = {min_separation_work(420e-6,0.75)/1e3:.1f} kJ/mol; "
      f"phenazine 104 kJ/mol = {gj_per_tonne(104e3):.2f} GJ/t (eta_II {second_law_efficiency(gj_per_tonne(104e3), air_floor):.0%})")
s = ScaleCheck(1.0, gj_per_tonne(130e3))
print(f"  1 Gt/yr at 130 kJ/mol electric: {s.ej_per_year:.2f} EJ = {s.share_of_world_electricity_if_electric:.1%} of world electricity")

print("=" * 80)
print("IDEA 6 add-on: Gt-scale membrane area vs today's chlor-alkali industry")
cl2_t = 95e6  # ASSUMED ~95 Mt/yr global chlorine
e_mol = cl2_t * 1e6 / 70.9 * 2
amps = e_mol * F / SEC_YR
for jca in (4000, 6000):
    print(f"  chlor-alkali: {cl2_t/1e6:.0f} Mt Cl2/yr -> {amps/1e9:.1f} GA -> {amps/jca/1e6:.2f} km2 at {jca} A/m2")
for j in (500, 1000, 3000):
    a = area_per_tpy(j) * 1e9 / 1e6
    print(f"  1 Gt/yr CO2 regen (n=1, 90% avail) at {j} A/m2: {a:.0f} km2 = "
          f"{a/(amps/5000/1e6):.0f}x the chlor-alkali membrane area at 5 kA/m2")
# Sabatino 2022 base case 24 GJ/t vs floor
print(f"  Sabatino 2022 base case 24 GJ/t = {24*M_CO2*1e3:.0f} kJ/mol; eta_II {second_law_efficiency(24, air_floor):.1%}")
# Idea 2 comparison: amine on 4% flue real ~1.0-1.4 GJe/t (map) vs SOFC route
for o2 in (0.12, 0.24):
    print(f"  SOFC route: residual-oxidation {o2} + compression 0.40 = {o2+0.40:.2f} GJ_e/t vs amine-NGCC 1.0-1.4 GJ_e/t")
