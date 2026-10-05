"""Exact reference solutions used to validate the numerical solvers (and as fast verifiers in their own right).

Conventions: time dependence exp(-i w t), outgoing Hankel H^(1), free-space wavenumber k = 2*pi/lambda,
relative index m (complex allowed, Im m > 0 = loss). 2D quantities are per unit length.
"""
import numpy as np
from scipy.special import jv, jvp, hankel1, h1vp


def cylinder_tm_coeffs(m, x, nmax=None):
    """Scattering coefficients b_n (n = -N..N) for an infinite dielectric cylinder, TM (E along the axis).

    Incident  E_z = sum_n i^n J_n(kr) e^{in phi};  scattered E_z = sum_n i^n b_n H_n(kr) e^{in phi}.
    """
    N = nmax or int(np.ceil(abs(x) + 4 * abs(x) ** (1 / 3) + 10))
    n = np.arange(-N, N + 1)
    num = m * jvp(n, m * x) * jv(n, x) - jv(n, m * x) * jvp(n, x)
    den = jv(n, m * x) * h1vp(n, x) - m * jvp(n, m * x) * hankel1(n, x)
    return n, num / den


def cylinder_tm_widths(m, radius, wavelength):
    """Scattering and extinction widths (same length unit as radius), TM polarization."""
    k = 2 * np.pi / wavelength
    _, b = cylinder_tm_coeffs(m, k * radius)
    return 4 / k * np.sum(np.abs(b) ** 2), -4 / k * np.sum(b.real)


def cylinder_tm_field(m, radius, wavelength, r, phi):
    """Scattered E_z at points outside the cylinder (r > radius), incident amplitude 1 along +x."""
    k = 2 * np.pi / wavelength
    n, b = cylinder_tm_coeffs(m, k * radius)
    r, phi = np.broadcast_arrays(np.asarray(r, float), np.asarray(phi, float))
    terms = (1j ** n)[:, None] * b[:, None] * hankel1(n[:, None], k * r.ravel()[None]) * np.exp(1j * n[:, None] * phi.ravel()[None])
    return terms.sum(0).reshape(r.shape)
