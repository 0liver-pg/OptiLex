"""Shared helpers for the systems-integration idea checks. Imports the OptiLex verifier."""
import math, sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

def iso_comp_gj_t(p_in_bar, p_out_bar, T=T0, M=M_CO2):
    """Ideal isothermal compression work, GJ/t of gas (lower bound)."""
    return R * T * math.log(p_out_bar / p_in_bar) / M / 1e6

def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)

def pr_fugacity_coeff_co2(T, P_pa):
    """Peng-Robinson fugacity coefficient of pure CO2 (vapour/supercritical root)."""
    Tc, Pc, w = 304.13, 7.3773e6, 0.2239
    k = 0.37464 + 1.54226 * w - 0.26992 * w * w
    a = 0.45724 * R**2 * Tc**2 / Pc * (1 + k * (1 - math.sqrt(T / Tc)))**2
    b = 0.07780 * R * Tc / Pc
    A = a * P_pa / (R * T)**2
    B = b * P_pa / (R * T)
    # cubic: Z^3 - (1-B)Z^2 + (A-3B^2-2B)Z - (AB-B^2-B^3) = 0
    import numpy as np
    roots = np.roots([1, -(1 - B), A - 3 * B * B - 2 * B, -(A * B - B * B - B**3)])
    Zs = [r.real for r in roots if abs(r.imag) < 1e-9 and r.real > B]
    Z = max(Zs) if T > Tc else min(Zs) if P_pa > 6e6 and T < Tc else max(Zs)
    lnphi = Z - 1 - math.log(Z - B) - A / (2 * math.sqrt(2) * B) * math.log(
        (Z + (1 + math.sqrt(2)) * B) / (Z + (1 - math.sqrt(2)) * B))
    return math.exp(lnphi)

def co2_solubility_mol_kg(T, P_pa, m_salt, ks=0.09, vbar=3.3e-5):
    """Approximate CO2 solubility (mol/kg water) in NaCl-type brine at saturation with pure CO2.
    Henry (Sander: 0.034 mol/kg/atm at 298 K, van 't Hoff 2400 K) x PR fugacity x Poynting x Sechenov.
    Accuracy ~ +/-25%; ks (log10 basis, per mol/kg) spans ~0.065-0.11 in the literature."""
    kh = 0.034 * math.exp(2400 * (1 / T - 1 / 298.15))  # mol/kg/atm
    f_atm = pr_fugacity_coeff_co2(T, P_pa) * P_pa / 101325
    poynting = math.exp(-vbar * (P_pa - 101325) / (R * T))
    return kh * f_atm * poynting * 10 ** (-ks * m_salt)
