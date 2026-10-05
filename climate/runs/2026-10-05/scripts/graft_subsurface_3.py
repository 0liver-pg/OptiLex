"""Verifier for graft_subsurface_3: fracture-stimulated horizontal doublets for in-situ CO2 mineralisation
in hot olivine-rich rock (peridotite), closed-loop CO2-charged water.
Run: cd OptiLex && .venv/bin/python <this file>
Labels: [src] sourced document read this session, [recall] pre-cutoff knowledge not re-verified (web search budget
exhausted this session), [assume] my assumption, [calc] derived here.
Boundary: STORAGE ONLY (CO2 delivered at ~1 bar, high purity). Capture and transport are excluded and added at the end."""
import sys, math
sys.path.insert(0, 'climate')
sys.path.insert(0, 'climate/runs/2026-10-05/scripts')
from physics import *  # noqa
from co2_brine import solubility_pure_water, CP

YR = 3.156e7
M_FO = 140.69e-3          # kg/mol forsterite Mg2SiO4
def hdr(s): print('\n' + '=' * 100 + '\n' + s + '\n' + '=' * 100)
def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)
def comp_gj(p1, p2, T=298.15): return R * T * math.log(p2 / p1) / M_CO2 / 1e6   # ideal isothermal, GJ/t

# ---------------------------------------------------------------- 1. thermodynamics
hdr('1. Thermodynamic floor and reaction energetics')
air = gj_per_tonne(min_separation_work(420e-6, 0.75, 0.99))
pure = gj_per_tonne(min_separation_work(0.95, 0.90, 0.999))
print(f'  Separation floor (upstream, not part of this idea): air {air:.3f} GJ/t; 95% CO2 stream {pure:.4f} GJ/t')
# [recall] Robie & Hemingway (1995) 298 K: dHf / dGf kJ/mol
H = {'Fo': -2174.0, 'Mgs': -1113.3, 'Qz': -910.7, 'CO2': -393.5}
G = {'Fo': -2053.6, 'Mgs': -1029.5, 'Qz': -856.3, 'CO2': -394.4}
dH = 2 * H['Mgs'] + H['Qz'] - H['Fo'] - 2 * H['CO2']
dG = 2 * G['Mgs'] + G['Qz'] - G['Fo'] - 2 * G['CO2']
print(f'  Mg2SiO4 + 2CO2(g) -> 2MgCO3 + SiO2: dH = {dH/2:.1f} kJ/mol CO2, dG = {dG/2:.1f} kJ/mol CO2 (spontaneous)')
print(f'  -> storage step has NO positive work floor; reaction releases {-dH/2/44.01:.2f} GJ_th per t CO2')
print(f'  The only unavoidable work is putting CO2 into solution at pCO2: isothermal floor 1->30 bar '
      f'{comp_gj(1,30):.3f}, 1->60 bar {comp_gj(1,60):.3f} GJ/t')
print(f'  Stoichiometry: {M_FO/(2*M_CO2):.3f} t forsterite per t CO2 (claim 1.60: OK)')
# solid volume change [recall] molar volumes cm3/mol: Fo 43.79, magnesite 28.02, quartz 22.69, amorphous silica ~27.3
for si, vsi in [('quartz', 22.69), ('amorphous silica', 27.3)]:
    dv = (2 * 28.02 + vsi - 43.79)
    print(f'  solid volume change with {si}: +{dv/43.79:.0%} per mol Fo -> {dv/2*1e-6*1e6/44.01:.2f} m3 new solid per t CO2')
dv_t = (2 * 28.02 + 22.69 - 43.79) / 2 * 1e-6 * 1e6 / 44.01

# ---------------------------------------------------------------- 2. kinetics (reproduce the idea's numbers)
hdr('2. Forsterite kinetics, Palandri & Kharaka (2004) [recall params]; reproduce the idea\'s area claims')
def fo_rate(T_C, pH):
    T = T_C + 273.15
    f = lambda Ea: math.exp(-Ea / 8.314 * (1 / T - 1 / 298.15))
    return 10 ** -6.85 * f(67200) * (10 ** -pH) ** 0.47 + 10 ** -10.64 * f(79000)
