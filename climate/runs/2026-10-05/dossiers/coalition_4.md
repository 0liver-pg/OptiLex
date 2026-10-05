# Verified idea dossier: clinker process-CO2 phasedown per tonne of binder (coalition_4, patched)

**Verdict:** plausible, but only as a measure adopted by a club of countries. The physics is sound and prior art is PARTIAL. The economics need a second patch:
- The patched Phase 1 cannot be met by clinker substitution alone.
- Outside an emissions trading system (ETS), crediting stored CO2 in proportion to its process share (pro-rata crediting) raises the cost of each credited tonne.

**Tags:** [calc] executed script; [meas] measured or documented fact (includes enacted law and published proposals); [mod] modelled; [claim] company or agency statement; [assume] our assumption.

## 1 Claim
**Claim.** The instrument is a tradeable cap on unabated limestone process CO2 per tonne of binder:
- the cap falls 25% by 2035 (we recommend 15%, see §3) and 90% by 2050;
- it can be met only by substitution, by storage with pro-rata crediting and no enhanced oil recovery (EOR), or by separated calcination.

Under that cap, at least 50% of the remaining process CO2 is abated by 2045 at €150 or less per credited tonne, and pass-through stays under 1% of OECD build cost. The claim is falsified if either part fails.

**Scope.** Process CO2 only: 0.526 t per t clinker, 1.50 Gt/yr globally [calc]. Realistic scale is 0.13 Gt/yr by 2050 for an EU+US+OECD-Asia club [calc].

## 2 Mechanism
**Conventional core**
- LC3 (limestone calcined clay cement) substitution, at technology readiness level 9.
- Amine capture as at Brevik: operating since June 2025 [meas], 400 kt/yr nameplate [claim].
- Leilac separated calcination. Leilac-2 is about 100 kt/yr, with commissioning scheduled for mid-2026 [claim].

**Imported mechanism**
- A Kigali-style scheduled phasedown of one emission class.
- Montreal-style border measures.
- Storage licences that put process CO2 and removals first in the injection queue.

**Metric.** (clinker × measured process factor − credited stored tonnes) ÷ binder tonnes.

**Rules**
- Traded clinker carries its embedded intensity.
- Capture from mixed kiln flue gas is credited at the process share, 0.62 [calc].
- Separated calcination counts 100%.
- Each stored tonne gets one registry serial number.
- No public capex subsidy.

## 3 Evidence and verification
| Quantity | Value | Basis |
|---|---|---|
| Process CO2 per t binder | 0.374 at a clinker ratio of 0.71; 0.264 at 0.50 | [calc] `patch_coalition_4.py` |
| Floor vs real energy | Floor 0.333 GJ/t (separation 0.110 + real-gas compression 0.223). Real use 2.72–4.20 GJ/t, 8–13× the floor | [calc] `coalition_4.py` |
| Avoided cost (low / base / high) | €99 / €204 / €382 per t | [calc on assume] |
| Brevik anchor | Capex about €421m [claim, GCCSI 2026], which is €110/t of capital charge at 8% [calc]. Gassnova's estimate is about €100/t [mod] | |
| Crediting all mixed-flue capture as process CO2 | Would claim 81–145% abatement | [calc] `critic_coalition_4.py` |
| Cost per credited process tonne where fuel CO2 is unpriced | €161–242 at the claimed €100–150; €329 at base | [calc] `dossier_coalition_4_checks.py` |
| Phase 1 | A 25% cut needs a clinker ratio of 0.532. The IEA Net Zero (NZE) 2035 ratio of 0.61 gives 14.1%; the GCCA 2030 path gives 7.9% | [calc on mod] |
| Phase 1 gap at a ratio of 0.61 | 12.7% of process CO2 must be stored, about 64 Brevik-size plants across the club by 2035 | [calc] |
| Phase 2 | €23–34 per t binder at the claimed cost, €46–74 at base. That is 0.17–1.12% of a €2,000/m² build and 0.85–5.6% of a €400/m² build | [calc on assume] |
| Club in 2050 | 92 Mt/yr stored plus 39 Mt/yr from substitution. Capture including the fuel share is 149 Mt/yr, 30× Northern Lights Phase 2 (5 Mt/yr) | [calc; claim] |
| Storage budget | 150 Gt per century, 10.2% of the 1,460 Gt prudent limit | [calc on mod] |

