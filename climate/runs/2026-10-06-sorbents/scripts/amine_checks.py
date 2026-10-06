import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

print("== 1. Grossmann/Mazzotti 2025 amine-alumina: Toth dry CO2 + GAB water (fitted params from paper)")
def toth(p_kpa, T, T0_=308.0, qs0=1.17, b0=2.96e3, t0=0.25, dH=-77.8e3, alpha=0.19, chi=0.49):
    b = b0*math.exp(-dH/(R*T0_)*(T0_/T-1.0))
    t = t0 + alpha*(1.0-T0_/T)
    qs = qs0*math.exp(chi*(1.0-T/T0_))
    return qs*b*p_kpa/((1.0+(b*p_kpa)**t)**(1.0/t))
def gab(x, qm=3.51, c=2.73, k=0.867):
    return qm*c*k*x/((1-k*x)*(1+(c-1)*k*x))
for T in (288.15, 298.15, 308.15):
    print(f"  dry CO2 uptake at 42 Pa, {T-273.15:.0f} C: {toth(0.042,T):.2f} mmol/g")
print(f"  dry CO2 at 1 kPa, 100 C (residual on desorption): {toth(1.0,373.15):.3f} mmol/g")
for rh in (0.2,0.4,0.5,0.8):
    w=gab(rh); q=toth(0.042,298.15)
    print(f"  RH {rh:.0%}: water {w:.2f} mmol/g ; H2O:CO2(dry-eq) = {w/q:.1f} mol/mol")

print("\n== 2. Water co-desorption heat penalty in the reference TVSA cycle")
for wc in (0,2,4,8):
    c=TVSACycle(dH=-70_000.0, dS=-165.0, q_max=2.0, T_des=373.15, p_des=1.0e3, water_coads=wc)
    print(f"  {wc} mol H2O/mol CO2: heat {c.heat_gj_per_t:.2f} GJ/t (water part {gj_per_tonne(c.water_heat):.2f}), work-eq {c.work_equivalent_gj_per_t:.2f} GJ/t")

print("\n== 3. Fan work at measured/target pressure drops (75% capture, 60% fan eff.)")
for dp,label in ((100,'OptiLex baseline'),(150,'GT monolith <150 Pa at 5 m/s (company)'),(400,'Climeworks/Svante Gen3 target low'),(700,'Gen3 target high'),(800,'Gen2 target low'),(1000,'Gen2 target high')):
    for cf in (0.75,0.5):
        e=fan_work_gj_per_tonne(X_AIR, cf, dp)
        print(f"  {dp:5d} Pa capture {cf:.0%}: {e:.2f} GJ/t = {e/0.0036:.0f} kWh/t   [{label}]")

print("\n== 4. Productivity and sorbent consumption: laminate fast cycle vs packed bed")
cases=[('Gen3 laminate target, 0.9 mol/kg fast-cycle, 40-min cycle',0.9,36.0),
       ('Gen3 laminate, 0.9 mol/kg, 60-min cycle',0.9,24.0),
       ('Muttenz test pace: 1300 cycles in ~250 d',0.9,1300/250),
       ('Packed bed Gen2-like, 1.0 mol/kg, 5 cycles/d',1.0,5.0)]
for label,wc,cpd in cases:
    p=productivity(wc,cpd)
    print(f"  {label}: {p:.2f} kg CO2/kg/day = {p*365/1000:.2f} t/kg/yr")
    for life_y in (0.5,1,3):
        cyc=cpd*365*life_y
        kg_per_t=1000/(wc*M_CO2*cyc)
        print(f"     life {life_y} y = {cyc:,.0f} cycles: {kg_per_t:.2f} kg sorbent/t; replacement ${sorbent_cost_per_tonne(15,wc,cyc):.0f}/t at $15/kg, ${sorbent_cost_per_tonne(50,wc,cyc):.0f}/t at $50/kg")

print("\n== 5. NETL 2022 sensitivity back-out: (COC at $15/kg - base)/(15-0.2) and ($100/kg)")
print(f"  implied sorbent use: {(1030-702)/(15-0.2):.1f} and {(2910-702)/(100-0.2):.1f} kg sorbent per t CO2 at 0.5-y life, 1.2 mol/kg")
kg=22.1; cycles=1000/(kg*1.2*M_CO2)
print(f"  => {cycles:.0f} full-capacity cycles in 0.5 y = {cycles/182.5:.1f} cycles/day equivalent")

print("\n== 6. Orca plant: best 7-day annualised rate on 2-year-old filter vs max achievable")
for mx in (2400,2500):
    print(f"  1900/{mx} = {1900/mx:.0%} -> all-cause shortfall {1-1900/mx:.0%} after >2 y; upper bound on capacity fade ~{(1-1900/mx)/2:.0%}/y (linear)")
print(f"  Orca 2023 actual 1000 t vs 3000 t design net = {1000/3000:.0%}; Mammoth H1-2026 675 t net vs 18,000 t half-year nameplate = {675/18000:.1%}")

print("\n== 7. Unstabilised bPEI/Al2O3 oxidation (JACS 2024, dry 0.04% CO2 in air, 18 h)")
k60=-math.log(1-0.15)/18; k55=-math.log(1-0.02)/18
print(f"  k(60C)={k60:.4f}/h, k(55C)={k55:.5f}/h; apparent Ea = {math.log(k60/k55)*R/(1/328.15-1/333.15)/1000:.0f} kJ/mol (non-Arrhenius: induction/autocatalysis)")
for loss in (0.05,0.10):
    h=-math.log(1-loss)/k60
    print(f"  hours at 60 C in air for {loss:.0%} loss: {h:.1f} h ; per cycle at 13,140 cycles/y: {h*3600/13140:.1f} s ; at 1,825 cycles/y: {h*3600/1825:.0f} s")
print("  ambient storage (ACS Omega 2026): <13% in 12 months at 23 C in air -> same order as the <5-10%/y commercial targets")

print("\n== 8. Amine efficiency headroom (laminate PEI/ePTFE/silica, JACS Au 2025)")
for ae in (0.12,0.17,0.19,0.29):
    print(f"  measured {ae} mol CO2/mol N -> {ae/0.5:.0%} of dry carbamate limit (0.5), {ae:.0%} of 1:1 limit")

print("\n== 9. Energy: reaction-heat share and 'half the energy' sanity check")
ref=reference_amine_cycle()
print(f"  reference: heat {ref.heat_gj_per_t:.2f} GJ/t, WC {ref.working_capacity:.2f} mol/kg; reaction {gj_per_tonne(ref.reaction_heat):.2f}, sensible {gj_per_tonne(ref.sensible_heat):.2f}, water {gj_per_tonne(ref.water_heat):.2f}")
print(f"  Deutz&Bardow-type plant data as tabulated in EES 2025 review: 700 kWh_el + 11.9 GJ heat (4 kt/y) ; 500 kWh_el + 5.4 GJ (100 kt/y scenario)")
print(f"  thermodynamic floor {gj_per_tonne(min_separation_work(X_AIR,0.75,0.99)):.2f} GJ/t; 11.9 GJ heat at 100 C exergy = {11.9*(1-298.15/373.15):.2f} GJ/t + 700 kWh = {0.7*3.6:.2f} GJ/t -> 2nd-law eff {gj_per_tonne(min_separation_work(X_AIR,0.75,0.99))/(11.9*(1-298.15/373.15)+0.7*3.6):.1%}")