target = 0.1e6                                    # t CO2/yr per doublet (idea's design)
mol_fo_s = target * 1e6 / 44.01 / 2 / YR
stages, xf, h = 40, 100, 50                       # [assume, idea] 40 stages, 100 m half-length, 50 m height
geo = stages * 2 * xf * h * 2
print(f'  geometric fracture-face area per well {geo:.2e} m2 (idea: 8e5: OK)')
for T, pH in [(40, 5), (60, 5), (90, 5), (90, 4), (120, 5), (150, 5)]:
    r = fo_rate(T, pH); need = mol_fo_s / r
    print(f'  {T:>3} C pH {pH}: r {r:.2e} mol/m2/s, area needed {need:.1e} m2, wall-rock depth at 1e4 m2/m3 '
          f'{need/(geo*1e4)*100:.2f} cm')
rho_rock, f_ol = 3.3, 0.7                         # [assume] t/m3, olivine fraction
rock_m3 = target * M_FO / (2 * M_CO2) / rho_rock / f_ol
print(f'  rock consumed {rock_m3:,.0f} m3/yr -> required front advance {rock_m3/geo*100:.1f} cm/yr per face (idea 8.6: OK)')
Cs = f_ol * rho_rock * 1e6 / 140.69 * 2           # mol CO2 uptake capacity per m3 rock
print(f'  CO2 uptake capacity of rock: {Cs:,.0f} mol/m3 = {Cs*0.04401/1e3:.2f} t CO2/m3')

# ---------------------------------------------------------------- 3. transport limit (NEW check, not in the idea)
hdr('3. Transport into the matrix: can the reaction actually reach 5 cm into low-porosity peridotite?')
def D_co2(T_C):
    """Stokes-Einstein scaling from D25 = 1.91e-9 m2/s [recall], water viscosity from CoolProp."""
    mu = CP.PropsSI('V', 'T', T_C + 273.15, 'P', 100e5, 'Water'); mu25 = CP.PropsSI('V', 'T', 298.15, 'P', 100e5, 'Water')
    return 1.91e-9 * (mu25 / mu) * (T_C + 273.15) / 298.15
for T in (25, 40, 60, 90, 150):
    s = solubility_pure_water(min(T, 100), 60)
    print(f'  CO2 solubility, pure water, 60 bar, {min(T,100)} C (Spycher 2003 model): {s:.2f} mol/kg; D_CO2 {D_co2(T):.2e} m2/s')
C0 = 800.0                                         # mol/m3 dissolved CO2 in the fracture fluid [calc ~0.8 mol/kg]
a_grain = 1e4                                      # m2/m3 [assume, idea's value]
print('  NOTE: 0.9 mol/kg needs dissolution at <=~40 C (or >60 bar); in-situ pressure at 3 km (~300 bar) keeps it dissolved.')
print('  Zero-order reaction-diffusion (optimistic: inlet-pH rate everywhere, no silica passivation, no clogging):')
print(f'  {"T":>4} {"phi":>5} {"D_eff":>9} {"L_pen mm":>9} {"J0 mol/m2/s":>12} {"front mm/yr(1y)":>16} '
      f'{"avg Mt/yr/doublet over 20y":>27} {"area multiplier needed":>23}')
diff_rows = {}
for T, pH in [(90, 5), (150, 5)]:
    for phi in (0.01, 0.03, 0.10):
        Deff = D_co2(T) * phi ** 2                 # Archie m=2 [assume]
        Rv = 2 * fo_rate(T, pH) * a_grain          # mol CO2 /m3/s
        L = math.sqrt(2 * Deff * C0 / Rv)
        J0 = math.sqrt(2 * Deff * C0 * Rv)
        # shrinking-core (reacted rim stays open): front x = sqrt(2 D C0 t / Cs); cumulative uptake = Cs x
        x1 = math.sqrt(2 * Deff * C0 * YR / Cs)
        x20 = math.sqrt(2 * Deff * C0 * 20 * YR / Cs)
        cum20 = Cs * x20 * geo * 0.04401 / 1e9      # Mt over 20 yr (mol x kg/mol -> kg -> Mt)
        avg = cum20 / 20
        mult = target / 1e6 / avg
        diff_rows[(T, phi)] = (avg, mult)
        print(f'  {T:>4} {phi:>5.2f} {Deff:>9.1e} {L*1e3:>9.2f} {J0:>12.2e} {x1*1e3:>16.1f} {avg*1e3:>23.2f} kt/y {mult:>23.0f}')
