import sys
sys.path.insert(0, 'climate')
from physics import *
# Field-level sizing (assumptions from critic's TEA case unit; not verified)
acres=10000; area=acres*4046.86; h=30; phi=0.12
for Soi in (0.70,0.80):
    for Bo in (1.2,):
        ooip_m3=area*h*phi*Soi/Bo; ooip_bbl=ooip_m3*6.2898
        print(f"Soi={Soi}: OOIP={ooip_bbl/1e6:.0f} Mbbl")
ooip=(535e6,611e6)
for rf in (0.08,0.18):
    for o in ooip:
        eor=rf*o
        for cap in (11e6,44e6):
            pass
# per-field retirement economics
co2_per_bbl=0.43
for eor_bbl in (43e6,110e6):
  for price in (28,52):
    for repl in (0.5,0.8):
      cost=eor_bbl*price
      net_t=eor_bbl*co2_per_bbl*(1-repl)
      for pv in (1.0,0.5):
        print(f"EOR {eor_bbl/1e6:.0f}Mbbl ${price}/bbl repl {repl} PVfac {pv}: cost ${cost*pv/1e9:.2f}B, net avoided {net_t/1e6:.1f} Mt, ${cost*pv/net_t:.0f}/t")
# per-bbl break-even at kill threshold $150/t net at 80% replacement
print("max $/bbl (PV) for $150/t at repl 0.8:", 150*co2_per_bbl*0.2, "; at repl 0.5:",150*co2_per_bbl*0.5)
