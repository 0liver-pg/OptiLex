"""Sorbent verifier for direct air capture (DAC) ideas: screening-level cycle thermodynamics.

Why a sorbent that binds CO2 at 420 ppm is expensive to regenerate, in numbers. The model is a
single-site Langmuir isotherm with temperature-dependent affinity, run through an idealised
temperature-vacuum swing. It is a screening tool: real sorbents have heterogeneous sites,
kinetics, humidity effects and heat losses, all of which make things worse, so results here
are optimistic bounds for a given set of material parameters.

    python climate/sorbent.py                  # reference case and the binding/regeneration trade-off
    python -m pytest climate/test_sorbent.py   # run from the climate/ directory
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from physics import (M_CO2, P0, R, T0, fan_work_gj_per_tonne, gj_per_tonne,
                     min_separation_work)

P_REF = 1.0e5            # Pa, standard-state pressure for dG = dH - T dS
X_AIR = 420e-6           # CO2 mole fraction in air
P_CO2_AIR = X_AIR * P0   # Pa
FARADAY = 96_485.332     # C/mol
DH_VAP_WATER = 44_000.0  # J/mol near ambient


def langmuir_b(dH: float, dS: float, T: float) -> float:
    """Langmuir affinity b(T) in 1/Pa for adsorption enthalpy dH (J/mol, negative) and entropy dS (J/mol/K)."""
    return math.exp(-(dH - T * dS) / (R * T)) / P_REF


def loading(p: float, T: float, dH: float, dS: float, q_max: float) -> float:
    """Equilibrium CO2 loading (same units as q_max) at CO2 partial pressure p (Pa) and temperature T (K)."""
    bp = langmuir_b(dH, dS, T) * p
    return q_max * bp / (1.0 + bp)


def dG_for_half_loading(p: float = P_CO2_AIR, T: float = T0) -> float:
    """Adsorption free energy (J/mol, negative) at which a Langmuir site is half-filled at pressure p."""
    return -R * T * math.log(P_REF / p)


def desorption_temperature(dH: float, dS: float, p_des: float, residual_fraction: float = 0.2) -> float:
    """Temperature (K) at which loading falls to residual_fraction of q_max under CO2 pressure p_des (Pa)."""
    L = math.log(P_REF / p_des * residual_fraction / (1.0 - residual_fraction))
    return -dH / (R * L - dS)


@dataclass
class TVSACycle:
    """Idealised temperature-vacuum swing cycle for a Langmuir sorbent. Energies are per mol CO2 captured."""
    dH: float                        # J/mol, negative
    dS: float                        # J/mol/K, negative
    q_max: float                     # mol CO2 per kg sorbent
    T_ads: float = T0
    T_des: float = 373.15
    p_ads: float = P_CO2_AIR
    p_des: float = 1.0e3             # CO2 partial pressure during desorption (vacuum and/or steam purge), Pa
    cp_sorbent: float = 1500.0       # J/kg/K, sorbent including its support
    inert_mass_ratio: float = 0.0    # kg of contactor structure heated per kg sorbent
    cp_inert: float = 900.0          # J/kg/K
    water_coads: float = 0.0         # mol H2O desorbed per mol CO2
    heat_recovery: float = 0.0       # fraction of sensible heat recovered between beds
    vacuum_efficiency: float = 0.7
    fan_gj_per_t: float | None = None  # defaults to 100 Pa contactor, 75% capture, 60% fan

    @property
    def q_ads(self) -> float:
        return loading(self.p_ads, self.T_ads, self.dH, self.dS, self.q_max)

    @property
    def q_des(self) -> float:
        return loading(self.p_des, self.T_des, self.dH, self.dS, self.q_max)

    @property
    def working_capacity(self) -> float:
        """mol CO2 per kg sorbent per cycle (zero if the swing does not release anything)."""
        return max(0.0, self.q_ads - self.q_des)

    def _require_capacity(self) -> float:
        wc = self.working_capacity
        if wc <= 0.0:
            raise ValueError("cycle has no working capacity: desorption conditions do not unload the sorbent")
        return wc

    @property
    def reaction_heat(self) -> float:
        return -self.dH

    @property
    def sensible_heat(self) -> float:
        wc = self._require_capacity()
        c = self.cp_sorbent + self.inert_mass_ratio * self.cp_inert
        return c * (self.T_des - self.T_ads) * (1.0 - self.heat_recovery) / wc

    @property
    def water_heat(self) -> float:
        return self.water_coads * DH_VAP_WATER

    @property
    def heat(self) -> float:
        """Regeneration heat, J per mol CO2."""
        return self.reaction_heat + self.sensible_heat + self.water_heat

    @property
    def heat_gj_per_t(self) -> float:
        return gj_per_tonne(self.heat)

    @property
    def vacuum_work(self) -> float:
        """Work to bring the product from p_des to 1 atm (isothermal ideal gas / efficiency), J/mol."""
        if self.p_des >= P0:
            return 0.0
        return R * self.T_ads * math.log(P0 / self.p_des) / self.vacuum_efficiency

    @property
    def work_equivalent_gj_per_t(self) -> float:
        """Exergy of the heat (Carnot factor at T_des) plus vacuum and fan work, GJ/t CO2."""
        carnot = 1.0 - self.T_ads / self.T_des
        fan = self.fan_gj_per_t if self.fan_gj_per_t is not None else fan_work_gj_per_tonne(X_AIR, 0.75, 100.0)
        return gj_per_tonne(self.heat * carnot + self.vacuum_work) + fan

    @property
    def second_law_efficiency(self) -> float:
        floor = gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99, self.T_ads))
        return floor / self.work_equivalent_gj_per_t


def sorbent_cost_per_tonne(price_per_kg: float, working_capacity: float, lifetime_cycles: float) -> float:
    """Sorbent replacement cost, $ per tonne CO2, for a working capacity in mol/kg."""
    kg_co2_per_kg_sorbent = working_capacity * M_CO2 * lifetime_cycles
    return price_per_kg / kg_co2_per_kg_sorbent * 1000.0


def productivity(working_capacity: float, cycles_per_day: float) -> float:
    """kg CO2 captured per kg sorbent per day."""
    return working_capacity * M_CO2 * cycles_per_day


def electrochemical_work(electrons_per_co2: float, cell_voltage: float, faradaic_efficiency: float = 1.0) -> float:
    """Electrical work of an electrochemical swing, J per mol CO2."""
    return electrons_per_co2 * FARADAY * cell_voltage / faradaic_efficiency


def moisture_swing_water_heat(mol_water_per_mol_co2: float) -> float:
    """Latent heat carried away by evaporating water in a moisture swing, J per mol CO2.

    This heat comes from ambient air if the air is dry enough; it is a water cost, not a fuel cost.
    """
    return mol_water_per_mol_co2 * DH_VAP_WATER


def reference_amine_cycle() -> TVSACycle:
    """Solid-amine-like reference: steam-assisted vacuum swing at 100 C with co-desorbed water."""
    return TVSACycle(dH=-70_000.0, dS=-165.0, q_max=2.0, T_des=373.15, p_des=1.0e3, water_coads=2.0)


def tradeoff_table(dS: float = -165.0, q_max: float = 2.0, p_des: float = 1.0e3,
                   residual_fraction: float = 0.2) -> list[dict]:
    """How binding strength sets both ambient uptake and regeneration temperature and heat."""
    rows = []
    for dH_kj in (-40, -50, -60, -70, -80, -90, -100):
        dH = dH_kj * 1e3
        theta = loading(P_CO2_AIR, T0, dH, dS, 1.0)
        t_des = desorption_temperature(dH, dS, p_des, residual_fraction)
        row = {"dH_kJ": dH_kj, "ambient_fill": theta, "T_des_C": t_des - 273.15}
        cyc = TVSACycle(dH=dH, dS=dS, q_max=q_max, T_des=max(t_des, T0 + 1.0), p_des=p_des)
        if cyc.working_capacity > 0:
            row.update(working_capacity=cyc.working_capacity, heat_gj_per_t=cyc.heat_gj_per_t,
                       work_eq_gj_per_t=cyc.work_equivalent_gj_per_t)
        rows.append(row)
    return rows


if __name__ == "__main__":
    print(f"Half-loading at 420 ppm needs dG = {dG_for_half_loading()/1e3:.1f} kJ/mol "
          f"(the same ~RT ln(1/x) that sets the separation floor)\n")
    ref = reference_amine_cycle()
    print("Reference solid-amine-like cycle (100 C, 1 kPa CO2, 2 mol water per mol CO2):")
    print(f"  working capacity {ref.working_capacity:.2f} mol/kg | heat {ref.heat_gj_per_t:.2f} GJ/t "
          f"(reaction {gj_per_tonne(ref.reaction_heat):.2f}, sensible {gj_per_tonne(ref.sensible_heat):.2f}, "
          f"water {gj_per_tonne(ref.water_heat):.2f})")
    print(f"  work-equivalent {ref.work_equivalent_gj_per_t:.2f} GJ/t | ideal-cycle second-law efficiency "
          f"{ref.second_law_efficiency:.0%}")
    print(f"  sorbent cost at $20/kg and 2,000 cycles: ${sorbent_cost_per_tonne(20, ref.working_capacity, 2000):.0f}/t; "
          f"at 20,000 cycles: ${sorbent_cost_per_tonne(20, ref.working_capacity, 20000):.0f}/t\n")
    print("Binding strength vs regeneration (dS = -165 J/mol/K, desorb to 20% fill at 1 kPa CO2, no water):")
    print(f"{'dH kJ/mol':>10}{'fill at 420 ppm':>17}{'T_des C':>9}{'wc mol/kg':>11}{'heat GJ/t':>11}{'work-eq GJ/t':>14}")
    for r in tradeoff_table():
        wc = f"{r['working_capacity']:.2f}" if "working_capacity" in r else "-"
        h = f"{r['heat_gj_per_t']:.2f}" if "heat_gj_per_t" in r else "-"
        w = f"{r['work_eq_gj_per_t']:.2f}" if "work_eq_gj_per_t" in r else "-"
        print(f"{r['dH_kJ']:>10}{r['ambient_fill']:>17.1%}{r['T_des_C']:>9.0f}{wc:>11}{h:>11}{w:>14}")
    print(f"\nElectro-swing example: 2 electrons per CO2 at 0.5 V, 90% faradaic efficiency = "
          f"{gj_per_tonne(electrochemical_work(2, 0.5, 0.9)):.2f} GJ/t (electricity)")
