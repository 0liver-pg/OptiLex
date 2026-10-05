"""Global South & land generator: energy/scale checks for 6 ideas, using the OptiLex verifier.

All assumptions are labelled ASSUME; sourced inputs labelled SRC. Run:
cd . && .venv/bin/python <this file>
"""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

G = 9.81
C_TO_CO2 = 44.01 / 12.011
GWP_CH4_BIO_100, GWP_CH4_BIO_20 = GWP100['CH4_biogenic'], GWP20['CH4_biogenic']
DAC_FLOOR = gj_per_tonne(min_separation_work(420e-6, 0.75))

def hdr(s):
    print('\n' + '=' * 78 + '\n' + s + '\n' + '=' * 78)

def dac_equiv(gt, label):
    for gj in (DAC_FLOOR, 6.0, 10.0):
        s = ScaleCheck(gt, gj)
        print(f"   DAC-equivalent for {label} ({gt*1e3:.0f} Mt/yr) at {gj:.2f} GJ/t: {s.ej_per_year:.3f} EJ/yr "
              f"= {s.share_of_world_primary_energy:.3%} of world primary")

# ---------------------------------------------------------------- 1. AWD with volumetric pump pricing
hdr('1. AWD rice + prepaid volumetric irrigation')
season_days = (100, 120)                         # ASSUME dry-season (boro) flooded period
ef_base = {'South Asia': 0.85, 'SE Asia': 1.22}   # SRC (recalled) IPCC 2019 refinement kg CH4/ha/day, verify
sf_multi = 0.55                                  # SRC (recalled) IPCC 2019 scaling factor, multiple drainage
for reg, ef in ef_base.items():
    for d in season_days:
        base = ef * d
        cut = base * (1 - sf_multi)
        print(f" {reg}, {d} d: baseline {base:.0f} kg CH4/ha, AWD cut {cut:.0f} kg CH4/ha = "
              f"{cut*GWP_CH4_BIO_100/1e3:.2f} t CO2e/ha (GWP100) / {cut*GWP_CH4_BIO_20/1e3:.2f} (GWP20)")
# pumping energy saved
for lift_m, eta, label in [(8, 0.12, 'shallow tubewell, small diesel set (fuel->water 12%)'),
                           (25, 0.30, 'deep tubewell, electric (wire->water 30%)')]:
    for saved_mm in (200, 400):
        v = saved_mm / 1000 * 1e4           # m3/ha
        e_hyd = 1000 * G * lift_m * v      # J
        e_in = e_hyd / eta
        kwh = e_in / 3.6e6
        if 'diesel' in label:
            litres = e_in / 36e6           # 36 MJ/L diesel LHV
            co2 = litres * 2.68
            print(f" {label}, lift {lift_m} m, save {saved_mm} mm ({v:,.0f} m3/ha): {e_in/1e9:.2f} GJ fuel/ha "
                  f"= {litres:.0f} L diesel = {co2/1e3:.2f} t CO2/ha")
        else:
            co2 = kwh * 0.65               # ASSUME South Asian grid 0.65 kg/kWh
            print(f" {label}, lift {lift_m} m, save {saved_mm} mm: {kwh:,.0f} kWh/ha = {co2/1e3:.2f} t CO2/ha")
# verifier contrast: removing the same CH4 from ambient air
fan_ch4 = fan_work_gj_per_tonne(1.93e-6, 0.5, 100, molar_mass=M_CH4)
print(f" Verifier: removing 1 t CH4 from ambient air costs {fan_ch4:,.0f} GJ in fan work alone; "
      f"AWD avoids it at source and SAVES pumping energy (negative GJ/t).")
