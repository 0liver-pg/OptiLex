import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
"""ODAC23 executed screen against the OptiLex sorbent verifier's DAC window.

Inputs (all in this folder, downloaded 2026-10-05):
  odac23_adsorption_energy.txt  172,659 relaxed DFT adsorption energies (PBE+D3), one per MOF+adsorbate placement
      https://dl.fbaipublicfiles.com/opencatalystproject/data/large_files/adsorption_energy.txt
  odac23_eint_compact.csv       51,478 rigid-framework interaction energies + open-metal-site flags (name, y, oms extracted from)
      https://dl.fbaipublicfiles.com/opencatalystproject/data/large_files/data_w_oms.json
  core2019_asr_public.csv       CoRE MOF 2019 metadata (metals, pore sizes)  https://zenodo.org/records/3370144
  promising_*_MOFs.csv          ODAC23 paper's own 'promising' lists (fairchem GitHub)
"""
import collections
import csv
import json
import math
import os
import re

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
EV = 96.48533  # kJ/mol per eV
RTk = R * T0 / 1e3  # kJ/mol


def P(*a):
    print(*a)


# ----------------------------------------------------------------------------------------------
# A. Verifier window as a function of the adsorption entropy
# ----------------------------------------------------------------------------------------------
FILL_MIN = 0.20          # 'meaningful uptake': >= 20% of sites filled at 420 ppm, 25 C
T_DES_MAX = 393.15       # unloads to 20% residual at 1 kPa CO2 by 120 C
P_DES = 1.0e3
RESID = 0.2


def window(dS):
    """(strong limit, weak limit) of dH in J/mol for the verifier's Langmuir site."""
    L = math.log(P_REF / P_DES * RESID / (1.0 - RESID))
    strong = -T_DES_MAX * (R * L - dS)                                   # desorption_temperature == T_DES_MAX
    weak = brentq(lambda dH: loading(P_CO2_AIR, T0, dH, dS, 1.0) - FILL_MIN, -150e3, -1e3)
    return strong, weak


P("=" * 100)
P("A. VERIFIER WINDOW")
P(f"half-loading dG at 420 ppm, 25 C: {dG_for_half_loading()/1e3:.2f} kJ/mol")
for dS in (-165.0,):
    s, w = window(dS)
    P(f"dS = {dS:.0f} J/mol/K (verifier default, amine-like): dH window {s/1e3:.1f} .. {w/1e3:.1f} kJ/mol "
      f"(fill >= {FILL_MIN:.0%} at 420 ppm; <= {RESID:.0%} residual at 1 kPa CO2 by {T_DES_MAX-273.15:.0f} C)")

# ----------------------------------------------------------------------------------------------
# B. Entropy calibration for physisorbents from MEASURED 400 ppm uptakes (dry, pure-component, 298 K)
# ----------------------------------------------------------------------------------------------
P("\n" + "=" * 100)
P("B. ENTROPY CALIBRATION FROM MEASURED PHYSISORBENT DATA (400 ppm CO2, 298 K, dry single-gas isotherms)")
# name, uptake at 400 ppm (mmol/g), Qst (kJ/mol), assumed saturation capacity (mmol/g)
MEASURED = [
    ("SIFSIX-3-Zn   (Nugent 2013 / Shekhah 2014)", 0.13, 45.0, 2.5),
    ("SIFSIX-3-Cu   (Shekhah 2014)", 1.24, 54.0, 2.6),
    ("NbOFFIVE-1-Ni (Bhatt 2016)", 1.30, 54.0, 2.2),
]
p400 = 400e-6 * P0
dS_cal = []
for name, q, qst, qmax in MEASURED:
    out = []
    for qm in (0.8 * qmax, qmax, 1.2 * qmax):
        th = q / qm
        dG = -R * 298.15 * math.log(th / (1 - th) * P_REF / p400)
        out.append((-qst * 1e3 - dG) / 298.15)
    dS_cal.append(out[1])
    P(f"  {name:<44} q={q:.2f} mmol/g, Qst={qst:.0f} kJ/mol, q_max={qmax} (+-20%): "
      f"dS = {out[1]:.1f} J/mol/K (range {min(out):.1f} .. {max(out):.1f}); +-3 kJ/mol in Qst shifts dS by +-{3e3/298.15:.1f}")
DS_PHYS = round(float(np.mean(dS_cal)), 0)
P(f"  -> physisorption-calibrated dS = {DS_PHYS:.0f} J/mol/K (mean of the three; spread {min(dS_cal):.1f} .. {max(dS_cal):.1f})")
s_p, w_p = window(DS_PHYS)
s_c, w_c = window(-165.0)
P(f"  window at dS = {DS_PHYS:.0f}: dH {s_p/1e3:.1f} .. {w_p/1e3:.1f} kJ/mol (width {abs(s_p-w_p)/1e3:.1f} kJ/mol)")
P(f"  window at dS = -165: dH {s_c/1e3:.1f} .. {w_c/1e3:.1f} kJ/mol (width {abs(s_c-w_c)/1e3:.1f} kJ/mol)")

