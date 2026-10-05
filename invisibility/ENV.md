# Invisibility test environment

Simulators installed locally for the idea engine's agents. Every one has been checked against an exact answer (`sim/validate.py`, `sim/validate_meep.py`; results in `sim/validation_*.json`). Agents should prefer the cheapest rung that can falsify an idea, then confirm on a higher rung.

| Rung | Tool | Use it for | Validation (this machine, 8 GB M1) | Speed |
|---|---|---|---|---|
| R0 | `sim/analytic.py` + bound calculators | Bound checks; exact cylinders | Lossless σ_sca = σ_ext to 1e-10; large lossy cylinder Q_ext → 2.003 | µs–ms |
| R1 | **scattnlay**, miepython, treams | Exact multilayer spheres/cylinders (scattering-cancellation and core–shell cloaks), T-matrix clusters | scattnlay vs miepython agree to 3e-13; Alù–Engheta shell cloak reproduced (610× less scattering) | ms |
| R2 | **ceviche** (2D FDFD, differentiable) | Fast single-frequency 2D inverse design | Point source vs exact Green's function: 1.3% deviation at λ/40 | ~1 min per 300×300 solve |
| R2 | **NGSolve** (FEM, high order) | Anisotropic/graded media (transformation optics), curved boundaries, frequency domain | Scattered field of a dielectric cylinder: 1.9e-4 relative error | ~15 s for a 2D cylinder problem |
| R3 | **MIT Meep 1.34** (FDTD, broadband) | Broadband and time-domain checks, dispersive and active media | 2D cylinder scattering width over 0.8–2 µm: 1.7% mean error (7.5% max, at sharp resonances), 37 s at 40 px/µm | minutes in 2D; 3D only for small cells |
| R4 | **Mitsuba 3** (physically based rendering) + **NVIDIA FLIP** | Ray-optics cloaks, lenticular sheets, display-based camouflage, rendering what a human observer sees | Cornell box render; FLIP = 0 for identical images, 0.025 between two noise seeds | ~25 s per 256² image at 64 spp (scalar mode) |
| — | fmmax (JAX RCWA) | Periodic metasurfaces, thermal-emissivity spectra | Installed, not yet validated | — |

**Commands**
```bash
cd invisibility
.venv/bin/python sim/validate.py                 # scattnlay, miepython, treams, ceviche, NGSolve, Mitsuba, FLIP, fmmax
.mamba/envs/meep/bin/python sim/validate_meep.py # MIT Meep
```

**Machine limits:** 8 GB RAM and about 6 GB of free disk. Stay in 2D or with small 3D cells, and keep each job under about 1 GB of RAM and 15 minutes. Mitsuba runs in `scalar_rgb` mode; its faster LLVM mode needs `brew install llvm` (about 1.5 GB). Large 3D or broadband optical problems belong on a cloud GPU (e.g. fdtdx or Tidy3D), not this laptop.

**Conventions:** `sim/analytic.py` uses exp(−iωt); ceviche uses exp(+iωt), so its outgoing waves are conjugated. Meep units are µm, with frequency = 1/wavelength.
