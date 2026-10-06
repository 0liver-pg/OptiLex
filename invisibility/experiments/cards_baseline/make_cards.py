"""Assemble invisibility/experiments/cards.json from the baseline result files in this folder.

Every number quoted in the card text is read from a JSON file written by run_*.py / p1_optimize_layers_ref.py here.
"""
import json, pathlib
import numpy as np
from cards_common import *  # noqa

D = HERE


def J(name):
    p = D / name
    return json.loads(p.read_text()) if p.exists() else None


QV = J("quad_verified.json") or {}


def qv(name, metric):
    """Adaptive-quadrature uniform band average (verify_quad.py); None if not verified."""
    r = QV.get(name, {}).get(metric)
    return None if r is None else float(r["adaptive"])


def load(name):
    d = J(name)
    if d is not None and "L4" in d:
        d = d["L4"]
    return d


def best_band(names, metric):
    """Lowest ADAPTIVE band average among available designs of one class; returns (value, file, record)."""
    best = (np.inf, None, None)
    for nm in names:
        v = qv(nm, metric)
        if v is not None and v < best[0]:
            best = (v, nm, load(nm))
    return best


def best_single(names, key="search_value"):
    best = (np.inf, None, None)
    for nm in names:
        d = load(nm)
        if d is not None and d[key] < best[0]:
            best = (float(d[key]), nm, d)
    return best


# ---------------- bare-object numbers (cloak2d) ----------------
bare = {
    "band_ext_B0.1": qv("BARE", "ext"),
    "band_ext_B0.1_gl41": band(lambda k: ext_width([], [A], k)),
    "ext_single_kc": float(ext_width([], [A], KC)),
    "band_sector_B0.1": qv("BARE", "sector"),
    "sector_single_kc": float(sector_width_c2d([], [A], KC)),
    "lorentzian_imF_B0.1": lorentzian_imF(lambda k: [], [A], 0.1),
    "band_channels_B0.1": {o: (qv("BARE", f"ch{o}") if o < 3 else band(lambda k, o=o: channel_width_c2d([], [A], k, o)))
                           for o in (0, 1, 2, 3)},
    "single_channels_kc": {o: channel_width_c2d([], [A], KC, o) for o in (0, 1, 2, 3)},
}
(D / "bare_metrics.json").write_text(json.dumps(bare, indent=1))
be, bs = bare["band_ext_B0.1"], bare["band_sector_B0.1"]
ch = bare["band_channels_B0.1"]

# ---------------- P1 ----------------
ref = load("p1_optimize_layers_ref.json")
ref_ext = qv("p1_optimize_layers_ref.json", "ext")
p1_b01 = best_band(["p1_optimize_layers_ref.json", "de_ext_B0.1_L8.json", "lossless_ext_B0.1_L8.json"], "ext")
p1_b0 = best_single(["de_ext_B0.0_L8.json", "de_ext_B0.0_L16.json", "lossless_ext_B0.0_L8.json"])
e12, e20 = J("de_ext_B0.0_L8_epsmax12.json"), J("de_ext_B0.0_L8_epsmax20.json")
aca0 = J("acausal_de_B0_L8.json")

# ---------------- P2 ----------------
p2_b01 = best_band(["de_sector_B0.1_L8.json", "lossless_sector_B0.1_L8.json"], "sector")
p2_b0 = best_single(["de_sector_B0.0_L8.json"])
de_sec = J("de_sector_B0.1_L8.json")
slep = J("sector_slepian_lambda.json")

# ---------------- P3 ----------------
lor = {}
for W in (0.5, 2.0, 8.0):
    names = [f"lorentz_W{w}_L4_g0.01{s}.json" for w in (0.5, 2.0, 8.0) if w <= W for s in ("", "_seeded")]
    lor[W] = best_band(names, "ext")   # smaller budgets are valid members of the larger class

summary = dict(
    quadrature="all band values: adaptive scipy.integrate.quad on 8 panels (verify_quad.py) with cloak2d; B = 0 values exact",
    bare=bare,
    P1=dict(opt_layers_ref=dict(ref, band_ext_adaptive=ref_ext), best_B0p1=p1_b01[0], best_B0p1_src=p1_b01[1],
            best_B0p1_eps=p1_b01[2]["eps"], best_B0p1_sector=qv(p1_b01[1], "sector"),
            best_B0=p1_b0[0], best_B0_src=p1_b0[1], best_B0_eps=p1_b0[2]["eps"],
            epsmax12_B0=e12["search_value"], epsmax20_B0=e20["search_value"],
            acausal_B0p1_L4=qv("acausal_ref_B0.1_L4.json", "ext"), acausal_B0_L8=(aca0 or {}).get("ext_cloak2d")),
    P2=dict(best_B0p1=p2_b01[0], best_B0p1_src=p2_b01[1], best_B0p1_ext=qv(p2_b01[1], "ext"),
            best_B0p1_eps=p2_b01[2]["eps"], best_B0=p2_b0[0] if p2_b0[2] else None,
            ref_design_sector=qv("p1_optimize_layers_ref.json", "sector"),
            node_exploit_example=dict(file="de_sector_B0.1_L8.json", gl21_search=de_sec["search_value"],
                                      gl41=de_sec["rescored_41pt"]["sector"], dense201=de_sec["dense201_avg"],
                                      adaptive=qv("de_sector_B0.1_L8.json", "sector"), dense201_max=de_sec["dense201_max"])),
    P3={str(W): dict(ext=v[0], src=v[1], sca=qv(v[1], "sca"), abs=v[0] - qv(v[1], "sca"),
                     eps_at_kc=v[2]["eps_at_kc"], budget_used=v[2]["budget_used"], k0_over_kc=v[2]["k0_over_kc"],
                     kp2_over_kc2=v[2]["kp2_over_kc2"]) for W, v in lor.items()},
    P4={})
