# Vectorised check of (A) 2D free-space f-sum rule and (B) PEC-difference ("waterbed") sum rule, TM, c=1.
import json, numpy as np
from scipy.special import jv, jvp, yv, yvp, hankel1, h1vp
def eps_lor(k, wp2, w0, g): return 1 + wp2/(w0**2 - k**2 - 1j*g*k)
def sig_ext_from_L(k, Lfun, R, N):
    n = np.arange(-N, N+1)[:, None]; kk = k[None, :]
    L = Lfun(n, kk)
    b = -(kk*jvp(n, kk*R) - L*jv(n, kk*R))/(kk*h1vp(n, kk*R) - L*hankel1(n, kk*R))
    mask = np.abs(n) <= (2*kk*R + 15)
    b = np.where(mask, b, 0)
    return -4/k*np.sum(b.real, axis=0)
def shell_L(a, b, m):  # log-derivative at r=b of the TM solution vanishing at r=a in a shell of index m(k)
    def L(n, kk):
        q = kk*m(kk)
        Z  = jv(n, q*b)*yv(n, q*a) - yv(n, q*b)*jv(n, q*a)
        Zp = jvp(n, q*b)*yv(n, q*a) - yvp(n, q*b)*jv(n, q*a)
        return q*Zp/Z
    return L
def bare(k, a, N):
    n = np.arange(-N, N+1)[:, None]; b = -jv(n, k[None,:]*a)/hankel1(n, k[None,:]*a)
    b = np.where(np.abs(n) <= 2*k[None,:]*a + 15, b, 0)
    return -4/k*np.sum(b.real, axis=0)
def grid(K):
    return np.unique(np.concatenate([np.logspace(-6, -1, 400), np.arange(0.1, K, 0.002)]))
def run_chunks(f, k, chunk=400):
    return np.concatenate([f(k[i:i+chunk]) for i in range(0, len(k), chunk)])
out = {}
# (A) free-space Lorentz cylinder
R, wp2, w0, g = 1.0, 1.0, 1.0, 0.2
for K in (20, 40):
    k = grid(K); N = int(2*K*R + 20)
    def fA(kc):
        m = lambda kk: np.sqrt(eps_lor(kk, wp2, w0, g))
        Lf = lambda n, kk: kk*m(kk)*jvp(n, kk*m(kk)*R)/jv(n, kk*m(kk)*R)
        return sig_ext_from_L(kc, Lf, R, N)
    s = run_chunks(fA, k)
    I = (2/np.pi)*np.trapezoid(s, k)
    out[f'A_K{K}'] = dict(integral=I, tail_sigma_at_K=float(s[-1]))
    print('A K', K, I, 'pred', wp2*np.pi*R**2, 'sigma(K)', s[-1], flush=True)
# (B) PEC core + Lorentz shell
a = 1.0
for (b, wp2, w0, g) in [(1.5, 1.0, 1.0, 0.2), (2.0, 0.5, 2.0, 0.3), (3.0, 0.3, 0.5, 0.1)]:
    gint = np.trapezoid((1 - 2/np.pi*np.arcsin(a/np.linspace(a, b, 4001)))*2*np.pi*np.linspace(a, b, 4001), np.linspace(a, b, 4001))
    rec = {}
    for K in (20, 40):
        k = grid(K); N = int(2*K*b + 20)
        m = lambda kk: np.sqrt(eps_lor(kk, wp2, w0, g))
        fd = lambda kc: sig_ext_from_L(kc, shell_L(a, b, m), b, N) - bare(kc, a, N)
        d = run_chunks(fd, k)
        I = (2/np.pi)*np.trapezoid(d, k)
        rec[K] = dict(integral=float(I), diff_at_K=float(d[-1]), K2diff=float(d[-1]*K**2))
        print(f'B b={b} wp2={wp2} w0={w0} g={g} K={K}: (2/pi)int = {I:.5f}; diff(K)={d[-1]:.3e}', flush=True)
    out[f'B_b{b}_wp2{wp2}_w0{w0}'] = dict(res=rec, pred_shadow=float(wp2*gint), pred_full=float(wp2*np.pi*(b*b-a*a)))
    print('   pred shadow', wp2*gint, ' pred full', wp2*np.pi*(b*b-a*a), flush=True)
json.dump(out, open('sumrule_fast.json', 'w'), indent=1)
