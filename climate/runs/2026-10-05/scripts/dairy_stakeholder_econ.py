# Stakeholder-relevant economics for MIR-verified ration balancing (assumptions labelled)
INR_PER_USD = 84.0  # assumption, approx 2025-26
# NDDB RBP (NDP-I, measured programme average): +Rs25.5/day/animal net income
for days in (270, 365):
    gain_inr = 25.5*days
    print(f"farmer net gain {days}d: Rs{gain_inr:,.0f}/yr = ${gain_inr/INR_PER_USD:,.0f}/yr per animal")
carbon = (3, 11)  # $/animal-yr from idea card (intensity basis, $15-30/t)
for d in (270, 365):
    g = 25.5*d/INR_PER_USD
    print(f"  carbon payment as % of feed-saving gain ({d}d): {carbon[0]/g*100:.1f}-{carbon[1]/g*100:.1f}%")
# premium per litre, assumed 1,500-3,000 L/animal-yr (assumption; Indian in-milk animals)
for L in (1500, 3000):
    lo, hi = carbon[0]/L*INR_PER_USD, carbon[1]/L*INR_PER_USD
    print(f"premium at {L} L/yr: Rs{lo:.2f}-{hi:.2f}/L; vs retail ~Rs56-68/L => {lo/68*100:.2f}-{hi/56*100:.2f}% of price")
# programme scale vs national: NDDB NDP-I 2.865 M animals; idea scale 10-30 M animals
print("NDP-I scale 2.865 M animals; idea scale 10-30 M = 3.5-10.5x NDP-I")
