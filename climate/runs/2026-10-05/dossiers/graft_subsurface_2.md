# Verified idea dossier: Lithium-unit storage sequencing (Smackover)

**Verdict:** the physics is plausible, and the cost is that of ordinary point-source Class VI storage. The lithium link adds little (P50 about $4/t; 26% chance of more than $5/t). The likeliest outcome is that this becomes plain point-source storage. Prior art: **PARTIAL**.

## 1. Claim
In the Smackover trend, CO2 from industrial processes (ammonia, hydrogen, gas processing) can be stored below the Buckner anhydrite seal at 0.5-2 Mt/yr per hub. The storage compartments sit at least 7 km down-dip of, or outside, active lithium and bromine brine units. Two tests decide the claim:
- **Test 1:** no CO2 reaches any active brine producer within 25 years.
- **Test 2:** the brine unit's data, wells and list of old wells cut Class VI cost by more than $5/t CO2.

**Scope:** this cuts US Gulf Coast industrial emissions; it does not remove CO2 from the air. Realistic scale is about 0.01 Gt/yr, or 0.03% of fossil CO2. Test 2 is the new part, and it is more likely to fail than pass.

## 2. Mechanism
- **Conventional core:** Class VI storage in a saline aquifer, with pressure and plume management (Buscheck et al. 2012 active reservoir management; DOE brine extraction test, 2022).
- **Graft:** the Smackover brine units being developed for direct lithium extraction (DLE) by Standard Lithium/Equinor, ExxonMobil, Albemarle and Lanxess. Three things carry over to storage: the units' rock and well data, their list of old wells, and their DLE wells, which can serve as pressure monitors in the reservoir. Decades later, well patterns stripped of lithium also become available.
- **Phase 1 (about 2028-35):**
  - CO2 injectors sit at least 7 km from brine producers. The modelled plume edge must also stay at least 2 km from producers at 25 years; if it would not, the injection rate is capped.
  - Spent brine is reinjected as already permitted.
  - No CO2 is used for enhanced oil recovery (EOR).
  - Brine operators can veto storage in any pattern still above the lithium cut-off grade.
- **Phase 2 (about 2045 on):** storage moves into patterns whose brine is down to 30% or less of the original lithium grade. The brine that the CO2 pushes out goes through DLE once more.
- **Dropped from the original idea:**
  - Using CO2 in place of the reinjected spent brine. CO2 does not mix with brine, so each tonne stored strands 0.57-1.41 m3 of full-grade brine in the rock. That loses $3-22/t of lithium, against $10-26/t of lithium in the brine the CO2 displaces.
  - The pressure-relief claim. DLE takes out and puts back the same volume of brine, so it creates no net room.

## 3. Evidence and verification
Labels used below:
- **[calc]** executed calculation
- **[src]** primary source
- **[assume]** assumption
- **[recall]** knowledge from before the model's cutoff, not re-checked

The scripts are in `scratchpad/climate/`: `graft_subsurface_2_patched.py`, `critic_li_swap.py`, `patch_li_swap.py`, and my independent cross-check, `dossier_li_unit_check.py`.

| Quantity | Value | Basis |
|---|---|---|
| Minimum separation energy, ammonia-plant CO2 (98% pure) | 0.0025 GJ/t (direct air capture: 0.465) | [calc] verifier |
| Minimum compression energy, 1→150 bar | 0.28 GJ/t | [calc] |
| Energy, low/base/high | 0.35/0.44/0.60 GJ/t | [calc] on [recall] compressor data |
| Net CO2 stored after grid power emissions | 92-97% | [calc]; grid at 0.35-0.45 t/MWh [assume] |
| CO2 density at 100-130 °C, 250-320 bar | 575-588 kg/m3 | [calc] CoolProp |
| Cost, plain Class VI | $16 / $42 / $164 per t | [calc] on [assume] capital costs; the high case includes 400 km of pipeline |
| Value of the lithium-unit link (Monte Carlo, N=200k) | P50 $3.9/t (P5-P95: 2.1-6.8) | [calc] on order-of-magnitude [assume] |
| Margin over the 45Q credit at $85/t | +$69 / +$43 / −$78; base case −$42/t after year 12 | [calc]; 45Q [recall] |
| Maximum rate per hub (≤40 bar rise at 5 km after 25 yr) | 0.8 / 1.8 / 6.6 Mt/yr at 50 / 100 / 300 mD | [calc] Theis model; my cross-check gives 0.9 / 1.9 / 7.1 |
| Pressure rise at brine producers 7 km away (1 Mt/yr, 25 yr) | 5-44 bar | [calc] |
| New Phase-2 capacity per DLE plant | 0.42-0.94 Mt/yr | [calc] |

