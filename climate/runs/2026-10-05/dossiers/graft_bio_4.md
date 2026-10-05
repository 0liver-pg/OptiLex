# Verified idea dossier: graft_bio_4, repair-cycle DAC sorbent

**Verdict:** plausible and not fatal. TRL 3 [A]. The novelty is narrowed to the in-place, multi-cycle step. **Labels:** [C] computed by script; [S] primary source checked this session; [S*] from an upstream agent, not re-checked; [M] recalled from memory, unverified; [A] assumption.

## 1. Claim
In PEI-impregnated structured DAC contactors, stripping the oxidised amine and re-coating fresh PEI *inside the intact contactor* keeps at least 90% of fresh working capacity after two reloads. That is the level needed for an 8-20% cut in gross cost per tonne against whole-sorbent replacement. **Scope:** impregnated PEI on monolith or laminate supports only. It excludes grafted aminosilane sorbents (Climeworks Gen-1/2 [M]) and liquid-KOH DAC (1PointFive). It is a cost lever on removal for residual emissions, not a new removal pathway.

## 2. Mechanism
- **Conventional core:** solid-amine temperature-vacuum swing DAC, regenerated at 80-100 °C.
- **Graft:** the photosystem II D1 repair cycle. The plant replaces only the damaged protein and keeps the rest of the complex.
- **Mechanism:** oxidation attacks the amine, not the support. Flow water, then ethanol, through the contactor to strip the spent PEI. Then flow fresh PEI through and vacuum-dry it in place. The support becomes a permanent scaffold and the amine a consumable.
- **What decides the value:** recovered capacity *r* and the number of support reuses *N*.

## 3. Evidence and verification
- **Floor:** 0.465 GJ/t [C, verifier]. Reload is not a separation, so its energy adds above the floor and cannot breach it. Real solid DAC uses 5-10 GJ/t [M, McQueen 2021, mostly modelled or pilot data], a second-law efficiency of 4.7-9.3% [C].
- **Sorbent replacement cost:** $69-1,038/t CO2 [C on A: 1-1.5 mol/kg, 3-6 cycles/day, 1-2 yr life, $20-50/kg].
- **Reload energy:** 0.010-0.24 GJ/t, at most 3.5% of 7 GJ/t [C]. Energy is not the constraint.
- **New check (this dossier):** the upstream model charged a lower *r* only against the sorbent line. A contactor with 15% less capacity also spreads capex, O&M, fan power and sensible heat over 15% fewer tonnes. With that included (a = 0.25, overhead 12%):

| r | Sorbent line only, N=5 | Total, N=5 (low/base/high case) | Total, N=3 |
|---|---|---|---|
| 1.00 | 48% | 21 / 23 / 27% | 16 / 19 / 22% |
| 0.90 | 42% | 13 / 15 / 20% | 8 / 10 / 13% |
| 0.85 | 39% | 8 / 11 / 15% | 3 / 5 / 8% |
| 0.80 | 35% | 2 / 5 / 10% | -3 / -1 / 3% |

