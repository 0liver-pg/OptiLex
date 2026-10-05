"""Sanity checks for six import-and-recombine ideas (chemical process engineer generator).

Run: cd . && .venv/bin/python <this file>
All inputs marked ASSUMPTION are my engineering assumptions, not sourced data.
"""
import math, sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

def floor(x, cap=0.9, pur=0.99):
    return gj_per_tonne(min_separation_work(x, cap, pur))

def iso_comp_gj(p_bar_out, p_bar_in=1.0, T=T0):
    """Ideal-gas isothermal compression work, GJ/t CO2."""
    return gj_per_tonne(R * T * math.log(p_bar_out / p_bar_in))

def carnot(T_hot_C, T0_K=T0):
    return 1 - T0_K / (T_hot_C + 273.15)

print("=" * 78)
print("IDEA 1  Leilac (pure process CO2) + Brevik amine on fuel CO2 only")
print("=" * 78)
plant = 800e3          # t CO2/yr total (Brevik: 400 kt = ~50%)
proc_share = 0.60      # LEILAC 2017: process CO2 ~60% of a plant's direct CO2
leilac_cap = 0.95      # LEILAC 2017 design claim: 95% of process CO2
amine_cap = 0.90
q_brevik = (2.7, 3.2)  # ASSUMPTION GJ heat/t for 20-25% CO2 flue (Brevik not published)
q_fuel = (3.0, 3.6)    # ASSUMPTION GJ heat/t for ~10-13% CO2 flue (coal-like)
heat_avail = [400e3 * q for q in q_brevik]      # GJ/yr waste heat that today supports 400 kt
for pen in (1.0, 1.15):   # fuel penalty of indirect heating (ASSUMPTION 0-15%)
    proc = plant * proc_share
    fuel = plant * (1 - proc_share) * pen
    cap_proc = proc * leilac_cap
    cap_fuel = fuel * amine_cap
    need = [cap_fuel * q for q in q_fuel]
    total = cap_proc + cap_fuel
    print(f"fuel penalty x{pen}: plant CO2 {(proc+fuel)/1e3:.0f} kt, captured {total/1e3:.0f} kt "
          f"= {total/(proc+fuel):.1%}; amine heat need {need[0]/1e6:.2f}-{need[1]/1e6:.2f} PJ vs "
          f"available {heat_avail[0]/1e6:.2f}-{heat_avail[1]/1e6:.2f} PJ "
          f"(ratio worst {need[1]/heat_avail[0]:.2f}, best {need[0]/heat_avail[1]:.2f})")
# extra high-grade heat: cooling Leilac CO2 900->150 C
hot = 456e3 * 1.1e-3 * 750  # GJ/yr, cp ~1.1 kJ/kgK
print(f"Leilac product-CO2 sensible heat 900->150C: {hot/1e6:.2f} PJ/yr (upside, not counted)")
# flue-gas volume to the absorber (moles) before/after
mol = lambda t: t * 1e6 / 44.01
before_total_flue = mol(plant) / 0.22
treated_now = before_total_flue * (400e3 / amine_cap / plant)
after_flue = before_total_flue - mol(plant * proc_share * leilac_cap)
print(f"Absorber gas volume: today ~{treated_now/1e9:.1f} Gmol/yr treated; after retrofit "
      f"{after_flue/1e9:.1f} Gmol/yr to capture 90% of fuel CO2 -> x{after_flue/treated_now:.2f} absorber gas capacity; "
      f"CO2 in that flue {mol(plant*0.4)/after_flue:.1%}")
for x in (0.10, 0.13, 0.22):
    print(f"  separation floor at {x:.0%} CO2, 90%: {floor(x):.3f} GJ/t")
print(f"  Leilac product (~97% CO2, drying only): {floor(0.97, 0.9, 0.999):.4f} GJ/t; "
      f"liquefaction-pressure compression floor 1->16 bar {iso_comp_gj(16):.3f} GJ/t")
