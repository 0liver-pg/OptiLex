# Verified idea dossier: methane-intensity quality differential in gas and LNG contracts (coalition_1)

**Verdict.** The idea is plausible, cheap and saves energy, but its reach is small: tens of Mt CO2e a year, not gigatonnes. Prior art is PARTIAL. This dossier covers the PATCHED design. Measurement is the weakest link. Public 2023–24 data, combined with an assumed uncertainty for the aircraft surveys, already put the Permian outside the settlement test's threshold.

## 1 Claim
**Claim.** Suppose EU, Japanese and Korean buyers adopt the patched clause. Then within three years, covered assets will cut their independently measured upstream methane intensity at least 0.1 pp/yr faster than matched assets without the clause. The average delivered price will rise by no more than the disclosed glide path, which is at most $0.043/MMBtu by year 5.

**Scope.** Upstream and midstream methane in LNG and in EU pipeline imports. Coal and LNG terminals are excluded.

## 2 Mechanism
- **Conventional core (TRL 9).** Leak detection and repair (LDAR), zero-bleed pneumatics, vapour recovery and an end to routine venting. IEA GMT 2026 estimates that more than 35 Mt CH4/yr can be avoided at no net cost [mod].
- **Imported mechanism.** The crude-oil quality escalator, or pipeline quality bank: a physical attribute re-prices every cargo symmetrically.
  - Unlike sulphur, methane intensity does not change what the gas itself is worth.
  - The value comes instead from EU Methane Regulation (MR) 2024/1787 [enacted]. It requires MRV equivalence from 2027, intensity reporting from 2028 and maximum intensity values from 2030.
- **Patched contract terms.**
  - **Slope.** $30/t CO2e. That is $894/t CH4, or $0.017/MMBtu for each 0.1 pp of intensity.
  - **Reference.** Starts at the supply's settled intensity in the year before signing, so the price differential is zero at signing. It then falls by 0.05 pp a year.
  - **Settlement per asset.** I_i = L5_i × F_b.
    - L5_i is the asset's own reported intensity under OGMP 2.0 Level 5.
    - F_b is the basin's top-down satellite estimate divided by the sum of the L5 emissions reported in that basin.
    - F_b is set to 1 unless it is significantly above 1 (the "gate").
  - **Integrity terms.**
    - Volume that cannot be traced to an asset pays a default set at the basin estimate's 90th percentile (P90).
    - The differential passes through to the liquefier's feedgas contracts.
    - Offset-based "carbon-neutral" claims are banned.

## 3 Evidence and verification
| Quantity | Value | Tag |
|---|---|---|
| Differential against a 0.5% reference, at 0.2 / 1.0 / 2.0% intensity | +0.051 / −0.085 / −0.255 $/MMBtu. That is +0.35 / −0.58 / −1.73% of the 2026 JKM forecast of $14.75 ([mod], EIA) | [calc] |
| Fixed 0.5% reference (original idea) | Not revenue-neutral: moves $1.68 bn/yr from exporters to buyers | [calc] on [assume] |
| Settlement bias | Old "higher of two methods" rule: +0.17 / +0.28 pp. Gated F_b: +0.03 / +0.05 pp | [calc] Monte Carlo |
| Reward to an operator for its own cut | Basin settlement: $0.3–3/t. Asset settlement: $15–37.5/t. Sources that L5 misses: $0 | [calc] |
| Net cost | $6.8/t CO2e (range −5.7 to 36.6) | [calc] on IEA capex [mod] |
| Energy | −0.82 GJ/t CO2e (net gain); thermodynamic floor 0 | [calc] |
| Scale, techno-economic model | 0.036 / 0.128 / 0.417 Gt/yr. The idea's claimed 1.0–2.5 Gt is overstated 8–20× | [calc] on [assume] |
| Scale allowing for clause-buyer share, 10-year adoption and no spillover | 0.006 / 0.025 / 0.078 Gt. After cargo reshuffling: 0.002 / 0.009 / 0.053 Gt | [calc] on [assume] |
| Permian intensity | 0.44% per barrel of oil equivalent (BOE) in 2024, aircraft plus model (S&P/Insight M) [meas]. 3.2% per unit of CH4 produced in 2023, TROPOMI satellite inversion (IMI) [meas] | sources |
| What drives the 7.3× Permian gap | Denominator 2.45× × year 1.22× × residual 2.4×. Comparing absolute masses (IMI 2019–23 mean vs S&P 2023) gives F_b ≈ 1.8 with an uncertainty (σ) of 31–37% | [calc]; oil output [memory], aircraft σ [assume] |
| Voluntary premia for certified gas | $0.01–0.05/MMBtu | [claim] |

