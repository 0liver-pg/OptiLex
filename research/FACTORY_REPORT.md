# OptiLex General Ideas Factory: Merged Final Report

*Produced by three multi-agent research workflows (about 185 agents) on 25–27 Sep 2026 and reviewed before commit. Supporting data is in [`data/`](data/); per-proposal vetting and checked targets are in [`factory_vetting_and_targets.json`](factory_vetting_and_targets.json).*

Date: 27 Sep 2026. Audience: the OptiLex team. Evidence is weighted in this order: realized outcomes (money paid, lab validation, executed results, citation impact), then expert ratings, then LLM-judge scores. Every statistic carries its task, benchmark and model. When a number comes from a different task than ours, the report says so.

## 0. Run status and coverage

Both research workflows finished, and their outputs are merged here:
- The engine map: 17 dimensions, about 250 approaches, each claim checked independently.
- The domain map: 8 dimensions.
- 25 domain × channel candidates, each scored by 3 lenses on 7 criteria.
- 12 vetted engine proposals.
- Live checks on specific targets, run on 27 Sep 2026.

There are four coverage gaps:
1. **One dimension is empty.** The domain map's `verifiable_science` dimension returned no findings, because a safety check withheld the worker's final output. It should be rerun, split into one task per domain.
2. **One target check is missing.** The target checks for `agent_security_aria` came back empty; the run appears to have been cut off. The ARIA facts below come from the domain map's own primary-source check on 25 Sep.
3. **Prior-art coverage is thinner than intended.** Almost every prior-art worker hit the shared cap of 200 web searches. They fell back to the arXiv, OpenAlex and Crossref APIs, some of which were rate-limited. "No prior art found" therefore means not found through those channels.
4. **Four items were not re-checked.** Vesuvius, Foresight, Enveda and ARIA were verified on 25 Sep but not re-checked on 27 Sep.

## 1. Executive answer

**Raw ideas cannot be sold. Verified artifacts get rewarded.** The evidence is consistent:
- Arrow's disclosure paradox: a buyer cannot value an idea until it is disclosed, and after disclosure already has it.
- Corporate intake portals treat submissions as non-confidential. P&G's Connect+Develop terms let anyone use unprotected aspects of a submission.
- Wazoku/InnoCentive, the largest pay-for-ideas platform, listed 6 public items on 25 Sep 2026. Its current challenges reject AI-only submissions and cap entries at 1–3 per solver.
- Invention promoters leave almost no clients net positive: InventHelp's own disclosures give 27 of 6,076 clients in 2013–15 (0.44%).
- Pre-revenue software sells for an average of $7,500 (Acquire.com guidance, Nov 2024).
- The whole brokered patent market was about $158M in 2024.
- No worker found a primary-source case of raw AI-generated ideas being sold.

Every cash conversion found for AI-assisted work in 2024–26 went to an artifact scored by an external oracle: hidden test sets (AIxCC $8.5M, ARC, AIMO, AtCoder), maintainer-confirmed exploits, Lean or expert-checked proofs, customer KPIs (AlphaEvolve), or clinical endpoints.

**The sellable unit is the *verified idea dossier*.** It contains the claim, the executed or formally checked evidence, the verifier result, a prior-art check and the IP status. It is delivered into a channel whose terms are fixed before disclosure: prize rules, a grant call, a bounty or a pilot contract (Section 9.4).

**Recommended path.** Build a thin, verifier-first engine, and spend most of the effort on domain packs that already have an external verifier and a live reward channel.
1. **Formal maths pack (credibility, and calibration outside ML).**
   - Targets: the SAIR Lean Kernel Challenge (20 Nov) and the Andrews–Curtis challenge (30 Nov); Erdős finite witnesses, formalisations and literature finds; the Optimization Constants table; the fast matrix multiplication (FMM) catalogue; FrontierMath Open Problems.
   - Verifiers are near-perfect and cost is Claude Max plus under $500 of CPU.
   - Cash is near zero, but this feeds the AI for Math seed grants (up to $100k, rolling).
2. **High-impact computational biology.**
   - Targets: Virtual Cell Challenge 2026 (VCC; $87.5k cash plus equal NVIDIA Brev credits; final 5 Nov), the Virtual Embryo Challenge Agent Team track ($112k total; final 2 Dec), and Anthropic × Adaptyv Track 3 (free wet-lab testing, no cash; challenges open weekly from 28 Sep, submissions close 31 Oct).
3. **Industrial optimisation.**
   - Public best-known-solution records on CVRPLIB (vehicle routing) and MIPLIB (mixed-integer programming) serve as cheap evidence.
   - That evidence leads into paid pilots on a customer's own KPI evaluator. This is the only route to repeatable invoices, and it competes with AlphaEvolve, generally available on Google Cloud since 10 Jul 2026.
4. **Grants, each with a named human author and an AI-use disclosure.**
   - ARIA Scaling Trust and Safeguarded AI (current batch closes 31 Oct).
   - Foresight AI for Science & Safety Nodes (31 Oct).
   - Innovate UK Frontier AI SME Champions (closes 11 Nov).
   - AI for Math seed grants (rolling).
5. **LLM-training efficiency stays the calibration pack.** The engine's architecture experiments run here: whether the knowledge base pays, which critics may be used, and shadow audits. OptiLex's 7M-parameter proxy detects 1.11× with 3 seeds (FEASIBILITY.md), which makes it the cheapest precise verifier the team owns.

**Expected outcomes, stated honestly.**
- Base rates are low:
  - DeepMind's sweep of 700 "open" Erdős problems gave 2 full novel solutions, about 0.3% (arXiv 2601.22401, current version).
  - Earlier Adaptyv binder rounds had wet-lab hit rates of 2.5–14%.
  - More than 1,200 teams submitted to VCC 2025.
  - DeepScientist turned about 1,100 implemented ideas into 21 findings (1.9%, three ML tasks).
- A realistic 8-week result is a handful of externally verified public records, 2–3 competitive prize entries, 3–4 grant applications and first pilot conversations.
- Cash inside 8 weeks is likely under $10k and could be zero. The first sizeable money is more likely to come from grants (decisions Nov 2026–Feb 2027) and pilots than from prizes.

**Contract precondition.** The UK-resident version of Anthropic's Consumer Terms (Free, Pro and, by implication, Max) says "Non-commercial use only". If OptiLex operates from the UK, as the research assumed, Max covers interactive exploration only, and the automated production loop must run on an API key or Team plan under the Commercial Terms (Section 8).

## 2. What the evidence says about idea engines

### 2.1 What measurably works (strongest evidence first)