print('  -> with an open reacted rim, diffusion alone delivers ~mm/yr fronts versus the 86 mm/yr the design needs.')
print('     0.1 Mt/yr per doublet therefore REQUIRES fresh surface to be created continuously (reaction-driven cracking')
print('     or a dense shear-fracture damage zone) with spacing ~cm, i.e. far more area than 40 hydraulic stages give.')
for spacing_cm in (1, 3, 10):
    # if the stimulated volume (40 stages x 2 x 100 m x 50 m x thickness 2 m each side) is cracked at this spacing
    vol = stages * 2 * xf * h * 2 * 2.0            # m3 damage zone, 2 m each side of each wing [assume]
    area = vol * 2 / (spacing_cm / 100)
    print(f'  damage zone 2 m each side, crack spacing {spacing_cm} cm: area {area:.1e} m2 = {area/geo:.0f}x geometric')
new_solid = target * dv_t
frac_vol = geo / 2 * 0.003                         # [assume] 3 mm mean aperture
print(f'  Clogging budget: new solid volume {new_solid:,.0f} m3/yr vs open fracture volume ~{frac_vol:,.0f} m3 and '
      f'matrix pore volume in the reacting rock ({rock_m3:,.0f} m3/yr x 1-3%) {rock_m3*0.01:,.0f}-{rock_m3*0.03:,.0f} m3')
print(f'  -> products occupy {new_solid/frac_vol:.0f}x the open fracture volume each year: permeability survives only if '
      f'cracking makes room (Kelemen) or Mg is carried out and precipitated elsewhere.')

# ---------------------------------------------------------------- 4. residence time and heat
hdr('4. Hydraulics, residence time, heat')
for m, eta in [(0.9, 1.0), (0.75, 0.8), (0.6, 0.5)]:
    w = 1 / (m * 0.04401 * eta)
    q = w * target / YR                            # t/s = m3/s approx
    print(f'  carrier {m} mol/kg, per-pass mineralised fraction {eta:.0%}: {w:.0f} t water/t CO2; flow {q*1e3:.0f} kg/s '
          f'({q*86400/0.158987/1e3:.0f} kbbl/d); residence in fractures {frac_vol/q/3600:.1f} h')
print('  [recall] Fervo Project Red ran ~60-63 kg/s per producer; design needs 70-140 kg/s: plausible, not demonstrated.')
q_base = 1 / (0.75 * 0.04401 * 0.8) * target / YR * 1e3
heat_rxn = -dH / 2 / 44.01 * target / YR * 1e9 / 1e6
for dT in (10, 30):
    print(f'  reaction heat {heat_rxn:.1f} MWth vs heat removed by {q_base:.0f} kg/s loop cooled by {dT} C at surface: '
          f'{q_base*4.18*dT/1e3:.1f} MWth')
print('  -> "co-produce heat" conflicts with the >=90 C kinetic rule: extracting heat cools the fracture faces')
print('     (that is what EGS is designed to do). Kinetics at 60 C need 7.6x the area of 90 C. Heat co-production')
print('     must be limited to roughly the reaction heat, or abandoned.')

# ---------------------------------------------------------------- 5. energy per tonne
hdr('5. Energy per tonne stored (storage boundary)')
cases = {
    'low':  dict(p=30, ceff=0.70, m=0.9, eta=1.0, dp=5e6, peff=0.80, misc=0.01),
    'base': dict(p=60, ceff=0.65, m=0.75, eta=0.8, dp=7.5e6, peff=0.75, misc=0.02),
    'high': dict(p=60, ceff=0.58, m=0.6, eta=0.5, dp=10e6, peff=0.70, misc=0.04),
}
E = {}
for k, c in cases.items():
    comp = comp_gj(1, c['p']) / c['ceff']
    water = 1 / (c['m'] * 0.04401 * c['eta'])     # m3 per t
    pump = water * c['dp'] / c['peff'] / 1e9
    E[k] = comp + pump + c['misc']
    print(f'  {k:<5}: compression 1->{c["p"]} bar at {c["ceff"]:.0%} = {comp:.2f}; circulation {water:.0f} m3/t x '
          f'{c["dp"]/1e6:.1f} MPa / {c["peff"]:.0%} = {pump:.2f}; misc {c["misc"]:.2f} -> {E[k]:.2f} GJ_e/t')