# exergy of reboiler heat at 125 C
for q in q_fuel:
    print(f"  amine heat {q} GJ/t at 125C = {q*carnot(125):.2f} GJ/t exergy -> 2nd-law eff "
          f"{(floor(0.13)+iso_comp_gj(16))/(q*carnot(125)+0.35):.0%} (incl 0.35 GJe/t aux+liquefaction ASSUMPTION)")

print()
print("=" * 78)
print("IDEA 2  CO2 as voidage replacement for Smackover direct lithium extraction")
print("=" * 78)
li_grade = (0.40, 0.58)   # kg Li/m3 (582 mg/L E. Texas 2025 avg per Wikipedia; SWA lower ASSUMPTION 400)
recov = 0.90              # ASSUMPTION DLE recovery
LCE = 5.323
rho_co2 = (600, 700)      # kg/m3 at ~300 bar, 110-130 C (ASSUMPTION from CO2 EOS tables)
for g in li_grade:
    lce_per_m3 = g * recov * LCE
    m3_per_t = 1000 / lce_per_m3
    co2 = [m3_per_t * r / 1000 for r in rho_co2]
    print(f"Li {g*1000:.0f} mg/L: {lce_per_m3:.2f} kg LCE/m3, {m3_per_t:.0f} m3 brine/t LCE -> "
          f"voidage holds {co2[0]:.0f}-{co2[1]:.0f} t CO2 per t LCE (100% replacement)")
for g in li_grade:
    m3 = 22_500 * 1000 / (g * recov * LCE)
    print(f"SWA 22.5 kt LCE/yr at {g*1000:.0f} mg/L: brine {m3/1e6:.1f} Mm3/yr -> CO2 "
          f"{m3*0.6/1e6:.1f}-{m3*0.7/1e6:.1f} Mt/yr at 100% replacement, "
          f"{m3*0.6*0.5/1e6:.1f}-{m3*0.7*0.5/1e6:.1f} Mt/yr at 50%")
# revenue per tonne CO2 from Li (reverse view)
for g in li_grade:
    m3_per_tco2 = 1000 / 650  # m3 voidage per t CO2 at 650 kg/m3
    lce = m3_per_tco2 * g * recov * LCE
    print(f"Per t CO2 stored at {g*1000:.0f} mg/L: {m3_per_tco2:.2f} m3 brine -> {lce:.1f} kg LCE = "
          f"${lce*10:.0f}-{lce*15:.0f} gross at $10-15/kg; storage fee $15-30/t CO2 x {1/lce*1000:.0f} t CO2/t LCE "
          f"= ${15/lce:.1f}-{30/lce:.1f}k per t LCE")
print(f"Compression floor to 300 bar (ideal isothermal): {iso_comp_gj(300):.2f} GJ/t; disposal of spent brine "
      f"$3-10/m3 (ASSUMPTION) = ${3*1.54:.0f}-{10*1.54:.0f}/t CO2")
# breakthrough time for a 1 km2 pattern
pv = 1e6 * 30 * 0.15
for sweep in (0.3, 0.5):
    print(f"Pattern 1 km2 x 30 m x 15% porosity: CO2 at {sweep:.0%} sweep before breakthrough = "
          f"{pv*sweep*0.65/1e6:.2f} Mt -> {pv*sweep*0.65/0.25e6:.0f} yr at 0.25 Mt/yr per injector")
for lce_kt in (100, 200):
    print(f"US Smackover {lce_kt} kt LCE/yr -> {lce_kt*1e3*214/1e6:.0f}-{lce_kt*1e3*368/1e6:.0f} Mt CO2/yr upper bound")

print()
print("=" * 78)
print("IDEA 3  Gas-DRI (Energiron-type) selective CO2 stream to ship-based storage")
print("=" * 78)
for gas in (9.6, 10.5):           # GJ NG / t DRI (2.3-2.5 Gcal/t, ASSUMPTION from vendor ranges)
    co2 = gas * 0.0561             # t CO2 / GJ for methane (56.1 kg/GJ LHV)
    for frac in (0.45, 0.60):
        cap = co2 * frac
        print(f"NG {gas} GJ/tDRI: total C as CO2 {co2:.2f} t/t; selective stream {frac:.0%} -> {cap:.2f} t CO2/t DRI")
