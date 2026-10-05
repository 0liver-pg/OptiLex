# Stakeholder-side magnitudes for retire-and-store (assumptions labelled)
bbl_per_t = (2.0, 3.0)          # incremental EOR oil per t CO2 retained (idea's assumption)
price = (60.0, 75.0)            # WTI $/bbl assumption (2026)
rates = {"primary 4.6%":0.046, "EOR 2.3%":0.023, "EOR+anthropogenic 1.15%":0.0115}
print("Texas severance tax forgone per t CO2 stored ($/t):")
for k,r in rates.items():
    lo = bbl_per_t[0]*price[0]*r; hi = bbl_per_t[1]*price[1]*r
    print(f"  {k}: {lo:.1f}-{hi:.1f}")
# Royalty to mineral owners (1/8 to 1/4 typical; Texas University Lands 20-25% assumption)
for roy in (0.125,0.20,0.25):
    lo = bbl_per_t[0]*price[0]*roy; hi = bbl_per_t[1]*price[1]*roy
    print(f"Royalty forgone at {roy:.3f}: ${lo:.0f}-{hi:.0f}/t CO2")
# Compare to premium budget
for credit in (85,180,500):
    print(f"credit ${credit}: premium 30-75 = {30/credit:.0%}-{75/credit:.0%}")
# Price effect for consumers of one field: e.g., 10 Mt/yr storage x 2.5 bbl/t = 25 Mbbl/yr = 68 kb/d vs ~103 Mb/d world
mt = 10; kbd = mt*1e6*2.5/365/1e3
print(f"10 Mt/yr retired-EOR equivalent: {kbd:.0f} kb/d = {kbd/103000:.3%} of ~103 Mb/d world supply")