# ----------------------------------------------------------------------------------------------
# C. DFT adsorption energy (0 K electronic) -> adsorption enthalpy at 298 K
# ----------------------------------------------------------------------------------------------
P("\n" + "=" * 100)
P("C. CONVERSION  dH(298 K) = E_ads(DFT) + delta")


def ho_energy_RT(wavenumber_cm, T=298.15):
    """Zero-point + thermal energy of a harmonic mode in units of RT."""
    x = 1.438777 * wavenumber_cm / T
    return x * (0.5 + 1.0 / math.expm1(x))


# CO2 (linear): gas H_thermal = 3/2 RT (trans) + RT (rot) + RT (pV) = 3.5 RT; 5 new frustrated modes when adsorbed
co2_harm = sum(ho_energy_RT(70.0) for _ in range(5)) - 3.5        # localized, soft modes ~70 cm-1
co2_mobile = (1.0 + 1.0 + ho_energy_RT(70.0)) - 3.5               # 2D-mobile, freely rotating limit
DELTA_CO2 = round(0.5 * (co2_harm + co2_mobile) * RTk, 1)
# H2O (non-linear): gas 4 RT; adsorbed: 3 librations ~500 cm-1 + 3 frustrated translations ~150 cm-1
h2o_harm = 3 * ho_energy_RT(500.0) + 3 * ho_energy_RT(150.0) - 4.0
h2o_mobile = (1.0 + 1.5 + ho_energy_RT(150.0)) - 4.0
DELTA_H2O = round(0.5 * (h2o_harm + h2o_mobile) * RTk, 1)
P(f"  CO2: localized-harmonic limit {co2_harm*RTk:+.1f}, mobile limit {co2_mobile*RTk:+.1f} kJ/mol -> delta_CO2 = {DELTA_CO2:+.1f} kJ/mol (midpoint)")
P(f"  H2O: localized-harmonic limit {h2o_harm*RTk:+.1f}, mobile limit {h2o_mobile*RTk:+.1f} kJ/mol -> delta_H2O = {DELTA_H2O:+.1f} kJ/mol (midpoint)")
DS_H2O = 69.95 - 188.84   # liquid-like bound water: S(liq) - S(gas, 1 bar), J/mol/K
P_SAT_25C = 3169.0        # Pa
RH = 0.5
P_W = RH * P_SAT_25C
P(f"  water site entropy: liquid-like dS_H2O = {DS_H2O:.1f} J/mol/K; humid case = {RH:.0%} RH at 25 C = {P_W:.0f} Pa H2O "
  f"({P_W/P_CO2_AIR:.0f}x the CO2 partial pressure)")
for name, lo_, hi_, dS_ in (("physisorption-calibrated", s_p, w_p, DS_PHYS), ("verifier default", s_c, w_c, -165.0)):
    P(f"  => E_ads(CO2) window, {name} (dS={dS_:.0f}): {(lo_/1e3-DELTA_CO2):.1f} .. {(hi_/1e3-DELTA_CO2):.1f} kJ/mol "
      f"= {(lo_/1e3-DELTA_CO2)/EV:.3f} .. {(hi_/1e3-DELTA_CO2)/EV:.3f} eV")

# ----------------------------------------------------------------------------------------------
# D. Parse ODAC23
# ----------------------------------------------------------------------------------------------
P("\n" + "=" * 100)
P("D. DATASET")
KIND = {"CO2": (1, 0), "H2O": (0, 1), "CO2_H2O": (1, 1), "CO2_2H2O": (1, 2)}
hosts = collections.defaultdict(lambda: collections.defaultdict(list))   # host -> kind -> [(cfg, E_eV, fullname)]
n_lines = n_unphys = 0
for line in open(os.path.join(HERE, "odac23_adsorption_energy.txt")):
    name, e = line.split()
    e = float(e)
    host, ads = name.rsplit("_w_", 1)
    m = re.fullmatch(r"(CO2_2H2O|CO2_H2O|CO2|H2O)(?:_(random|new))?(?:_(\d+))?", ads)
    if not m:
        raise SystemExit(f"unparsed name {name}")
    kind = m.group(1)
    n_lines += 1
    nmol = sum(KIND[kind])
    if abs(e / nmol) >= 2.0:            # ODAC23 paper's own 'unphysical' cut
        n_unphys += 1
        continue
    hosts[host][kind].append((ads, e, name))
