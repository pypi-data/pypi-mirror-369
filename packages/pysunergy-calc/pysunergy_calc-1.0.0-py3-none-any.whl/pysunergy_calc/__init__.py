# The MIT License (MIT)

# Copyright (c) 2025 Abdullah Waqar

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Solar energy calculation references:
 - Instantaneous: https://www.pveducation.org/pvcdrom/properties-of-sunlight/calculation-of-solar-insolation
 - Energy formula: https://www.sunbasedata.com/blog/how-to-calculate-solar-panel-output
 - Methodology: https://palmetto.com/solar/how-much-energy-does-a-solar-panel-produce
 - General guide: https://www.ecoflow.com/us/blog/how-to-calculate-solar-panel-output

 | Step        | Equation                                            |
 | ----------- | --------------------------------------------------- |
 | Declination | δ = 23.45 × sin[(360/365) × (n − 81)]               |
 | Hour angle  | H = 15 × (solar-time-hours − 12)                    |
 | Altitude    | sin(α) = sin(δ) sin(φ) + cos(δ) cos(φ) cos(H)       |
 | Azimuth     | sin(Az) = cos(δ) sin(H) / cos(α)                    |
 | Irradiance  | I = I₀ × sin(α) (for horizontal surface, clear sky) |
"""

from dataclasses import dataclass
import math
from datetime import datetime, timezone

# All angles are in degrees


@dataclass
class SolarPosition:
    declination: float
    hour_angle: float
    altitude: float
    azimuth: float
    zenith: float
    irradiance: float  # W/m² (solar on horizontal)


def to_radians(deg: float) -> float:
    """Helper for radians conversion"""
    return (deg * math.pi) / 180


def to_degrees(rad: float) -> float:
    """Helper for degrees conversion"""
    return (rad * 180) / math.pi


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value between min and max"""
    return max(min_value, min(value, max_value))


def get_day_of_year(date: datetime) -> int:
    """
    Day of year from UTC date

    Args:
        date: datetime in UTC (timezone-aware)

    Returns:
        int: Day of year
    """
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    start = datetime(date.year, 1, 1, tzinfo=timezone.utc)
    return (date - start).days + 1


def compute_solar_potential(
    lat: float,
    lon: float,
    date: datetime,
) -> SolarPosition:
    """
    Computes solar position and horizontal surface irradiance for a given location and UTC time.

    Reference: https://www.pveducation.org/pvcdrom/properties-of-sunlight/calculation-of-solar-insolation

    Args:
        lat (float): Latitude in degrees [-90, 90]
        lon (float): Longitude in degrees [-180, 180]
        date (datetime): UTC datetime (timezone-aware recommended)

    Returns:
        SolarPosition: Calculated solar parameters
    """
    if math.isnan(lat) or lat < -90 or lat > 90:
        raise ValueError("Latitude must be in [-90, 90].")
    if math.isnan(lon) or lon < -180 or lon > 180:
        raise ValueError("Longitude must be in [-180, 180].")
    if not isinstance(date, datetime):
        raise ValueError("Invalid datetime object.")
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    # Solar constant, W/m²
    I0 = 1367
    n = get_day_of_year(date)

    # Solar declination (degrees)
    decl = 23.45 * math.sin(to_radians((360 / 365) * (n - 81)))

    # Solar time
    hours = date.hour + date.minute / 60 + date.second / 3600

    # Nearest standard meridian
    lstm = 15 * round(lon / 15)
    # Approx eq of time
    #
    eq_time = 7.5 * math.sin(to_radians((360 / 365) * (n - 81)))
    time_offset = eq_time + 4 * (lon - lstm)
    solar_time = hours + time_offset / 60
    hour_angle = 15 * (solar_time - 12)
    # Angles in radians
    lat_rad = to_radians(lat)
    decl_rad = to_radians(decl)
    ha_rad = to_radians(hour_angle)
    sin_alt = clamp(
        math.sin(lat_rad) * math.sin(decl_rad)
        + math.cos(lat_rad) * math.cos(decl_rad) * math.cos(ha_rad),
        -1,
        1,
    )
    altitude = to_degrees(math.asin(sin_alt))
    zenith = 90 - altitude
    azimuth = float("nan")
    ground_irradiance = 0.0
    if altitude > 0:
        # Azimuth
        den = math.cos(to_radians(altitude))
        sin_az = 0.0 if den == 0 else (math.cos(decl_rad) * math.sin(ha_rad)) / den
        sin_az = clamp(sin_az, -1, 1)
        azimuth = to_degrees(math.asin(sin_az))
        azimuth = 180 - azimuth if hour_angle > 0 else 180 + azimuth
        azimuth = (azimuth + 360) % 360
        ground_irradiance = max(0.0, I0 * sin_alt)
    return SolarPosition(
        declination=decl,
        hour_angle=hour_angle,
        altitude=altitude,
        azimuth=azimuth,
        zenith=zenith,
        irradiance=ground_irradiance,
    )


def compute_panel_power(
    area: float,
    efficiency: float,
    irradiance: float,
) -> float:
    """
    Compute instantaneous solar panel output (W) given panel specs and sun conditions.

    Reference: https://www.sunbasedata.com/blog/how-to-calculate-solar-panel-output

    Power = Area * Efficiency * Irradiance

    Args:
        area (float): Panel area in m²
        efficiency (float): Panel efficiency (fraction 0–1)
        irradiance (float): Solar irradiance in W/m² (from compute_solar_potential)

    Returns:
        float: Power output in Watts
    """
    if area < 0 or not math.isfinite(area):
        raise ValueError("Area must be >= 0.")
    if efficiency < 0 or efficiency > 1:
        raise ValueError("Efficiency in range 0–1.")
    if irradiance < 0:
        return 0.0
    return area * efficiency * irradiance


def estimate_energy_produced(
    area: float,
    efficiency: float,
    average_irradiance: float,
    period_hours: float,
    performance_ratio: float = 0.75,
) -> float:
    """
    Estimate total electrical energy produced over a given interval.

    Main reference: https://www.ecoflow.com/us/blog/how-to-calculate-solar-panel-output

    E(kWh) = Area * Efficiency * H * PR
    H = daily (or monthly/yearly) average insolation on panel in kWh/m²/day
    PR = performance ratio (accounts for losses, default 0.75)
    Reference: https://palmetto.com/solar/how-much-energy-does-a-solar-panel-produce

    Args:
        area (float): Panel area in m²
        efficiency (float): Panel efficiency [0, 1]
        average_irradiance (float): Average irradiance in W/m² (use as H)
        period_hours (float): Number of hours for the period (e.g. 24 for daily)
        performance_ratio (float): Performance ratio [0, 1] (default: 0.75)

    Returns:
        float: Energy produced in kWh
    """
    # For daily output, period_hours=24; for annual, period_hours=365 * 24, etc.
    if area < 0 or not math.isfinite(area):
        raise ValueError("Panel area must be >= 0.")
    if efficiency < 0 or efficiency > 1:
        raise ValueError("Efficiency in range 0–1.")
    if average_irradiance < 0:
        raise ValueError("Irradiance must be >= 0")
    if performance_ratio < 0 or performance_ratio > 1:
        raise ValueError("Performance ratio in 0–1")
    if period_hours <= 0:
        raise ValueError("Period hours must be > 0")

    # average_irradiance expected in W/m², so convert to kWh as averageIrradiance * period / 1000
    energy_kwh = (
        area
        * efficiency
        * ((average_irradiance * period_hours) / 1000)
        * performance_ratio
    )
    return energy_kwh
