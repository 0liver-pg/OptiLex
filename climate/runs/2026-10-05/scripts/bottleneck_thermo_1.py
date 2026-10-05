"""Verifier for idea bottleneck_thermo_1: passive solar collector-adsorber DAC panel
(night air loading, day atmospheric steam sweep by the panel's own solar heat).

Independent re-check of the idea's claims. Differences from the proposer's script (thermo_ideas2.py):
  * collector heat is SIMULATED hour by hour (EN 12975-style efficiency curve, morning warm-up of the
    whole panel thermal mass, then desorption at T_reg) instead of an assumed 35-50% daily efficiency;
  * sorbent mass per m2 is solved self-consistently with the daily loading (more loading -> more
    sorbent -> more sensible heat);
  * working capacity is reduced for 1-atm regeneration (no vacuum, so residual loading is higher);
  * purge steam, condenser fan, field balance-of-plant, sorbent replacement and CRF are explicit.
Every assumption is labelled: [lit] = literature/handbook value quoted from memory (not re-verified this
run, web search budget exhausted), [claim] = the idea's own number, [eng] = engineering judgement.
"""
import sys, math
sys.path.insert(0, 'climate')
from physics import *

MW = 44.01e-3
LAT_H2O = 44.0          # kJ/mol, latent heat of water ~ near 100 C (40.7 at 100 C + sensible) [lit]
dac_floor = gj_per_tonne(min_separation_work(420e-6, 0.75, 0.99))
comp_floor = gj_per_tonne(R * T0 * math.log(150.0))
print("=" * 100)
print("0. FLOORS (OptiLex verifier)")
print(f"  separation floor, air 420 ppm, 75% capture, 99% pure: {dac_floor:.3f} GJ/t ({dac_floor/0.0036:.0f} kWh/t)")
print(f"  isothermal compression 1->150 bar floor:               {comp_floor:.3f} GJ/t")
print(f"  air to process: {air_volume_per_tonne(420e-6, 0.75):,.0f} m3/t;  fan work at 10 Pa/60%: "
      f"{fan_work_gj_per_tonne(420e-6, 0.75, 10):.3f} GJ/t; at 15 Pa/30% (small fans): "
      f"{fan_work_gj_per_tonne(420e-6, 0.75, 15, 0.30):.3f} GJ/t")

# ---------------------------------------------------------------- 1. K2CO3 thermochemistry check
print("\n1. K2CO3 + CO2 + H2O(g) <-> 2 KHCO3 (NBS tables, 298 K) [lit]")
Hf = {"K2CO3": -1151.02, "KHCO3": -963.2, "CO2": -393.51, "H2O": -241.82}       # kJ/mol
S = {"K2CO3": 155.52, "KHCO3": 115.5, "CO2": 213.74, "H2O": 188.83}             # J/mol/K
dH = 2 * Hf["KHCO3"] - Hf["K2CO3"] - Hf["CO2"] - Hf["H2O"]
dS = 2 * S["KHCO3"] - S["K2CO3"] - S["CO2"] - S["H2O"]
K = lambda T: math.exp(-(dH * 1e3 - T * dS) / (R * T))     # = 1/(pCO2 pH2O), bar^-2
print(f"  dH {dH:.1f} kJ/mol, dS {dS:.1f} J/mol/K (constant-dH approximation)")
print(f"  night equilibrium pCO2 at 25 C, pH2O 0.01 bar: {1/(K(298.15)*0.01):.2e} bar (air: 4.2e-4) -> loading favoured")
T_for = lambda prod: dH * 1e3 / (dS - R * math.log(prod)) if False else (dH * 1e3) / (dS + R * math.log(1 / prod))
for label, pc, pw in (("self-pressurised 1 atm (0.5/0.5)", 0.5, 0.5), ("steam swept, pCO2 0.2 / pH2O 0.8", 0.2, 0.8),
                      ("steam swept, pCO2 0.1 / pH2O 0.9", 0.1, 0.9), ("claim: 0.2 bar total (0.1/0.1)", 0.1, 0.1)):
    # equilibrium: K(T) = 1/(pc*pw)  ->  -dH/RT + dS/R = ln(1/(pc pw))
    T = -dH * 1e3 / (R * math.log(1 / (pc * pw)) - dS)
    print(f"  release equilibrium, {label:34s}: T >= {T-273.15:.0f} C")