P(f"  parsed {n_lines} relaxed systems; dropped {n_unphys} with |E_ads/n| >= 2 eV (paper's rule); {len(hosts)} host frameworks")

eint = {}
oms_flag = {}
# compact extract (name, y, oms) of data_w_oms.json; the 22 MB original was deleted after extraction to save disk
for r in csv.DictReader(open(os.path.join(HERE, "odac23_eint_compact.csv"))):
    eint[r["name"]] = float(r["E_int_eV"])
    oms_flag[r["name"].rsplit("_w_", 1)[0]] = bool(int(r["oms"]))
P(f"  rigid-framework interaction energies available for {len(eint)} systems")

core = {r["filename"]: r for r in csv.DictReader(open(os.path.join(HERE, "core2019_asr_public.csv"), encoding="utf-8", errors="replace"))}


def is_defective(host):
    return re.search(r"_0\.\d+_\d$", host) is not None


def parent(host):
    return re.sub(r"_0\.\d+_\d$", "", host)


def core_row(host):
    b = parent(host)
    for k in (b, b + "_clean", b + "_clean_h", b + "_clean_h_min"):
        if k in core:
            return core[k]
    c = [k for k in core if k.startswith(b + "_")]
    return core[c[0]] if len(c) == 1 else None


DEF_TOL = 0.05   # eV; |E_ads - E_int| tolerance = framework (and molecule) deformation term


def summarise(host):
    """Per framework: lowest raw E_ads per adsorbate, plus a framework-reference-corrected CO2/H2O energy.

    E_corr(placement) = E_int   if E_ads - E_int < -DEF_TOL  (empty-MOF reference too high: use rigid-framework energy)
                      = E_ads   otherwise (|difference| small, or framework genuinely distorts, or no record)
    status of the lowest corrected placement: ok | refcorr | distort | unverified (no interaction-energy record)
    """
    d = hosts[host]
    out = {"host": host, "defective": is_defective(host)}
    for kind in KIND:
        lst = sorted(d.get(kind, []), key=lambda t: t[1])
        out["n_" + kind] = len(lst)
        if lst:
            ads, e, name = lst[0]
            out["E_" + kind] = e
            out["cfg_" + kind] = ads
            out["def_" + kind] = (e - eint[name]) if name in eint else None
        if kind in ("CO2", "H2O") and lst:
            corr = []
            for ads, e, name in lst:
                if name not in eint:
                    corr.append((e, "unverified", ads))
                else:
                    df = e - eint[name]
                    if df < -DEF_TOL:
                        corr.append((eint[name], "refcorr", ads))
                    elif df > DEF_TOL:
                        corr.append((e, "distort", ads))
                    else:
                        corr.append((e, "ok", ads))
            corr.sort()
            out["Ec_" + kind], out["st_" + kind], out["cfgc_" + kind] = corr[0]
    # host-level view of the framework reference: every single-molecule placement of this host that has a record
    rec = [e - eint[name] for kind in ("CO2", "H2O") for (ads, e, name) in d.get(kind, []) if name in eint]
    out["host_n_rec"] = len(rec)
    out["host_min_def"] = min(rec) if rec else None
    out["host_max_def"] = max(rec) if rec else None
    out["host_ref_ok"] = bool(rec) and all(abs(x) <= DEF_TOL for x in rec)
    return out


S = {h: summarise(h) for h in hosts}
n_pr = sum(not s["defective"] for s in S.values())
P(f"  pristine frameworks {n_pr}; defective (hypothetical missing-linker) {len(S)-n_pr}")
both = [s for s in S.values() if "E_CO2" in s and "E_H2O" in s]
P(f"  frameworks with both CO2 and H2O single-molecule energies: {len(both)}")

# data-quality census of the framework-reference problem (flagged by the ODAC25 paper)
defs = np.array([e - eint[n] for h in hosts for (a, e, n) in hosts[h].get("CO2", []) if n in eint])
P(f"  CO2 systems with interaction-energy record: {len(defs)}; E_ads - E_int: median {np.median(defs):+.3f} eV; "
  f"{(defs < -DEF_TOL).mean():.1%} below -{DEF_TOL} eV (empty-MOF reference too high -> binding overstated); "
  f"{(defs > DEF_TOL).mean():.1%} above +{DEF_TOL} eV (framework distorts); {(np.abs(defs) <= DEF_TOL).mean():.1%} within +-{DEF_TOL} eV")

