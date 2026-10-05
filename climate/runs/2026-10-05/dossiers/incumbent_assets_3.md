# Verified idea dossier: dissolved CO2 storage at Permian saltwater-disposal pads (incumbent_assets_3, patched)

**Verdict:** the physics is plausible, but this is prior art to import, not a new invention. It is a niche of a few million tonnes a year, and its cost edge over simply drilling a dedicated well is narrow. Pursue it only to accelerate, license or site the work NETL and NGL have already started.

Tags: **[C]** computed by OptiLex scripts; **[S]** sourced; **[A]** assumed.

## 1. Claim
At least 10 Permian commercial disposal pads should meet three conditions:
- (a) at least 80k bbl/d of contained deep disposal;
- (b) outside seismic response areas;
- (c) within 3 km of a vented gas-plant CO2 stream of at least 50 kt/yr.

At those pads, dissolving the CO2 into the disposal water at no more than 75% of saturation should cost less per tonne than a $12M dedicated injection well, in the same cost model.

**Scope:** vents from gas-plant amine units (AGRU) of about 0.03-0.15 Mt/yr each. US-only, because it depends on the 45Q tax credit. It is not a gigatonne lever.

## 2. Mechanism
- **Conventional core:** Class II saltwater-disposal (SWD) pads, which already take water at high rates. The CO2 source is AGRU off-gas, which is already more than 95% CO2 and is vented at small plants.
- **Graft:** Carbfix's in-well dissolution. A dip-tube releases compressed CO2 into the down-flowing water below the depth where water pressure dissolves it.
- **Design rules:**
  - Site from the water first, with one pad and one permit unit per CO2 source.
  - Load to no more than 75% of saturation, so no free gas can form downstream.
  - Make a binding commitment: no EOR and no resale as offsets.
  - In wells that take water on vacuum, set the release point 620-1,580 m deep [C]. Add a backpressure choke and an interlock that cuts CO2 when water flow stops.

## 3. Evidence and verification
Scripts are in `climate/runs/2026-10-05/scripts/`: `incumbent_assets_3.py`, `critic_ia3.py`, `patch_ia3.py`, and `dossier_ia3_checks.py` (new).

