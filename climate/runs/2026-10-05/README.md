# Climate idea engine: run of 2026-10-05

**Question (from the user):** find a technological solution to climate change that does not hurt major industries, for example efficient capture of greenhouse gases or pollutants. If efficient capture is thermodynamically impossible, find something else that satisfies as many parties as possible, from climate activists to high-carbon corporations.

**Start with [REPORT.md](REPORT.md).** The full write-ups for the eight best ideas are in [dossiers/](dossiers/).

## How the engine ran

The engine ran as one multi-agent workflow of 174 agents, plus a follow-up of 2 more. Its design follows the OptiLex research in [../../../IDEAS_FACTORY.md](../../../IDEAS_FACTORY.md) and [../../../research/FACTORY_REPORT.md](../../../research/FACTORY_REPORT.md).

1. **Physics first.** [`climate/physics.py`](../../physics.py) is a tested calculator for the minimum separation work, fan work and gigatonne-scale arithmetic. Its results were given to every agent before any idea was generated.
2. **Map** ([map.json](map.json)). Ten parallel sweeps covered known solutions, their measured performance, their bottlenecks and documented stakeholder positions. Two key claims per sweep were checked against primary sources.
3. **Generate** ([all_72_ideas.json](all_72_ideas.json)). Twelve generators with structured diversity produced 72 ideas. The generator styles were:
   - import and recombine;
   - one imported mechanism from a near field, from biology, from electrochemistry or from subsurface engineering;
   - bottleneck-first thermodynamics;
   - non-CO2 first;
   - coalition-first policy design;
   - reuse of incumbents' assets;
   - anti-availability (rarely used mechanisms);
   - systems integration;
   - Global South land use.
4. **Dedupe** ([families.json](families.json)). The 72 ideas were grouped into 50 mechanism families. One representative from each of 24 families went forward to vetting.
5. **Vet** ([vetting.json](vetting.json), [scripts/](scripts/)). Each idea went through four checks:
   - a prior-art search, labelled IMPORT, PARTIAL or NOVEL;
   - an executed Python physics and cost script, measured against the thermodynamic floor;
   - a stakeholder stance map for 11 groups, built from documented positions rather than role-play;
   - one critic, then a patch-only fixer. If the mechanism changed, the physics was re-run.
6. **Score in code** ([scored_ideas.json](scored_ideas.json)). Ideas were filtered on their physics verdict, then kept if no other idea beat them on every axis at once (the Pareto front). The axes were cost per tonne, scale and coalition score. No AI judge ranked quality or novelty.

## Caveats

- **Two definitions of the best ideas.** The workflow kept every idea not beaten on cost, scale and coalition score. The synthesis agent applied a stricter rule: it added technology readiness as a fourth axis and dropped ideas any stakeholder group is on record opposing. REPORT.md uses the stricter rule.
- **Dossier selection.** I capped the dossiers at six and picked them by coalition score. That left out two of the eight best ideas, the methane contract differential and the clinker phasedown. Their dossiers were written in a follow-up pass from the same verification records.
- **Paper results, not experiments.** Every number is a desk calculation or a sourced figure, tagged [calc], [meas], [mod], [claim] or [assume]. No idea has been tested at the bench or in the field. Each dossier names the cheapest experiment that could prove it wrong.
- **Re-running the scripts.** Run them from the repo root with `.venv/bin/python climate/runs/2026-10-05/scripts/<name>.py`. They import `climate/physics.py`.