print(f"  enthalpy {-dH:.0f} kJ/mol = {(-dH)/(dac_floor*44.01):.1f}x the separation floor ({dac_floor*44.01:.1f} kJ/mol)")

# ---------------------------------------------------------------- 2. hourly collector-bed simulation
def day_heat(L_kg, v, insol_kwh, ta_day=30.0, t_start=20.0, dt_s=60.0):
    """Return (desorption heat available kJ/m2/day, sensible heat kJ/m2, hours at T_reg) for loading L."""
    n_mol = L_kg / MW                                  # mol CO2 per m2 per day
    m_s = n_mol / v["w"]                                # kg sorbent per m2 (w in mol/kg = mmol/g)
    C = m_s * (v["cp_s"] + v["struct"] * 0.9) + v["C_case"] + n_mol * v["nH2O"] * 0.018 * 4.18  # kJ/K/m2
    gpk = insol_kwh * 1000 / (24 / math.pi)            # W/m2 peak for a half-sine 06-18 h day
    T, q_des, sens, hrs = t_start, 0.0, 0.0, 0.0
    t = 6 * 3600.0
    while t < 18 * 3600:
        G = gpk * math.sin(math.pi * (t / 3600 - 6) / 12)
        dT = T - ta_day
        q = (v["eta0"] * G - v["a1"] * dT - v["a2"] * dT * abs(dT)) * dt_s / 1e3   # kJ/m2 this step
        if T < v["T_reg"]:
            T += q / C
            sens += max(q, 0)
        else:
            if q > 0:
                q_des += q
                hrs += dt_s / 3600
            else:
                T += q / C
        t += dt_s
    return q_des, C * (v["T_reg"] - t_start), hrs, m_s


def per_mol_heat(v, L_kg):
    n = L_kg / MW
    return v["dH"] + v["nH2O"] * LAT_H2O + v["purge_mol_m2"] * LAT_H2O / n    # kJ per mol CO2 (desorption phase)


BED_CAP = {"low": 15.0, "base": 10.0, "high": 7.5}   # kg sorbent/m2 that fits a 3-5 cm layer at 250-300 kg/m3 [claim depth; eng density]

def max_loading(v, insol):
    lo, hi = 1e-4, 3.0
    for _ in range(60):
        mid = (lo + hi) / 2
        q_des, _, _, _ = day_heat(mid, v, insol)
        if q_des >= per_mol_heat(v, mid) * mid / MW:
            lo = mid
        else:
            hi = mid
    return lo


# variant parameter sets: low = optimistic (low cost), base, high = pessimistic (high cost)
COMMON = {"C_case": {"low": 5, "base": 8, "high": 12}}   # kJ/K/m2 absorber+glass+frame swing [eng]
amine = {
    "low":  dict(w=1.2, dH=70, nH2O=3.0, purge_mol_m2=2.0, cp_s=1.5, struct=0.5, T_reg=100, eta0=0.80, a1=3.5, a2=0.015),
    "base": dict(w=0.8, dH=75, nH2O=5.0, purge_mol_m2=3.5, cp_s=1.5, struct=0.5, T_reg=105, eta0=0.75, a1=4.5, a2=0.015),
    "high": dict(w=0.5, dH=80, nH2O=8.0, purge_mol_m2=5.0, cp_s=1.5, struct=0.5, T_reg=110, eta0=0.75, a1=4.5, a2=0.015),
}
k2co3 = {
    "low":  dict(w=0.8, dH=140, nH2O=0.5, purge_mol_m2=2.0, cp_s=1.0, struct=0.5, T_reg=130, eta0=0.65, a1=1.2, a2=0.008),
    "base": dict(w=0.6, dH=140, nH2O=1.5, purge_mol_m2=3.5, cp_s=1.0, struct=0.5, T_reg=140, eta0=0.72, a1=2.8, a2=0.012),
    "high": dict(w=0.35, dH=140, nH2O=3.0, purge_mol_m2=5.0, cp_s=1.0, struct=0.5, T_reg=150, eta0=0.72, a1=2.8, a2=0.012),
}
for d in (amine, k2co3):
    for c in d:
        d[c]["C_case"] = COMMON["C_case"][c]
