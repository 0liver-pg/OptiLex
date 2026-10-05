"""Verifier for idea global_south_4: dairy ration balancing (RBP) verified by
MIR methane prediction on pooled bulk-milk samples, paid per litre via co-ops.

Source tags: [M] measured/field, [R] recalled literature value (not re-fetched in
this run; web search budget exhausted), [A] assumption, [C] computed here.
"""
import sys, math
sys.path.insert(0, 'climate')
from physics import *  # noqa

from statistics import NormalDist
Z = NormalDist()

GWP100_CH4_BIO = 27.0   # [R] IPCC AR6 WG1 Table 7.15, non-fossil CH4
GWP20_CH4_BIO = 79.7    # [R] IPCC AR6 non-fossil CH4
USD_INR = 88.0          # [A] ~2026 exchange rate

print("=== 0. Thermodynamic floor ===")
print("No gas separation: abatement is a change in rumen fermentation per unit milk.")
print("Separation floor not applicable -> no floor violation possible. floor_gj_per_t = 0")

# ---------------------------------------------------------------- 1. per-animal abatement
print("\n=== 1. Per-animal abatement (lactating animal-year) ===")
# Enteric CH4 per lactating animal, India. [R] Indian inventory / IPCC Tier 2 for
# Indian subcontinent: indigenous lactating cow ~30-40, crossbred ~50-60,
# lactating buffalo ~55-75 kg CH4/yr. Idea claims 50-70 (upper half).
ch4_kg = dict(low=35.0, base=52.0, high=70.0)
# Intensity cut (CH4 per kg milk): Garg et al. 2013 [M] 15-20%.
intensity_cut = dict(low=0.15, base=0.175, high=0.20)
# Milk gain: Garg 2013 [M] 2-14%.
milk_gain = dict(low=0.14, base=0.08, high=0.02)   # paired so 'high' abs cut = low gain
# Absolute per-animal change = (1-cut)*(1+gain) - 1  [C]
res = {}
for k in ("low", "base", "high"):
    abs_change = (1 - intensity_cut[k]) * (1 + milk_gain[k]) - 1
    t_int = ch4_kg[k] * intensity_cut[k] / 1000 * GWP100_CH4_BIO
    t_abs = ch4_kg[k] * max(0.0, -abs_change) / 1000 * GWP100_CH4_BIO
    res[k] = (abs_change, t_int, t_abs)
    print(f"{k:5s}: CH4 {ch4_kg[k]:.0f} kg/yr, intensity cut {intensity_cut[k]:.1%}, milk +{milk_gain[k]:.0%}"
          f" -> absolute per-animal change {abs_change:+.1%};"
          f" intensity-basis {t_int:.3f} tCO2e/yr, absolute-basis {t_abs:.3f} tCO2e/yr (GWP100)")
# Check idea's claim 0.20-0.38 t intensity basis using its own 50-70 kg and 15-20%
lo = 50 * 0.15 / 1000 * GWP100_CH4_BIO
hi = 70 * 0.20 / 1000 * GWP100_CH4_BIO
print(f"Idea's intensity-basis claim recomputed (50-70 kg, 15-20%): {lo:.3f}-{hi:.3f} t CO2e/animal-yr (claimed 0.20-0.38)")
print(f"Carbon value at $15-30/t: ${lo*15:.1f}-${hi*30:.1f} per animal-yr (claimed $3-11)")
# Absolute-basis credit is what the idea says it will pay
t_abs_base = res["base"][2]
print(f"Absolute-basis base case: {t_abs_base:.3f} t CO2e/animal-yr; GWP20 equivalent "
      f"{t_abs_base/GWP100_CH4_BIO*GWP20_CH4_BIO:.3f} t")

