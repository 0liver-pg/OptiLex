import numpy as np
rng=np.random.default_rng(1)
# Bottom-up (sum of fenceline plant estimates) vs top-down (14.0 +/- 0.9 Gg, CEE 2024) reconciliation
true_total=14.0
for n in (25,35,60):
  for missing in (0.0,1.0,2.0,3.0):
    covered=true_total-missing
    w=rng.dirichlet(np.ones(n)*0.7,size=20000)*covered
    # per-plant multiplicative error, 5-95% [0.51,1.98] -> lognormal sigma ~0.42 (500 m ring case)
    est=(w*rng.lognormal(0,0.42,size=w.shape)).sum(1)
    td=rng.normal(true_total,0.9,size=20000)
    gap=td-est
    flag=(gap>1.645*np.sqrt(0.9**2+np.var(est))).mean()
    print(f"n={n} missing={missing:.0f} Gg  bottom-up sd={est.std():.2f} Gg  P(flag missing source)={flag:.2f}")
