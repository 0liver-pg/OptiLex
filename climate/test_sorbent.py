import math
import pytest
from physics import R, T0, gj_per_tonne
from sorbent import (P_CO2_AIR, P_REF, TVSACycle, dG_for_half_loading, desorption_temperature,
                     electrochemical_work, langmuir_b, loading, productivity, reference_amine_cycle,
                     sorbent_cost_per_tonne, tradeoff_table)


def test_half_loading_free_energy_matches_dilution_term():
    dG = dG_for_half_loading()
    assert dG == pytest.approx(-R * T0 * math.log(P_REF / P_CO2_AIR))
    assert -20.0e3 < dG < -18.5e3
    # A site with exactly that dG is half full at 420 ppm.
    dS = -150.0
    dH = dG + T0 * dS
    assert loading(P_CO2_AIR, T0, dH, dS, 1.0) == pytest.approx(0.5, rel=1e-9)


def test_loading_falls_with_temperature_and_rises_with_pressure():
    args = (-70e3, -165.0, 2.0)
    assert loading(P_CO2_AIR, 373.15, *args) < loading(P_CO2_AIR, T0, *args)
    assert loading(10 * P_CO2_AIR, T0, *args) > loading(P_CO2_AIR, T0, *args)
    assert langmuir_b(-80e3, -165.0, T0) > langmuir_b(-60e3, -165.0, T0)


def test_desorption_temperature_is_self_consistent():
    dH, dS, p_des = -70e3, -165.0, 1e3
    T = desorption_temperature(dH, dS, p_des, residual_fraction=0.2)
    assert loading(p_des, T, dH, dS, 1.0) == pytest.approx(0.2, rel=1e-6)


def test_regeneration_heat_never_below_binding_enthalpy():
    cyc = TVSACycle(dH=-70e3, dS=-165.0, q_max=2.0)
    assert cyc.heat >= 70e3
    assert cyc.heat_gj_per_t == pytest.approx(gj_per_tonne(cyc.heat))


def test_reference_amine_cycle_lands_in_literature_range():
    # Solid-amine DAC is commonly reported at roughly 5-7 GJ/t of heat (about 1,500-2,000 kWh/t thermal).
    ref = reference_amine_cycle()
    assert 4.0 < ref.heat_gj_per_t < 8.0
    assert 0.5 < ref.working_capacity < 1.5
    assert 0.0 < ref.second_law_efficiency < 1.0


def test_stronger_binding_needs_hotter_regeneration():
    rows = tradeoff_table()
    temps = [r["T_des_C"] for r in rows]
    fills = [r["ambient_fill"] for r in rows]
    assert temps == sorted(temps)
    assert fills == sorted(fills)


def test_heat_recovery_and_water_change_heat_in_the_right_direction():
    base = TVSACycle(dH=-70e3, dS=-165.0, q_max=2.0)
    assert TVSACycle(dH=-70e3, dS=-165.0, q_max=2.0, heat_recovery=0.5).heat < base.heat
    assert TVSACycle(dH=-70e3, dS=-165.0, q_max=2.0, water_coads=2.0).heat > base.heat


def test_no_working_capacity_raises():
    cyc = TVSACycle(dH=-70e3, dS=-165.0, q_max=2.0, T_des=T0, p_des=1e5)
    assert cyc.working_capacity == 0.0
    with pytest.raises(ValueError):
        _ = cyc.heat


def test_sorbent_cost_and_productivity_units():
    # 1 mol/kg x 0.04401 kg/mol x 1,000 cycles = 44.01 kg CO2 per kg sorbent; $44.01/kg -> $1,000/t.
    assert sorbent_cost_per_tonne(44.01, 1.0, 1000) == pytest.approx(1000.0)
    assert productivity(1.0, 10) == pytest.approx(0.4401)


def test_electrochemical_work_units():
    # 1 electron at 1 V = 96.485 kJ/mol = 2.19 GJ/t CO2.
    assert gj_per_tonne(electrochemical_work(1, 1.0)) == pytest.approx(2.192, rel=1e-3)