INSOL = {"low": 7.0, "base": 6.5, "high": 5.5}         # kWh/m2/day tilted aperture, desert annual mean [claim range]
DAYS = {"low": 330, "base": 300, "high": 270}           # productive cycles per year [claim 300; eng range]

print("\n2. HOURLY COLLECTOR-BED SIMULATION (half-sine day 06-18 h, ambient 30 C, bed starts 20 C)")
print("   collector curves [lit, typical Solar Keymark ranges]: selective flat plate eta0 0.75-0.82, a1 3-4, a2 ~0.015;")
print("   evacuated tube eta0 ~0.65, a1 ~1.2; deep louvred box assumed to lose more (a1 4.5-6) [eng]")
results = {}
for name, d in (("amine/silica", amine), ("K2CO3/carbon", k2co3)):
    for case in ("low", "base", "high"):
        v = d[case]
        L_heat = max_loading(v, INSOL[case])
        L_bed = BED_CAP[case] * v["w"] * MW          # kg CO2/m2/day if the 3-5 cm bed is fully cycled once
        L = min(L_heat, L_bed)
        print(f"  {name:13s} {case:4s}: heat-limited {L_heat:.2f} vs bed-depth-limited {L_bed:.2f} kg/m2/day "
              f"({BED_CAP[case]} kg/m2 sorbent) -> binding: {'heat' if L_heat < L_bed else 'bed depth'}")
        q_des, sens, hrs, m_s = day_heat(L, v, INSOL[case])
        qmol = per_mol_heat(v, L)
        q_need = per_mol_heat(v, L) * L / MW if L > 1e-3 else q_des    # desorption heat actually used, kJ/m2
        q_tot_t = (min(q_need, q_des) + sens) / max(L / MW, 1e-9) / 44.01      # kJ/mol -> GJ/t
        eff = (q_des + sens) / (INSOL[case] * 3600)
        if L < 0.02:
            print(f"  {name:13s} {case:4s}: PANEL DOES NOT REACH/HOLD T_reg {v['T_reg']} C -> no output (cost unbounded)")
        results[(name, case)] = dict(L=L, m_s=m_s, q_t=q_tot_t, eff=eff, hrs=hrs, v=v)
        print(f"  {name:13s} {case:4s}: w {v['w']} mmol/g, T_reg {v['T_reg']} C, H2O {v['nH2O']} mol/mol -> max loading "
              f"{L:.2f} kg/m2/day, sorbent {m_s:.1f} kg/m2, {hrs:.1f} h at T_reg, daily collector eff {eff:.0%}, "
              f"solar heat {q_tot_t:.1f} GJ_th/t (desorption {qmol:.0f} kJ/mol + sensible)")
# claim's own parameters through this simulation
v_c = dict(amine["base"]); v_c.update(w=1.2, nH2O=3.0, purge_mol_m2=0.0, T_reg=105, eta0=0.80, a1=3.5, a2=0.015, C_case=0)
print(f"  claim parameters (amine 1.2 mmol/g, 3 mol H2O, no purge, no casing mass, good flat plate), 6.5 kWh: "
      f"heat-limited {max_loading(v_c, 6.5):.2f} kg/m2/day (claim 1.25)")
