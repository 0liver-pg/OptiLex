import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
floor = gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99))
# 8 Rivers/Origen application: 4.9 GJ per t CaO; 85% carbonation
co2_per_t_cao = 0.85 * 44.01 / 56.08
print(f"8 Rivers: 4.9 GJ/t CaO at 85% carbonation -> {4.9/co2_per_t_cao:.2f} GJ per t atmospheric CO2 ({4.9/co2_per_t_cao/floor:.1f}x floor)")
# Make-up as limestone fed to the same kiln: N cycles per Ca atom
wc = 0.85 / 0.07409
for N in (8, 10, 30, 100):
    limestone_kg_per_t = 1000 / (wc * M_CO2 * N) * (100.09 / 74.09)     # kg CaCO3 per t CO2 (air)
    extra_energy = 1 / (0.85 * N)                                       # extra calcination duty: 1 fresh CaCO3 per N cycles of 0.85 CO2
    geo_co2 = 1 / (0.85 * N)                                            # t fossil-limestone CO2 co-stored per t air CO2
    print(f"  N={N:>3} cycles: limestone make-up {limestone_kg_per_t:6.0f} kg/t CO2 (${limestone_kg_per_t*0.03:5.1f}/t at $30/t), "
          f"extra kiln duty +{extra_energy:.1%}, extra CO2 to store +{geo_co2:.1%}, spent solids {limestone_kg_per_t/1000:.2f} t/t")
# Heirloom Tracy: implied tray area at the diffusion-limited 3-day flux
for flux in (119, 73):
    print(f"Tray area for 1,000 t/yr at {flux} kg/m2/yr: {1e6/flux:,.0f} m2; for 1 Mt/yr: {1e9/flux/1e6:.1f} km2 of exposed bed")
# Air throughput sanity: capture fraction from air moving over trays; air needed per t at 50% capture
print(f"Air volume per t CO2 at 50% capture: {air_volume_per_tonne(X_AIR, 0.5):,.0f} m3; fan work at 20 Pa: {fan_work_gj_per_tonne(X_AIR,0.5,20):.3f} GJ/t")
# Water: Ca(OH)2 needs RH>50-80%. Humidifying dry air: water to raise 1 t-CO2-worth of air from 20% to 80% RH at 25 C
v = air_volume_per_tonne(X_AIR, 0.5)
dw = (0.8 - 0.2) * 3169 / (R * T0) * 0.018   # kg water per m3
print(f"Humidifying that air from 20% to 80% RH at 25 C: {v*dw/1000:,.0f} t water per t CO2 and {v*dw*2.44e6/1e9:.0f} GJ/t latent heat (drawn from air -> evaporative cooling)")
# Slag legacy heap: 3.6% of potential in ~140 yr; compare with ground material
print(f"Consett slag: 8-10 kg CO2/t over ~150 yr = {9/150*1000:.0f} g CO2/t/yr vs potential ~400 kg/t (Renforth 2019)")
# Renforth potential in context
print(f"2.9-8.5 Gt/yr (2100 potential) = {2.9/FOSSIL_CO2_GT:.0%}-{8.5/FOSSIL_CO2_GT:.0%} of 2024 fossil CO2")
