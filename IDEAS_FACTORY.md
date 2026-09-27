# OptiLex ideas factory: what the evidence supports

*2026-09-25, SciMuse references updated 2026-09-27. Core goal: the joint frontier of minimal data, compute and energy for maximal performance. For the broader general-factory strategy (domains, channels, targets, plan), see [research/FACTORY_REPORT.md](research/FACTORY_REPORT.md).*

Three proposals were evaluated against the literature (sources below) and one small experiment of our own (`factory_pilot/`):
(1) a swarm of about 100 agents with noisy prompts, (2) a chaotic generator ↔ soundness critic ↔ fixer loop in which an idea fails only when the fixer cannot rescue it, and (3) a knowledge base covering frontier research.

## Verdicts

| Proposal | Verdict | Why |
|---|---|---|
| 100 agents × noisy prompts | **Keep the swarm, change the noise.** | Independent agents on one model converge. In our pilot, 30 of 30 clean prompts produced near-variants of one idea. Content-free noise barely helps (a random sonnet: 0.686 vs 0.679 diversity). *Task-relevant* structured variety helps a lot: random personas and constraints 0.735–0.757, mixing model vendors 0.763, near the human level of 0.773. Cross-domain analogy gives +90–173% diversity. Diversity comes from the archive and selection, not from randomness. |
| Chaotic generator ↔ critic ↔ fixer, "fails only if unfixable" | **Keep the loop, invert the rule.** | Prompted LLM judges of research ideas are near chance (53% agreement with humans; o3 no better than random at predicting which idea wins empirically). An LLM fixer can almost always produce a plausible rescue, so under this rule ideas stop failing. Revision without external feedback often makes answers worse, novelty peaks at about 5 rounds and then declines, and sycophancy makes agents give in when pushed. |
| Knowledge base of frontier research | **Build it narrow, as verified records, and use it to sample rarely explored concepts. Test the graph layer before investing in it.** | Graph retrieval vs plain retrieval (arXiv 2502.11371, Llama-3.1 on QA and summarization benchmarks) is *complementary*, not worse. Graphs win on multi-hop, temporal and comparison questions (e.g. temporal 49 vs 26); they lose on single-hop and "no answer" questions; and they take 41–57× longer to build. None of the graph-vs-retrieval studies tests scientific ideation. The one large ideation test with expert raters (SciMuse v4, 24 Sep 2026: 110 Max Planck group leaders rating GPT-4 ideas) found that knowledge-graph-selected concept pairs gave no gain in *rated interest* over a titles-only prompt. Its connectivity measures were taken on the rater's own concept, so they do not show that less-explored fields are more promising. Retrieval quality with reranking clearly helps novelty checking (about 0.81 accuracy vs κ≈0.05). A scoped corpus is about 10–25k papers, costing about $300–700 in a Haiku batch run. |

**The key point in all three is that an idea should be judged by running it.** Our calibrated proxy (FEASIBILITY.md) detects a 1.11× effect for a few dollars. Testing an idea therefore costs about as much as the tokens an agent would spend arguing about it, and testing is far more reliable than an LLM verdict.

## The design the evidence supports

```
 seeds ──► GENERATORS ──► DEDUPE / NOVELTY ──► CRITIC ⇄ FIXER ──► PROXY LAB ──► frontier ledger
 (KB records,  (Opus 5.5 + other   (archive + KB,      (≤3 rounds; job:     (data, FLOPs, energy;     │
  analogies,    model families;     reject near-dups    make it TESTABLE,   code-owned gates)         │
  constraints)  verbalized tails)   before any critic)  not approve it)                              │
      ▲                                                                                              │
      └──────────── archive of tested ideas + outcomes; trains the OUTCOME PREDICTOR ◄──────────────┘
```

1. **Generators.** Diversity comes from task-relevant structure, not noise:
   - **Seed cards** drawn from the knowledge base: a known lever, a mechanism from another field, or a hard constraint (e.g. "no extra FLOPs", "must work at 4-bit").
   - **Personas** (e.g. "a hardware architect", "a neuroscientist of sleep replay").
   - **Verbalized sampling:** ask for five ideas with probabilities and keep only the low-probability tail.
   - **At least two model families**, since mixing vendors reached near-human diversity.
   - **Archive-conditioned prompts:** show the families already explored and ask for a mechanism outside them (novelty rejection, as in ShinkaEvolve).
   - **What to avoid:** repeated "make it bolder" loops (diversity 0.575, collapse onto shared gimmicks) and one isolated session per agent with an identical prompt (0.452, the worst configuration measured).