- **Breakeven r** rises from 0.52-0.62 to 0.72-0.83. If each support's first fill is fresh, it is 0.65-0.74 [C].
- **Base-case cost:** at r = 0.90 (similar to Li 2026), $592/t falls to $502/t, a 15% cut [C on A]. At r = 0.85, base-case energy rises from 7.0 to 8.2 GJ/t [C; heat of adsorption 80 kJ/mol, M].
- **Degradation:** in Thakkar 2024, PEI-silica pellets at about 1 mmol/g degraded "ca. 94% within 24 h" at 120 °C in ambient air [S]. Degradation in dry CO2 was 30-40% higher than in wet CO2 [S]. Urea formation therefore matters, and the test needs humid ageing.
- **Scale:** 0.5 Gt/yr by 2050 [A, within IEA NZE's roughly 1 Gt, M] needs 3.5 EJ, or 0.56% of world primary energy [C]. Amine make-up is 1.4-8.3 Mt/yr per Gt [C], 2-14x the ethyleneamines market [M]. Embodied emissions are 0.3-3.3% of captured CO2 [C on A]. **There is no realized field data for this idea.** Every cost figure is modelled.
- **Scripts:** in `climate/runs/2026-10-05/scripts/`: `graft_bio_4.py`, `patch_graft_bio_4.py` and `dossier_graft_bio_4.py`.

## 4. Prior art: PARTIAL
- **Coralli 2023, IJMS** [S]: methanol extraction of degraded PEI from silica. The aim was to find uses for the spent PEI, not to reuse the support.
- **Li et al. 2026, Energy & Fuels** [S]: the closest work.
  - Recovered the silica by pyrolysis at 500-600 °C. Mesopores contracted 13% and pore volume fell 10%.
  - Re-impregnated at 45 wt% (47 wt% fresh). Capacity was about 10% lower.
  - Ran one cycle only and left multiple cycles to "further studies".
- **SCR catalyst rejuvenation** [M]: a commercial precedent for keeping the support and replacing only the active phase.
- **Wang et al. 2025, IECR** [S, title and authors]: tackles fibre-sorbent degradation through support and material choices. The upstream agent wrongly credited this to "Shu/Lively".
- **New:** solvent-only, in-place, multi-cycle reload of a structured DAC contactor.
- **Not checked:** patents. Google Patents returned a CAPTCHA, OpenAlex hit its rate limit and the WebSearch budget was used up.

## 5. Stakeholder map
The evidence comes from the upstream agent [S*], fetched 2026-10-05. Stances on this specific idea are inferred.

| ID | Stance | Basis |
|---|---|---|
| S1 | Split | CAN (2021) says DACCS has "no place" as a substitute for cuts. Moderates accept removal for residual emissions. |
| S2 | Support | IPCC AR6 says CDR is needed for residuals. Orca ran at about 600 of its 4,000 t/yr nameplate (measured), so a cheap test of an unmeasured cost driver is welcome. |
| S3 | Support (inferred) | The 45Q DAC credit of $180/t survived in 2025, so cheaper DAC widens margins. Oxy's own liquid process gains nothing. |
| S4 | Support | A recurring amine market and cheaper removal for process emissions. Module suppliers lose. |
| S5 | Neutral | Load is unchanged, slightly higher if r < 1. |
| S6 | Neutral | Minor extra O&M labour; solvent exposure needs controls. |
| S7 | Support | Lower fiscal cost per tonne under 45Q. |
| S8 | Split | Baum 2024: engineered CDR rated the highest mitigation-deterrence risk. |
| S9 | Neutral | No visible price effect. |
| S10 | Support | cdr.fyi: 50.5 Mt contracted, 1.7 Mt delivered. A predictable operating cost lowers risk. |
| S11 | Split | New on-site handling of ethanol and spent amine: 14-83 kt/yr of solvent cycled per Mt CO2 [C]. |

**Coalition logic:** stances follow each group's view of DAC, not of the reload step. Three commitments that cost the idea nothing widen the coalition:
- a closed water-ethanol loop, with the spent-amine waste characterised (S6, S11);
- dedicated geologic storage only, with no EOR (S1, S8);
- framing the output as removal for residual emissions, consistent with COP28 para 28(e).

## 6. Risks
- **Technical:** urea-linked PEI may not wash out, which caps N. Re-coating in place risks uneven loading, surface skins and higher pressure drop. Silica ages under steam. Below r = 0.85 the idea is close to breakeven.
- **MRV:** tonnes are metered at the product stream, but net-removal accounting must subtract the amine's embodied emissions (0.3-3.3%) and solvent losses.
- **Moral hazard:** cheaper DAC strengthens the "removal instead of reduction" argument. Mitigation: residual-only framing and no EOR.
- **Local safety:** flammable ethanol inside large contactors. The oxidised-amine waste is uncharacterised and may contain nitrosamine precursors [A].
- **Rebound and obsolescence:** 1.4-8.3 Mt/yr of amine per Gt could raise amine prices for other users. Oxidation-resistant amines (Zhao 2025, Han 2026 [S*]) could shrink the payoff.

## 7. Cheapest falsifying experiment
A two-arm test, about 6 weeks, under $15k [A].
- **Arm A:** repeat Li 2026 ex situ as the baseline (r ≈ 0.90).
- **Arm B:** a 5-10 cm impregnated-PEI monolith coupon in a sealed flow cell.
  - Age it under humid 400 ppm CO2 cycling at 80-100 °C, plus one block at 110 °C in air, until it is at about 50% of fresh capacity.
  - Strip by flow-through (water, then ethanol), re-coat by flow-through and vacuum-dry. Run 5 cycles.
  - Measure loading slice by slice (TGA), pressure drop, working capacity at 400 ppm and 50% RH, BET surface area and pore volume, and nitrogen in the wash.

**Pre-stated thresholds:**
- **Go:** r ≥ 0.90 after reload 2.
- **Kill:** any one of these:
  - r < 0.85 (total saving 3-15%, near breakeven at N = 3);
  - axial loading spread above ±15%;
  - pressure-drop rise above 20%;
  - pore-volume loss above 5% per cycle.

## 8. Proof-of-concept path
1. **Step 0 (about $0):** a patent search on [Espacenet](https://worldwide.espacenet.com) and [Lens](https://www.lens.org) covering Global Thermostat/Corning, Climeworks and Svante. Publish the r/N cost model.
2. **Step 1 (under $2k [A]):** a gravimetric screen on ceramic honeycomb coupons. Age them in an oven, weigh slices for mass lost on stripping and gained on re-coating, and measure pressure drop with a manometer. Add about 8 contract TGA runs and 2 BET runs (about $1.3k [A]).
3. **Step 2:** run Arms A and B with an academic partner. Candidates:
   - the Snape/Stevens group at Nottingham (Li 2026);
   - the Fabbri group at Bologna (Coralli 2023);
   - the Thakkar et al. authors (accelerated-ageing protocol).
4. **Funders and community:**
   - [Frontier Track 1](https://frontierclimate.com/apply): R&D grants for results "within ~18 months", rolling, with data shared openly [S].
   - [Innovate UK](https://www.ukri.org/councils/innovate-uk/).
   - The [CO2RE](https://co2re.org) greenhouse-gas-removal hub, active in 2026 [S].
   - [AirMiners](https://airminers.com) and [Activate](https://activate.org).

## 9. IP and publish decision
**Publish; do not file.** The ex-situ chemistry is already published, and in-situ SCR rejuvenation makes a patent on the in-place step likely to fail as obvious. Frontier grants require open data, which also serves S2 and S10. **Exception:** if Arm B produces a non-obvious method for uniform re-coating, file a UK priority application *before* disclosing it, because the UK has no general grace period.

## 10. Open questions
1. Is oxidised, urea-linked PEI soluble in water or ethanol?
2. Which DAC developers use impregnated PEI on structured supports at scale?
3. What is the real cost split between amine and support (a = 0.04-0.40)?
4. How fast does r fall with each reload?
5. Is the spent wash toxic?
6. Do existing patents cover in-situ refurbishment?