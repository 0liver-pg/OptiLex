"""systems_5 verifier: enclosed degassing weir below tropical hydro dams + VAM-type RTO.

Checks the idea's quantitative claims against the OptiLex physics verifier and against
MEASURED site data (all primary sources, read this session):
  * Nam Theun 2 (Lao PDR; flooded 2008, commissioned Apr 2010): Deshmukh et al. 2016,
    Biogeosciences 13:1919 -- downstream emissions 10 Gg CH4/yr after commissioning -> 2 Gg CH4/yr
    4 yr after impoundment (2012); 80% within 2-4 months; peak-month degassing (2010):
    powerhouse 385, regulating dam 1240, aeration weir 756 Mg CH4/month; aeration weir degassing
    efficiency "up to 99%"; turbined-water CH4 at TRC1 117+-71 umol/L (WD 2010) falling to
    33 (2011) and 9.8 (2012) umol/L averages; inflow ~7527 Mm3/yr.
  * Petit Saut (French Guiana; flooded 1994): Abril et al. 2005, GBC, doi 10.1029/2005GB002457 --
    CH4 emissions 0.07 Mt C/yr (1994-96) -> 0.016 Mt C/yr since 2000; degassing at the aerating weir
    "reaching 70% of the total CH4 flux".
  * Balbina (Brazil; flooded 1987): Kemenes et al. 2007, GRL, doi 10.1029/2007GL029479 --
    downstream CH4 emission 39 Gg C/yr (measured degassing at turbine outflow + downstream diffusion).
Hydraulic data (head, mean flow) for the sites are approximate engineering values from memory and
are labelled ASSUMED below; they only change the energy penalty, not the methane quantities.
"""
import math
import sys

sys.path.insert(0, 'climate')
from physics import *  # noqa: F401,F403

SEC_YR = 3.1536e7
RHO_CH4 = M_CH4 * P0 / (R * 301.0)          # kg/m3 CH4 gas at 28 C, 1 atm
GWP = GWP100['CH4_biogenic']                 # 27.0 (IPCC AR6), verifier constant
GWP_20 = GWP20['CH4_biogenic']               # 79.7


def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def kt_ch4_from_gg_c(gg_c):
    return gg_c * 16.04 / 12.011


print("=" * 100)
print("1. THERMODYNAMIC FLOOR (separation step)")
# Henry's law: Sander (2015) compilation Hcp(CH4) ~1.4e-5 mol m-3 Pa-1 at 298 K, d lnH/d(1/T) ~1600 K
T = 301.0
Hcp = 1.4e-5 * math.exp(1600 * (1 / T - 1 / 298.15))
Hcc = 1 / (Hcp * R * T)                      # dimensionless gas/liquid concentration ratio
print(f"Henry Hcc(CH4, 28 C) = {Hcc:.1f} (idea assumed ~30: OK)")
for c_mgL in (0.5, 2.0, 16.0):
    c_mol_m3 = c_mgL / 1000 / M_CH4          # mg/L = g/m3 -> mol/m3
    p_eq = c_mol_m3 / Hcp                    # Pa, partial pressure in equilibrium with the water
    y_eq = p_eq / P0
    dG_out = R * T * math.log(y_eq / 0.01)   # J/mol released moving CH4 from water to a 1% sweep
    print(f"  {c_mgL:>5} mg/L dissolved -> equilibrium gas-phase CH4 {y_eq:.1%} "
          f"(supersaturation vs 1.9 ppm air: {y_eq/1.93e-6:,.0f}x); "
          f"stripping into a 1% sweep RELEASES {dG_out/1e3:.1f} kJ/mol")
print("  -> Separation floor = 0 GJ/t (desorption is spontaneous; the water is supersaturated). "
      "Oxidation is exothermic (-802 kJ/mol). No thermodynamic floor is violated;")
print("     the energy cost is hydraulic (head lost / fan work), not separation work.")
print(f"  Safety flag: equilibrium headspace over 2 mg/L water is ~9% CH4 (inside the 5-15% flammable "
      f"range); over 16 mg/L (NT2 hypolimnion peak, 1000 umol/L) it is far above the UEL. Enclosure needs "
      f"forced sweep + LEL interlocks, as in coal-mine VAM practice.")

print("\n" + "=" * 100)
print("2. STRIPPING: finite enclosed air vs an open weir")
print("Open weir: air is effectively unlimited (NT2 measured up to 99% degassing at the weir).")
print("Enclosed weir: finite sweep G/L, stripping factor S = Hcc*G/L. Kremser, counter-current, n ideal stages:")
for S in (2, 4, 7):
    row = []
    for n in (1, 2, 3):
        f = (S ** (n + 1) - S) / (S ** (n + 1) - 1)
        row.append(f"n={n}: {f:.0%}")
    cocur = S / (1 + S)
    print(f"  S={S}: co-current single stage max {cocur:.0%}; counter-current " + ", ".join(row))
print("  -> 75% at S=4 needs ~1 ideal stage; a 2-3 step counter-current cascade gives margin. Idea's 75% is OK.")