# reproduce the paper's 'promising' count: E_CO2 < -0.5 eV and E_CO2 < E_H2O
prom_p = [s for s in both if not s["defective"] and s["E_CO2"] < -0.5 and s["E_CO2"] < s["E_H2O"]]
prom_d = [s for s in both if s["defective"] and s["E_CO2"] < -0.5 and s["E_CO2"] < s["E_H2O"]]
paper_p = {r["MOF"] for r in csv.DictReader(open(os.path.join(HERE, "promising_pristine_MOFs.csv")))}
paper_d = {r["Name"] for r in csv.DictReader(open(os.path.join(HERE, "promising_defective_MOFs.csv")))}
P(f"  paper's criteria re-applied here: {len(prom_p)} pristine, {len(prom_d)} defective "
  f"(paper lists {len(paper_p)} and {len(paper_d)}; overlap {len(paper_p & {s['host'] for s in prom_p})} and {len(paper_d & {s['host'] for s in prom_d})})")

# ----------------------------------------------------------------------------------------------
# E. Benchmark: DFT E_ads vs measured isosteric heats for well-known MOFs present in ODAC23
# ----------------------------------------------------------------------------------------------
P("\n" + "=" * 100)
P("E. BENCHMARK  (ODAC23 lowest E_ads + delta_CO2  vs  measured low-coverage Qst)")
# (host, common name, measured Qst kJ/mol, provenance)
BENCH = [
    ("FUDQIF", "SIFSIX-3-Zn", 45.0, "confirmed this run (Nugent 2013 via search snippet)"),
    ("VOGTIV_clean_h", "Mg-MOF-74", 43.5, "recalled, Queen 2014; not re-fetched"),
    ("ORIVUI", "Ni-MOF-74", 38.6, "recalled, Queen 2014; not re-fetched"),
    ("ORIWAP", "Co-MOF-74", 33.6, "recalled, Queen 2014; not re-fetched"),
    ("ORIWET", "Mn-MOF-74", 31.7, "recalled, Queen 2014; not re-fetched"),
    ("FIJDOS", "Zn-MOF-74", 26.8, "recalled, Queen 2014; not re-fetched"),
]
errs = []
for host, nm, qst, prov in BENCH:
    s = S.get(host)
    if not s or "E_CO2" not in s:
        P(f"  {nm:<12} {host:<16} not in dataset")
        continue
    dH = s["E_CO2"] * EV + DELTA_CO2
    errs.append(dH - (-qst))
    P(f"  {nm:<12} {host:<16} E_ads {s['E_CO2']:+.3f} eV = {s['E_CO2']*EV:6.1f} kJ/mol -> dH {dH:6.1f} | measured -{qst:.1f} | "
      f"error {dH+qst:+5.1f} | n_cfg {s['n_CO2']} | {prov}")
errs = np.array(errs)
P(f"  mean signed error {errs.mean():+.1f} kJ/mol; RMSE {math.sqrt((errs**2).mean()):.1f} kJ/mol; max |error| {np.abs(errs).max():.1f} (n={len(errs)})")
SIGMAS = (5.0, 10.0)

# positive control: predicted 400 ppm uptake of SIFSIX-3-Zn from DFT energy alone
s = S["FUDQIF"]
th = loading(p400, 298.15, (s["E_CO2"] * EV + DELTA_CO2) * 1e3, DS_PHYS, 1.0)
P(f"  positive control SIFSIX-3-Zn (FUDQIF): predicted fill at 400 ppm = {th:.3f} -> {th*2.5:.2f} mmol/g at q_max 2.5 "
  f"(measured 0.13 mmol/g); DFT E_H2O {s['E_H2O']*EV:.1f} vs E_CO2 {s['E_CO2']*EV:.1f} kJ/mol (water binds more strongly)")

# same material deposited under several CSD refcodes: how reproducible is the lowest energy over a handful of placements?
P("  duplicate-structure reproducibility (lowest raw E_ads, kJ/mol; same material, different CSD entries):")
DUPS = {"HKUST-1": ["FIQCEN", "XAMDUM", "XAMDUM02", "XAMDUM04", "XAMDUM05", "XAMDUM06", "XAMDUM07"],
        "Zn-MOF-74": ["FIJDOS", "WOBHEB", "WOBHEB01"], "UiO-66": ["RUBTAK01_SL", "RUBTAK02_SL", "RUBTAK03_auto"],
        "MOF-5": ["EDUSIF", "MIBQAR16"], "ZIF-8": ["OFERUN", "OFERUN06"]}
dup_c, dup_w = [], []
for nm, hs in DUPS.items():
    c = [S[h]["E_CO2"] * EV for h in hs if h in S and "E_CO2" in S[h]]
    w = [S[h]["E_H2O"] * EV for h in hs if h in S and "E_H2O" in S[h]]
    dup_c += [x - np.mean(c) for x in c]
    dup_w += [x - np.mean(w) for x in w]
    P(f"    {nm:<10} CO2: " + " ".join(f"{x:6.1f}" for x in c) + f"  (range {max(c)-min(c):.1f}) | H2O: " + " ".join(f"{x:6.1f}" for x in w) + f"  (range {max(w)-min(w):.1f})")