S1 = summary["P1"]
# =====================================================================================================================
# Card text
# =====================================================================================================================
def f3(x):
    return f"{x:.3g}"


def f4(x):
    return f"{x:.4g}"


CONV = ("Conventions (sim/cloak2d.py): a = 1, k = omega/c, time exp(-i omega t); TM, incident E_z = exp(i k x); scattered "
        "E_z = sum_n i^n b_n(k) H_n^(1)(k r) e^{i n phi} with b_n = cloak2d.coeffs(m_layers, radii, k, pol='TM', core='pec'); "
        "T(phi;k) = sum_n b_n e^{i n phi}; sigma_ext = -(4/k) sum_n Re b_n; sigma_sca = (4/k) sum_n |b_n|^2; "
        "d sigma/d phi = (2/(pi k)) |T(phi)|^2 (forward = phi 0); uniform band average <g>_B = (1/(k_c B)) "
        "int_{k_c(1-B/2)}^{k_c(1+B/2)} g dk, evaluated by adaptive quadrature (verify_quad.py: scipy.integrate.quad on 8 panels, "
        "epsrel 1e-8) and cross-checked with cloak2d.band_average(g, k_c, B, n=41).")

S1 = summary["P1"]; S2 = summary["P2"]; S3 = summary["P3"]; S4 = summary["P4"]
bsk = bare["sector_single_kc"]; bek = bare["ext_single_kc"]
rB0 = S1["best_B0"] / bek

cards = []