print("\n" + "=" * 100)
print("3. SWEEP CONCENTRATION and RTO LIMITS")
# VAM RTO operating window: autothermal >= ~0.2% CH4; upper ~1.0-1.2% (overheating / 25% LEL = 1.25%)
Y_MAX = 0.010
for c_mgL, q in [(0.5, 1000), (2.0, 1000), (5.0, 1000)]:
    ch4_kg_s = q * c_mgL / 1000 * 0.75
    G4 = 4 / Hcc * q
    y4 = ch4_kg_s / RHO_CH4 / G4
    G_needed = max(G4, ch4_kg_s / RHO_CH4 / Y_MAX)
    print(f"  {c_mgL} mg/L, {q} m3/s: at S=4 sweep {G4:.0f} m3/s carries {y4:.2%} CH4; "
          f"to stay <= {Y_MAX:.0%} needs {G_needed:.0f} m3/s air (S={Hcc*G_needed/q:.1f})")
print("  -> idea's 1.7% at 2 mg/L is ABOVE the ~1-1.2% VAM-RTO ceiling and 25% LEL (1.25%): needs ~1.7x more")
print("     air/RTO capacity than claimed (which also raises stripping). 0.4-1% is the usable window.")

print("\n" + "=" * 100)
print("4. MEASURED SITE CAPTURABLE METHANE (the cost driver)")
nt2_peak_weir_share = 756 / (385 + 1240 + 756)
sites = {
    # name: (capturable kt CH4/yr low, base, high, notes, head_m, mean_flow_m3s, operating months)
    "Idea's generic case (1000 m3/s, 2 mg/L, all year)": (47.3, 47.3, 47.3, "idea claim, not a site", 100, 1000, 12),
    "Nam Theun 2 (2012 level, enclosing aeration weir only)":
        (2.0 * 0.2, 2.0 * nt2_peak_weir_share, 2.0 * 0.6,
         f"downstream 2 Gg/yr (2012, measured); weir share {nt2_peak_weir_share:.0%} of 2010 peak-month degassing", 350, 240, 4),
    "Nam Theun 2 (2010 commissioning year, all 3 sites enclosed)": (10 * 0.5, 10 * 0.7, 10 * 0.9,
         "10 Gg/yr (2010, measured); one-off early-years pulse", 350, 240, 5),
    "Petit Saut (weir = 70% of CH4 flux, post-2000)":
        (kt_ch4_from_gg_c(16) * 0.7 * 0.3, kt_ch4_from_gg_c(16) * 0.7 * 0.5, kt_ch4_from_gg_c(16) * 0.7 * 0.75,
         "0.016 Mt C/yr since 2000 (measured); x0.3-0.75 for decline to 2026 and 75% recovery (assumed)", 32, 260, 8),
    "Balbina (downstream 39 Gg C/yr, 2004-06)":
        (kt_ch4_from_gg_c(39) * 0.3, kt_ch4_from_gg_c(39) * 0.5, kt_ch4_from_gg_c(39) * 0.7,
         "52 kt CH4/yr measured incl. river diffusion; capturable 30-70% (assumed: turbine-outflow degassing upstream of any weir)", 22, 600, 10),
}
for k, v in sites.items():
    lo, base, hi, note, *_ = v
    print(f"  {k}: capturable {lo:.1f} / {base:.1f} / {hi:.1f} kt CH4/yr = "
          f"{base*GWP/1e3:.3f} Mt CO2e (GWP100 base) -- {note}")

print("\n" + "=" * 100)
print("5. ENERGY per t CO2e (head lost + fans) and COST per t CO2e (low/base/high)")
FAN_EFF = 0.7
DP = {"low": 2000, "base": 3000, "high": 5000}           # Pa: RTO beds + ducting + enclosure (VAM RTO ~2-5 kPa)
HEAD = {"low": 0.0, "base": 1.0, "high": 4.0}             # m incremental head: retrofit of existing weir -> 0-1 m; new weir 2-4 m
ELEC = {"low": 40, "base": 60, "high": 90}                # $/MWh value of lost hydro / bought power
RTO_CAPEX = {"low": 70e3, "base": 105e3, "high": 200e3}   # $ per m3/s installed (MATEC EUR9.5M/100 m3/s ~ $103k; tropical/escalation high)
ENCL = {"low": 10e6, "base": 30e6, "high": 60e6}          # $ per 1000 m3/s of water, scaled ^0.7 (ASSUMED: no costed design exists)
OM_FRAC = {"low": 0.03, "base": 0.04, "high": 0.06}       # O&M as share of capex per year
MRV = {"low": 0.3e6, "base": 0.5e6, "high": 1.0e6}        # $/yr monitoring + verification
WACC, LIFE = 0.08, 20


