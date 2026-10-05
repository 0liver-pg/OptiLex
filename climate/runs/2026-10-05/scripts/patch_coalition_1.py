import sys, random, statistics as st
sys.path.insert(0, 'climate')
from physics import *
GWP=GWP100['CH4_fossil']; slope=30.0  # $/t CO2e
kg=19.01  # kg CH4 per MMBtu (from coalition_ideas.py)
def usd_per_mmbtu(dI_pp): return slope*GWP*kg*dI_pp/100/1000
print(f"slope ${slope}/tCO2e = ${slope*GWP:.0f}/t CH4; 0.1pp intensity = ${usd_per_mmbtu(0.1):.4f}/MMBtu")
# 1. Marginal incentive per own tonne abated
print("\n1) marginal reward per t CO2e of own abatement")
for share,clause in [(0.02,0.5),(0.10,1.0)]:
    print(f"  basin settle (old max rule), share {share}, clause {clause}: ${slope*share*clause:.2f}")
for F in [1.0,1.5,2.5]:
    for clause in [0.5,1.0]:
        print(f"  asset settle F_b={F}, clause {clause}: ${slope*F*clause:.2f}")
# 2. Bias: max rule vs gated reconciliation factor (F set to 1 unless significantly >1)
random.seed(2); n=20000; true=1.5
print("\n2) bias, true intensity 1.5%, L5 complete (true gap F=1)")
for sd in [0.3,0.5]:
    mx=[max(random.gauss(true,sd),random.gauss(true,sd)) for _ in range(n)]
    # gated F: inversion inv ~ N(true, sd); L5 sum unbiased small sd 0.1; F=inv/L5 if inv-L5 > 1.645*sqrt(sd^2+0.1^2) else 1
    g=[]; ug=[]
    for _ in range(n):
        inv=random.gauss(true,sd); l5=random.gauss(true,0.1)
        F_ung=max(1,inv/l5); ug.append(l5*F_ung)
        F= inv/l5 if inv-l5>1.645*(sd**2+0.1**2)**0.5 else 1.0
        g.append(l5*F)
    print(f"  sd {sd}: max-rule bias {st.mean(mx)-true:+.3f} pp | ungated max(1,F) {st.mean(ug)-true:+.3f} pp | gated F {st.mean(g)-true:+.3f} pp")
# with a real L5 gap: L5 reports 60% of true -> F should be ~1.67
print("  real gap, L5 = 60% of true 1.5%, sd 0.3:")
r=[]
for _ in range(n):
    inv=random.gauss(true,0.3); l5=random.gauss(0.9,0.06)
    F= inv/l5 if inv-l5>1.645*(0.3**2+0.06**2)**0.5 else 1.0
    r.append(l5*F)
print(f"   gated settled mean {st.mean(r):.3f}% vs true {true}% (bias {st.mean(r)-true:+.3f} pp)")
# 3. Clean operator in dirty basin
print("\n3) clean operator (L5 0.2%) in basin with inversion 3.0% vs sum-L5 1.2% (F=2.5)")
for name,I in [("old max rule (basin)",3.0),("patch L5*F",0.2*2.5)]:
    print(f"  {name}: settled {I:.2f}%  -> differential vs 0.5% ref {-usd_per_mmbtu(I-0.5):+.3f} $/MMBtu")
# 4. Laundering: untraced portfolio volume at basin P90 vs traced
print("\n4) default for untraced volume: basin inversion 1.5% +/- 0.3 (1 sd) -> P90 =", round(1.5+1.2816*0.3,2),"%")
p90=1.5+1.2816*0.3
for traced in [0.3,0.8,1.5]:
    print(f"  traced at {traced}% vs untraced default {p90:.2f}%: untraced pays extra {usd_per_mmbtu(p90-traced):.3f} $/MMBtu")
# 5. Per-contract reference with glide path -0.05pp/yr: expected transfer if operator holds intensity flat
print("\n5) per-contract reference = prior-year intensity, glide -0.05pp/yr")
for yr in range(1,6):
    print(f"  yr{yr}: flat-intensity seller pays {usd_per_mmbtu(0.05*yr):.4f} $/MMBtu; seller cutting 0.1pp/yr earns {usd_per_mmbtu(0.05*yr):.4f}")
# per-contract neutrality: at signing, differential is 0 by construction
# 6. Reshuffling check inputs (rough, from memory, unverified): clause demand vs low-intensity supply
lng=411
for clause_share in [0.35,0.5]:
    for low_share in [0.2,0.3]:
        print(f"  clause demand {clause_share*lng:.0f} Mt vs low-intensity supply {low_share*lng:.0f} Mt -> signal survives: {clause_share>low_share}")
