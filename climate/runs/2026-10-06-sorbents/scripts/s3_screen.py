"""Step 3: DAC-window screen of NIST ISODB single-component CO2 isotherms using the OptiLex sorbent verifier.

Rule (fixed before the final ranking was read):
  1. Data: entries not labelled simulation/model, mass-based units, 288-308 K CO2 isotherm with >= 3 points.
     Points below 2% of the isotherm's top pressure are treated as unresolved (figure digitisation) and dropped,
     unless the low-pressure region is itself resolved (>= 4 such points reaching below 0.2% of the top pressure,
     or the entry is tabular). Loadings are made monotone by isotonic regression (pool-adjacent-violators).
  2. Uptake at 420 ppm (P_CO2_AIR = 42.56 Pa):
       class A "measured": resolved points within one decade on both sides of 42.56 Pa -> log-log interpolation.
       class B "bounded":  nearest resolved point p1 above 42.56 Pa. For a concave isotherm through the origin,
                q(p1) * p_air / p1 <= q(p_air) <= q(p1). Central estimate = low-pressure Langmuir fit, clamped.
  3. Per paper: the isotherm closest to 298 K. Per adsorbent: score = median over papers of the guaranteed
     (lower-bound) uptake, using papers whose p1 <= 25 x 42.56 Pa when any exist. Rank by score.
  4. Verifier mapping: effective Langmuir site (q_max from the low-pressure fit, b chosen to reproduce the central
     420 ppm uptake) -> dG = -R T ln(b P_REF); dH from Clausius-Clapeyron at the lowest loading measured at every
     temperature (same paper and adsorbent, span >= 10 K); dS = (dH - dG)/T_a.
  5. DAC window: score >= 0.1 mol/kg AND temperature to unload 80% of the ambient loading under 1 kPa CO2
     (the verifier's default desorption pressure) <= 120 C. Without multi-temperature data: "unknown".
"""
import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import collections
import json
import math
import os
import pickle
import statistics

import numpy as np
from scipy.optimize import brentq, least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
D = pickle.load(open(os.path.join(HERE, "co2_h2o_isotherms.pkl"), "rb"))
ISO, ADS, BIB = D["isotherms"], D["adsorbents"], D["bib"]
P_AIR = P_CO2_AIR                       # 42.56 Pa
M_CO2_G = 44.0095
M_H2O_G = 18.015
V_STP = 22.414                          # L/mol

SIM_WORDS = ("simulat", "monte carlo", "computational", "molecular dynamics", "first-principles",
             "first principles", "dft", "in silico", "ab initio", "force field")


def to_molkg(q, units, molar_mass_g):
    u = units
    if u in ("mmol/g", "mol/kg"):
        return q
    if u in ("cm3(STP)/g", "ml(STP)/g", "ml/g"):
        return q / V_STP
    if u == "mg/g":
        return q / molar_mass_g
    if u == "g/g":
        return q * 1000.0 / molar_mass_g
    if u == "wt%":
        return q * 10.0 / molar_mass_g
    if u == "mol/g":
        return q * 1000.0
    if u == "mmol/kg":
        return q / 1000.0
    return None


def pava(y):
    """Isotonic (non-decreasing) regression, equal weights."""
    vals, wts = [], []
    for v in y:
        vals.append(float(v)); wts.append(1.0)
        while len(vals) > 1 and vals[-2] > vals[-1]:
            w = wts[-2] + wts[-1]
            v2 = (vals[-2] * wts[-2] + vals[-1] * wts[-1]) / w
            vals[-2:] = [v2]; wts[-2:] = [w]
    out = []
    for v, w in zip(vals, wts):
        out.extend([v] * int(round(w)))
    return np.array(out)


