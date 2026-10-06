# Minimal int|S| dA over divergence-free S in the annulus a<r<b with plane-wave normal flux cos(theta) on r=b and S.n=0 on r=a
# = W1 transport (geodesic metric around the disk r<a) from inflow (left) to outflow (right). Compare with the vacuum disk value pi b^2.
import numpy as np
from scipy.optimize import linprog
def geod(p, q, a):
    d = q - p; L = np.linalg.norm(d)
    t = np.clip(-(p @ d)/(L*L), 0, 1); 
    if np.linalg.norm(p + t*d) >= a: return L
    lp, lq = np.sqrt(p @ p - a*a), np.sqrt(q @ q - a*a)
    ang = np.arccos(np.clip(p @ q/np.linalg.norm(p)/np.linalg.norm(q), -1, 1)) - np.arccos(a/np.linalg.norm(p)) - np.arccos(a/np.linalg.norm(q))
    return lp + lq + a*ang
def W1(a, b, n=120):
    th = (np.arange(n) + 0.5)*np.pi/n - np.pi/2           # right half: theta in (-pi/2, pi/2)
    wq = np.cos(th)*b*np.pi/n                            # outflow mass per node (flux density cos th times arc length)
    R = np.stack([b*np.cos(th), b*np.sin(th)], 1); Lp = R*np.array([-1, 1])
    C = np.array([[geod(p, q, a) for q in R] for p in Lp])
    nn = n*n; A = []; rhs = []
    for i in range(n):
        row = np.zeros(nn); row[i*n:(i+1)*n] = 1; A.append(row); rhs.append(wq[i])
    for j in range(n):
        row = np.zeros(nn); row[j::n] = 1; A.append(row); rhs.append(wq[j])
    res = linprog(C.ravel(), A_eq=np.array(A), b_eq=np.array(rhs), bounds=(0, None), method='highs')
    mirror = sum(wq[i]*C[i, i] for i in range(n))
    return res.fun, mirror
for a, b in [(1, 3), (1, 2), (1, 1.5), (1e-6, 3)]:
    w, mirr = W1(a, b, n=100)
    print(f"a={a} b={b}: W1(annulus)={w:.4f}  mirror plan={mirr:.4f}  vacuum disk pi b^2={np.pi*b*b:.4f}  excess/(pi b^2)={(w - np.pi*b*b)/(np.pi*b*b):.4f}  excess={w-np.pi*b*b:.4f} (a^2 units)")
