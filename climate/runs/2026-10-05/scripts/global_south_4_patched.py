"""Verifier for global_south_4_patched: co-op ration balancing (RBP) credited on an
absolute, herd-capped Tier-2 basis from per-animal ration records, audited (haircut-only)
by MIR methane predictions on a sealed weekly society milk sample.

Source tags: [M] measured/field (as reported by the idea card; primary not re-fetched in
this run because the session web-search budget is exhausted), [R] recalled literature
value, [P] earlier OptiLex research note in this scratchpad, [A] assumption, [C] computed.
"""
import sys, math
sys.path.insert(0, 'climate')
from physics import *  # noqa
from statistics import NormalDist
Z = NormalDist()

GWP = GWP100["CH4_biogenic"]       # 27, IPCC AR6 (verifier constant)
GWP20b = GWP20["CH4_biogenic"]     # 79.7
USD_INR = 88.0                     # [A] Oct 2026
crf = lambda r, n: r * (1 + r) ** n / ((1 + r) ** n - 1)

def hdr(s): print(f"\n=== {s} ===")

hdr("0. Thermodynamic floor")
print("No gas separation: abatement is a change in rumen fermentation and feed efficiency.")
print("floor_gj_per_t = 0 (no separation step); compare DAC floor "
      f"{gj_per_tonne(min_separation_work(420e-6, 0.75)):.2f} GJ/t and ambient-CH4 fan work in brief.")

# ------------------------------------------------------------------ 1. reproduce card
hdr("1. Reproduce the card's absolute-basis numbers")
def abs_cut(cut, gain): return 1 - (1 - cut) * (1 + gain)
card = {"low": (50, 0.15, 0.14), "mid": (60, 0.175, 0.08), "high": (70, 0.20, 0.02)}
card_t = {}
for k, (ch4, cut, g) in card.items():
    a = abs_cut(cut, g); card_t[k] = ch4 * a * GWP / 1000
    print(f"card {k:4s}: {ch4} kg CH4/yr, intensity -{cut:.1%}, milk +{g:.0%} -> absolute -{a:.1%}"
          f" -> {card_t[k]:.3f} t CO2e/animal-yr; ${card_t[k]*15:.2f}-{card_t[k]*30:.2f} at $15-30/t")
print(f"card scale: 10 M x low = {10e6*card_t['low']/1e6:.2f} Mt; 30 M x high = {30e6*card_t['high']/1e6:.2f} Mt;"
      f" central 10-30 M x mid = {10e6*card_t['mid']/1e6:.2f}-{30e6*card_t['mid']/1e6:.2f} Mt CO2e/yr")
print("-> card arithmetic reproduces (0.04-0.35 t, central ~0.18; 0.4-10 Mt; central 1.8-5.3 Mt).")

# ------------------------------------------------------------------ 2. own low/base/high
hdr("2. Own per-animal abatement (absolute, GWP100)")
# Enteric CH4 per in-milk animal, India [R]: IPCC 2006 Tier 1 Indian subcontinent dairy
# cattle 58, buffalo 55 kg/head/yr; Indian Tier-2 studies put indigenous cows ~30-40,
# crossbreds ~50-60, lactating buffalo ~55-75. Card's 50-70 is the upper half.
ch4 = dict(low=35.0, base=52.0, high=70.0)
cut = dict(low=0.15, base=0.175, high=0.20)          # [M] Garg 2013 per kg milk
gain = dict(low=0.14, base=0.08, high=0.02)          # [M] Garg 2013 milk +2-14% (paired pessimistically)
# Fraction of the animal-year the balanced ration is fed. RBP advises in-milk animals;
# calving interval in Indian smallholder herds ~14-18 months [R] -> lactation share ~0.6-0.75.
# The card applies the cut to whole-year CH4 (fraction 1.0).
active = dict(low=0.65, base=0.8, high=1.0)          # [A]
t_abs = {}
for k in ("low", "base", "high"):
    a = abs_cut(cut[k], gain[k])
    t_abs[k] = ch4[k] * a * active[k] * GWP / 1000
    print(f"{k:5s}: {ch4[k]:.0f} kg/yr x abs cut {a:.1%} x active {active[k]:.2f} -> {t_abs[k]:.3f} t CO2e/animal-yr"
          f" (GWP20 {t_abs[k]/GWP*GWP20b:.3f})")