for k in E:
    s = ScaleCheck(1.0, E[k])
    print(f'  {k}: per 1 Gt/yr -> {s.ej_per_year:.2f} EJ_e = {s.share_of_world_electricity_if_electric:.2%} of world electricity '
          f'({s.ej_per_year/3.6e-3:.0f} TWh)')
s = ScaleCheck(1.0, 0.55); s2 = ScaleCheck(1.0, 0.73)
print(f'  CLAIM CHECK "0.55-0.73 GJ/t ~ 1-2% of world electricity per Gt/yr": actually '
      f'{s.share_of_world_electricity_if_electric:.2%}-{s2.share_of_world_electricity_if_electric:.2%} -> claim overstated '
      f'~2-3x (conservative direction; not a physics violation)')
print(f'  vs DAC floor {air:.2f} GJ/t: storage energy is {E["base"]/air:.1f}x the AIR-CAPTURE floor - it is not the bottleneck')

# ---------------------------------------------------------------- 6. cost per tonne
hdr('6. Cost per tonne stored (excludes capture and transport)')
# [src] Fervo S-1/A (2026): GeoBlock ~$7,000/kW x 50 MW incl. wellfield, surface, plant; 8-10 wells per GeoBlock;
#       Cape wells ~9,000 ft TVD, ~14,000 ft MD, ~5,000 ft laterals; per-foot drilling cost down ~70% 2022-25.
blk = 7000 * 50e3
for ws in (0.55, 0.70):                           # [assume] wellfield share of GeoBlock capex
    print(f'  Fervo-derived all-in per well (wellfield share {ws:.0%}, 9 wells): ${blk*ws/9/1e6:.0f}M')
cc = {   # well cost $M (each, incl. stimulation), wells, surface $M, Mt/yr per doublet, WACC, life, elec $/MWh, MMV $/t, O&M frac, restim $M/5yr
    'low':  dict(well=8,  n=2, surf=8,  cap=0.20, r=0.06, life=25, pe=40, mmv=3,  om=0.02, restim=0),
    'base': dict(well=15, n=2, surf=12, cap=0.10, r=0.08, life=20, pe=60, mmv=5,  om=0.03, restim=3),
    'high': dict(well=25, n=2, surf=18, cap=0.03, r=0.10, life=10, pe=90, mmv=10, om=0.04, restim=6),
}
emap = {'low': 'low', 'base': 'base', 'high': 'high'}
COST = {}
for k, c in cc.items():
    capex = (c['well'] * c['n'] + c['surf'] + 5) * 1e6   # +$5M baseline monitoring/permitting [assume]
    t = c['cap'] * 1e6
    ann = capex * crf(c['r'], c['life']) / t
    energy = energy_cost_floor(E[emap[k]], c['pe'])
    om = capex * c['om'] / t
    restim = c['restim'] * 1e6 / 5 / t
    water = 0.02 * 1 / (0.75 * 0.04401) * 1.0      # [assume] 2% loop make-up at $1/m3 desal/brackish
    COST[k] = ann + energy + om + c['mmv'] + restim + water
    print(f'  {k:<5}: capex ${capex/1e6:.0f}M per doublet, {c["cap"]} Mt/yr -> capital ${ann:.1f}/t; energy ${energy:.1f}; '
          f'O&M ${om:.1f}; MMV ${c["mmv"]}; re-stim ${restim:.1f}; water ${water:.1f} => ${COST[k]:.0f}/t')
# diffusion-limited (no cracking) case for the base doublet
avg90 = diff_rows[(90, 0.03)][0]; avg150 = diff_rows[(150, 0.03)][0]
c = cc['base']; capex = (c['well'] * 2 + c['surf'] + 5) * 1e6
for lbl, avg in [('90 C, phi 3%', avg90), ('150 C, phi 3%', avg150)]:
    print(f'  diffusion-limited, no cracking ({lbl}): {avg*1e3:.1f} kt/yr per doublet -> capital alone '
          f'${capex*crf(0.08,20)/(avg*1e6):,.0f}/t (kill case)')
