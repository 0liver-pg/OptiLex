# Critic check: amine cost share 'a' implied by PEI price and loading vs structured sorbent price,
# and saving sensitivity to support survival N and in-situ coating non-uniformity (capacity penalty).
for pei in (5,10,20):
    for sorb in (20,35,50):
        a=0.40*pei/sorb
        print(f"PEI ${pei}/kg, sorbent ${sorb}/kg -> amine share a={a:.2f}")
def saving(a,N,proc,cap_ret):
    f=a+(1-a)/N+proc           # reload cost as fraction of new sorbent
    # capacity retained after reload lowers kg CO2 per kg-equivalent: cost per t scales 1/cap_ret
    return 1-f/cap_ret
for cap in (1.0,0.9,0.8,0.7):
    print(f"cap_ret={cap}: a=0.25,N=5,proc=0.12 saving={saving(0.25,5,0.12,cap):.0%}; N=3 {saving(0.25,3,0.12,cap):.0%}")
