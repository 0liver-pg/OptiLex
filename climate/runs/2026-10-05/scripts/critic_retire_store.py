# Critic check: is the forgone oil a property of the field (fixed) or of tonnes stored?
# Case unit from TEA: 10,000 acres, 30 m net pay, 12% porosity.
acre=4046.86; A=10000*acre; h=30; phi=0.12
PV=A*h*phi; bbl=0.158987
for So,Bo in [(0.7,1.2),(0.8,1.2)]:
    OOIP=PV*So/Bo/bbl
    for rf in [0.08,0.12,0.18]:  # incremental CO2-EOR recovery factor (assume, recall Permian 8-18% OOIP)
        oil=OOIP*rf
        for cap_Mt in [11,28,44]:
            print(f"So={So} OOIP={OOIP/1e6:.0f}Mbbl rf={rf} EORoil={oil/1e6:.0f}Mbbl cap={cap_Mt}Mt -> bbl/t stored={oil/(cap_Mt*1e6):.2f}")
# per-field purchase price if all owners paid ($/bbl all-owners 28-52 from TEA netback+royalty)
for oil in [50e6,75e6,110e6]:
    for p in [28,37,52]:
        cost=oil*p
        for rep in [0.5,0.65,0.8]:
            av=oil*0.43*(1-rep)
            print(f"oil={oil/1e6:.0f}Mbbl ${p}/bbl field cost=${cost/1e9:.1f}B  net avoided={av/1e6:.1f}Mt  $/t avoided={cost/av:.0f}")
