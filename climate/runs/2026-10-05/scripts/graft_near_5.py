"""Verifier for graft_near_5: forced aeration of brucite-bearing ultramafic tailings heaps
with mine power-station exhaust (~5% CO2).

Sources / basis (M = measured, E = expert/literature estimate, A = my assumption):
  Wilson et al. 2014 IJGGC doi:10.1016/j.ijggc.2014.04.002 (M): Mt Keith passive ~39.8 kt CO2/yr = ~11% of
      mine emissions; ~11 Mt/yr tailings (figures as given in the idea brief; abstract not re-read this run).
  Harrison, Power & Dipple, ES&T 47:126 (2013) doi:10.1021/es3012854 (bench, M): brucite -> nesquehonite,
      rate increases LINEARLY with pCO2 at 1 atm total; CO2 uptake into solution remains rate-limiting;
      authors estimate accelerated brucite carbonation could offset ~22-57% of Mt Keith emissions (E).
  Thermochemistry (approx., Robie & Hemingway-type tables; +/- few kJ/mol, nesquehonite least certain):
      dHf brucite -924.5, CO2(g) -393.5, H2O(l) -285.8, nesquehonite -1977 kJ/mol
      dGf brucite -833.5, CO2(g) -394.4, H2O(l) -237.1, nesquehonite -1723.7 kJ/mol
  Molar volumes: brucite 24.6 cm3/mol (rho 2.37); nesquehonite 138.36/1.84 = 75.2 cm3/mol.
  Tailings handling costs/energy (filtering, agglomeration, conveyor stacking): A, informed by
      filtered/dry-stack literature ranges (~$1-5/t incremental over slurry; order of magnitude only).
"""
import math
import sys

sys.path.insert(0, "climate")
from physics import *  # noqa: F401,F403

M_BRU = 58.32e-3   # kg/mol Mg(OH)2
MU_GAS = 1.8e-5    # Pa s, humid N2/CO2 exhaust ~30 C
T_GAS = 303.15
P_ATM = 101_325.0


def sep(title):
    print("\n" + "=" * 8 + " " + title + " " + "=" * (70 - len(title)))


# ---------------------------------------------------------------------------------------------
sep("1. Thermodynamic floor")
w_sep = min_separation_work(0.05, 0.40, 0.99)
print(f"Reference only: separating CO2 from 5% exhaust (40% capture, 99% pure): {w_sep/1e3:.2f} kJ/mol = "
      f"{gj_per_tonne(w_sep):.3f} GJ/t. The idea does NOT purify CO2, so this floor does not bind.")
dH = -1977.0 - (-924.5 - 393.5 - 2 * 285.8)
dG0 = -1723.7 - (-833.5 - 394.4 - 2 * 237.1)
print(f"Brucite + CO2 + 2H2O(l) -> nesquehonite: dH = {dH:.1f} kJ/mol CO2 ({-dH/1e3/M_CO2/1e3*1e3:.2f} GJ/t heat released), "
      f"dG0 (1 atm CO2) = {dG0:.1f} kJ/mol")
for p in (0.05, 0.03, 0.02, 0.0042, 420e-6):
    dG = dG0 + R * T0 * math.log(1 / p) / 1e3
    print(f"   dG at pCO2 = {p:.4g} atm: {dG:+.1f} kJ/mol  -> {'spontaneous' if dG < 0 else 'NOT spontaneous'}")
print("Floor for capture-into-brucite is <= 0 (exergonic). Required work is transport only (gas, solids, water).")

