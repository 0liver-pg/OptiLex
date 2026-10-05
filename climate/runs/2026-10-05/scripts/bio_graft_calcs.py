"""Bio-graft generator: sanity calculations for six single-graft ideas.

All inputs that are assumptions are labelled ASSUME. Run from the OptiLex repo root:
  .venv/bin/python <this file>
"""
import math
import sys

sys.path.insert(0, 'climate')
from physics import *  # noqa: F401,F403

T0K = 298.15


def carnot(T_c):
    return 1 - T0K / (T_c + 273.15)


def hp_cop(T_source_c, T_sink_c, carnot_fraction=0.5):
    Th = T_sink_c + 273.15
    return carnot_fraction * Th / (T_sink_c - T_source_c)


def comp_floor_gj(p_from_bar, p_to_bar):
    return gj_per_tonne(R * T0 * math.log(p_to_bar / p_from_bar))


def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


print("=" * 78)
print("IDEA 1  CA-promoted K2CO3, ~75 C vacuum regeneration, cement kiln (Brevik-type)")
print("=" * 78)
sep90 = gj_per_tonne(min_separation_work(0.25, 0.90))
sep95 = gj_per_tonne(min_separation_work(0.25, 0.95))
c_atm = comp_floor_gj(1.0, 150)
c_vac = comp_floor_gj(0.3, 150)
print(f"Separation floor 25% CO2: 90% {sep90:.3f} GJ/t, 95% {sep95:.3f} GJ/t")
print(f"Compression floor 1->150 bar {c_atm:.3f}; 0.3->150 bar (vacuum stripper) {c_vac:.3f} GJ/t "
      f"(+{c_vac - c_atm:.3f})")
for label, Q, Tr in [("amine, 2.7 GJ/t at 125 C", 2.7, 125), ("amine, 3.2 GJ/t at 125 C", 3.2, 125),
                     ("CA-K2CO3, 2.5 GJ/t at 75 C (ASSUME)", 2.5, 75),
                     ("CA-K2CO3, 3.5 GJ/t at 75 C (ASSUME)", 3.5, 75)]:
    ex = Q * carnot(Tr)
    print(f"  {label:<38} heat exergy {ex:.2f} GJ/t; 2nd-law eff (sep+comp floor / exergy+0.4 GJe comp) "
          f"{(sep90 + c_atm) / (ex + 0.4):.0%}")
# heat pumps from 45 C low-grade sources (flue condensate, absorber intercool, CO2 compressor intercool)
cop_low = hp_cop(45, 80)
cop_high = hp_cop(45, 130)
print(f"Heat pump COP (50% of Carnot) 45->80 C: {cop_low:.2f}; 45->130 C: {cop_high:.2f}")
for Q in (2.5, 3.0, 3.5):
    e_low = Q / cop_low
    e_high = Q / cop_high
    print(f"  Q={Q} GJ/t all by HP: low-T {e_low:.2f} GJe/t ({e_low/0.0036:.0f} kWh/t, "
          f"${energy_cost_floor(e_low, 60):.0f}/t @ $60/MWh) vs high-T {e_high:.2f} GJe/t "
          f"({e_high/0.0036:.0f} kWh/t, ${energy_cost_floor(e_high, 60):.0f}/t); "
          f"e-boiler {Q/0.0036:.0f} kWh/t ${energy_cost_floor(Q, 60):.0f}/t")
gas_boiler_co2 = 3.0 / 0.9 * 0.0561
print(f"Gas boiler alternative for 3 GJ/t: {gas_boiler_co2:.2f} t CO2 emitted per t captured "
      f"(fuel ~${3.0/0.9*10:.0f}/t at $10/GJ)")
# Per tonne clinker heat inventory (ASSUME 0.85 t CO2/t clinker)
co2_per_clinker = 0.85
waste_hi = 0.5 * co2_per_clinker * 2.7  # calibrated: Brevik covers ~50% at amine 2.7 GJ/t
print(f"Implied >130 C waste heat (calibrated to Brevik 50% at 2.7 GJ/t): {waste_hi:.2f} GJ/t clinker")
for shell, deep in [(0.15 * 0.5, 0.15), (0.4 * 0.5, 0.25)]:
    for Q in (2.5, 3.0, 3.5):
        avail = waste_hi + shell + deep
        frac = min(avail / (co2_per_clinker * Q), 1)
        need90 = co2_per_clinker * 0.9 * Q
        short = max(need90 - avail, 0)
        print(f"  shell {shell:.2f} + deep-cooling {deep:.2f} GJ/t clk, Q {Q}: capture from free heat {frac:.0%}; "
              f"shortfall to 90% {short:.2f} GJ/t clk -> HP {short/cop_low/0.0036:.0f} kWh/t clk")