# ------------------------------------------------------------------ P1
cards.append(dict(
    id="P1",
    title="Band-averaged extinction floor: TM PEC cylinder wrapped in a lossless dielectric annulus (free-form)",
    statement=(
        "Fixed object: perfectly conducting cylinder r < a, TM polarisation, one plane wave. Design region: annulus a < r < b in "
        "vacuum, any 2D pattern (not necessarily rotationally symmetric). Find a certified function L1(k_c a, b/a, B, eps_max) such "
        "that every design in the class satisfies R1 = <sigma_ext>_B / <sigma_ext,bare>_B >= L1, and report the gap ratio "
        "(best design R1 / L1) against layered (optimize_layers) and free-form (ceviche) adversaries in the same class. The class is "
        "lossless, so sigma_ext = sigma_sca for every design and L1 also bounds total scattering. Sanity gates any bound must pass: "
        "(i) for B > 0 the class minimum is strictly positive: in TM with mu = 1, eps enters only the zeroth-order term of "
        "laplacian(E_z) + k^2 eps E_z = 0, so {eps in L^inf, 1 <= eps <= eps_max} is weak-* compact and <sigma_ext>_B is weak-* "
        "continuous, the minimum is attained, and the attained design is a finite passive LTI 2D scatterer, for which zero "
        "scattering on an interval forces T(0;k) = 0 on it, hence everywhere by analyticity in Im k > 0, contradicting the "
        "nonzero low-frequency PEC extinction (2D form of Miller & Monticone 2026, Sec. 5.7); (ii) L1 must be non-increasing "
        "in eps_max and in b/a (nested classes; eps = 1 is allowed). Monotonicity in B is expected but NOT implied, because "
        "the band centre is fixed and a wider window adds frequencies that may be easier to cloak. Gray levels are the weak-* closure of binary {1, eps_max} "
        "patterns (checked: a 50% binary laminate converges to the eps = 3.5 shell, 7.728 vs 7.732 at 512 sublayers), so L1 "
        "also bounds binary topology-optimised designs. Deliverable: L1 versus B with gap ratios, and a statement of which "
        "constraint binds (bandwidth or material class; see baseline)."),
    parameters=(
        "Canonical: k_c a = pi/2 (a = lambda_c/4); b/a = 3 (b = 3 lambda_c/4, the radii of Strekha et al. 2024 Fig. 1); "
        "eps_max = 6 (chi_max = 5); B = 0.1 (uniform window). Sweeps: B in {0, 0.01, 0.03, 0.1, 0.3}; eps_max in {2, 4, 6, 12, 20}; "
        "b/a in {1.5, 2, 3}; k_c a in {0.5, pi/2, 3}. Secondary Lorentzian window half-width dk = k_c B/2. Units: lengths in a."),
    material_class=(
        "Passive, linear, local, non-magnetic (mu = 1), lossless, frequency-independent real eps_zz(x, y) in [1, eps_max] on "
        "a < r < b, arbitrary 2D pattern; vacuum elsewhere; PEC core fixed. A constant real eps >= 1 is causal and passive at all "
        "frequencies (a constant eps < 1 is Kramers-Kronig-inconsistent over a band; cloak2d warns about this). TM with mu = 1 "
        "sees only eps_zz, so anisotropic electric media are included. Layered adversary: L equal-thickness layers, "
        "cloak2d.optimize_layers(L, radii, k_c, B, pol='TM', core='pec', eps_bounds=(1, eps_max), loss_max=0, metric='ext'). "
        "Free-form adversary: ceviche eps(x, y) in [1, eps_max] with the PEC disc as a Dirichlet mask or a large-|eps| conductor, "
        "validated first against the cloak2d bare value."),
    metric=(
        CONV + " Primary: R1 = <sigma_ext>_B / <sigma_ext,bare>_B, with sigma_ext(k) = cloak2d.widths(m, radii, k, pol='TM', "
        "core='pec')[1] and the bare value from m = [], radii = [a]. Quadrature requirement: lossless "
        "adversarial designs can hide sharp resonances between fixed nodes (observed in P2: one design scores 1.018 on 21 "
        "Gauss nodes, 1.102 on 41 and 1.048 adaptively), so report band values from adaptive quadrature (here "
        "scipy.integrate.quad on 8 panels, epsrel 1e-8; verify_quad.py) and use the 41-node value only as a cross-check. Secondary (comparable with Hashemi 2012 and "
        "Strekha 2024): M_L = Im F(k~), F = -(4i/k) sum_n b_n, k~ = k_c(1 + iB/2), b_n = cloak2d.coeffs(m, radii, k~, "
        "core='pec', nmax=60). M_L = int_0^inf sigma_ext(k)[L(k) + L(-k)] dk with L = (dk/pi)/((k - k_c)^2 + dk^2), a positive "
        "unit-mass weight; constant real eps needs no continuation. For the PEC core this weight sees the k -> 0 extinction "
        "singularity sigma_ext ~ pi^2/(k ln^2 k)."),
    baseline=(
        f"Bare PEC (cloak2d, adaptive quadrature): <sigma_ext>_B = {f4(be)} a (single frequency {f4(bek)} a); M_L = "
        f"{f4(bare['lorentzian_imF_B0.1'])} a. cloak2d.optimize_layers unmodified (L = 4, 4 seeds, eps in [1, 6]): <sigma_ext>_B = "
        f"{f4(S1['opt_layers_ref']['band_ext_adaptive'])} a, R1 = {f3(S1['opt_layers_ref']['band_ext_adaptive'] / be)}; design eps = "
        f"[{', '.join(f3(e) for e in S1['opt_layers_ref']['eps'])}], i.e. one eps ~ 4 coating of thickness a/2, vacuum outside. "
        f"Best found at B = 0.1 over all adversaries (optimize_layers L = 4; multi-start L-BFGS-B and differential evolution + "
        f"L-BFGS-B, L = 8): <sigma_ext>_B = {f4(S1['best_B0p1'])} a, R1 = {f3(S1['best_B0p1'] / be)} ({S1['best_B0p1_src']}; eps = "
        f"[{', '.join(f3(e) for e in S1['best_B0p1_eps'])}], again a thick high-index coating). Single frequency B = 0 (DE, L = 8 and 16): best R1 = {f3(rB0)}; "
        f"eps_max = 12 / 20 give R1(B=0) = {f3(S1['epsmax12_B0'] / bek)} / {f3(S1['epsmax20_B0'] / bek)}. So at the canonical "
        "point the layered baseline is limited by the material class, not by bandwidth: R1 changes by only a few per cent "
        "between B = 0 and B = 0.1. Context only (NOT in class): constant eps in [-10, 10] (acausal over a band) gives R1 = "
        f"{f3(S1['acausal_B0p1_L4'] / be)} at B = 0.1 (L = 4), and at B = 0, where it is a legitimate material, R1 = "
        f"{f3(S1['acausal_B0_L8'] / bek)} (L = 8). Free-form (ceviche) adversary not yet run; all layered values are upper "
        "bounds on the class minimum. Files: invisibility/experiments/cards_baseline/{p1_optimize_layers_ref, de_ext_B0.1_L8, "
        "de_ext_B0.0_L8, de_ext_B0.0_L16, de_ext_B0.0_L8_epsmax12, de_ext_B0.0_L8_epsmax20, acausal_*}.json and baseline_summary.json."),
    prior_bound=(
        "None for this card. Rigorous but non-quantitative: R1_min > 0 for every B > 0 (sanity gate (i)). Closest computed bound, "
        "a different problem: Strekha et al. 2024 (PRA 110, 063513) Lagrange-dual bound for a penetrable object (chi_obj = -4 + i "
        "or 4 + 1e-3 i), binary {0, chi_clk = 3 or 5 (+1e-3 i)} pattern, Lorentzian window with chi fixed at omega0 + i domega, "
        "TM, R_obj = lambda0/4, R_des = 3 lambda0/4. Their bound ratio runs from about 1e-3 to 1e-4 at the low end up to 1 over "
        "domega/omega0 = 1e-7..1e-2 (figure axes only; no tabulated values, and the base's two readings differ). It does not transfer to the PEC object or the uniform window without re-running their "
        "dual. All-frequency 2D sum rule int sigma_ext d lambda = pi^2 alpha_TM: vacuous here (alpha_TM is infinite for PEC; "
        "sigma_ext ~ pi^2/(k ln^2 k) as k -> 0). Monticone-Alu 2016 Eq. 218: 3D, large-a, heuristic; not applicable."),
    why_open=(
        "OQ16 (part 1) asks for causality/passivity-based size-bandwidth-performance limits for any cloak. The only computable "
        "full-wave band bound (Strekha 2024) covers penetrable objects, a Lorentzian window and chi fixed at a complex frequency, "
        "with gaps of about 2-500x to designs depending on case. Open here: (a) the PEC object; its TM Green's function is "
        "analytic, G_obj = (i/4)[H_0(k|r - r'|) - sum_n (J_n(ka)/H_n(ka)) H_n(kr) H_n(kr') e^{in(phi - phi')}], so a Strekha-type "
        "dual at k~ = k_c(1 + iB/2) with local power constraints in the annulus is one solve and certifies a floor on M_L; "
        "(b) a flat window: a Lorentzian puts 50% of its weight outside k_c +/- dk, so an M_L floor is not an in-band floor "
        "unless out-of-band extinction is capped (needs a certified channel-count tail for radius b and eps_max) or sampled-"
        "frequency QCQPs with cross-constraints (tutorial Eq. 183) are combined with interpolation control; (c) whether "
        "free-form eps >= 1 designs beat the radial floor found here (see P4); Strekha et al. report their domega = 0 bound "
        "growing in proportion to Im chi_clk (vanishing for lossless chi), so if the true free-form minimum at B = 0 is "
        "positive, current relaxations cannot see it."),
))