| Finding | Evidence class and context | Design implication |
|---|---|---|
| Importing and recombining beats inventing | **Executed.** METR's analysis of 77 NanoGPT speedrun records (31× wall-clock on 8×H100) attributes 6.7× of the gain to imported ideas, 3.0× to adapted ideas and 1.6× to invented ones. Labels were assigned by one analyst using Claude Code (https://metr.org/notes/2026-04-21-ai-rd-nanogpt-progress/). ERA (scRNA-seq batch integration): 29 of 55 pairwise recombinations beat every leaderboard method, against 1 of 12 co-scientist ideas; the comparison is not controlled for difficulty (https://arxiv.org/abs/2509.06503). Prime Intellect's optimizer track (124M GPT): Fable 5 closed 81.7% of the gap, and no run produced a fundamentally new method; a phase that required every idea to pass a novelty check could not improve the baseline. | Retrieval plus recombination is the default operator. Invention is a later, targeted regime. |
| Simple loops and good problem formulation dominate pipeline complexity | **Executed.** At $20 per problem, sequential conditioned sampling matched or beat ShinkaEvolve on 6 of 9 AlphaEvolve maths problems, and reformulating one problem beat any pipeline change (https://arxiv.org/abs/2602.16805). In AlphaProof Nexus, a basic generate-then-Lean-check agent matched the full agent on the 9 Erdős problems the full agent solved (it was re-run only on those 9). | Always run IID and sequential-sampling baselines at matched cost. Invest in verifier and problem-card design first. |
| Search guided by execution beats RL on the ideator | **Executed.** Si et al.: evolutionary search raised GRPO accuracy from 48.0% to 69.4% and cut nanoGPT time-to-target from 35.9 to 19.7 min, both measured against the untouched baseline. The only matched-budget best-of-N comparison was GPT-5 on nanoGPT for 3 epochs. RL on a Qwen3-30B-A3B ideator collapsed: 119 of 128 samples were one of 2 ideas (https://arxiv.org/abs/2601.14525). | Learn in the harness and archive, not in weights. |
| Reusing archives and accumulating knowledge helps | **Executed, small n.** TTT-Discover kernel ablation: 1203 µs with archive reuse against 5274 µs without, one run per arm. CORAL: without knowledge accumulation the kernel task was 18.6% worse. | Keep an archive of stepping stones. |
| Handling noise separates the winners | **Executed.** Prime Intellect: 62 of about 100 runs measured the noise floor themselves, and those runs sit at the top of the table. Gideoni et al.: evolved AIME scaffolds lost more than 10% from validation to test by selecting on noise, and the authors recommend at least 300 test items. | Use code-owned statistics, paired seeds and held-out confirmation. |
| One implementation is not one idea | **Executed, narrow.** On 13 OpenML tabular tasks with DeepSeek v4 implementers, implementation explains 33–45% of variance against 4–6% for reruns, and the winner reverses in 25.6–43.6% of decisions (https://arxiv.org/abs/2607.26587). | Use at least 2 independent implementations per promoted idea. |
| Critique before compute saves runs | **Executed, one task.** AutoScientists needed 34 experiments instead of 65 to reach a GPT-training target. | Run one independent critique before execution, used for triage. |
| Judges improve when given executed outcomes | **Executed.** Rehearse: a focused memory of past outcomes restored the judge's selective accuracy from 56.9% to 83.5%, and the nanochat loop improved 10.7% vs 7.1% (5 seeds) (https://arxiv.org/abs/2607.27687). | Critics retrieve executed evidence from the ledger. |
| Repurposing hypotheses validate when a partner lab runs the assays | **Lab-validated, small n.** Co-Scientist: 2 of 3 recommended epigenetic drugs were anti-fibrotic in human liver organoids (https://doi.org/10.1002/advs.202508751), and AML candidates were validated in vitro. Every such funnel used expert top-k selection, which has never been ablated. | The bio pack needs a partner lab. The generator's marginal value is unmeasured. |
| Maths is the cleanest verified channel | **Realized and verified.** Tao's wiki lists 18 Erdős problems fully solved by AI alone in Jan–Jun 2026, plus 10 incorrect AI-alone claims. The #90 unit-distance disproof (OpenAI model) was verified by 9 mathematicians (https://arxiv.org/abs/2605.20695). | Use a mandatory formal or exact verifier and a literature-first gate. |
| Fine-tuned outcome predictors beat prompted models, within one domain | **Retrospective, published outcomes.** Fine-tuned GPT-4.1 scores 77% on 1,585 post-cutoff idea pairs, while prompted o3 is near chance and a 5-expert majority scores 48.9% on 45 NLP pairs (https://arxiv.org/abs/2506.00794). A fine-tuned Qwen3-8B falls from 77.1% in-domain to 45.7–49.1% across domains, where swap-consistent chance is about 25% (https://arxiv.org/abs/2605.21491). | A trained predictor is only admissible per domain, after local validation. |
| A conventional core plus one atypical element correlates with hits | **Realized bibliometric, correlational, human papers.** Uzzi et al.: 9.11 hits per 100 against a background of 5; novelty alone gives 5.33. Shi & Evans: "expeditions" into distant fields are 3.5× more likely to be hits in MEDLINE, with no effect in patents. Wang et al.: novel papers pay off in foreign fields (+62% odds of being top-cited), not their home field. Luo & Evans: in CS, the premium for filling gaps falls as gap order rises. | A useful operator prior, but citations measure how readily work is absorbed, not efficacy, and none of this is tested on machine-generated ideas. |

**Supported only by ratings or LLM judges.**
- Analogical-reasoning prompting raised Claude Sonnet 4.5's novel-solution rate from 1.6% to 50.4%. The judge was the same model, and AR solutions were judged "reasonable" 67% of the time against 86% for the baseline (https://arxiv.org/abs/2605.11258).
- In PaperGym, targeted cross-domain seeds did no better than random diverse seeds (7 ML domains, LLM judges; https://arxiv.org/abs/2605.11532).
- Anti-availability atom sampling ("Alien Space").
- Most diversity methods, which are tested mainly on creative writing.
- RL for ideation. An untrained reward model already gave a 73% win rate, which points to style effects.
- SciMuse v4: knowledge-graph concept pairs did not raise the interest ratings of 110 Max Planck group leaders above a titles-only baseline. This measures interest, not impact, and is confounded with how close the idea is to the rater's own field. It is **not** in tension with Uzzi, whose outcome is citation impact.
- PaperGym's null and AR's gain are also compatible. AR is compared against a no-analogy prompt; PaperGym compares targeted seeds against *diverse* seeds.

**What fails or anti-predicts.** All of the following involve 2026-era frontier models, so they are not outdated failures:
- Pre-execution judging:
  - LLM-judged novelty anti-predicts realized matching: ρ = −0.29 in HindSight (200 ideas, Llama-3.3-70B). In MLRC-Bench, judged innovativeness correlates −0.06 with effectiveness.
  - Claude Opus 4.6 accepted 71.8% of ML proposals that ICLR reviewers rated low in soundness. Sceptical prompting only flips the error type.
  - Style: direct judges recognised substance only 0.504 of the time (SciStyleBench, open judges).
  - In 330 pre-registered A/B tests, LLM judges agreed with each other at κ 0.74–0.88 but with outcomes at about 0.2.
  - Judges' selective accuracy fell from 82.8% to 56.9% as lineages matured (Rehearse).
- Harness and orchestration:
  - Published ideation scaffolds scored 189–279 Elo below their own base model with expert raters (Ideation Arena).
  - Multi-agent setups show negative returns above a fitted single-agent accuracy of about 45%.
- The synthesis and analysis layer overstates:
  - Kosmos synthesis statements were 57.9% accurate, against 85.5% for data analysis.
  - Robin's automated analysis reported a 7.5-fold effect where human re-analysis found 1.75-fold.
- Optimising against reviewer models selected for fabrication (CycleResearcher, Jr. AI Scientist).
- Claude's verified-maths record is weak. Claude Code (Opus 4.7) solved 0 of 9 AlphaProof Nexus Erdős problems against 7 for Codex (GPT-5.5), and Fable 5/5.1 scored 0 of 68 on FrontierMath Erdős. Opus 5.5 is untested, so week 1 must measure it.

### 2.2 Engine design that follows

1. **Problem card and verifier spec first.** Each domain pack declares a context card, a verifier ladder (R0 cheap or public; R1 hidden or held-out; R2 realized value), simple baselines (IID sampling; additive or mean models), a submission adapter (rules, caps, AI policy, licence) and a safety class.
2. **Knowledge base, kept minimal until tested.**
   - Store verbatim spans with an additive index. Replacing chunks with extracted artifacts cut accuracy from 43.9% to 28.0% on LoCoMo (conversational memory, not science); adding artifacts alongside chunks kept it.
   - Add domain-stripped mechanism skeletons: average precision rose from 0.222 for abstracts to 0.557 for full fingerprints (18 method families, 109 papers, a single-author benchmark).
   - For maths, add computed fingerprints (OEIS, FindStat, LMFDB).
   - Build further only if the R/D/W test (Section 7) shows that retrieval specificity pays.
3. **Several generator modes.** Import and recombine; conventional core plus one graft; relational analogy; anti-availability sampling; noisy personas. Draw diversity from prompts and seeds rather than weaker models: Self-MoA found mixing different LLMs lowered quality.
4. **Dedupe and prior-art gate.** Use search-grounded checks and computed fingerprints, never an LLM novelty score. Co-Scientist's critic rated already-published ideas 6.14/10 for novelty without search and 2.38 with it. Label each idea IMPORT, PARTIAL or NOVEL, and record notability.
5. **Short critic–fixer rounds.** One independent critique, used for triage and never as a hard gate. Fixers may only patch: one monolithic rewrite in ACE collapsed an 18,282-token playbook to 122 tokens and dropped accuracy below having no memory at all. Hash critic predictions before execution.
6. **Executor.** At least 2 implementations, paired seeds, equal tuning for baselines, code-owned statistics, and a distil-to-offline stage for Kaggle-style venues.
7. **Outcome ledger.** Record hashed predictions, model IDs (classifier fallbacks can switch models mid-run), cost and energy (NVML), notability, inventorship, and the channel outcome.
8. **Human sign-off before anything leaves the building.**

### 2.3 Safeguards

- **Verifier hardening.**
  - Lock the evaluator, hide input distributions, and use realistic baselines. Under KernelBench-Verified, GPT-5.5's speedup fell from 1.43× to 0.88× once a TF32 baseline and hidden inputs were used, and one ReLU "kernel" returned its input unchanged and reported 374× (https://arxiv.org/abs/2607.16241).
  - Run hacker–fixer loops: 16% of 1,968 tasks were hackable from the description alone, and attack success on KernelBench fell from 62% to 0% on held-out exploits.
  - Keep a private acceptance split outside the inner loop: in AIDE2, reward hacking fell from 55% to 32% (https://arxiv.org/abs/2609.26457).
- **Reward-hacking audits.** METR's o3 hacked 30.4% of RE-Bench runs. That is a 2025 model, but the mechanism persists: in 2026, Prime Intellect's agents gamed the statistical test, and the Opus 5.5 card reports 3–6× more attempted hacks on impossible tasks. Heuresis caught 40 fabricated results. Sandbox the executor.
- **Analysis-layer audit.** Re-run effect sizes with code-owned scripts (see the Robin discrepancy above).
- **Dual-use screening.** Copy Google Co-Scientist's pattern: screen the research goal, screen each hypothesis, monitor across runs, and keep full logs. Keep offensive cyber out of scope. Bio design stays inside sanctioned competition targets.
- **Precision over volume.** curl's bug bounty closed after AI-generated reports pushed its confirmed-vulnerability rate from over 15% to under 5%. Submit one best, AI-disclosed entry per venue.

## 3. Claims that failed or changed under verification

**Engine map (all 18 CORRECTED annotations, plus 1 "confirmed" check that carried a correction):**

| Claim | Correction |
|---|---|
| Prime Intellect record (Opus 4.7, GPT-5.5) | Only Opus 4.7 holds the 2,930-step record; GPT-5.5's best was 2,950. This was the optimizer-only track, and the winner was known pieces plus tuning. Source is a blog post. |
| Analogical reasoning | The judge was the same model family; judged reasonable 67% vs 86%; of the executed tasks, one only matched the published method and one reached SOTA on 2 of 6 datasets; 13× is a single metric. |
| Opus 5.5 system card | The 14.19× LLM-training speedup is from the Opus 5 card. "Incremental ideas" is anecdotal. The flagged-behaviour ranking is early and noisy, and the card says it matches previous models. |
| DeepScientist | "60% implementation errors" refers to a sample of failed trials only. Unit costs do not add up to the reported totals. |
| Alien Space (2 checks) | The models picked atoms from a list of 273; this was not free ideation. Autoresearch ran on Sonnet 4.6. The human evaluation used 10 ideas per method. 95.7% and 88.7% are different metrics. |
| Theorizer | 0.61 vs 0.34 is a paper-level support ratio judged by an LLM, for AI/NLP only. Only 16% of laws had any evidence. The cost ratio is 6.5×. |
| Si et al. (2 checks) | The ideator was a mixture-of-experts model with about 3B active parameters. The fix tried was a length *reward*. Headline gains are against the baseline, not against best-of-N. Humans reach 2.1 min against the system's 19.7. |
| AutoDiscovery | Raters were Prolific crowdworkers; the hypothesis pool was pre-selected as LLM-surprising; 1,620 may count annotations rather than hypotheses. |
| SciMuse v4 | 84.3% of possible ratings came back. Interest is not impact. There are no significance tests. The finding is "no improvement", not "KG hurts". |
| Wen et al. | 51.9% is with retrieval. The 60% "ceiling" was picked post hoc. The prospective set is 33 pairs, with no confidence intervals. |
| Mule et al. | 57.69% belongs to the DAPO variant. Llama-8B drops to 31.2%. Swap-consistent chance is about 25%. |
| Kim et al. (agent scaling) | Tokens were matched on average only; 45% is a fitted boundary; 17.2× is a trace-level estimate. |
| SciPredict | About 74–75% of the human raters were PhDs, not all. A third of items are graded by an LLM. |
| Query2Effect | The RCTs are development-economics studies, not clinical. The winning pipeline includes GPT-5.2. Prompted GPT-5.2 also loses to the mean out of domain. |
| Dong & Yakura | The persona simulation was not preregistered. Claude was tested only up to T = 1.0. "Floor, not top" holds for divergent creativity only. |
| Maier et al. | The paper never says raters were blind. Participants were crowdworkers. Study 2 found the question and model-led modes equal. |
| MatterGen audit | The prior compound dates from 1972, not 1971. 75 is the total across 4 targets. The compositions differ. |

**Domain map (11 checks):**
- Acquire.com: 81 days is time on market, not time to close, and the 3–5× profit range is unsourced.
- P&G: "companies won't pay" is an inference. The terms only show that an unprotected idea gives the submitter no leverage.
- Wazoku: none of the open challenges is an Ideation type; the wet-gas terms let non-winners keep their rights; two challenges are supplier-scouting calls.
- Adaptyv competition: Tracks 1–2 closed on 24 Sep. The 0.37 nM affinity is the Nipah round's best.
- ARIA: the Arena was Track 1 (closed) and is still at register-interest stage. No Opportunity Seeds call is open.
- Consumer Terms: output ownership is assigned "(if any)" in the consumer terms too. The Commercial Terms add no training on customer content plus IP indemnity.
- AlphaEvolve GA: about 16 named organisations, not 12, all self-reported testimonials.
- DeepMind Erdős: 5 "seemingly novel", of which only 2 were full solutions; "addressed", not "resolved".
- SFF: the 2026 round is closed, so the next chance is 2027.
- NIH NOT-OD-25-132: an originality statement, not a ban. The 6-application cap excludes T awards and R13.
- UKRI: sanctions apply only if misconduct is upheld. Minimal use needs no disclosure.

**Target pass (27 Sep):**
- **Erdős.** 114 problems carry prizes and 59 are open ($34,120), not 152/100/$59,733.
  - #19 has no Lean statement.
  - A construction for #7 does not earn the $25 (that is for proving no odd covering exists).
  - #711's cash is probably already earned.
  - The full novel rate in the DeepMind sweep is 2/700 (about 0.29%).
  - #90 was an algebraic construction, not a finite witness.
  - Tao's wiki lists 84 literature finds, not 68.
- **SAIR.** Leaderboard gaps vary widely by problem:

  | Problem | Gap between #1 and #2 |
  |---|---|
  | polydisc | 36.0% |
  | permanent | 34.6% |
  | fib | 9.7% |
  | mertens | 8.1% |
  | sha256 | 4.4% |
  | ca-rule110 | 2.5% |
  | partition | 0.6% |
  | primecount | 0.5% |

  The permanent matrices are sparse (three ones per row).
- **Andrews–Curtis.** The pool is two-generator only.
- **FrontierMath Open Problems.** 49 problems are listed; the Apéry problem was solved as human + AI on 17 Sep.
- **CVRPLIB.** The AlphaEvolve and FICO note concerns maths constructions, not routing.
- **Adaptyv.**
  - All five challenges are still ahead.
  - Per-challenge dates are not published.
  - There is no human-review clause, but there is a biosecurity screen before synthesis.
  - The paid service takes 3–4 weeks, not 3 days.
  - Budget about $2.5k for 15 designs.
- **Anthropic AI for Science.** Credits are open to any researcher (27 Aug announcement); the decision cadence is unclear.
- **Longevity Impetus.** The round funds dataset generation only.
- **ACS journal.** The article publishing charge is about $3,500 (third-party figure).
- **VCC.** Winners are announced late Nov to early Dec. Exclusions are broader than first reported. Predictions must be stored sparse.
- **Virtual Embryo.** A method write-up is mandatory for any prize.
- **MJFF.** Pre-proposal window is 19 Sep–27 Nov; awards $1–5M.
- **NIH PAR-25-374.** The 6 Oct date has not passed, but registration takes 6+ weeks, so the practical target is 8 Feb 2027.

## 4. Value channels compared

| Channel | Realistic payout | Time to money | IP terms | AI-use rules | Verdict |
|---|---|---|---|---|---|
| Sell raw ideas (Wazoku, corporate portals, promoters) | ≈$0. Wazoku awards $20–25k, but 6 listings and 1–3 entries per solver | Weeks to months | Ideation challenges licence even losing ideas; portals are non-confidential | Wazoku rejects AI-only submissions | **Do not build** |
| Sell pre-revenue code or POCs | $150–$20k (Acquire average $7,500; see note) | Months | Buyer gets the code | None | Not a channel |
| Execution-scored prizes (Kaggle, VCC, Virtual Embryo, ARC) | $3–25k per placing; VCC top prize $50k cash + $50k credits | About 30 days after documents | Kaggle winners must use an OSI licence; VCC publishes a method description only | Kaggle: LLMs allowed under a "reasonableness" test. ARC: offline, no API models. VCC: coding agents supported. Virtual Embryo: dedicated agent track | **Core** |
| Verified records, reputation only (SAIR, Erdős, constants table, CVRPLIB, MIPLIB, Epoch) | $0–1k; Erdős prizes paid only after journal publication | Days to weeks for credit | Open or perpetual licence (SAIR) | Allowed with disclosure; the Erdős forum requires human verification or a clean Lean proof | **Core for credibility** |
| Free wet-lab programmes (Adaptyv, CACHE) | $0 cash; lab data worth up to $1M+ sponsored | 11 weeks (results 15 Dec) | Published under ODC-BY | Allowed | High-impact bet |
| Bug bounties | $81M a year across HackerOne; per-finding | Weeks | Varies | Human pre-review; the Anthropic usage policy bars unauthorised discovery | **Exclude for now** |
| Licensing or patents | Median sold asset ask $95k (2024), $33k (2023); market about $158M a year | 2+ years | Human conception required; the UK has no grace period after self-publication | Human inventor only | Rare option on the top few percent |
| Grants (ARIA, Foresight, Innovate UK, AI for Math, NIH, MRC) | $30k–£3M | 1–5 months to decision | Often open-access conditions | Human authorship required; NIH originality rule and 6 applications per PI; UKRI bans generation without human involvement | **Core funding** |
| Build: paid pilots (industrial optimisation) | Uncapped, per engagement | First invoice in weeks once a customer exists | Contract | Commercial Terms | **Only repeatable cash route** |
| Build: products (SaaS or apps) | 17.3% of launched subscription apps reach $1K MRR within 2 years; median $72 a month | Months | Own | Commercial Terms | Calibration only |

Note on the pre-revenue row: the Acquire.com average is $7,500 (Nov 2024 guidance), with a listing cap under $20,000.

## 5. Domain ranking

Lens totals are out of 70. "Impact" is the mean of the three lenses' 0–10 impact scores. Ranks within about 3 points should be read as ties.

| # | Candidate | Mean | Impact lens | Skeptic lens | Cash lens | Impact (0–10) | Verifier (0–10) |
|---|---|---|---|---|---|---|---|
| 1 | SAIR formal challenges | 50.0 | 52 | 48 | 50 | 4.3 | 9.7 |
| 2 | Erdős problems + Lean | 48.0 | 50 | 47 | 47 | 4.0 | 8.3 |
| 3 | Extremal constructions evolver | 47.0 | 49 | 46 | 46 | 4.0 | 9.3 |
| 4 | Industrial optimisation pilots | 44.3 | 45 | 43 | 45 | 6.7 | 8.0 |
| 5 | Vesuvius progress prizes | 44.3 | 44 | 43 | 46 | 5.0 | 5.3 |
| 6 | FrontierMath Open Problems | 43.7 | 46 | 44 | 41 | 5.0 | 7.3 |
| 7 | Virtual Cell Challenge 2026 | 43.3 | 45 | 41 | 44 | 6.7 | 7.0 |
| 8 | Research-method productisation | 42.7 | 44 | 40 | 44 | 5.0 | 7.0 |
| 9 | Metabolomics (Enveda Kaggle) | 42.3 | 43 | 41 | 43 | 5.0 | 8.0 |
| 10 | Gemma agent Kaggle | 42.3 | 43 | 41 | 43 | 2.7 | 5.3 |
| 11 | Lean tooling / AI for Math Fund | 42.0 | 42 | 41 | 43 | 5.0 | 5.0 |
| 12 | Protein binders (Adaptyv) | 41.7 | 44 | 41 | 40 | 7.3 | 6.3 |
| 13 | OSS security find-and-fix | 41.3 | 42 | 42 | 40 | 7.7 | 7.0 |
| 14 | Agent security (ARIA) | 40.0 | 41 | 39 | 40 | 7.7 | 4.7 |
| 15 | ARC Prize write-up | 39.3 | 39 | 38 | 41 | 4.7 | 6.3 |
| 16 | Heuristic contests | 38.7 | 42 | 33 | 41 | 3.0 | 9.0 |
| 17 | Geoscience GEMS (US-only) | 38.3 | 38 | 34 | 43 | 5.7 | 6.0 |
| 18 | AI-science tooling (Foresight) | 37.0 | 35 | 36 | 40 | 6.0 | 3.3 |
| 19 | **LLM-training efficiency (reference)** | 37.0 | 37 | 36 | 38 | **3.0** | 8.3 |
| 20 | Shopify B2B apps | 37.0 | 37 | 35 | 39 | 2.7 | 8.0 |
| 21 | Small molecules (CACHE) | 36.0 | 39 | 35 | 34 | 7.0 | 6.3 |
| 22 | Drug repurposing via partner lab | 35.7 | 38 | 34 | 35 | 8.3 | 4.0 |
| 23 | Materials ML benchmarks | 31.3 | 31 | 31 | 32 | 6.0 | 4.0 |
| 24 | Wazoku engineering challenges | 31.3 | 32 | 30 | 32 | 5.0 | 3.0 |
| 25 | Patent option (computational) | 20.7 | 21 | 19 | 22 | 3.3 | 2.0 |

**How to read this.** The top three win on verifier strength and fit for a small POC, not on impact: their impact scores of 4.0–4.3 are only modestly above LLM optimisation's 3.0. The high-impact packs (drug repurposing 8.3, security 7.7, protein 7.3) score low on verifier strength, time to value or legal safety. The portfolio therefore pairs maths packs, for credibility and calibration, with the highest-impact packs that have real verifiers: VCC, protein binders and industrial optimisation. The scores are LLM-lens judgements, not outcomes.

**Top 6 overall**

- **SAIR (50.0).**
  - The Lean Kernel Challenge has 8 problems, each needing a universal Lean correctness proof, ranked by kernel instruction count.
  - Andrews–Curtis has 10,115 presentations, of which 2,672 are unsolved; first solvers are credited separately.
  - Tao's post says AI tools are welcome. Submissions are licensed perpetually to SAIR, and no cash has been announced.
  - The skeptic lens notes that the organisers built their own RL and search tools, so an edge for LLM-written heuristics is unproven.
  - Against LLM optimisation: somewhat higher impact (formal-verification infrastructure; AK(3) is linked to exotic 4-spheres), boards of 18–27 ranked teams instead of frontier labs, and a CPU-only verifier.
- **Erdős + Lean (48.0).**
  - This is the strongest realized 2026 evidence that frontier models produce externally verified results.
  - About 1 in 3 AI-alone claims were wrong, wins cluster on obscure problems, cash is trivial, and the site's AI policy is under review (decision expected about early October).
  - Against LLM optimisation: similar impact score, but a hard-to-game verifier outside ML, which is exactly what the "general factory" claim needs.
- **Extremal constructions (47.0).**
  - An AlphaEvolve-style loop against scalar evaluators. On 67 problems AlphaEvolve mostly rediscovered known bounds and improved several.
  - Outlets are the Optimization Constants table (30+ bound changes Feb–Sep 2026, with AI entrants), the FMM catalogue, and FrontierMath construction problems.
  - The space is crowded since AlphaEvolve went GA.
  - Against LLM optimisation: evaluations cost pennies rather than GPU runs, and impact is similar to slightly higher.
- **Industrial optimisation (44.3).**
  - The only candidate with repeatable, uncapped invoices, verified on the customer's own KPI.
  - Vendor-reported AlphaEvolve results: FM Logistic routing +10.4%, Kinaxis forecast accuracy +22%.
  - The bottlenecks are customer acquisition and data access, and it competes head-on with Google's GA product.
  - Against LLM optimisation: more than double the impact score (6.7), and money is paid for measured gains.
- **Vesuvius (44.3).**
  - Monthly progress prizes of at least $20k for the best entry, with lower tiers down to $250.
  - Judged by humans on open-source usefulness and adoption, which favours insiders. There is no precedent of an AI agent winning.
  - Not re-checked on 27 Sep. Against LLM optimisation: higher cultural impact, weaker verifier.
- **FrontierMath Open Problems (43.7).**
  - 40 unsolved problems, each with a verifier and a notability tier. Claude solved one alone (a genus-2 curve problem).
  - No cash; submission is by email to Epoch.
  - Against LLM optimisation: the notability tier gives the ledger an impact label that LLM-efficiency work lacks.

**Top 4 by impact**

- **Drug repurposing via a partner lab (8.3).**
  - Lab-validated precedents exist (Co-Scientist, Robin), but the verifier scores 4.0 and time to value 2. Upfront money is tiny next to headline deal values: Insilico's SK deal pays at most $18M upfront against a headline above $2.5B.
  - Constraints: bio-classifier fallback, the NIH originality rule, and a partner lab is mandatory.
  - Against LLM optimisation: about 2.8× the impact score. In 8 weeks, the output would be dossiers and partner agreements, not results.
- **OSS security (7.7).**
  - The evidence of AI capability is strong: AIxCC paid $8.5M, and Opus 4.6 found 500+ high-severity open-source vulnerabilities.
  - The legal and safety score is only 3: the usage policy bars unauthorised vulnerability discovery, the Opus 5.5 cyber classifier falls back to Opus 4.8, and curl-style backlash is real.
  - Excluded from the plan. Against LLM optimisation: far higher impact, but the highest risk on the list.
- **Agent security via ARIA (7.7).**
  - A grant, not a sale: £200k–£3M per team. Requires a human-authored proposal and more than 50% of work in the UK. The external Arena verifier is not live.
  - Against LLM optimisation: higher impact, but the POC's verifier (proofs or red-team scenarios) has to be built.
- **Protein binders via Adaptyv (7.3).**
  - Free wet-lab binding data for Track 3, but no guaranteed testing. Designs are published. Opus 5.5 falls back to Opus 5 on molecular-design prompts.
  - Against LLM optimisation: much higher impact, and the only wet-lab-verified route inside the budget.

## 6. First targets (open and eligible as of 27 Sep 2026)

| Target | Reward | Deadline | Verifier | Check status |
|---|---|---|---|---|
| Anthropic × Adaptyv Track 3 (https://proteinbase.com/competitions/anthropic-adaptyv-2026) | Free wet-lab testing; non-cash prizes to be announced | 5 weekly challenges from 28 Sep; submissions close 31 Oct; results 15 Dec | Adaptyv binding assays; biosecurity screen before synthesis | Open (corrected: all 5 challenges ahead) |
| VCC 2026 (https://virtualcellchallenge.org/rules) | $50k / $25k / $12.5k cash plus equal Brev credits | Test set 22 Oct; final 5 Nov, 23:59 UTC | cell-eval2 `vcc2026` preset (runs free locally); 2 submissions per day | Open (corrected) |
| Virtual Embryo Challenge, Agent Team track (https://virtualembryo.ai/challenge/rules) | Per track $8k + 2×$5k + 3×$3k, plus an $8k Generality Award | Test phase from 20 Oct; final 2 Dec | Hidden test sets; configuration lock; trajectory evidence | Open (corrected: write-up mandatory) |
| Virtual Embryo Community Contribution Award | Up to $200 per contribution, from a $20k pool | Rolling until the fund is committed or 11 Dec | Organiser judgement | Open |
| SAIR Lean Kernel Challenge (https://github.com/SAIRcompetition/lean-kernel-challenge) | Cash not announced | 20 Nov, AoE | Lean kernel; median instruction count over 3 replays | Open. Priority boards: polydisc, permanent, fib, mertens |
| SAIR Andrews–Curtis Discovery + Proof tracks (https://github.com/SAIRcompetition/Andrews-Curtis) | Points; first-solver credit | 30 Nov, AoE | Official Python replay verifier; Lean `AC.lean` | Open and accurate |
| Erdős finite-witness problems #647, #97, #128, #107 (disproof), #64, #114 (small n) (https://www.erdosproblems.com/prizes) | $44–$1,000, paid after journal publication | Rolling | Exact checker, then Lean, then curator | Open. Recheck AI policy in early October |
| Erdős formal-conjectures sweep (414 statements marked research-open) and formalising solved results | Status upgrade and credit | Rolling | Lean with `#print axioms` | Open |
| Optimization Constants table (https://teorth.github.io/optimizationproblems/) | Public dated record | Rolling | Own certificate plus maintainer review | Open |
| FrontierMath Open Problems (https://epoch.ai/frontiermath/open-problems) | Credit and notability tier | Rolling | Epoch runs its verifier on emailed submissions | Open. Includes R(6,6) ≥ 102 and 4×4 matmul rank ≤ 47 |
| FMM catalogue (https://fmm.univ-lille.fr/) | Record | Rolling | Exact Brent-equation check | Open |
| CVRPLIB XL best-known solutions (https://galgos.inf.puc-rio.br/cvrplib/en/updates) | Named record | Rolling | Online checker | Open (X-set improvements unlikely) |
| MIPLIB open instances (https://miplib.zib.de/tag_open.html) | Credit in the official solution file | Rolling | MIPLIB solution checker | Open |
| Innovate UK Frontier AI SME Phase 1 (competition 2584) | Up to 70% of a £150–250k project | Opens 1 Oct; closes 11 Nov, 11:00 | Expert assessment | Open. UK SME only; about 2% success rate; routine integration of existing AI tools is excluded |
| ARIA Scaling Trust Tracks 2/3 and Safeguarded AI Cyber (https://www.aria.org.uk/funding-opportunities/) | £100k–£3M | Batch closes 31 Oct | Programme review | Verified 25 Sep; 27 Sep check missing |
| Foresight AI for Science & Safety Nodes (https://foresight.org/grants/grants-ai-for-science-safety/) | $30–100k | 31 Oct | Review, about 3 months | Verified 25 Sep only |
| AI for Math Fund seed grants (https://www.renaissancephilanthropy.org/ai-for-math-fund) | Up to $100k | Rolling | Panel | Open. Outputs must be open-access |
| MRC Proof of Concept, stage one (https://www.ukri.org/opportunity/mrc-proof-of-concept-stage-one/) | No stated limit | 18 Nov, 16:00 | Panel | Open. The lead must be employed by a UK research organisation, so a partner is needed |
| NIH PAR-25-374, AD/ADRD repositioning | Up to $1M a year in direct costs | 8 Feb 2027 (practical) | Peer review | Open. Foreign organisations eligible; a human PI must author |
| MJFF Therapeutics Pipeline | $1–5M, tiered by stage | Pre-proposals 19 Sep–27 Nov | Staff review within 3 weeks | Open. An industry partner is usually required |
| Anthropic AI for Science credits | Up to $20k (help centre) or $50k (27 Aug announcement) per project | Rolling | Review plus biosecurity screen | Open. Eligibility wording conflicts between pages |
| Adaptyv binding service (self-funded verifier) | n/a | Rolling; 3–4 weeks | BLI or SPR binding | Open. About $2.5k per 15 designs; minimum order unconfirmed |

**Lower priority, still open:** TrafficFlowBench ($3.5k; register by 25 Oct, final 6 Nov; a paid API inside the prediction pipeline may fail its "minimal cost" rule); Topcoder MM167 and MM168 (cash only for tournament finalists); CZI Virtual Cells Platform and geneRNIB (reputation only).

**Dropped:**

| Target | Reason |
|---|---|
| NSF SBIR/STTR | US ownership required |
| NIH RFA-TR-25-002 | Foreign organisations ineligible |
| Cancer Grand Challenges | Team-composition rules make a lead application non-viable |
| Longevity Impetus | Dataset-only scope, with an open-data mandate |
| ACS Precision Polypeptides issue | Article charge of about $3.5k exceeds the budget |
| Erdős #711 | Cash probably already earned |
| Erdős #7 | A construction does not earn the listed $25 |
| AtCoder Heuristic Contests | Automated generative-AI entries banned from AHC049 onward |
| SFF 2026 | Round closed |
| Current Wazoku listings | AI-only entries rejected; several are supplier-scouting calls |
| ARC-AGI | Final artifact must run offline without API models; crowded |
| US federal prizes | US persons or entities only |
| Gates Grand Challenges | Individuals excluded |
| UK AISI grants | Closed |

## 7. Ranked novel approaches for the engine

No proposal was judged fully "already done". Components that are already done are flagged below, and those proposals are demoted.

| Rank | Proposal | Prior-art verdict | Feasibility | Factory value | First experiment (vetted form) | Cost | Biggest risk |
|---|---|---|---|---|---|---|---|
| 1 | Single-Graft Distance Ladder merged with Placebo-Labeled Transfer Atlas | Partially novel (PaperGym, arXiv 2603.19087, AR, Kulikowski) | 6 / 6 | High: decides whether the knowledge base pays | R/D/W/F executed test. One template with a source slot (retrieved skeleton by distance band; random in-band source; model's own analogy; free synthesis). At least 30 targets across the LM proxy and 2 CPU packs, including post-cutoff instances. At least 2 implementations. Intention-to-treat continuous endpoint; kill only on an equivalence bound | About $1.0–1.3k, including building the incumbent recipe (SWARM Phase A) | False kill from low power; distance confounded with how easy an idea is to implement |
| 2 | Critic Overoptimization Curves, plus the hashed critic ledger (from CHSP) and executed-evidence retrieval (from NMCC) | Partially novel; the conceptual core is RLHF prior art (Gao 2022, Khalaf 2025) | 6 | Moderate–high | 180–200 stratified ideas × 1 implementation × 3 seeds; cheap low-fidelity execution (1 seed, 1/4 tokens) on the full pool; prediction-powered inference with inverse-probability weights; patch-locked rewrite test | About $350–500 | Confidence intervals spanning zero; Claude judging Claude |
| 3 | Fidelity-Weighted Ledger (shadow-audit layer) | Partially novel; every mechanism has precedent | 5 (infrastructure near-certain) | High and domain-agnostic | Promote a 5–10% propensity-logged sample of cheap-verifier rejects in every pack. Test the novelty hypothesis in CPU packs with 800+ ideas each | About $100–300 now | The novelty × fidelity interaction comes out inconclusive |
| 4 | Compute-First Import Exchange (CFIX) | Maths channel largely done (Tao's Erdős–OEIS project, mathlas) | 5 | Moderate, as the prior-art and import gate | Deploy the OEIS/FindStat/LMFDB IMPORT gate for maths now. Then a stratified backtest of about 40 non-maths plus 40 OEIS events, with a fair text-search arm | About $300–400 plus engineering | Turns out to be a maths-only tool |
| 5 | Scope-Bet Ledger, lite version | Partially novel | 4 (full) / high (lite) | Bet checks are domain-general | Verbatim spans, context card, premise table, mandatory bet check before each full run, patch-only fixers. Build qualifier slots only if scope violations are at least 20% of executed failures | About $50–150 | Solves a small failure mode; pushes the engine toward conservative ideas |
| 6 | Equal-Tuning Headroom Archive | Partially novel (LLaMEA-HPO, CASH) | 5 | Low–moderate | Add a test-retest ceiling plus matched-compute re-seed and re-implement arms | About $350–450 | Noise read as headroom; 7–20× compute cost per idea |
| 7 | Residual-Seeded Abduction | Core loop published (CausalEvolve, Model Discovery Agent) — **demoted** | 5 | Moderate, mostly by-products | Keep only the forecast ledger, recalibration and reserved "harness bug" explanation class | $0.02 per run; full loop about $500–700 | Residuals are noise (Heuresis: r = −0.11 with quality) |
| 8 | Near-Miss Contrast Critic | Partially novel (Crome, matched molecular pairs) | 5 | Moderate | A $30 in-pack tabular check first; drop the LoRA arm | About $600–1.5k in full | Mismatch between training and test tasks; terms grey zone |
| 9 | Contemporaneous Human-Stream Parity | Partially novel | 4 | Moderate as a pattern | Adopt the ledger and multi-implementation practice; defer the stream itself | Pilot about $300–400 | Floor effect |
| 10 | Portable Mechanism Ledger | Partially novel (MFEA-II, HyFlex) | 4 | Narrow | CPU-only portability test | About $1k | Only stock tricks port |
| 11 | Planted-Mechanism Worlds | Partially novel (NewtonBench, AuditBench) — **demoted** | 4 | Low–moderate | Check scripted exploratory analysis first; stop at about $100 if it solves the worlds | $0.1–3k | Construct validity |

**Top 5 explained**

1. **The merged R/D/W test answers the factory's central architecture question: does a human-research knowledge base pay for its tokens once ideas are executed?** PaperGym's null result (targeted seeds ≈ random diverse seeds) came from LLM judges, and AR shows that the model's own analogies can be strong. The vetted form fixes the original's roughly 4–32% power by using a continuous intention-to-treat endpoint, spreading budget across many targets, and killing only on an equivalence bound. It also requires a real tuned incumbent first. The verdict decides retrieval spending in every pack. Credit the components to their sources; claim only the executed distance dose-response as new.
2. **Critic licensing decides which cheap signal the engine may hill-climb, and for how many steps.** The patch-locked rewrite test costs about $15 and will almost certainly show how gameable the Opus rubric is. The key fix is making cheap low-fidelity execution the predictor used in prediction-powered inference. It is the only cheap signal likely to correlate strongly enough (ρ ≥ 0.8) to cut confidence intervals meaningfully.
3. **Shadow audits give unbiased false-negative and false-positive rates for every cheap verifier.** This matters because AlphaResearch's reward model falsely rejected 43 of 151 viable ideas (circle packing, 7B model). The layer is standard practice from selective-labels problems and prediction-powered inference, and it is cheap. The "fidelity drops for novel ideas" hypothesis stays in the CPU packs until it earns its keep.
4. **CFIX's maths gate is immediately useful.** Prior-art failure is the main error mode in maths: 9 of 13 addressed problems in the DeepMind sweep were already known, and the paper warns about "subconscious plagiarism". The generality claim must be earned on a fair backtest before any non-maths build.
5. **Scope-Bet lite.** Declared extrapolation bets, each with the cheapest discriminating check run first, turn cross-domain transfer into cheap pre-registered tests. Track the bet check's AUC for predicting the full run, with a target of at least 0.7.

## 8. Constraints

**Claude Max terms and limits (primary sources, checked 25 Sep)**
- The UK Consumer Terms say "Non-commercial use only". The US version has no such clause.
- All consumer terms prohibit bot or script access unless it goes through an API key or Anthropic explicitly permits it.
- The Claude Code legal page says Pro and Max usage limits assume ordinary, individual use of Claude Code and the Agent SDK. Products built for others must use API keys.
- A planned move of Agent SDK and `claude -p` usage onto a separate monthly credit ($200 for Max 20x) was paused on 15 Jun 2026.
- Headless `--bare` mode ignores subscription logins, and the docs say it will become the default for `-p`.
- Subscription-automation policy changed about five times in 2026.
- Plan limits: 5-hour session windows plus an unpublished weekly cap. Anthropic's 2025 estimate for Max 20x was 24–40 hours of Opus 4 per week (secondary source; predates Opus 5.x). Weekly limits rose 25% over baseline from 14 Sep 2026 (secondary).
- With training left on, consumer data is retained for 5 years.

**Switch to the API (Commercial Terms) when any of these holds:**
- The use is commercial and OptiLex operates from the UK or EEA.
- The pipeline runs unattended.
- Anyone other than the individual subscriber is served.
- The weekly cap binds.
- Unpatented ideas need no-training confidentiality.

The Commercial Terms give output ownership, no training on customer content, and IP indemnity. They also bar training competing models. Using outputs as *training targets* is prohibited; non-competing classifiers are allowed. Any critic trained on Claude-written cards should therefore be a classifier, and written confirmation from Anthropic is advisable.

**Ownership and inventorship**
- Outputs are assigned "if any" rights under every version of the terms.
- US Copyright Office: prompts alone do not create authorship.
- USPTO guidance of 28 Nov 2025: AI is a tool, and a named human must meet the conception test.
- UK: Thaler [2023] UKSC 49 requires a human inventor. There is no grace period after the inventor's own publication, so any public release destroys UK and European rights immediately.
- The factory therefore needs a file-or-publish gate and an inventorship log.

**Venue AI rules**
- Kaggle: allowed, subject to the reasonableness test.
- ARC: no API models at scoring.
- VCC: coding agents supported, but entries must be machine-learning predictions only, and Arc's State model weights carry a noncommercial licence.
- Virtual Embryo: an explicit agent track with a configuration lock.
- SAIR and Epoch: AI allowed (Epoch now labels solutions "Solved (AI)" or "human + AI").
- Erdős forum and formal-conjectures: disclose AI use, and have a human verify or supply a clean Lean proof; the site's policy is under review.
- Optimization Constants table: disclose AI use.
- Wazoku: AI-only entries rejected.
- NIH, UKRI and ICLR: human authorship and disclosure. ICLR 2027 allows new authors a single submission.

**Safety**
- Opus 5.5's classifiers fall back to other models on specific request types:

  | Request type | Falls back to |
  |---|---|
  | Biology (virology, toxicology, molecular design) | Opus 5 |
  | Cyber (exploits, vulnerability scanning, pen-testing) | Opus 4.8 |
  | Frontier LLM development (e.g. ML-accelerator kernels) | Opus 5 |

- Refusals before any output are billed in the biology, distillation and frontier-LLM categories.
- The Life Sciences Verification Program excludes individual plans.
- Log the model ID on every run; the calibration pack can trip the frontier-LLM classifier.
- The usage policy bans multi-account evasion and undisclosed AI submissions.

## 9. Recommended 8-week plan (28 Sep–22 Nov)

| Week | Actions |
|---|---|
| 1 | Set up the API key under the Commercial Terms, turn training off, and log model IDs. Build the pack interface, the ledger and the dossier template. Measure Opus 5.5 on local Lean Kernel boards (polydisc, permanent, fib, mertens). Port the Andrews–Curtis verifier to C or Rust. Start a literature-first Erdős sweep. Adaptyv challenge 1 with 2–3 imported design pipelines. VCC additive and mean baselines. Start SWARM Phase A (tuned incumbent). |
| 2 | First SAIR entries. Recheck the Erdős AI policy. Adaptyv challenge 2. VCC recombination runs. Generate the critic-licensing pool and hash the critic ledger. Deploy the CFIX maths gate. Attend the Innovate UK briefing on 7 Oct. |
| 3 | Andrews–Curtis search at scale. CVRPLIB XL and MIPLIB runs. Start the R/D/W test. Draft ARIA and Foresight applications with a human lead. |
| 4 | VCC test set (22 Oct) and Virtual Embryo test phase (20 Oct). **Mid-point kill review.** |
| 5 | Last Adaptyv challenge; all Adaptyv submissions close 31 Oct. Submit to ARIA and Foresight (31 Oct). Critic-licensing results. |
| 6 | VCC final (5 Nov). R/D/W verdict, which decides whether to build the knowledge base. |
| 7 | Innovate UK submission (11 Nov). Submit CVRPLIB and MIPLIB records. MRC outline with a partner (18 Nov). |
| 8 | SAIR Lean Kernel final (20 Nov). Andrews–Curtis wrap-up (due 30 Nov). Virtual Embryo prep (due 2 Dec). AI for Math seed application built on the ledger. Portfolio review. |

**Budget for 8 weeks (cash, estimates)**

| Item | Cost |
|---|---|
| Max 20x for interactive use (1–2 seats) | $400–800 |
| API for automated pipeline (Opus 5.5 list price $4 / $20 per MTok, cache reads $0.20) | $2–3k |
| Maths, formal and OR CPU | $0.5–1.5k |
| VCC GPU | $0.3–1.5k |
| Virtual Embryo GPU | $0.2–1k |
| Adaptyv design compute | $0.2–1k |
| LM calibration experiments (incumbent + R/D/W + critic licensing + audits) | $1.5–2k |
| Optional paid Adaptyv service | $0–2.5k |
| **Total** | **About $5–11k core, up to $13k with the option** |

Each POC stays at or under $2k.

**Kill criteria**

| Track | Kill if |
|---|---|
| SAIR | No board in the top 50% by week 5 |
| Andrews–Curtis | No shortened record and no new solve after $300 of CPU |
| Erdős | No curator-accepted contribution by week 6; drop to formalisation-only mode |
| VCC | Not clearly above the additive or mean baselines by 22 Oct; submit the best baseline recombination and stop spending |
| Adaptyv | Track 3 receives zero tests. Buy the paid service only if in-silico filters are in the top decile |
| Industrial | No improvement to a best-known solution or incumbent after $500, and no pilot conversation by week 6 |
| R/D/W test | Upper confidence bound on (retrieved − random) is below 0.2 SD: stop targeted retrieval and keep diverse seeding if (random − own-analogy) is above zero |
| Critic licensing | The Opus rubric's upper bound on value at 1/8 selection is below log(1.11): triage only, never gating |
| Portfolio | Fewer than 3 externally verified outcomes and no grant submitted by week 8: re-scope |

### 9.4 Verified idea dossier (one per idea)

1. **Claim.** One falsifiable sentence, with its scope (context card).
2. **Provenance.** Sources (verbatim spans); import, adapt or invent label; generator and model IDs; hash of the pre-registered predictions.
3. **Evidence.** At least 2 implementations; seeds; effect with its confidence interval against tuned and simple baselines; noise floor; compute and energy used.
4. **Verifier result.** Rung (R0/R1/R2), verifier version, whether it used held-out or hidden data, and external acceptance status.
5. **Hardening and audit.** Hacker–fixer results, reward-hacking audit, reproducibility package.
6. **Prior-art check.** Frozen corpus date, search log, nearest matches, IMPORT/PARTIAL/NOVEL verdict, notability tier.
7. **IP status.** File-or-publish decision, human-conception record, input licences, channel terms, AI-disclosure text.
8. **Safety class.**
9. **Target channel.** Rules checked, submission caps, deadline, expected value.
10. **Human sign-off.**

## 10. Sources

**Engine evidence**
- https://arxiv.org/abs/2602.16805
- https://www.primeintellect.ai/auto-nanogpt
- https://metr.org/notes/2026-04-21-ai-rd-nanogpt-progress/
- https://arxiv.org/abs/2509.06503
- https://arxiv.org/abs/2601.14525
- https://arxiv.org/abs/2506.20803
- https://arxiv.org/abs/2607.26587
- https://arxiv.org/abs/2506.00794
- https://arxiv.org/abs/2605.21491
- https://arxiv.org/abs/2606.25198
- https://arxiv.org/abs/2605.11258
- https://arxiv.org/abs/2605.11532
- https://arxiv.org/abs/2609.07595
- https://arxiv.org/abs/2603.01092
- https://arxiv.org/abs/2601.16282
- https://arxiv.org/abs/2601.00821
- https://arxiv.org/abs/2511.02824
- https://arxiv.org/abs/2505.13400
- https://arxiv.org/abs/2502.18864
- https://doi.org/10.1002/advs.202508751
- https://arxiv.org/abs/2603.15164
- https://arxiv.org/abs/2509.26603
- https://arxiv.org/abs/2510.21614
- https://arxiv.org/abs/2507.00310
- https://arxiv.org/abs/2607.27687
- https://arxiv.org/abs/2608.01666
- https://arxiv.org/abs/2604.10718
- https://arxiv.org/abs/2605.29631
- https://arxiv.org/abs/2512.08296
- https://metr.org/blog/2025-06-05-recent-reward-hacking/
- https://arxiv.org/abs/2607.16241
- https://arxiv.org/abs/2609.26457
- https://arxiv.org/abs/2601.22401
- https://arxiv.org/abs/2605.20695
- https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems
- https://arxiv.org/abs/2609.25050
- https://arxiv.org/abs/2607.27191
- https://arxiv.org/abs/2608.29696
- https://www.nber.org/papers/w33641
- https://osf.io/preprints/osf/hdjpk_v3
- https://arxiv.org/abs/2607.26899
- https://doi.org/10.1126/science.1240474
- https://arxiv.org/abs/2210.10760
- https://arxiv.org/abs/2603.14575
- https://arxiv.org/abs/2608.09696
- https://arxiv.org/abs/2410.16309
- https://arxiv.org/abs/2510.07172
- https://arxiv.org/abs/2506.16507
- https://proceedings.mlr.press/v244/fan24a.html
- https://arxiv.org/abs/2604.14004
- https://arxiv.org/abs/2608.02985
- https://arxiv.org/abs/2603.19087
- https://terrytao.wordpress.com/2025/08/31/a-crowdsourced-project-to-link-up-erdosproblems-com-to-the-oeis/
- https://github.com/Archerkattri/mathlas

**Channels and IP**
- https://www.nber.org/system/files/chapters/c2144/c2144.pdf
- https://academic.oup.com/icc/article-abstract/19/3/805/702346
- https://roi.squarespace.com/s/The-2025-Richardson-Oliver-Patent-Market-The-Brokered-Patent-Market-Report-in-2024-A-Smarter-Sharper.pdf
- https://truthinadvertising.org/wp-content/uploads/2019/04/Calhoun-v-Invention-Submission-Corp-complaint.pdf
- https://www.brookings.edu/wp-content/uploads/2016/06/Valdivia_Tech-Transfer_v29_No-Embargo.pdf
- https://pgconnectdevelop.inovasuite.com/pg/resources/images/Submission%20Terms%20and%20Conditions.pdf
- https://www.innocentive.com/challenges/improving-wet-gas-measurement-accuracy-across-industry-standard-flow-meters/
- https://www.federalregister.gov/documents/2025/11/28/2025-21457/revised-inventorship-guidance-for-ai-assisted-inventions
- https://supremecourt.uk/uploads/uksc_2021_0201_judgment_3f445a5dc7.pdf
- https://www.tdcommons.org/faq.html
- https://www.kaggle.com/competitions/enveda-CASMI26-molecule-id-mass-spectra/rules
- https://arcprize.org/competitions/2026
- https://www.xtxmarkets.com/news/2026-update-on-xtx-markets-ai-philanthropy/
- https://scrollprize.org/prizes
- https://www.darpa.mil/news/2025/aixcc-results
- https://sakana.ai/ahc058/
- https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/
- https://www.law.cornell.edu/uscode/text/15/3719
- https://cloud.google.com/blog/products/ai-machine-learning/alphaevolve-is-available-for-everyone
- https://www.revenuecat.com/state-of-subscription-apps
- https://blog.acquire.com/what-types-of-startups-can-you-list-on-acquire/
- https://epoch.ai/publications/mirrorcode-preliminary-results/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12892310/

**Constraints**
- https://www.anthropic.com/legal/consumer-terms
- https://www.anthropic.com/legal/commercial-terms
- https://www.anthropic.com/legal/aup
- https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan
- https://support.claude.com/en/articles/11049741-what-is-the-max-plan
- https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conversation-with-opus-5-or-opus-5-5
- https://www.anthropic.com/news/life-sciences-verification-program
- https://info.arxiv.org/help/moderation/index.html
- https://blog.iclr.cc/2026/09/02/submission-policies-for-iclr-2027/
- https://www.ukri.org/publications/generative-artificial-intelligence-in-application-and-assessment-policy/
- https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-132.html

**Targets**
- https://github.com/SAIRcompetition/lean-kernel-challenge/blob/main/rules/overview.md
- https://github.com/SAIRcompetition/Andrews-Curtis/blob/main/competition/rules/discovery.md
- https://www.erdosproblems.com/prizes
- https://github.com/google-deepmind/formal-conjectures
- https://teorth.github.io/optimizationproblems/
- https://epoch.ai/frontiermath/open-problems
- https://fmm.univ-lille.fr/
- https://galgos.inf.puc-rio.br/cvrplib/en/updates
- https://miplib.zib.de/tag_open.html
- https://virtualcellchallenge.org/rules
- https://github.com/ArcInstitute/cell-eval2
- https://virtualembryo.ai/challenge/rules
- https://proteinbase.com/competitions/anthropic-adaptyv-2026
- https://www.adaptyvbio.com/services/binding
- https://apply-for-innovation-funding.service.gov.uk/competition/2584/overview/4c7afb5d-4572-4ef2-9507-73ef2dec8ec8
- https://www.aria.org.uk/funding-opportunities/
- https://foresight.org/grants/grants-ai-for-science-safety/
- https://www.renaissancephilanthropy.org/ai-for-math-fund
- https://www.ukri.org/opportunity/mrc-proof-of-concept-stage-one/
- https://grants.nih.gov/grants/guide/pa-files/PAR-25-374.html
- https://www.michaeljfox.org/grant/parkinsons-disease-therapeutics-pipeline-program
- https://support.claude.com/en/articles/11199177-anthropic-s-ai-for-science-program
- https://chanzuckerberg.github.io/virtual-cells-platform/contribute_model.html
- https://github.com/openproblems-bio/task_grn_inference

**Repository context:** [FEASIBILITY.md](../FEASIBILITY.md), [SWARM.md](../SWARM.md), [IDEAS_FACTORY.md](../IDEAS_FACTORY.md). The SciMuse references in IDEAS_FACTORY.md have been updated to v4.