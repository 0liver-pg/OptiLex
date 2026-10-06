"""Check Paley-Wiener growth of the sector far-field amplitude T(phi,z) in the upper half plane:
|e^{i z c_phi} T(phi, z)| should grow at most polynomially for c_phi = 2R|sin(phi/2)| (R = outer radius)."""
import sys, json, numpy as np
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d
d = json.load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/de_ext_B0.0_L16.json'))
designs = {'bare(R=1)': ([], [1.0], 1.0), 'L16(R=3)': (list(np.sqrt(d['eps'])), d['radii'], 3.0)}
kc = np.pi / 2
for name, (m, radii, R) in designs.items():
    print(name)
    for phi in [np.pi, 3*np.pi/4, np.pi/2]:
        c = 2 * R * abs(np.sin(phi / 2))
        row = []
        for y in [0.0, 1.0, 2.0, 4.0, 6.0]:
            z = kc + 1j * y
            n, b = cloak2d.coeffs(m, radii, z, core='pec', nmax=60)
            T = np.sum(b * np.exp(1j * n * phi))
            row.append((y, abs(T), abs(np.exp(1j * z * c) * T)))
        print('  phi=%.3f c=%.2f ' % (phi, c) + '  '.join('y=%g |T|=%.3g |e^{izc}T|=%.3g' % r for r in row))