# ---------------------------------------------------------------------------------------------
sep("2. Capacity claim (a): 11 Mt/yr tailings, 0.5-3 wt% brucite")
TAIL = 11e6  # t/yr
mine_emis = 39.8e3 / 0.11
print(f"Implied Mt Keith emissions (39.8 kt / 11%): {mine_emis/1e3:.0f} kt/yr")
for b in (0.005, 0.015, 0.03):
    mol = TAIL * 1e6 * b / (M_BRU * 1e3)       # mol brucite/yr  (t -> g)
    nesq = mol * M_CO2 / 1e3                   # t CO2 (1 CO2 per Mg; M_CO2 in kg/mol)
    hmgs = 0.8 * nesq                          # hydromagnesite 4 CO2 per 5 Mg
    print(f"  brucite {b:.1%}: nesquehonite {nesq/1e3:6.1f} kt/yr ({nesq/mine_emis:.0%}),"
          f" hydromagnesite {hmgs/1e3:6.1f} kt/yr ({hmgs/mine_emis:.0%})")
print("Claim 33-199 kt (9-55%) reproduces the hydromagnesite stoichiometry; Harrison 2013 estimate 22-57% is consistent.")

# ---------------------------------------------------------------------------------------------
sep("3. Claim (b): dissolved delivery water volume")
KH = 0.034  # mol/(L atm) at 25 C
for p in (0.05, 1.0):
    gL = KH * p * 44.01
    vol = 100e3 * 1e6 / gL / 1e3 / 1e6  # Mm3 per 100 kt
    print(f"  pCO2 {p} atm: {gL:.3f} g/L dissolved CO2(aq) -> {vol:,.0f} Mm3 water per 100 kt (molecular CO2 only)")
print("  Caveat: brucite-buffered pore water (pH ~9-10) carries DIC mainly as HCO3-/CO3--, up to ~10-100x more;"
      " claim (b) is directionally right but overstates the water penalty for alkaline recirculation.")

# ---------------------------------------------------------------------------------------------
sep("4. Claim (c): Darcy blower work, 100 kt/yr, 2 km2 x 8 m pad, 5% CO2")


def gas_flow_m3s(t_co2_yr, x, uptake):
    mol_gas = t_co2_yr * 1e6 / 44.01 / (x * uptake)
    return mol_gas * R * T_GAS / P_ATM / (365.25 * 86400)


def darcy(t_co2_yr, x, uptake, k, area=2e6, L=8.0, eta=0.6, extra_pa=0.0):
    Q = gas_flow_m3s(t_co2_yr, x, uptake)
    v = Q / area
    dp = MU_GAS * v * L / k + extra_pa
    W = Q * dp / eta * 365.25 * 86400  # J/yr
    return Q, v, dp, W / 1e9 / t_co2_yr  # GJ/t


print(f"{'x':>6}{'uptake':>7}{'k m2':>9}{'Q m3/s':>9}{'v m/h':>8}{'dp kPa':>9}{'GJ/t':>9}")
for x in (0.05,):
    for up in (0.3, 0.6):
        for k in (1e-11, 1e-12, 1e-13):
            Q, v, dp, gj = darcy(100e3, x, up, k)
            print(f"{x:>6}{up:>7}{k:>9.0e}{Q:>9.1f}{v*3600:>8.3f}{dp/1e3:>9.2f}{gj:>9.3f}")
print("With +1.5 kPa for exhaust ducting and perforated-pipe distribution (needed for even flow), 60% blower:")
for up in (0.3, 0.6):
    for k in (1e-11, 1e-12):
        Q, v, dp, gj = darcy(100e3, 0.05, up, k, extra_pa=1500)
        print(f"   uptake {up}, k {k:.0e}: dp {dp/1e3:.2f} kPa, {gj:.3f} GJ/t")
print("Air-fed (420 ppm) on the same pad:")
for up in (0.3, 0.6):
    for k in (1e-11, 1e-12, 1e-13):
        Q, v, dp, gj = darcy(100e3, 420e-6, up, k)
        print(f"   uptake {up}, k {k:.0e}: Q {Q:,.0f} m3/s, dp {dp/1e3:,.1f} kPa, {gj:,.1f} GJ/t")
