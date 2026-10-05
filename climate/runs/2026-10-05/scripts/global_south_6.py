"""Verifier for idea global_south_6: paid full rewetting of drained deep-peat plantation
blocks, MRV by InSAR subsidence against paired drained blocks.

Not a separation process -> the separation floor does not bind; we report the DAC-equivalent
floor only as a yardstick. Every input is labelled: [M] measured / primary source read this run,
[R] recalled literature value (not re-verified this run), [A] assumption with reasoning.
"""
import sys, math, random
sys.path.insert(0, 'climate')
from physics import *

random.seed(42)
C_TO_CO2 = 44.0 / 12.0

print("=" * 78)
print("1. Subsidence -> CO2 conversion (Hooijer et al. 2012, Biogeosciences 9:1053) [M]")
# Hooijer 2012 (read this run): BD 0.075 g/cm3 below 0.5 m, ~0.15 near surface; C 55 %; oxidation 92 %
def co2_per_ha_from_subsidence(s_cm_yr, ox, bd_kg_m3, c_frac):
    vol = s_cm_yr / 100 * 1e4             # m3/ha/yr
    return vol * ox * bd_kg_m3 * c_frac * C_TO_CO2 / 1e3   # t CO2/ha/yr
print(f"  Hooijer central (5 cm/yr, 92%, 75 kg/m3, 55% C): {co2_per_ha_from_subsidence(5,0.92,75,0.55):.1f} t CO2/ha/yr  (paper: 73)")
lo = co2_per_ha_from_subsidence(3, 0.75, 80, 0.55); hi = co2_per_ha_from_subsidence(5, 0.92, 100, 0.57)
print(f"  Idea's range 3-5 cm, 0.75-0.92 ox, 80-100 kg/m3, 55-57% C: {lo:.1f} - {hi:.1f} t CO2/ha/yr  (idea claims 36-96)")
print(f"  t CO2/ha per cm of subsidence at Hooijer values: {co2_per_ha_from_subsidence(1,0.92,75,0.55):.1f}")

print("\n2. Water-table dependence (Hooijer 2012 regressions) [M]")
# Plantation: CL = 21 + 69*WD (t CO2/ha/yr, WD in m below surface) ; drained forest: CL = 98*WD
plant = lambda wd: 21 + 69 * wd
forest = lambda wd: 98 * wd
for wd in (0.8, 0.7, 0.6, 0.4):
    print(f"  plantation WD {wd:.1f} m: {plant(wd):5.1f} t CO2/ha/yr")
print(f"  'best practice' 0.7->0.4 m saves {1-plant(0.4)/plant(0.7):.0%} (paper says <=20% vs current conditions)")
for wd in (0.05, 0.15, 0.30):
    print(f"  rewetted, natural-veg relation, mean WD {wd:.2f} m: residual {forest(wd):5.1f} t CO2/ha/yr")
print("  NOTE: plantation intercept 21 t at WD=0 => rewetting gives near-zero CO2 only if the")
print("  crop is removed AND mean water table stays within ~0.1 m of the surface year-round.")

print("\n3. Net abatement per hectare (low / base / high) ")
GWP_CH4 = GWP100["CH4_biogenic"]
cases = {
    #           drained baseline [t CO2/ha/yr], rewet mean WD [m], CH4 kg/ha/yr, leakage frac
    "low":  dict(base=40.0, wd=0.30, ch4=134, leak=0.50),   # IPCC 2013 WS Tier1 oil palm 11 tC [R]; poor rewet; CH4 upper of IPCC rewetted range [R]
    "base": dict(base=60.0, wd=0.15, ch4=41,  leak=0.30),   # mix of oil palm/Acacia mature plantations; IPCC rewetted tropical CH4 41 kg [R]
    "high": dict(base=73.0, wd=0.05, ch4=20,  leak=0.10),   # Hooijer post-yr-5 [M]; near-surface water table; low leakage
}
DOC_SAVE = 0.82 * C_TO_CO2 * 0.5   # [R] IPCC WS DOC 0.82 tC/ha/yr drained tropical; assume half avoided
net = {}
for k, c in cases.items():
    resid_co2 = forest(c["wd"])
    ch4_co2e = c["ch4"] / 1000 * GWP_CH4
    gross = c["base"] - resid_co2 - ch4_co2e + DOC_SAVE
    n = gross * (1 - c["leak"])
    net[k] = n
    print(f"  {k:4s}: drained {c['base']:.0f} - residual CO2 {resid_co2:.1f} - CH4 {ch4_co2e:.1f} + DOC {DOC_SAVE:.1f}"
          f" = gross {gross:.1f}; after leakage {c['leak']:.0%}: NET {n:.1f} t CO2e/ha/yr")
