"""CO2 solubility in NaCl brine: Spycher, Pfeiffer & Apps (2003) CO2-H2O model (12-100 C, to 600 bar)
plus Duan & Sun (2003) salting-out activity coefficient. Approximate; for screening only.
CO2 density from CoolProp (Span-Wagner) when available."""
import math, sys
sys.path.append('climate/runs/2026-10-05/scripts/pylib')
try:
    import CoolProp.CoolProp as CP
except Exception:
    CP = None

R = 83.1447  # bar cm3 /(mol K)


def _rk_volume(T, P, a, b):
    # P = RT/(V-b) - a/(T^0.5 V (V+b))  -> cubic in V
    c2 = -R * T / P
    c1 = -(R * T * b / P - a / (P * T ** 0.5) + b * b)
    c0 = -a * b / (P * T ** 0.5)
    import numpy as np
    roots = np.roots([1.0, c2, c1, c0])
    real = sorted(r.real for r in roots if abs(r.imag) < 1e-6 and r.real > b)
    return real


def solubility_pure_water(T_C, P_bar):
    """mol CO2 / kg H2O in pure water (SPA 2003). Liquid-CO2 constants below 31 C if P above saturation."""
    T = T_C + 273.15
    a_co2 = 7.54e7 - 4.13e4 * T
    b_co2, b_h2o, a_h2o_co2 = 27.80, 18.18, 7.89e7
    roots = _rk_volume(T, P_bar, a_co2, b_co2)
    liquid = T_C < 31.0 and len(roots) >= 1 and P_bar > 60  # crude
    V = min(roots) if liquid else max(roots)
    am, bm = a_co2, b_co2
    lnV = math.log(V / (V - bm))
    t15 = R * T ** 1.5
    common = am * bm / (t15 * bm * bm) * (math.log((V + bm) / V) - bm / (V + bm))
    z = P_bar * V / (R * T)
    ln_phi_co2 = lnV + b_co2 / (V - bm) - 2 * am / (t15 * bm) * math.log((V + bm) / V) + b_co2 / bm * common - math.log(z)
    ln_phi_h2o = lnV + b_h2o / (V - bm) - 2 * a_h2o_co2 / (t15 * bm) * math.log((V + bm) / V) + b_h2o / bm * common - math.log(z)
    phi_co2, phi_h2o = math.exp(ln_phi_co2), math.exp(ln_phi_h2o)
    t = T_C
    logK_h2o = -2.209 + 3.097e-2 * t - 1.098e-4 * t ** 2 + 2.048e-7 * t ** 3
    if liquid:
        logK_co2 = 1.169 + 1.368e-2 * t - 5.380e-5 * t ** 2
    else:
        logK_co2 = 1.189 + 1.304e-2 * t - 5.446e-5 * t ** 2
    K_h2o, K_co2 = 10 ** logK_h2o, 10 ** logK_co2
    Vh2o, Vco2 = 18.1, 32.6
    A = K_h2o / (phi_h2o * P_bar) * math.exp((P_bar - 1) * Vh2o / (R * T))
    B = phi_co2 * P_bar / (55.508 * K_co2) * math.exp(-(P_bar - 1) * Vco2 / (R * T))
    y_h2o = (1 - B) / (1 / A - B)
    x_co2 = B * (1 - y_h2o)
    return 55.508 * x_co2 / (1 - x_co2)


def _par(c, T, P):
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11 = c
    return (c1 + c2 * T + c3 / T + c4 * T * T + c5 / (630 - T) + c6 * P + c7 * P * math.log(T)
            + c8 * P / T + c9 * P / (630 - T) + c10 * P * P / (630 - T) ** 2 + c11 * T * math.log(P))


LAM = (-0.411370585, 6.07632013e-4, 97.5347708, 0, 0, 0, 0, -0.0237622469, 0.0170656236, 0, 1.41335834e-5)
ZETA = (3.36389723e-4, -1.98298980e-5, 0, 0, 0, 0, 0, 2.12220830e-3, -5.24873303e-3, 0, 0)


def solubility_brine(T_C, P_bar, m_nacl):
    """mol CO2 / kg H2O in NaCl brine of molality m_nacl (Duan & Sun 2003 activity correction)."""
    T = T_C + 273.15
    lam, zeta = _par(LAM, T, P_bar), _par(ZETA, T, P_bar)
    ln_gamma = 2 * lam * m_nacl + zeta * m_nacl * m_nacl
    return solubility_pure_water(T_C, P_bar) / math.exp(ln_gamma)


def tds_to_molality(tds_g_per_l, brine_density=1.09):
    """Treat all TDS as NaCl (crude). g/L -> mol/kg H2O."""
    salt_kg = tds_g_per_l / 1000.0
    water_kg = brine_density - salt_kg
    return (tds_g_per_l / 58.44) / water_kg


def kg_co2_per_m3_brine(T_C, P_bar, tds, brine_density=1.09):
    m = solubility_brine(T_C, P_bar, tds_to_molality(tds, brine_density))
    water_kg = brine_density * 1000 - tds  # kg water per m3 brine
    return m * 0.04401 * water_kg


def co2_density(T_C, P_bar):
    if CP is None:
        raise RuntimeError('CoolProp unavailable')
    return CP.PropsSI('D', 'T', T_C + 273.15, 'P', P_bar * 1e5, 'CO2')


if __name__ == '__main__':
    print('Validation (pure water): literature ~1.09 mol/kg at 50 C 100 bar (Bamberger 2000 x=0.0193);')
    for T, P in [(25, 50), (25, 100), (50, 100), (50, 200), (75, 150), (100, 300)]:
        print(f'  {T:>3} C {P:>4} bar: pure {solubility_pure_water(T, P):.3f}  1m {solubility_brine(T, P, 1):.3f}  '
              f'2m {solubility_brine(T, P, 2):.3f}  4m {solubility_brine(T, P, 4):.3f} mol/kg')