2. **Dedupe and novelty gate, before any critic spends tokens.** Embed each idea, cluster it against the archive, and check it against the knowledge base with facet-level reranking (Ai2 checker design). Expect about 95% of raw ideas to be duplicates.
3. **Critic ⇄ fixer, with a changed job.** The loop stays high-frequency but short:
   - At most 3 rounds.
   - The critic comes from a different model family and must cite a specific mechanism, number or paper.
   - The fixer's job is to make the idea **precise and falsifiable** (a concrete diff to `train.py` plus a predicted effect on each axis), not to certify it true.
   - After every fix, a **drift check** re-runs the novelty gate. If the "rescued" idea is now a known method, it is logged as *collapsed-to-known*, not passed.
   - **The failure rule is inverted:** an idea earns a lab slot when it is novel, testable and free of any *cited* fatal flaw. It earns *survival* only in the lab.
4. **Proxy lab** (SWARM.md tiers 1–3). This is the only judge that counts. It reports three multipliers per idea (data, training FLOPs, measured energy) and promotes only moves on the joint frontier.
5. **The compounding asset: an outcome predictor trained on our own lab results.** Off-the-shelf models are at chance at predicting empirical outcomes, but fine-tuned predictors reach 64–77%. Every executed idea becomes a labelled example, so over months the soundness agent turns into a *calibrated* filter. Nobody else has this dataset for efficiency ideas.

## Funnel economics (per day, estimates)

| Stage | Volume | Cost |
|---|---|---|
| Generate (about 100 agents, 10 ideas each) | ~1,000 raw ideas | ~$45 ($0.044 per idea, measured in the pilot) |
| Dedupe + novelty gate | → ~50–100 distinct families | ~$5 (embeddings + a reranker) |
| Critic ⇄ fixer, ≤3 rounds | → ~20–30 testable specs | ~$20–40 |
| Implement + tier-1 test | 20–30 experiments | ~$30–45 LLM + ~$5–10 GPU |
| **Total** | **~25 real experiments/day** | **~$105–135/day** |

The "100-agent swarm" is affordable, but it is the cheapest stage and not the one that matters. The binding constraints are dedupe quality and how many ideas get tested each day.

## Knowledge base: minimal version

