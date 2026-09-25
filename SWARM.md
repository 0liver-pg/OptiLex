# OptiLex swarm: the cheapest setup that can find a data-efficiency gain

Goal: beat a strong, compute-matched baseline on **loss at a fixed unique-token budget** — and show
the gain holds as scale grows. The research question is data efficiency, so the budget that is
fixed is *unique training tokens*. Compute is capped separately, so the swarm cannot win by
simply spending more.

## Design principles (each one targets a known failure mode)

| Principle | Failure mode it prevents (arXiv 2601.03315, 2608.14905) |
|---|---|
| Agents never own the loss, the data loader or the eval. A frozen `evaluator/` does, and runs on a separate queue. | Declaring success on bad results; leaking the test set; quietly using more data |
| Every agent call is short-lived with a fresh context that starts from `LEDGER.md` — no multi-day sessions | Losing context over long tasks; drifting from the plan |
| Promotion is decided by code (a statistical gate), not by an LLM's judgement | Trusting one noisy result |
| Winners are re-implemented from a written description by a replicator that never saw the original code | Artifacts of one particular implementation |
| The baseline is the *best known* recipe (tuned multi-epoch training + regularization), not a naive 1-epoch model | "Discovering" repetition or weight decay (a 2–5× gain that is already known) |
| A human picks the direction every day or two, from a one-page digest | Falling back on training-data defaults; weak taste in which ideas to try |

## Roles (all Opus 5.5; effort level is the cost dial)

| Role | Effort | When it runs | Output |
|---|---|---|---|
| **Director** | high | Once per result batch (~every 2–4 GPU-hours) | Ranked idea queue in `LEDGER.md`; kills dead directions |
| **Implementer** ×2–4 | medium | One call per idea | A patch to `train.py` inside a git worktree, a CPU smoke test, a job submitted to the queue |
| **Auditor** | high | Before any GPU spend over tier 1, and on every promotion | Checks the diff for data, eval or compute violations; can veto |
| **Replicator** | medium | On each tier-2 promotion | Re-implements the idea from its one-paragraph description; must reproduce the effect within its CI |

No LLM ever waits on a GPU. The queue wakes the director when results land, so billing is by event, not by the hour.

## Evaluation ladder (code-owned gates)

| Tier | What | Cost per idea | Gate to the next tier |
|---|---|---|---|
| 0 | CPU/M1 smoke: 200 steps, loss decreasing, budget counter intact | ~$0 | Runs; no violations |
| 1 | Proxy: ~20M-parameter model at 3 data budgets (4M/8M/16M tokens) × 3 paired seeds; **held-out loss only** (BLiMP is noise at this scale; see FEASIBILITY.md) | ~0.1–0.3 H100-hours (estimated, not yet measured on a GPU) | Effective-data multiplier ≥ 1.15× over the *stacked* baseline at every budget (measured noise floor: 1.11× at n = 3), and not shrinking as data grows |
| 2 | BabyLM strict-small (10M words) with the official eval pipeline plus hidden held-out loss, 5 seeds | ~2–4 H100-hours | Beats the strong baseline on hidden loss (p<0.01); replicator reproduces it |
| 3 | Strict (100M words) and a 2–4× larger model | ~20–40 H100-hours | Human decision |

## Tooling (cheapest option that works)

- **Agent harness:** Claude Code headless (`claude -p` or the Claude Agent SDK), one git worktree per implementer, all driven by a ~200-line Python orchestrator (or the `Workflow` tool). Managed Agents is a hosted alternative if you don't want to run the loop yourself.
- **Compute:** 1× H100 on RunPod community (~$2.69/h) or Vast (~$1.74–3.14/h) for tiers 1–2. Add a second GPU only after tier-1 throughput becomes the bottleneck. Use Modal ($3.95/h) only if scale-to-zero matters more than price.
- **Queue:** a directory of job JSON files on the GPU box plus `rsync` — no Kubernetes, no Ray.
- **Tracking:** `results/*.json` + `LEDGER.md` + one `analyze.py`. W&B is optional.
- **Prompt caching:** freeze the system prompt, tool list, `train.py` and the evaluator spec as the cached prefix; each call adds only the ledger delta. Cache reads cost $0.20/MTok on Opus 5.5, versus $4.00 uncached.

## Phased plan and budget

API list prices: Opus 5.5 costs $4 per MTok input, $20 per MTok output and $0.20 per MTok for cache reads. GPU: one RunPod community H100 at about $2.69/h.
Cost per agent call is an estimate: about 30 turns × about 60k context, mostly cached, comes to **about $1–1.50 per implemented idea**, about $1 per auditor pass and about $1–2 per director batch.

At tier 1, one GPU can test far more ideas per day than the agents can sensibly propose. **LLM tokens, not GPU time, are the main cost at tier 1.** So the cheap setup throttles the number of ideas (the director keeps only the best 10–20 per day) and spends on tier-2 validation instead.

| Phase | Weeks | Work | Agents | Estimated cost |
|---|---|---|---|---|
| **0: port** | 1 day | Port `pilot/` to CUDA with bf16 + `torch.compile`. Re-run the calibration at 20M parameters to measure real tier-1 cost and noise. | None (one Claude Code session) | ~$20 GPU |
| **A: stacking study** | 1 | Reproduce multi-epoch, heavy weight decay, ensemble→distill, rephrasing and formal pre-pretraining, then every pairwise combination. The output is the *stacked baseline*. | Director + 2 implementers + auditor | ~$300 LLM + ~$200 GPU |
| **B: novel search** | 2–3 | Test new ideas against the stacked baseline. Priorities: self-generated verified data, learned priors, replay-based consolidation. Promotions go to tier 2 with replication. | Director + 3–4 implementers + auditor + replicator | ~$1.5–2.5k LLM + ~$1–1.5k GPU |
| **C: scale check** | 1 | Tier 3 (100M words), only for survivors | Replicator + auditor | ~$500–1k GPU |

**Total: about $3.5–5.5k, 4–5 weeks, and about 30 minutes a day of human direction.** If the agents run through a Claude Max subscription in Claude Code instead of the API, the LLM line mostly disappears, subject to plan limits.