print(f"DAC contactor fan reference (verifier, 75%, 100 Pa): {fan_work_gj_per_tonne(420e-6, 0.75, 100):.2f} GJ/t")
Q, v, dp, _ = darcy(100e3, 0.05, 0.3, 1e-11)
print(f"Aeration flux at 30% uptake: {v*3600:.3f} m3/m2/h  (Cu bioleach heaps typically ~0.01-0.1 Nm3/m2/h, my recollection:"
      " the graft needs 2-20x more air than heap-leach practice)")
pore = 2e6 * 8 * 0.35
print(f"Gas residence time in pad (porosity 0.35): {pore/Q/3600:.1f} h at 30% uptake")

# kinetic requirement
pad_t = 2e6 * 8 * 1.6
print(f"Pad holds {pad_t/1e6:.1f} Mt = {pad_t/TAIL:.1f} yr of tailings; 100 kt/yr needs {100e3/pad_t*1e3:.1f} kg CO2/t tailings/yr")
for b in (0.005, 0.015, 0.03):
    cap = b * 1e3 / 58.32 * 44.01  # kg CO2 per t tailings (nesquehonite)
    print(f"   brucite {b:.1%}: capacity {cap:.1f} kg CO2/t -> required brucite conversion {100e3/pad_t*1e3/cap:.0%}/yr"
          f"{'  (exceeds 100%: impossible on this pad)' if 100e3/pad_t*1e3/cap > 1 else ''}")

# ---------------------------------------------------------------------------------------------
sep("5. Pore clogging by product volume (Kozeny-Carman)")
for b in (0.015, 0.03):
    mol_m3 = 1.6e6 * b / 58.32  # mol brucite per m3 heap (bulk 1.6 t/m3)
    dV = mol_m3 * (75.2 - 24.6) * 1e-6
    phi0 = 0.35
    phi1 = phi0 - dV
    kc = (phi1 ** 3 / (1 - phi1) ** 2) / (phi0 ** 3 / (1 - phi0) ** 2)
    print(f"  brucite {b:.1%}: solid volume gain {dV:.3f} m3/m3 -> porosity {phi0}->{phi1:.3f}, k x{kc:.2f} if uniform"
          " (crusting at the gas front would be far worse)")