# ------------------------------------------------------------------ 3. Tier-2 crediting model sanity
hdr("3. Does an IPCC Tier-2 model actually credit an absolute cut?")
# IPCC 2006 Vol4 Ch10 Tier 2 (energy-requirement driven):
#   NEm = 0.386 W^0.75 (lactating), NEl = milk*(1.47+0.40*fat), NEa=0 (stall-fed)
#   REM = 1.123 - 4.092e-3 DE + 1.126e-5 DE^2 - 25.4/DE
#   GE  = (NEm+NEl+NEp)/REM / (DE/100);  CH4 kg/yr = GE*Ym/100*365/55.65
# 2019 Refinement Table 10.12: dairy cows <5000 kg/yr milk, DE<=62% -> Ym 6.5% (single bin).
def tier2(W, milk, fat, DE, Ym, preg=0.10):
    NEm = 0.386 * W ** 0.75
    NEl = milk * (1.47 + 0.40 * fat)
    NEp = preg * NEm * 0.7                     # [A] pregnant ~70% of year-average
    REM = 1.123 - 4.092e-3 * DE + 1.126e-5 * DE ** 2 - 25.4 / DE
    GE = (NEm + NEl + NEp) / REM / (DE / 100)
    return GE * Ym / 100 * 365 / 55.65, GE
cases = {"crossbred cow": (350, 7.0, 4.0), "buffalo": (450, 6.0, 7.0)}   # [A] W kg, milk kg/d, fat %
for name, (W, milk, fat) in cases.items():
    c0, ge0 = tier2(W, milk, fat, 55, 6.5)
    for g in (0.02, 0.08, 0.14):
        c1, _ = tier2(W, milk * (1 + g), fat, 55, 6.5)
        # DE rise needed (Ym fixed by IPCC bin) for absolute cut equal to card base (-10.9%)
        target = c0 * (1 - abs_cut(0.175, g))
        DE = 55.0
        while tier2(W, milk * (1 + g), fat, DE, 6.5)[0] > target and DE < 75: DE += 0.05
        print(f"{name:13s} base {c0:.0f} kg CH4/yr (GE {ge0:.0f} MJ/d). milk +{g:.0%} at same DE/Ym:"
              f" {c1:.0f} kg ({c1/c0-1:+.1%}); to reach card intensity cut 17.5% needs DE 55->{DE:.1f}%"
              f" (or Ym 6.5->{6.5*target/c1:.2f}%)")
print("-> Standard Tier 2 (energy-requirement driven, single Ym bin) credits an absolute INCREASE"
      " when milk rises unless the ration records drive a DE rise of several points or a"
      " country-specific Ym-diet equation is used. The crediting model must be an intake-based"
      " variant (recorded DMI x GE x diet-specific Ym); its Ym equation is the load-bearing,"
      " untested element, and recorded DMI is a prescription, not measured intake.")

# ------------------------------------------------------------------ 4. MRV cost
hdr("4. MRV cost (weekly sealed society sample)")
per_sample = dict(low=0.5, base=0.9, high=1.5)        # [A] marginal FTIR run + logistics + seal
animals_per_soc = dict(low=500, base=300, high=200)   # [A] enrolled animals per society
# FTIR capex if a dedicated analyser is needed: $100k [A], 10 yr, 8%; 1,000 societies x 52 samples
ftir_capex_per_sample = 100e3 * crf(0.08, 10) / (1000 * 52)
print(f"dedicated FTIR capex share: ${ftir_capex_per_sample:.2f}/sample (inside the $0.5-1.5 range)")
mrv = {}
for k in ("low", "base", "high"):
    mrv[k] = 52 * per_sample[k] / animals_per_soc[k]
    print(f"{k:5s}: ${per_sample[k]}/sample x 52 / {animals_per_soc[k]} animals = ${mrv[k]:.3f}/animal-yr")