# Enzyme make-up cost vs half-life
cap_tph = 0.9 * 0.8e6 / 8000  # t CO2/h for 0.8 Mt/yr kiln at 90%
for inv_m3, dose in [(2000, 0.2), (3400, 1.0)]:
    inv_kg = inv_m3 * dose  # g/L == kg/m3
    for half in (7, 30, 90):
        kg_yr = inv_kg * math.log(2) / half * 365
        for price in (20, 200):
            print(f"  enzyme inventory {inv_kg:,.0f} kg, t1/2 {half:>2} d, ${price}/kg: "
                  f"{kg_yr/1e3:,.1f} t/yr -> ${kg_yr*price/(cap_tph*8000):.2f}/t CO2")

print()
print("=" * 78)
print("IDEA 2  Methanotroph biofilter on sub-autothermal ventilation air methane")
print("=" * 78)
kH_CH4 = 1.4e-3  # mol/(L atm) at 25 C
for ppm in (1.93, 10, 1000, 2000, 3000, 5000):
    c_aq = ppm * 1e-6 * kH_CH4 * 1e6  # uM
    print(f"  {ppm:>6} ppm CH4 -> dissolved {c_aq:.4g} uM  (low-affinity pMMO Km ~1-10 uM ASSUME; "
          f"high-affinity ~0.01-0.1 uM)")
# autothermal threshold of RTO
dT_per_01pct = 0.001 * 802e3 / 29.1
for eff in (0.95, 0.97):
    xmin = (1 - eff) * (1000 - 25) / dT_per_01pct * 0.1
    print(f"  RTO autothermal threshold at {eff:.0%} regenerator, 1000 C bed: {xmin:.2f}% CH4 "
          f"(adiabatic rise {dT_per_01pct:.1f} K per 0.1% CH4)")
x = 0.001
need = (1 - 0.95) * 975 - dT_per_01pct
print(f"  At 0.10% CH4 an RTO needs +{need:.0f} K of supplementary fuel = "
      f"{need/dT_per_01pct:.0%} extra CH4-equivalent burned per CH4 destroyed")
# Bed sizing for a 300 m3/s shaft
Q = 300.0  # m3/s
rho_ch4 = P0 * M_CH4 / (R * T0)  # kg/m3 pure CH4 at 25 C
print(f"  CH4 density {rho_ch4:.3f} kg/m3")
for conc in (0.001, 0.002, 0.003):
    load_kgph = Q * conc * rho_ch4 * 3600
    for EC05 in (5, 15):  # g/m3/h at 0.5% (lit range 3-20 at low conc; ASSUME first-order below 0.5%)
        EC = EC05 * conc / 0.005
        RE = 0.5
        V = load_kgph * RE * 1000 / EC
        ebrt = V / Q
        area_ha = V / 1.5 / 1e4
        t_yr = load_kgph * RE * 8000 / 1000
        for capex_m3 in (100, 400):
            capex = V * capex_m3
            ann = capex * crf(0.10, 15) + 0.04 * capex  # 4%/yr O&M incl. media replacement (ASSUME)
            fan_kw = Q * 400 / 0.6 / 1000
            fan_cost = fan_kw * 8000 * 0.08  # $80/MWh
            per_tch4 = (ann + fan_cost) / t_yr
            net_co2e = GWP100['CH4_fossil'] - 44.01 / 16.04
            print(f"   {conc:.1%} EC@0.5%={EC05:>2} -> EC {EC:4.1f} g/m3/h, bed {V:>9,.0f} m3 ({area_ha:4.1f} ha @1.5 m), "
                  f"EBRT {ebrt:4.0f} s, {t_yr:5.0f} t CH4/yr, capex ${capex/1e6:5.1f}M @${capex_m3}/m3 -> "
                  f"${per_tch4:5.0f}/t CH4 = ${per_tch4/net_co2e:4.1f}/t CO2e(net GWP100)")
fan = fan_work_gj_per_tonne(0.003, 0.5, 400, 0.6, molar_mass=M_CH4)
print(f"  Verifier fan work, 0.3% CH4, 50% removal, 400 Pa: {fan:.2f} GJ/t CH4 = "
      f"{fan/GWP100['CH4_fossil']:.3f} GJ/t CO2e")