# ---------------------------------------------------------------------------------------------
sep("6. Energy and cost per tonne (net of CO2 debits)")
CRF = lambda r, n: r * (1 + r) ** n / ((1 + r) ** n - 1)
cases = {
    #           brucite conv  k      uptake handling kWh/t  $/MWh  incremental $/t tailings  binder frac  binder $/t  pipe spacing m  pipe $/m  fixed capex $M  MRV $/t  water $/m3
    "low":  dict(b=0.03, conv=0.8, k=1e-11, up=0.6, hk=0.5, pe=80, inc=0.5, bf=0.0, bp=0, sp=3.0, pp=4, cap=10, mrv=5, wp=0.5),
    "base": dict(b=0.015, conv=0.6, k=1e-12, up=0.4, hk=1.5, pe=120, inc=2.0, bf=0.005, bp=150, sp=2.0, pp=8, cap=25, mrv=15, wp=1.5),
    "high": dict(b=0.005, conv=0.4, k=1e-12, up=0.3, hk=4.0, pe=180, inc=5.0, bf=0.015, bp=200, sp=1.5, pp=15, cap=60, mrv=30, wp=3.0),
}
EF_ELEC = 0.45   # t CO2/MWh, on-site gas generation
EF_CEM = 0.8     # t CO2/t cement binder
crf = CRF(0.08, 15)
results = {}
for name, c in cases.items():
    stored = TAIL * c["b"] / 58.32 * 44.01 * c["conv"]          # t CO2/yr (nesquehonite basis)
    stored = min(stored, 0.5 * mine_emis)                         # cap: assume ~half of mine CO2 is power-station exhaust (A)
    _, _, dp, gj_blow = darcy(stored, 0.05, c["up"], c["k"], extra_pa=1500)
    gj_hand = TAIL * c["hk"] * 3.6e-3 / stored                  # kWh/t tailings -> GJ/t CO2
    gj_tot = gj_blow + gj_hand
    mwh = gj_tot / 3.6 * stored
    co2_energy = mwh * EF_ELEC
    co2_binder = TAIL * c["bf"] * EF_CEM
    net = stored - co2_energy - co2_binder
    area_yr = TAIL / 1.6 / 8.0                                   # m2 new pad per yr
    pipe_cost = area_yr / c["sp"] * c["pp"]
    water = stored * 2 * 18.0 / 44.01 + stored * (-dH) / 44.01 * 1e3 / 2.43e3 / 1e3 * 0.5  # stoich + half heat evaporates (t)
    costs = {
        "fixed capex (ducts, quench, blowers) annualised": c["cap"] * 1e6 * crf,
        "aeration pipe (sacrificial, per new pad)": pipe_cost,
        "tailings filter/agglomerate/stack (incremental)": TAIL * c["inc"],
        "binder": TAIL * c["bf"] * c["bp"],
        "energy": mwh * c["pe"],
        "water": water * c["wp"],
        "MRV": stored * c["mrv"],
    }
    tot = sum(costs.values())
    results[name] = (stored, net, gj_tot, tot / stored, tot / net if net > 0 else float("inf"))
    print(f"\n[{name}] brucite {c['b']:.1%}, conversion {c['conv']:.0%}, k {c['k']:.0e}, uptake {c['up']:.0%}")
    print(f"  stored {stored/1e3:.1f} kt/yr ({stored/mine_emis:.0%} of mine); blower dp {dp/1e3:.2f} kPa")
    print(f"  energy: blower {gj_blow:.3f} + tailings handling {gj_hand:.2f} = {gj_tot:.2f} GJ/t stored")
    print(f"  CO2 debits: energy {co2_energy/1e3:.1f} kt, binder {co2_binder/1e3:.1f} kt -> NET {net/1e3:.1f} kt/yr")
    print(f"  water {water/1e3:.0f} kt/yr ({water/stored:.2f} t/t)")
    for k_, v_ in costs.items():
        print(f"    {k_:<50}${v_/1e6:8.2f}M  (${v_/stored:7.0f}/t)")
    print(f"  TOTAL ${tot/1e6:.1f}M/yr -> ${tot/stored:.0f}/t stored, ${tot/net:.0f}/t net" if net > 0
          else f"  TOTAL ${tot/1e6:.1f}M/yr -> NET NEGATIVE: binder/energy emissions exceed storage")

print("\nSensitivity: base case if dry stacking is already justified for dam safety/water (incremental tailings cost = 0):")
c = cases["base"]
s, n, g, cs, cn = results["base"]
print(f"  base cost drops by ${TAIL*c['inc']/s:.0f}/t stored -> ${cs - TAIL*c['inc']/s:.0f}/t stored")
print("Sensitivity: base case with cement binder at 1.5%:")
print(f"  binder CO2 {TAIL*0.015*EF_CEM/1e3:.0f} kt/yr vs stored {s/1e3:.0f} kt/yr")

# ---------------------------------------------------------------------------------------------
sep("7. Global scale")
for tail_gt, bru, conv in ((0.2, 0.005, 0.4), (0.4, 0.01, 0.6), (1.0, 0.02, 0.8)):
    gt = tail_gt * bru / 58.32 * 44.01 * conv
    print(f"  ultramafic tailings {tail_gt} Gt/yr x brucite {bru:.1%} x conv {conv:.0%}: {gt*1e3:.1f} Mt CO2/yr = {gt:.4f} Gt"
          f" ({gt/FOSSIL_CO2_GT:.3%} of fossil CO2)")
s = ScaleCheck(0.006, results["base"][2])
print(f"  At ~6 Mt/yr and base {results['base'][2]:.2f} GJ/t: {s.ej_per_year*1e3:.1f} PJ/yr = "
      f"{s.share_of_world_primary_energy:.5%} of world primary energy")