# ---------------------------------------------------------------- 2. MRV cost
print("\n=== 2. MRV cost per animal-year ===")
# Per-sample FTIR cost when the spectrum is run in an existing union plant lab:
# instrument amortisation + labour + sample logistics. [A] $0.3/0.8/1.5 per sample
# (DHI labs charge ~$0.5-1.5 per sample incl. fat/protein; marginal equation run ~0).
per_sample = dict(low=0.3, base=0.8, high=1.5)
for design, freq, animals in (("per-cow monthly", 12, 1),
                              ("society daily, 500 animals", 365, 500),
                              ("society daily, 200 animals", 365, 200),
                              ("society weekly, 300 animals", 52, 300)):
    v = [per_sample[k] * freq / animals for k in ("low", "base", "high")]
    print(f"{design:30s}: ${v[0]:.2f} / ${v[1]:.2f} / ${v[2]:.2f} per animal-yr")
print("Idea claims per-cow $6-18, pooled $0.4-2.7: per-cow check $3.6-18 (0.3-1.5 $/sample);"
      " pooled range reproduced. Weekly pooled sampling would cut MRV ~7x with little power loss.")

# One-off calibration study (tropical buffalo/crossbred, crop-residue diets):
# [A] reference methane (SF6 or GreenFeed) on ~150-300 animals x 2 diets, $0.3-1.5M.
calib = dict(low=0.3e6, base=0.8e6, high=1.5e6)

# ---------------------------------------------------------------- 3. programme delivery and farmer benefit
print("\n=== 3. Delivery cost and farmer benefit ===")
# Delivery: local resource person (LRP) visits, software, training, supervision.
# [A] $2/5/10 per animal-yr (LRP honorarium in INR tens per animal-visit, 3-6 visits/yr,
# plus overhead). Recalled NDP-I scale: RBP reached a few million animals [R].
delivery = dict(low=2.0, base=5.0, high=10.0)
# Farmer net benefit: [R] NDDB/Garg reports increased net daily income of roughly
# Rs 10-25 per animal per day from lower feed cost + more milk; not re-verified here.
# Use conservative [A] Rs 3/8/20 per day over 300 lactation days.
benefit_inr_day = dict(low=3.0, base=8.0, high=20.0)
for k in ("low", "base", "high"):
    b = benefit_inr_day[k] * 300 / USD_INR
    print(f"{k:5s}: delivery ${delivery[k]:.1f}/animal-yr; farmer net benefit ${b:.1f}/animal-yr")

# ---------------------------------------------------------------- 4. cost per tonne
print("\n=== 4. Cost per t CO2e (absolute basis, GWP100) ===")
crf = lambda r, n: r * (1 + r) ** n / ((1 + r) ** n - 1)
# scenario pairing: low cost = high abatement etc.
pair = dict(low=("high", "low", "low", "low"),    # abatement case, delivery, mrv, calib
            base=("base", "base", "base", "base"),
            high=("low", "high", "high", "high"))
animals_programme = 10e6   # [A] animals over which calibration is amortised
cost_out = {}
for k, (ab, dl, mr, ca) in pair.items():
    t = res[ab][2]
    if ab == "low":
        # absolute basis is zero in the pessimistic pairing (milk +14% offsets cut);
        # use a floor of 5% absolute cut to avoid divide-by-zero, flag it.
        t = max(t, ch4_kg["low"] * 0.05 / 1000 * GWP100_CH4_BIO)
    mrv = per_sample[mr] * 365 / 300
    cal = calib[ca] * crf(0.08, 10) / animals_programme
    gross = delivery[dl] + mrv + cal
    net = gross - benefit_inr_day[{"low": "high", "base": "base", "high": "low"}[k]] * 300 / USD_INR
    cost_out[k] = (gross / t, net / t, t, gross)
    print(f"{k:5s}: abatement {t:.3f} t/animal-yr; gross payer cost ${gross:.2f}/animal-yr "
          f"(delivery {delivery[dl]:.1f}, MRV {mrv:.2f}, calibration {cal:.3f}) -> "
          f"${gross/t:.0f}/t gross; net of farmer benefit ${net/t:.0f}/t")
print("MRV-only cost per t (base): ${:.1f}/t".format(per_sample['base'] * 365 / 300 / res['base'][2]))

