# OptiLex

Can an Opus 5.5 agent swarm find a data-efficiency breakthrough for LM pretraining?

- [FEASIBILITY.md](FEASIBILITY.md): calibration results and verdict
- [SWARM.md](SWARM.md): cheapest swarm, harness and tooling design, with a phased budget
- `pilot/`: BabyLM-2026 strict-small proxy (`prep.py` downloads and tokenizes into `data/`, `train.py` runs one training run, `grid.sh` runs the calibration grid, `analyze.py` reports the noise floor and effective-data multipliers)
- `results/`: raw per-run JSON and `summary.json`
- [IDEAS_FACTORY.md](IDEAS_FACTORY.md): evidence review and design for the idea-generation front end (noisy swarm, critic/fixer loop, knowledge base)
- `factory_pilot/`: clean vs novelty-request vs noisy-prompt pilot with blind scoring
- [research/FACTORY_REPORT.md](research/FACTORY_REPORT.md): merged strategy report for a general ideas factory: engine evidence, value channels, 25 scored domains, checked open targets, vetted engine proposals, 8-week plan
- `research/data/`: digests of the underlying multi-agent research (claims checked against primary sources)

- `climate/`: physics verifier for climate ideas (minimum separation work, fan work, gigatonne-scale arithmetic), with tests
- `climate/sorbent.py`: sorbent verifier for direct air capture (Langmuir temperature-vacuum swing: working capacity, regeneration heat, work-equivalent energy, sorbent cost per tonne), with tests
- `climate/runs/`: idea-engine runs on climate questions; each has a README, a report, verified idea dossiers and the scripts behind them