print(f"card claims $0.05-0.39 -> reproduced (52x0.5/500={52*0.5/500:.3f}; 52x1.5/200={52*1.5/200:.3f})")
print(f"per-cow monthly MIR: ${12*0.5:.0f}-{12*1.5:.0f}/animal-yr (card $6-18: reproduced)")
# Calibration study (tropical buffalo/crossbred, crop residue): 60-animal falsification test
# plus a production calibration of ~300 animals x 2 diets with GreenFeed/SF6 [A].
calib = dict(low=0.2e6, base=0.6e6, high=1.5e6)
# Tier-2 Ym validation / methodology approval / registry: [A] $0.2-1 M one-off
method = dict(low=0.2e6, base=0.5e6, high=1.0e6)

# ------------------------------------------------------------------ 5. Cost per tonne
hdr("5. Cost per t CO2e (absolute basis)")
# Delivery: LRP visits, software, training, supervision [A] $2/5/10 per animal-yr.
delivery = dict(low=2.0, base=5.0, high=10.0)
# Farmer benefit [P]: NDDB NDP-I RBP average +Rs25.5/day/animal net income (programme-reported).
# Use Rs 8/15/25.5 x 270 in-milk days to stay conservative.
benefit = {k: v * 270 / USD_INR for k, v in dict(low=8.0, base=15.0, high=25.5).items()}
N_PROG = dict(low=30e6, base=20e6, high=10e6)        # animals over which one-offs amortise
pair = dict(low=("high", "low"), base=("base", "base"), high=("low", "high"))
cost = {}
for k, (ab, c) in pair.items():
    t = t_abs[ab]
    oneoff = (calib[c] + method[c]) * crf(0.08, 10) / N_PROG[c]
    admin = 0.05 * t * 25                       # [A] 5% registry/payment admin on a $25/t payment
    gross = delivery[c] + mrv[c] + oneoff + admin
    carbon_only = mrv[c] + oneoff + admin
    net = gross - benefit[{"low": "high", "base": "base", "high": "low"}[k]]
    cost[k] = gross / t
    print(f"{k:5s}: abatement {t:.3f} t/animal-yr | delivery {delivery[c]:.2f} + MRV {mrv[c]:.3f}"
          f" + one-offs {oneoff:.3f} + admin {admin:.3f} = ${gross:.2f}/animal-yr"
          f" -> gross ${gross/t:.0f}/t; carbon-layer only ${carbon_only/t:.1f}/t;"
          f" net of farmer benefit ${net/t:.0f}/t")
print(f"Farmer benefit ${benefit['low']:.0f}-{benefit['high']:.0f}/animal-yr vs carbon value at $15-30/t"
      f" ${t_abs['low']*15:.2f}-{t_abs['high']*30:.2f}/animal-yr ->"
      f" carbon = {t_abs['low']*15/benefit['high']*100:.1f}-{t_abs['high']*30/benefit['low']*100:.0f}% of private gain")
print("Additionality flag: RBP pays farmers far more than carbon does, so it fails strict offset"
      " additionality; the card's framing (insetting / results-based livelihood payment) is the honest one.")

# ------------------------------------------------------------------ 6. Energy per tonne
hdr("6. Energy per t CO2e")
for k, km in (("low", 1.0), ("base", 2.0), ("high", 3.0)):
    e_mj = 4 * km * 0.75 + 52 / 300 * 2e-3 * 3.6    # [A] 4 LRP visits x km x 0.75 MJ/km moped; FTIR ~2 Wh/sample
    print(f"{k:5s}: {e_mj:.2f} MJ/animal-yr -> {e_mj/1000/t_abs['base']:.3f} GJ/t CO2e"
          " (before feed saved per litre, likely net negative)")