def clean(k, molar_mass_g):
    """Adsorption branch, Pa and mol/kg, sorted, positive, resolved, monotone. Returns (ps, qs, p_top) or None."""
    pts = k["pts"]
    if len(pts) < 3 or to_molkg(1.0, k["q_units"], molar_mass_g) is None:
        return None
    imax = max(range(len(pts)), key=lambda i: pts[i][0])
    branch = pts[: imax + 1]
    rows = sorted((p * 1e5, to_molkg(q, k["q_units"], molar_mass_g)) for p, q in branch if p > 0 and q > 0)
    if len(rows) < 3:
        return None
    p_top = rows[-1][0]
    low = [r for r in rows if r[0] <= 0.02 * p_top]
    resolved = bool(k.get("tabular")) or (len(low) >= 4 and rows[0][0] <= 0.002 * p_top)
    if not resolved:
        rows = [r for r in rows if r[0] > 0.02 * p_top]
    ps, qs = [], []
    for p, q in rows:
        if ps and p <= ps[-1] * 1.0000001:
            continue
        ps.append(p); qs.append(q)
    if len(ps) < 3:
        return None
    raw = np.array(qs)
    qs = pava(qs)
    if qs.max() > 60.0:
        return None
    n6 = min(6, len(raw))
    k["noisy_low"] = bool(np.any(np.abs(raw[:n6] - qs[:n6]) > 0.2 * qs[:n6]))
    return np.array(ps), qs, p_top


def loglog_interp(x, xs, ys):
    return float(math.exp(np.interp(math.log(x), np.log(xs), np.log(ys))))


def nonconcave(ps, qs):
    """True if the secant slope q/p rises by >25% between consecutive points above 2% of the top loading."""
    s = qs / ps
    floor = 0.02 * qs.max()
    for i in range(len(ps) - 1):
        if qs[i] > floor and s[i + 1] > 1.25 * s[i]:
            return True
    return False


def fit_langmuir(ps, qs):
    """Low-pressure single-site Langmuir. Window: p <= max(2 kPa, 5th-lowest pressure). Returns b (1/Pa), qmax, n, rms."""
    pcut = max(2000.0, ps[min(4, len(ps) - 1)])
    m = ps <= pcut
    p, q = ps[m], qs[m]
    qtop = qs.max()
    w = q + 0.05 * q.max()

    def res(x):
        b, qm = math.exp(x[0]), math.exp(x[1])
        return (qm * b * p / (1 + b * p) - q) / w

    lo = [math.log(1e-12), math.log(max(q.max() * 0.8, 1e-9))]
    hi = [math.log(1e3), math.log(max(qtop * 1.5, q.max() * 1.6, 1e-8))]
    x0 = [math.log(max(q[0] / p[0] / max(q.max(), 1e-9), 1e-12)), math.log(max(q.max() * 1.2, 1e-6))]
    x0 = [min(max(x0[0], lo[0] + 1e-6), hi[0] - 1e-6), min(max(x0[1], lo[1] + 1e-6), hi[1] - 1e-6)]
    try:
        r = least_squares(res, x0, bounds=(lo, hi))
    except Exception:
        return None
    return math.exp(r.x[0]), math.exp(r.x[1]), int(m.sum()), float(np.sqrt(np.mean(r.fun ** 2)))


def uptake_at_air(ps, qs):
    below, above = ps <= P_AIR, ps >= P_AIR
    if not above.any():
        return None
    out = dict(p_min=float(ps[0]), n_pts=len(ps), nonconcave=nonconcave(ps, qs), fit=fit_langmuir(ps, qs))
    if out["fit"] is None:
        return None
    i_hi = int(np.argmax(above))
    p_hi, q_hi = float(ps[i_hi]), float(qs[i_hi])
    p_lo = q_lo = None
    if below.any():
        i_lo = int(np.where(below)[0][-1])
        p_lo, q_lo = float(ps[i_lo]), float(qs[i_lo])
    if p_lo is not None and p_lo >= P_AIR / 10 and p_hi <= P_AIR * 10:
        c = loglog_interp(P_AIR, ps, qs)
        out.update(kind="A", lo=c, hi=q_hi, central=c, extrap=1.0)
        return out
    lo_b = 0.0 if out["nonconcave"] else q_hi * P_AIR / p_hi
    if q_lo is not None:
        lo_b = max(lo_b, q_lo)
    b, qm = out["fit"][0], out["fit"][1]
    c = min(max(qm * b * P_AIR / (1 + b * P_AIR), lo_b), q_hi)
    out.update(kind="B", lo=lo_b, hi=q_hi, central=c, extrap=p_hi / P_AIR)
    return out


