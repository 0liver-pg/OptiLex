# Verified idea dossier: store heat, not loaded sorbent (bottleneck_thermo_4, patched)

**Status (2026-10-05):** a marginal, incremental refinement of published work. Prior art: PARTIAL.

**Labels:** [C] computed by OptiLex scripts; [S] sourced; [A] assumed. Every cost here is modelled. None is measured at a plant.

## 1 Claim
Take a solid-sorbent DAC plant on a grid or power purchase agreement (PPA) below ~0.05 t CO2/MWh. Its regeneration heat comes from three parts: a heat pump sized to the average heat load and running flat, an electrode boiler sized to twice that load on an interruptible tariff, and a 16 h pressurised hot-water store. Such a plant earns at least $15 per net tonne more than a plant on a flat heat pump alone, once demand-response (DR) revenue is counted. Buffering heat is also at least ~18x cheaper per unit of capacity than buffering loaded amine sorbent.

**Scope:** sorbent DAC that regenerates at ~100 C. It does not cover 900 C liquid-solvent DAC (Stratos-type) or methane removal.

## 2 Mechanism
- **Conventional core:** solid-sorbent temperature-vacuum-swing DAC at ~95% capacity factor. The parent paper is Mohan, Konuru, Luo & Jenkins (2025).
- **Graft:** power-to-heat as practised in Danish and German district heating. A base heat pump and an electrode boiler on an interruptible tariff feed a tank.
- **Heat pump:** runs flat and delivers ~110 C directly to the plant, at COP 1.9 from 10 C air at 50% of Carnot [C]. It never has to reach store temperature, which fixes the original idea's COP error.
- **Boiler:** fires when power is below EUR 10-20/MWh and charges the store from 105 to 150 C (4.8 bar).
- **Fans and vacuum:** run continuously at 0.65 MWh_e/t [A].
- **Dropped:** the capacity-factor argument. A flat heat pump already reaches 95% capacity factor, so the store adds only price arbitrage and the ability to interrupt load.

## 3 Evidence and verification
Scripts are in `climate/runs/2026-10-05/scripts/`: `bottleneck_thermo_4.py`, `critic_bt4_hybrid.py`, `patch_bt4_net.py` and `dossier_bt4_checks.py` (new in this pass).

Prices are 2025 day-ahead data from SMARD [S]. Equipment costs are Danish Energy Agency ranges recalled from memory [A].

| Quantity (100 kt/yr plant) | Value | Label |
|---|---|---|
| Thermodynamic floor | 0.465 GJ/t (20.5 kJ/mol) | C |
| Plant energy, electric-boiler route | 7.3/9.5/11.9 GJ_e/t (second-law efficiency 3.9-6.4%); no floor violation | C |
| Heat demand | 22.8 MW_th at 7.2 GJ_th/t | A (Climeworks Gen2 nominal) |
| 16 h store | 365 MWh_th, ~7,500 m3 cycling 150 to 105 C, $11-30 per t/yr | C (steam-table recheck; the earlier 6,300-6,734 m3 was 10-15% low) |
| 16 h buffer of loaded sorbent | 2,770-4,150 t, $553-1,660 per t/yr | C; sorbent price $20-40/kg and capacity 1.0-1.5 mmol/g are A |
| Heat cost in $/t, flat heat pump vs hybrid | DE-LU 170 vs 158-160; DK1 159 vs 149-151; FR 133 vs 124-127 | C; German-style network charges are A |
| Original design (charging hardware rated 3x) | saving of -1/-3/-9 $/t, i.e. a loss | C |
| Gross capture cost | $352/673/1,151 per t | C; the $2,600 per t/yr Stratos capex proxy is A |
| Net removal, DE-LU grid (0.316 t/MWh) | 0.44 t per t captured, ~$1,520 per net t | C |
| Net removal, FR hybrid | 2.20 MWh_e/t × 0.019 t/MWh gives 0.96 t/t, ~$700 per net t | C; RTE eco2mix direct intensity (19 g/kWh in 2024, 17 g Jan-Aug 2026) is S |
| Scale | 0.3 Gt/yr by 2050; the heat-pump route needs 5-6% of world electricity per Gt/yr | A / C |

**New finding:** the critic's $10-12/t saving was computed for DE-LU, which is the grid the siting rule excludes. France is the only measured market that passes the carbon rule, and there the saving is **$6-9/t, about 1% of gross cost.** The hybrid also raises electricity use from 1.76 to 2.20 MWh_e/t (+25%), because boiler heat at COP 1 displaces heat-pump heat. Arbitrage cannot carry the idea; DR revenue would have to.

## 4 Prior art and what is new (PARTIAL)
- **Mohan et al. 2025**, *J. Phys.: Energy* 8(1) 015011, https://doi.org/10.1088/2515-7655/ae24ac (DOI checked via Crossref). Grid-charged thermal storage plus a heat pump for sorbent DAC. Storage changed gross cost by less than 3%.
- **Fan & Xu 2026**, *ES&T*: concentrated solar heat with sand storage, above 80% capacity factor.
- **Arwa & Schell 2024**, *Applied Energy*: CaO/CaCO3 silos compared against batteries.

What is new is incremental:
- (a) the cost comparison of storing heat versus storing loaded amine sorbent, which I found in no paper;
- (b) the district-heating hybrid with storage at the sorbent's matched temperature;
- (c) a siting rule based on net tonnes;
- (d) a store sized for large-load demand response.

