# Augmented Nevanlinna-Pick matrix for h(z) = z*chi(z) of a passive Lorentz medium with oscillator strength s:
#   M = [[s, conj(h)^T], [h, P]],  P_ij = (h_i - conj h_j)/(z_i - conj z_j)  must be PSD.
import json, numpy as np
rng = np.random.default_rng(0)
kc, B = np.pi/2, 0.1
zs = kc*(1 + B/2*np.array([-1, -0.5, 0, 0.5, 1])) + 1j*kc*B/2*np.array([0.2, 0.5, 1, 0.5, 0.2])
def M_of(h, s):
    P = (h[:, None] - h.conj()[None, :])/(zs[:, None] - zs.conj()[None, :])
    top = np.concatenate([[s], h.conj()])
    return np.vstack([top, np.hstack([h[:, None], P])])
mins = []
for _ in range(100000):
    J = rng.integers(1, 4); wp2 = rng.exponential(1, J); w0 = rng.uniform(0, 5, J); g = 10**rng.uniform(-3, 0.5, J)
    chi = sum(wp2[j]/(w0[j]**2 - zs**2 - 1j*g[j]*zs) for j in range(J))
    s = wp2.sum()*rng.uniform(1.0, 1.5)       # budget >= used strength
    M = M_of(zs*chi, s); M = (M + M.conj().T)/2
    mins.append(np.linalg.eigvalsh(M)[0]/np.linalg.norm(M))
mins = np.array(mins)
# acausal: constant real chi < 0 (eps = 0.5) with any finite s
acaus = [np.linalg.eigvalsh((lambda M: (M+M.conj().T)/2)(M_of(zs*(-0.5)*np.ones(5), s)))[0] for s in (0.1, 1, 10, 100)]
# non-dispersive eps >= 1 (chi = 5 constant): h = 5 z is Herglotz but not a finite-mass Cauchy transform (no f-sum): P >= 0 but border fails
nd = [np.linalg.eigvalsh((lambda M: (M+M.conj().T)/2)(M_of(zs*5.0*np.ones(5), s)))[0] for s in (0.1, 1, 10, 100)]
P_nd = (lambda h: (h[:, None]-h.conj()[None, :])/(zs[:, None]-zs.conj()[None, :]))(zs*5.0)
r = dict(n=len(mins), min_normalised_eig=float(mins.min()), frac_negative=float((mins < -1e-12).mean()),
         acausal_eps0p5_min_eig=[float(x) for x in acaus], constant_chi5_min_eig=[float(x) for x in nd],
         constant_chi5_P_min_eig=float(np.linalg.eigvalsh((P_nd+P_nd.conj().T)/2)[0]))
print(json.dumps(r, indent=1)); json.dump(r, open('pick_check.json', 'w'), indent=1)
