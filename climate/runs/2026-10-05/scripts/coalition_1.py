"""coalition_1: Methane-intensity quality differential in gas/LNG contracts -- physics + techno-economic check.

Sources used (labelled in output):
  [IEA-NZR23] IEA Net Zero Roadmap 2023 update (local copy nzr.txt): fossil CH4 ~125 Mt (2022), oil ~40, gas ~40,
              coal ~40 Mt; US and Russia ~14 Mt each from oil & gas; ~40% of oil&gas CH4 avoidable at no net cost
              (2017-21 prices); USD 75 bn cumulative to 2030 for all oil&gas abatement measures (75% cut).
  [IGU]       LNG trade 2024 ~411 Mt (IGU World LNG Report 2025, from memory, unverified this session).
  [MEM]       From memory, unverified this session (web search budget exhausted) -- flagged where used.
"""
import sys, math, random
sys.path.insert(0, 'climate')
from physics import *

G100, G20 = GWP100["CH4_fossil"], GWP20["CH4_fossil"]
GJ_PER_MMBTU = 1.055056
HHV, LHV = 55.5, 50.0                   # MJ/kg CH4
KG_PER_MMBTU = GJ_PER_MMBTU * 1e3 / HHV
MMBTU_PER_T_CH4 = 1e3 / KG_PER_MMBTU

def hdr(s): print("\n=== " + s + " ===")
def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)

hdr("0. Thermodynamic floor")
w_air = min_separation_work(1.93e-6, 0.5, 0.99)
print(f"Separating CH4 from ambient air (1.93 ppm, 50% capture): floor {w_air/1e3:.1f} kJ/mol = "
      f"{gj_per_tonne(w_air, M_CH4):.2f} GJ/t CH4 = {gj_per_tonne(w_air, M_CH4)/G100:.3f} GJ/t CO2e (GWP100)")
fan = fan_work_gj_per_tonne(1.93e-6, 0.5, 100, 0.6, M_CH4)
print(f"Fan work alone (100 Pa, 60% fan): {fan:.0f} GJ/t CH4 = {fan/G100:.1f} GJ/t CO2e (GWP100), {fan/G20:.1f} (GWP20)")
print("Source abatement involves NO separation (it prevents release): floor = 0 GJ/t; recovered gas is energy-positive.")

hdr("1. Unit checks of the idea's claims (1)-(7)")
print(f"(1) kg CH4 per MMBtu (HHV): {KG_PER_MMBTU:.2f}   [claim 19.0]  -- pipeline gas is ~90-95% CH4, so true CH4 per MMBtu is ~3-8% lower [MEM]")
for hi, lo in [(0.01, 0.002), (0.02, 0.002)]:
    d = (hi - lo) * KG_PER_MMBTU
    print(f"(2) {hi:.1%}->{lo:.1%}: {d:.3f} kg CH4/MMBtu = {d*G100:.2f} kg CO2e GWP100, {d*G20:.2f} GWP20")
d = 0.008 * KG_PER_MMBTU * G100 / 1000
for p in (20, 50):
    print(f"(3) ${p}/t CO2e on the 1.0->0.2% step = ${d*p:.3f}/MMBtu = {d*p/11:.1%}-{d*p/10:.1%} of $10-11 LNG")
for i in (0.002, 0.01, 0.02):
    print(f"(4) intensity {i:.1%}: differential {(0.005-i)*KG_PER_MMBTU*G100/1000*30:+.3f} $/MMBtu (ref 0.5%, $30/t)")
LNG_MT = 411.0
mmbtu_lng = LNG_MT * 1e6 * 54.4 / GJ_PER_MMBTU
print(f"(5) LNG {LNG_MT} Mt = {mmbtu_lng/1e9:.1f} bn MMBtu; $0.10/MMBtu = ${mmbtu_lng*0.1/1e9:.2f} bn/yr; "
      f"buys {mmbtu_lng*0.1/20/1e6:.0f} Mt CO2e at $20/t ({mmbtu_lng*0.1/20/G100/1e6:.2f} Mt CH4), {mmbtu_lng*0.1/50/1e6:.0f} Mt at $50/t")
for p in (3, 11):
    print(f"(6) recovered gas at ${p}/MMBtu: ${p*MMBTU_PER_T_CH4:.0f}/t CH4 = ${p*MMBTU_PER_T_CH4/G100:.1f}/t CO2e GWP100")