idea_lo, idea_hi = 35, 70
print(f"  Idea claims net 35-70 (no residual CO2, no leakage). Verified range: {net['low']:.1f} / {net['base']:.1f} / {net['high']:.1f}")

print("\n4. Idea's own break-even check (margin / abatement)")
print(f"  $300/ha / 70 t = ${300/70:.1f}/t ; $900/ha / 35 t = ${900/35:.1f}/t  (idea: $4-26)")

print("\n5. Full cost per tonne CO2e (low / base / high)")
def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)
cost_in = {
    #  forgone net margin $/ha/yr [A: FFB 15-20 t/ha x $170-220/t, net margin 10-30%; pulpwood lower],
    #  one-off rewetting capex $/ha [A: canal blocks + revegetation/paludiculture planting],
    #  O&M (block repair, fire patrol) $/ha/yr [A], MRV $/ha/yr [A: InSAR processing + dipwells + verification],
    #  overhead share (community benefit share, registry, intermediaries) [A], discount rate, life
    "low":  dict(margin=300,  capex=300,  om=20,  mrv=2,  ovh=0.10, r=0.06, n=25),
    "base": dict(margin=700,  capex=1200, om=50,  mrv=6,  ovh=0.20, r=0.08, n=20),
    "high": dict(margin=1300, capex=3000, om=100, mrv=15, ovh=0.30, r=0.10, n=15),
}
cost = {}
for k, c in cost_in.items():
    ann = c["capex"] * crf(c["r"], c["n"])
    per_ha = (c["margin"] + ann + c["om"] + c["mrv"]) / (1 - c["ovh"])
    cost[k] = per_ha
    print(f"  {k:4s}: margin {c['margin']} + capex {c['capex']}xCRF({c['r']},{c['n']})={ann:.0f} + O&M {c['om']} + MRV {c['mrv']}"
          f" / (1-{c['ovh']}) = ${per_ha:.0f}/ha/yr")
# pair cheap-cost with high abatement for 'low $/t' and vice versa
usd_t = {"low": cost["low"] / net["high"], "base": cost["base"] / net["base"], "high": cost["high"] / net["low"]}
for k in ("low", "base", "high"):
    print(f"  $/t CO2e {k}: {usd_t[k]:.1f}")
# Monte Carlo
samples = []
for _ in range(20000):
    base_e = random.triangular(40, 73, 60)
    wd = random.triangular(0.05, 0.35, 0.15)
    ch4 = random.triangular(7, 134, 41)
    leak = random.triangular(0.1, 0.6, 0.3)
    g = (base_e - forest(wd) - ch4 / 1000 * GWP_CH4 + DOC_SAVE) * (1 - leak)
    m = random.triangular(250, 1400, 700); cap = random.triangular(300, 3000, 1200)
    r = random.uniform(0.06, 0.10); n = random.choice([15, 20, 25])
    ovh = random.uniform(0.1, 0.3)
    c = (m + cap * crf(r, n) + random.uniform(20, 100) + random.uniform(2, 15)) / (1 - ovh)
    if g > 1: samples.append((c / g, g))
samples.sort()
q = lambda p: samples[int(p * len(samples))][0]
print(f"  Monte Carlo $/t: P10 {q(0.1):.1f}  P50 {q(0.5):.1f}  P90 {q(0.9):.1f}  (n={len(samples)})")
gs = sorted(s[1] for s in samples)
print(f"  Monte Carlo net t CO2e/ha/yr: P10 {gs[int(.1*len(gs))]:.1f}  P50 {gs[int(.5*len(gs))]:.1f}  P90 {gs[int(.9*len(gs))]:.1f}")