**Correction to the vetting record.** It attributed the 7.3× Permian gap mainly to the aircraft survey seeing only large point sources. That is wrong: S&P observes more than 68% of emissions directly and models the smaller sources below its detection limit. The gap comes mostly from the different denominators (per BOE vs per unit of gas) and from a real difference between methods of about 1.8×.

**Scripts.**
- In `climate/runs/2026-10-05/scripts/`: `coalition_ideas.py`, `coalition_1.py`, `critic_coalition_1.py` and `patch_coalition_1.py`. All were re-run and reproduce their numbers.
- New: `climate/runs/2026-10-05/scripts/dossier_coalition_1_checks.py`, which holds the extensions above.

## 4 Prior art and what is new (PARTIAL)
**Closest existing work**
- **EU model clauses, Recommendation 2026/1834** [verified]. Information clauses only, with no price term, and they lean towards certificates.
- **EU MR maximum intensity from 2030.** A pass/fail limit only.
- **MiQ and responsibly sourced gas (RSG).** Voluntary premia paid in one direction only.
- **Pavilion's GHG statements, Cheniere's cargo emissions tags and the CLEAN initiative.** Disclosure only [memory].
- **Quality banks.** These are the imported mechanism itself.
- **Market commentary.** S&P (Oct 2024) expected price differentiation only around 2030. A non-exhaustive search of 2026 supply contracts (e.g. Cheniere–CPC) found no price term linked to intensity.

**What is new**
- a symmetric slope inside the contract price formula;
- a per-contract reference on a glide path;
- settlement as L5 × gated F_b;
- the P90 default for untraced volume and the feedgas pass-through.

## 5 Stakeholder map and coalition logic
| Group | Stance | Evidence |
|---|---|---|
| S1 Activists/NGOs | split | Methane NGOs backed the EU MR, and the offset ban meets CAN's red line. The anti-LNG wing sees the clause as legitimising LNG [memory] |
| S2 Scientists | support | COP28 para 28(f). Their concern is the uncertainty of satellite estimates |
| S3 Oil and gas | split | Low-intensity OGCI/OGDC firms gain. Independents helped kill the US Waste Emissions Charge (WEC); the clause's discount is 37–54% of the WEC rate [calc] |
| S4 Heavy industry | neutral | At most 1% of the retail gas price [calc] |
| S5 Utilities | support | Gives them a compliance path. Supply security is their red line |
| S6 Workers/unions | neutral | Leak repair adds jobs; wells shut in only where netbacks are below $1 |
| S7 Governments | split | The EU suspended importer penalties for 2027–29 [policy]; the US repealed the WEC |
| S8 Global South | split | Same discrimination objection as to CBAM; no finance for measurement |
| S9 Consumers | neutral | Invisible to households; at most $0.05/MMBtu |
| S10 Investors/insurers | support | Methane risk becomes priceable; greenwashing liability if measurements prove wrong |
| S11 Local communities | split | Benefits near wells; nothing for communities at terminals |

**Coalition logic**
- **Support:** S2, S5, S10, importing governments in S7, low-intensity S3, and methane-focused NGOs.
- **Opposition:** the coalition that killed the WEC, exporting governments, and the anti-LNG wings of S1, S8 and S11.

Leverage shrank in 2026, for two reasons:
- **Hormuz.** The strait has been largely closed since 28 February, removing about 20% of LNG supply [meas, EIA]. Only partial Qatari transits had resumed by late September.
- **EU penalties.** The EU has suspended importer penalties for 2027–29.

In this sellers' market, buyers can realistically ask for no more than "shadow" clauses (no money changes hands) before about 2029.

**Levers that widen the coalition**
- asset-level settlement, so clean operators in leaky basins are not penalised;
- measurement finance for S8;
- a ban on "clean LNG" marketing;
- conditions at LNG terminals.

## 6 Risks
- **Measurement.**
  - With σ at 31–37%, the gate lets 29–37% of emissions go unreported without detection [calc].
  - EPA has proposed suspending Subpart W reporting until 2034. It is not final, but if adopted it removes the US bottom-up data that F_b divides by.
  - MethaneSAT was lost in June 2025.
