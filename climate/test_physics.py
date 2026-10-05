import math
import pytest
from physics import (R, T0, M_CO2, min_separation_work, gj_per_tonne, air_volume_per_tonne,
                     fan_work_gj_per_tonne, ScaleCheck, second_law_efficiency)


def test_dilute_limit_matches_rt_ln_inverse_x():
    # Vanishing capture into a pure product: W -> RT ln(1/x).
    x = 420e-6
    w = min_separation_work(x, capture_fraction=1e-6, purity=1 - 1e-12)
    assert w == pytest.approx(R * T0 * math.log(1 / x), rel=1e-3)


def test_air_capture_floor_is_about_20_kj_per_mol():
    # Literature: ~20 kJ/mol (~0.45-0.5 GJ/t) for DAC at realistic capture fractions
    # (e.g. House et al. 2011 PNAS; Lackner). Our ideal-gas calculation should land there.
    w = min_separation_work(420e-6, 0.75, 0.99)
    assert 19e3 < w < 22e3
    assert 0.43 < gj_per_tonne(w) < 0.5


def test_flue_gas_is_several_times_cheaper_than_air():
    air = min_separation_work(420e-6, 0.9, 0.99)
    coal = min_separation_work(0.12, 0.9, 0.99)
    assert air / coal > 2.5


def test_work_increases_with_capture_fraction():
    assert min_separation_work(0.12, 0.99) > min_separation_work(0.12, 0.5)


def test_air_volume_order_of_magnitude():
    # ~0.76 g CO2 per m^3 of air at 420 ppm -> ~1.3e6 m^3 per tonne at 100% capture.
    assert air_volume_per_tonne(420e-6, 1.0) == pytest.approx(1.32e6, rel=0.03)


def test_scale_check_units():
    s = ScaleCheck(gt_per_year=1.0, gj_per_tonne=1.0)
    assert s.ej_per_year == pytest.approx(1.0)


def test_second_law_efficiency():
    assert second_law_efficiency(5.0, 0.5) == pytest.approx(0.1)


def test_fan_work_positive_and_scales_with_pressure_drop():
    a = fan_work_gj_per_tonne(420e-6, 0.75, 100)
    b = fan_work_gj_per_tonne(420e-6, 0.75, 200)
    assert b == pytest.approx(2 * a)
