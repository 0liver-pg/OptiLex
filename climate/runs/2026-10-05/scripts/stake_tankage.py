import sys
sys.path.insert(0, 'climate')
from physics import *
# Stakeholder-relevant magnitudes for graft_near_6 (assumptions labelled)
cap_tph = 270.0          # t CO2/h at full load (idea basis)
for name, cyc in (("30wt% MEA", 0.5), ("5m PZ", 0.86)):  # mol CO2/kg solvent cyclic (idea basis)
    circ = cap_tph*1e6/44.01/cyc/1e3   # t solvent/h
    for holdup_h in (0.5, 1.0):        # ASSUMED conventional system hold-up time
        print(f"{name}: circulation {circ:,.0f} t/h; conventional inventory @{holdup_h}h ~ {circ*holdup_h/1e3:.1f} kt")
for kt in (41, 71):
    print(f"tank inventory {kt} kt -> x{kt/ (12.3*0.5):.0f} to x{kt/(12.3*1.0):.0f} vs MEA conventional 0.5-1 h holdup (approx)")
# S9 consumer: idea saves $13-49/t on ~0.95 Mt/yr at 40% CF
for s in (13, 49):
    print(f"saving ${s}/t x 0.95 Mt = ${s*0.95:.0f}M/yr")
# S1 climate-guard: net capture per t at different marginal grid intensities (e-boiler 0.93 MWh/t; HP 0.43)
for g in (50, 100, 200, 400):
    print(f"grid {g} g/kWh: e-boiler adds {0.93*g/1000:.2f} t/t, heat pump {0.43*g/1000:.2f} t/t")
# Residual: NGCC 90% capture leaves ~0.035 tCO2/MWh stack + upstream methane
for leak in (0.002, 0.01, 0.02):
    # gas per MWh: ~6.3 GJ fuel/MWh at 57% LHV; ~ 0.12 t CH4/MWh fuel mass; GWP100 30, GWP20 83 (AR6 fossil)
    ch4 = 6.3/50.0*leak  # t CH4 leaked per MWh (LHV 50 GJ/t)
    print(f"upstream leak {leak:.1%}: {ch4*30:.3f} tCO2e/MWh GWP100, {ch4*83:.3f} GWP20 vs stack residual ~0.035")
