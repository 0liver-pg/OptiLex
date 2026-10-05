# OptiLex idea engine: climate solutions that the most parties can accept

**Run date:** 5 October 2026.

**How to read the numbers.** Every figure carries one of these tags:
- **[calc]**: an OptiLex calculation that was actually executed (the verifier `climate/physics.py` plus one script per idea).
- **[meas]**: sourced, and measured at a real plant, field trial or in the atmosphere.
- **[mod]**: sourced, but a modelled estimate.
- **[claim]**: a company statement.
- **[assume]**: our own assumption.

The scripts are in [`scripts/`](scripts/) (run them from the repo root with `.venv/bin/python`). The cross-checks behind this report are in [`scripts/final_report_checks.py`](scripts/final_report_checks.py).

---

## 1. Short answer

### Can greenhouse-gas capture be efficient?

Yes. The thermodynamic minimum work is small for every source [calc]:

| Stream | Minimum separation work |
|---|---|
| Air, 420 ppm CO2, 75% capture | 0.47 GJ/t CO2 (129 kWh/t) |
| Gas-turbine flue gas, 4% CO2, 90% capture | 0.22 GJ/t |
| Coal flue gas, 12%, 90% capture | 0.16 GJ/t |
| Cement kiln, 25%, 90% capture | 0.11 GJ/t |
| Fermentation, gas processing, ammonia (SMR) process streams | about 0; only compression, with a floor of about 0.25–0.3 GJ/t |

Even capturing all 37.4 Gt of fossil CO2 from air would take only about 2.8% of world primary energy at the floor. Physics does not rule capture out. It does show where today's efficiency is good and where it is poor.

**Point sources are already close to their practical limit.** Amine capture runs at roughly 27–43% second-law efficiency, counting separation plus compression.
- Boundary Dam 3 gives an upper bound of about 1.0–1.3 GJ of electricity per tonne for CO2 capture, against a floor of about 0.42 GJ/t [calc, from measured derate and capture data].
- A perfect solvent would save at most about $10–15/t out of a total of $60–120/t.
- Cost is driven by capital spending (capex), capacity factor, storage and revenue risk, not by thermodynamics.
- Raising capture from 90% to 99% lifts the floor by only about 5% (0.219 to 0.231 GJ/t for gas-turbine flue gas) [calc]. When real plants capture less, that is a design and economic choice, not a physical limit.

**Direct air capture (DAC) is efficient on paper but not yet in practice.**
- Engineering designs reach about 5–12% second-law efficiency. The Carbon Engineering design is 7.8% on an exergy basis [mod]. Climeworks' nominal Gen2 figures give 4.9% on an energy basis and 12.3% on exergy [calc on claim].
- The flagship plant does worse. Climeworks' Mammoth reported 675 t in the first half of 2026 against a nameplate of 36,000 t/yr, about 3.75% utilisation [claim, reported by Bloomberg: https://www.energyconnects.com/news/renewables/2026/september/carbon-removal-pioneer-climeworks-increases-co2-capture-sixfold/].
- At 6–10 GJ/t, capturing 1 Gt/yr would take 1.0–1.6% of world primary energy [calc].
- DAC is therefore suited to residual emissions, not to cleaning up fossil emissions in bulk.

**Methane is a different problem.**
- The floor for separating methane from ambient air (1.93 ppm) is tiny, about 0.07 GJ/t CO2e [calc].
- Moving that much air costs 263 GJ/t CH4 in fan work alone. That is 8.8 GJ/t CO2e on a 100-year GWP basis, worse than DAC [calc].
- Methane therefore has to be stopped at the source, or oxidised where it is concentrated. Mine ventilation air at about 0.2% methane or more can sustain its own oxidation.
- Releasing chlorine or iron salts into the open air to destroy methane faces two problems. One model needs 1,250 Tg/yr of chlorine, about 20 times current world chlorine production, to cut methane by 14%, and it also cuts the atmosphere's natural cleaning agent, OH, by 28% (Horowitz 2026 [mod], https://acp.copernicus.org/articles/26/9471/2026/). It is also blocked politically by governance concerns.

### What this implies

The practical question is not whether capture can be efficient. It is who pays for the capital and the storage, and who checks that the tonnes are real. The cheapest tonnes that leave major industries intact are non-CO2 emissions stopped at source:

- **Fossil methane.** The IEA estimates more than 35 Mt CH4/yr could be avoided at no net cost at 2025 prices [mod] (https://www.iea.org/reports/global-methane-tracker-2026/key-findings). That is about 1.04 Gt CO2e, 16 times all CCS capacity operating today [calc], and the recovered gas is sold.
- **HFC-23.** Atmospheric measurements put global emissions at 14.0 Gg in 2023, about 5 times what countries report [meas] (Adam et al. 2024, doi:10.1038/s43247-024-01946-y). Closing the gap is worth about 0.16 Gt CO2e at a cost of cents per tonne [calc].
- **Industrial N2O.** Abating the N2O from China's adipic-acid plants, about 76 Mt CO2e/yr, would cost $19–304M a year [calc].

After these come concentrated CO2 streams: gas processing, ethanol, ammonia and cement process CO2. Capturing these costs about $15–35/t where the stream is nearly pure [mod, IEA 2019].

### The engine's best candidates

These are the 8 ideas on the Pareto front, out of 24 vetted (sections 3 and 4):

1. **A methane-intensity price term in gas and LNG contracts.** Base cost $6.8/t CO2e; 0.13 Gt/yr.
2. **An HFC-23 enforcement pair.** Both act on the same emissions gap, so count them once:
   - audited fenceline monitoring at HCFC-22 plants: $0.44/t, 0.11 Gt/yr;
   - an HFC-23 mass balance anchored on plant inputs, with conversion to VDF as an optional extra: $0.25/t, 0.07 Gt/yr.
3. **A phasedown of clinker process CO2 that can only be met by geological storage.** $235/t; 0.13 Gt/yr by 2050 if adopted by a club of the EU, US and OECD Asia; technology readiness level (TRL) 8.
4. **Two niche storage designs:**
   - sequencing CO2 storage around Smackover lithium brine units: $38/t, 0.01 Gt/yr;
   - dissolving CO2 into Permian saltwater-disposal wells: $55/t, 0.016 Gt/yr.
5. **Two cost levers for DAC:**
   - repairing the amine sorbent in place: about a 15% cut in gross cost, if the repaired sorbent recovers at least 90% of its capacity;
   - a grid-charged hot-water heat store: saves about 1%.

### Honest limits

- **The engine did not find "the solution."**
  - Counted once, the abatement ideas on the front total about 0.4 Gt CO2e/yr, about 0.75% of global greenhouse-gas emissions [calc].
  - What the engine found are enforcement, contract and siting mechanisms that release tonnes known technology can already abate.
  - No idea scored better than PARTIAL on novelty. That matches the evidence that most real progress comes from recombining known ideas.
- **Nothing here satisfies everyone. These groups bear the cost:**
  - HCFC-22 producers that do not comply, and the states that host them.
  - Gas exporters with leaky supply chains, and producers in basins where gas is cheap or even negatively priced. Waha averaged −$2.38/MMBtu in 2026 [src].
  - Cement buyers: +€23–129 per tonne of cement [calc]. The EU ex-works price could rise 28–67% [calc on assumed prices].
  - Taxpayers. Norway's Longship CCS project was NOK 22bn state-funded out of NOK 34bn, and the US 45Q credit pays $180/t for DAC.
  - The few voluntary buyers of carbon removal.
- **"Doesn't hurt major industries" cannot hold for fossil-fuel volumes.**
  - IPCC 1.5°C pathways cut coal, oil and gas use by about 95%, 60% and 45% by 2050 [mod].
  - CCS cannot support unabated fossil use indefinitely. The prudent geological storage limit, about 1,460 Gt (Gidden 2025 [mod], https://www.nature.com/articles/s41586-025-09423-y), is only about 39 years of today's fossil CO2 [calc].
  - Realistic CCS growth is 0.07–0.37 Gt/yr by 2030 (Kazlou 2024 [mod], https://www.nature.com/articles/s41558-024-02104-0).
  - Incumbents can keep their assets and skills: storage as a service, low-methane gas, geothermal drilling, capture of process CO2. They cannot keep today's volumes.
- **Some red lines rule options out:**
  - Mainstream climate NGOs, as set out in Climate Action Network's 2021 position, oppose:
    - using CO2 for enhanced oil recovery (EOR);
    - public money for fossil-linked CCS;
    - offsets that replace emission cuts.

    So only CCS restricted to process emissions, with no EOR, can win them.
  - Solar radiation modification is a hard red line for organised NGOs and many Global South voices: more than 650 academics and more than 2,000 organisations back the call for non-use.

---

## 2. What the map shows

### The known levers closest to win-win today

| Lever | Best measured evidence | Already supported by | Binding bottleneck |
|---|---|---|---|
| Oil and gas methane (leak detection and repair, ending venting and flaring) | Permian methane intensity fell from 5.2% to 3.2% (2019–23, satellite inversion). New Mexico fell from 4.5% to 2.1% under state rules [meas] | OGCI; the OGDC (55+ companies, about 40% of oil output); API backs direct regulation; scientists; the EU | Measurement and enforcement. Recovered gas is worth $6/t CO2e at $3.5/MMBtu but $19 at $11 [calc]. Negative prices at Waha. The US methane fee was repealed in 2025, and EU import penalties are paused |
| HFC-23 destruction (Kigali Art. 2J(6)) | A plant with abatement measured 0.19% emission factor (Rust 2024). Global emissions 14.0 Gg against about 2.8 Gg reported [meas] | 172 Parties plus the EU; US industry backed the AIM Act | Verification. 59% of emissions come from outside eastern Asia and cannot be traced to plants |
| Industrial N2O | Adipic acid plants have achieved more than 90% abatement since the 1990s [meas]; $0.25–4/t [mod] | Cost to heavy industry is negligible | No revenue stream; gaming of offset credits under the UN Clean Development Mechanism (CDM) |
| CCS on concentrated streams | Sleipner about 1 Mt/yr since 1996. Quest stored 5 Mt in under 5 years. CF Donaldsonville up to 2 Mt/yr from July 2025. Brevik cement plant designed for 400 kt/yr from June 2025 [meas/claim] | Oil and gas, heavy industry, unions and governments (45Q, UK, Norway). NGOs tolerate it for process CO2 only | Storage: Gorgon injected 25% of its reservoir CO2 against an 80% condition; the ADM well leak. Dependence on subsidy. Opposition to EOR. A ban on eminent domain for CO2 pipelines (South Dakota, 2025) |
| Capture on power plants | Boundary Dam 3 captured 721 kt in 2025, 72% of nameplate. Petra Nova captured 92.4% while online [meas] | Utilities and unions | Capex: $700–2,250 per t/yr of capacity, or $67–211/t annualised [calc]. Capacity factor. Revenue: Petra Nova was mothballed when oil prices fell |
| Clinker substitution (LC3) | Commercial, but less than 1% of cement [meas] | Heavy industry; Global South producers | Scale-up and building standards |
| Firm power from oilfield skills | Fervo: drilling time per well down 75% and cost per foot down 70% (2022–25) [company data, SEC S-1/A]. 658 MW of binding power purchase agreements. About $7,000/kW for the first plant | Oil and gas (Shell is an offtaker), utilities, bipartisan US support | First-of-a-kind capex is 2.3 times the target. Reservoir decline is unproven at 100 MW |
| Green premium per product | Less than 1% of the price of a car or building [mod] | Consumers barely affected | The premium is 9–18% of a 6% carmaker profit margin [calc], so it lands on the manufacturer |

### Policy evidence

US politics in 2025 shows a pattern:
- Instruments that pay incumbents survived and grew. The 45Q credit kept $85/t for point sources and $180/t for DAC, and EOR now earns the same rate.
- Fees charged to incumbents and consumers died. The US methane Waste Emissions Charge was repealed under the Congressional Review Act. Canada dropped its consumer carbon price on 1 April 2025.
- On the other side, Washington voters kept cap-and-invest by 62 to 38.

Confound: this is one law and one political cycle. It supports "who receives the money matters." It does not establish a general rule.

### The binding bottlenecks

1. **Capital and utilisation, not energy.** At the floor, point-source capture energy costs $6–8/t, against $67–211/t of capex. DAC's capital charge is $274/t even at a 95% capacity factor, using Stratos's roughly $1.3bn reported project cost as a proxy [calc].
2. **Storage.**
   - Pressure and well integrity.
   - A finite "prudent" storage budget.
   - About 1,430 injection wells per Gt/yr [mod].
3. **Measurement, reporting and verification (MRV).** Inventories are wrong by large factors:
   - HFC-23: 5 times reported.
   - Open dumps: 5.3 times.
   - Chinese industrial N2O: 2 times the GAINS model's estimate.
   - Permian methane: 0.44% by aircraft against 3.2% by satellite. This last gap is a difference in method (aircraft miss small and diffuse leaks), not a contradiction.
4. **Revenue durability.**
   - Fees can be reversed within one political cycle.
   - The market for durable carbon removal is effectively one buyer: Microsoft made about 90% of 2025 purchases.
   - Deliveries are 3.4% of contracts: 1.7 Mt delivered against 50.5 Mt contracted [src, https://www.cdr.fyi/].
5. **Deployment rate.** 64 Mt/yr of CCS is operating, 0.17% of fossil CO2. Historically, 88% of planned CCS projects failed.

---

## 3. Engine output

### How scoring worked

- **Generation.** Each idea is a conventional core plus one imported mechanism, seeded from the map's open problems across eight families.
- **Physics and techno-economic analysis.** Every idea ran through an executed Python script against the verifier: a floor check, energy use, low/base/high cost, and realistic scale. A critic script then checked it, and a patch script fixed it. Verdicts are strong, plausible or implausible. No surviving idea breaks a thermodynamic floor.
- **Prior art.**
  - IMPORT means the idea exists already and the value lies in deploying it.
  - PARTIAL means the core is published and only the specific combination is plausibly new.
  - No idea scored above PARTIAL.
- **Coalition score (out of 11).** Each of the 11 stakeholder groups was given a stance from documented positions. Sources include the Climate Action Network's 2021 position, API, OGCI, IPCC AR6, the COP28 text and the Baum 2024 30-country survey. Groups on record as opposing an idea are listed. Caveat: the dossiers refined their stance tables after scoring, and I could not reproduce every score exactly. Read them as ±0.5.
- **No LLM quality or novelty ranking was used.**
- **The Pareto front.**
  - An idea is on the front if no other idea beats it on all four axes: lower base cost, larger scale, higher TRL and higher coalition score. The front is limited to ideas with no documented opposition.
  - My re-run reproduces all 8 front labels [calc].
  - The green-iron compact is also unbeaten on the four axes, but it is excluded because ironmaking workers oppose moving ironmaking abroad.
- **Caveats on the axes.**
  - The cost column mixes abatement (dollars per tonne CO2e avoided, GWP100) with removal (dollars per tonne captured, gross). Net DAC costs are higher: the heat-buffer idea is about $700 per net tonne on France's grid and about $1,520 on Germany's.
  - The scale figures for the two DAC levers are the size of the DAC fleet they would apply to. They add no tonnes of their own.
  - Cheap non-CO2 ideas beat CO2 storage ideas across families. The front is a screen, not a ranking of importance.

### Scored table

| # | Idea | Family (core + import) | Prior art | Physics | $/t CO2e base (low–high) | Gt/yr | TRL | Coalition /11 | Opposed by | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lithium-unit storage sequencing (Smackover) | Class VI storage phased around lithium and bromine brine units | PARTIAL | plausible | 38.1 (12.1–163.5) | 0.01 | 7 | 7.75 | – | front |
| 2 | Gas-plant CO2 dissolved in Permian disposal wells | Carbfix-style dissolution into produced-water disposal wells | IMPORT | plausible | 55 (12–330) | 0.016 | 4 | 6.5 | – | front |
| 3 | Audited fenceline monitoring at HCFC-22 plants | Refinery fenceline rule applied to HFC-23 enforcement | PARTIAL | strong | 0.444 (0.081–4.97) | 0.114 | 6 | 6.25 | – | front |
| 4 | Hooded tailrace degassing at tropical dams | Hydropower methane capture plus an oxidiser of the kind used for mine ventilation air | PARTIAL | plausible | 23.9 (8–68.6) | 0.0015 | 4 | 5.5 | – | alive |
| 5 | Sulfate-recharged alternate wetting and drying in rice | Gypsum plus alternate wetting and drying | PARTIAL | plausible | 89 (11–1,870) | 0.0167 | 4 | 5.0 | – | alive |
| 6 | Heat buffer for DAC on a low-carbon grid | Grid-charged hot-water store for sorbent regeneration | PARTIAL | plausible | 673 (352–1,151) | 0.3 | 5 | 7.5 | – | front |
| 7 | Solar collector-adsorber DAC panel | Passive loading at night, solar steam release by day | IMPORT | plausible | 584 (137–3,289) | 0.05 | 3 | 5.75 | – | alive |
| 8 | Repair-cycle DAC sorbent | Strip and re-coat oxidised amine in place | PARTIAL | plausible | 474 (118–1,607) | 0.5 | 3 | 7.25 | – | front |
| 9 | Sorbent qualification modelled on the car-electronics AEC-Q100 standard | Accelerated lifetime tests that gate offtake contracts | PARTIAL | plausible | 663 (160–3,311) | 0.01 | 4 | 6.75 | – | alive |
| 10 | Forced aeration of ultramafic tailings | Heap-leach aeration using mine power-station exhaust | PARTIAL | plausible | 543 (54–6,759) | 0.002 | 3 | 7.0 | – | alive |
| 11 | Fracture-stimulated peridotite doublets | In-situ mineralisation in hot olivine rock | PARTIAL | implausible | 86 (23–582) | 0.05 | 3 | 7.0 | – | dropped |
| 12 | Retire-and-store | Storage in depleted fields plus an auction to retire their residual oil | PARTIAL | plausible | 155 (65–302) | 0.02 | 5 | 5.25 | – | alive |
| 13 | Capture-ready fuel-cell (SOFC) power in the Permian | Fuel-cell anode CO2 from stranded gas | PARTIAL | plausible | 48.8 (28.9–86.9) | 0.03 | 5 | 6.0 | S1 | alive |
| 14 | Input-anchored HFC-23 balance, VDF optional | HCFC-22 input mass balance; HFC-23 converted to VDF | PARTIAL | plausible | 0.252 (−0.021–0.44) | 0.069 | 6 | 5.75 | – | front |
| 15 | Methane-intensity differential in contracts | A price term in gas/LNG contracts tied to measured methane intensity | PARTIAL | plausible | 6.8 (−5.7–36.6) | 0.128 | 6 | 5.75 | – | front |
| 16 | Clinker process-CO2 phasedown | Tradeable phasedown met only by storage | PARTIAL | plausible | 235 (114–440) | 0.13 | 8 | 4.75 | – | front |
| 17 | Green-iron border-revenue compact | Carbon border revenue funds contracts for difference for exporters' green iron (HBI) | PARTIAL | plausible | 145 (65–279) | 0.031 | 7 | 5.5 | S6 | alive |
| 18 | CO2 as cushion gas in gas storage | CO2 replaces cushion gas in underground gas storage | PARTIAL | plausible | 129 (25–516) | 0.02 | 4 | 6.25 | S11 | alive |
| 19 | Dredged reservoir sediment for LC3 | Sediment used as calcined clay | PARTIAL | plausible | 60.4 (−23.7–641.4) | 0.009 | 4 | 7.25 | – | alive |
| 20 | N2O-respiring bacteria in slurry | NosZ bacteria dosed into slurry tankers | PARTIAL | plausible | 331 (28–2,738) | 0.007 | 4 | 6.5 | – | alive |
| 21 | Swap carbonate aglime for silicate fines | Source apportionment with river mixing models | PARTIAL | plausible | 234 (−79 to net-emitting) | 0.0011 | 4 | 5.25 | – | dropped |
| 22 | Verified dairy ration balancing | Ration records audited against mid-infrared (MIR) spectra of milk | PARTIAL | plausible | 43 (7–549) | 0.0037 | 4 | 7.75 | – | alive |
| 23 | Paid peat rewetting, verified by InSAR | Satellite radar (InSAR) shows subsidence stopping, with before/after and control blocks | PARTIAL | plausible | 34.3 (6.2–81.1) | 0.032 | 6 | 4.75 | S6 | alive |
| 24 | Rich/lean amine tankage for cycling gas plants | Solvent storage plus a heat-pump reboiler | PARTIAL | plausible | 116 (76–179) | 0.1 | 4 | 5.75 | S1 | alive |

### Why ideas were dropped or left off the front

**Dropped: fracture-stimulated peridotite doublets** (pairs of wells in hot olivine-rich rock that turn injected CO2 into minerals).
- The design target of 0.1 Mt/yr per doublet needs 91–129 times the reactive rock surface that diffusion can supply.
- If reaction is limited by diffusion, each doublet takes only 0.8–1.1 kt/yr, and capital alone costs $4,400–6,200/t [calc].
- Reaction-driven cracking could close the gap only if crystallisation pressures of 27–126 MPa exceed the 41–96 MPa effective stress. That is unproven.

**Dropped: aglime-to-silicate swap.**
- Base cost is $234/t. The high case is net-emitting once haulage and regrinding are counted [calc].
- The avoided emissions, 0.10–0.21 t/ha, are below the 1.19 t/ha needed to detect a difference at two standard deviations.
- A 10–20% rise in N2O can cancel the benefit [calc].

**Dominated, but kept alive.**
- Smackover storage sequencing beats the dairy-ration, sediment-LC3 and sorbent-qualification ideas.
- Fenceline monitoring beats the fuel-cell, cushion-gas, retire-and-store and amine-tankage ideas.
- The methane differential and the HFC-23 ideas beat the tailrace, peat and rice ideas.
- Being dominated here is partly an artefact of comparing across families. The dairy idea (7.75) and the sediment LC3 idea (7.25) are among the best-liked ideas and lose only on scale or TRL.

---

## 4. The Pareto-front ideas

Full dossiers are in [`dossiers/`](dossiers/). The first run produced six; the dossiers for 4.1 (`coalition_1`) and 4.4 (`coalition_4`) were written in a follow-up pass from the same verification records. The summaries below come from the verification scripts.

### 4.1 A methane-intensity price differential in gas and LNG contracts

- **Claim.** A revenue-neutral price term per MMBtu, set by the seller's measured upstream methane intensity, pays sellers of low-leak gas more.
- **Mechanism.** The conventional core is ordinary gas contracts plus OGMP 2.0 reporting. The imported mechanism is the feebate.
- **Size of the signal [calc].**
  - A $30/t CO2e slope equals $894/t CH4, or $0.017/MMBtu for each 0.1 percentage point of methane intensity.
  - Cutting intensity from 1.0% to 0.2% is worth $0.09–0.23/MMBtu at $20–50/t, or 0.8–2.3% of the LNG price.
- **Cost and scale.**
  - Net cost: $6.8/t CO2e base (range −5.7 to 36.6).
  - Scale: 0.036, 0.128 or 0.417 Gt CO2e/yr (low/base/high), covering only supply linked to LNG and the EU. The original idea claimed the whole pool of 35–85 Mt CH4, which overstated it about 8–20 times.
- **Changes from verification.**
  1. A fixed 0.5% reference is not revenue-neutral. In the base case it moves about $1.7bn a year from exporters to buyers (range −$0.1bn to +$5.1bn). The reference must instead be either:
     - the volume-weighted measured mean, reset each period; or
     - each contract's prior-year intensity, on a glide path.
  2. Settling on the higher of two measurement methods biases intensity upward by 0.17–0.28 percentage points.
  3. Settling at basin level dilutes each seller's incentive to $0.3–3/t. Settling at asset level, using operator data scaled by a gated basin reconciliation factor, restores $15–45/t.
- **Who backs it.** Exporters who need EU equivalence from January 2027, the EU, and climate groups and scientists.
- **Main risk.** Measurement methods disagree (0.44% against 3.2% for the Permian).

### 4.2 Audited fenceline monitoring at HCFC-22 plants

- **Claim.** A ring of 8–12 canister samplers 1–1.5 km from the plant can tell a plant emitting 0.2% of its output as HFC-23 from one emitting 1% or more, within one 14-day period, for under $0.50/t. The design includes:
  - calibration with a tracer gas;
  - sealed split samples, 10–20% of which go to an independent lab;
  - one unannounced mobile survey a year.

  That would make Kigali's destruction duty enforceable against the gap of about 11.2 Gg (about 163 Mt CO2e).
- **Imported mechanism.** The US refinery fenceline rule (40 CFR 63.658).
- **Results [calc].**
  - Two-week signal at 2 km: 390–630 ppt at an emission factor of 0.19%, against 2,070–3,300 ppt at 1%. Background is about 37 ppt [assume].
  - On a 1.5 km ring over flat terrain, 100% of emission estimates fall within ±50%.
  - Distinguishing 0.2% from 1% gives 3% false alarms and 1.5% misses.
  - The split-sample audit catches tampering in 4 of 26 periods 34–59% of the time.
  - Cost: $0.08, $0.44 or $4.97 per tonne (low/base/high).
- **Physics.** Destruction is exothermic, so it has no energy floor.
- **Limits.**
  - Unregistered production lines are never monitored.
  - Complex terrain widens the errors.
  - A "practicable" threshold of 0.3% would still allow about 3.5 Gg/yr, a 75% cut rather than more.
- **Coalition.**
  - NGOs, scientists and local communities support it.
  - Industry is split: compliant producers gain a level playing field.
  - Producer states object on sovereignty grounds.
- **Condition.** It must never become a credit. Under the CDM, HFC-23 projects earned 38% of all credits issued by 2013.

### 4.3 An input-anchored HFC-23 balance, with VDF conversion as an option

- **Claim.** A plant-level mass balance would halve eastern China's excess emissions of 3.5–4.3 Gg/yr within three years, at under $0.5/t. It has three parts:
  - expected HFC-23 is computed from independently reported chloroform and HF inputs (1.381 t of chloroform and 0.463 t of HF per tonne of HCFC-22);
  - the by-product ratio is continuously re-verified;
  - unaccounted HFC-23 pays a penalty of $5–10/kg.
- **Detection [calc].**
  - The balance has 80% power to detect venting of 14–18% or more, provided the coefficient of variation of the by-product ratio is 5% or less.
  - A 20% bias introduced at commissioning cuts detection to about 5%.
  - Explaining the excess needs a 12–36% shortfall, which sits right at this detection limit.
- **The VDF option.**
  - Measured thermal selectivity to VDF is only 15.4–22.4% (Yu et al.), against the 40–80% the idea assumed.
  - Revenue is $420–1,430 per tonne of HFC-23, and the margin is −$60 to +$200.
  - VDF therefore stays optional and must only substitute for existing VDF supply.
  - It is sensitive on PFAS for local communities and the anti-PFAS wing of the NGOs.
- **Cost.** −$0.02, +$0.25 or +$0.44 per tonne (low/base/high).
- **Simple baseline.** Atmospheric measurements plus enforcement already cut eastern China's emissions from 8.0 to 5.6 Gg between 2018 and 2023.
- **Fit with 4.2.** The balance catches undeclared output; the fenceline catches venting.

### 4.4 Clinker process-CO2 phasedown with storage-only compliance

- **Claim.** A tradeable phasedown of process CO2 per tonne of binder. It is met first by substituting for clinker, and the remainder only by geological storage: no EOR and no offsets. Process CO2 gets priority in shared storage hubs.
- **Numbers [calc].**
  - Process CO2 is 0.526 t per tonne of clinker, about 1.5 Gt/yr worldwide.
  - Capture costs €99, €198 or €344 per tonne (low/base/high). The base case is about €204/t avoided ($235), roughly twice the idea's claim of €100–150.
- **Price pass-through.**
  - Cement: +€23–129/t.
  - EU build cost: 0.25–0.84% at €100/t.
  - Global South build cost: 1.3–3.8% at €100–150/t [calc on assumed build costs].
- **Changes from verification.**
  - The metric moved from per tonne of clinker to per tonne of binder, so clinker substitution now counts. Cutting the clinker ratio from 0.71 to 0.50 alone gives a 30% reduction.
  - Flue-gas capture is credited in proportion to the process share. Naive accounting would have claimed 81–145% of process CO2 "abated".
- **Scale.** 0.021–0.77 Gt/yr by 2050, depending on which countries join.
- **Storage use.** A century of all process CO2 would use about 10% of the prudent storage budget [calc].
- **Coalition.**
  - Heavy industry: the GCCA cement roadmap relies on carbon capture for 36% of its reductions.
  - Climate scientists support it.
  - NGOs are partly persuadable: CAN's objection to CCS in heavy industry rests partly on evidence, and this design excludes EOR.
  - Global South builders and consumers are weak, because of the price.

### 4.5 Lithium-unit storage sequencing (Smackover)

- **Claim.** Store point-source CO2 (from ammonia, hydrogen and gas processing) below the Buckner anhydrite seal at 0.5–2 Mt/yr per hub.
  - Injectors sit at least 7 km from active lithium and bromine brine producers.
  - From about 2045, a second phase moves storage into brine patterns already stripped of lithium.
- **Results [calc].**
  - Energy: 0.35–0.60 GJ/t.
  - 92–97% of the CO2 is stored net of grid power emissions.
  - Cost: $16, $42 or $164 per tonne (the high case includes 400 km of pipeline).
  - Rate limit per hub: 0.8–6.6 Mt/yr, set by reservoir pressure.
  - The lithium link is worth only about $4/t at the median, against a $5/t test threshold.
  - The margin over 45Q is +$43/t in the base case, falling to −$42/t once the 12-year credit ends.
- **Verdict.** The physics is plausible, but the likeliest outcome is ordinary point-source storage.
- **Coalition.** It fits the coalition that already backs 45Q (oil and gas, heavy industry, unions, government, investors). It will not win the NGOs.

### 4.6 Dissolving gas-plant CO2 into Permian saltwater-disposal wells

- **Claim.** Vented CO2 from gas-plant amine units (over 95% pure; sources of 0.03–0.15 Mt/yr) is dissolved into produced water going down high-rate disposal wells.
  - A downhole dip-tube releases it at no more than 75% of saturation.
  - It should beat a $12M dedicated injection well at 10 or more pads.
- **Results [calc].**
  - Compression: 0.24–0.42 GJ/t.
  - Realistic loading: about 15 kg of CO2 per m³ of water at 60 bar.
  - Capacity: 35–70 kt/yr per well.
  - Tubing must be 7 inches or wider.
  - Cost: $34–54/t at 0.1 Mt/yr, against $36–62/t for a dedicated well. The advantage is $0–25/t, within the model's uncertainty.
- **Prior art (IMPORT).** NETL's carbonated-brine-injection work, the Pena Creek pilot plan with NGL in South Texas, and Hydrozonix patent US12246975B2. A freedom-to-operate opinion is needed before field work.
- **Risks.**
  - Charged brine that degasses at the surface releases 5.5–11 m³ of CO2 per m³, an asphyxiation hazard in low ground.
  - Induced earthquakes.
  - It is uncertain whether the reporting route that 45Q relies on will survive EPA's proposed changes to its greenhouse-gas reporting programme.
- **Best use.** Speeding up or siting NETL and NGL's work, not inventing anything.

### 4.7 Repair-cycle DAC sorbent

- **Claim.** In structured DAC contactors coated with impregnated PEI, flush out the oxidised amine with water and then ethanol, and re-coat in place. This should keep at least 90% of fresh working capacity after two reloads.
- **Imported mechanism.** The D1 protein repair cycle in plant photosynthesis, where only the damaged part is replaced.
- **Results [calc].**
  - At 90% recovered capacity and five reuses of the support, gross cost falls from $592 to $502/t (−15%).
  - The breakeven recovery rises to 0.72–0.83 once the lost capacity is spread across capex and fans.
  - Reload energy is at most 3.5% of plant energy.
- **Closest prior art.** Li et al. 2026 recovered the support once, outside the contactor, at about 90% capacity.
- **Novelty.** The in-place, multi-cycle step.
- **Status.** TRL 3. There is no field data.

### 4.8 Heat buffer for DAC on a low-carbon grid

The system has three parts:
- a heat pump sized to average load;
- an electrode boiler on an interruptible tariff;
- a 16-hour pressurised hot-water store.

**What verification found [calc].**
- Storing heat costs at least 18 times less than buffering loaded sorbent: $11–30 against $553–1,660 per t/yr of capacity.
- France is the only market that passes the net-removal rule. There the saving is $6–9/t, about 1% of cost.
- Electricity use rises 25%.
- The idea survives only if demand-response payments reach at least $15 per net tonne. A desk test costing under $500 settles this.

---

## 5. Claims that failed or changed under verification

### Claims from the evidence map

| Original claim | What verification found |
|---|---|
| BD3's derate implies 1.3–1.5 GJ of electricity per tonne | That is an upper bound: the derate also covers normal auxiliary load and SO2 capture. CO2 capture alone is about 1.0–1.3. SaskPower states about 115 MW net, not 110 |
| NETL: $95–109/t at a 40% capacity factor | About $99–110 by scaling NETL's cost breakdown. NETL's $61/t excludes transport and storage; cost per tonne avoided is $75–81. F-class plant cost rises 115–120%, not 100–104% |
| Mammoth's "675 t net removal" | Company-reported via Bloomberg; not stated whether gross or net. The first 10 months' figure was 0.35% of nameplate, about 2% of installed capacity, because only 12 of 72 units existed |
| Lab electrochemical DAC (2.36 GJ/t) beats commercial DAC | The figure is cell-only (4 cm², 5 cycles) and excludes air-moving, pumping and vacuum, so it is not comparable |
| ERW elicitation: 24 experts, 0.7 Gt/yr | 20 experts, screened for financial ties. The median of 0.4 Gt/yr is below Beerling's modelled 0.5–2 |
| The Illinois ERW yield gain pays without credits | Yield gains were significant only in single years, and rock costs were not netted out. The 10.5 t/ha is a "potential" computed from soil cation loss, not measured removal |
| IEA: current policies give only about a 20% methane cut by 2030 | Not on the key-findings page, so unverified. Of the 200 bcm of recoverable gas, only about 15 bcm is available near-term |
| Atmospheric methane removal needs about 13 times world chlorine output; OH falls 8–12% | The paper says about 20 times. OH falls 27.7% in the chlorine case. Iron salt alone gives −1.7% in the Results section, −2.5% in the Conclusions |
| Green steel premium is $186–231/t | GEI's range is $186–263/t, or $167–237 per car, which is 9–18% of a 6% carmaker margin |
| Instruments that pay incumbents are the politically durable class | That rests on one law. EOR parity applies only to equipment placed in service after 4 July 2025 |
| CAN's objection to industrial CCS is purely about evidence | It is partly about principle too: storage liability, equity, and a blanket phase-out of public support |
| CCS reaches at most 0.37 Gt by 2030 | 0.37 is the optimistic bound. The realistic range is 0.07–0.37 |
| Fervo's PPAs are at $100–130/MWh | That is Rystad's market estimate. Fervo's contract prices are not disclosed |

### Claims about the engine's own ideas

| Idea | What changed |
|---|---|
| Smackover | Two mechanisms were dropped:<br>• Using CO2 to replace spent brine strands 0.57–1.41 m³ of full-grade brine per tonne, losing $3–22/t of lithium.<br>• The "pressure relief" claim fails because lithium extraction removes and returns equal volumes.<br>The 7 km stand-off also fails in the thin-reservoir case: the plume reaches 6.4 km |
| Heat buffer | The original design with charging hardware rated at 3 times load lost $1–9/t. The capacity-factor argument was dropped. The store volume was 10–15% too small. Texas SB 6's 24 hours is a notice period, not an event duration |
| Repair-cycle sorbent | Spreading the lost capacity across all costs cuts the saving at 90% recovery from 42% to 15% |
| Permian disposal wells | Reclassified from new to IMPORT. 5.5-inch tubing is not operable because friction losses reach 179 bar. The 20 kg/m³ loading needs release at about 100 bar |
| Fenceline monitoring | Plume signals were overstated about 2 times; monitoring cost was understated 1.5–2 times |
| HFC-23 and VDF | VDF selectivity is 2–5 times lower than assumed. "Eastern China dominates the gap" is false. The source paper was cited in the wrong journal |
| Methane differential | Not revenue-neutral as designed. The higher-of-two-methods rule is biased upward. Basin-level settlement dilutes the incentive. Scale was overclaimed 8–20 times |
| Clinker phasedown | Cost is about twice the claim. The original metric ignored clinker substitution. Flue-gas capture was double-counted as process CO2. "Under 1% price impact" holds only for EU building cost, not for the price of cement |

---

## 6. Recommended next steps

### The cheapest experiments to run first

Each experiment below is pre-registered, with kill thresholds taken from the dossiers.

**1. HFC-23 desk tests.** Under $4k, 6–8 weeks.
- **(a) Input-anchor check.**
  - **Method:** compare China's 2015–23 HCFC-22 production with data on:
    - chloroform production and trade (UN Comtrade HS 290313);
    - whether each plant makes its own chloroform or buys it in.
  - **Falsified if:** more than half of capacity makes its own chloroform, or if chloroform-implied output cannot be bounded within ±10%.
- **(b) Fenceline check.**
  - Re-run the fenceline Monte Carlo with ERA5 meteorology and EPA's AERMOD model at 3–5 real sites.
  - Run one TO-15 lab recovery test for CHF3, about $1–1.5k.
- **If both pass:** a 3-month field pilot at one plant, $30–160k.
- **Partners:** Bristol ACRG, Empa, TNO, EIA (https://eia-international.org/climate/) and IGSD. The MLF and the Ozone Secretariat are the natural hosts.
- **Funders:** Clean Cooling Collaborative and ClimateWorks. Open calls are unverified.

**2. Backtest of the methane differential.** Desk study, $0–2k, about 4 weeks.
- **Method:** settle the patched contract rule on public Permian data for 2019–2025, using satellite inversions and aircraft surveys.
- **Kill if:** the reconciliation factor moves by more than 0.3 percentage points from year to year, the same size as the signal.
- **Timing:** align it with the EU Methane Regulation's importer reporting from 1 January 2027.
- **Partners:** UNEP IMEO/OGMP 2.0 and LNG buyers. Not contacted.

**3. Storage kill screens.** Under $2.2k in total.
- **Smackover desk study** (under $200).
  - **Pass:** at least $5/t of avoided Class VI cost, or a permitting speed-up of at least one year.
  - **Otherwise:** reclassify it as plain storage.
- **Permian pad-to-vent screen** (under $2k). Kill if any one of these holds:
  - fewer than 10 qualifying pad-vent pairs exist;
  - median CO2 loading is below 14 kg/m³ at 60 bar;
  - fewer than 5 pads beat a $12M dedicated well by $10/t or more.
- **Partners:** the BEG Gulf Coast Carbon Center (https://gccc.beg.utexas.edu), NETL's carbonated-brine team and the Texas Produced Water Consortium.

**First physical experiment, if there is a lab budget.** The repair-cycle sorbent coupon screen.
- **Cost:** a gravimetric screen for under $2k, then about $15k for the two-arm test.
- **Go:** 90% or more of capacity recovered after the second reload.
- **Kill:** below 85%.
- **Partners:** Nottingham (Snape/Stevens) and Bologna (Fabbri).
- **Funder:** Frontier Track 1 (rolling, requires open data).

The heat-buffer desk test is cheap, but its upside is about 1% of cost.

**Where not to spend engine effort:**
- better solvents for point sources, where the headroom is $10–15/t or less;
- cleverer hydrogen-based ironmaking (H2-DRI) chemistry, which is already within about 1.8 times its floor.

### What would change these conclusions

- **DAC.**
  - Watch Stratos's first-year utilisation (start-up is guided for end-2026), Mammoth's ramp-up, and independently measured GJ/t from Deep Sky Alpha's side-by-side tests.
  - If a plant above 100 kt/yr runs above 50% utilisation at under about 6 GJ/t, the DAC levers move up.
- **Methane.**
  - Watch enforcement of the EU import rules: penalties are recommended to pause for 2027–29.
  - Also watch whether the aircraft and satellite intensity figures can be reconciled.
  - If buyers will not pay a differential, the lever reverts to plain regulation.
- **HFC-23.** If atmospheric measurements show eastern China falling further without new measures, the simple baseline is enough and both ideas lose value.
- **CCS.** Watch for:
  - measured GJ/t and capture rates at Brevik;
  - the first operating data from gas-fired CCS: NZT and Baytown, 2027–28;
  - whether 45Q and its reporting route survive.
- **The coalition test.** This month's IMO vote on the Net-Zero Framework (October 2026) shows whether petrostates can still block global fuel standards.
- **Removal options.**
  - Measured enhanced-weathering removals in the tropics could add options that Global South groups support.
  - So could settling how long biochar carbon lasts.