# ------------------------------------------------------------------ P2
p2_bestB0 = S2["best_B0"]
cards.append(dict(
    id="P2",
    title="Angle-limited, intensity-only metric: band-averaged scattering into the backward half-plane",
    statement=(
        "Same object, design region, material class and band as P1, but the metric is the scattered power into the observation "
        "sector Theta = {|phi - phi0| <= Delta} (canonical phi0 = pi, Delta = pi/2: the backward half-plane |phi| >= pi/2, with "
        "the incident wave travelling toward phi = 0). Only the intensity in the sector counts. Find a certified L2 such that "
        "R2 = <sigma_Theta>_B / <sigma_Theta,bare>_B >= L2 for every design in the class, and report gap ratios. Structural facts "
        "a bound must respect: (1) sigma_Theta is quadratic in the fields and is not the real or imaginary part of a function "
        "analytic in Im k > 0, so the single-solve complex-frequency reduction (Hashemi 2012; Strekha 2024) does not apply "
        "(Shim, Fan, Johnson & Miller 2019: absorbed and scattered powers cannot be continued analytically); (2) in the lossless "
        "class sigma_Theta <= sigma_sca = sigma_ext, so P1 floors give no floor here, and the adversary can lower sigma_Theta by "
        "sending scattering forward while raising sigma_ext (see baseline); (3) sanity gate: for B > 0 the class minimum is "
        "positive, because T(phi;k) is real-analytic in phi for a finite scatterer (|b_n| decays super-exponentially), so zero "
        "power on an arc of positive width forces T = 0 for all phi, i.e. sigma_sca = 0 on the band, contradicting the P1 gate. "
        "Attainment follows from the same weak-* argument. Single-direction metrics (Delta -> 0) lose this protection (3D "
        "eps = mu spheres have zero backscatter at every frequency, Kerker, Wang & Giles 1983; not verified from the primary "
        "in the base), so Delta > 0 and mu = 1 are "
        "part of the card."),
    parameters=(
        "Canonical: k_c a = pi/2, b/a = 3, eps_max = 6, B = 0.1, phi0 = pi, Delta = pi/2. Variants: Delta in {pi/8, pi/4, pi/2}; "
        "phi0 = pi/2 (side sector); lossy class with Im eps in [0, 0.5], where absorption can lower sigma_Theta (the "
        "scattered-power degeneracy of Jelinek et al. 2021, App. A), so that variant must also report sigma_abs."),
    material_class=(
        "As P1: passive, lossless, non-magnetic, frequency-independent real eps_zz(x, y) in [1, eps_max] in a < r < b, any 2D "
        "pattern, PEC core, TM. Layered adversary: L equal-thickness layers minimising the sector metric (run_de.py sector, "
        "run_lossless.py sector in experiments/cards_baseline); free-form: ceviche with the same metric computed from a "
        "near-to-far projection."),
    metric=(
        CONV + " sigma_Theta(k) = (2/(pi k)) int_{phi0 - Delta}^{phi0 + Delta} |T(phi;k)|^2 dphi = (2/(pi k)) sum_{m,n} conj(b_m) "
        "K_mn b_n, with K_mn = 2 e^{i(n - m) phi0} sin((n - m) Delta)/(n - m) and K_nn = 2 Delta; b_n from cloak2d.coeffs. "
        "Implemented as fastcyl.sector_width(b, n, k, phi0, Delta) in experiments/cards_baseline (checks: the full circle "
        "reproduces sigma_sca exactly; the half-plane kernel matches 20001-point quadrature to 1.3e-9). R2 = <sigma_Theta>_B "
        "(adaptive; 41-node cloak2d.band_average only as a cross-check) divided by the same for the bare PEC (m = [], radii = [a])."),
    baseline=(
        f"Bare PEC: <sigma_Theta>_B = {f4(bs)} a ({f3(bs / be)} of <sigma_ext>_B); single frequency {f4(bsk)} a. Best layered "
        f"design for the sector metric at B = 0.1 (L = 8; DE + L-BFGS-B and multi-start L-BFGS-B): <sigma_Theta>_B = "
        f"{f4(S2['best_B0p1'])} a, R2 = {f3(S2['best_B0p1'] / bs)} ({S2['best_B0p1_src']}). That design has <sigma_ext>_B = "
        f"{f4(S2['best_B0p1_ext'])} a, {f3(S2['best_B0p1_ext'] / be)}x the bare value: it pushes scattering forward. "
        + (f"Single frequency B = 0: R2 = {f3(p2_bestB0 / bsk)} (DE, L = 8). " if p2_bestB0 is not None else "")
        + f"The P1-optimal layered design (eps ~ 4 coating) gives <sigma_Theta>_B = {f4(S2['ref_design_sector'])} a, R2 = "
        f"{f3(S2['ref_design_sector'] / bs)}. No free-form run yet. Rigorous bridge checked and found useless: "
        "sigma_Theta >= lambda_min(K_N/(2 pi)) sigma_sca for designs radiating only in |n| <= N, but lambda_min = "
        f"{slep['N8_hw1.571']['lam_min_all']:.1e} at N = 8 and below round-off at N = 12 (canonical size needs N ~ 12), "
        "so this route is vacuous (sector_slepian_lambda.json). Quadrature warning: the DE sector design scored "
        f"{f4(S2['node_exploit_example']['gl21_search'])} on its 21-node search grid but {f4(S2['node_exploit_example']['adaptive'])} "
        f"adaptively, with an in-band peak of {f3(S2['node_exploit_example']['dense201_max'])} a; band values must be adaptive. Files: de_sector_B0.1_L8.json, de_sector_B0.0_L8.json, "
        "lossless_sector_B0.1_L8.json, baseline_summary.json."),
    prior_bound=(
        "None. No published lower bound on scattering into an angular sector for a fixed object plus design region. Hashemi et "
        "al. 2012 list restricted-angle and phase-insensitive observers as not covered. Strekha 2024 treats several incidence "
        "directions only as summed extinction. Jelinek et al. 2021 (App. A) argue, without numbers, that a scattered-power QCQP "
        "degenerates when the cloak may absorb. Design-side context only (different metric and class, not bounds): Andkjaer & "
        "Sigmund 2011 report topology-optimised all-dielectric cloaks around PEC cylinders with <1-5% residual scattering for "
        "1-4 incidence angles."),
    why_open=(
        "Neither OQ16 nor the tutorial states phase-insensitive or angle-limited metrics; this framing is OptiLex's own "
        "extension (BOUNDS_BRIEF.md). The nearest published hook is OQ15, which asks for bandwidth bounds on directional or "
        "multipolar scattering. Published directional designs reach residuals orders of magnitude below omnidirectional "
        "ones, and no theory constrains them. Tractable first steps: (i) single- and K-frequency QCQP/SDP with sigma_Theta as "
        "the quadratic objective and local power-conservation constraints in the annulus; the class is lossless, so the "
        "absorption degeneracy does not arise; (ii) because the optimiser trades sector power for forward scattering, add the "
        "optical theorem per frequency, sigma_ext = -(4/k) Re T(0) = sigma_sca, as a constraint linking the forward amplitude "
        "to the total; (iii) a continuous-band version needs interpolation control in k, since no analytic continuation "
        "exists."),
))