**New findings**
1. No published trajectory supports a Phase 1 met by substitution alone. Either set Phase 1 at a 15% cut by 2035, or allow storage before 2035.
2. Pro-rata crediting penalises amine capture outside an ETS by about 1.6×. That favours Leilac-type kilns combined with LC3.

## 4 Prior art and what is new: PARTIAL
**Existing instruments**
- **EU ETS plus CBAM** already cap clinker CO2, credit only storage under the CCS Directive and adjust at the border.
- **The Commission's 17 July 2026 ETS proposal** [meas] would loosen this. It lowers the linear reduction factor to 3.7% for 2031–35 and 1.7% from 2036, and extends free allocation to 2040. This weakens the vetting stage's finding that the idea duplicates existing EU rules.
- **India's CCTS** requires cement emission-intensity cuts of 4.7–7.6% for FY2025–27 [meas].
- **California SB 596** requires a 40% cut by 2035 and net zero by 2045 [meas].

**What is new** is a combination of design choices, not a technology:
- the scope is process CO2 only, measured per tonne of binder;
- the instrument itself bans public subsidy, EOR and using storage to extend fossil power's life;
- compliance is tied to storage priority;
- stored tonnes are credited pro rata, with one serial number each.

## 5 Stakeholder map
| Group | Stance | Evidence |
|---|---|---|
| S1 NGOs | Split | CAN (2021) objects partly on evidence and endorses clay binders. The Climate Center (2022) backed cement CCS demonstrations but says CCS "should not be used for... enhanced oil recovery (EOR) under any circumstances". CIEL opposes CCS outright |
| S2 Scientists | Support | IPCC AR6 and the COP28 Global Stocktake back CCUS in hard-to-abate sectors |
| S3 Oil & gas | Split | Storage operators gain. US EOR firms oppose the exclusion |
| S4 Heavy industry | Split | GCCA relies on CCUS for 36% of its 2050 cuts [mod]. Brevik's first year of low-carbon evoZero cement was pre-sold [claim]. Cement Europe wants contracts for difference (CfDs). Inland kilns lose |
| S5 Utilities | Neutral | They lose only fossil-power CCS's place in the queue |
| S6 Workers | Split | Coastal jobs are kept. Inland kilns close, with no transition fund |
| S7 Governments | Split | No fiscal outlay. But the EU is moving toward relief for industry, and the US repealed an industry charge in 2025 |
| S8 Global South | Split | LC3 counts. But there is no Kigali-style grace period or fund, and build costs rise 0.85–5.6% [calc] |
| S9 Consumers | Neutral | The cost is embedded and under 1% of an EU build |
| S10 Investors/insurers | Support | They gain schedule certainty, and will price storage liability |
| S11 Communities | Split | The Satartia CO2 pipeline rupture (2020) forced about 292 evacuations [meas, PHMSA; not re-checked]. Host communities need benefit-sharing |

**Coalition logic**
- **Core coalition:** S2, S10, coastal S4 majors, EU storage operators and pragmatic S1 groups.
- **Levers to widen it:**
  - put substitution first (S1, S8);
  - add a grace period and use border revenue to fund LC3 (S8);
  - guarantee process CO2 access to storage rather than putting fossil power last (S3, S5).
- **Open tension.** CfDs funded from recycled revenue are still public money, which strains the no-subsidy promise to S1.

## 6 Risks
- **Measurement.** Measuring binder at the grinding plant misses supplementary cementitious materials (SCMs) added at ready-mix plants. The gap between GCCA's 0.63 baseline and the IEA's 0.71 shows how much this boundary matters. The process share depends on a kiln mass balance, and storage needs its own monitoring, reporting and verification (MRV).
- **Gaming.** Filler dilution: the metric can show a 14.1% cut while concrete improves only 5.5%, if binder per m³ has to rise 10% to keep strength [calc on assume]. Requiring standard-conformant cements closes this. Moving grinding offshore is a second route.
- **Political reversal.** The EU's 2026 relief proposals, and the US preference for 45Q subsidies over charges.
- **Leakage.** Imports from outside the club, and inland kiln closures.
- **Price effects.** EU ex-works cement rises 28–67% [calc on assume]. Storage liability is unresolved.