# ------------------------------------------------------------------ 7. Scale
hdr("7. Scale")
print("NDP-I RBP reached 2.865 M animals [P]; 10-30 M = 3.5-10.5x that.")
for n in (2.865e6, 10e6, 30e6):
    print(f"{n/1e6:5.1f} M animals: {n*t_abs['low']/1e6:.2f} / {n*t_abs['base']/1e6:.2f} / {n*t_abs['high']/1e6:.2f} Mt CO2e/yr")
india_ent = 9.5 * GWP          # [R] India enteric CH4 ~9-10 Mt/yr
print(f"India enteric ~{india_ent:.0f} Mt CO2e/yr; 30 M base = {30e6*t_abs['base']/1e6/india_ent:.1%} of it")
for n in (150e6,):
    print(f"Global smallholder ceiling {n/1e6:.0f} M animals: {n*t_abs['base']/1e9:.4f} Gt (base),"
          f" {n*t_abs['high']/1e9:.4f} Gt (high) = {n*t_abs['base']/1e9/TOTAL_GHG_GT_CO2E:.3%} of global GHG")

# ------------------------------------------------------------------ 8. Audit signal
hdr("8. Pooled MIR audit signal and detectability")
for enrol in (0.6, 0.8):
    for g, c in ((0.02, 0.20), (0.08, 0.175), (0.14, 0.15)):
        w = enrol * (1 + g) / (enrol * (1 + g) + (1 - enrol))     # litre-weighted share
        print(f"enrol {enrol:.0%}, milk +{g:.0%}, cut {c:.1%}: litre-weighted share {w:.2f} -> pooled signal {w*c:.1%}"
              f" (card: {enrol*c:.1%})")
# Species-mix residual after volume-split correction: [A] buffalo vs cow MIR-intensity gap 20-40%,
# correction removes 70-90% of a 10-20 pt share swing.
for gap in (0.2, 0.4):
    for swing in (0.10, 0.20):
        for rem in (0.7, 0.9):
            r = gap * swing * (1 - rem)
            if rem == 0.7 and swing == 0.20 and gap == 0.4 or rem == 0.9 and swing == 0.10 and gap == 0.2:
                print(f"species gap {gap:.0%}, share swing {swing:.0%}, correction {rem:.0%}: residual {r:.1%}")
# Seasonal diet (green fodder vs dry residue) shifts predicted intensity [A] SD 5-10%; needs
# control (non-enrolled) societies -> diff-in-diff power for one society-year vs tolerance.
def power(eff, sd, n): return 1 - Z.cdf(Z.inv_cdf(0.975) - eff / (sd * math.sqrt(2 / n)))
for sd in (0.03, 0.06):
    for n in (1, 5, 20):
        print(f"DiD SD {sd:.0%}, n={n:2d} societies/arm, effect 9%: power {power(0.09, sd, n):.2f}")
print("-> Per-society haircuts are noisy unless the between-season residual SD is <=3%; audit is"
      " credible at cluster (10-20 society) level, which the card does not specify.")

hdr("9. Resource needs")
print("Energy ~0 (MJ/animal-yr; 0% of world supply). Materials: existing union FTIR analysers"
      " (~$100k each if new), tamper-evident sample vials, mineral mixture. Land/water: none added;"
      " better feed conversion lowers feed per litre. Labour: LRPs (~1 per few hundred to 1,000 animals),"
      " one-off reference-methane calibration on ~60-300 animals.")

hdr("SUMMARY")
print(f"floor 0 GJ/t; energy ~{4*1*0.75/1000/t_abs['base']:.3f}-{4*3*0.75/1000/t_abs['base']:.3f} GJ/t;"
      f" cost gross ${cost['low']:.0f}/{cost['base']:.0f}/{cost['high']:.0f} per t (low/base/high);"
      f" net of farmer benefit negative; scale {10e6*t_abs['low']/1e9:.4f}-{30e6*t_abs['high']/1e9:.4f} Gt/yr"
      f" (base 10-30 M: {10e6*t_abs['base']/1e9:.4f}-{30e6*t_abs['base']/1e9:.4f})")
