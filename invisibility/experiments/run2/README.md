# Run 2 recovered work (2026-10-06)

Everything here was recovered after run 2 was stopped with the stop command (not by a usage limit). The agents' reasoning is not recoverable; their scripts, numbers and fetched pages are.

| Folder / file | What it is | Status |
|---|---|---|
| `completed_agents.json` | Structured outputs of the 11 agents that finished: strategies, families F1–F6, prior-art verdicts (F1, F2, F3, F6), critic verdicts (F1, F2) | Finished results |
| `generators/gen_{duality,analytic,channels,cons,metric,import}/` | Prototype scripts and numeric results behind each generator's strategies, previously only in scratch space | Prototypes. Not certified bounds; several are noted as loose or not a certificate |
| `critics/F2/` | Checks run by the F2 critic (finished) | Finished |
| `critics/F3_partial/`, `critics/F4_partial/` | Numeric check scripts started by the stopped F3 and F4 critics. They produced no results | Unrun or incomplete |
| `partial_prior_art_F4_F5.md` | Searches and pages read by the stopped prior-art agents for F4 and F5 | Leads only; no verdicts were written |

Stopped and lost without recoverable results: the F5 and F6 critics, and the F3, F4 and F5 critic verdicts.

**Environment note:** `invisibility/.venv` has lost its `site-packages` folder (the generators reported this). Its cause is unknown. The Meep environment (`.mamba/envs/meep`, which has numpy and scipy) still works, and the generators ran on it. Rebuilding `.venv` restores cvxpy, ngsolve, ceviche, scattnlay and Mitsuba.

## Headline numbers in the recovered prototypes (read as unverified leads)
- **Variable-phase relaxations (`gen_import`)** are loose: two- and three-channel relaxations reach at most 0.07 and 0.185 of the bare value, against a best design of 0.559. The grid dynamic program overestimates at coarse grids (1.43 versus an attained 1.004), so it is not a certificate.
- **Window LP (`gen_duality/window_lp.log`):** with an assumed upper bound on extinction, floors on the band average were 4.94 / 2.56 / 0.64 for upper bounds of 1× / 3× / 10× the bare 5.434. The bound weakens as the allowed extinction rises.
- **Naive angular-sector bound (`gen_cons/subharm_out.txt`):** the uncompensated version is violated by real designs at 4 of 5 angles. The compensated version holds, with ratios of 0.976 to 0.994.
- **Sum-rule check (`gen_analytic`):** the extinction sum rule matches its prediction to about 4 digits for free space (3.1416) and for a PEC core with a penumbra-type tail.
- **Per-channel floors (`gen_channels/NOTES.txt`):** the floor is nonzero at 44 of 64 sweep points but zero at the canonical point (b/a = 3, ε_max = 6). A branch-and-bound lower bound reached 0.252a versus 0.046 for the bare value on only a restricted design class.