# ------------------------------------------------------------------ P3
def p3line(W):
    d = S3[str(W)]
    eps = ", ".join(f"{complex(e).real:.3g}{complex(e).imag:+.1e}i" for e in d["eps_at_kc"])
    return (f"W = {W:g}: <sigma_ext>_B = {f4(d['ext'])} a, R3 = {f3(d['ext'] / be)} (<sigma_sca>_B = {f4(d['sca'])}, "
            f"<sigma_abs>_B = {f3(d['abs'])}; budget used {f3(d['budget_used'])}; eps(k_c) per layer = [{eps}])")


cards.append(dict(
    id="P3",
    title="Amount of matter: band-averaged extinction with causal Lorentz cloak material under an electron-count (f-sum) budget",
    statement=(
        "Same object, design region and band as P1, but the cloak material is a causal, passive, dispersive Lorentz medium and "
        "the resource is the total oscillator strength (electron count; tutorial fn. 62 and Eq. 169) in the annulus. Find a "
        "certified L3(W, gamma_min, B) such that R3 = <sigma_ext>_B / <sigma_ext,bare>_B >= L3 for every design in the class: "
        "the least achievable band-averaged extinction as a function of the amount of matter W. Report <sigma_sca>_B and "
        "<sigma_abs>_B too, since the class is lossy. Unlike P1, this class reaches eps < 1 in band (plasmonic layers), at the "
        "price of dispersion and the budget, and a constant eps >= 1 is approached only as W -> infinity (a chi = 5 annulus "
        "far below resonance needs W = 5 (omega0/omega_c)^2). Lorentz media are analytic in Im omega > 0, so the Lorentzian-"
        "window value M_L = Im F(k~) is an exact single solve with the physical continuation eps_j(k~). L3 must be "
        "non-increasing in W, because a larger budget contains the smaller class."),
    parameters=(
        "Canonical: k_c a = pi/2, b/a = 3, B = 0.1, gamma_min = 0.01 omega_c, W in {0.5, 2, 8} (headline W = 0.5, where the "
        "budget binds). Variants: gamma_min in {0.001, 0.01, 0.1} omega_c; lossless limit gamma_min -> 0; B in {0.03, 0.1, 0.3}. "
        "c = 1, so omega and k are interchangeable; A_ann = pi (b^2 - a^2) = 8 pi a^2."),
    material_class=(
        "Passive, causal, local, isotropic, non-magnetic: in a < r < b, eps(x, omega) = 1 + sum_j omega_pj^2(x) / (omega_0j^2(x) "
        "- omega^2 - i gamma_j(x) omega), any number of oscillators, omega_0j >= 0, gamma_j >= gamma_min, omega_pj^2 >= 0, any 2D "
        "pattern. Budget: (1/A_ann) int_ann sum_j omega_pj^2 dA <= W omega_c^2. By the f-sum rule, int_0^inf omega Im eps d omega "
        "= (pi/2) sum_j omega_pj^2, so this caps total oscillator strength. PEC core, TM. Baseline adversary (run_lorentz.py): "
        "L = 4 equal-thickness layers, one oscillator per layer, gamma = gamma_min, free allocation of the budget including an "
        "unused share, omega_0j in [0.05, 20] omega_c; multi-start L-BFGS-B, warm-started from smaller-budget optima."),
    metric=(
        CONV + " R3 = <sigma_ext>_B / <sigma_ext,bare>_B, with b_n = cloak2d.coeffs(sqrt(eps_j(k)), radii, k, pol='TM', "
        "core='pec') evaluated at each k (dispersive indices), band-averaged with cloak2d.band_average(., k_c, B, n=41) and "
        "verified by adaptive quadrature (Lorentz resonances with gamma = 0.01 omega_c are narrower than the node spacing). Also sigma_sca = (4/k) sum |b_n|^2 and sigma_abs = sigma_ext - sigma_sca. "
        "Secondary: M_L = Im[-(4i/k~) sum_n b_n(k~)] at k~ = k_c(1 + iB/2) with eps_j(k~) from the same Lorentz formula."),
    baseline=(
        "Bare PEC: <sigma_ext>_B = " + f4(be) + " a. Best Lorentz-class designs found (L = 4): " + "; ".join(p3line(W) for W in (0.5, 2.0, 8.0))
        + f". Non-dispersive eps in [1, 6] (P1 class, the W -> infinity reference), best layered: R1 = {f3(S1['best_B0p1'] / be)}. "
        "Reading: at W = 0.5 the optimum uses a Drude-like eps(k_c) ~ 0.5 layer plus an eps ~ 2.2 layer (the matter-limited "
        "regime uses sub-unity eps); at W >= 2 it reverts to the eps ~ 4 coating found in P1, with the resonance moved above "
        "the band (omega0 ~ 2.3-3.7 omega_c). Context only: if sub-unity eps were free and non-dispersive (acausal over a band), "
        f"layers would reach R = {f3(S1['acausal_B0p1_L4'] / be)} at B = 0.1 (L = 4). The gap down from the non-dispersive value is "
        "what sub-unity eps would be worth; causality makes the cloak pay for it through dispersion, loss and electrons. All values are adaptive-quadrature band averages of cloak2d and are upper bounds on the class minimum. Files: lorentz_W*_L4_g0.01*.json, acausal_ref_B0.1_L4.json, baseline_summary.json."),
    prior_bound=(
        "None for this card. Related but not applicable: (i) the high-frequency sum rule int_0^inf sigma_ext d omega = "
        "(pi/2c) int omega_p^2 dA (tutorial Eq. 169; 2D form by the same Herglotz argument, my derivation, unverified) needs an "
        "object transparent at high frequency; with the PEC core sigma_ext -> 4a as omega -> infinity, so the integral "
        "diverges and gives no constraint. (ii) Strekha 2024 fixes chi at the complex frequency instead of bounding over a "
        "causal class. (iii) Passive-approximation floor (Gustafsson & Sjoberg 2010; Ivanenko et al. 2019): a Herglotz eps "
        "cannot track a real target eps_t < 0 over the band better than (1 - eps_t)(B/2)/(1 + B/2) in sup norm (the base's "
        "correction; re-verify against the primary). That constrains the material, not the cloaking metric."),
    why_open=(
        "This is OQ16 part 2 ('given a specified amount of matter within a prescribed volume'; fn. 62 names electron count) "
        "made computable. No existing cloaking bound uses an f-sum budget: Strekha fixes chi(omega~), Jelinek fixes a loss "
        "floor, and Monticone & Alu 2013 constrain only the all-frequency integral. Tractable route: at k~ = k_c(1 + iB/2) "
        "the Lorentzian-weighted extinction is one solve. A single oscillator gives chi(k~)/omega_p^2 = 1/(omega_0^2 - k~^2 - "
        "i gamma k~), and sums of oscillators under the budget fill the convex hull of that curve family (including 0), "
        "scaled by W. The matter budget is then a linear constraint over a convex set of local susceptibilities. It can enter "
        "a Strekha / Kuang-Miller dual with local constraints, or the volume-T-matrix oscillator model (Zhang, Monticone & "
        "Miller 2023, Eq. 175c). The result would be the first explicit cloaking-versus-electron-count curve, and it shows "
        "where dispersion (needed for eps < 1, see P4) costs bandwidth."),
))

