# OptiLex

Can an Opus 5.5 agent swarm find a data-efficiency breakthrough for LM pretraining?

- [FEASIBILITY.md](FEASIBILITY.md): calibration results and verdict
- [SWARM.md](SWARM.md): cheapest swarm, harness and tooling design, with a phased budget
- `pilot/`: BabyLM-2026 strict-small proxy (`prep.py` downloads and tokenizes into `data/`, `train.py` runs one training run, `grid.sh` runs the calibration grid, `analyze.py` reports the noise floor and effective-data multipliers)
- `results/`: raw per-run JSON and `summary.json`
