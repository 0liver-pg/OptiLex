# Brief: rigorous limits on invisibility (OptiLex idea-engine run)

## Goal
Pure physics. Find new, **rigorous or computable lower bounds** on how well any object can be made invisible, as a function of object size, bandwidth, the amount and kind of material available, and the invisibility metric. Then test each bound objectively.

The open target is from Miller & Monticone, "Fundamental limits in photonics and electromagnetics: a tutorial" (arXiv:2605.24738, May 2026), §5.7 and open questions OQ15/OQ16. Their status:
- Rigorous size–bandwidth–performance limits for *any* invisibility effect, given the matter in a volume, remain open.
- This includes phase-insensitive and angle-limited metrics.
- The widely quoted 3D Bode–Fano cloaking bound (Monticone & Alù, Optica 2016) is a heuristic circuit-model estimate, not a theorem.

## Scope
- **In scope:** theorems and computable bounds, together with designs that test them.
- **Out of scope:** applications, devices for hiding people, and anything about evading sensors or detection systems. Keep all work at the level of scattering physics and mathematics.

## Why this suits an idea engine
A bound makes a falsifiable claim: *no* passive design in a stated class can beat it. Any design that does beat it refutes the bound, and code can check that cheaply and without an AI judge. The quality of a valid bound is its tightness: the gap between the bound and the best design found.

## Objective test environment (validated; see `ENV.md`)
- **`sim/cloak2d.py`:** exact scattering by radially layered cylinders (TM and TE, PEC or dielectric core), with band averaging and a baseline adversary (`optimize_layers`).
  - Validated against an independent FEM solver (NGSolve) to about 2e-4, and against closed-form solutions to machine precision.
  - **Use this as the shared verifier.**
- **`sim/analytic.py`:** exact cylinder solutions.
- **scattnlay, treams:** layered spheres and T-matrices.
- **ceviche:** 2D FDFD with autograd, for free-form (topology-optimised) adversarial designs.
- **NGSolve:** FEM.
- **Meep:** broadband FDTD.
- **cvxpy:** with the Clarabel and SCS solvers, for duality and SDP bounds.

## Rules for every result
1. **Reproduce a known result first.** Before computing anything new, show the code reproduces a known limit or bound (e.g. the 1D Bode–Fano slab bound, the quasi-static sum rule, or a published T-operator bound value).
2. **State the class.** Give the material class (passive; causal dispersive vs non-dispersive; bounded susceptibility; isotropic or anisotropic), the design region, the object, the band and the metric. Falsification must use the same class.
3. **Run an adversarial falsification search.** Use at minimum `optimize_layers`; add free-form ceviche designs where feasible. Report the best design value, the bound value, and the gap ratio (best design ÷ bound, which must be ≥ 1 for the bound to be valid).
4. **Compare tightness** against the best prior bound on the same problem.
5. **Keep code and results** in `experiments/<id>/`, with a `result.json`. Numbers go in files, not prose.
6. **Replicate before believing.** No claim counts until an independent agent re-implements it from the written statement alone and reproduces it.

## Machine limits
8 GB RAM, about 4 GB free disk. Keep each job under about 1 GB and 20 minutes; work in 2D, or with small spheres and cylinders.