def p_sat_water(T):
    """Buck equation, Pa."""
    tc = T - 273.15
    return 611.21 * math.exp((18.678 - tc / 234.5) * (tc / (257.14 + tc)))


def looks_simulated(doi):
    b = BIB.get(doi) or {}
    t = ((b.get("title") or "") + " " + (b.get("journal") or "")).lower()
    return any(w in t for w in SIM_WORDS)


# ---------- pass 1: clean every CO2 isotherm ----------
co2 = []
funnel = collections.Counter()
for k in ISO:
    if k["gas"] != "CO2":
        continue
    funnel["CO2 single-component isotherms"] += 1
    if not isinstance(k["T"], (int, float)):
        continue
    if k["doi"] == "10.1007/s10450-026-00701-3" and k["T"] == 25:
        k = dict(k); k["T"] = 298.15            # entry stores 25 (deg C); documented unit fix
        funnel["temperature unit fix (25 C -> 298.15 K, NIST 2026 13X interlaboratory entries)"] += 1
    if k["file"] and k["file"].endswith("Desorption"):
        funnel["dropped: desorption branch files"] += 1
        continue
    if k["category"] in ("sim", "mod", "qua") or "(site" in (k["name"] or ""):
        funnel["dropped: labelled simulation/model/site-decomposition"] += 1
        continue
    c = clean(k, M_CO2_G)
    if c is None:
        funnel["dropped: units not mass-based, <3 resolved points or implausible"] += 1
        continue
    k2 = dict(k)
    k2["ps"], k2["qs"], k2["p_top"] = c
    k2["noisy_low"] = k.get("noisy_low", False)
    k2["flag_units"] = k["q_units"] in ("wt%", "ml/g")
    co2.append(k2)
funnel["usable CO2 isotherms (any T)"] = len(co2)

# ---------- pass 2: isosteric heat per (DOI, adsorbent) ----------
sets = collections.defaultdict(list)
for k in co2:
    if 263 <= k["T"] <= 373:
        sets[(k["doi"], k["hashkey"])].append(k)


def clausius_clapeyron(group):
    byT = {}
    for k in group:
        Tr = round(k["T"])
        if Tr not in byT or k["ps"][0] < byT[Tr]["ps"][0]:
            byT[Tr] = k
    Ts = sorted(byT)
    if len(Ts) < 2 or Ts[-1] - Ts[0] < 10:
        return None
    qstar = max(byT[T]["qs"][0] for T in Ts) * 1.02
    if qstar > 0.9 * min(byT[T]["qs"][-1] for T in Ts):
        return None
    x, y = [], []
    for T in Ts:
        k = byT[T]
        qs_u, idx = np.unique(k["qs"], return_index=True)
        if len(qs_u) < 2:
            return None
        y.append(float(np.interp(math.log(qstar), np.log(qs_u), np.log(k["ps"][idx]))))
        x.append(1.0 / k["T"])
    slope, _ = np.polyfit(x, y, 1)
    dH = R * slope
    if not (-150e3 < dH < -5e3):
        return None
    return dict(dH=float(dH), nT=len(Ts), Tmin=Ts[0], Tmax=Ts[-1], qstar=float(qstar))


cc = {}
for key, group in sets.items():
    r = clausius_clapeyron(group)
    if r:
        cc[key] = r
funnel["(paper x adsorbent) sets with a Clausius-Clapeyron dH"] = len(cc)

# ---------- pass 3: ambient uptake at 420 ppm ----------
amb = []
for k in co2:
    if not (288 <= k["T"] <= 308):
        continue
    funnel["usable isotherms at 288-308 K"] += 1
    u = uptake_at_air(k["ps"], k["qs"])
    if u is None:
        funnel["dropped: all points below 42.56 Pa or no fit"] += 1
        continue
    k["u"] = u
    amb.append(k)
funnel["isotherms with a 420 ppm bracket"] = len(amb)
funnel["  class A (measured within a decade either side)"] = sum(1 for k in amb if k["u"]["kind"] == "A")
funnel["  class B (bounded, extrapolated)"] = sum(1 for k in amb if k["u"]["kind"] == "B")
funnel["  class B with first resolved point <= 25 x 42.56 Pa"] = sum(
    1 for k in amb if k["u"]["kind"] == "B" and k["u"]["extrap"] <= 25)