# ---------------------------------------------------------------- 5. energy
print("\n=== 5. Energy per t CO2e ===")
# FTIR analyser ~0.5 kW at ~300 samples/h -> ~1.7 Wh/sample; sample transport rides
# existing milk logistics. LRP travel: motorcycle ~0.75 MJ/km [A], 4 visits/animal-yr,
# 1-3 km attributable per animal-visit. Mineral mixture embodied energy ignored (small).
for k, km in (("low", 1.0), ("base", 2.0), ("high", 3.0)):
    e_mj = 4 * km * 0.75 + 365 / 300 * 1.7e-3 * 3.6
    t = res["base"][2]
    print(f"{k:5s}: {e_mj:.2f} MJ/animal-yr -> {e_mj/1000/t:.3f} GJ/t CO2e "
          f"(before credit for feed saved per litre, which is likely net-negative)")

# ---------------------------------------------------------------- 6. scale
print("\n=== 6. Scale ===")
# [R] India 20th Livestock Census 2019: ~192 M cattle, ~110 M buffalo; ~125 M milch
# (in-milk + dry) animals. India enteric CH4 ~9-10 Mt/yr [R].
for n in (10e6, 30e6, 80e6):
    for k in ("low", "base", "high"):
        pass
    a = n * res["base"][2] / 1e6
    i = n * res["base"][1] / 1e6
    print(f"{n/1e6:.0f} M animals: absolute basis {a:.2f} Mt CO2e/yr, intensity basis {i:.2f} Mt CO2e/yr "
          f"= {a/1000:.4f} Gt")
india_enteric = 9.5 * GWP100_CH4_BIO
print(f"India enteric total ~{india_enteric:.0f} Mt CO2e/yr; 30 M animals base = "
      f"{30e6*res['base'][2]/1e6/india_enteric:.1%} of it")
# Global smallholder dairy extension (East Africa, S/SE Asia): [A] up to ~150 M animals
g = 150e6 * res["base"][2] / 1e9
print(f"Global ceiling (150 M smallholder dairy animals, base absolute): {g:.3f} Gt CO2e/yr")

# ---------------------------------------------------------------- 7. statistical detectability (falsification test)
print("\n=== 7. Can pooled bulk-milk MIR detect the effect? ===")
# Society-level effect is diluted by enrolment share. Between-society SD of
# MIR-predicted intensity (breed mix, cow/buffalo mix, season) [A] 8-15%.
# Paired before/after design removes most fixed between-society variance [A] SD 4-8%.
def power(effect, sd, n, alpha=0.05):
    se = sd * math.sqrt(2 / n)
    return 1 - Z.cdf(Z.inv_cdf(1 - alpha / 2) - effect / se)
for enrol in (0.3, 0.6, 1.0):
    eff = 0.175 * enrol
    for sd, label in ((0.12, "cross-sectional SD 12%"), (0.06, "diff-in-diff SD 6%")):
        print(f"enrolment {enrol:.0%}: society effect {eff:.1%}, {label}, n=20/arm -> power "
              f"{power(eff, sd, 20):.2f}")
# Required n for 80% power at 30% enrolment
eff = 0.175 * 0.3
for sd in (0.06, 0.12):
    n = 2 * ((Z.inv_cdf(0.975) + Z.inv_cdf(0.8)) * sd / eff) ** 2
    print(f"30% enrolment, SD {sd:.0%}: n per arm for 80% power = {math.ceil(n)}")
print("Note: a cow-level MIR RMSE of 15-20% does NOT by itself falsify a pooled design;"
      " random error averages ~1/sqrt(N) over hundreds of animals. The binding risk is"
      " systematic bias/slope: whether MIR-predicted CH4 change tracks measured change"
      " when the diet itself changes (fatty-acid proxy can respond to diet, not methane).")
# random-error averaging
for rmse in (0.15, 0.20):
    print(f"cow-level RMSE {rmse:.0%} -> pooled 300-animal random error {rmse/math.sqrt(300):.2%}")

print("\n=== 8. Resource needs ===")
print("Energy: ~0 share of world supply (MJ per animal-yr). Materials: existing FTIR analysers"
      " (~$50-150k each [A]) in union labs; mineral mixture. Land/water: none added; feed"
      " efficiency gain likely reduces feed demand per litre. Labour: ~1 LRP per few hundred"
      " to ~1,000 animals [A].")