P(f"    pooled within-material std: CO2 {np.std(dup_c, ddof=len(DUPS)):.1f} kJ/mol, H2O {np.std(dup_w, ddof=len(DUPS)):.1f} kJ/mol (n={len(dup_c)}, {len(dup_w)})")
dup_cc = []
for nm, hs in DUPS.items():
    c = [S[h]["Ec_CO2"] * EV for h in hs if h in S and "Ec_CO2" in S[h]]
    st_ = [S[h]["st_CO2"][:3] for h in hs if h in S and "Ec_CO2" in S[h]]
    dup_cc += [x - np.mean(c) for x in c]
    P(f"    {nm:<10} CO2 corrected: " + " ".join(f"{x:6.1f}({t})" for x, t in zip(c, st_)) + f"  (range {max(c)-min(c):.1f})")
P(f"    pooled within-material std after reference correction: CO2 {np.std(dup_cc, ddof=len(DUPS)):.1f} kJ/mol")

# ----------------------------------------------------------------------------------------------
# F. Screen
# ----------------------------------------------------------------------------------------------


def metrics(s, dS):
    """Verifier-based numbers. CO2 uses the corrected energy; water is placed relative to CO2 with the raw margin
    E_H2O - E_CO2, in which the empty-framework reference cancels."""
    margin = (s["E_H2O"] - s["E_CO2"]) * EV
    dH = (s["Ec_CO2"] * EV + DELTA_CO2) * 1e3
    dHw = (s["Ec_CO2"] * EV + margin + DELTA_H2O) * 1e3
    bc = langmuir_b(dH, dS, T0) * P_CO2_AIR
    bw = langmuir_b(dHw, DS_H2O, T0) * P_W
    th_dry = bc / (1 + bc)
    th_hum = bc / (1 + bc + bw)
    th_des = loading(P_DES, 373.15, dH, dS, 1.0)
    return {
        "dH": dH / 1e3, "dHw": dHw / 1e3, "fill_dry": th_dry, "fill_humid": th_hum, "water_fill": bw / (1 + bc + bw),
        "resid100": th_des, "wc_dry": max(0.0, th_dry - th_des), "wc_humid": max(0.0, th_hum - th_des),
        "T_des_C": desorption_temperature(dH, dS, P_DES, RESID) - 273.15,
        "margin": margin,
    }


def p_in_window(dH_kj, lo, hi, sigma):
    return norm.cdf((hi - dH_kj) / sigma) - norm.cdf((lo - dH_kj) / sigma)


