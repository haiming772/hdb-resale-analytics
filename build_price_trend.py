# build_price_trend.py
#
# One-off helper script to create a small JSON file with
# yearly median HDB resale prices for the hero "Price trend snapshot".

from pathlib import Path
import json
import pandas as pd


RAW_PATH = Path("data/raw/sg-resale-flat-prices-2017-onwards.csv")
if not RAW_PATH.exists():
    raise SystemExit(f"CSV not found at {RAW_PATH.resolve()}")

df = pd.read_csv(RAW_PATH)

# Expect a "month" column like "2017-01"
if "month" not in df.columns or "resale_price" not in df.columns:
    raise SystemExit("CSV must contain 'month' and 'resale_price' columns.")

df["year"] = pd.to_datetime(df["month"]).dt.year

trend = (
    df.groupby("year")["resale_price"]
    .median()
    .reset_index()
    .sort_values("year")
)

records = [
    {"year": int(row.year), "resale_price": float(row.resale_price)}
    for _, row in trend.iterrows()
]

out_path = Path("application/static/data/price_trend.json")
out_path.parent.mkdir(parents=True, exist_ok=True)

with out_path.open("w", encoding="utf-8") as f:
    json.dump(records, f, indent=2)

print(f"✅ Wrote {len(records)} yearly points to {out_path}")