## 7 Cheapest falsifying experiment
**(a) Plant-level abatement curve.** Cover about 90 US, about 200 EU and the 7 California kilns.
- **Data sources:**
  - Global Energy Monitor's 2026 Global Cement and Concrete Tracker (substitution rates and production);
  - EPA GHGRP subpart H;
  - the EU ETS registry;
  - EPA Class VI and EU storage permits.
- **Cost model:** `coalition_4.py` with pro-rata crediting.

**(b) NGO elicitation.** A pre-registered elicitation with 12 NGOs on the exact rule text.

**Cost and duration:** $0–2k, 6 weeks.

**Kill thresholds, stated in advance**
- **K1.** Substitution achievable across the club by 2035, with clay sourced within 150 km [assume], is below 15% per t binder. This kills the substitution-first logic.
- **K2.** Less than 50% of the remaining process CO2 can be credited by 2045 at €150 or less per process tonne. This kills the idea outside ETS jurisdictions.
- **K3.** Half or more of the NGOs would campaign against it, or two or more of Bellona, CATF, The Climate Center and E3G oppose it.

## 8 Proof-of-concept path
1. **First step (under $2k):** run the §7 desk test and publish the model openly, framed as input to California's SB 596 strategy (https://ww2.arb.ca.gov/our-work/programs/net-zero-emissions-strategy-cement-sector).
2. **Partners** (all links checked):
   - Global Energy Monitor: https://globalenergymonitor.org/projects/global-cement-and-concrete-tracker/
   - EPFL LC3 project: https://lc3.ch
   - Bellona: https://bellona.org
   - The Climate Center: https://theclimatecenter.org
   - Climate Action Network (CAN): https://climatenetwork.org
   - GCCA Innovandi: https://gccassociation.org/innovandi/
   - Northern Lights: https://norlights.com
   - Global CCS Institute: https://www.globalccsinstitute.com
   - CATF (https://www.catf.us) is unverified because the site blocked the check.
3. **Funders:** ClimateWorks (https://www.climateworks.org), which published a 2019 California cement benchmarking report, and the Quadrature Climate Foundation (https://www.qcf.org). Open calls are unverified.

## 9 IP and publish decision
**Publish openly; do not file.** Policy and accounting rules cannot be patented, and they are worth something only if adopted.
- Release the rule text, the model and a protocol pre-registered on OSF.
- Report closure-risk results in aggregate rather than naming plants.

## 10 Open questions
- **Cost:** What scope and discount rate does Gassnova's estimate use? What are Brevik's measured GJ/t and capture rate, and Northern Lights' tariffs?
- **Subsidy:** Does the instrument bar stacking with US 45Q (about $85/t [assume])? Does CAN count CfDs funded from recycled revenue as subsidy?
- **Design:** Where should the binder boundary sit? When will Leilac-2 start up? Will the EU proposal pass? How fast can calcined-clay capacity be built?
- **Still unverified:** China's cement ETS details, the 8.7–15 Gt/yr CCS rates, and the cement tonnages by bloc.

---
Dossier file: `climate/runs/2026-10-05/scripts/dossier_coalition_4.md` (about 1,380 words, not counting URLs).

New checks this run, in `climate/runs/2026-10-05/scripts/dossier_coalition_4_checks.py`. I also re-ran `critic_coalition_4.py`, `patch_coalition_4.py` and `coalition_4.py`, and they reproduce the vetting numbers.
- **Phase 1 cannot be met by substitution alone.** The patched −25% by 2035 needs a clinker ratio of 0.532. Published paths give much less: IEA NZE 2035 gives −14.1% and GCCA 2030 gives −7.9%.
- **Pro-rata crediting is expensive outside an ETS.** Where fuel CO2 is unpriced, amine capture costs €161–329 per credited process tonne.
- **The low Brevik cost estimate rests on a low discount rate.** Brevik's capex, about €421m [claim, GCCSI 2026], is €110/t of capital charge alone at 8%. Gassnova's about €100/t therefore implies a low discount rate.
- **EU redundancy is weaker than the vetting stage found.** The 17 July 2026 ETS proposal lowers the reduction factor to 3.7% and then 1.7% (ICAP summary).
- **Filler dilution is a gaming risk** for the per-binder metric.

The Phase 1 and pro-rata findings make kill thresholds K1 and K2 likely to trigger unless Phase 1 is relaxed to −15%. Nothing in the repo was modified.