def screen(dS, label, strong, weak):
    P("\n" + "=" * 100)
    P(f"F. SCREEN  [{label}]  dS = {dS:.0f} J/mol/K ; dH window {strong/1e3:.1f} .. {weak/1e3:.1f} kJ/mol")
    funnel = collections.OrderedDict()
    pool = both
    funnel["frameworks with CO2 and H2O energies"] = len(pool)
    pool = [s for s in pool if s["n_CO2"] >= 3 and s["n_H2O"] >= 2]
    funnel[">=3 CO2 and >=2 H2O placements converged"] = len(pool)
    raw = [s for s in pool if strong / 1e3 <= s["E_CO2"] * EV + DELTA_CO2 <= weak / 1e3]
    funnel["(for reference) raw lowest E_ads in window, no quality check"] = len(raw)
    funnel["(for reference) ...of those, CO2 at least as strong as H2O"] = sum(s["E_H2O"] >= s["E_CO2"] for s in raw)
    inwin = [s for s in pool if strong / 1e3 <= s["Ec_CO2"] * EV + DELTA_CO2 <= weak / 1e3]
    funnel["corrected CO2 dH inside window"] = len(inwin)
    st = collections.Counter(s["st_CO2"] for s in inwin)
    funnel["   status of the deciding CO2 placement: " + ", ".join(f"{k} {v}" for k, v in sorted(st.items()))] = len(inwin)
    chk = [s for s in inwin if s["st_CO2"] in ("ok", "refcorr")]
    funnel["deciding CO2 placement checked against rigid-framework energy (ok or refcorr)"] = len(chk)
    funnel["   (sensitivity) CO2 within 5 kJ/mol of H2O or stronger"] = sum((s["E_H2O"] - s["E_CO2"]) * EV >= -5.0 for s in chk)
    sel = [s for s in chk if s["E_H2O"] >= s["E_CO2"]]
    funnel["TIER A: ...and CO2 binds at least as strongly as H2O (raw margin >= 0)"] = len(sel)
    tb = [s for s in inwin if s["st_CO2"] in ("unverified", "distort") and s["E_H2O"] >= s["E_CO2"]]
    funnel["TIER B: in window, CO2 >= H2O, but deciding placement unverified or framework-distorting"] = len(tb)
    for k, v in funnel.items():
        P(f"  {v:>6}  {k}")
    P(f"  Tier A: pristine {sum(not s['defective'] for s in sel)}, defective {sum(s['defective'] for s in sel)}; "
      f"Tier B: pristine {sum(not s['defective'] for s in tb)}, defective {sum(s['defective'] for s in tb)}")

    def build(lst, tier):
        rows = []
        for s in lst:
            m = metrics(s, dS)
            cr = core_row(s["host"]) or {}
            co = s.get("E_CO2_H2O")
            m.update(host=s["host"], tier=tier, defective=s["defective"], E_CO2=s["E_CO2"], Ec_CO2=s["Ec_CO2"], st_CO2=s["st_CO2"],
                     E_H2O=s["E_H2O"], st_H2O=s["st_H2O"], n_CO2=s["n_CO2"], n_H2O=s["n_H2O"],
                     dE_CO2_given_H2O=(co - s["E_H2O"]) * EV if co is not None else None,
                     host_n_rec=s["host_n_rec"], host_min_def=s["host_min_def"], host_max_def=s["host_max_def"], host_ref_ok=s["host_ref_ok"],
                     metals=cr.get("All_Metals", "?"), oms=oms_flag.get(s["host"], cr.get("Has_OMS", "?")),
                     PLD=float(cr["PLD"]) if cr.get("PLD") else None, LCD=float(cr["LCD"]) if cr.get("LCD") else None,
                     doi=cr.get("DOI_public", ""), in_paper_list=(s["host"] in paper_p or s["host"] in paper_d),
                     p_win_s5=p_in_window(m["dH"], strong / 1e3, weak / 1e3, SIGMAS[0]),
                     p_win_s10=p_in_window(m["dH"], strong / 1e3, weak / 1e3, SIGMAS[1]))
            rows.append(m)
        rows.sort(key=lambda r: (-r["wc_humid"], r["host"]))
        return rows
    return build(sel, "A"), build(tb, "B"), funnel


def show(rows, n=15):
    P(f"  {'#':>2} {'host':<24}{'metals':<9}{'OMS':<6}{'PLD':>5} {'E_CO2':>7}{'Ecorr':>7}{'status':>11}{'E_H2O':>7} {'dH':>6} {'margin':>6} "
      f"{'fill':>5}{'fillRH':>7}{'res100':>7}{'wcDry':>6}{'wcRH':>6}{'Tdes':>5} {'dE|H2O':>7} {'nC/nW':>6} {'Pwin5':>6}{'Pwin10':>7} {'paper':<6}{'hostRec(n,min,max eV)':<22}")
    for i, r in enumerate(rows[:n], 1):
        co = f"{r['dE_CO2_given_H2O']:7.1f}" if r["dE_CO2_given_H2O"] is not None else "    n/a"
        P(f"  {i:>2} {r['host']:<24}{r['metals']:<9}{str(r['oms']):<6}{(r['PLD'] or 0):5.2f} {r['E_CO2']*EV:7.1f}{r['Ec_CO2']*EV:7.1f}{r['st_CO2']:>11}{r['E_H2O']*EV:7.1f} "
          f"{r['dH']:6.1f} {r['margin']:6.1f} {r['fill_dry']:5.2f}{r['fill_humid']:7.2f}{r['resid100']:7.2f}{r['wc_dry']:6.2f}{r['wc_humid']:6.2f}"
          f"{r['T_des_C']:5.0f} {co} {r['n_CO2']:>3}/{r['n_H2O']:<2} {r['p_win_s5']:6.2f}{r['p_win_s10']:7.2f} {('yes' if r['in_paper_list'] else 'no'):<6}"
          + (f"{r['host_n_rec']},{r['host_min_def']:+.2f},{r['host_max_def']:+.2f}{' OK' if r['host_ref_ok'] else ''}" if r['host_n_rec'] else "none"))


