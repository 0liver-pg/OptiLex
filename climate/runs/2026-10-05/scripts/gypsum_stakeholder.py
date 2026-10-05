# Dose of gypsum/ha -> soil S concentration in plough layer, vs Li et al 2023 (500/1000 mg S-input/kg) MeHg study
depth=0.20; bd=1300  # m, kg/m3 (assumed)
soil_kg=depth*1e4*bd
S_frac=32.06/172.17   # CaSO4.2H2O
for t in [0.3,0.7,1.0,2.0,3.6]:
    S=t*1000*S_frac*1e6/soil_kg  # mg S/kg
    SO4=S*96.06/32.06
    print(f"{t} t gypsum/ha -> {S:.0f} mg S/kg ({SO4:.0f} mg SO4/kg); vs 1000 mg/kg: {1000/S:.1f}x lower (if Li dose is as S) / {1000/SO4:.1f}x (if as SO4)")
# Ra-226 burden at the 10 pCi/g cap
for t in [0.7,2.0]:
    Bq=t*1e6*10*0.037
    print(f"{t} t PG at 10 pCi/g -> {Bq/1e3:.0f} kBq Ra-226/ha/season; added soil activity {Bq/soil_kg:.4f} Bq/g (typical soil ~0.03-0.04 Bq/g)")
# Cd: phosphogypsum Cd range assumed 0.5-5 mg/kg (literature range, unverified)
for cd in [0.5,5]:
    for t in [0.7,2.0]:
        g=t*1000*cd/1000
        print(f"PG Cd {cd} mg/kg, {t} t/ha -> {g:.2f} g Cd/ha/season")