fan_amb = fan_work_gj_per_tonne(1.93e-6, 0.5, 400, 0.6, molar_mass=M_CH4)
print(f"  Same bed on ambient air (1.93 ppm): {fan_amb:,.0f} GJ/t CH4 = {fan_amb/GWP100['CH4_fossil']:.1f} GJ/t CO2e")
# ambient bed volume per t CO2e if first-order kinetics continue down to 1.93 ppm
EC_amb = 15 * 1.93e-6 / 0.005
V_per_t = 1e6 / (EC_amb * 8760 * 0.5)
print(f"  First-order extrapolation to 1.93 ppm: EC {EC_amb:.4f} g/m3/h -> {V_per_t:,.0f} m3 bed per t CH4/yr "
      f"= {V_per_t/GWP100['CH4_fossil']:,.0f} m3 per t CO2e/yr")
matec = 9.52e6 * crf(0.10, 15) + 0.87e6
print(f"  MATEC RTO reference (0.326%, 360,000 m3/h): EUR {matec/7236:.0f}/t CH4 = "
      f"EUR {matec/7236/GWP100['CH4_fossil']:.1f}/t CO2e (GWP100, gross)")

print()
print("=" * 78)
print("IDEA 3  N2O-respiring (NosZ) bacteria grown in livestock slurry/digestate before spreading")
print("=" * 78)
for N, EF in [(150, 0.005), (150, 0.01), (150, 0.016)]:
    n2o = N * EF * 44.013 / 28.013
    co2e = n2o * GWP100['N2O'] / 1000
    for cut in (0.3, 0.6):
        saved = co2e * cut
        print(f"  {N} kg N/ha, EF {EF:.1%}: {n2o:.2f} kg N2O = {co2e:.2f} t CO2e/ha/yr; {cut:.0%} cut -> "
              f"{saved:.2f} t; at $10-30/ha => ${10/saved:.0f}-{30/saved:.0f}/t CO2e")
N_applied = 110 + 30  # Mt N synthetic + manure applied (ASSUME, FAO order of magnitude)
for EF in (0.008, 0.012):
    gt = N_applied * EF * 44.013 / 28.013 * GWP100['N2O'] / 1000
    print(f"  Global direct soil N2O at EF {EF:.1%}: {gt:.2f} Gt CO2e/yr")
    for share_denit, adopt, cut in [(0.5, 0.2, 0.3), (0.6, 0.4, 0.5)]:
        print(f"    denitrification-dominated share {share_denit:.0%} x adoption {adopt:.0%} x cut {cut:.0%} "
              f"= {gt*share_denit*adopt*cut*1000:.0f} Mt CO2e/yr")

print()
print("=" * 78)
print("IDEA 4  Sulfate-reducer competitive exclusion (gypsum) recharged by AWD drying cycles, rice")
print("=" * 78)
M_gyp = 172.17
for emit in (100, 250):  # kg CH4/ha/season emitted under continuous flooding (ASSUME, IPCC EF ~1.19 kg/ha/d x ~113 d)
    for emitted_share in (0.3, 0.6):
        produced_kmol = emit / emitted_share / 16.04
        for divert in (0.2, 0.4):
            so4_kmol = produced_kmol * divert
            gyp_t = so4_kmol * M_gyp / 1000
            saved = emit * divert * GWP100['CH4_biogenic'] / 1000
            print(f"  emit {emit} kg/ha, emitted/produced {emitted_share:.0%}, divert {divert:.0%}: "
                  f"gypsum {gyp_t:.1f} t/ha/season with no recycling; {gyp_t/3:.1f} t/ha if AWD reoxidation recycles "
                  f"sulfate 3x; saves {saved:.2f} t CO2e/ha")
for gyp, price in [(0.7, 15), (2.0, 40)]:
    print(f"  {gyp} t/ha gypsum at ${price}/t + $10/ha spreading = ${gyp*price+10:.0f}/ha")
rice_ch4 = 30.0  # Mt CH4/yr (ASSUME, Global Methane Budget order of magnitude)
gt_rice = rice_ch4 * GWP100['CH4_biogenic'] / 1000
print(f"  Rice CH4 {rice_ch4} Mt = {gt_rice:.2f} Gt CO2e (GWP100) / {rice_ch4*GWP20['CH4_biogenic']/1000:.2f} (GWP20)")
for adopt, extra_cut in [(0.1, 0.1), (0.3, 0.25)]:
    print(f"  adoption {adopt:.0%} x extra cut over AWD {extra_cut:.0%} = {gt_rice*adopt*extra_cut*1000:.0f} Mt CO2e/yr")

