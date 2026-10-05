"""Physics verifier for climate ideas: thermodynamic floors and scale arithmetic.

Every idea the engine proposes must pass through these calculators. They are
deterministic, so an idea's energy and scale claims are checked by arithmetic, not
by an LLM's opinion. Global reference values are approximate and labelled; override
them when a better source is available.

    python climate/physics.py          # prints the reference table
    python -m pytest climate/test_physics.py
"""
from __future__ import annotations

import math
from dataclasses import dataclass

R = 8.314462618          # J/(mol K)
T0 = 298.15              # K
P0 = 101_325.0           # Pa
M_CO2 = 0.04401          # kg/mol
M_CH4 = 0.01604          # kg/mol
M_N2O = 0.04401          # kg/mol

# Approximate global reference values (verify before quoting; sources in comments).
WORLD_PRIMARY_ENERGY_EJ = 620.0      # ~2023-24, Energy Institute Statistical Review (order of magnitude)
WORLD_ELECTRICITY_TWH = 30_000.0     # ~2024, Ember / IEA
FOSSIL_CO2_GT = 37.4                 # fossil CO2, 2024, Global Carbon Budget
TOTAL_GHG_GT_CO2E = 53.0             # all GHGs incl. LULUCF, ~2023, UNEP Emissions Gap
GWP100 = {"CO2": 1.0, "CH4_fossil": 29.8, "CH4_biogenic": 27.0, "N2O": 273.0}   # IPCC AR6
GWP20 = {"CO2": 1.0, "CH4_fossil": 82.5, "CH4_biogenic": 79.7, "N2O": 273.0}    # IPCC AR6


def _g(y: float) -> float:
    """Dimensionless molar Gibbs energy of mixing for a binary ideal gas, y ln y + (1-y) ln(1-y)."""
    if y <= 0.0 or y >= 1.0:
        return 0.0
    return y * math.log(y) + (1 - y) * math.log(1 - y)


def min_separation_work(x_feed: float, capture_fraction: float = 0.9, purity: float = 0.99,
                        T: float = T0) -> float:
    """Minimum (reversible) work to separate a target gas, J per mol of target captured.

    Feed: 1 mol of ideal binary gas with target mole fraction x_feed. A fraction
    `capture_fraction` of the target leaves in a product stream of mole fraction `purity`;
    the rest leaves in the lean stream. Work = increase in Gibbs energy of the streams.
    """
    if not (0 < x_feed < 1 and 0 < capture_fraction <= 1 and x_feed < purity <= 1):
        raise ValueError("need 0 < x_feed < purity <= 1 and 0 < capture_fraction <= 1")
    captured = capture_fraction * x_feed
    n_prod = captured / purity
    n_lean = 1.0 - n_prod
    y_lean = (x_feed - captured) / n_lean if n_lean > 0 else 0.0
    dg = n_prod * _g(purity) + n_lean * _g(y_lean) - _g(x_feed)
    return R * T * dg / captured


def gj_per_tonne(j_per_mol: float, molar_mass: float = M_CO2) -> float:
    """Convert J/mol of a species to GJ per tonne of that species."""
    return j_per_mol / molar_mass / 1e6  # J/mol / (kg/mol) = J/kg; 1 J/kg = 1e-6 GJ/t


def air_volume_per_tonne(x_feed: float, capture_fraction: float, molar_mass: float = M_CO2,
                         T: float = T0, P: float = P0) -> float:
    """m^3 of gas that must be processed to capture 1 tonne of the target species."""
    mol_per_m3 = P / (R * T) * x_feed
    return 1e6 / (mol_per_m3 * molar_mass * 1e3 * capture_fraction)


def fan_work_gj_per_tonne(x_feed: float, capture_fraction: float, pressure_drop_pa: float,
                          fan_efficiency: float = 0.6, molar_mass: float = M_CO2) -> float:
    """Electrical work to push the required gas volume through a contactor, GJ per tonne captured."""
    v = air_volume_per_tonne(x_feed, capture_fraction, molar_mass)
    return v * pressure_drop_pa / fan_efficiency / 1e9


@dataclass
class ScaleCheck:
    gt_per_year: float
    gj_per_tonne: float

    @property
    def ej_per_year(self) -> float:
        return self.gt_per_year * 1e9 * self.gj_per_tonne / 1e9

    @property
    def share_of_world_primary_energy(self) -> float:
        return self.ej_per_year / WORLD_PRIMARY_ENERGY_EJ

    @property
    def share_of_world_electricity_if_electric(self) -> float:
        twh = self.ej_per_year * 1e18 / 3.6e15
        return twh / WORLD_ELECTRICITY_TWH


def second_law_efficiency(actual_gj_per_tonne: float, minimum_gj_per_tonne: float) -> float:
    return minimum_gj_per_tonne / actual_gj_per_tonne


def energy_cost_floor(gj_per_tonne_value: float, usd_per_mwh: float) -> float:
    """$/t if all energy were bought as electricity at usd_per_mwh (a floor on energy cost only)."""
    return gj_per_tonne_value / 3.6 * usd_per_mwh


def reference_table() -> list[tuple[str, float, float]]:
    """(case, J/mol, GJ/t) for the standard capture cases."""
    cases = [
        ("Air, 420 ppm CO2, 75% capture, 99% pure", 420e-6, 0.75, 0.99),
        ("Air, 420 ppm CO2, 10% capture, 99% pure", 420e-6, 0.10, 0.99),
        ("Gas-turbine flue, 4% CO2, 90% capture", 0.04, 0.90, 0.99),
        ("Coal flue, 12% CO2, 90% capture", 0.12, 0.90, 0.99),
        ("Cement kiln flue, 25% CO2, 90% capture", 0.25, 0.90, 0.99),
        ("Ethanol fermentation, ~99% CO2 (drying only)", 0.98, 0.90, 0.999),
    ]
    return [(name, w := min_separation_work(x, f, p), gj_per_tonne(w)) for name, x, f, p in cases]


if __name__ == "__main__":
    print(f"{'Case':<48}{'kJ/mol':>9}{'GJ/t CO2':>10}{'kWh/t':>8}")
    for name, w, gj in reference_table():
        print(f"{name:<48}{w/1e3:>9.2f}{gj:>10.3f}{gj/0.0036:>8.0f}")
    print()
    for label, gj in [("thermodynamic minimum (air)", gj_per_tonne(min_separation_work(420e-6, 0.75))),
                      ("good real DAC, ~6 GJ/t", 6.0), ("typical real DAC, ~10 GJ/t", 10.0)]:
        s = ScaleCheck(FOSSIL_CO2_GT, gj)
        print(f"All fossil CO2 ({FOSSIL_CO2_GT} Gt) by DAC at {label}: {s.ej_per_year:,.0f} EJ/yr = "
              f"{s.share_of_world_primary_energy:.1%} of world primary energy")
    print()
    fan = fan_work_gj_per_tonne(420e-6, 0.75, 100)
    print(f"Fan work to process air for CO2 (75% capture, 100 Pa, 60% fan): {fan:.2f} GJ/t "
          f"(air volume {air_volume_per_tonne(420e-6, 0.75):,.0f} m3/t)")
    ch4 = fan_work_gj_per_tonne(1.93e-6, 0.5, 100, molar_mass=M_CH4)
    print(f"Fan work to process air for methane (1.93 ppm, 50% removal, 100 Pa): {ch4:,.0f} GJ/t CH4 = "
          f"{ch4/GWP100['CH4_fossil']:.2f} GJ/t CO2e (GWP100), {ch4/GWP20['CH4_fossil']:.2f} GJ/t CO2e (GWP20)")
