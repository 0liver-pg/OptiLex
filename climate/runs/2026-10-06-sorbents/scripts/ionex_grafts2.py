import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

print("=== IDEA 4 (replacement): hydrophobic microporous layer (PEMFC GDL/MPL import) on steam-regenerated amine laminates ===")
gamma100 = 0.0589   # N/m water surface tension at 100 C
gamma25 = 0.072
for theta in (120.0, 140.0):
    for r_um in (0.5, 2.0, 10.0):
        dp = -2*gamma100*math.cos(math.radians(theta))/(r_um*1e-6)
        print(f"  contact angle {theta:.0f} deg, pore radius {r_um} um: liquid breakthrough pressure {dp/1e3:.0f} kPa at 100 C "
              f"(condensate head of 1 cm water = 0.1 kPa)")
# vapour/CO2 diffusion resistance of the MPL vs gas film in a 1 mm channel
D_co2_air = 1.6e-5; D_h2o_air = 2.5e-5
delta, eps, tau = 40e-6, 0.5, 3.0
R_mpl_co2 = delta/(eps*D_co2_air/tau); R_mpl_h2o = delta/(eps*D_h2o_air/tau)
Sh, dh = 3.66, 2e-3
kg = Sh*D_co2_air/dh
print(f"  MPL 40 um, porosity 0.5, tortuosity 3: diffusion resistance {R_mpl_co2:.1f} s/m (CO2), {R_mpl_h2o:.1f} s/m (H2O) vs gas film {1/kg:.1f} s/m in a 1 mm channel")
print("  (the sorbent layer is 10-20x slower than the gas film per the map, so a +30% gas-side resistance is not limiting)")
# heat conduction through the MPL during steam heating
m_sorb, cp, dT, t_heat, k_mpl = 0.2, 1500.0, 75.0, 60.0, 0.2
q = m_sorb*cp*dT/t_heat
print(f"  heating 0.2 kg/m2 sorbent by 75 K in 60 s needs {q:.0f} W/m2; temperature drop across a 40 um MPL (k 0.2 W/m/K): {q*delta/k_mpl:.2f} K")
# thermal-mass penalty of the MPL
for mpl_gsm in (10, 30):
    ratio = mpl_gsm/200.0
    base = TVSACycle(dH=-70e3, dS=-165.0, q_max=2.0, water_coads=3.0)
    with_mpl = TVSACycle(dH=-70e3, dS=-165.0, q_max=2.0, water_coads=3.0, inert_mass_ratio=ratio, cp_inert=800.0)
    print(f"  MPL {mpl_gsm} g/m2 on 200 g/m2 sorbent: inert ratio {ratio:.2f} -> heat {base.heat_gj_per_t:.2f} -> {with_mpl.heat_gj_per_t:.2f} GJ/t (+{with_mpl.heat_gj_per_t-base.heat_gj_per_t:.2f})")
print("  cycle-life economics the MPL protects (1.04 mol/kg, $15/kg):")
for cyc in (300, 2000, 6500, 20000):
    print(f"    {cyc:>6} cycles: ${sorbent_cost_per_tonne(15, 1.04, cyc):.0f}/t")

print("\n=== IDEA 1 extra: per-cycle loss budget and diagnostic sensitivity ===")
for life_cycles, loss in ((1380, 0.9), (15000, 0.2), (50000, 0.2)):
    print(f"  {loss:.0%} loss over {life_cycles} cycles = {loss/life_cycles*100:.1e} % per cycle")
print("  Hofmann/SN2 products: trimethylamine (SN2 on BTMA) 1 mol per site lost; 10 g resin x 4.18 mmol/g x 1e-3 %/cycle = "
      f"{10*4.18e-3*1e-5:.1e} mol TMA per cycle -> headspace GC-MS detectable (ng level)")

print("\n=== IDEA 6 extra: pressure drop budget and water ratio reference ===")
# Georgia Tech/Gore hydrophobic laminate: 3.1 mol H2O per mol CO2 measured (Realff NETL 2023) -> 3.1 GJ/t
print(f"  3.1 mol H2O/mol CO2 (GT/Gore hydrophobic laminate) = {gj_per_tonne(3.1*DH_VAP_WATER):.2f} GJ/t latent; alumina-type 6-9 mol/mol = {gj_per_tonne(6*DH_VAP_WATER):.1f}-{gj_per_tonne(9*DH_VAP_WATER):.1f} GJ/t")
for dp in (150, 300, 700):
    print(f"  fan work at {dp} Pa, 60% capture: {fan_work_gj_per_tonne(420e-6, 0.6, dp):.2f} GJ/t ({fan_work_gj_per_tonne(420e-6, 0.6, dp)/0.0036:.0f} kWh/t)")