print("\n6. InSAR MRV signal-to-noise for a paired 100 ha block")
# Signal: drained 3-5 cm/yr vs rewetted residual subsidence (compaction lag + residual oxidation) 0.5-2 cm/yr
for label, s_dr, s_rw, sig_pix, coh_frac, sig_corr in [
    # [A] sigma_pix: per-pixel annual velocity std; coh_frac: fraction of 20x20 m cells coherent at C-band
    # under palm canopy (low; L-band NISAR/ALOS-2 better); sig_corr: spatially correlated residual (atmosphere,
    # seasonal peat swelling) not removed by averaging, per block-pair, cm/yr
    ("pessimistic C-band", 3.0, 2.0, 1.5, 0.05, 0.8),
    ("base", 4.0, 1.0, 1.0, 0.20, 0.4),
    ("optimistic L-band", 5.0, 0.5, 0.5, 0.60, 0.2),
]:
    n_px = 100e4 / (20 * 20) * coh_frac
    sig_block = math.sqrt(sig_corr ** 2 + sig_pix ** 2 / n_px)
    sig_diff = math.sqrt(2) * sig_block
    d = s_dr - s_rw
    print(f"  {label:18s}: diff {d:.1f} cm/yr, coherent px {n_px:.0f}, sigma_diff {sig_diff:.2f} cm/yr -> SNR {d/sig_diff:.1f};"
          f" tonnes uncertainty +/-{sig_diff*co2_per_ha_from_subsidence(1,0.92,75,0.55):.1f} t CO2/ha/yr")
# conversion uncertainty (BD of oxidising layer 0.075-0.15, ox share, C content)
rel = math.sqrt((0.25) ** 2 + (0.08) ** 2 + (0.03) ** 2)
print(f"  Conversion relative uncertainty (BD +/-25%, ox +/-8%, C +/-3%): +/-{rel:.0%} on tonnes")

print("\n7. Scale and resource needs")
ha_plant = 4.3e6  # Miettinen 2016 [R]
for mha in (0.5, 1.0, 2.0):
    print(f"  {mha} Mha: net {mha*1e6*net['low']/1e6:.0f} / {mha*1e6*net['base']/1e6:.0f} / {mha*1e6*net['high']/1e6:.0f} Mt CO2e/yr"
          f"  (idea claims {mha*35:.0f}-{mha*70:.0f})")
print(f"  Ceiling all 4.3 Mha (base): {ha_plant*net['base']/1e9:.3f} Gt CO2e/yr; high: {ha_plant*net['high']/1e9:.3f}")
print(f"  Share of total GHG ({TOTAL_GHG_GT_CO2E} Gt): 1 Mha base = {1e6*net['base']/1e9/TOTAL_GHG_GT_CO2E:.2%}")
# palm output forgone
for mha in (1.0, 2.0):
    palm_share = 0.72  # 3.1/4.3 Mha
    cpo = mha * palm_share * 3.5  # Mt CPO, [A] 3-4 t CPO/ha/yr on peat
    print(f"  {mha} Mha (72% palm, 3.5 t CPO/ha): forgone {cpo:.1f} Mt CPO/yr = {cpo/79:.1%} of world ~79 Mt [R]")
# energy
dac_floor = gj_per_tonne(min_separation_work(420e-6, 0.75))
s50 = ScaleCheck(0.05, 6.0)
print(f"  DAC-equivalent yardstick for 50 Mt: {s50.ej_per_year:.3f} EJ/yr at 6 GJ/t = {s50.share_of_world_primary_energy:.3%}"
      f" of world primary; floor {0.05*dac_floor:.4f} EJ/yr ({dac_floor:.2f} GJ/t)")
# own process energy: canal block ~ [A] 1 block per 20 ha, 15 t earth/timber + 2 t diesel-equivalent works 5 GJ
e_block = 5.0 / 20  # GJ/ha one-off
e_om = 0.05         # GJ/ha/yr patrol fuel [A]
for k in ("low", "base", "high"):
    print(f"  process energy {k}: {(e_block/20 + e_om)/net[k]:.4f} GJ/t CO2e  (vs DAC floor {dac_floor:.2f})")
print("  Separation floor: NOT APPLICABLE (avoided emission, no gas separation) -> no floor violation possible.")
print("  Land: 0 new ha (uses converted land; removes output). Water: retained rainfall, no withdrawals.")