# ------------------------------------------------------------------ P4
def chmin(order, B):
    names = [f"de_ch{order}_B{B}_L8.json", f"lossless_ch{order}_B{B}_L8.json"]
    if B == 0:
        v = best_single(names)
        return (v[0], v[2]["rescored_41pt"]["ext"]) if v[2] else (None, None)   # B = 0: exact single-frequency values
    v = best_band(names, f"ch{order}")
    return (v[0], qv(v[1], "ext")) if v[2] else (None, None)


pc = {B: {o: chmin(o, B) for o in (0, 1, 2)} for B in (0.0, 0.1)}
summary["P4"]["per_channel"] = {str(B): {str(o): dict(min=v[0], design_total=v[1]) for o, v in d.items()} for B, d in pc.items()}
summary["P4"]["joint_B0"] = S1["best_B0"]
summary["P4"]["joint_B0p1"] = S1["best_B0p1"]


def pc_sentence(B, bareb, jointv, barej):
    parts, tot = [], 0.0
    for o in (0, 1, 2):
        v, t = pc[B][o]
        if v is None:
            tot += bareb[o]; parts.append(f"|n| = {o}: not run (bare {f3(bareb[o])} used)")
        else:
            tot += v; parts.append(f"|n| = {o} alone {v:.2g} a (bare {f3(bareb[o])}; that design's total {f3(t)} a)")
    tot += bareb[3]
    return (f"Per-channel minima at B = {B:g} (eps in [1, 6], L = 8): " + "; ".join(parts)
            + f". Sum of per-channel minima for |n| <= 2 plus the bare |n| = 3 term = {tot:.2g} a, against the best joint design "
            f"{f3(jointv)} a (R4 = {f3(jointv / barej)}).")