# ---------- pass 4: water isotherms per adsorbent ----------
water = collections.defaultdict(list)
for k in ISO:
    if k["gas"] != "H2O" or not isinstance(k["T"], (int, float)) or not (288 <= k["T"] <= 308):
        continue
    if k["category"] in ("sim", "mod", "qua"):
        continue
    c = clean(k, M_H2O_G)
    if c is None:
        continue
    ps, qs, _ = c
    psat = p_sat_water(k["T"])
    rec = dict(doi=k["doi"], T=k["T"])
    for rh in (0.1, 0.5):
        p = rh * psat
        rec[rh] = loglog_interp(p, ps, qs) if ps[0] <= p <= ps[-1] else None
    water[k["hashkey"]].append(rec)
funnel["adsorbents with a usable 288-308 K water isotherm"] = len(water)

# hot isotherms for a direct swing check
hot = collections.defaultdict(list)
for k in co2:
    if k["T"] >= 343:
        hot[(k["doi"], k["hashkey"])].append(k)


def t_unload80(dH, dS, theta, p_des):
    f = lambda T: loading(p_des, T, dH, dS, 1.0) - 0.2 * theta
    try:
        return brentq(f, 150.0, 1200.0) - 273.15
    except Exception:
        return float("nan")


def verifier_numbers(central, qmax, T_a, dH):
    qmax = max(qmax, central / 0.98)
    b = central / (P_AIR * (qmax - central))
    dG = -R * T_a * math.log(b * P_REF)
    out = dict(dG=dG, qmax_eff=qmax, fill_Ta=central / qmax)
    if dH is None:
        return out
    dS = (dH - dG) / T_a
    theta = loading(P_AIR, T0, dH, dS, 1.0)
    out.update(dS=dS, theta=theta, T80_C=t_unload80(dH, dS, theta, 1.0e3), T80_100Pa_C=t_unload80(dH, dS, theta, 100.0),
               Tdes_verifier_C=desorption_temperature(dH, dS, 1.0e3, 0.2) - 273.15)
    for ddH in (-5e3, 5e3):
        dS2 = (dH + ddH - dG) / T_a
        th2 = loading(P_AIR, T0, dH + ddH, dS2, 1.0)
        out["T80_C_dH%+d" % (ddH / 1e3)] = t_unload80(dH + ddH, dS2, th2, 1.0e3)
    for Td in (373.15, 393.15):
        cyc = TVSACycle(dH=dH, dS=dS, q_max=qmax, T_des=Td, p_des=1.0e3)
        tag = f"{Td - 273.15:.0f}C"
        out["wc_" + tag] = cyc.working_capacity
        if cyc.working_capacity > 1e-3:
            out["heat_" + tag] = cyc.heat_gj_per_t
            out["workeq_" + tag] = cyc.work_equivalent_gj_per_t
    return out


# ---------- pass 5: aggregate per adsorbent ----------
by_ads = collections.defaultdict(lambda: collections.defaultdict(list))
for k in amb:
    by_ads[k["hashkey"]][k["doi"]].append(k)
funnel["adsorbents with a 420 ppm bracket"] = len(by_ads)

