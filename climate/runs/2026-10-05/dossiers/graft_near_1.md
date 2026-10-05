# Verified idea dossier: audited fenceline monitoring at HCFC-22 plants (graft_near_1)

Labels: **[C]** computed by an executed script; **[S]** primary source checked; **[A]** assumption; **[M]** recollection, not verified.

## 1 Claim
A perimeter network of air-sampling canisters at each HCFC-22 plant, calibrated with a tracer gas and audited independently, can do two things. It can tell a plant with an HFC-23 emission factor (EF) of about 0.2% of output from one at 1% or more, within one two-week period. And it can do so for under $0.50/t CO2e. That would make Kigali's existing destruction duty enforceable against the ~11 Gg/yr (~160 Mt CO2e) gap between measured and reported emissions.

**Scope:** HFC-23 by-product only, 0.04-0.17 Gt CO2e/yr, or 0.1-0.3% of global GHG [C]. It is a cheap, high-certainty niche lever, not a primary solution.

## 2 Mechanism
- **Core:** thermal destruction of HFC-23 (TRL 9).
  - Kigali Art. 2J(6) requires destruction "to the extent practicable" from 2020.
  - Art. 7(3 ter) already requires HFC-23 emissions to be reported per facility [S, ozone.unep.org, 5 Oct 2026].
- **Graft:** the US refinery fenceline rule (40 CFR 63.658) [S].
  - It uses 14-day samples, an action level of 9 µg/m3 on the difference between sampling sites, and root-cause analysis.
  - Canisters replace the rule's sorbent tubes, because CHF3 boils at -82 °C.
- **Patched design:**
  - 8-12 samplers on a ring 1-1.5 km out, with tracer released at several vents.
  - Sealed duplicate samples, of which a random 10-20% go to an independent lab.
  - One unannounced mobile tracer survey a year.
  - A numeric "practicable" standard of EF 0.3%.
  - Reconciliation against atmospheric inversions, as a backstop only.
  - Hosting inside the Multilateral Fund's (MLF) production verification [M].

## 3 Evidence and verification
Scripts are in `climate/runs/2026-10-05/scripts/`:
- `graft_near_1.py` and `critic_hfc23_recon.py`: both re-run, and the outputs reproduced.
- `dossier_hfc23_check.py`: my extensions.

| Quantity | Value | Basis |
|---|---|---|
| Global HFC-23 emissions, 2023 | 14.0 ± 0.9 Gg/yr | [S] inversion, Adam et al. 2024 |
| Gap vs reports | 11.2 Gg = 163 Mt CO2e (142-177) | [C]; compares 2023 measured with 2021 reported |
| Abated EF at one plant | 0.19% (0.13-0.24%) | [S] measured, Rust et al. 2024 |
| Physical floor | 0, because destruction is exothermic (ΔH ≈ -275 kJ/mol) | [C] |
| Removing HFC-23 from air instead | 216 GJ/t CO2e in fan work alone | [C]: only prevention is viable |
| Energy | 1.4-10 MJ/t CO2e | [C] from [A] fuel use |
| Total cost (low / base / high) | $0.08 / $0.44 / $4.97 per t | [C] from [A] 25-60 plants and 30-95% of the gap closed |
| Audited monitoring | $5.4-23M/yr: $0.03-0.14/t, or $0.11-0.47/t if only 30% of the gap closes | [C] from [A] |
| Two-week signal at 2 km | Average plant (29-47 kt/yr): 390-630 ppt at EF 0.19% vs 2,070-3,300 ppt at EF 1%; background 37 ppt | [C] plume model; background [A] |
| Share of emission estimates within ±50% | 78% on a 500 m ring; 100% on a 1.5 km ring; 84% with a neighbouring source. Telling EF 0.2% from 1%: 3% false alarms, 1.5% misses | [C] Monte Carlo, flat terrain |
| Reconciliation backstop | Flags a hidden 2 Gg source 10-14% of the time, and a 3 Gg source 29-43% | [C] |
| Split-sample audit | Tampering in 4 of 26 periods is caught 34-59% of the time; tampering in all 26, 94-100% | [C] |
| EF 0.3% threshold | Permits ~3.5 Gg globally: a 75% cut, vs 84% at 0.19% | [C] |
| Destruction cost | $22-438 per t HCFC-22 | [C] from [A] |

**Verdict:** no physical violation. Enforcement, not physics, is the constraint. The original idea overstated plume signals by about 2x and understated monitoring cost by 1.5-2x. Its claim that destruction costs under $1/t is [M].

## 4 Prior art and what is new: PARTIAL
- **Rust et al., Nature 2024:** a one-off measurement at one facility, with no compliance regime.
- **Adam et al. 2024; Stanley et al. 2020:** show the gap, but cannot attribute it to a plant.
- **Liang et al., Environ Pollut 2024** (doi 10.1016/j.envpol.2024.124609; new this run): research sampling near Chinese fluorochemical sites detects HFC-23.
- **The refinery rule and its 2024 HON extension:** the regulatory template, but for benzene and ethylene oxide.
- **Mobile tracer dispersion (Mønster, Fredenslund):** validated, but for methane.