v_c2 = dict(k2co3["base"]); v_c2.update(w=0.8, nH2O=0.0, purge_mol_m2=0.0, T_reg=141, eta0=0.65, a1=1.2, a2=0.008, C_case=0)
print(f"  claim parameters (K2CO3 0.8 mmol/g, 141 C, evacuated-tube curve, no casing mass): heat-limited "
      f"{max_loading(v_c2, 6.5):.2f} kg/m2/day (claim 0.97)")
# failure modes
v_f = dict(amine["base"]); v_f.update(eta0=0.72, a1=6.0, a2=0.018)
print(f"  amine, leaky louvred box (eta0 0.72, a1 6.0) at 5.5 kWh: max loading {max_loading(v_f, 5.5):.2f} kg/m2/day; at 6.5 kWh: {max_loading(v_f, 6.5):.2f}")
# non-selective single glazing: show failure mode
v_ns = dict(amine["base"]); v_ns.update(eta0=0.78, a1=7.5, a2=0.02)
print(f"  amine, NON-selective single-glazed box (a1 7.5): max loading {max_loading(v_ns, 6.5):.2f} kg/m2/day "
      "-> a selective absorber (or double glazing) is mandatory")
v_fk = dict(k2co3["base"]); v_fk.update(eta0=0.80, a1=3.5, a2=0.015)
print(f"  K2CO3 at 140 C in a good SINGLE-glazed selective flat plate: max loading {max_loading(v_fk, 6.5):.2f} kg/m2/day")
print("  claim check: idea states heat-limited ceilings 1.25 (amine) / 0.97 (K2CO3) kg/m2/day and designs at 0.3-0.6")

# ---------------------------------------------------------------- 3. exergy / floor check
print("\n3. FLOOR CHECK")
for (name, case), r in results.items():
    ex = r["q_t"] * (1 - T0 / (r["v"]["T_reg"] + 273.15))
    print(f"  {name:13s} {case:4s}: heat exergy {ex:.2f} GJ/t vs separation floor {dac_floor:.2f} -> eta_II(sep) {dac_floor/ex:.0%}"
          f"{'  BELOW FLOOR' if ex < dac_floor else ''}")
print("  claimed purchased electricity 0.46 GJe/t is below the 0.47 separation floor, but that is NOT a violation:")
print("  the separation work is supplied by solar heat exergy (above); electricity only covers compression.")

# ---------------------------------------------------------------- 4. electricity, energy per tonne
print("\n4. ENERGY PER TONNE")
ELEC = {}
for case, (comp_eff, fan_pa, fan_eff, cond_frac, aux) in {
        "low": (0.70, 0.0, 0.6, 0.010, 0.02),     # wind-driven, no fan
        "base": (0.65, 10.0, 0.5, 0.015, 0.03),
        "high": (0.60, 15.0, 0.3, 0.020, 0.05)}.items():
    for name, d in (("amine/silica", amine), ("K2CO3/carbon", k2co3)):
        v = d[case]
        comp = comp_floor / comp_eff
        fan = fan_work_gj_per_tonne(420e-6, 0.75, fan_pa, fan_eff) if fan_pa else 0.0
        steam_t = (v["nH2O"] * LAT_H2O + v["purge_mol_m2"] * LAT_H2O / (results[(name, case)]["L"] / MW)) / 44.01
        cond = cond_frac * steam_t                    # air-cooled condenser fans, ~1-2% of heat rejected [eng]
        e = comp + fan + cond + aux
        ELEC[(name, case)] = e
        r = results[(name, case)]
        print(f"  {name:13s} {case:4s}: electricity {e:.2f} GJe/t ({e/0.0036:.0f} kWh/t: comp {comp:.2f}, fan {fan:.3f}, "
              f"condenser {cond:.3f}, aux {aux:.2f}); solar heat {r['q_t']:.1f} GJ_th/t; "
              f"1 Gt/yr = {ScaleCheck(1, e).share_of_world_electricity_if_electric:.2%} of world electricity")
print("  claim: 0.46 GJe/t (129 kWh/t) vs Climeworks Gen2 stated 2.34 GJe/t (company-stated, not measured)")

