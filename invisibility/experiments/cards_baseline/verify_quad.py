"""Resonance-safe re-scoring: exact uniform band average by adaptive quadrature (scipy.integrate.quad) with sim/cloak2d.py.

Fixed-node averages (Gauss-Legendre 21/41 points) can be exploited by lossless designs whose sharp resonances fall between
nodes (seen here for a sector-metric design: 21-pt 1.018, 41-pt 1.102, adaptive ~1.05). Every number quoted in a card's
'best design' must come from this file.
"""
import json, sys
import numpy as np
from scipy.integrate import quad
from cards_common import *  # noqa


def uniform_avg(fn, B=BW, kc=KC):
    k1, k2 = kc * (1 - B / 2), kc * (1 + B / 2)
    # split into 8 panels so narrow resonances are found; tight tolerances
    edges = np.linspace(k1, k2, 9)
    tot, err = 0.0, 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        v, e = quad(fn, lo, hi, limit=200, epsabs=1e-10, epsrel=1e-8)
        tot += v; err += e
    return tot / (k2 - k1), err / (k2 - k1)


def design_fn(d):
    """Return m_of_k for a result record (lossless eps list, or Lorentz parameters)."""
    if "kp2_over_kc2" in d:
        kp2 = np.array(d["kp2_over_kc2"]) * KC ** 2
        k0 = np.array(d["k0_over_kc"]) * KC
        g = d["gam_over_wc"] * KC
        return lambda k: np.sqrt(1 + kp2 / (k0 ** 2 - k ** 2 - 1j * g * k))
    m = np.sqrt(np.asarray(d["eps"], float).astype(complex))
    return lambda k: m


METRICS = {
    "ext": lambda mk, r: (lambda k: ext_width(mk(k), r, k)),
    "sca": lambda mk, r: (lambda k: sca_width(mk(k), r, k)),
    "sector": lambda mk, r: (lambda k: sector_width_c2d(mk(k), r, k)),
    "ch0": lambda mk, r: (lambda k: channel_width_c2d(mk(k), r, k, 0)),
    "ch1": lambda mk, r: (lambda k: channel_width_c2d(mk(k), r, k, 1)),
    "ch2": lambda mk, r: (lambda k: channel_width_c2d(mk(k), r, k, 2)),
}

JOBS = [  # (file, metrics)
    ("p1_optimize_layers_ref.json", ["ext", "sector"]),
    ("de_ext_B0.1_L8.json", ["ext", "sector"]),
    ("lossless_ext_B0.1_L8.json", ["ext"]),
    ("de_sector_B0.1_L8.json", ["sector", "ext"]),
    ("lossless_sector_B0.1_L8.json", ["sector", "ext"]),
    ("lossless_ch0_B0.1_L8.json", ["ch0", "ext"]),
    ("lossless_ch1_B0.1_L8.json", ["ch1", "ext"]),
    ("de_ch2_B0.1_L8.json", ["ch2", "ext"]),
    ("lorentz_W0.5_L4_g0.01.json", ["ext", "sca"]),
    ("lorentz_W2.0_L4_g0.01.json", ["ext", "sca"]),
    ("lorentz_W2.0_L4_g0.01_seeded.json", ["ext", "sca"]),
    ("lorentz_W8.0_L4_g0.01.json", ["ext", "sca"]),
    ("lorentz_W8.0_L4_g0.01_seeded.json", ["ext", "sca"]),
    ("acausal_ref_B0.1_L4.json", ["ext"]),
    ("BARE", ["ext", "sector", "ch0", "ch1", "ch2"]),
]

if __name__ == "__main__":
    out_path = HERE / "quad_verified.json"
    out = json.loads(out_path.read_text()) if out_path.exists() else {}
    only = set(sys.argv[1:])
    for fname, mets in JOBS:
        if only and fname not in only:
            continue
        if fname == "BARE":
            mk, radii = (lambda k: []), [A]
        else:
            p = HERE / fname
            if not p.exists():
                continue
            d = json.loads(p.read_text())
            if "L4" in d:
                d = d["L4"]
            mk, radii = design_fn(d), d["radii"]
        rec = {}
        for mt in mets:
            v, e = uniform_avg(METRICS[mt](mk, radii))
            rec[mt] = dict(adaptive=v, abs_err_est=e, gl41=band(METRICS[mt](mk, radii)))
        out[fname] = rec
        print(fname, json.dumps(rec), flush=True)
        out_path.write_text(json.dumps(out, indent=1))
