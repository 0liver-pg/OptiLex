"""Critic check for anti_availability_3 (dam sediment -> LC3 clay).
(1) Is 'drying fully on waste heat' (the $23/t niche) physically available?
(2) Patched siting rule: only sediment the operator ALREADY dredges and pays to dispose of.
All plant heat figures are recalled typical values, NOT verified (flagged)."""
import sys; sys.path.insert(0, 'climate')
from physics import *  # noqa (verifier import per protocol)
def crf(r,n): return r*(1+r)**n/((1+r)**n-1)
clinker_co2 = 0.510 + 3.4*0.095
# base-case sediment per t calcined clay (CC), from anti_availability_3.py base
k, orgC = 0.35, 0.015
loi = 0.1395*k + orgC*1.5; raw = 1/(1-loi); rho = 0.75; vol = raw/rho
print(f"raw dry sediment {raw:.3f} t/t CC, in-situ {vol:.2f} m3/t CC")
# (1) waste heat budget per t CC in an LC3-50 plant: 0.50/0.30 = 1.667 t clinker per t CC
clk = 0.50/0.30
for spare_per_clk, calc_exh in [(0.15,0.6),(0.3,0.8),(0.45,1.0)]:  # GJ spare after raw/coal mill drying; flash-calciner exhaust GJ/t CC (recalled ranges)
    avail = clk*spare_per_clk + calc_exh
    for m in (0.30,0.40,0.50):
        w = raw*m/(1-m); need = w*3.1
        print(f"spare {spare_per_clk:.2f} GJ/t clk + calciner exh {calc_exh:.1f}: avail {avail:.2f} GJ/t CC | moisture {m:.0%}: need {need:.2f} -> waste-heat share {min(1,avail/need):.0%}")
# (2) patched economics, base parameters, 50 km haul, waste-heat share capped by (1) mid case
def case(label, haul, wh, dredge_cost, disposal_avoided, m=0.40):
    w = raw*m/(1-m); dryf = w*3.1*(1-wh)
    debit = 3.0*0.080 + dryf*0.080 + raw*orgC*44.01/12.01 + (raw+w)*haul*0.08/1e3 + vol*4*0.27e-3
    cf = 0.50 + max(0, 0.40-k)/0.20*0.15
    a = (0.95-cf)/0.30*clinker_co2 - debit
    c_calc = 3.0*5 + 150*crf(0.08,20) + 7
    cost_cc = vol*dredge_cost + raw*8 + dryf*5 + (raw+w)*haul*0.07 + c_calc + 0.04*80 - vol*disposal_avoided
    net = cost_cc + 3.0 - 1.5*35
    q_cc = raw*7 + c_calc + 0.04*80; qnet = q_cc + 3.0 - 1.5*35
    print(f"{label:<55} avoided {a:.3f} t/t CC | dam CC ${cost_cc:6.1f}/t vs quarry ${q_cc:5.1f}/t | dam ${net/a:6.1f}/tCO2, quarry ${qnet/a:6.1f}/tCO2")
case("original niche: 50 km, 100% waste heat, new dredging $10/m3", 50, 1.0, 10, 0.5)
case("same but realistic waste heat ~45%", 50, 0.45, 10, 0.5)
case("PATCH: already-dredged, avoided disposal $5/m3, 45% WH", 50, 0.45, 0, 5)
case("PATCH: already-dredged, avoided disposal $10/m3, 45% WH", 50, 0.45, 0, 10)
case("PATCH at 150 km, avoided disposal $5/m3, 45% WH", 150, 0.45, 0, 5)
