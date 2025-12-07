import requests

payload = {
    "floor_area_sqm": 90,
    "storey_mid": 8,
    "remaining_lease_years": 70,
    "year": 2024,
    "dist_mrt_km": 0.4,
    "dist_school_km": 0.3,
    "dist_supermarket_km": 0.2,
    "dist_health_km": 0.5,
    "town": "ANG MO KIO",
    "flat_type": "4 ROOM",
    "flat_model": "Model A"
}

r = requests.post("http://127.0.0.1:5000/api/predict", json=payload)
print(r.json())
