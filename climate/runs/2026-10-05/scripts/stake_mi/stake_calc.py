import sys
sys.path.insert(0, 'climate')
from physics import *
KG_CH4_PER_MMBTU = 1055.06/55.5  # MJ per MMBtu / HHV MJ/kg -> ~19.0 kg
g = GWP100['CH4_fossil']
print(f"kg CH4/MMBtu {KG_CH4_PER_MMBTU:.2f}")
# Clause: slope $30/t CO2e GWP100 around 0.5% reference
slope_co2e = 30.0
slope_ch4 = slope_co2e*g
print(f"clause slope = ${slope_ch4:.0f}/t CH4 (GWP100)")
def clause(i, ref=0.005): return -(i-ref)*KG_CH4_PER_MMBTU/1000*slope_ch4
# Repealed US Waste Emissions Charge: $1500/t CH4 on emissions above 0.2% of gas sent to sale (production segment)
def wec(i, thr=0.002, fee=1500): return -max(0,i-thr)*KG_CH4_PER_MMBTU/1000*fee
for i in [0.002,0.005,0.01,0.02,0.032]:
    print(f"intensity {i*100:.1f}%: clause {clause(i):+.3f} $/MMBtu, WEC(2026 rate) {wec(i):+.3f} $/MMBtu, ratio clause/WEC {clause(i)/wec(i) if wec(i) else float('nan'):.2f}")
# Implied $/t CO2e of WEC
print(f"WEC $1500/t CH4 = ${1500/g:.0f}/t CO2e GWP100, ${1500/GWP20['CH4_fossil']:.0f}/t CO2e GWP20")
# Consumer side: EU household retail gas ~ EUR 0.10-0.12/kWh -> $/MMBtu
for eur_kwh in [0.08,0.12]:
    usd_mmbtu = eur_kwh*1.08*293.07
    print(f"retail {eur_kwh} EUR/kWh = ${usd_mmbtu:.0f}/MMBtu; a $0.26 max discount = {0.26/usd_mmbtu*100:.2f}% of retail")
# Henry Hub ~ $3; Permian Waha netback can be <$1 or negative
for netback in [3.0,1.0,0.5]:
    print(f"producer netback ${netback}/MMBtu: discount at 2.0% = {abs(clause(0.02))/netback*100:.0f}% of netback; at 3.2% = {abs(clause(0.032))/netback*100:.0f}%")
