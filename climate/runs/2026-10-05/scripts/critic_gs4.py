# Critic check: society-level bulk-milk signal vs confounders
effects=[0.15,0.175,0.20]          # per-kg-milk CH4 cut in enrolled animals (Garg 2013)
for enrol in [0.3,0.6,1.0]:
    for milk_gain in [0.02,0.14]:
        for e in effects:
            # milk-weighted share of enrolled milk in the pool
            w=enrol*(1+milk_gain)/(enrol*(1+milk_gain)+(1-enrol))
            sig=w*e
            print(f"enrol={enrol:.0%} gain={milk_gain:.0%} eff={e:.1%} -> pooled intensity signal {sig:.1%}")
# Species mix: buffalo vs cow milk-fat ~7% vs ~4%; CH4 intensity differs by species.
# If predicted intensity differs by X% between species, a shift d in buffalo milk share moves pooled value by d*X.
for X in [0.2,0.4]:
    for d in [0.05,0.10,0.20]:
        print(f"species gap {X:.0%}, buffalo-share swing {d:.0%} -> pooled shift {X*d:.1%}")
