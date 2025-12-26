"""Geography and Radio Math Utilities."""

import math


def calculate_heading_impl(start: str, end: str) -> float:
    """
    Calculates the initial beam heading (azimuth) from start to end in degrees.
    """
    lat1, lon1 = to_latlon(start)
    lat2, lon2 = to_latlon(end)

    # Convert to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_lambda = math.radians(lon2 - lon1)

    y = math.sin(d_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)

    theta = math.atan2(y, x)
    bearing = (math.degrees(theta) + 360) % 360

    return round(bearing, 1)


def to_latlon(locator: str) -> tuple[float, float]:
    """
    Decodes a Maidenhead locator to (latitude, longitude).

    Args:
        locator: Maidenhead locator (e.g., 'CN87' or 'CN87ra').

    Returns:
        A tuple of (latitude, longitude).
    """
    locator = locator.strip().upper()
    if len(locator) < 4:
        raise ValueError("Locator must be at least 4 characters")

    # Field 1 (A-R): 20 deg Lon, 10 deg Lat
    lon = (ord(locator[0]) - ord("A")) * 20.0 - 180.0
    lat = (ord(locator[1]) - ord("A")) * 10.0 - 90.0

    # Field 2 (0-9): 2 deg Lon, 1 deg Lat
    lon += (ord(locator[2]) - ord("0")) * 2
    lat += (ord(locator[3]) - ord("0")) * 1

    # Field 3 (A-X): 5 min Lon, 2.5 min Lat
    if len(locator) >= 6:
        lon += (ord(locator[4]) - ord("A")) * (5 / 60) + (2.5 / 60)
        lat += (ord(locator[5]) - ord("A")) * (2.5 / 60) + (1.25 / 60)
    else:
        # Center of 4-character square
        lon += 1.0
        lat += 0.5

    return lat, lon


def calculate_distance_impl(start: str, end: str) -> float:
    """
    Calculates great-circle distance (km) between two Maidenhead locators.

    Args:
        start: Starting Maidenhead locator.
        end: Ending Maidenhead locator.

    Returns:
        Distance in kilometers rounded to 2 decimal places.
    """
    lat1, lon1 = to_latlon(start)
    lat2, lon2 = to_latlon(end)

    r_earth = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(r_earth * c, 2)
