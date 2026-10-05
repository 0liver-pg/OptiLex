"""Verifier for graft_bio_3: sulfate-recharged AWD (gypsum + alternate wetting and drying in rice).

No gas separation is involved, so the separation floor does not apply. The binding "floor"
is electron-balance stoichiometry: one mol SO4 accepts the 8 electrons that would otherwise
make one mol CH4 (CH3COO- + SO4 -> 2 HCO3- + HS-; 4 H2 + SO4 + H+ -> HS- + 4 H2O).
"""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

M_GYP = 0.17217   # kg/mol CaSO4.2H2O
M_S = 0.03206
GWP100_B = GWP100["CH4_biogenic"]   # 27.0 (AR6, biogenic incl. no fossil C)
GWP20_B = GWP20["CH4_biogenic"]     # 79.7

def line(t=""):
    print(t)

# ---------------------------------------------------------------- 1. stoichiometric cap
line("=== 1. Stoichiometric cap (replaces the separation floor; no separation step) ===")
kg_gyp_per_kg_ch4 = M_GYP / M_CH4
ch4_per_t_gyp = 1000 / kg_gyp_per_kg_ch4
line(f"Gypsum needed per kg CH4 diverted (1:1 SO4:CH4, 100% efficiency): {kg_gyp_per_kg_ch4:.2f} kg")
line(f"Max CH4 avoided per tonne gypsum, single use: {ch4_per_t_gyp:.1f} kg = "
     f"{ch4_per_t_gyp*GWP100_B/1000:.2f} t CO2e (GWP100) / {ch4_per_t_gyp*GWP20_B/1000:.2f} t CO2e (GWP20)")
line(f"S content of gypsum: {M_S/M_GYP:.1%}")

# Check claim (2): emissions 100-250 kg CH4/ha; emissions = 30-60% of production; divert 20-40% of production
line("\nClaim (2) re-derivation:")
for E, ef, div in [(100, 0.60, 0.20), (250, 0.30, 0.40)]:
    prod = E / ef
    ch4_div = prod * div
    gyp = ch4_div * kg_gyp_per_kg_ch4 / 1000
    line(f"  E={E} kg, emitted/produced={ef:.0%}, divert {div:.0%} of production -> "
         f"{ch4_div:.0f} kg CH4 diverted, {gyp:.2f} t gypsum single-use, {gyp/3:.2f} t with 3x recycle")

# Check claim (3) per-dose consistency: savings 0.54-2.7 t CO2e/ha at 0.7-2 t gypsum
line("\nClaim (3) consistency with the cap:")
for dose, sav in [(0.7, 2.7), (2.0, 2.7), (0.7, 0.54)]:
    cap = dose * ch4_per_t_gyp * GWP100_B / 1000
    line(f"  dose {dose} t/ha -> single-use cap {cap:.2f} t CO2e/ha; claimed {sav} t CO2e/ha "
         f"needs recycle factor >= {max(sav/cap,0):.2f} at 100% electron efficiency")

# Cross-check against measured dose-response: Hu et al. 2018 (Huan Jing Ke Xue, FGD gypsum, Chongqing paddy,
# static chambers; continuous flood assumed): 2/4/8/16 t/ha cut mean CH4 flux by 31.6/57.3/83.6/90.7%.
line("\nImplied electron efficiency in Hu et al. 2018 (baseline flux not available to me; bracket 150-400 kg/ha):")
for dose, cut in [(2, 0.3156), (4, 0.5730), (8, 0.8360), (16, 0.9066)]:
    effs = []
    for base in (150, 400):
        avoided = base * cut
        effs.append(avoided / (dose * ch4_per_t_gyp))
    line(f"  {dose:>2} t/ha, -{cut:.1%}: avoided/stoich-max = {effs[0]:.0%} (150 kg base) to {effs[1]:.0%} (400 kg base)")