print()
print("=" * 78)
print("IDEA 5  CAM-style time-shifted regeneration for a cycling NGCC with amine capture")
print("=" * 78)
sep = gj_per_tonne(min_separation_work(0.04, 0.90))
print(f"Floor 4% CO2 90%: {sep:.3f} GJ/t + compression {c_atm:.3f} = {sep + c_atm:.3f} GJ/t")
for label, e in [("steam extraction (BD3-like 1.33 GJe/t)", 1.33),
                 ("e-boiler 3.0 GJ_th + 0.4 GJe comp", 3.4),
                 ("HP COP 2.37 + 0.4 comp", 3.0 / cop_high + 0.4)]:
    print(f"  {label:<40} 2nd-law {(sep + c_atm)/e:.0%}")
G = 270.0  # t/h at full load (NZT-like 742 MW, ~2 Mt/yr at 85% CF)
block_h = 10.0
f = 0.40
stored_t = G * block_h
kmol = stored_t * 1e3 / 44.01
for cyc in (0.8, 1.2):  # mol CO2 per kg solvent cyclic (ASSUME: PZ ~0.8, MEA ~1.0-1.2)
    solvent_t = kmol / cyc
    for amine_price, tank_m3 in [(1.5, 150), (2.5, 300)]:
        tanks = 2 * solvent_t * tank_m3  # lean + rich, ~1 t/m3
        inv = solvent_t * 0.3 * amine_price * 1e3
        print(f"  cyclic {cyc} mol/kg: {solvent_t:,.0f} t solvent per tank; tanks ${tanks/1e6:.0f}M + amine "
              f"${inv/1e6:.0f}M = ${(tanks+inv)/1e6:.0f}M")
annual = G * 8760 * f
capture_capex = 628e6  # $ (NETL H-class: +$966/kW x ~650 MW net), 2018$
for r in (0.45, 0.6):
    regen = capture_capex * r
    avg_rate = G * block_h / 24
    ratio = (avg_rate / G) ** 0.65
    saving = regen * (1 - ratio)
    eboiler = avg_rate * 3.0 / 3.6 * 1000 * 150  # kWth * $150/kWth
    for storage in (46e6, 82e6):
        net = saving - eboiler - storage
        print(f"  regen share {r:.0%}: regen sized {avg_rate/G:.0%} of peak -> capex x{ratio:.2f}, saves "
              f"${saving/1e6:.0f}M; e-boiler ${eboiler/1e6:.0f}M; storage ${storage/1e6:.0f}M; net "
              f"${net/1e6:+.0f}M -> ${net*crf(0.08,25)/annual:+.1f}/t ({annual/1e3:,.0f} kt/yr)")
for peak, off in [(80, 30), (150, 20)]:
    base = 0.37 * peak  # MWh/t lost output at peak (BD3 derate 0.37 MWh/t)
    cam = 3.0 / 3.6 * off + 0.11 * off  # e-boiler heat + compression at off-peak
    print(f"  energy: steam extraction at ${peak}/MWh = ${base:.0f}/t vs e-boiler at ${off}/MWh = ${cam:.0f}/t "
          f"-> saves ${base-cam:.0f}/t")

print()
print("=" * 78)
print("IDEA 6  PSII-D1-style repair: wash out and reload the amine phase of solid DAC sorbent in place")
print("=" * 78)
dac = gj_per_tonne(min_separation_work(420e-6, 0.75))
print(f"DAC floor {dac:.3f} GJ/t")
for q, cyc, L in [(1.0, 3, 1.0), (1.5, 6, 2.0)]:
    kg_co2_per_kg = q * cyc * 365 * L * 0.04401
    for C in (20, 50):
        base = C / kg_co2_per_kg * 1000
        for a, N, p in [(0.2, 5, 0.1), (0.3, 10, 0.15)]:
            factor = a + (1 - a) / N + p
            print(f"  q {q} mol/kg, {cyc} cyc/d, life {L} yr -> {kg_co2_per_kg:.0f} kg CO2/kg; ${C}/kg -> "
                  f"${base:.0f}/t; reload (amine share {a:.0%}, support reused {N}x, process {p:.0%}) "
                  f"-> ${base*factor:.0f}/t (saves ${base*(1-factor):.0f})")
        mt_per_gt = 1e9 / kg_co2_per_kg / 1e9 * 1e3  # Mt sorbent per Gt CO2
        print(f"    sorbent replacement {mt_per_gt:.1f} Mt/yr per Gt; amine (40 wt%) {0.4*mt_per_gt:.1f} Mt/yr")
# reload energy: evaporate 2 kg methanol per kg sorbent per reload
e_reload = 2 * 1.1e-3  # GJ per kg sorbent
for kg in (48, 289):
    print(f"  reload solvent-evaporation energy: {e_reload/kg*1000:.4f} GJ/t CO2 (if {kg} kg CO2 per kg per life)")
