# Scale check of the hydro-weir idea against measured Nam Theun 2 downstream CH4 (Deshmukh et al. 2016)
gwp = 27.0  # AR6 GWP100 non-fossil CH4
capex = 44e6; crf = 0.08  # assumed capital recovery factor (~10 yr @ 5% ~ 0.13; 20yr@5% ~0.08)
for label, kt in [("NT2 first year after commissioning", 10.0), ("NT2 4 yr after impoundment", 2.0)]:
    cap = 0.75*kt*1e3  # t CH4/yr captured
    co2e = cap*gwp
    for c in (0.08, 0.13):
        print(f"{label}: {cap:.0f} t CH4/yr -> {co2e/1e3:.0f} kt CO2e/yr; capex-only $/t at CRF {c}: {capex*c/co2e:.0f}")
# idea's own claim: 47 kt CH4/yr at 2 mg/L, 1000 m3/s, all year
print("idea claim vs NT2 year-4 measured downstream:", 47/2.0, "x")