- **Corpus:** about 15k arXiv papers from 2024–2026 on efficient LM training, pulled from OpenAlex / Semantic Scholar (metadata, SPECTER2 embeddings, citation contexts).
- **Records:** one Haiku batch pass (about $300–700) extracts {method, mechanism, claim, scale, data multiplier, compute multiplier, energy figure, source span}. A second model checks every number against its source span, because extraction of numbers from papers runs at only about 70 F1.
- **Index:** hybrid keyword + embedding search; citations come from Semantic Scholar rather than being extracted.
- **Refresh:** daily, since more than 20k AI papers appear each month and a stale knowledge base causes false-novel verdicts.
- **Reuse:** the alphaXiv MCP server and the Papers with Code archive. Add a concept graph only once the A/B test below shows it helps.
- **Use the knowledge base as a sampler, not only a library.** The model already knows the popular concepts; its failure is collapsing onto them (our pilot: 3 families out of 30; in "The Alien Space of Science", Claude Opus 4.7's ten most-used idea atoms appeared in 95.7% of its combinations). The knowledge base's distinctive value is supplying rarely used concepts as seeds, and verified numbers for novelty checks. Whether that pays off on *executed* outcomes is untested; the R/D/W test in [research/FACTORY_REPORT.md](research/FACTORY_REPORT.md) §7 decides it.
- **The A/B test that settles it:** run the same generator budget with (a) no seeds, (b) knowledge-base seeds of rarely connected concepts from within ML, and (c) knowledge-base seeds from distant fields. Score all three arms in the proxy lab, not with a judge. This tests two things at once: whether the polymath knowledge base helps, and whether ideas from distant fields beat nearby ones.

## Prior attempts at a "polymath" research knowledge base

| Attempt | Scale | Measured result |
|---|---|---|
| Microsoft Academic Graph → OpenAlex | about 250M works | Infrastructure, not a reasoning engine |
| Swanson / Arrowsmith literature-based discovery | Two separated literatures at a time | Fish oil–Raynaud's and magnesium–migraine links, later supported clinically; modern evaluations mostly rediscover known links |
| Hetionet (drug repurposing) | 47k nodes, 2.25M edges | AUROC 97% on known treatments, 70% on drugs later entering clinical trials |
| Krenn group: SemNet → Science4Cast → Impact4Cast → **SciMuse** | Up to 58M papers, 123k concepts | Predicts future concept links well (new-link AUC up to 0.93). As an idea source, SciMuse v4 (Sep 2026) found graph-selected pairs gave no gain in experts' *rated interest* over a titles-only prompt. This measures interest, not realized impact |
| Buehler (MIT): graph reasoning, SciAgents | Graph from about 1,000 papers | Striking cross-domain hypotheses (art → mycelium composites); no lab or expert validation found; judged by LLMs |
| FutureHouse Robin; Google AI co-scientist | LLM + retrieval, no curated graph | Findings confirmed in cell culture or organoids (ripasudil for dry AMD; vorinostat in liver fibrosis) |
| Microsoft Discovery | Graph-based knowledge engine | Coolant found after screening 367k candidates (company claim) |

Earlier "store all of science" projects (Cyc; Galactica, 2022; IBM Watson for Oncology) are left out of this table on purpose. They failed through hand-coding that did not scale, or through model fabrication typical of pre-2023 technology, so they say little about what a current frontier model with a verified knowledge base can do.

On combinations: the realized-impact evidence (Uzzi et al. 2013, 17.9M papers: a conventional core plus a tail of atypical combinations doubles the hit rate; Shi & Evans 2023: surprising combinations, often introduced by outsiders from distant fields, predict outsized impact) is the directly relevant evidence and supports a cross-discipline design. SciMuse's finding that distant-field pairings got lower *interest ratings* is not strong counter-evidence. It is a rating rather than an outcome, and it is plausibly confounded: raters judged fields they did not know, and the generator (GPT-4) may bridge distant fields less well. **No prior effort has connected a cross-discipline knowledge base to an executable harness with a numeric result. That combination is where OptiLex is new.**

## Our pilot: clean vs "ask for novelty" vs noisy prompts (`factory_pilot/`)

90 one-idea calls (30 per condition), each in a fresh context. The model was Opus via Claude Code headless; the installed CLI resolved this to `claude-opus-5`, not 5.5. Generation cost **$3.92, or $0.044 per idea**. An Opus judge scored the ideas blind (shuffled, unlabelled IDs), twice with different shuffles.

| | clean | ask ("avoid the obvious") | noisy (random distant concept + lens) |
|---|---|---|---|
| Distinct mechanism families (pass 1 / pass 2) | **3 / 3** | 13 / 10 | **15 / 11** |
| Families in a random subsample of 15 | 3.0 / 3.0 | 9.8 / 7.8 | 10.4 / 8.7 |
| Judged novelty, 0–2 (pass 1 / 2) | 0.13 / 0.90 | **1.27 / 1.53** | 0.90 / 1.07 |
| Share judged "no close precedent" | 0% / 0% | 27% / 53% | 10% / 7% |
| Mean soundness, 1–5 | 3.0 / 2.2 | 2.1 / 2.2 | 2.6 / 2.1 |
| Novel *and* soundness ≥ 4 | 0 / 0 | 0 / 0 | 1 / 0 |
| Lexical distance (no LLM) | 0.748 | 0.829 | 0.828 |

Findings:

1. **Mode collapse is severe.** All 30 clean ideas fell into 3 families of one known approach, selective backprop / token gating (Rho-1, Selective Backprop, Mixture-of-Depths): 13 + 12 + 5.
2. **Noise works, but no better than asking for novelty.** Both give 3–5× more families than clean. Noise gives slightly more families and the explicit request gives higher judged novelty; neither difference is reliable at n = 30. Noise is one cheap diversity lever among several, not a new pathway.
3. **Every top-rated idea has a named precedent.** Examples: auxiliary heads ≈ multi-token prediction + deep supervision; nested curriculum ≈ MatFormer + progressive stacking. The best output of 90 ideas was recombination, which is what the literature predicts.
4. **The soundness judge disagrees with itself.** Across two blind passes of the *same* model on the *same* ideas, novelty ratings matched exactly only 53% of the time and soundness rank correlation was 0.40. Clean-condition novelty moved from 0.13 to 0.90 just because the order changed. A single LLM verdict should not decide whether an idea lives or dies.
5. **The novelty/soundness trade-off appears straight away:** clean prompts were the most "sound" in pass 1 and the least novel.

Files: `factory_pilot/ideas.jsonl` (all 90 ideas), `judgements.json`, `report.json`. Re-run with `python3 factory_pilot/generate.py 30 && python3 factory_pilot/judge.py`.

## Key sources

- Si et al., ICLR 2025 (arXiv 2409.04109): LLM ideas are rated more novel, but only 5% of 4,000 are unique, and LLM judges agree with humans 53% of the time. "The Ideation-Execution Gap" (2506.20803): after execution the AI ideas lose their advantage and the ranking flips.
- Terwiesch, Meincke, Mollick et al. (2607.27553): diversity by prompting strategy, including personas, a sonnet as noise, independent sessions, "bolder" refinement and mixing vendors.
- Verbalized Sampling (2510.01171); cross-domain analogy (2605.11258).
- FunSearch; AlphaEvolve ablations; ShinkaEvolve (2509.19349); Darwin Gödel Machine (2505.22954: 50% vs 23% without the archive).
- Huang et al. 2310.01798 (self-correction without feedback hurts); sycophancy under "are you sure?" (2311.08596); VirSci novelty peak at about 5 turns (2410.09403).
- Predicting empirical AI research outcomes (2506.00794, 2605.21491): fine-tuned predictors reach 64–77%, off-the-shelf models are at chance.
- Ai2 novelty checker (2025.sdp-1.9); RAG vs GraphRAG (2502.11371); PaperQA2 (2409.13740).