- **Gaming.**
  - A seller that delays a 0.5 pp cut until after signing earns $0.085/MMBtu, about $44M per 1 Mtpa contract over 10 years [calc]. The fix is to set the reference at the lower of the prior-year value and the 3-year trailing average.
  - An operator that under-reports its L5 data shifts cost onto other operators in its basin through F_b.
- **Political reversal.** The EU penalty suspension, the WEC repeal, and the EU's intensity methodology (due August 2027), which may conflict with the clause.
- **Leakage.** Low-leak cargoes can be steered to clause buyers. That cuts the base-case scale to 0.009 Gt.
- **Price effects.** At most 1.7% of the JKM price. In a tight market, sellers can raise the base price to cover any discount.

## 7 Cheapest falsifying experiment
- **Design.** Cover the Permian, Haynesville and Marcellus basins, using the same years (2023–24), the same scope and the same denominator (per unit of CH4 produced).
  - Compare IMI/TROPOMI satellite inversions with bottom-up totals:
    - Permian: S&P/Insight M.
    - Haynesville and Marcellus: Subpart W data, plus Carbon Mapper plume data, plus modelled small sources.
  - Compute F_b and its uncertainty for each basin.
  - Build a 2025–26 LNG trade matrix from GIIGNL data.
- **Cost and time.** About $500–1,500 of cloud compute (IMI costs about $20 per basin-month [claim]), plus 3–4 person-weeks.
- **Kill thresholds, set in advance.**
  - (a) The settlement design fails if F_b's 1σ uncertainty exceeds 25% in two or more basins. The Permian is already at 31–37%.
  - (b) The price signal fails if LNG demand from likely clause buyers does not exceed the supply that is already below 0.2% intensity.
  - (c) The voluntary route fails if certified-gas premia stay below $0.02/MMBtu.

## 8 Proof-of-concept path
1. **First step, under $2k.** Run the experiment in section 7 and publish an add-on clause to the EU model clauses (Recommendation 2026/1834).
   - Tools: [IMI](https://imi.readthedocs.io/en/latest/getting-started/faqs.html) (free on AWS) and [Carbon Mapper](https://data.carbonmapper.org).
   - Data: the [S&P Permian release](https://press.spglobal.com/2025-07-24-Methane-Emissions-Intensity-of-Permian-Basin-Declined-by-More-than-Half-in-Two-Years,-New-S-P-Global-Commodity-Insights-Analysis-Finds), plus [EPA FLIGHT](https://ghgdata.epa.gov) and [GIIGNL](https://giignl.org) (these two not verified).
2. **Partners.**
   - [OGMP 2.0 / UNEP IMEO](https://ogmpartnership.org/) (verified).
   - [MiQ](https://miq.org/) (verified).
   - [CATF](https://cdn.catf.us/wp-content/uploads/2026/06/11074009/CATF-EU-Methane-Regulation-Penalties-Paper.pdf): its June 2026 paper on EU MR penalties exists, but I did not open it.
   - EDF and the Oxford Institute for Energy Studies (not verified).
   - Pilot: one EU importer and one low-intensity exporter running a shadow clause on 2027 cargoes.
3. **Funders.**
   - [Global Methane Hub](https://www.globalmethanehub.org/) (verified).
   - ClimateWorks and Bloomberg Philanthropies (not verified).

## 9 IP and publish decision
Do not patent: this is a contract design with quality-bank prior art, and it is only valuable if adopted. Publish it under CC-BY before the consultation on the EU delegated act (due by 5 August 2027); that also creates defensive prior art. Run a paid search of supply-contract databases before claiming novelty.

## 10 Open questions
1. Can F_b reach σ ≤ 25% now that MethaneSAT is gone, using Tanager, GHGSat and TROPOMI?
2. Which denominator will the EU delegated act use? The choice shifts the Permian figure by 2.45×.
3. Will oil and gas producers accept a reference that resists gaming, and will Subpart W survive?
4. Do the trade shares and supplier intensities, which come from memory, hold?
5. Will a clause standard spill over to gas sold without the clause? The high-scale case assumes 8 Mt CH4 of spillover.
6. Should GWP20 be used? It would multiply the climate value by 2.8×.