**Scale:** 25 Mt/yr would need 4-33 hubs, spaced about 100-200 km apart. Reservoir pressure, not lithium, is the binding limit. Arkansas brine above 400 mg/L lithium is [src] (USGS, Knierim 2024).

**Corrections made during verification:**
1. The 7 km stand-off fails the 2 km margin in one case: a thin reservoir where buoyant CO2 spreads strongly along the top, at 1 Mt/yr. There the plume reaches 6.4 km.
2. Phase-2 lithium losses pass, but only because the flushed brine (45-120 mg/L) is below the roughly 150 mg/L cut-off, so the lithium has no commercial value. Discounting does not save it: the loss is still $1.1-6.5/t. If lithium carbonate reaches $20k/t and the cut-off falls, the loss reaches $14/t.
3. Without discounting, the cost avoided through the brine unit is P50 $0.73/t. It is small because the Phase-1 plume lies outside the pore space the unit has already pooled.
4. A licence fee would earn $1-10M/yr, which is 0.4-4.4% of a 25 kt/yr lithium carbonate plant's revenue. That is too little to make DLE profitable (Malone et al. 2026).
5. No thermodynamic floor is violated.

## 4. Prior art and what is new: PARTIAL
- **The mechanism is old.**
  - Chinese patent CN103603642B (China University of Geosciences, Wuhan; priority 2013) covers CO2 displacing deep mineral brine.
  - China's work on recovering deep water with CO2 also covers it (Li et al. 2015, plus a Junggar field test).
  - So do potash brine recovery with CO2 (Fang et al. 2017) and active reservoir management (Buscheck 2012).
- **Closest lithium work:** Hamdi, Clarkson and Zirbes 2025 (SPE 228170, Leduc aquifer, Alberta). It dissolves CO2 in the spent DLE brine at a few tonnes a day.
- **Plausibly new:**
  - the siting and sequencing rule around live DLE units
  - Phase-2 storage in patterns already stripped of lithium
  - valuing the brine unit as avoided Class VI cost
  - the analysis of lithium losses and CO2 reaching producers

  The novelty is in combining these, and it is modest.
- **Caveat:** industry announcements went unchecked because the search budget ran out.

## 5. Stakeholder map

| Group | Stance | Evidence |
|---|---|---|
| S1 Climate activists, NGOs | Split | Climate Action Network (2021) opposes subsidies for fossil-linked CCS and moving liability to the state; the no-EOR commitment helps |
| S2 Scientists | Support | IPCC AR6 and COP28 back CCS in hard-to-abate sectors; support depends on results for CO2 reaching producers, earthquakes and monitoring |
| S3 Oil and gas | Support | Equinor's lithium joint venture ($225M DOE grant, 2025); 45Q pays EOR the same, so EOR competes for the CO2 |
| S4 Heavy industry | Split | Emitters need storage; bromine producers fear CO2 reaching their brine |
| S5 Utilities | Neutral | Flue-gas CO2 costs more to separate (0.22 GJ/t minimum); not early suppliers |
| S6 Workers | Support | Reuses oilfield skills; modest number of jobs |
| S7 Governments | Support | Critical minerals plus 45Q; fiscal cost $0.7-2.0bn/yr |
| S8 Global South | Split | Competes with Lithium Triangle supply; opposes Northern CCS subsidies |
| S9 Consumers | Neutral | Cost falls on taxpayers, not on bills |
| S10 Investors | Support | Lowers DLE risk; adds risks of credit clawback and liability |
| S11 Communities | Split | Satartia, Mississippi 2020 CO2 pipeline rupture (about 300 evacuated); but a century of local brine industry |

