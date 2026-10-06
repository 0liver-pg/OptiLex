# Cloaking-bounds engine: run log

## Run 1 (2026-10-05): stopped by the weekly plan limit

| Stage | Status | Saved to |
|---|---|---|
| Base: tutorial (Miller & Monticone 2026, OQ15/OQ16), bound methods, prior cloaking bounds | ✅ 3 research agents; 9 claim checks (2 confirmed, 7 corrected, 0 refuted) | `research/bounds_base_research.md` |
| Formulate: 4 problem cards with computed baselines | ✅ | `experiments/cards.json`, `experiments/cards_full.json`, `experiments/cards_baseline/` (scripts, logs, design optima) |
| Generate: 6 modes | ⚠️ 1 of 6 completed (`import`: control-theory and convex-geometry imports). `duality`, `analytic`, `channels`, `conservation` and `metric` hit the weekly limit | `experiments/strategies/import.json` |
| Dedupe, triage, execute, replicate | ❌ not reached | — |
| Synthesis | ❌ hit the weekly limit | — |

No simulations were left running. Two web pages that an earlier research agent saved in the repo root were moved out of the repo.

### Problem cards (canonical point: k_c·a = π/2, b/a = 3, ε_max = 6, B = 0.1, TM, PEC core)
- **P1 Band-averaged extinction floor**, lossless free-form dielectric annulus. Bare object 5.434a. Best layered design R1 = 0.582, a thick high-index coating; the material class limits it, not the bandwidth. No prior bound exists for this card.
- **P2 Angle-limited, intensity-only metric** (scattering into a sector). Best layered design R2 = 0.607, but it raises total extinction to 3.1× bare. No published bound exists for sector metrics.
- **P3 Amount of matter**: causal Lorentz material under an oscillator-strength budget W. Best designs: R3 = 0.658 at W = 0.5, 0.597 at W = 2.
- **P4 Positive-susceptibility floor** for rotationally symmetric cloaks (per scattering channel). Best single-frequency R4 = 0.559 with 16 layers.

### Strategies so far (`import` mode)
- **S1** Calogero variable-phase equation recast as optimal control, certified by an occupation-measure LP / Lasserre moment–SOS hierarchy.
- **S2** Poisson–Jensen "waterbed" bound (Bode sensitivity integral) for the sector metric.
- **S3** Convex-geometry relaxation of the f-sum (oscillator-strength) budget for the Lorentz class.

## Resuming
The workflow script is saved in the session's workflow directory. Completed agents replay from cache. The 5 missing generator modes, dedupe and everything after must run fresh. Inputs for a fresh continuation are all in this folder: `BOUNDS_BRIEF.md`, `research/bounds_base_research.md`, `experiments/cards_full.json`, `experiments/strategies/import.json`.

## Run 2 (2026-10-06): stopped by the stop command at the user's request to pause (cause was my stop, not a usage limit; the exact limit behind the user's warning was not verified)

| Stage | Status |
|---|---|
| 5 missing generator modes (duality, analytic, channels, conservation, metric) | ✅ done |
| Dedupe into ≤ 6 families | ✅ done |
| Prior-art checks | ✅ F1, F2, F3, F6; ⏸ F4, F5 stopped |
| Soundness critics | ✅ F1, F2; ⏸ F3–F6 stopped |
| Fixer, execute, replicate, report | not reached |

All completed agent outputs (strategies, families, prior-art and critic verdicts) are in `experiments/run2/completed_agents.json`. To continue: resume workflow run `wf_561e4309-c72` from this session (completed agents replay from cache), or start a continuation from that file.

**Recovery (2026-10-06):** see `experiments/run2/README.md`. Scripts and numbers from the generators and from the stopped critics and prior-art agents were recovered from scratch space and transcripts. `invisibility/.venv` has lost its site-packages, cause unknown; the Meep env still works.
