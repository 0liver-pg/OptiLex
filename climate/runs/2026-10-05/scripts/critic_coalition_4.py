# Critic check: metric consistency and process/fuel capture accounting
p_clk = 0.65*44.01/56.08 + 0.015*44.01/40.30   # t CO2 process / t clinker
print("process CO2 per t clinker", round(p_clk,3))
# Metric A (idea): unabated process CO2 per t clinker, no capture
for cr in (0.71,0.50):
    print(f"CR={cr}: metric A = {p_clk:.3f} t/t clk (unchanged); metric B per t cement = {p_clk*cr:.3f}")
print("metric B reduction 0.71->0.50:", round(1-0.50/0.71,3))
# Fuel CO2 per t clinker: ~3.4 GJ/t clk thermal, fuel mix ~95 kg CO2/GJ (coal/petcoke) [ASSUME]
fuel = 3.4*0.095
share_proc = p_clk/(p_clk+fuel)
print("fuel CO2/t clk", round(fuel,3), "process share of kiln CO2", round(share_proc,3))
# Post-combustion amine capturing X% of total kiln flue: if all counted as process
for X in (0.5,0.6,0.9):
    cap = X*(p_clk+fuel)
    claimed = min(cap,p_clk)/p_clk
    true = X
    print(f"capture {X:.0%} of flue: if credited as process -> {claimed:.0%} process 'abated' vs pro-rata {true:.0%}")