PCH = (pc_sentence(0.0, bch_all := bare["single_channels_kc"], summary["P4"]["joint_B0"], bek) + " "
       + pc_sentence(0.1, ch, S1["best_B0p1"], be))
L16 = J("de_ext_B0.0_L16.json")
bch = bare["single_channels_kc"]
cards.append(dict(
    id="P4",
    title="Positive-susceptibility floor for rotationally symmetric cloaks of a TM PEC cylinder (exact 1D multi-channel problem)",
    statement=(
        "Restrict P1 to rotationally symmetric designs eps(r). The cylindrical harmonics then decouple exactly: b_n(k) depends "
        "only on the radial problem (r u')' + (k^2 eps(r) r - n^2/r) u = 0 on a < r < b with u(a) = 0, matched at r = b to "
        "e^{i delta_n}[cos(delta_n) J_n(kr) - sin(delta_n) Y_n(kr)]. Lossless gives s_n = 1 + 2 b_n = e^{2 i delta_n}, so channel n "
        "is cancelled iff delta_n = 0 (mod pi). Find a certified L4(k_c a, b/a, eps_max, B) such that every eps(r) in "
        "[1, eps_max] satisfies R4 = <sigma_ext>_B / <sigma_ext,bare>_B >= L4, starting with the single-frequency case B = 0. "
        f"Numerical evidence for a POSITIVE floor already at B = 0, caused by eps >= 1: radial optima stall at R4 = {f3(S1['best_B0'] / bek)} / "
        f"{f3(S1['epsmax12_B0'] / bek)} / {f3(S1['epsmax20_B0'] / bek)} for eps_max = 6 / 12 / 20, while allowing eps in [-10, 10] at "
        f"one frequency drives R4 to {S1['acausal_B0_L8'] / bek:.1g} (numbers in baseline). Each channel "
        "alone can be cancelled almost exactly, so the floor is a joint-channel effect of one shared eps(r): the optimal "
        "designs suppress n = +/-1 but leave the monopole above its bare value. Conjecture C4 (to prove or refute): for every "
        "finite eps_max, inf over eps(r) in [1, eps_max] of R4(B = 0) > 0 at the canonical size; its behaviour as eps_max -> "
        "infinity is open, because high-index resonances could emulate eps < 1. A proof would be a rigorous full-wave "
        "statement that causal non-dispersive (chi >= 0) rotationally symmetric shells cannot cloak this object even at one "
        "frequency. Below the floor one then needs eps < 1, which over a band requires dispersion, linking this card to P3 "
        "and to bandwidth."),
    parameters=(
        "Canonical: k_c a = pi/2, b/a = 3, eps_max = 6, B = 0 (headline) and B = 0.1. Sweeps: eps_max in {2, 4, 6, 12, 20, 50}; "
        "b/a in {1.25, 1.5, 2, 3}; k_c a in {0.5, 1, pi/2, 3}; B in {0, 0.03, 0.1, 0.3}. Bare channel shares at k_c "
        f"(sigma_|n| / sigma_ext): n = 0: {f3(bch[0] / bek)}, |n| = 1: {f3(bch[1] / bek)}, |n| = 2: {f3(bch[2] / bek)}, "
        f"|n| = 3: {f3(bch[3] / bek)}."),
    material_class=(
        "Passive, lossless, non-dispersive, non-magnetic, rotationally symmetric: any measurable real eps_zz(r) in "
        "[1, eps_max] on a < r < b (TM with mu = 1 sees only eps_zz, so radially anisotropic electric media are included). "
        "PEC core, vacuum outside b. Layered adversary: L equal-thickness layers (run_de.py ext <B> <L>; per-channel: "
        "run_lossless.py ch<n>). Out-of-class references must be labelled: eps < 1 is allowed only at B = 0."),
    metric=(
        CONV + " R4 = sigma_ext(k_c) / sigma_ext,bare(k_c) at B = 0 (cloak2d.widths(m, radii, k_c, pol='TM', core='pec')[1]); "
        "for B > 0 the P1 band ratio. Lossless gives sigma_ext = sigma_sca. Channel diagnostics: sigma_|n| = (4/k)(|b_n|^2 + "
        "|b_-n|^2) for n >= 1, (4/k)|b_0|^2 for n = 0 (equal to the channel extinction -(4/k) sum_{+/-n} Re b_n in this class). "
        "The per-channel relaxation min_eps sum_n sigma_|n| >= sum_n min_eps sigma_|n| is rigorous, but the baseline shows it "
        "is useless here."),
    baseline=(
        f"Bare PEC at k_c: sigma_ext = {f4(bek)} a (channels n = 0, 1, 2, 3: {f3(bch[0])}, {f3(bch[1])}, {f3(bch[2])}, "
        f"{f3(bch[3])} a). Single frequency, eps in [1, 6]: DE + L-BFGS-B gives R4 = {f3(J('de_ext_B0.0_L8.json')['search_value'] / bek)} (L = 8) and "
        f"{f3(L16['search_value'] / bek)} (L = 16). The L = 16 optimum is nearly bang-bang: eps = 6 for a < r < 1.75a, one "
        f"1.92 sublayer, vacuum beyond; its channels are n = 0: {f3(L16['rescored_41pt']['ch0'])} (above bare {f3(bch[0])}), "
        f"|n| = 1: {f3(L16['rescored_41pt']['ch1'])}, |n| = 2: {f3(L16['rescored_41pt']['ch2'])}. eps_max = 12 / 20: R4 = "
        f"{f3(S1['epsmax12_B0'] / bek)} / {f3(S1['epsmax20_B0'] / bek)}. Out of class (eps in [-10, 10], valid at B = 0 only): "
        f"R4 = {f3(S1['acausal_B0_L8'] / bek)} with every channel < 5e-5. " + PCH + " Files: de_ext_B0.0_L8.json, de_ext_B0.0_L16.json, "
        "de_ext_B0.0_L8_epsmax{12,20}.json, acausal_de_B0_L8.json, de_ch{0,1,2}_B0.0_L8.json, lossless_ch{0,1}_B0.1_L8.json, "
        "de_ch2_B0.1_L8.json, quad_verified.json, bare_metrics.json."),
    prior_bound=(
        "None. The only rigorous per-channel sum rule (Bernland, Gustafsson & Nordebo 2011; tutorial Eqs. 208-210, "
        "|ln S0| B/pi <= k0 a) constrains |s_n| and is vacuous for lossless designs (|s_n| = 1), as the tutorial states "
        "(p. 125). It is also a single-channel statement, and the baseline shows single channels are not the obstruction. "
        "Monticone & Alu 2016 Eq. (2)/(4) is a 3D per-harmonic circuit-model (Bode-Fano-inspired) estimate, heuristic per "
        "the tutorial, with no published 2D version; it treats harmonics independently, so it cannot express this "
        "joint-channel floor. The global sum rule (Monticone & Alu 2013: no passive non-diamagnetic cloak lowers the "
        "all-frequency integrated extinction) is the closest in spirit (chi >= 0 cannot help on aggregate), but it is "
        "integral-only and vacuous for a PEC TM core (infinite static polarizability). Quasistatic Cassier-Milton bounds "
        "do not apply at k_c a = pi/2."),
    why_open=(
        "The base flags the cylindrically symmetric case as the place to make or break the Monticone-Alu per-harmonic "
        "estimate ('channels decouple into radial transmission lines ... directly testable with cloak2d.py and "
        "optimize_layers'). That has not been done, and the baseline here shows the real obstruction is cross-channel, which "
        "no published bound captures. Why it is the most tractable route to a genuinely new rigorous result: (1) exact 1D "
        "reduction; (2) at B = 0 the bound is a single-frequency QCQP whose scenarios are the channels |n| <= N (N ~ k b + 4 "
        "~ 9) sharing one eps(r). Local power-conservation constraints on a radial grid (N_r ~ 100) plus cross-channel "
        "constraints of the tutorial Eq. 183 type (channels in place of frequencies) give an SDP of order 1000 x 1000, "
        "feasible with cvxpy + Clarabel on this machine; (3) eps enters the ODE linearly, so by the Pontryagin principle "
        "optimal profiles are bang-bang in {1, eps_max} except on singular arcs. The L = 16 optimum already is, so the design "
        "side reduces to a few switch radii and a gap near 1 is plausible; (4) an analytic route exists (my suggestion, "
        "untested): by Sturm comparison, eps >= 1 can only advance each channel's Prufer phase, and to first order the "
        "phase added to channel n is k^2 int (eps - 1) r sin^2(theta_n) dr. The numerical obstruction is the impossibility of "
        "adding the required phases to n = 0 and n = 1 at once, so a two-channel phase-coupling inequality would give a "
        "closed-form floor; (5) the band version follows by adding frequencies as further scenarios, and comparison with P3 "
        "prices the eps < 1 escape route in electrons and bandwidth."),
))

# ---------------- write ----------------
canon = dict(a=A, k_c_a=KC * A, b_over_a=BOUT / A, B=BW, eps_max=6.0, sector=dict(phi0=float(np.pi), half_width=float(np.pi / 2)),
             gamma_min_over_wc=0.01, W=[0.5, 2.0, 8.0])
outcards = []
for c in cards:
    outcards.append({k: c[k] for k in ("id", "title", "statement", "parameters", "material_class", "metric", "baseline",
                                       "prior_bound", "why_open")})
doc = dict(generated="2026-10-05", source="invisibility/experiments/cards_baseline/make_cards.py",
           verifier="invisibility/sim/cloak2d.py (all reported values re-scored with it)", canonical=canon,
           cards=outcards, baseline_numbers=summary)
(D / "baseline_summary.json").write_text(json.dumps(summary, indent=1, default=float))
(D / "result.json").write_text(json.dumps(dict(cards=[c["id"] for c in outcards], canonical=canon, numbers=summary), indent=1, default=float))
(D.parent / "cards.json").write_text(json.dumps(doc, indent=1, default=float))
(D / "cards_struct.json").write_text(json.dumps(dict(cards=outcards), indent=1))
print("wrote", D.parent / "cards.json")