# ---------------------------------------------------------------- 2. scenarios per ha
line("\n=== 2. Per-hectare scenarios (gypsum stacked on AWD) ===")
# IPCC 2019 refinement: baseline EF 1.19 kg CH4/ha/day (continuously flooded, no organic amendment);
# multiple-drainage scaling factor 0.55 (i.e. AWD-like ~ -45%). Season ~100-130 days.
scen = {
    #            E0 kg/ha  AWD resid  extra cut of AWD residual  dose t/ha  gyp $/t  haul km  spread $/ha  MRV $/ha  yield credit $/ha
    "low":  dict(E0=250, awd=0.60, cut=0.40, dose=0.5, price=15, km=50,  spread=5,  mrv=3,  ycred=45),
    "base": dict(E0=150, awd=0.55, cut=0.25, dose=0.75, price=25, km=200, spread=10, mrv=8,  ycred=0),
    "high": dict(E0=100, awd=0.55, cut=0.10, dose=1.5, price=40, km=500, spread=15, mrv=12, ycred=0),
}
HAUL_USD_TKM = 0.06       # India road freight ~ INR 4-6 per t-km (order of magnitude, unverified)
TRUCK_MJ_TKM = 1.2        # heavy-duty diesel truck, ~0.8-1.5 MJ/t-km (ICCT-range, order of magnitude)
PROC_GJ_T = 0.05          # crushing/drying of by-product gypsum, GJ/t (assumed; natural gypsum ~0.1-0.2)
DIESEL_KGCO2_GJ = 74.1    # IPCC default diesel
CRF = 0.1 * 1.1**10 / (1.1**10 - 1)   # 10%, 10 yr
DEPOT_CAPEX_USD_PER_TPA = 15.0         # covered storage/blending depot per t/yr throughput (assumed)
res = {}
for k, s in scen.items():
    resid = s["E0"] * s["awd"]
    avoided_ch4 = resid * s["cut"]
    co2e100 = avoided_ch4 * GWP100_B / 1000
    co2e20 = avoided_ch4 * GWP20_B / 1000
    stoich_eff = avoided_ch4 / (s["dose"] * ch4_per_t_gyp)
    energy_gj_ha = s["dose"] * (s["km"] * TRUCK_MJ_TKM / 1000 + PROC_GJ_T) + 0.05  # +0.05 GJ/ha spreading/tractor
    emb_co2 = energy_gj_ha * DIESEL_KGCO2_GJ / 1000
    net100 = co2e100 - emb_co2
    capex_ann = s["dose"] * DEPOT_CAPEX_USD_PER_TPA * CRF
    cost_ha = s["dose"] * (s["price"] + s["km"] * HAUL_USD_TKM) + s["spread"] + s["mrv"] + capex_ann
    res[k] = dict(net100=net100, co2e20=co2e20, egj=energy_gj_ha / net100, cost=cost_ha / net100,
                  cost_y=(cost_ha - s["ycred"]) / net100, cost20=cost_ha / co2e20)
    line(f"[{k}] baseline {s['E0']} kg CH4/ha/season, AWD residual {resid:.0f} kg, extra cut {s['cut']:.0%} "
         f"-> {avoided_ch4:.1f} kg CH4 = {co2e100:.2f} t CO2e GWP100 ({co2e20:.2f} GWP20)")
    line(f"     dose {s['dose']} t/ha; electron efficiency needed (single use) {stoich_eff:.0%}; "
         f"S applied {s['dose']*1000*M_S/M_GYP:.0f} kg S/ha")
    line(f"     energy {energy_gj_ha:.3f} GJ/ha = {energy_gj_ha/net100:.3f} GJ/t CO2e net; embodied {emb_co2*1000:.0f} kg CO2/ha; "
         f"net {net100:.2f} t CO2e/ha")
    line(f"     cost ${cost_ha:.0f}/ha (capex annuity ${capex_ann:.2f}) -> ${res[k]['cost']:.0f}/t CO2e (GWP100), "
         f"${res[k]['cost20']:.0f}/t (GWP20); after yield credit ${s['ycred']}: ${res[k]['cost_y']:.0f}/t")

# Agronomic S requirement vs methane dose
line("\nAgronomic S dose for S-deficient rice soils ~20-40 kg S/ha (Indian practice, from memory) = "
     f"{20/(M_S/M_GYP)/1000:.2f}-{40/(M_S/M_GYP)/1000:.2f} t gypsum/ha; "
     "methane doses above are 2-7x that, so the yield credit only covers the first ~0.1-0.2 t.")

# ---------------------------------------------------------------- 3. scale
line("\n=== 3. Global scale ===")
RICE_CH4_MT = 30.0          # bottom-up ~25-38 Mt/yr (Global Methane Budget, Saunois et al.)
RICE_AREA_MHA = 165.0       # FAOSTAT harvested area ~2022
base_gt100 = RICE_CH4_MT * 1e6 * GWP100_B / 1e9
line(f"Rice CH4 {RICE_CH4_MT} Mt/yr = {base_gt100:.2f} Gt CO2e GWP100, {RICE_CH4_MT*GWP20_B/1e3:.2f} Gt GWP20")
RICE_CH4_PER_HA = RICE_CH4_MT * 1e9 / (RICE_AREA_MHA * 1e6)
line(f"Implied global mean: {RICE_CH4_PER_HA:.0f} kg CH4/ha/yr of harvested area")
for k, adopt, awd, cut, dose in [("low", 0.05, 0.55, 0.15, 1.0), ("base", 0.15, 0.55, 0.25, 0.75), ("high", 0.30, 0.60, 0.40, 0.5)]:
    # extra cut applies to the AWD residual of the adopted share
    mt = base_gt100 * 1e3 * adopt * awd * cut
    gyp_mt = RICE_AREA_MHA * adopt * dose
    # energy: 200 km haul + processing + spreading, per t CO2e at this scenario's own avoided CH4
    area_ha = RICE_AREA_MHA * 1e6 * adopt
    e_gj = area_ha * (dose * (200 * TRUCK_MJ_TKM / 1000 + PROC_GJ_T) + 0.05)
    eg = e_gj / (mt * 1e6)
    sc = ScaleCheck(mt / 1e3, eg)
    line(f"[{k}] adoption {adopt:.0%} of rice area, extra cut {cut:.0%} of AWD residual -> "
         f"{mt:.1f} Mt CO2e/yr GWP100 ({mt*GWP20_B/GWP100_B:.1f} GWP20); gypsum {gyp_mt:.1f} Mt/yr; "
         f"{eg:.2f} GJ/t CO2e, energy {sc.ej_per_year*1e3:.2f} PJ/yr = {sc.share_of_world_primary_energy:.5%} of world primary")
line("Claim (4) check: 0.81 Gt x 10-30% adoption x 10-25 pp extra = "
     f"{base_gt100*0.1*0.1*1e3:.0f}-{base_gt100*0.3*0.25*1e3:.0f} Mt CO2e/yr (arithmetic correct; "
     "upper end assumes 25 pp of the flooded baseline, i.e. ~45% of the AWD residual).")
line("Supply context (from memory, unverified): phosphogypsum generated ~150-280 Mt/yr globally; "
     "India ~10-15 Mt/yr; FGD gypsum ~ >100 Mt/yr (China dominant).")
