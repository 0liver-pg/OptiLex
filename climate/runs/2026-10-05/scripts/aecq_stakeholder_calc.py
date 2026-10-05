# Burden of qualification on stakeholders vs market size, and Mammoth utilisation check
qual_cost=(0.1e6,0.3e6)
# amortise over a 36 kt/yr nameplate plant, 10 yr, at various utilisations
for util in (0.0375,0.27,0.9):
    t=36000*util*10
    print(f"util {util:.4f}: qual cost/t over 10y = ${qual_cost[0]/t:.2f}-{qual_cost[1]/t:.2f}")
# Mammoth: 105 t in 10 months vs 36,000 t/yr nameplate, but only 12-24 of 72 machines installed
cap10=36000*10/12
print("Mammoth 105 t / 10-month nameplate =", f"{105/cap10*100:.2f}%")
for inst in (12,24):
    print(f"  per installed share {inst}/72: {105/(cap10*inst/72)*100:.1f}% of installed nameplate")
# Sorbent cost check C/(0.044 q N): $/kg / (kg CO2 per kg sorbent per cycle * N)
for q in (1,2):
    for C in (20,50):
        print(q,C,[round(C/(0.044*q*N)*1000) for N in (1000,5000,20000,100000)])
# Market scale: Frontier AMC $1.8bn; cumulative delivered 1.7 Mt vs 50.5 Mt contracted (cdr.fyi, 2026)
print("delivered/contracted =", f"{1.7/50.5*100:.1f}%")
