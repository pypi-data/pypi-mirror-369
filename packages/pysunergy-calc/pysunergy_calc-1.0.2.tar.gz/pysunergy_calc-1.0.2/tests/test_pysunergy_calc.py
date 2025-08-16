import math
import pytest
from datetime import datetime, timezone

from pysunergy_calc import (
    compute_solar_potential,
    compute_panel_power,
    estimate_energy_produced,
)


def test_compute_solar_potential_equator_equinox_noon():
    # Computes expected solar position at equator, equinox, solar noon
    date = datetime(2025, 3, 21, 12, 0, 0, tzinfo=timezone.utc)
    position = compute_solar_potential(0, 0, date)
    assert abs(position.declination) < 0.5
    # Allow up to 0.5 degree difference due to real-world astronomical subtlety
    assert abs(position.altitude - 90) < 0.5
    assert math.isclose(position.hour_angle, 0, abs_tol=1)
    assert position.irradiance > 1350


def test_compute_solar_potential_at_night():
    # Returns zero irradiance and NaN azimuth with nighttime (sun below horizon)
    date = datetime(2025, 3, 21, 0, 0, 0, tzinfo=timezone.utc)
    position = compute_solar_potential(0, 0, date)
    assert position.altitude <= 0
    assert position.irradiance == 0
    assert math.isnan(position.azimuth)


def test_compute_solar_potential_invalid_inputs():
    # Throws error on out-of-range latitude/longitude or bad date
    with pytest.raises(ValueError):
        compute_solar_potential(-91, 0, datetime.utcnow())
    with pytest.raises(ValueError):
        compute_solar_potential(0, -181, datetime.utcnow())
    with pytest.raises(ValueError):
        compute_solar_potential(0, 0, "bad-date")


def test_compute_panel_power_correct():
    # Computes correct output
    area = 2  # m²
    eff = 0.2  # 20%
    irrad = 1000  # W/m²
    assert math.isclose(compute_panel_power(area, eff, irrad), 400, abs_tol=1e-3)


def test_compute_panel_power_negative_irradiance():
    # Returns zero if irradiance negative
    assert compute_panel_power(2, 0.2, -10) == 0


def test_compute_panel_power_invalid_input():
    # Throws error on invalid input
    with pytest.raises(ValueError):
        compute_panel_power(-2, 0.2, 1000)
    with pytest.raises(ValueError):
        compute_panel_power(2, -0.1, 1000)
    with pytest.raises(ValueError):
        compute_panel_power(2, 1.1, 1000)


def test_estimate_energy_produced_correct():
    # Computes correct daily energy
    # ~5kWh/m²/day under full sun for 2m² panel at 20% efficiency, PR=0.8
    area = 2
    efficiency = 0.2
    avg_irr = 5000 / 24  # 5kWh/m²/day = ~208.3W/m² avg
    kWh = estimate_energy_produced(area, efficiency, avg_irr, 24, 0.8)
    # 2×0.2×5×0.8 = 1.6kWh/day
    assert math.isclose(kWh, 1.6, abs_tol=0.1)


def test_estimate_energy_produced_invalid_input():
    # Throws error on invalid input
    with pytest.raises(ValueError):
        estimate_energy_produced(-2, 0.2, 100, 24)
    with pytest.raises(ValueError):
        estimate_energy_produced(2, -0.1, 100, 24)
    with pytest.raises(ValueError):
        estimate_energy_produced(2, 0.2, -100, 24)
    with pytest.raises(ValueError):
        estimate_energy_produced(2, 0.2, 100, 0)
    with pytest.raises(ValueError):
        estimate_energy_produced(2, 0.2, 100, 24, 2)