**Coalition logic:** the idea fits the coalition that already backs the 45Q credit (S3, S4, S6, S7, S10). Lithium brings in critical-minerals advocates, but it will not win over S1. Per tonne stored, 45Q is worth 1.4-9.6 times the lithium. The project should be presented honestly as subsidised storage.

To widen the coalition:
- Use local industrial CO2 so pipelines stay short.
- Commit to no EOR.
- Have operators fund liability bonds instead of handing long-term liability to the state.
- Pay fees to the owners of the pore space.
- Share revenue with bromine operators, or keep storage out of their units.
- Time the storage revenue to replace the 45X manufacturing credit as it phases out in 2031-33.

## 6. Risks
- **Technical:** pressure limits capacity, and fault-bounded compartments and high-permeability streaks can move CO2 faster than modelled. Buoyant CO2 also drifts up-dip toward the brine unit and oil traps at 3-61 m/yr until it becomes trapped.
- **Monitoring and verification:** the CO2 sits in a formation still producing brine, so leakage would be hard to rule out, and 45Q credits could be clawed back.
- **Moral hazard:** lower than for engineered CO2 removal, since this cuts emissions at the source. But storing gas-processing CO2 helps keep gas sales going, and equal 45Q pay for EOR invites diverting the CO2 to oil fields.
- **Local safety:** CO2 pipelines, old wells, brine spills and induced earthquakes.
- **Rebound:** small, though cheap compliance may extend fossil hydrogen production.

## 7. Cheapest falsifying experiment
1. **Desk study** (1-2 person-weeks, under $200). Compare the Class VI cost of a Smackover site whose pore space a brine unit has already pooled with a new site. Sources: EPA Class VI permit files and Arkansas Oil and Gas Commission unit orders.
   - **Success:** at least $5/t of avoided cost, or a documented permitting speed-up of at least one year.
   - Otherwise, file the idea under plain point-source storage.
2. **Reservoir simulation in OPM Flow** (2-4 weeks), only if step 1 succeeds. **Kill if** any of these holds:
   - CO2 reaches a brine producer within 25 years, with injectors 7 km away at 0.5-1 Mt/yr.
   - The pressure rise breaks the permitted limits for brine reinjection.
   - Phase-2 lithium losses reach $2/t or more.

## 8. Proof-of-concept path
- **Step 1:** the desk study, about $0-200.
- **Step 2:** OPM Flow 2026.04 (open source under GPL, with CO2 storage support) on a cloud virtual machine, about $300-1,500. Inputs are USGS lithium data and published Smackover rock properties.
- **Partners and resources** (links checked 2026-10-05):
  - Gulf Coast Carbon Center at UT Austin's Bureau of Economic Geology, which runs an industry research consortium: https://gccc.beg.utexas.edu
  - OPM: https://opm-project.org
  - EPA tracker of Class VI projects under review (updated 28 Sep 2026): https://www.epa.gov/uic/current-class-vi-projects-under-review-epa
- **Data and host partners:** Smackover Lithium (Standard Lithium/Equinor) and TETRA (https://ir.onetetra.com).
- **Funding:** no funder was confirmed; both steps fit OptiLex's own budget.

## 9. IP and publish decision
**Do not patent; publish.** The mechanism is already patented (CN103603642B), the siting rule is likely obvious to reservoir engineers, and the commercial value lies in pore-space contracts rather than patents. Publish the desk study and simulation as a preprint, including a negative result, which also blocks others from patenting it.

## 10. Open questions
- **Permitting:** EPA pages fetched 2026-10-05 show Arkansas neither holds nor has applied for Class VI permitting authority, so EPA Region 6 would issue permits. Arkansas pore-space law is unverified.
- **CO2 supply:** how much concentrated CO2 lies within about 150 km of the trend? The El Dorado ammonia plant's CCS project is unverified.
- **Reservoir:** permeability, thickness and compartments near the brine units.
- **Lithium processing:** how well lithium sorbents work on brine made more acidic by dissolved CO2.
- **Policy:** what carbon price follows 45Q, given its 2033 construction-start deadline and 12-year payment window.
- **Competition:** whether ExxonMobil or Equinor already plan this internally.

---
Dossier file: climate/runs/2026-10-05/scripts/dossier_li_unit.md
Cross-check script: climate/runs/2026-10-05/scripts/dossier_li_unit_check.py