| Quantity | Value | Tag |
|---|---|---|
| Separation floor, 96%→99.9% CO2 | 0.008 GJ/t (energy already spent in the AGRU) | C |
| Compression floor (real gas, 1.5→35/60/100 bar) | 0.174 / 0.198 / 0.210 GJ/t | C |
| Compression energy | 0.24-0.42 GJ/t (67-117 kWh/t) | C (efficiencies A) |
| CO2 loading at 75% of saturation, 2-3 molal NaCl (about 110-160 g/L, Permian-like) | 35 bar/30C: 11.5-16.9 kg/m3<br>60 bar/40C: 14.0-20.5 kg/m3<br>100 bar/45C: 16.3-23.9 kg/m3 | C (salinity A; the model runs about 7% high against Bamberger 2000) |
| Capacity per well at 60k bbl/d | 35-70 kt/yr | C |
| Tubing friction over 3 km at 60k bbl/d | 5.5 in: 179 bar (not operable)<br>7 in: 50 bar<br>7 in with a 1.5 in dip-tube: 78 bar | C |
| CO2 released if charged brine degasses at the surface | 5.5-10.9 m3 of gas per m3 of brine (at 10-20 kg/m3) | C |
| 45Q credit | $85/t, with EOR now paid the same<br>Minimum 12,500 t/yr for industrial facilities<br>12-year credit period<br>Construction must start before 2033<br>([26 USC 45Q](https://www.law.cornell.edu/uscode/text/26/45Q)) | S |
| Permian deliverable (before the patch) | 0.8 / 3.7 / 11.2 Mt/yr | C on A inputs |
| Global scale | 0.003-0.073 Gt/yr | C on A inputs |

**Corrections from my checks:**
- The patch says 5.5-7 in tubing works at 60k bbl/d. In fact the tubing must be 7 in or larger.
- At Permian-like salinity, a loading of 20 kg/m3 needs release at about 100 bar, roughly 930 m below the liquid level. The realistic base is about 15 kg/m3 at 60 bar.

**Cost.** This uses the hub cost model [C] with assumed inputs: 8% over 20 years, $60/MWh and a $2M retrofit per well. The pad ranges span 40-60k bbl/d per well and 8-20 kg/m3.

| Source size | Pad | Pad + $2M permit per well | Dedicated well at $6M / $12M / $25M |
|---|---|---|---|
| 0.05 Mt/yr | $50-73/t | $55-95/t | $60 / $76 / $112 |
| 0.10 Mt/yr | $34-54/t | $40-73/t | $36 / $44 / $62 |
| 0.15 Mt/yr | $29-50/t | $35-70/t | $28 / $33 / $45 |

The pad beats a dedicated well only under three conditions together:
- the source is about 0.1 Mt/yr or smaller;
- loading is at least 12-16 kg/m3;
- permits are issued per pad, not per well.

Even then the edge is about $0-25/t, which is inside the model's uncertainty.

**Realized evidence:**
- Carbfix measured more than 95% of injected CO2 mineralised within 2 years ([Matter 2016](https://doi.org/10.1126/science.aad8132)). That was in basalt with fresh water. In sedimentary disposal zones the CO2 is held only by staying dissolved.
- Carbonated brine injection (CBI) has been modelled but not field-tested. OSTI lists no CBI record after August 2024 (queried 5 Oct 2026).

## 4. Prior art: an existing idea to import
- **NETL carbonated brine injection:** produced water carries dissolved CO2 into existing Class II wells to earn 45Q ([OSTI 2204489](https://www.osti.gov/biblio/2204489); corrosion study [OSTI 2323923](https://www.osti.gov/biblio/2323923)).
- **Pena Creek pilot plan with NGL Energy Partners** ([OSTI 2446568](https://www.osti.gov/biblio/2446568)): the site is in Dimmit County, South Texas, not the Permian.
- **Hydrozonix patent [US12246975B2](https://patents.google.com/patent/US12246975B2/en):** it covers produced water supersaturated with CO2 and injected into Class II wells (priority 2018, granted 2025). [S, from an earlier search; the page returned a 503 error today]
- **Eke et al. ([SPE 124711](https://doi.org/10.2118/124711-pa)) and Burton & Bryant 2009:** both cover dissolving CO2 at the surface.

**Possibly new, but only as engineering refinements:**
- Dissolving the CO2 downhole through a dip-tube inside the SWD tubing. The NETL abstracts do not say whether their mixing happens at the surface or downhole.
- Pairing AGRU vents with pads, choosing the water first.
- Arguing that the area of review only needs to cover the pressure footprint, because dissolved CO2 forms no plume.

## 5. Stakeholder map
| Id | Stance | Evidence |
|---|---|---|
| S1 | Split | CAN's red lines oppose subsidies for fossil-linked CCS. Texas groups fought Texas's Class VI permitting authority ([FR 2025-19898](https://www.govinfo.gov/content/pkg/FR-2025-11-14/html/2025-19898.htm), 7,534 comments). The no-EOR commitment wins over moderates. |
| S2 | Conditional support | IPCC AR6 backs CCS where it abates emissions. Support depends on monitoring and on seismic risk. |
| S3 | Support | They earn 45Q income on CO2 they now vent. Frictions: EOR earns the same credit, and Class VI rules would burden their disposal wells. |
| S4 | Neutral | Not affected. |
| S5 | Neutral | Small extra power load. |
| S6 | Support | Unions are in the Carbon Capture Coalition; retrofits add jobs. |
| S7 | Support, with a fiscal caveat | Texas sought Class VI permitting authority (EPA, Nov 2025). A margin of up to about $50/t invites scrutiny over whether the CO2 would have been stored anyway. |
| S8 | Split | Gas processing falls outside COP28's "hard-to-abate" qualifier. Concern about LNG lock-in. |
| S9 | Neutral | No effect on prices. |
| S10 | Split | The credits are bankable, but long-term liability and seismic exposure are unpriced. |
| S11 | Split | The vents end. But the area has had the M5.4 Gardendale quake, and 23 disposal permits were suspended in Northern Culberson-Reeves ([RRC](https://www.rrc.texas.gov/oil-and-gas/applications-and-permits/injection-storage-permits/oil-and-gas-waste-disposal/injection-disposal-permit-procedures/seismicity-review/seismicity-response/)). |

**Coalition logic:** start from the existing 45Q alliance (S3, S6, S7) and add conditional S2 and moderate S1. Three commitments hold it together:
- no EOR and no resale as offsets;
- open monitoring data;
- siting outside seismic response areas.

## 6. Risks
- **Technical:**
  - Corrosion from CO2 plus H2S in high-salinity brine.
  - Carbonate dissolution or scale changing how much water the well accepts.
  - Friction from the dip-tube.
  - Low liquid levels in wells that take water on vacuum.
- **Monitoring, reporting and verification (MRV):**
  - Dissolved CO2 forms no plume to image. Accounting has to rest on metering at the wellhead, fluid sampling and pressure.
  - 45Q relies on EPA's GHGRP Subpart RR reporting. EPA proposed on 12 Sep 2025 to drop reporting for 46 GHGRP source categories ([EPA](https://www.epa.gov/ghgreporting)). I did not verify whether Subparts RR and W are among them.
- **Moral hazard:**
  - It feeds a "decarbonised gas" narrative.
  - Operators could get a 45Q windfall.
  - CO2 could be diverted to EOR, which now earns the same credit.
- **Local safety:**
  - A brine breakout at the surface would release 5.5-11 m3 of CO2 per m3 of brine, an asphyxiation risk in low ground.
  - Induced seismicity.
- **Rebound:** small. Gas plants must remove the CO2 to meet pipeline spec anyway, so the idea does not change gas output.

## 7. Cheapest falsifying experiment
**Design:** a desk screen matching pads to vents. Join four data sources:
- the RRC injection-well database (H-10 volumes and pressures; free, updated monthly; [RRC data](https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/));
- EPA GHGRP Subpart W acid-gas-removal vent reports, latest available year;
- USGS produced-water salinity data;
- seismic response area boundaries.

Compute CO2 loading with the script and cross-check it in PHREEQC (Pitzer database). In parallel, ask NETL about the status of Pena Creek and read the Hydrozonix claims.

**Cost and time:** under $2k (the data is free), 4-6 weeks.

**Kill the idea if any of these holds:**
- (a) Fewer than 10 qualifying pad-vent pairs exist.
- (b) Median loading at the qualifying pads is below 14 kg/m3 at 60 bar.
- (c) Fewer than 5 pads beat a $12M dedicated well by at least $10/t at their actual rates.

## 8. Proof-of-concept path
1. **Under $2k:** run the screen above, then publish it with the scripts.
2. **About $20-80k [A]:** run autoclave corrosion tests in Permian brine with CO2 plus H2S, if NETL's study leaves gaps. Hold an RRC pre-application meeting for one pad.
3. **Field pilot,** funded by an operator and by 45Q.

**Partners:**
- NETL's carbonated-brine-injection team (Wei Xiong)
- NGL Energy Partners
- Permian water midstream firms (WaterBridge, Aris; ownership not re-verified)
- BEG Gulf Coast Carbon Center ([gccc.beg.utexas.edu](https://gccc.beg.utexas.edu/))
- Texas Produced Water Consortium ([TXPWC](https://www.depts.ttu.edu/research/tx-water-consortium/), active as of May 2026)

**Funders:** transferable 45Q credits, operator co-funding, and DOE's Office of Fossil Energy and Carbon Management (2026 funding status not verified).

## 9. IP and publish decision
Do not file a patent. NETL has published the concept and Hydrozonix has patented it, and the refinements are likely obvious given Carbfix and NETL's work. Publish the screen with open data as a defensive publication, which also builds trust with S1 and S11. Get a freedom-to-operate opinion on US12246975B2 before any field work.

## 10. Open questions
1. Has Pena Creek injected anything yet, and does it mix at the surface or downhole?
2. Will the RRC accept one permit per pad, with an area of review covering only the pressure footprint?
3. Will the 45Q reporting route survive the GHGRP changes?
4. How much CO2 do Subpart W vents actually release, and how much already goes to acid-gas injection or incineration?
5. Does the charged brine actually sink, given the salinity and temperature differences with the formation brine?
6. Would this CO2 go to EOR anyway, since EOR earns the same $85/t?

The dossier file is at `climate/runs/2026-10-05/scripts/dossier_ia3.md`.

Sources: [26 USC 45Q](https://www.law.cornell.edu/uscode/text/26/45Q), [OSTI 2446568](https://www.osti.gov/biblio/2446568), [OSTI 2204489](https://www.osti.gov/biblio/2204489), [EPA GHGRP](https://www.epa.gov/ghgreporting), [RRC data sets](https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/), [TXPWC](https://www.depts.ttu.edu/research/tx-water-consortium/), [GCCC](https://gccc.beg.utexas.edu/)