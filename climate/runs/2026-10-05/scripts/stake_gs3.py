# Stakeholder-relevant scale numbers for global_south_3 (aglime -> silicate swap)
lime_lo, lime_hi = 35e6, 50e6        # t lime/yr Brazil (idea's recalled range)
swap = 0.30
for ratio in (3, 10):                # t rock per t lime replaced (idea's computed range)
    for lime in (lime_lo, lime_hi):
        displaced = lime*swap
        rock = displaced*ratio
        extra = rock - displaced      # extra tonnage hauled vs lime
        trucks = extra/30             # 30 t payload trucks
        print(f"ratio {ratio:>2}, lime {lime/1e6:.0f} Mt: lime displaced {displaced/1e6:.1f} Mt, rock {rock/1e6:.0f} Mt, extra haul {extra/1e6:.0f} Mt = {trucks/1e6:.2f} M extra 30-t truckloads/yr")
# Avoided CO2 vs Brazil emissions
for f in (0.22, 0.44):
    for lime in (lime_lo, lime_hi):
        av = lime*swap*f
        print(f"factor {f}: avoided {av/1e6:.1f} Mt CO2/yr")
brazil_gross = 2.3e9  # t CO2e, SEEG ~2023 gross (recalled, approx)
print("share of Brazil gross emissions:", 2.5e6/brazil_gross, 7e6/brazil_gross)
# Revenue at stake for lime suppliers (illustrative price range, recalled/unverified)
for p in (15, 40):   # USD/t delivered aglime, assumed
    print(f"lime revenue displaced at ${p}/t: ${lime_lo*swap*p/1e6:.0f}-{lime_hi*swap*p/1e6:.0f} M/yr")
# Credit revenue for avoided emissions at avoidance vs removal prices
for price in (10, 30, 352):
    print(f"credit price ${price}/t: ${2.5e6*price/1e6:.0f}-{7e6*price/1e6:.0f} M/yr")
