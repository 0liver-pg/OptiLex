# Verified idea dossier: an input-anchored HFC-23 balance, with VDF conversion as an optional offset (non_co2_6)

**Verdict:** plausible. The lever is small, real and very cheap. The VDF graft is weaker than claimed. Prior art is PARTIAL.

## 1 Claim
**Falsifiable claim.** Suppose eastern-China HCFC-22 plants ran under a plant-level HFC-23 balance with three features:
- it is anchored on independently reported chloroform and HF;
- the by-product ratio is continuously re-verified, and unaccounted HFC-23 is penalised at $5–10/kg;
- destruction and VDF conversion are equal compliance routes.

Then top-down emissions from eastern China, measured by AGAGE inversions, would fall within three years by at least half of their 3.5–4.3 Gg/yr excess over China's reports. The cost would be under $0.5/t CO2e.

**Scope.** Only by-product HFC-23 from HCFC-22 production: 0.03–0.12 Gt CO2e/yr, or 0.07–0.31% of fossil CO2.

## 2 Mechanism
- **Conventional core (TRL 9).** Kigali Article 2J(6) capture and destruction. Multilateral Fund (MLF) projects interpret "to the extent practicable" as emissions of at most 0.1% of HCFC-22 mass.
- **Imported mechanism, which now does the work: input-side material accountancy.**
  - CHCl3 + 2HF → CHClF2 + 2HCl fixes the inputs at 1.381 t chloroform and 0.463 t HF per t HCFC-22.
  - Expected HFC-23 equals the plant ratio times the output implied by those inputs.
  - Unaccounted kilograms pay a penalty, and plant-cluster inversions cross-check the result.
- **Optional offset (the original graft).** Co-pyrolysis CHF3 + CH4 → CH2=CF2 + HF + H2 makes VDF for PVDF battery binder. It is used only to substitute for VDF from the HCFC-142b route.

**Why revenue was demoted.** Eastern-China emissions averaged 5.1 ± 0.6 Gg/yr in 2021–23, against 5.8 ± 0.6 in 2015. Over the same period, reported abatement rose from 0% to 99.8% (Adam et al. 2024), and conversion was already permitted.

## 3 Evidence and verification
| Quantity | Value | Basis |
|---|---|---|
| Separation floor (90% vent) | 7.8e-7 GJ/t CO2e (about 6×10^5 below the DAC floor) | Computed |
| VDF reaction dH | +153 kJ/mol = 150 kJ/t CO2e | Computed |
| Destruction energy | 5–40 GJ/t HFC-23, at most 0.3 PJ/yr globally | Assumed |
| Global emissions | 14.0 ± 0.9 Gg (2023), against 2.8 Gg reported (2021) | Sourced, observation-based |
| Eastern-China excess | 3.5–4.3 Gg, about one-third of the gap | Sourced |
| Outside eastern Asia | 8.3 ± 1.7 Gg (59%), not attributable today | Sourced |
| Scale | 0.026 / 0.069 / 0.117 Gt CO2e/yr | Computed on assumed recovery shares |
| Social cost | −$0.02 / +$0.25 / +$0.44 per t CO2e; stress case $1.28 | Computed. MRV of $5–27M/yr is assumed; destruction at $1.02/kg is modelled (Zhao 2023) |
| Detection power of the balance | 80% power at ≥14–18% venting (ratio CV 5%) or ≥34–36% (CV 15%). A 20% commissioning bias drops P(detect 20% venting) to 0.04–0.05 | Modelled (Monte Carlo) |
| Shortfall needed to explain the excess | 12–36% of generation vented, or 12–36% of output undeclared | Computed; production of 0.6–1.0 Mt and a 2–3% ratio are assumed |
| VDF selectivity | 15.4–22.4% at 47–48% conversion, 1153 K, thermal (Yu et al.); about 43% only with a CBrF3 (halon) promoter (Han 2010) | Sourced, measured |
| VDF revenue | $420–1,430/t HFC-23 against $1,100–5,100 claimed; margin over opex −$60 to +$200 | Computed; price of $3–7k/t VDF assumed |

**What the table implies**
- The venting needed to explain the excess sits at the balance's detection floor. The scheme therefore works only if the by-product ratio is verified continuously (CV ≤ ~5%, no commissioning bias).
- The penalty must be $5–10/kg, not $1–2. A biased ratio cannot be out-penalised: it would take about $20/kg.

**Corrections to the patched idea**
- "Eastern China dominates the gap" is false.
- The HF increment is 0.013–0.034 t/t.
- The CDM credit equivalence is $117–234/kg.
- The 0.4–1.5 Gg from non-HCFC-22 sources is a global figure.
- The source paper is in *Commun. Earth Environ.* (doi:10.1038/s43247-024-01946-y), not *Nat. Commun.*

**Scripts** (in `climate/runs/2026-10-05/scripts/`):
- `non_co2_6_patched.py`: re-run, and it reproduces every figure above.
- `dossier_non_co2_6_checks.py`

## 4 Prior art and what is new: PARTIAL
- **Chemistry.**
  - Newcastle, 2006–10.
  - Catalytic versions from Zhejiang University of Technology (ZJUT), 2014–22, with unverified yields.
  - A 2024 paper in *J. Ind. Eng. Chem.*
- **Business case.**
  - A 2014 review co-authored by Juhua.
  - Patents CN104628514A and CN109748775B.
  - An engineering-scale conversion unit at Sinochem Lantian, announced in 2024. It claims "high target-product selectivity" but does not name the product.
