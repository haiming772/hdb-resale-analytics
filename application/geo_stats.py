# application/geo_stats.py

import os
from typing import List, Dict, Any

import pandas as pd

from .ml_inference import predict_resale_price

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_PATH = os.path.join(
    BASE_DIR,
    "..",
    "data",
    "raw",
    "sg-resale-flat-prices-2017-onwards.csv",
)

# Approximate centroids for HDB towns (good enough for coursework)
TOWN_COORDS = {
    "ANG MO KIO": (1.3691, 103.8450),
    "BEDOK": (1.3236, 103.9273),
    "BISHAN": (1.3508, 103.8485),
    "BUKIT BATOK": (1.3496, 103.7500),
    "BUKIT MERAH": (1.2854, 103.8185),
    "BUKIT PANJANG": (1.3787, 103.7643),
    "BUKIT TIMAH": (1.3294, 103.8021),
    "CENTRAL AREA": (1.2929, 103.8530),
    "CHOA CHU KANG": (1.3854, 103.7445),
    "CLEMENTI": (1.3151, 103.7640),
    "GEYLANG": (1.3186, 103.8840),
    "HOUGANG": (1.3713, 103.8925),
    "JURONG EAST": (1.3327, 103.7432),
    "JURONG WEST": (1.3395, 103.7090),
    "KALLANG/WHAMPOA": (1.3190, 103.8570),
    "MARINE PARADE": (1.3031, 103.9013),
    "PASIR RIS": (1.3730, 103.9490),
    "PUNGGOL": (1.4043, 103.9020),
    "QUEENSTOWN": (1.2941, 103.7875),
    "SEMBAWANG": (1.4491, 103.8180),
    "SENGKANG": (1.3924, 103.8950),
    "SERANGOON": (1.3539, 103.8720),
    "TAMPINES": (1.3546, 103.9450),
    "TOA PAYOH": (1.3347, 103.8510),
    "WOODLANDS": (1.4360, 103.7865),
    "YISHUN": (1.4293, 103.8355),
    "LIM CHU KANG": (1.4310, 103.7110),
}


def _load_raw() -> pd.DataFrame:
    if not os.path.exists(RAW_PATH):
        return pd.DataFrame()

    df = pd.read_csv(RAW_PATH)

    # Minimal sanity filter: drop impossible / 0 prices
    if "resale_price" in df.columns:
        df = df[df["resale_price"] > 0]

    return df


def compute_town_geo_stats() -> List[Dict[str, Any]]:
    """
    Level-3 geo analytics:
    - historical median price per town
    - transaction count per town
    - standardised model prediction per town
      (4R, 90sqm, 60-year lease, 2024, fixed amenity distances)
    """
    df = _load_raw()
    if df.empty or "town" not in df.columns or "resale_price" not in df.columns:
        return []

    grouped = df.groupby("town")["resale_price"]
    medians = grouped.median()
    counts = grouped.size()

    results: List[Dict[str, Any]] = []

    for town, median_price in medians.items():
        if town not in TOWN_COORDS:
            continue

        lat, lon = TOWN_COORDS[town]

        # Standardised scenario so towns are comparable
        scenario_kwargs = dict(
            floor_area_sqm=90,
            storey_mid=10,
            remaining_lease_years=60,
            year=2024,
            dist_mrt_km=0.6,
            dist_school_km=0.8,
            dist_supermarket_km=0.5,
            dist_health_km=1.0,
            town=town,
            flat_type="4 ROOM",
            flat_model="Model A",
        )

        try:
            model_price = predict_resale_price(**scenario_kwargs)
        except Exception:
            model_price = None

        results.append(
            dict(
                town=town,
                lat=float(lat),
                lon=float(lon),
                median_resale_price=float(median_price),
                n_transactions=int(counts[town]),
                model_price=float(model_price) if model_price is not None else None,
            )
        )

    return results