## 5 Stakeholder map
| Group | Stance | Evidence |
|---|---|---|
| S1 activists and NGOs | split | CAN (2021) says DACCS has "no place" as a substitute for cuts, and CIEL calls it a "license to pollute". The graft only removes fossil process heat. |
| S2 climate scientists | support for R&D | IPCC AR6 WGIII sees CDR as needed for residual emissions. The energy-scale worry remains (+25% electricity). |
| S3 oil and gas | neutral | Oxy's Stratos (liquid solvent) is out of scope. Gas-heat suppliers lose a small market. |
| S4 heavy industry | neutral | Their route is point-source capture (kiln floor 0.11 GJ/t); removals are a residual option. |
| S5 power utilities | support | Texas SB 6 (2025) [S] procures demand reduction from loads of 75 MW and above, with "at least a 24-hour notice". |
| S6 workers and unions | support, low confidence | Unions belong to the Carbon Capture Coalition; the stance is inferred. |
| S7 governments | support, with a fiscal caveat | The 45Q credit for DAC was kept at $180/t in OBBBA (Jul 2025); fiscal hawks object. |
| S8 Global South | split | Baum et al. 2024 (N=30,284): more support, but more worry about mitigation deterrence. |
| S9 consumers | neutral | No consumer price impact unless interconnection costs are socialised. |
| S10 investors and insurers | weak support | cdr.fyi reports 50.5 Mt contracted against 1.7 Mt delivered. The hardware is bankable, but it is worth only ~1% of cost. |
| S11 local communities | neutral | Pressurised water is a low hazard; CO2 pipeline and Class VI well risk comes with DAC itself. |

**Coalition logic:** these stances belong to DAC, not to the graft. The graft wins S5 and S7 only if the interruptibility is credible. The widest coalition needs three things: dedicated geologic storage with no enhanced oil recovery, a framing limited to residual emissions, and reporting per net tonne.

## 6 Risks
- **Technical:** air-source heat pumps delivering 110 C are unproven at 20+ MW_th [A]. The store is a 4.8 bar pressure vessel. Store cost never decides the result.
- **MRV:** net tonnes depend on hourly, marginal and import-adjusted grid intensity. RTE's figure covers direct production only.
- **Moral hazard and local safety:** inherited from DAC. The hazards are CO2 transport and injection, not the tank.
- **Rebound and siting tension:** DR revenue is found in grids like ERCOT. I assume, without fetching data, that ERCOT's intensity is far above 0.05 t/MWh. There the carbon rule fails unless the plant has a dedicated PPA matched hour by hour.

## 7 Cheapest falsifying experiment
**Desk test:** under $500 and about 2 weeks.
- Extend `dossier_bt4_checks.py` to ERCOT, CAISO, SE3 and FR using 2025 hourly prices and grid intensity.
- Add 1-2%/day store loss and savings from avoiding ERCOT's four-coincident-peak (4CP) transmission charges.
- Proxy DR revenue with ERCOT's Emergency Response Service clearing prices.

**Pass** if arbitrage plus DR revenue is at least $15 per net tonne against a flat heat pump, in at least one market where net removal is at least 0.9 t/t. **Falsified** otherwise.

**Correction to the patch:** the 24 h in SB 6 is the *notice period*; curtailment lasts for the duration of the emergency event. A 16 h store charged during the notice period covers events lasting several hours. A multi-day event like February 2021 would simply pause capture. A 24 h store (11,200 m3, $17-45 per t/yr [C]) is therefore unnecessary.

## 8 Proof-of-concept path
1. **First step, under $2k:** run the desk test on free data:
   - ENTSO-E Transparency (transparency.entsoe.eu);
   - RTE ODRE eco2mix (odre.opendatasoft.com, used here);
   - ERCOT and CAISO public price data;
   - the EIA Hourly Electric Grid Monitor (not re-verified).

   Replace the from-memory equipment costs with the Danish Energy Agency technology catalogues (ens.dk/en/analyses-and-statistics/technology-catalogues [S]).
2. **Partners:**
   - Princeton ZERO Lab, authors of the parent paper, to rerun their model with the hybrid.
   - A developer of solid-sorbent temperature-vacuum-swing DAC.
   - Deep Sky Alpha (Innisfail, Alberta), an operating cross-technology DAC test centre where partners keep their IP (deepskyclimate.com/alpha [S]).
   - Frontier prepurchases (frontierclimate.com/apply [S]), which a developer would apply for.

   I found no verified 2026 grant that fits; this is still open.

## 9 IP and publish decision
**Publish; do not patent.** The core is prior art (Mohan 2025), and the hybrid is standard district-heating practice, so it is likely obvious. The value is about 1% of cost. Release the desk study with open code as a preprint or defensive publication, and offer it to the ZERO Lab.

## 10 Open questions
1. What do the SB 6 and ERCOT DR products pay per MW-yr, and can they coexist with clean supply?
2. Does ramping regeneration change sorbent degradation?
3. What is the real heat duty of sorbent DAC? Early plants underperform, and Mammoth's shortfall has no stated cause.
4. What do France's TURPE network tariffs and Nordic tariffs charge an interruptible electrode boiler?
5. Should net accounting use marginal or average grid intensity?