- **Enforcement precedent.** CFC-11: Rigby 2019, then Park 2021 (from memory, not re-checked).
- **Plausibly new.** An input-anchored plant balance, a penalty well below CDM incentives, and substitution-only VDF. This is policy and MRV design, not technology.

## 5 Stakeholder map
| Group | Stance | Evidence |
|---|---|---|
| S1 Activists/NGOs | Split | Climate NGOs fought the CDM over-reward (the EU banned HFC-23 CERs in 2013). The anti-PFAS wing (ChemSec, Aug 2026) opposes ties to fluoropolymer demand |
| S2 Scientists | Support | Their inversions exposed the gap; they will want attribution first |
| S3 Oil & gas | Neutral | About 3 kt/yr of CH4 co-reactant |
| S4 Heavy industry | Conditional support | Compliant fluorochemical firms gain a level field, and under-reporters lose. EU PFAS rules put PVDF at risk |
| S5 Utilities | Neutral | At most 0.3 PJ/yr |
| S6 Workers | Neutral | No job losses; HF exposure is a safety issue |
| S7 Governments | Split | Shared treaty duty, but plant audits are sensitive and there is tension with EU PFAS policy |
| S8 Global South | Neutral | No North–South credits |
| S9 Consumers | Neutral | Destruction is about 1% of the HCFC-22 price |
| S10 Investors/insurers | Neutral | No credit asset; existing PFAS liability |
| S11 Local communities | Split | A new HF/TFE pyrolysis step at PFAS-contaminated sites; a destruction-only route avoids it |

**Coalition logic**
- No major industry loses.
- Frame the scheme as treaty enforcement, never as credits.
- Keep VDF optional and substitution-only.
- Concede the simple baseline: inversions plus enforcement already cut eastern China from 8.0 to 5.6 Gg (2018–23).

## 6 Risks
- **Technical.** Thermal selectivity is below 40%. TFE, a hazardous monomer, is a main co-product. Coke forms, and catalysts deactivate in HF.
- **MRV.**
  - Commissioning bias.
  - Integrated producers may make their own chloroform, which turns "independent" inputs back into self-reporting.
  - Off-book plants are invisible to the balance.
  - 59% of emissions are unmonitored.
- **Moral hazard.** Cheap, cents-per-tonne abatement could be cited to defer CO2 cuts.
- **Local safety.** HF, TFE, PFAS.
- **Rebound.** VDF could add to PVDF supply rather than substitute for it.

## 7 Cheapest falsifying experiment
**Design: a desk test of the input anchor.** Compare four sources:
- China's 2015–23 HCFC-22 production (Article 7 and MLF data);
- chloroform production and trade (UN Comtrade HS 290313);
- the eastern-China inversion series;
- where each plant gets its chloroform (in-house or bought in).

**Cost and duration.** $0–2k for one data set and about 4 analyst-weeks, over 6–8 weeks.

**Thresholds, stated in advance.**
- **Falsified** if more than half of capacity makes its own chloroform, or if chloroform-implied output cannot be bounded within ±10% (the signal is 12–36%).
- **Supported** otherwise. The comparison then shows whether venting or undeclared output dominates.

**Parallel free test of the offset.**
1. Build a Cantera plug-flow model with the NIST HFC and GRI-Mech 3.0 mechanisms, which Yu et al. matched.
2. Reproduce their 15.4% and 22.4%.
3. Scan operating conditions.
4. Drop the thermal route if none reaches ≥40% VDF selectivity at ≥50% conversion.

## 8 Proof-of-concept path
1. **Under $2k:** the desk test and the Cantera model, with public scripts. No hazardous work in-house.
2. **Partners:**
   - Bristol ACRG for inversions (https://www.bristol.ac.uk/chemistry/research/acrg/);
   - the Gosan/Kyungpook regional team;
   - Newcastle (Kennedy) or ZJUT (Han Wenfeng) for HF-capable catalytic trials;
   - EIA (https://eia-international.org/climate/) and IGSD (https://www.igsd.org) for advocacy.
3. **Funders:** the Multilateral Fund (https://www.multilateralfund.org), through Article 5 ozone units, and the Clean Cooling Collaborative (https://www.cleancoolingcollaborative.org). Data come from https://ozone.unep.org/countries/data-table. Open calls were not verified.

## 9 IP and publish decision
**Publish openly; do not file.**
- The chemistry is already published and patented in China.
- The novel part is MRV design, which is unpatentable and valuable only if adopted.
- Release a preprint and policy brief after the desk test, with aggregated results and no plant allegations.

## 10 Open questions
- What does the Sinochem unit make?
- Does China's 2021 notice credit conversion?
- How independent are the chloroform supplies?
- What is the by-product ratio's CV across operating modes?
- What is the source of the 8.3 Gg emitted outside eastern Asia (India reported zero)?
- What selectivity do ZJUT's catalysts actually reach?
- How does the EU PFAS restriction treat battery PVDF?

---
Dossier file: climate/runs/2026-10-05/scripts/dossier_non_co2_6.md (about 1,370 words).

New checks this run:
- **VDF selectivity.** I read the primary Yu et al. paper (NIST-hosted PDF). Without a promoter, CHF3+CH4 measures only 15.4–22.4% VDF selectivity, so the idea's 40–80% assumption is off by 2–5x and the offset roughly breaks even.
- **Eastern-China figures.** I confirmed the 2015 vs 2021–23 eastern-China emissions series and the journal from the cached Adam 2024 text.
- **Attribution.** To explain the excess, 12–36% of HFC-23 would have to be vented, or that much HCFC-22 output left undeclared. That is right at the balance's detection floor.

Web search budget was exhausted. Partner and funder URLs were checked by fetching them; open funding calls were not verified.