rows = []
for hk, per_doi in by_ads.items():
    reps = [min(ks, key=lambda k: (abs(k["T"] - 298.15), k["u"]["extrap"])) for ks in per_doi.values()]
    good = [k for k in reps if k["u"]["extrap"] <= 25] or reps
    score = statistics.median(k["u"]["lo"] for k in good)
    # representative isotherm: the paper whose guaranteed uptake is closest to the median from below/at it
    rep = min(good, key=lambda k: (abs(k["u"]["lo"] - score), k["u"]["extrap"]))
    u = rep["u"]
    centrals = [k["u"]["central"] for k in good]
    c_same = cc.get((rep["doi"], hk))
    c_all = [v["dH"] for (d, h), v in cc.items() if h == hk]
    dH = c_same["dH"] if c_same else (statistics.median(c_all) if c_all else None)
    central_med = statistics.median(centrals)
    v = verifier_numbers(central_med, u["fit"][1], rep["T"], dH)
    w = water.get(hk, [])
    w50 = [r[0.5] for r in w if r[0.5] is not None]
    w10 = [r[0.1] for r in w if r[0.1] is not None]
    # direct hot-isotherm check from the representative paper
    direct = None
    hs = hot.get((rep["doi"], hk), [])
    if hs:
        h = max(hs, key=lambda k: k["T"])
        if h["ps"][0] <= 1.0e3 <= h["ps"][-1]:
            direct = dict(T_hot_C=h["T"] - 273.15, q_hot_1kPa=loglog_interp(1.0e3, h["ps"], h["qs"]))
        else:
            direct = dict(T_hot_C=h["T"] - 273.15, q_hot_1kPa=None, p_first=float(h["ps"][0]), q_first=float(h["qs"][0]))
    bibrec = BIB.get(rep["doi"]) or {}
    rows.append(dict(
        hashkey=hk, name=rep["name"], formula=(ADS.get(hk) or {}).get("formula"),
        synonyms=((ADS.get(hk) or {}).get("synonyms") or [])[:4],
        score=score, T_a=rep["T"], kind=u["kind"], lo=u["lo"], central=u["central"], hi=u["hi"], extrap=u["extrap"],
        p_min=u["p_min"], p_top=rep["p_top"], nonconcave=u["nonconcave"], central_med=central_med,
        central_min=min(centrals), central_max=max(centrals),
        n_doi=len(per_doi), n_doi_good=len(good), n_iso=sum(len(ks) for ks in per_doi.values()),
        doi=rep["doi"], year=bibrec.get("year"), title=bibrec.get("title"), category=rep["category"],
        flag_units=rep["flag_units"], q_units=rep["q_units"],
        sim_suspect=looks_simulated(rep["doi"]) and rep["category"] != "exp", noisy_low=rep["noisy_low"],
        pscale_suspect=rep["p_top"] < 500.0,
        dH=dH, dH_same_paper=bool(c_same), dH_n_papers=len(c_all),
        dH_all=[round(x / 1e3, 1) for x in sorted(c_all)], cc=c_same, direct=direct,
        h2o_50rh=(statistics.median(w50) if w50 else None), h2o_10rh=(statistics.median(w10) if w10 else None),
        n_h2o=len(w), **v))

print("FUNNEL")
for kf, vf in funnel.items():
    print(f"  {vf:6d}  {kf}")
print(f"  P_CO2_AIR = {P_AIR:.2f} Pa; half-loading dG = {dG_for_half_loading() / 1e3:.2f} kJ/mol")
for thr in (0.02, 0.05, 0.1, 0.2, 0.5, 1.0):
    n_lo = sum(1 for r in rows if r["score"] >= thr)
    n_c = sum(1 for r in rows if r["central_med"] >= thr)
    print(f"  adsorbents with guaranteed uptake >= {thr} mol/kg: {n_lo:4d} | with central estimate >= {thr}: {n_c:4d}")
have = [r for r in rows if r["score"] >= 0.1]
n_dh = sum(1 for r in have if r["dH"] is not None)
n_in = sum(1 for r in have if r["dH"] is not None and r["T80_C"] <= 120)
n_in_vac = sum(1 for r in have if r["dH"] is not None and r["T80_C"] > 120 and r["T80_100Pa_C"] <= 120)
print(f"  of the {len(have)} adsorbents with guaranteed uptake >= 0.1 mol/kg: {n_dh} have a measured dH; "
      f"{n_in} unload 80% by 120 C at 1 kPa CO2; a further {n_in_vac} do so only at 0.1 kPa CO2")

rows.sort(key=lambda r: -r["score"])
json.dump(rows, open(os.path.join(HERE, "screen_rows.json"), "w"), default=str)


def fmt(x, f="{:.2f}"):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f.format(x)