print(f"Separation floor for a 95% CO2 stream: {floor(0.95,0.9,0.999):.4f} GJ/t; "
      f"liquefaction compression floor 1->16 bar {iso_comp_gj(16):.2f} GJ/t")
# net intensity per t liquid steel (1.07 t DRI / t LS)
for cap, resid_dri, elec, grid, leak in [(0.33, 0.20, 0.55, 0.20, 0.005), (0.20, 0.35, 0.60, 0.25, 0.015)]:
    ch4 = 10.0 / 50.0  # t CH4 per t DRI at 10 GJ
    up = ch4 * leak * GWP100['CH4_fossil']
    eaf_direct = 0.08
    total = 1.07 * (resid_dri + up) + eaf_direct + elec * grid
    print(f"captured {cap} t/tDRI: net {total:.2f} t CO2e/t steel (residual DRI {resid_dri}, leak {leak:.1%}, "
          f"EAF {elec} MWh at {grid} t/MWh) vs BF-BOF 1.9-2.2 -> cut {1-total/2.05:.0%}")
for tns in (55, 105):
    for cap in (0.20, 0.33):
        print(f"  CCS cost ${tns}/t CO2 x {cap} t/t x1.07 = ${tns*cap*1.07:.0f}/t steel; EU ETS avoided at EUR70-100: "
              f"EUR{70*cap*1.07:.0f}-{100*cap*1.07:.0f}/t steel")
print("  H2 premium reference: $55/t steel per $1/kg H2 (map); $5 vs $1.5/kg gap ~$190/t steel")

print()
print("=" * 78)
print("IDEA 4  Carbfix-style dissolution into Permian produced-water disposal")
print("=" * 78)
def co2_solubility_g_per_L(p_bar, T_C, nacl_molal):
    """Rough: Henry + fugacity + Setschenow. ASSUMPTION-level accuracy (+-30%)."""
    kH25 = 0.034  # mol/(L atm)
    kH = kH25 * math.exp(2400 * (1 / (T_C + 273.15) - 1 / 298.15))
    phi = 1 - 0.005 * p_bar if p_bar < 60 else 0.7   # crude fugacity coefficient ~0.75 at 50 bar
    ks = 0.11  # L/mol Setschenow (NaCl)
    c = kH * phi * p_bar / 1.01325 * 10 ** (-ks * nacl_molal)
    return c * 44.01
for p in (30, 50):
    for T in (30, 40):
        for m in (0.0, 2.0, 3.5):
            print(f"  {p} bar, {T} C, NaCl {m} mol/kg: ~{co2_solubility_g_per_L(p,T,m):.0f} g CO2/L", end="")
        print()
for bbl_d in (15e6, 20e6):
    m3 = bbl_d * 0.158987 * 365
    for s in (15, 30):
        print(f"SWD {bbl_d/1e6:.0f} MMbbl/d = {m3/1e9:.2f} bn m3/yr x {s} kg/m3 = {m3*s/1e9:.0f} Mt CO2/yr "
              f"({1000/s:.0f} m3 water per t CO2; added volume ~{s/1000/ (44.01/0.035/1e3) if False else s*0.8/1000:.1%} of water)")
print(f"Compression floor 1->50 bar: {iso_comp_gj(50):.2f} GJ/t vs 1->150 bar {iso_comp_gj(150):.2f} GJ/t")
for dp in (0, 3e6):
    print(f"  extra water pressurisation {dp/1e6:.0f} MPa x 50 m3/t / 0.7 = {dp*50/0.7/1e9:.2f} GJ/t")