# ---------------------------------------------------------------- 5. cost per tonne
print("\n5. LEVELISED COST OF REMOVAL ($/t CO2 captured and stored; gross, before life-cycle emissions)")
crf = lambda i, n: i * (1 + i) ** n / ((1 + i) ** n - 1)
CP = {  # panel $/m2 installed, BOS $ per t/yr, panel life yr, discount, O&M %capex, $/MWh, T&S $/t, sorbent $/kg, sorbent life yr
    ("amine/silica", "low"): (120, 150, 25, 0.06, 0.02, 40, 15, 10, 10),
    ("amine/silica", "base"): (200, 350, 20, 0.08, 0.03, 60, 25, 20, 5),
    ("amine/silica", "high"): (350, 700, 15, 0.10, 0.05, 80, 40, 50, 2),
    ("K2CO3/carbon", "low"): (150, 150, 25, 0.06, 0.02, 40, 15, 2, 15),
    ("K2CO3/carbon", "base"): (250, 350, 20, 0.08, 0.03, 60, 25, 4, 8),
    ("K2CO3/carbon", "high"): (400, 700, 15, 0.10, 0.05, 80, 40, 8, 3),
}
COST = {}
for (name, case), (panel, bos, life, i, om, pe, ts, sp, slife) in CP.items():
    r = results[(name, case)]
    t_m2_yr = r["L"] * DAYS[case] / 1000
    m2 = 1 / t_m2_yr
    sorb_kg = r["m_s"] * m2
    capex = panel * m2 + bos
    cap_charge = capex * crf(i, life)
    sorb_cost = sorb_kg * sp * crf(i, slife)          # inventory annuitised over its own life
    omc = om * capex
    elec = ELEC[(name, case)] / 3.6 * pe
    total = cap_charge + sorb_cost + omc + elec + ts
    COST[(name, case)] = dict(total=total, m2=m2, sorb=sorb_kg, capex=capex + sorb_kg * sp)
    print(f"  {name:13s} {case:4s}: {r['L']:.2f} kg/m2/d x {DAYS[case]} d -> {m2:.1f} m2 & {sorb_kg:.0f} kg sorbent per t/yr; "
          f"capex ${capex + sorb_kg*sp:,.0f} per t/yr (panel ${panel}/m2, BOS ${bos}, sorbent ${sp}/kg)")
    print(f"      capital ${cap_charge:.0f} + sorbent ${sorb_cost:.0f} (life {slife} yr) + O&M ${omc:.0f} + electricity ${elec:.0f} "
          f"(${pe}/MWh) + T&S ${ts} = ${total:,.0f}/t")
# moderate-high case: pessimistic chemistry and costs, but base collector and base sun
for name, d in (("amine/silica", amine), ("K2CO3/carbon", k2co3)):
    v = dict(d["high"]); vb = d["base"]; v.update(eta0=vb["eta0"], a1=vb["a1"], a2=vb["a2"])
    L = min(max_loading(v, 6.5), BED_CAP["high"] * v["w"] * MW)
    q_des, sens, hrs, m_s = day_heat(L, v, 6.5)
    panel, bos, life, i, om, pe, ts, sp, slife = CP[(name, "high")]
    m2 = 1 / (L * 300 / 1000); sk = m_s * m2; capex = panel * m2 + bos
    tot = capex * crf(i, life) + sk * sp * crf(i, slife) + om * capex + 0.7 / 3.6 * pe + ts
    print(f"  moderate-high {name}: high chemistry/costs, base collector & 6.5 kWh, 300 d: {L:.2f} kg/m2/d, {m2:.1f} m2, "
          f"{sk:.0f} kg sorbent per t/yr -> ${tot:,.0f}/t")
# sorbent-life sensitivity, amine base
for slife in (2, 5, 10):
    r = results[("amine/silica", "base")]; m2 = 1 / (r["L"] * 300 / 1000); sk = r["m_s"] * m2
    print(f"  amine base, sorbent life {slife} yr at $20/kg: sorbent charge ${sk*20*crf(0.08, slife):.0f}/t; at $10/kg ${sk*10*crf(0.08, slife):.0f}/t")