N = 50
print(f"\nTOP {N} ADSORBENTS BY GUARANTEED UPTAKE AT 420 ppm (mol/kg), 288-308 K")
print(f"{'#':>2} {'adsorbent':32.32} {'T_a':>4} {'cls':>3} {'score':>6} {'q_c':>6} {'q_hi':>6} {'xtrap':>6} "
      f"{'nDOI':>4} {'dH':>6} {'dG':>6} {'dS':>5} {'fill':>5} {'T80':>4} {'T80-':>4} {'T80+':>4} {'T80v':>4} "
      f"{'wc100':>5} {'heat':>6} {'wc120':>5} {'H2O50':>5} {'flags':6} doi (year)")
for i, r in enumerate(rows[:N], 1):
    flags = "".join([("S" if r["sim_suspect"] else ""), ("U" if r["flag_units"] else ""),
                     ("N" if r["nonconcave"] else ""), ("P" if r["pscale_suspect"] else ""), ("M" if r["noisy_low"] else ""),
                     ("" if r["dH_same_paper"] or r["dH"] is None else "o")])
    print(f"{i:>2} {r['name'] or '?':32.32} {r['T_a']:>4.0f} {r['kind']:>3} {r['score']:>6.3f} {r['central_med']:>6.3f} "
          f"{r['hi']:>6.3f} {r['extrap']:>6.1f} {r['n_doi']:>4d} "
          f"{fmt(r['dH'] / 1e3 if r['dH'] else None, '{:.1f}'):>6} {r['dG'] / 1e3:>6.1f} "
          f"{fmt(r.get('dS'), '{:.0f}'):>5} {fmt(r.get('theta'), '{:.2f}'):>5} {fmt(r.get('T80_C'), '{:.0f}'):>4} "
          f"{fmt(r.get('T80_C_dH-5'), '{:.0f}'):>4} {fmt(r.get('T80_C_dH+5'), '{:.0f}'):>4} "
          f"{fmt(r.get('T80_100Pa_C'), '{:.0f}'):>4} "
          f"{fmt(r.get('wc_100C'), '{:.2f}'):>5} {fmt(r.get('heat_100C'), '{:.1f}'):>6} {fmt(r.get('wc_120C'), '{:.2f}'):>5} "
          f"{fmt(r['h2o_50rh'], '{:.1f}'):>5} {flags:6} {r['doi']} ({r['year']})")
print("columns: score = guaranteed uptake (median over papers); q_c = central estimate; q_hi = upper bound; xtrap = p1/42.56 Pa;"
      "\n  dH kJ/mol (Clausius-Clapeyron), dG kJ/mol at T_a, dS J/mol/K, fill = verifier site filling at 420 ppm and 25 C;"
      "\n  T80 = C to unload 80% of ambient loading at 1 kPa CO2 (T80-/T80+ = same with dH 5 kJ/mol stronger/weaker);"
      "\n  T80v = same at 0.1 kPa CO2; wc100/wc120 = verifier working capacity (mol/kg) for a 100/120 C, 1 kPa swing;"
      "\n  heat = verifier dry regeneration heat GJ/t at 100 C; H2O50 = pure-water uptake at 50% RH, mol/kg."
      "\nflags: S = title/journal suggests simulation; U = ambiguous unit (wt% or ml/g); N = non-concave (stepped) isotherm;"
      "\n  P = top pressure of the entry < 5 mbar (pressure scale suspect); M = raw low-pressure points non-monotone (digitisation noise); o = dH from other paper(s) on the same adsorbent")
print("\nTITLES")
for i, r in enumerate(rows[:N], 1):
    d = r["direct"]
    ds = ""
    if d:
        ds = (f" | hot isotherm {d['T_hot_C']:.0f} C: q(1 kPa) = {fmt(d['q_hot_1kPa'], '{:.3f}')}")
    ccs = f" | CC: {r['cc']['nT']} T, {r['cc']['Tmin']}-{r['cc']['Tmax']} K, q*={r['cc']['qstar']:.3f}" if r["cc"] else ""
    print(f"{i:>2} {r['name']}: {str(r['title'])[:110]} [{r['category'] or 'unlabelled'}; {r['q_units']}]{ccs}{ds}"
          f"{' | dH all papers ' + str(r['dH_all']) if r['dH_n_papers'] > 1 else ''}")