print('  Comparators [recall]: saline-aquifer storage ~$10-30/t (CCS Norway/Northern Lights-type, ex-transport);')
print('  Carbfix commercial storage quoted ~$25-50/t; US 45Q $85/t point source, $180/t DAC (geologic).')
print(f'  With high-purity Gulf CO2 (ammonia/gas processing, capture+compression ~$15-30/t [recall]) and ~$10/t transport:')
for k in COST:
    print(f'    {k}: total ${COST[k]+15+10:.0f}-{COST[k]+30+10:.0f}/t')

# ---------------------------------------------------------------- 7. scale and resources
hdr('7. Realistic scale and resource needs')
for gt in (0.05, 0.2, 1.0):
    n = gt * 1e9 / (cc['base']['cap'] * 1e6)
    print(f'  {gt} Gt/yr at 0.1 Mt/yr/doublet: {n:,.0f} doublets = {2*n:,.0f} wells (US shale drills ~10-20k wells/yr [recall]); '
          f'rock {gt*1e9*M_FO/(2*M_CO2)/rho_rock/f_ol/1e9:.2f} km3/yr; loop water inventory ~{gt*1e9*30/365*0.25/1e6:.0f} Mt; '
          f'make-up {gt*1e9*30*0.02/1e6:.0f} Mt/yr; pads ~{n*2/100:,.0f} km2 at 2 ha each; '
          f'electricity {ScaleCheck(gt, E["base"]).share_of_world_electricity_if_electric:.2%} of world')
print('  [recall, unverified] Kelemen & Matter 2008 (PNAS) estimated Oman peridotite could take order 1 Gt CO2/yr with')
print('  fracturing + heating; regional CO2 supply (UAE + Oman fossil CO2 ~0.25-0.3 Gt/yr [recall]) caps a Gulf hub.')
print('  Hot (>=90 C at <=4 km) ultramafic rock is a small subset of ultramafic outcrop area; resource not mapped.')

# ---------------------------------------------------------------- 8. verdict flags
hdr('8. Flags')
print('  physically_impossible: none. Storage step is exergonic; energy claims sit well above any floor.')
print('  arithmetic: stoichiometry, area, front-rate, water and energy claims reproduce; electricity share overstated 2-3x.')
print('  heroic/central assumption: 0.1 Mt/yr per doublet needs continuous fresh-surface generation (~cm crack spacing, ')
print(f'  ~{diff_rows[(90,0.03)][1]:.0f}x (90 C) / {diff_rows[(150,0.03)][1]:.0f}x (150 C) the area diffusion alone gives at phi 3%) AND '
      f'room for {dv_t:.2f} m3 new solid per tonne.')
print('  internal conflict: heat co-production vs >=90 C kinetic rule.')

# ---------------------------------------------------------------- 9. variant: leach-and-export (products leave the rock)
hdr('9. Variant: if dissolved Mg is carried out (precipitated downstream/at surface), the reacted rim stays porous')
for T in (90, 150):
    for phi_rim in (0.2, 0.4):                     # [assume] rim porosity after olivine dissolves, silica skeleton left
        D = D_co2(T) * phi_rim ** 2
        x1 = math.sqrt(2 * D * C0 * YR / Cs)
        x20 = math.sqrt(2 * D * C0 * 20 * YR / Cs)
        avg = Cs * x20 * geo * 0.04401 / 1e9 / 20
        print(f'  {T} C, rim porosity {phi_rim:.0%}: front {x1*100:.1f} cm in yr 1, {x20*100:.0f} cm by yr 20; '
              f'20-yr average {avg:.3f} Mt/yr per doublet (design 0.1)')
mgs_m3 = 1e6 / 44.01 * 84.31e-3 / 3000.0   # kg / (kg/m3), magnesite 3.0 t/m3
print(f'  but then carbonate forms where pressure/temperature change (producer tubing, surface): {mgs_m3:.2f} m3 '
      f'magnesite per t CO2 to handle -> scaling risk moves to the producer; becomes in-situ leaching + ex-situ storage.')
print('  -> even with products exported and a 20-40% porous rim, diffusion gives 5-15 kt/yr per doublet, 7-20x short of')
print('     0.1 Mt/yr. Only advective flow through a densely cracked (cm-scale) damage zone closes the gap.')