cut_t = 0.85 * 110 * (1 - sf_multi) / 1000  # t CH4/ha, South Asia mid
print(f" -> fan work to remove one hectare-season's avoided CH4 ({cut_t*1000:.0f} kg) from air: {fan_ch4*cut_t:.1f} GJ")
area_mha = (5, 15)                            # ASSUME adoption on 5-15 Mha of dry-season irrigated rice
for a in area_mha:
    for tco2e in (1.0, 2.0):
        print(f" scale: {a} Mha x {tco2e} t CO2e/ha/season = {a*tco2e:.0f} Mt CO2e/yr (one dry season)")

# ---------------------------------------------------------------- 2. Rice-husk char at parboiling mills
hdr('2. Rice-mill husk -> steam + biochar')
paddy_mt = 776.0       # SRC (recalled) FAOSTAT world paddy ~2022, verify
husk_frac = 0.20       # ASSUME husk = 20% of paddy mass
husk_mt = paddy_mt * husk_frac
husk_C, husk_LHV = 0.38, 13.5           # ASSUME dry husk C mass fraction, MJ/kg
for y_char, c_char in [(0.35, 0.40), (0.38, 0.45), (0.42, 0.50)]:
    c_ret = y_char * c_char / husk_C
    co2_t = y_char * c_char * C_TO_CO2
    char_lhv = c_char * 32.8 + 0.0       # MJ/kg char, carbon-dominated, ash inert (approximation)
    e_char = y_char * char_lhv
    pyro_heat = 0.8                      # ASSUME MJ/kg husk heat of pyrolysis + drying
    e_vol = husk_LHV - e_char - pyro_heat
    print(f" char yield {y_char:.0%}, char C {c_char:.0%}: C retained {c_ret:.0%}, {co2_t:.2f} t CO2/t husk (pre-permanence), "
          f"char holds {e_char:.1f} MJ/kg husk ({e_char/husk_LHV:.0%} of husk energy); volatiles left {e_vol:.1f} MJ/kg ({e_vol/husk_LHV:.0%})")
    for perm in (0.75, 0.9):
        print(f"     x permanence {perm}: {co2_t*perm:.2f} t CO2/t husk")
    # leakage if diverted husk energy displaced coal in a boiler
    leak = e_char / 1e3 * 94.6           # t CO2 per t husk (coal 94.6 kg CO2/GJ, IPCC default)
    print(f"     leakage if the char's energy was previously burned instead of coal: {leak:.2f} t CO2/t husk "
          f"-> net {co2_t*0.8 - leak:+.2f} t CO2/t husk (permanence 0.8)")
# parboiling heat match
for steam_share in (0.40, 0.55, 0.70):   # ASSUME fraction of husk energy a parboiling mill burns for steam/drying
    vol_share = 0.53
    f = 1.0 if steam_share <= vol_share else (1 - steam_share) / (1 - vol_share)
    print(f" mill burning {steam_share:.0%} of its husk energy: can char {f:.0%} of husk with steam still met by pyrolysis gas")
for surplus in (0.2, 0.4):
    mt = husk_mt * surplus * 0.38 * 0.45 * C_TO_CO2 * 0.8
    print(f" scale: {surplus:.0%} of {husk_mt:.0f} Mt husk/yr is surplus (dumped/open-burned) -> {mt:.0f} Mt CO2/yr durable-ish")
print(f" revenue at $100-150/t CO2 x 0.50 t/t husk = ${0.5*100:.0f}-{0.5*150:.0f} per t husk")

# ---------------------------------------------------------------- 3. carbonate -> silicate liming swap
hdr('3. Liming swap: carbonate aglime -> silicate fines, with source-apportioned MRV')
ef_lime, ef_dolo = 0.12 * C_TO_CO2, 0.13 * C_TO_CO2     # SRC IPCC 2006 Tier 1 t CO2/t
print(f" IPCC Tier 1: limestone {ef_lime:.3f}, dolomite {ef_dolo:.3f} t CO2/t applied")
wm = 0.059 * C_TO_CO2                                    # SRC (recalled) West & McBride 2005 US net estimate
print(f" West & McBride-type net estimate: {wm:.3f} t CO2/t limestone ({wm/ef_lime:.0%} of Tier 1)")
for brazil_lime in (35, 50):                             # ASSUME Brazil agricultural lime use Mt/yr (recalled ~45-55)
    print(f" Brazil {brazil_lime} Mt lime/yr -> Tier-1 {brazil_lime*ef_lime:.0f} Mt CO2/yr; net-estimate {brazil_lime*wm:.0f} Mt")
