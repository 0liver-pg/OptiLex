# Non-rigorous estimate of the joint-channel floor min_eps sum_{n in S} sigma_n(k_c) over measurable eps(r) in [emin, emax],
# via semi-Lagrangian DP of the value function on the Prufer-angle torus (period pi per channel).
import numpy as np, sys, time
from scipy.ndimage import map_coordinates
from scipy.special import jv, jvp, hankel1, h1vp
k = np.pi/2; a, b = 1.0, 3.0
def sig_n(th, n):
    x = k*b
    num = x*jvp(n, x)*np.sin(th) - jv(n, x)*np.cos(th)
    den = x*h1vp(n, x)*np.sin(th) - hankel1(n, x)*np.cos(th)
    return (4/k)*(1 if n == 0 else 2)*np.abs(num/den)**2
def run(chans, G, nsteps, emin=1.0, emax=6.0):
    d = len(chans)
    th1 = np.arange(G)*np.pi/G
    grids = np.meshgrid(*([th1]*d), indexing='ij')
    V = sum(sig_n(grids[i], n) for i, n in enumerate(chans))
    rs = np.linspace(a, b, nsteps + 1)
    for j in range(nsteps, 0, -1):
        r0, r1 = rs[j-1], rs[j]; h = r1 - r0; rm = 0.5*(r0 + r1)
        best = None
        for e in (emin, emax):
            # midpoint (RK2) step forward from r0 to r1 for each channel
            coords = []
            for i, n in enumerate(chans):
                th = grids[i]
                f = lambda r, t: np.cos(t)**2/r + (k**2*e*r - n**2/r)*np.sin(t)**2
                tm = th + 0.5*h*f(r0, th)
                tn = th + h*f(rm, tm)
                coords.append(tn/(np.pi/G))
            Vn = map_coordinates(V, coords, order=1, mode='grid-wrap')
            best = Vn if best is None else np.minimum(best, Vn)
        V = best
    return V[(0,)*d]
bare = 5.43350338479252
for chans in ([0, 1], [0, 1, 2]):
    for G, ns in ([(128, 200), (256, 400)] if len(chans) == 2 else [(64, 200), (96, 300)]):
        t0 = time.time()
        v = run(chans, G, ns)
        print(f"channels {chans} G={G} steps={ns}: DP floor = {v:.4f} a  (R = {v/bare:.3f})  [{time.time()-t0:.1f}s]", flush=True)
# falsification sanity: acausal range eps in [-10, 10] must drive the floor to ~0
v = run([0, 1], 256, 400, emin=-10, emax=10)
print(f"acausal eps in [-10,10], channels [0,1]: DP floor = {v:.4f}")
