# Scale checks for stakeholder red lines (sediment budget, haul traffic)
plant_clay = 0.33e6      # t/yr dry clay per 1 Mt/yr LC3 plant (idea claim)
mekong_load = 160e6      # t/yr present Mekong sediment load (Wikipedia, Mekong Delta page)
print("one plant / Mekong load: %.2f%%" % (100*plant_clay/mekong_load))
for n in (1,5,20):
    print(f"{n} plants: {100*n*plant_clay/mekong_load:.1f}% of Mekong load")
# fine fraction only: assume ~fines are e.g. 80-90% of load (assumption), so ratios similar
# truck traffic for local community (S11)
wet_factor = 1/(1-0.4)   # 40% moisture by mass of wet sediment -> wet t per dry t
truck_t = 25
trips = plant_clay*wet_factor/truck_t
print("truck loads/yr (wet, 40%% moisture): %.0f, per day (300 d): %.0f" % (trips, trips/300))
