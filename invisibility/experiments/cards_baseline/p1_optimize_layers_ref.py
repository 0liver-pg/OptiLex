"""P1 reference run with the shared adversary itself: cloak2d.optimize_layers (unmodified), canonical card parameters."""
import sys, json, time, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "sim"))
import cloak2d as c
a, kc, b, B = 1.0, np.pi / 2, 3.0, 0.1
out = {}
for L in (4,):
    radii = list(np.linspace(a, b, L + 1))
    t = time.time()
    val, p = c.optimize_layers(L, radii, kc, B, pol="TM", core="pec", eps_bounds=(1.0, 6.0), loss_max=0.0,
                               metric="ext", seeds=4, rng=0)
    m = np.sqrt(np.asarray(p, float).astype(complex))
    # re-score with 41-point band average (cloak2d default) for the reported value
    ext41 = c.band_average(lambda k: c.widths(m, radii, k, core="pec")[1], kc, B, n=41)
    sca41 = c.band_average(lambda k: c.widths(m, radii, k, core="pec")[0], kc, B, n=41)
    out[f"L{L}"] = dict(radii=radii, eps=list(map(float, p)), band_ext_21pt=val, band_ext_41pt=ext41,
                        band_sca_41pt=sca41, seconds=round(time.time() - t, 1))
    print(out[f"L{L}"], flush=True)
bare = c.band_average(lambda k: c.widths([], [a], k, core="pec")[1], kc, B, n=41)
out["bare_band_ext_41pt"] = bare
pathlib.Path(__file__).with_name("p1_optimize_layers_ref.json").write_text(json.dumps(out, indent=1))