def evaluate(capt_kt, head_m, flow, months, case, c_scale=1.0):
    """capt_kt: kt CH4/yr captured. Returns (GJ/t CO2e, $/t CO2e, details)."""
    hrs = months / 12 * 8760
    ch4_kg_s_op = capt_kt * 1e6 / (hrs * 3600)                 # kg/s while operating
    G = max(4 / Hcc * flow, ch4_kg_s_op / RHO_CH4 / Y_MAX)      # m3/s sweep (>= S=4, <= 1% CH4)
    fan_mw = G * DP[case] / FAN_EFF / 1e6
    head_mw = flow * 1000 * 9.81 * HEAD[case] * 0.9 / 1e6
    mwh = (fan_mw + head_mw) * hrs
    t_co2e = capt_kt * 1e3 * GWP
    gj_t = mwh * 3.6 / t_co2e
    capex = G * RTO_CAPEX[case] + ENCL[case] * (flow / 1000) ** 0.7
    ann = capex * crf(WACC, LIFE) + capex * OM_FRAC[case] + MRV[case] + mwh * ELEC[case]
    return gj_t, ann / t_co2e, dict(G=G, fan_mw=fan_mw, head_mw=head_mw, capex=capex,
                                     head_share=HEAD[case] / head_m)


summary = {}
for name, (lo, base, hi, note, head_m, flow, months) in sites.items():
    print(f"\n  {name} (head ~{head_m} m ASSUMED, mean flow ~{flow} m3/s ASSUMED, {months} operating months)")
    # pair optimistic tonnes with optimistic costs and vice versa
    for case, capt in (("low", hi), ("base", base), ("high", lo)):
        gj, usd, d = evaluate(capt, head_m, flow, months, case)
        summary.setdefault(name, {})[case] = (gj, usd)
        print(f"    {case:>4}: {capt:6.1f} kt CH4/yr; sweep {d['G']:.0f} m3/s; fans {d['fan_mw']:.2f} MW; "
              f"head loss {d['head_mw']:.1f} MW ({d['head_share']:.1%} of plant head); capex ${d['capex']/1e6:.0f}M "
              f"-> {gj:.3f} GJ/t CO2e, ${usd:,.0f}/t CO2e (GWP100); ${usd*GWP/GWP_20:,.0f}/t CO2e (GWP20)")

print("\n  Idea claims vs this check:")
gj, usd, d = evaluate(47.3, 100, 1000, 12, "base")
print(f"   generic all-year case, base: {gj:.3f} GJ/t, ${usd:.1f}/t (idea: 0.44-0.88 GJ/t energy, $3.5/t capex "
      f"+ $6-12/t energy; its head loss of 2-4 m is the dominant term only for NEW weirs)")
for hm in (2, 4):
    mw = 1000 * 1000 * 9.81 * hm * 0.9 / 1e6
    print(f"   head {hm} m at 1000 m3/s: {mw:.1f} MW lost -> {mw*SEC_YR/1e3/(47.3e3*GWP):.2f} GJ/t CO2e "
          f"(idea 18-35 MW, 0.44-0.88 GJ/t: arithmetic reproduced)")
print("   Output-loss claim '0.5-3%': 2-4 m is 0.6-1.1% at NT2 (~350 m head) but 6-13% at Petit Saut (~32 m) "
      "and 9-18% at Balbina (~22 m) -> holds only for high-head plants.")

print("\n" + "=" * 100)
print("6. SCALE and RESOURCES")
# Bottom-up: number of dams with turbined water >~0.5 mg/L for months, x capturable kt
for label, n_dams, kt_each in (("low", 15, 3), ("base", 40, 8), ("high", 100, 15)):
    kt = n_dams * kt_each
    print(f"  {label}: {n_dams} suitable tropical dams x {kt_each} kt CH4/yr = {kt/1e3:.2f} Tg CH4/yr = "
          f"{kt*GWP/1e6:.3f} Gt CO2e/yr (GWP100), {kt*GWP_20/1e6:.3f} Gt CO2e/yr (GWP20)")
print("  Cross-check (top-down): G-res (Harrison et al. 2021) finds degassing is a major CH4 pathway in tropical")
print("  reservoirs; global reservoir CH4 is ~10-18 Tg/yr across studies (MODELLED, not verified this session).")
print("  Even capturing 5-10% of that (0.5-1.8 Tg CH4) is", f"{0.5*GWP/1e3:.3f}-{1.8*GWP/1e3:.3f} Gt CO2e/yr (GWP100).")
print(f"  Share of total GHG ({TOTAL_GHG_GT_CO2E} Gt CO2e): base {40*8*GWP/1e6/TOTAL_GHG_GT_CO2E:.3%}")
s = ScaleCheck(40 * 8 * GWP / 1e6, summary["Petit Saut (weir = 70% of CH4 flux, post-2000)"]["base"][0])
print(f"  Energy at base scale: {s.ej_per_year*1e3:.2f} PJ/yr = {s.share_of_world_primary_energy:.5%} of world primary energy")
print("  Materials: steel/concrete enclosure + RTO ceramic beds per dam; land ~1-3 ha at existing dam sites; "
      "water: none consumed (water passes through, oxygenation preserved).")
print("  Additionality caveat: for a NEW weir, the CH4 it strips would partly have been oxidised in the river "
      "(NT2: river CH4 fell to background within 30 km); net avoided emission < captured.")