rowsA, rowsB, funnel_p = screen(DS_PHYS, "PRIMARY: physisorption-calibrated entropy", s_p, w_p)
P("\n  Units: energies kJ/mol. E_CO2 = lowest raw DFT adsorption energy; Ecorr = reference-corrected value used for the window;")
P("  margin = E_H2O - E_CO2 (positive = CO2 stronger); fill = site filling at 420 ppm, 25 C (dry); fillRH = same with water")
P("  competing for the site at 50% RH; res100 = residual at 100 C under 1 kPa CO2; wc = fill - res100; Tdes = C to reach 20%")
P("  residual at 1 kPa; dE|H2O = CO2 binding with one H2O already adsorbed (raw); Pwin = P(true dH in window) for DFT sigma 5 / 10.")
P("\n  TIER A, PRISTINE (experimentally reported crystal structures), ranked by humid working-capacity fraction:")
show([r for r in rowsA if not r["defective"]], 15)
P("\n  TIER A, DEFECTIVE (hypothetical missing-linker models):")
show([r for r in rowsA if r["defective"]], 10)
P("\n  TIER B, PRISTINE (unverified / distorting deciding placement) - all:")
show([r for r in rowsB if not r["defective"]], 30)
P(f"  Tier B pristine with a passing host-level reference check (other placements of the same host all within +-{DEF_TOL} eV): "
  + ", ".join(r["host"] for r in rowsB if not r["defective"] and r["host_ref_ok"]))
P(f"  Tier B pristine where another placement of the host shows the reference problem (host min E_ads-E_int < -{DEF_TOL} eV): "
  + ", ".join(r["host"] for r in rowsB if not r["defective"] and r["host_min_def"] is not None and r["host_min_def"] < -DEF_TOL))
P("\n  TIER B, DEFECTIVE - all:")
show([r for r in rowsB if r["defective"]], 10)

rowsA_c, rowsB_c, funnel_c = screen(-165.0, "SECONDARY: verifier-default (amine-like) entropy", s_c, w_c)
P("\n  TIER A (pristine and defective) under the verifier-default entropy:")
show(rowsA_c, 10)
P("\n  TIER B, PRISTINE under the verifier-default entropy - top 5:")
show([r for r in rowsB_c if not r["defective"]], 5)

# how often does an unverified in-window energy survive the check, judging by the frameworks where the check is possible?
P("\n" + "=" * 100)
P("F2. SURVIVAL RATE OF RAW ENERGIES WHERE THE CHECK IS POSSIBLE (calibrates trust in Tier B)")
pool_ = [s for s in both if s["n_CO2"] >= 3 and s["n_H2O"] >= 2]
for lab, lo_, hi_ in (("physisorption window", s_p, w_p), ("dS=-165 window", s_c, w_c)):
    raw_ = [s for s in pool_ if lo_ / 1e3 <= s["E_CO2"] * EV + DELTA_CO2 <= hi_ / 1e3]
    rec_ = [s for s in raw_ if s["def_CO2"] is not None]
    ok_ = [s for s in rec_ if abs(s["def_CO2"]) <= DEF_TOL]
    sel_ = [s for s in rec_ if s["E_H2O"] >= s["E_CO2"]]
    selok_ = [s for s in sel_ if abs(s["def_CO2"]) <= DEF_TOL]
    P(f"  {lab}: raw in-window {len(raw_)}; with a record {len(rec_)}; consistent (|E_ads-E_int| <= {DEF_TOL} eV) {len(ok_)} = {len(ok_)/max(len(rec_),1):.0%}")
    P(f"     of those with a record AND raw CO2 >= H2O: {len(sel_)}; consistent {len(selok_)} = {len(selok_)/max(len(sel_),1):.0%}")

# ----------------------------------------------------------------------------------------------
# G. Where do the paper's own experimental-ready picks land?
# ----------------------------------------------------------------------------------------------
P("\n" + "=" * 100)
P("G. ODAC23 PAPER'S 'suitable for synthesis' PICKS (Tables 2-3) IN THIS WINDOW (physisorption-calibrated)")
for h in ("ODIXEG", "QOVSOL", "QEFNAQ", "FECXES", "DITYOW", "POLDUQ_0.06_0", "CUGVUW_0.16_0", "PEPKOL_0.08_0", "SUJNUH_0.12_0", "LUYHAP_0.16_0"):
    s = S.get(h)
    if not s or "E_CO2" not in s or "E_H2O" not in s:
        P(f"  {h:<16} missing (no CO2 or H2O energy under the |E/n| < 2 eV rule)")
        continue
    m = metrics(s, DS_PHYS)
    verdict = "IN WINDOW" if s_p / 1e3 <= m["dH"] <= w_p / 1e3 else ("too strong" if m["dH"] < s_p / 1e3 else "too weak")
    dfc = f"{s['def_CO2']:+.3f}" if s["def_CO2"] is not None else "n/a"
    P(f"  {h:<16} raw E_CO2 {s['E_CO2']*EV:7.1f} (E_ads-E_int {dfc} eV)  corrected {s['Ec_CO2']*EV:7.1f} [{s['st_CO2']}]  E_H2O {s['E_H2O']*EV:7.1f}  "
      f"dH {m['dH']:6.1f}  fill {m['fill_dry']:.2f}  Tdes {m['T_des_C']:4.0f} C  -> {verdict}")
