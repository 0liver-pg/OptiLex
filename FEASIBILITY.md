# OptiLex feasibility check: can an agent swarm measure, and then find, a data-efficiency gain?

*2026-09-24. Calibration grid run locally on an Apple M1 (8 GB) with the BabyLM-2026 strict-small corpus.*

## Verdict

- **Measurement: feasible and cheap.** A 7M-parameter proxy trained on 1–4M tokens detects a data-efficiency multiplier of **1.11× with 3 seeds** (1.07× with 5). It recovers a known 3.4× effect with p = 0.0003.
- **Finding something new: plausible for a 1.3–2× gain on top of the known levers. A 10×-plus paradigm shift is not plausible.** Known levers already stack to roughly 5×. The one published large-scale autonomous-research campaign spent about $50–60k and needed about 100 human interventions to get small, mostly hyperparameter-level wins.
- **Best first campaign:** find out whether the known levers *stack*. Nobody has answered this, a swarm is well suited to it, and it produces the strong baseline that every later claim must beat.

## What the calibration grid measured

Model: 6 layers, d = 256, 6.9M parameters. Tokenizer: 8k BPE (the 10M words come to 16.9M tokens). Metric: loss on a 256k-token held-out slice covering all six sources. Each run gets its own full cosine learning-rate schedule. 12 runs in total.

| Condition | Held-out loss (mean ± sd, 3 seeds) | BLiMP-fast |
|---|---|---|
| 1M tokens × 1 epoch | 4.522 ± 0.021 | 52.7% |
| 2M × 1 | 4.199 ± 0.007 | 51.4% |
| 4M × 1 | 3.929 ± 0.014 | 53.9% |
| **1M × 4 epochs** (positive control) | **3.997 ± 0.004** | 54.8% |

| Quantity | Held-out loss | BLiMP-fast |
|---|---|---|
| Value of one doubling of data | −0.296 nats | +0.6 pts |
| Pooled seed sd | 0.015 | 0.97 pts |
| Minimum detectable multiplier (80% power, α = 0.05), n = 3 / 5 / 8 seeds | **1.11× / 1.07× / 1.05×** | 38× / 11× / 6× |
| Positive control: effective data multiplier | **3.41×** (p = 3e-4) | not significant (p = 0.09) |

What follows from these numbers:

1. **Gate on held-out loss. Do not gate on BLiMP at proxy scale.** BLiMP barely moves between 1M and 4M tokens, so at this scale it is noise. Grammar benchmarks only become meaningful at tier 2 (the full 10M words) and above. The loss-vs-benchmark gap is itself a risk, and it is the reason tier 2 exists.
2. **Repetition is a 3.4× free lunch.** This matches Muennighoff et al. (2023). A swarm measured against a 1-epoch baseline would "discover" it straight away. The baseline must therefore already include tuned multi-epoch training plus heavy regularization (Kim et al., arXiv 2509.14786: 2.3×, rising to 5.2× with ensembling and distillation).
3. **The noise floor is low enough for cheap, fast iteration.** Paired seeds (same seed and data order in both arms) would lower it further.
4. **The M1 is fine for smoke tests only** (about 8.6k tokens/s, 8 minutes for a 4M-token run). Real iteration belongs on a rented GPU.

## Headroom (from the literature, detailed in SWARM.md)

| Lever | Claimed multiplier | Shown at |
|---|---|---|
| Multi-epoch repetition (≤ 4 epochs) | ~3–4× | Up to 9B parameters (and 3.4× here) |
| Heavy regularization → + ensembling + distillation | 2.3× → 5.2× | 200M tokens |
| Synthetic rephrasing / "megadocs" | 1.5–1.8× (generation compute not counted) | 300M parameters |
| Formal-language pre-pretraining | ~1.5× | 1B parameters |
| Mixed causal + masked objective (GPT-BERT) | +9 BabyLM points over the 2024 baselines | 10M / 100M words |

The BabyLM 2025 winner beat the GPT-BERT baseline by only about 1 point, so easy architecture gains are mostly used up. **The open question is whether these levers compound.** If they do multiplicatively, 10–20× is available without any new idea.

## Kill criteria

- After Phase A (the stacking study): if the proxy fails to reproduce at least 2 of the 3 published multipliers within 2× of their stated value, the proxy does not transfer. Fix the proxy before spending on agents.
- After Phase B: if nothing beats the stacked baseline by ≥ 1.3× at tier 2, with independent replication, within about $4k, stop and write up the stacking results.

## Reproduce

```
uv venv .venv && uv pip install --python .venv/bin/python torch numpy tokenizers scipy
.venv/bin/python pilot/prep.py && ./pilot/grid.sh && .venv/bin/python pilot/analyze.py
```
