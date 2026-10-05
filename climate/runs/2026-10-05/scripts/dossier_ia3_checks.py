"""Dossier extension checks for incumbent_assets_3 (patched: small vents -> high-rate SWD pads).
1. Design loading (75% of saturation) vs Permian-like salinity at each release pressure.
2. Tubing friction at 40k/60k bbl/d, incl. a 1.5in dip-tube inside the tubing.
3. Pad-vs-baseline cost sensitivity to loading (re-uses critic_ia3 cost model).
4. Surface degassing volume of CO2-charged brine; 45Q margin.
"""
import math, sys
sys.path.insert(0, 'climate')
from physics import *
src = open('climate/runs/2026-10-05/scripts/incumbent_assets_3.py').read()
end = src.index('print("\\n" + "=" * 78)\nprint("4. TUBING')
import io, contextlib
ns = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(src[:end], ns)
sol = ns['co2_molality_brine']; kgm3 = ns['kg_co2_per_m3_brine']
BBL = 0.158987; YR = 365.25

print("1. DESIGN LOADING at 75% of saturation, kg CO2/m3 (ks 0.10-0.12)")
print("   NaCl molal ~ Permian TDS: 1.5 ~ 85 g/L, 2.0 ~ 110, 2.5 ~ 135, 3.0 ~ 160, 4.0 ~ 200 (assumed mapping)")
for T, P in ((30, 35), (40, 60), (45, 100)):
    row = []
    for m in (1.5, 2.0, 2.5, 3.0, 4.0):
        lo = 0.75 * kgm3(sol(P, T, m, 0.12), m); hi = 0.75 * kgm3(sol(P, T, m, 0.10), m)
        row.append(f"{m}m: {lo:.1f}-{hi:.1f}")
    print(f"   {T}C/{P} bar: " + " | ".join(row))

print("\n2. TUBING FRICTION over 3,000 m (Swamee-Jain, brine 1,100 kg/m3)")
def fric(q, D, Dh=None, A=None):
    A = A or math.pi * D * D / 4; Dh = Dh or D
    v = q / A; Re = 1100 * v * Dh / 1e-3
    f = 0.25 / (math.log10(4.6e-5 / Dh / 3.7 + 5.74 / Re ** 0.9)) ** 2
    return v, f * 3000 / Dh * 1100 * v * v / 2 / 1e5
dip = 1.5 * 0.0254  # 1.5in OD dip-tube / coil
for rate in (40e3, 60e3):
    q = rate * BBL / 86400
    for name, d_in in (("5.5in (4.892 ID)", 4.892), ("7in (6.276 ID)", 6.276), ("9-5/8 casing (8.681 ID)", 8.681)):
        D = d_in * 0.0254
        v, dp = fric(q, D)
        A_ann = math.pi * (D * D - dip * dip) / 4; Dh = D - dip
        v2, dp2 = fric(q, D, Dh, A_ann)
        print(f"   {rate/1e3:.0f}k bbl/d {name}: v {v:.1f} m/s, dP {dp:.0f} bar; with 1.5in dip-tube: v {v2:.1f}, dP {dp2:.0f} bar")

print("\n3. PAD vs DEDICATED-WELL COST, 0.1 Mt/yr source (critic_ia3 model, 8%/20yr, $60/MWh)")
def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)
E = 0.325; r, n = 0.08, 20
def pad(Q, bbl, load, perm, util=0.8):
    pw = bbl * BBL * YR * util * load / 1000; nw = math.ceil(Q / pw)
    mw = Q * E * 1e9 / (YR * 86400) / 1e6 / 0.9
    cx = mw * 1000 * 3000 + 3 * 1e6 + nw * 0.2 * 0.4e6 + nw * (2e6 + perm) + 4e6
    return nw, cx * crf(r, n) / Q + E / 3.6 * 60 + cx * 0.035 / Q + (0.6e6 + nw * 0.1e6) / Q + 1.0
def base(Q, well=12e6):
    e = 0.217 / 0.65 + 0.02; mw = Q * e * 1e9 / (YR * 86400) / 1e6 / 0.9
    cx = mw * 1000 * 3000 + 3e6 + well + 4e6
    return cx * crf(r, n) / Q + e / 3.6 * 60 + cx * 0.035 / Q + 0.6e6 / Q + 1.0
for Q in (0.05e6, 0.1e6, 0.15e6):
    for bbl in (40e3, 60e3):
        out = []
        for load in (8, 12, 16, 20):
            nw, c0 = pad(Q, bbl, load, 0); _, c2 = pad(Q, bbl, load, 2e6)
            out.append(f"{load}kg/m3:{nw}w ${c0:.0f}/${c2:.0f}")
        print(f"   Q {Q/1e6:.2f} Mt/yr, {bbl/1e3:.0f}k bbl/d: " + " | ".join(out))
    print(f"      dedicated well: $12M ${base(Q):.0f}/t, $6M ${base(Q,6e6):.0f}/t, $25M ${base(Q,25e6):.0f}/t")

print("\n4. SURFACE DEGASSING and 45Q")
for load in (10, 15, 20):
    print(f"   {load} kg/m3 fully degassed at 1 atm, 20C: {load/44.01*1e3*0.024055:.1f} m3 CO2 gas per m3 brine")
print("   45Q geologic storage $85/t; pad base cases $27-69/t -> margin $16-58/t before transfer discount")