allp = [S[h] for h in (paper_p | paper_d) if h in S and "E_CO2" in S[h]]
dHs = np.array([s["E_CO2"] * EV + DELTA_CO2 for s in allp])
dHc = np.array([s["Ec_CO2"] * EV + DELTA_CO2 for s in allp])
stp = collections.Counter(s["st_CO2"] for s in allp)
P(f"  the paper's {len(allp)} promising MOFs, raw energies: {(dHs < s_p/1e3).sum()} bind too strongly for a <=120 C swing, "
  f"{((dHs >= s_p/1e3) & (dHs <= w_p/1e3)).sum()} in window, {(dHs > w_p/1e3).sum()} too weak (physisorption-calibrated window)")
P(f"  same, corrected energies: {(dHc < s_p/1e3).sum()} too strong, {((dHc >= s_p/1e3) & (dHc <= w_p/1e3)).sum()} in window, {(dHc > w_p/1e3).sum()} too weak; "
  f"deciding-placement status: " + ", ".join(f"{k} {v}" for k, v in sorted(stp.items())))
rawdef = np.array([s["def_CO2"] for s in allp if s["def_CO2"] is not None])
P(f"  of the {len(rawdef)} promising MOFs whose lowest raw CO2 placement has an interaction-energy record: "
  f"{(rawdef < -DEF_TOL).sum()} have E_ads - E_int < -{DEF_TOL} eV (binding overstated by the reference), median overstatement "
  f"{-np.median(rawdef[rawdef < -DEF_TOL])*EV:.0f} kJ/mol; {(rawdef > DEF_TOL).sum()} distort the framework; {(np.abs(rawdef) <= DEF_TOL).sum()} consistent")
P(f"  under dS=-165 (raw): {(dHs < s_c/1e3).sum()} too strong, {((dHs >= s_c/1e3) & (dHs <= w_c/1e3)).sum()} in window, {(dHs > w_c/1e3).sum()} too weak")

# ----------------------------------------------------------------------------------------------
# H. What an in-window physisorbent buys in the verifier's cycle model
# ----------------------------------------------------------------------------------------------
P("\n" + "=" * 100)
P("H. VERIFIER CYCLE FOR A GENERIC IN-WINDOW PHYSISORBENT vs AMINE REFERENCE (q_max 2 mol/kg, 100 C, 1 kPa CO2)")
ref = reference_amine_cycle()
P(f"  amine reference: wc {ref.working_capacity:.2f} mol/kg, heat {ref.heat_gj_per_t:.2f} GJ/t, work-eq {ref.work_equivalent_gj_per_t:.2f} GJ/t")
mid = 0.5 * (s_p + w_p)
for dH_, wco in ((s_p, 0.0), (mid, 0.0), (s_p, 2.0), (mid, 2.0)):
    c = TVSACycle(dH=dH_, dS=DS_PHYS, q_max=2.0, T_des=373.15, p_des=1.0e3, water_coads=wco)
    P(f"  physisorbent dH {dH_/1e3:.1f}, dS {DS_PHYS:.0f}, water co-desorbed {wco:.0f} mol/mol: wc {c.working_capacity:.2f} mol/kg, "
      f"heat {c.heat_gj_per_t:.2f} GJ/t (reaction {gj_per_tonne(c.reaction_heat):.2f}, sensible {gj_per_tonne(c.sensible_heat):.2f}, "
      f"water {gj_per_tonne(c.water_heat):.2f}), work-eq {c.work_equivalent_gj_per_t:.2f} GJ/t")

# window width vs DFT error
P("\n" + "=" * 100)
P("I. WINDOW WIDTH vs DFT ERROR")
for sig in SIGMAS:
    c = 0.5 * (s_p + w_p) / 1e3
    P(f"  sigma {sig:.0f} kJ/mol: a MOF computed at the window centre is truly in the window with P = "
      f"{p_in_window(c, s_p/1e3, w_p/1e3, sig):.2f} (physisorption window), {p_in_window(0.5*(s_c+w_c)/1e3, s_c/1e3, w_c/1e3, sig):.2f} (dS=-165 window)")

json.dump({"tierA_primary": rowsA, "tierB_primary": rowsB, "tierA_secondary": rowsA_c, "tierB_secondary": rowsB_c,
           "funnel_primary": funnel_p, "funnel_secondary": funnel_c,
           "DS_PHYS": DS_PHYS, "DELTA_CO2": DELTA_CO2, "DELTA_H2O": DELTA_H2O,
           "window_primary_kJ": [s_p / 1e3, w_p / 1e3], "window_secondary_kJ": [s_c / 1e3, w_c / 1e3]},
          open(os.path.join(HERE, "odac23_screen_results.json"), "w"), indent=1, default=str)
P("\nresults written to odac23_screen_results.json")
