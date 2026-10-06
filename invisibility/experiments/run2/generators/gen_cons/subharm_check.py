# Test: for each phi, int_0^inf (dsigma/dphi)(phi,k) [P_z(k)+P_z(-k)] dk >= (2/(pi|z|)) |T(phi,z)|^2 exp(-4 b sin(|phi|/2) Im z)
import numpy as np, sys, json
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
import fastcyl
kc, B = np.pi/2, 0.1
z = kc*(1 + 0.5j*B)
P = lambda k: (z.imag/np.pi)/((k - z.real)**2 + z.imag**2)

def T_multi(m, radii, ks, phis, N=None):
    L = len(m)
    mlk = np.repeat(np.asarray(m, complex)[:, None], len(ks), axis=1) if L else np.zeros((0, len(ks)))
    n, b = fastcyl.coeffs_pec_multi(mlk, radii, np.asarray(ks), N=N)   # b (2N+1, K)
    return np.einsum('nk,pn->pk', b, np.exp(1j*np.outer(phis, n)))

designs = {'bare': ([], [1.0])}
for nm, f in [('sector_opt', 'lossless_sector_B0.1_L8.json'), ('ext_opt_L16', 'de_ext_B0.0_L16.json')]:
    d = json.load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/' + f))
    designs[nm] = (np.sqrt(np.array(d['eps'], float)), list(d['radii']))
phis = np.array([np.pi, 3*np.pi/4, np.pi/2, np.pi/4, 0.0])
# k grid: log-dense near 0, dense near kc, up to Kmax; chunks to limit memory
Kmax = 12.0
kgrid = np.unique(np.r_[np.geomspace(1e-7, 0.5, 4000), np.linspace(0.5, 4, 14000), np.linspace(4, Kmax, 3000)])
for name, (m, radii) in designs.items():
    b = radii[-1]
    Tz = T_multi(m, radii, np.array([z]), phis, N=40)[:, 0]
    rhs_c = (2/(np.pi*abs(z)))*np.abs(Tz)**2*np.exp(-4*b*np.sin(np.abs(phis)/2)*z.imag)
    rhs_nocomp = (2/(np.pi*abs(z)))*np.abs(Tz)**2
    vals = []
    eps = np.asarray(m, float)**2
    for chunk in np.array_split(kgrid, 40):
        elk = np.repeat(eps[:, None], len(chunk), axis=1) if len(eps) else np.zeros((0, len(chunk)))
        n, bb = fastcyl.coeffs_pec_real_tm(elk, radii, chunk)
        Tc = np.einsum('nk,pn->pk', bb, np.exp(1j*np.outer(phis, n)))
        vals.append((2/(np.pi*chunk))[None, :]*np.abs(Tc)**2)
    ds = np.concatenate(vals, axis=1)
    w = P(kgrid) + P(-kgrid)
    lhs = np.trapezoid(ds*w[None, :], kgrid, axis=1) + ds[:, -1]*(z.imag/np.pi)/Kmax   # crude tail
    Tk = T_multi(m, radii, np.array([kc]), phis)[:, 0]
    print(name)
    for i, ph in enumerate(phis):
        print(f"  phi={ph:.3f}: Lorentz-avg dsig/dphi={lhs[i]:.5f}  bound(compensated)={rhs_c[i]:.5f}  ratio={rhs_c[i]/lhs[i]:.3f}  "
              f"uncompensated={rhs_nocomp[i]:.5f} ({'VIOLATES' if rhs_nocomp[i]>lhs[i] else 'ok'})  dsig/dphi(kc)={(2/(np.pi*kc))*abs(Tk[i])**2:.5f}")