**What is new:** a routine perimeter network with an action level and an independent audit, tied to Art. 2J(6) and 7(3 ter). The novelty is institutional. The search budget ran out, so these remain unchecked:
- Montreal Protocol meeting (MOP) and MLF Executive Committee (ExCom) papers.
- Reports from EIA, the Environmental Investigation Agency.
- The rules of China's Ministry of Ecology and Environment (MEE).

## 5 Stakeholder map

| Group | Stance | Evidence |
|---|---|---|
| S1 activists | Support | Not CCS, an offset or removal. Fenceline data is an established environmental-justice tool. Support flips if the scheme is credited. |
| S2 scientists | Support | Comes from the measurement community (Rust 2024). CFC-11 precedent: detection led to enforcement. Wants validation first. |
| S3 oil & gas | Neutral | No HCFC-22 stake. Precedent risk for methane fees. |
| S4 heavy industry | Split | Compliant producers gain a level field. Violators pay $22-438/t HCFC-22. The US chemical sector won relief from the HON rule (Jul 2025). |
| S5 utilities | Neutral | No exposure. |
| S6 workers | Neutral | No closures. |
| S7 governments | Split | All accepted Kigali (China in 2021). Producer states object to outside monitoring on sovereignty grounds. |
| S8 Global South | Split | Acceptable if MLF-funded and nationally owned. |
| S9 consumers | Neutral | No visible price. |
| S10 investors | Neutral | Disclosure risk at violators. |
| S11 communities | Support | Public data is a standing demand. |

**Coalition logic:** the scheme enforces a duty every Party already accepted. Opposition is concentrated in non-compliant producers and their host states. Four rules hold the coalition together:
1. It is a compliance instrument, never a credit.
2. Data stays nationally owned, with an independent audit.
3. The MLF funds it.
4. Validation comes before enforcement.

## 6 Risks
- **Technical:** chemical parks with several sources, and complex terrain, widen errors. Specialist analysis capacity is short: about 12,700 samples a year [C/A].
- **Monitoring, reporting and verification:**
  - Split samples miss bias introduced before the split, such as moved samplers. Only unannounced surveys catch that.
  - Unregistered production lines are never ringed.
- **Moral hazard:**
  - Crediting would revive the perverse incentive seen under the Clean Development Mechanism (CDM). HFC-23 projects earned 38% of CDM credits (CERs) by 2013, and the EU banned them.
  - Mitigation deterrence is minor, but a 0.3% threshold legitimises about 3.5 Gg/yr.
- **Local safety:**
  - The tracer must be inert, non-toxic and low-GWP, which rules out SF6.
  - The local issue near fluoropolymer plants is PFAS (ES&T 2026: 52 plants, about 14 million people nearby). Scope creep toward PFAS could harden S4's opposition.
- **Rebound:** feedstock emissions run at about 3.6% of production, not the 0.5% once assumed (Reimann et al., Nat Commun 2026). A fixed EF on growing output still means growing emissions.

## 7 Cheapest falsifying experiment
- **Design:** 3 months at one plant with a known EF.
  - 6-8 weekly canisters on a ring 1-1.5 km out.
  - Tracer released at several vents.
  - Blinded analysis, with spiked canisters sent to an independent lab.
- **Success thresholds, stated in advance:**
  - at least 80% of estimates within ±50%;
  - EF 0.2% and 1% separated with no more than 5% false alarms and 5% misses;
  - no misattribution to the wrong source;
  - spiked samples recovered within ±20%.
- **Cost:** $30-160k [A, at $400-1,500 per sample], or less if a lab contributes analysis in kind. The original idea's "tens of thousands of dollars" is the low end.
- **Duration:** about 5 months.
- **Separate go/no-go:** whether ExCom and one producer Party accept independent analysis of split samples.

## 8 Proof-of-concept path
**First steps, under $2k:**
1. Re-run the Monte Carlo with ERA5 meteorology and EPA's AERMOD model (both free) at 3-5 real sites from the ES&T plant inventory.
2. Test CHF3 recovery at a commercial lab running the standard TO-15 canister method (~$1-1.5k [A]).
3. Write a 4-page note mapping the scheme onto Art. 7(3 ter) reporting.

**Partners:**
- Empa (https://www.empa.ch)
- TNO (https://www.tno.nl/en/)
- EIA (https://eia-international.org/climate/)
- IGSD (https://www.igsd.org/)
- The MLF (https://www.multilateralfund.org/)
- The Ozone Secretariat (https://ozone.unep.org/)

**Funders:**
- Clean Cooling Collaborative (https://www.cleancoolingcollaborative.org/)
- ClimateWorks (https://www.climateworks.org/)

These sites resolve, but whether these bodies would take the project on is unconfirmed.

## 9 IP and publish decision
There is nothing to patent, and adoption is the goal. Publish openly as a preprint with a pre-registered protocol. Keep the scheme out of crediting.

## 10 Open questions
1. Does MLF production verification exist in the assumed form, and could it host this?
2. Have earlier MOP decisions proposed facility-level checks?
3. Are Art. 7(3 ter) reports public?
4. What does China's MEE already require?
5. How much of the gap comes from HCFC-22 lines?
6. Do the traps used in TO-15 analysis retain CHF3?
7. Which threshold is achievable? At EF 0.5% the cut is only 58% [C].
8. Could the same canisters track feedstock ozone-depleting substances?