# substitution logistics
for cce in (0.10, 0.30):                                 # ASSUME silicate CaCO3-equivalence (slow, multi-year)
    rock_per_t_lime = 1 / cce
    for km in (30, 100):
        truck = rock_per_t_lime * km * 0.1 / 1000        # t CO2 (0.1 kg/t-km map value)
        print(f" CCE {cce:.0%}, haul {km} km: {rock_per_t_lime:.0f} t rock per t lime replaced, truck {truck*1000:.0f} kg CO2 "
              f"vs {ef_lime*1000:.0f} kg (Tier1) / {wm*1000:.0f} kg (net) avoided")
# Bond grinding if fines are NOT pre-existing (verifier-style check)
def bond_kwh(wi, p80_um, f80_um=10_000):
    return 10 * wi * (1 / p80_um ** 0.5 - 1 / f80_um ** 0.5)
for p in (100, 50):
    print(f" Bond grinding (Wi 20) to P80 {p} um: {bond_kwh(20, p):.0f} kWh/t rock -> zero if quarry fines reused")
# silicate CDR at Illinois field rate applied per tonne
print(f" Silicate CDR at Illinois field rate ~0.05 t CO2/t rock; Larkin 2022 tropical andesite: not detectable (3.8 vs 3.7 t/ha)")

# ---------------------------------------------------------------- 4. dairy ration balancing + milk-MIR MRV
hdr('4. Co-op ration balancing with bulk-milk MIR verification')
for ch4_kg in (50, 70):                                  # ASSUME kg CH4/yr per lactating Indian cow/buffalo
    for cut in (0.15, 0.20):                             # SRC Garg 2013: CH4/kg milk -15-20%
        t = ch4_kg * cut * GWP_CH4_BIO_100 / 1000
        print(f" {ch4_kg} kg CH4/yr x {cut:.0%} = {t:.2f} t CO2e/animal/yr (intensity basis) -> ${t*15:.1f}-{t*30:.1f} at $15-30/t")
for animals_m in (10, 30):                               # ASSUME animals enrolled (millions)
    print(f" scale: {animals_m} M animals x 0.15-0.38 t = {animals_m*0.15:.1f}-{animals_m*0.38:.1f} Mt CO2e/yr")
mrv_cost_per_sample = (0.5, 1.5)                         # ASSUME $ per FTIR milk sample
for animals_per_society in (200, 500):
    c = [x * 365 / animals_per_society for x in mrv_cost_per_sample]
    print(f" bulk-milk MIR daily at society level ({animals_per_society} animals): ${c[0]:.2f}-{c[1]:.2f}/animal/yr")
print(f" per-cow monthly MIR: ${0.5*12:.0f}-{1.5*12:.0f}/animal/yr  (exceeds carbon value -> pooled design required)")

# ---------------------------------------------------------------- 5. retort kilns for charcoal
hdr('5. Retort/afterburner kilns for the charcoal trade')
charcoal_mt = 53.0                                        # SRC (recalled) FAOSTAT world charcoal, verify
for ef in (30, 60):                                       # g CH4/kg charcoal, traditional (IPCC 1996 default ~30; field higher)
    for cut in (0.35, 0.75):                              # SRC Ethiopia improved kilns 30-57%; ASSUME retort+afterburner 75%
        t100 = ef * cut * GWP_CH4_BIO_100 / 1000
        t20 = ef * cut * GWP_CH4_BIO_20 / 1000
        print(f" EF {ef} g/kg, cut {cut:.0%}: {t100:.2f} t CO2e/t charcoal (GWP100), {t20:.2f} (GWP20)")
