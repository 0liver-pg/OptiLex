# Critic check: CO2 back-produced with withdrawn working gas while the UGS keeps cycling.
# Stored CO2 moles = f * C_mol * Rmol ; Rmol = mass ratio * 16.04/44.01
# Lost per year = W_mol * x  (x = mean CO2 mole fraction in withdrawn gas)
import itertools
M_CH4, M_CO2 = 16.04, 44.01
rows=[]
for mass_ratio in (3.2, 4.5):
    Rmol = mass_ratio*M_CH4/M_CO2
    for C_over_W in (0.6, 1.0):          # idea's own cushion/working assumption
        for f in (0.3, 0.5):             # swap fraction
            for x in (0.005, 0.01, 0.025):
                frac = x*(1/C_over_W)/(f*Rmol)
                left30 = (1-frac)**30
                rows.append((mass_ratio,C_over_W,f,x,frac,1-left30))
for r in rows:
    print("ratio %.1f C/W %.1f swap %.1f xCO2 %.3f -> lost %.1f%%/yr, %.0f%% lost over 30 cycles"%(r[0],r[1],r[2],r[3],100*r[4],100*r[5]))
fr=[r[4] for r in rows]; print("range %.2f-%.1f %%/yr"%(100*min(fr),100*max(fr)))
# Example absolute: 1 bcm(st) working gas withdrawn per year
mol = 1e9/0.023645  # m3 at 15C,1 atm
for x in (0.005,0.01,0.025):
    print("1 bcm/yr at x=%.3f -> %.1f kt CO2/yr back-produced"%(x, mol*x*M_CO2/1e9))
# Amine removal at withdrawal: separation floor for 2.5% stream, via verifier
import sys; sys.path.insert(0,'climate')
import physics
print([n for n in dir(physics) if not n.startswith('_')][:40])