print("  claim: K2CO3 $150-230/t, amine $290-520/t; Stratos ~$2,600 per t/yr [claim]; Fan & Xu 2026 CSP+sand DAC $160-200/t core (modelled)")

# sensitivity: the claim's own design point under the base cost stack
print("\n  sensitivity: claim's design points re-costed with base cost stack (only loading/w changed)")
for name, Lc, w, sp in (("amine", 0.6, 1.2, 20), ("amine", 0.3, 1.2, 20), ("K2CO3", 0.6, 0.8, 4)):
    m2 = 1 / (Lc * 300 / 1000)
    sk = Lc / MW / w * m2
    capex = 200 * m2 + 350
    slife = 5 if name == "amine" else 8
    tot = capex * crf(0.08, 20) + sk * sp * crf(0.08, slife) + 0.03 * capex + 0.5 / 3.6 * 60 + 25
    print(f"    {name} {Lc} kg/m2/d, {w} mmol/g: {m2:.1f} m2, {sk:.0f} kg sorbent per t/yr -> ${tot:,.0f}/t")

# ---------------------------------------------------------------- 6. simple baseline: PV + heat pump conventional DAC
print("\n6. BASELINE: conventional sorbent DAC, same desert, PV electricity")
for pe in (30, 45):
    for cop in (2.0, 2.8):
        e = 2.34 + 7.2 / cop     # Climeworks-stated 2.34 GJe + 7.2 GJth/t [company-stated], heat pump at COP
        print(f"  PV ${pe}/MWh, heat pump COP {cop}: {e:.1f} GJe/t -> energy ${e/3.6*pe:.0f}/t "
              "(but PV is daytime-only: needs storage or 25-30% capacity factor on contactor capex)")
print("  -> the panel's saving is at most ~$50-120/t of energy; its value rests on panel+sorbent capex being below")
print("     a conventional contactor's capital charge at the same output.")

# ---------------------------------------------------------------- 7. scale and resources
print("\n7. SCALE AND RESOURCES (per Gt CO2/yr)")
GLASS_KG_M2, METAL_KG_M2 = 10.0, 12.0        # 4 mm cover glass; Al/steel frame, absorber, louvres [eng]
WORLD_FLAT_GLASS_MT = 80.0                    # ~70-90 Mt/yr flat glass [lit, approximate]
WORLD_SOLAR_THERMAL_NEW_MM2 = 30.0            # ~25-35 million m2/yr new glazed collectors, mostly China [lit, IEA SHC, approximate]
for (name, case) in (("amine/silica", "base"), ("K2CO3/carbon", "base"), ("amine/silica", "low"), ("K2CO3/carbon", "low")):
    c = COST[(name, case)]
    m2_gt = c["m2"] * 1e9
    land_km2 = m2_gt * {"low": 2.0, "base": 2.2, "high": 2.5}[case] / 1e6
    print(f"  {name:13s} {case:4s}: aperture {m2_gt/1e9:.1f} bn m2 = {m2_gt/1e6/WORLD_SOLAR_THERMAL_NEW_MM2:,.0f} yr of today's "
          f"solar-thermal output; land {land_km2:,.0f} km2; glass {m2_gt*GLASS_KG_M2/1e9:.0f} Mt "
          f"({m2_gt*GLASS_KG_M2/1e9/WORLD_FLAT_GLASS_MT:.1f} yr of world flat glass); metal {m2_gt*METAL_KG_M2/1e9:.0f} Mt; "
          f"sorbent inventory {c['sorb']*1e9/1e9:.0f} Mt")
print("  reference: amine-functional resin output is ~O(0.1-1) Mt/yr; K2CO3 ~2 Mt/yr; activated carbon ~3 Mt/yr [lit, approximate]")
print("  water: net PRODUCER (night air co-adsorbs water; condensate recycled); electricity per Gt/yr from section 4")
