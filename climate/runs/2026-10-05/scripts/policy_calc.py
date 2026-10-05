import sys
sys.path.insert(0, 'climate')
from physics import *
# 1. Germany CCfD round 1: max EUR per tonne
print("CCfD R1 max subsidy EUR/t:", 2.8e9/17e6)
# 2. US methane WEC $1500/t CH4 -> $/t CO2e
for gwp,name in [(29.8,'GWP100 (AR6 fossil)'),(82.5,'GWP20 (AR6 fossil)')]:
    print("WEC $/tCO2e", name, round(1500/gwp,1))
# 3. 45Q $85/t vs fossil CO2 37.4 Gt: annual fiscal cost if universal
print("45Q-for-everything $tn/yr:", 37.4e9*85/1e12)
# 4. CDR delivery gap: contracted 42.5 Mt cumulative; delivered ~1.2% -> Mt
print("delivered Mt at 1.2%:", 42.5*0.012)
# time to deliver contracted at 2024 delivery rate 0.3186 Mt/yr
print("years to deliver 42.5 Mt at 2024 rate:", 42.5/0.3186)
# Microsoft FY25 45 Mt vs Microsoft emissions ~15-17 Mt/yr (assumed scope 1-3 ~15.5Mt FY24)
# 5. CTBO: storing fraction f of 37.4 Gt; cost at $100/t point-source (storage+capture) -> share of fossil fuel spend
fossil_spend_tn = 7.0  # rough assumption, $tn/yr global fossil fuel spending (IEA WEI ~ order of magnitude), flagged as assumption
for f in [0.1,0.5,1.0]:
    for c in [80,150]:
        cost = 37.4e9*f*c/1e12
        print(f"CTBO f={f} c=${c}/t -> ${cost:.2f}tn/yr = {100*cost/fossil_spend_tn:.0f}% of ~$7tn fossil spend")
# per-unit: CO2 per barrel oil ~0.43 t combustion; per GJ gas 0.0561 t
for c in [80,150]:
    print(f"$/bbl at {c}$/t, 10% stored: {0.43*0.1*c:.1f}; 100%: {0.43*c:.0f}")
# 6. NZIA 50 Mt/yr vs EU ETS emissions (~1.1 Gt stationary 2024 assumption)
print("NZIA 50Mt as % of ~1.1Gt ETS stationary:", 50/1100*100)
# 7. thermodynamic floor energy for the 50 Mt at cement/flue concentrations (from verifier constants in task)
for name,gj in [('coal flue',0.16),('gas flue',0.22),('cement',0.11)]:
    print(name, "floor PJ for 50 Mt:", gj*50e6/1e6)
