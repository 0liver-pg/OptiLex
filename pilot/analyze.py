"""Turn the calibration grid into the three numbers that decide feasibility.

1. Noise floor: seed std of val loss / BLiMP at fixed budget.
2. Ruler: slope of metric vs ln(tokens), i.e. what a 2x data gain is worth in metric units.
3. Minimum detectable data multiplier (MDM) at n seeds, and whether the positive control
   (1M tokens x 4 epochs) is detected and what effective-data multiplier it earns.
"""
import json, math
from pathlib import Path
import numpy as np
from scipy import stats

R = Path(__file__).resolve().parent.parent / "results"
runs = [json.load(open(p)) for p in sorted(R.glob("D*_E*_s*.json"))]
by = {}
for r in runs:
    by.setdefault((r["tokens"], r["epochs"]), []).append(r)

def mde(sigma, n, alpha=0.05, power=0.8):
    df = 2 * n - 2
    return (stats.t.ppf(1 - alpha / 2, df) + stats.t.ppf(power, df)) * sigma * math.sqrt(2 / n)

out = {"conditions": {}}
for (D, E), rs in sorted(by.items()):
    vl = np.array([r["val_loss"] for r in rs]); bl = np.array([r["blimp"] for r in rs])
    out["conditions"][f"{D/1e6:.0f}M x{E}ep"] = dict(
        n=len(rs), val_loss=round(vl.mean(), 4), val_sd=round(vl.std(ddof=1), 4) if len(rs) > 1 else None,
        blimp=round(bl.mean(), 4), blimp_sd=round(bl.std(ddof=1), 4) if len(rs) > 1 else None,
        train_min=round(np.mean([r["train_seconds"] for r in rs]) / 60, 1), tok_per_s=int(np.mean([r["tok_per_s"] for r in rs])))

ruler = [(D, rs) for (D, E), rs in sorted(by.items()) if E == 1]
for metric in ("val_loss", "blimp"):
    xs = np.concatenate([[math.log(D)] * len(rs) for D, rs in ruler])
    ys = np.concatenate([[r[metric] for r in rs] for D, rs in ruler])
    slope, icpt = np.polyfit(xs, ys, 1)
    # pooled within-condition seed sd across all 1-epoch conditions
    resid = [r[metric] - np.mean([q[metric] for q in rs]) for D, rs in ruler for r in rs]
    dof = sum(len(rs) - 1 for D, rs in ruler)
    sd = math.sqrt(sum(e * e for e in resid) / dof) if dof else float("nan")
    m = {"slope_per_doubling": round(slope * math.log(2), 4), "pooled_seed_sd": round(sd, 4)}
    for n in (3, 5, 8):
        d = mde(sd, n)
        m[f"min_detectable_multiplier_n{n}"] = round(math.exp(d / abs(slope)), 2)
    ctrl = by.get((1_000_000, 4), [])
    base = by.get((1_000_000, 1), [])
    if ctrl and base:
        c = np.mean([r[metric] for r in ctrl]); b = np.mean([r[metric] for r in base])
        m["control_4ep_delta"] = round(c - b, 4)
        m["control_4ep_effective_multiplier"] = round(math.exp((c - b) / slope), 2)  # D_eff / D
        if len(ctrl) > 1 and len(base) > 1:
            m["control_welch_p"] = float(stats.ttest_ind([r[metric] for r in ctrl], [r[metric] for r in base], equal_var=False).pvalue)
    out[metric] = m

json.dump(out, open(R / "summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
