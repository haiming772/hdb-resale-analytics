# application/utils_geo.py

"""
Geospatial utilities for the HDB Resale app.

Currently provides:
- haversine_km: distance between two lat/lng points
- distance_band_to_km: convert UI bands into numeric km values
"""

from math import radians, sin, cos, sqrt, atan2

# Default "typical" distances (km) used when the user isn't sure.
AMENITY_DEFAULTS = {
    "mrt": 0.6,
    "school": 0.7,
    "supermarket": 0.5,
    "health": 0.8,
}

# Band midpoints in km – same for all amenity types
BAND_MIDPOINTS = {
    "lt_0_3": 0.2,
    "b_0_3_0_8": 0.55,
    "b_0_8_1_5": 1.1,
    "b_1_5_3_0": 2.2,
    "gt_3_0": 3.5,
}


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """
    Basic haversine distance in km between two WGS84 coordinates.
    """
    R = 6371.0  # Earth radius in km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def distance_band_to_km(band: str, amenity_key: str) -> float:
    """
    Convert a band code from the form into a numeric distance in km.

    band: one of ["typical", "lt_0_3", "b_0_3_0_8", "b_0_8_1_5", "b_1_5_3_0", "gt_3_0"]
    amenity_key: "mrt" | "school" | "supermarket" | "health"
    """
    if not band or band == "typical":
        return AMENITY_DEFAULTS[amenity_key]

    return BAND_MIDPOINTS.get(band, AMENITY_DEFAULTS[amenity_key])