print(f"(7) energy recovered per t CH4 sold: {LHV:.0f} GJ (LHV), {HHV:.1f} GJ (HHV)")

hdr("2. Revenue neutrality: fixed 0.5% reference vs supply-weighted mean")
# 2024 LNG exporter shares and upstream intensities: ALL [MEM], modelled/illustrative, measurement-dependent.
suppliers = {  # name: (Mt LNG, low, base, high intensity as fraction of gas delivered)
    "USA":       (88, 0.008, 0.015, 0.030),   # aerial basin surveys ~1-3% (Sherwin 2024 order), operator-reported lower
    "Australia": (80, 0.003, 0.006, 0.010),
    "Qatar":     (77, 0.001, 0.002, 0.005),   # operator-reported; little independent measurement
    "Russia":    (33, 0.008, 0.015, 0.030),
    "Malaysia":  (27, 0.003, 0.007, 0.015),
    "Nigeria":   (15, 0.010, 0.020, 0.040),
    "Algeria":   (12, 0.010, 0.020, 0.040),
    "Others":    (79, 0.004, 0.010, 0.020),
}
tot = sum(v[0] for v in suppliers.values())
print(f"Supplier volumes sum to {tot} Mt [MEM, approximate 2024 shares]")
for k, lab in [(1, "low"), (2, "base"), (3, "high")]:
    mean = sum(v[0] * v[k] for v in suppliers.values()) / tot
    net = (0.005 - mean) * KG_PER_MMBTU * G100 / 1000 * 30 * mmbtu_lng
    ch4 = sum(v[0] * v[k] for v in suppliers.values()) * 1e6 * 0.92  # t CH4, 92% CH4 content
    print(f"  {lab}: volume-weighted intensity {mean:.2%}; net seller->buyer transfer at fixed 0.5% ref, $30/t: "
          f"${-net/1e9:+.2f} bn/yr (positive = buyers receive); upstream CH4 tied to LNG = {ch4/1e6:.1f} Mt/yr")
print("  => With a fixed 0.5% reference the clause is NOT revenue-neutral: in the base case it is a ~$1.7 bn/yr (range -0.1 to +5.1) price cut paid by")
print("     exporters. Neutrality requires the reference to be the volume-weighted measured mean, reset each period (a feebate).")

hdr("3. 'More conservative of two methods' bias")
random.seed(1)
for s in (0.001, 0.003, 0.005):
    sims = [max(random.gauss(0, s), random.gauss(0, s)) for _ in range(200000)]
    bias = sum(sims) / len(sims)
    print(f"  each method unbiased, sigma {s:.1%}: E[max] bias = +{bias:.3%} (analytic {s/math.sqrt(math.pi):.3%}) "
          f"= ${bias*KG_PER_MMBTU*G100/1000*30:.3f}/MMBtu systematic penalty at $30/t")
# plume-inventory (lower bound, detection limit) vs inversion (total): structural, not noise
for frac_detected in (0.3, 0.5, 0.7):
    print(f"  if a plume inventory sees only {frac_detected:.0%} of total emissions (detection limit), a true 1.5% basin reads "
          f"{1.5*frac_detected:.2f}% vs inversion 1.5%: gap {1.5*(1-frac_detected):.2f} pp > 0.3 pp falsification threshold")
print(f"  Idea's own Permian example: 3.2/0.44 = {3.2/0.44:.1f}x disagreement")

hdr("4. Incentive dilution: basin-level settlement vs export share")
for exp_share in (0.12, 0.25, 0.5):
    for slope in (30, 50):
        print(f"  export share {exp_share:.0%} of basin gas, slope ${slope}/t: effective basin-wide incentive "
              f"${exp_share*slope:.1f}/t CO2e (${exp_share*slope*G100:.0f}/t CH4)")
print("  US LNG exports ~12% of US dry gas output (2024, [MEM]); basin-level measurement also gives a best-practice")
print("  operator in a leaky basin the basin's (worse) number -> individual incentive is weak unless operator-level data dominate.")

hdr("5. Abatement cost per t CO2e (GWP100)")
abated_mt = 0.75 * 80   # IEA-NZR23: 75% of ~80 Mt oil&gas CH4
for r, n, om, lab in [(0.06, 15, 0.03, "low"), (0.08, 10, 0.05, "base"), (0.10, 7, 0.08, "high")]:
    ann = 75e9 * crf(r, n) + 75e9 * om
    gross = ann / (abated_mt * 1e6)
    print(f"  {lab}: r={r:.0%}, n={n}, O&M {om:.0%}/yr: ${ann/1e9:.1f} bn/yr -> ${gross:.0f}/t CH4 = ${gross/G100:.1f}/t CO2e gross (fleet average)")
