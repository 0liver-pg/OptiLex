# Stakeholder-relevant magnitudes for the peat-rewetting idea. All inputs are assumptions (recalled, not re-verified).
global_palm_oil_mt = 79.0   # assumed world palm oil production ~79 Mt/yr (USDA-type figure, ~2024/25)
cpo_yield_peat = (2.0, 3.5) # t CPO/ha/yr on peat (assumed, lower than mineral soils)
for frac_palm, area in [("0.5 Mha", 0.5), ("1 Mha", 1.0), ("2 Mha", 2.0)]:
    # assume 72% of rewetted area is oil palm (3.1/4.3 split from Miettinen 2016)
    palm_area = area*3.1/4.3
    lo, hi = [palm_area*y for y in cpo_yield_peat]
    print(f"{frac_palm}: palm area {palm_area:.2f} Mha, lost CPO {lo:.1f}-{hi:.1f} Mt = {100*lo/global_palm_oil_mt:.1f}-{100*hi/global_palm_oil_mt:.1f}% of world supply")
# payment per ha and total programme cost
for price in (10, 26, 50):
    for t in (35, 70):
        pass
for price in (10, 26, 50):
    print(f"${price}/t: payment/ha {35*price}-{70*price} $/ha/yr; 1 Mha programme {35*price*1e6/1e9:.2f}-{70*price*1e6/1e9:.2f} $bn/yr")
# jobs: oil palm labour intensity assumed 0.1-0.2 workers/ha (plantation)
for area in (0.5,1,2):
    pa = area*3.1/4.3*1e6
    print(f"{area} Mha: palm workers at risk ~{pa*0.1/1e3:.0f}-{pa*0.2/1e3:.0f}k (0.1-0.2 workers/ha assumed)")
