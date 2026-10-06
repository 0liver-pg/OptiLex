"""Quick (non-rigorous) HJB/DP estimate of the radial multi-channel floor:
min over eps(r) in [1, eps_max] of sum_{n in chans} sigma_n(k_c), B = 0, via Prufer phases on the torus [0,pi)^d.
Semi-Lagrangian backward DP; controls = a few eps levels (endpoints suffice for HJB; levels help at finite step)."""
import sys, time, numpy as np
from scipy.ndimage import map_coordinates
from scipy.special import jv, yv, jvp, yvp

def run(chans, M, nsteps, eps_max=6.0, k=np.pi/2, a=1.0, b=3.0, levels=None):
    d = len(chans)
    th1 = np.arange(M) * np.pi / M
    grids = np.meshgrid(*([th1] * d), indexing='ij')
    def sig(n, th):
        x = k * b
        N = jv(n, x) * np.cos(th) - x * jvp(n, x) * np.sin(th)
        D = yv(n, x) * np.cos(th) - x * yvp(n, x) * np.sin(th)
        return (4 / k) * N**2 / (N**2 + D**2) * (1 if n == 0 else 2)
    V = sum(sig(n, g) for n, g in zip(chans, grids))
    rs = np.linspace(a, b, nsteps + 1)
    levels = levels or [1.0, eps_max]
    def f(r, th, n, e):
        return np.cos(th)**2 / r + (k*k*e*r - n*n/r) * np.sin(th)**2
    for i in range(nsteps, 0, -1):
        r1, r0 = rs[i], rs[i - 1]; h = r1 - r0
        best = None
        for e in levels:
            coords = []
            for n, g in zip(chans, grids):
                # RK4 forward from r0 to r1 (point lands at theta(r1))
                t = g
                k1 = f(r0, t, n, e); k2 = f(r0 + h/2, t + h/2*k1, n, e)
                k3 = f(r0 + h/2, t + h/2*k2, n, e); k4 = f(r1, t + h*k3, n, e)
                t = t + h/6*(k1 + 2*k2 + 2*k3 + k4)
                coords.append((t % np.pi) * M / np.pi)
            Vi = map_coordinates(V, coords, order=1, mode='grid-wrap')
            best = Vi if best is None else np.minimum(best, Vi)
        V = best
    return V.flat[0]  # theta = 0 for all channels at r = a

if __name__ == '__main__':
    bare = {0: 1.4514, 1: 3.5927, 2: 0.3824}
    for chans, M, ns in [((0, 1), 256, 400), ((0, 1), 512, 800), ((0, 1, 2), 64, 400), ((0, 1, 2), 96, 600)]:
        t0 = time.time()
        v = run(chans, M, ns)
        print(chans, M, ns, 'V(a,0)=%.4f' % v, 'R(over total bare 5.434)=%.4f' % (v / 5.4338), '%.1fs' % (time.time() - t0), flush=True)