for gas_p, sellable in [(11, 0.6), (3, 0.5), (0, 0.0)]:
    credit = gas_p * MMBTU_PER_T_CH4 * sellable / G100
    print(f"  gas credit at ${gas_p}/MMBtu, {sellable:.0%} of abated CH4 sellable: -${credit:.1f}/t CO2e")
meas_low, meas_base, meas_high = 0.002, 0.005, 0.015   # $/MMBtu measurement+verification overhead [assumed]
for lab, m, step in [("low", meas_low, 0.010), ("base", meas_base, 0.008), ("high", meas_high, 0.004)]:
    t = step * KG_PER_MMBTU * G100 / 1000
    print(f"  MRV overhead {lab}: ${m}/MMBtu over an intensity cut of {step:.1%} ({t*1000:.1f} kg CO2e/MMBtu) = ${m/t:.1f}/t CO2e")
c_low  = 75e9*crf(0.06,15)+75e9*0.03; c_low = c_low/(abated_mt*1e6)/G100 - 11*MMBTU_PER_T_CH4*0.6/G100 + 0.002/(0.010*KG_PER_MMBTU*G100/1000)
c_base = 75e9*crf(0.08,10)+75e9*0.05; c_base = c_base/(abated_mt*1e6)/G100 - 3*MMBTU_PER_T_CH4*0.5/G100 + 0.005/(0.008*KG_PER_MMBTU*G100/1000)
c_high = 30 + 0.015/(0.004*KG_PER_MMBTU*G100/1000)   # marginal measures up to slope ($30/t) + high MRV
print(f"  NET cost per t CO2e GWP100: low {c_low:+.1f}, base {c_base:+.1f}, high {c_high:+.1f} "
      f"(high = marginal measures abated up to the $30/t slope + high MRV, no gas credit)")

hdr("6. Energy per t CO2e (GWP100)")
vru = R * T0 * math.log(70) / 0.7 / M_CH4 / 1e6   # GJ/t CH4 isothermal 1->70 bar at 70% eff
e_low = -LHV / G100
e_base = (-LHV * 0.5 + vru * 0.5) / G100
e_high = 0.05
print(f"  VRU compression 1->70 bar (70% eff): {vru:.2f} GJ/t CH4")
print(f"  low {e_low:.2f} GJ/t CO2e (all abated CH4 recovered, LHV), base {e_base:.2f} (50% recovered, compressed), "
      f"high +{e_high:.2f} (no recovery; measurement + electric pneumatics only, assumed)")

hdr("7. Realistic scale (Gt CO2e/yr)")
cases = {"low":  (3.0, 0.4, 0.0),    # Mt CH4 tied to covered trade, fraction abated, spillover Mt
         "base": (5.5, 0.6, 1.0),
         "high": (8.0, 0.75, 8.0)}  # high: basin-wide spillover in exporting basins (US+others, ~14+ Mt base [IEA-NZR23])
for lab, (m, f, sp) in cases.items():
    mt = m * f + sp
    print(f"  {lab}: covered upstream CH4 {m} Mt x {f:.0%} abated + spillover {sp} Mt = {mt:.1f} Mt CH4 = "
          f"{mt*G100/1e3:.3f} Gt CO2e GWP100 ({mt*G20/1e3:.3f} GWP20)")
print(f"  Idea's claimed lever 35-85 Mt CH4 = {35*G100/1e3:.2f}-{85*G100/1e3:.2f} Gt CO2e: that is the whole abatable "
      f"fossil pool (oil+gas+coal), not what LNG/EU-import contracts can reach.")
s = ScaleCheck(0.2, e_base)
print(f"  Energy at base scale 0.2 Gt: {s.ej_per_year:+.2f} EJ/yr = {s.share_of_world_primary_energy:+.3%} of world primary energy (negative = net supply)")

hdr("8. Adoption pace (contract turnover)")
for spot, renew in [(0.35, 0.05), (0.35, 0.10)]:
    for yr in (3, 5, 10):
        cov = spot + (1 - spot) * (1 - (1 - renew) ** yr)
        print(f"  spot/short-term {spot:.0%} adopt at once, term contracts renew {renew:.0%}/yr: coverage after {yr} yr = {cov:.0%}")
