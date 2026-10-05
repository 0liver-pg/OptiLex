"""Validate MIT Meep (2D FDTD) against the exact scattering width of a dielectric cylinder over a band.
Run: .mamba/envs/meep/bin/python sim/validate_meep.py   (units: um; frequency = 1/wavelength)"""
import json, sys, time
from pathlib import Path
import numpy as np
import meep as mp

sys.path.insert(0, str(Path(__file__).parent))
from analytic import cylinder_tm_widths

r, n_cyl, res, dpml = 0.5, 2.0, 40, 1.0
s = 2 * (r + 2.5 + dpml)                       # cell side
fcen, df, nfreq = 0.875, 0.75, 25              # wavelengths ~0.8-2 um
box = 2 * r + 0.6                              # flux box side
cell, pml = mp.Vector3(s, s), [mp.PML(dpml)]
src = [mp.Source(mp.GaussianSource(fcen, fwidth=df, is_integrated=True), mp.Ez,
                 center=mp.Vector3(-0.5 * s + dpml), size=mp.Vector3(0, s))]
sides = [(mp.Vector3(-box / 2, 0), mp.Vector3(0, box), +1), (mp.Vector3(box / 2, 0), mp.Vector3(0, box), -1),
         (mp.Vector3(0, -box / 2), mp.Vector3(box, 0), +1), (mp.Vector3(0, box / 2), mp.Vector3(box, 0), -1)]

def run(geometry, minus=None):
    sim = mp.Simulation(resolution=res, cell_size=cell, boundary_layers=pml, sources=src, geometry=geometry)
    fl = [sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=c, size=sz)) for c, sz, _ in sides]
    if minus:
        for f, d in zip(fl, minus):
            sim.load_minus_flux_data(f, d)
    sim.run(until_after_sources=mp.stop_when_dft_decayed(1e-7, 0))
    return sim, fl

t = time.time()
sim0, fl0 = run([])
incident = np.array(mp.get_fluxes(fl0[0])) / box          # intensity (power per unit length of wavefront)
minus = [sim0.get_flux_data(f) for f in fl0]
freqs = np.array(mp.get_flux_freqs(fl0[0]))
sim0.reset_meep()
sim1, fl1 = run([mp.Cylinder(radius=r, material=mp.Medium(index=n_cyl))], minus)
# outward scattered power: flux sign follows +x/+y, so left/bottom sides count with a minus sign
P = sum(-sgn * np.array(mp.get_fluxes(f)) for f, (_, _, sgn) in zip(fl1, sides))
sigma = P / incident
exact = np.array([cylinder_tm_widths(n_cyl, r, 1 / f)[0] for f in freqs])
rel = np.abs(sigma - exact) / exact
out = dict(ok=bool(np.mean(rel) < 0.03), mean_rel_err=float(np.mean(rel)), max_rel_err=float(np.max(rel)),
           seconds=round(time.time() - t, 1), resolution=res,
           table=[(round(1 / f, 3), round(a, 4), round(b, 4)) for f, a, b in zip(freqs, sigma, exact)][::4])
print(f"[{'PASS' if out['ok'] else 'FAIL'}] Meep 2D cylinder sigma_sca vs exact: mean rel.err={out['mean_rel_err']:.3f}, "
      f"max={out['max_rel_err']:.3f}, {out['seconds']}s at {res} px/um")
print("  (wavelength um, meep, exact):", out["table"])
Path(__file__).with_name("validation_meep.json").write_text(json.dumps(out, indent=1))
