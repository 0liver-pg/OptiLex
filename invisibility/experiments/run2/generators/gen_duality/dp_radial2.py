"""Faster DP variant: cubic periodic interpolation, fewer radial steps, intermediate eps levels (emulate chattering).
Non-rigorous estimate only (strategy scoping)."""
import sys, time, numpy as np
from scipy.ndimage import map_coordinates, spline_filter
from dp_radial import run as _unused
from scipy.special import jv, yv, jvp, yvp

def run(chans, M, nsteps, eps_max=6.0, k=np.pi/2, a=1.0, b=3.0, levels=(1.0, 6.0), order=3):
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
    f = lambda r, th, n, e: np.cos(th)**2 / r + (k*k*e*r - n*n/r) * np.sin(th)**2
    flows = {}
    for i in range(nsteps, 0, -1):
        r1, r0 = rs[i], rs[i - 1]; h = r1 - r0
        Vf = spline_filter(V, order=order, mode='grid-wrap') if order > 1 else V
        best = None
        for e in levels:
            coords = []
            for n, g in zip(chans, grids):
                t = g
                sub = 4
                hh = h / sub; rr = r0
                for _ in range(sub):
                    k1 = f(rr, t, n, e); k2 = f(rr + hh/2, t + hh/2*k1, n, e)
                    k3 = f(rr + hh/2, t + hh/2*k2, n, e); k4 = f(rr + hh, t + hh*k3, n, e)
                    t = t + hh/6*(k1 + 2*k2 + 2*k3 + k4); rr += hh
                coords.append((t % np.pi) * M / np.pi)
            Vi = map_coordinates(Vf, coords, order=order, mode='grid-wrap', prefilter=False)
            best = Vi if best is None else np.minimum(best, Vi)
        V = best
    return V.flat[0]

if __name__ == '__main__':
    lv = (1.0, 2.25, 3.5, 4.75, 6.0)
    for chans, M, ns in [((0, 1), 128, 100), ((0, 1), 256, 200), ((0, 1), 256, 100), ((0, 1, 2), 48, 100), ((0, 1, 2), 64, 100)]:
        t0 = time.time()
        v = run(chans, M, ns, levels=lv)
        print(chans, M, ns, 'V(a,0)=%.4f' % v, 'R=%.4f' % (v / 5.4338), '%.1fs' % (time.time() - t0), flush=True)
