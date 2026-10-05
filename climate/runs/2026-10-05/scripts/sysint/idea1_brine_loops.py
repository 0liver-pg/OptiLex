"""Idea 1: dissolve concentrated CO2 into brine that is already being re-injected
(oilfield saltwater disposal, DLE lithium brine, geothermal re-injection)."""
from common import *

BBL = 0.158987
print("== Solubility at design points (approx model; ks range 0.065-0.11) ==")
hosts = {
  # name: (T_C used for solubility (capped at 60C, conservative), far-field min pressure bar, salt molality)
  "Permian shallow SWD (Delaware Mtn Grp ~1.2 km, ~2.5 m NaCl-eq)": (40, 110, 2.5),
  "Permian deep SWD (Ellenburger/Devonian ~4 km, ~2 m)":           (60, 380, 2.0),
  "Smackover DLE re-injection (~2.5 km, ~5 m)":                     (60, 250, 5.0),
  "Upper Rhine geothermal re-injection (~3 km, ~1.8 m)":           (60, 280, 1.8),
}
design_frac = 0.5   # dissolve to <=50% of saturation at the lowest far-field pressure (no exsolution)
res = {}
for name, (Tc, Pbar, m) in hosts.items():
    T = Tc + 273.15
    lo = co2_solubility_mol_kg(T, Pbar * 1e5, m, ks=0.11)
    hi = co2_solubility_mol_kg(T, Pbar * 1e5, m, ks=0.065)
    # kg CO2 per m3 brine; ~0.85-0.95 kg water per litre of brine
    wfrac = 0.95 if m < 3 else 0.85
    kgm3 = [s * design_frac * M_CO2 * 1000 * wfrac for s in (lo, hi)]
    res[name] = kgm3
    print(f"{name}: sat {lo:.2f}-{hi:.2f} mol/kg -> design {kgm3[0]:.0f}-{kgm3[1]:.0f} kg CO2/m3 "
          f"= {1000/kgm3[1]:.0f}-{1000/kgm3[0]:.0f} m3 brine per t CO2")

print("\n== Permian scale (produced water ~20-23 Mbbl/d: B3/Enverus-type figure, unverified here) ==")
for mbbl in (20, 23):
    m3yr = mbbl * 1e6 * BBL * 365
    lo, hi = res["Permian shallow SWD (Delaware Mtn Grp ~1.2 km, ~2.5 m NaCl-eq)"]
    print(f"{mbbl} Mbbl/d = {m3yr/1e9:.2f} km3/yr -> {m3yr*lo/1e9:.0f}-{m3yr*hi/1e9:.0f} Mt CO2/yr carrying capacity")
# Permian gas-processing CO2 (my estimate): 25-28 bcf/d gas, 1-3% CO2
for bcfd, frac in ((25, 0.01), (27, 0.02), (28, 0.03)):
    m3 = bcfd * 1e9 * 0.0283168 * frac
    t = m3 * 1.87 / 1000 * 365   # kg/m3 at ~15C, 1 atm
    print(f"Permian gas {bcfd} bcf/d at {frac:.0%} CO2 -> {t/1e6:.1f} Mt CO2/yr separated at gas plants")

print("\n== Energy: compression only to the mixing pressure (verifier-style ideal isothermal) ==")
for p in (30, 60, 100, 150):
    w = iso_comp_gj_t(1.0, p)
    print(f"1 -> {p} bar: ideal {w:.3f} GJ/t; at 65% isothermal eff {w/0.65:.3f} GJ/t = {w/0.65/0.0036:.0f} kWh/t")
print(f"Separation floor for an amine-vent stream (95% CO2 -> 99%): "
      f"{gj_per_tonne(min_separation_work(0.95, 0.9, 0.99)):.3f} GJ/t")
print(f"Reference: conventional supercritical injection (1->150 bar) ideal {iso_comp_gj_t(1,150):.3f} GJ/t")

print("\n== Added volume (pressure/seismicity) ==")
vbar = 3.3e-5  # m3/mol partial molar volume of dissolved CO2
for kg in (10, 20, 30):
    print(f"{kg} kg CO2/m3 -> +{kg/0.04401*vbar*100:.1f}% fluid volume vs brine alone; "
          f"free-phase CO2 at ~700 kg/m3 would add {kg/700*100:.1f}%")

print("\n== Smackover DLE coupling: lithium co-produced per tonne CO2 stored ==")
for li_mgL in (350, 582):   # 582 mg/L = 2025 Lafayette Co. AR average (Wikipedia, Smackover Formation)
    for kg in res["Smackover DLE re-injection (~2.5 km, ~5 m)"]:
        m3_t = 1000 / kg
        li = m3_t * li_mgL / 1000 * 0.9       # kg Li per t CO2, 90% DLE recovery
        lce = li * 5.323
        print(f"Li {li_mgL} mg/L, {kg:.0f} kg CO2/m3: {m3_t:.0f} m3/t -> {lce:.0f} kg LCE per t CO2 "
              f"= {1000/lce:.1f} t CO2 per t LCE")
# 45Q value per tonne LCE at $85/t
for t_per_lce in (8, 15, 25):
    print(f"  45Q $85/t x {t_per_lce} t CO2/t LCE = ${85*t_per_lce:,.0f} per t LCE "
          f"({85*t_per_lce/12000:.0%} of a $12k/t LCE price)")
# a 22.5 kt/yr LCE plant (SWA-scale, from memory)
for kg in res["Smackover DLE re-injection (~2.5 km, ~5 m)"]:
    li_t = 22500 / 5.323
    m3 = li_t * 1000 / (0.582 * 0.9)   # 582 mg/L
    print(f"22.5 kt LCE/yr at 582 mg/L -> {m3/1e6:.1f} Mm3/yr brine -> {m3*kg/1e9:.2f} Mt CO2/yr at {kg:.0f} kg/m3")

print("\n== Incremental cost sketch ($/t CO2), my assumptions ==")
p_mwh = 50
comp = iso_comp_gj_t(1, 60) / 0.65 / 0.0036 * p_mwh / 1000
capex_comp = 300 * 1e6 / 1e6   # $ per t/yr capacity? use $60-120 per t/yr for small compressor+mixer
for capex_tpy in (60, 120):
    ann = capex_tpy * crf(0.08, 20)
    mrv = 5   # $/t monitoring (Subpart RR + downhole sampling), assumption
    tub = 3   # $/t corrosion-resistant tubing/completions amortised, assumption
    tot = comp + ann + mrv + tub
    print(f"compression energy ${comp:.1f}/t + capex ${ann:.1f}/t + MRV ${mrv}/t + tubing ${tub}/t = ${tot:.0f}/t "
          f"vs 45Q $85/t (margin ${85-tot:.0f}/t)")