for y0, y1 in [(0.24, 0.34), (0.24, 0.40)]:               # SRC Ethiopia: earth mound 24%, improved 34-42%
    wood_saved = 1 / y0 - 1 / y1
    for fnrb in (0.3, 0.6):
        co2 = wood_saved * 0.48 * C_TO_CO2 * fnrb
        print(f" yield {y0:.0%}->{y1:.0%}: wood saved {wood_saved:.2f} t/t charcoal ({wood_saved*y0:.0%} less wood); "
              f"fNRB {fnrb}: {co2:.2f} t CO2/t charcoal")
for share in (0.25, 0.5):
    lo = charcoal_mt * share * (30 * 0.35 * 27 / 1000)
    hi = charcoal_mt * share * (60 * 0.75 * 27 / 1000 + 1.39 * 0.48 * C_TO_CO2 * 0.3)
    print(f" scale: {share:.0%} of {charcoal_mt:.0f} Mt charcoal -> {lo:.0f}-{hi:.0f} Mt CO2e/yr (methane-only low, +wood high)")
# verifier: CH4 at the source vs in air
for x in (0.02, 0.05):                                    # ASSUME CH4 mole fraction in kiln smoke (dry)
    w = min_separation_work(x, 0.9, 0.99)
    print(f" verifier min separation work for CH4 at {x:.0%}: {gj_per_tonne(w, M_CH4):.2f} GJ/t CH4 "
          f"(vs {gj_per_tonne(min_separation_work(1.93e-6, 0.5, 0.99), M_CH4):.2f} from air); an afterburner needs no separation at all")
print(f" fan work to strip the same CH4 back out of ambient air: {fan_ch4:,.0f} GJ/t CH4 = "
      f"{fan_ch4/GWP_CH4_BIO_100:.1f} GJ/t CO2e (GWP100)")

# ---------------------------------------------------------------- 6. plantation peat rewetting with InSAR MRV
hdr('6. Rewetting drained plantation peat, paid per InSAR-measured subsidence arrested')
for sub_cm, ox, bd, c in [(3, 0.75, 80, 0.55), (5, 0.92, 88, 0.55), (5, 0.92, 100, 0.57)]:
    co2 = sub_cm / 100 * ox * bd * c * C_TO_CO2 * 10      # t CO2/ha/yr  (kg/m2 * 10 = t/ha)
    print(f" subsidence {sub_cm} cm/yr, oxidative share {ox}, BD {bd} kg/m3, C {c}: {co2:.0f} t CO2/ha/yr "
          f"(Hooijer 2012 measured 73 after yr 5)")
resid_ch4_kg = (20, 60)                                   # ASSUME kg CH4/ha/yr from rewetted tropical peat
for r in resid_ch4_kg:
    print(f" residual CH4 after rewetting {r} kg/ha/yr = {r*GWP_CH4_BIO_100/1000:.1f} t CO2e/ha/yr")
for margin in (300, 900):                                 # ASSUME $/ha/yr net margin oil palm on peat
    for avoided in (35, 70):
        print(f" break-even carbon price: margin ${margin}/ha / {avoided} t = ${margin/avoided:.0f}/t CO2e")
for mha in (0.5, 1.0, 2.0):
    print(f" scale: rewet {mha} Mha of 4.3 Mha industrial-plantation peat x 35-70 t = {mha*35:.0f}-{mha*70:.0f} Mt CO2e/yr")
dac_equiv(0.05, 'rewetting 1 Mha (~50 Mt)')
print(" InSAR detection: Sentinel-1 time-series precision ~ mm-cm/yr (ASSUME 0.5-1 cm/yr per pixel-year);"
      " signal 3-5 cm/yr drained vs ~0-1 cm/yr rewetted -> SNR 3-10 per year before spatial averaging")