# partial molar volume of dissolved CO2 ~35 cm3/mol -> m3 per t
print(f"Dissolved CO2 adds {1e6/44.01*35e-6:.2f} m3 per t vs free-phase {1000/650:.2f} m3/t at 650 kg/m3")

print()
print("=" * 78)
print("IDEA 5  Horizontal stimulated doublets with water recycle for basalt mineral storage")
print("=" * 78)
for q_Ls in (30, 63):            # Fervo Project Red doublet up to 63 L/s
    for c in (25, 45):           # kg CO2/m3 dissolved (seawater ~25, fresh ~45 at 25-40 bar)
        kg_s = q_Ls / 1000 * c
        print(f"  {q_Ls} L/s x {c} kg/m3 = {kg_s:.2f} kg/s = {kg_s*3.156e7/1e6*1000:.0f} kt/yr per doublet "
              f"-> {1e6/(kg_s*3.156e7):.0f} doublets per Mt/yr")
for loss in (0.05, 0.2):
    for c in (25, 45):
        print(f"  water make-up at {loss:.0%} fluid loss, {c} kg/m3: {1000/c*loss:.1f} t/t (once-through {1000/c:.0f} t/t)")
# kinetics: cation supply needed
for kt in (20, 80):
    mol_s = kt * 1e9 / 44.01 / 3.156e7
    for logr, label in ((-9.0, 'basaltic glass pH~4-5, ~50C'), (-10.0, 'crystalline basalt ~25-50C')):
        r = 10 ** logr * 0.6   # mol divalent cations per m2 per s (Ca+Mg+Fe ~0.6 per Si) ASSUMPTION
        A = mol_s / r
        print(f"  {kt} kt/yr = {mol_s:.0f} mol/s needs {A:.1e} m2 reactive surface at log r={logr} ({label}); "
              f"at 300 m2/m3 rock = {A/300/1e6:.0f} Mm3 rock")

print()
print("=" * 78)
print("IDEA 6  Industrial N2O results contract with EU-ETS-grade CEMS and capped baseline")
print("=" * 78)
china_co2e_ar5 = 76e6
n2o_t = china_co2e_ar5 / 265
print(f"China adipic N2O ~76 Mt CO2e (AR5) = {n2o_t/1e3:.0f} kt N2O = {n2o_t*GWP100['N2O']/1e6:.0f} Mt CO2e at AR6")
ef = 0.30   # t N2O per t adipic acid unabated (ASSUMPTION, IPCC default ~0.3)
print(f"Unabated: {ef} t N2O/t AA = {ef*GWP100['N2O']:.0f} t CO2e per t adipic acid")
for price in (1, 2, 5, 10):
    print(f"  payment ${price}/t CO2e x 95% abatement = ${price*ef*GWP100['N2O']*0.95:.0f} per t AA "
          f"(AA price ~$1,400-1,800/t ASSUMPTION) ; China total ${price*n2o_t*GWP100['N2O']*0.95/1e6:.0f}M/yr")
# detectability of a plant plume: 25 kt N2O/yr plant
plant_kt = n2o_t / 11 / 1e3
q = plant_kt * 1e6 / 3.156e7  # kg/s
for u, sigma_area in ((5, 200 * 100),):
    # crude Gaussian-plume centreline enhancement at ~2 km: C = Q/(pi u sy sz); sy=200, sz=100 m
    C = q / (math.pi * u * 200 * 100)    # kg/m3
    ppb = C / (M_N2O) * R * T0 / P0 * 1e9
    print(f"  plant ~{plant_kt:.0f} kt N2O/yr unabated ({q:.2f} kg/s): ~2 km downwind enhancement ~{ppb:.0f} ppb "
          f"over ~337 ppb background (CRDS precision <0.1 ppb) -> trivially detectable; 90% abated -> ~{ppb/10:.0f} ppb")
fan = fan_work_gj_per_tonne(1.93e-6, 0.5, 100, molar_mass=M_CH4)
print(f"(context) ambient-air CH4 fan floor: {fan:.0f} GJ/t CH4 -> source abatement is the only sane route")
