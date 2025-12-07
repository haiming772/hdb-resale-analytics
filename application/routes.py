# application/routes.py

from collections import defaultdict

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    current_app,
)
from flask_login import login_required, current_user

from application.forms import HDBPriceForm
from application.ml_inference import predict_resale_price
from application.crud import save_prediction, get_user_predictions
from application.utils_geo import distance_band_to_km

main_bp = Blueprint("main", __name__)

# Approximate town centroids (lat, lng) for map visualisation.
TOWN_COORDS = {
    "ANG MO KIO": (1.3700, 103.8490),
    "BEDOK": (1.3250, 103.9310),
    "BISHAN": (1.3500, 103.8480),
    "BUKIT BATOK": (1.3480, 103.7540),
    "BUKIT MERAH": (1.2820, 103.8180),
    "BUKIT PANJANG": (1.3780, 103.7640),
    "BUKIT TIMAH": (1.3290, 103.7910),
    "CENTRAL AREA": (1.2900, 103.8520),
    "CHOA CHU KANG": (1.3840, 103.7470),
    "CLEMENTI": (1.3150, 103.7640),
    "GEYLANG": (1.3180, 103.8870),
    "HOUGANG": (1.3710, 103.8860),
    "JURONG EAST": (1.3340, 103.7420),
    "JURONG WEST": (1.3400, 103.7080),
    "KALLANG/WHAMPOA": (1.3130, 103.8570),
    "MARINE PARADE": (1.3030, 103.9070),
    "PASIR RIS": (1.3730, 103.9490),
    "PUNGGOL": (1.4050, 103.9020),
    "QUEENSTOWN": (1.2940, 103.8060),
    "SEMBAWANG": (1.4480, 103.8180),
    "SENGKANG": (1.3930, 103.8950),
    "SERANGOON": (1.3510, 103.8700),
    "TAMPINES": (1.3540, 103.9450),
    "TOA PAYOH": (1.3340, 103.8510),
    "WOODLANDS": (1.4380, 103.7880),
    "YISHUN": (1.4290, 103.8370),
    "LIM CHU KANG": (1.4240, 103.7100),
}


@main_bp.route("/")
def index():
    """
    Landing page that explains what the app does and funnels users into
    login / signup or the predictor if they are already signed in.
    """
    return render_template("index.html")


@main_bp.route("/hdb/")
def hdb_root():
    """
    Convenience redirect so /hdb/ still works and just goes to the predictor.
    """
    return redirect(url_for("main.hdb_predict"))


@main_bp.route("/hdb/predict", methods=["GET", "POST"])
@login_required
def hdb_predict():
    form = HDBPriceForm()
    predicted_price = None

    if form.validate_on_submit():
        # Convert amenity bands into numeric km values
        use_amenities = form.use_amenity_distances.data

        if use_amenities:
            dist_mrt_km = distance_band_to_km(form.dist_mrt_band.data, "mrt")
            dist_school_km = distance_band_to_km(form.dist_school_band.data, "school")
            dist_supermarket_km = distance_band_to_km(
                form.dist_supermarket_band.data, "supermarket"
            )
            dist_health_km = distance_band_to_km(form.dist_health_band.data, "health")
        else:
            # If user disables amenities, fall back entirely to typical distances
            dist_mrt_km = distance_band_to_km("typical", "mrt")
            dist_school_km = distance_band_to_km("typical", "school")
            dist_supermarket_km = distance_band_to_km("typical", "supermarket")
            dist_health_km = distance_band_to_km("typical", "health")

        kwargs = dict(
            floor_area_sqm=form.floor_area_sqm.data,
            storey_mid=form.storey_mid.data,
            remaining_lease_years=form.remaining_lease_years.data,
            year=form.year.data,
            dist_mrt_km=dist_mrt_km,
            dist_school_km=dist_school_km,
            dist_supermarket_km=dist_supermarket_km,
            dist_health_km=dist_health_km,
            town=form.town.data,
            flat_type=form.flat_type.data,
            flat_model=form.flat_model.data,
        )

        predicted_price = predict_resale_price(**kwargs)
        save_prediction(predicted_price=predicted_price, **kwargs)

        flash(f"Estimated resale price: ${predicted_price:,.0f}", "success")

    return render_template(
        "hdb_predict.html",
        form=form,
        predicted_price=predicted_price,
    )


@main_bp.route("/history")
@login_required
def history():
    """
    Prediction history page (endpoint name = main.history).
    Needed for the navbar and for error pages that extend base.html.
    """
    predictions = get_user_predictions(limit=100)
    return render_template("history.html", predictions=predictions)


# ---------- JSON APIs ----------


@main_bp.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json() or {}

    # Expect raw numeric distances from the frontend for this API
    required = [
        "floor_area_sqm",
        "storey_mid",
        "remaining_lease_years",
        "year",
        "dist_mrt_km",
        "dist_school_km",
        "dist_supermarket_km",
        "dist_health_km",
        "town",
        "flat_type",
        "flat_model",
    ]
    missing = [k for k in required if k not in data]
    if missing:
        return (
            jsonify({"success": False, "error": f"Missing keys: {', '.join(missing)}"}),
            400,
        )

    # Wrap the ML + DB logic in a try/except so unexpected failures
    # become a clean 500 JSON response instead of crashing the app.
    try:
        price = predict_resale_price(**data)
        save_prediction(predicted_price=price, **data)
    except Exception as exc:  # noqa: BLE001 - we do want a broad catch here
        current_app.logger.exception("Unexpected error in /api/predict: %s", exc)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Internal model error while generating prediction.",
                }
            ),
            500,
        )

    return jsonify({"success": True, "predicted_price": price})


@main_bp.route("/api/history")
@login_required
def api_history():
    entries = get_user_predictions(limit=100)
    return jsonify(
        [
            {
                "created_at": e.created_at.isoformat(),
                "town": e.town,
                "flat_type": e.flat_type,
                "flat_model": e.flat_model,
                "floor_area_sqm": e.floor_area_sqm,
                "storey_mid": e.storey_mid,
                "remaining_lease_years": e.remaining_lease_years,
                "year": e.year,
                "dist_mrt_km": e.dist_mrt_km,
                "dist_school_km": e.dist_school_km,
                "dist_supermarket_km": e.dist_supermarket_km,
                "dist_health_km": e.dist_health_km,
                "predicted_price": e.predicted_price,
            }
            for e in entries
        ]
    )


@main_bp.route("/api/map-data")
@login_required
def api_map_data():
    """
    Returns aggregated prediction stats by town for the interactive map.

    Output:
    {
      "towns": [
        {
          "town": "...",
          "lat": ...,
          "lng": ...,
          "count": 5,
          "avg_price": 520000.0
        },
        ...
      ],
      "latest": {...}  # latest prediction (if any)
    }
    """
    entries = get_user_predictions(limit=200)

    stats = defaultdict(lambda: {"count": 0, "sum_price": 0.0})
    latest = None

    for p in entries:
        stats[p.town]["count"] += 1
        stats[p.town]["sum_price"] += p.predicted_price

        if latest is None or p.created_at > latest.created_at:
            latest = p

    towns_payload = []
    for town, agg in stats.items():
        coords = TOWN_COORDS.get(town)
        if not coords:
            continue
        count = agg["count"]
        avg_price = agg["sum_price"] / count if count else 0.0
        towns_payload.append(
            {
                "town": town,
                "lat": coords[0],
                "lng": coords[1],
                "count": count,
                "avg_price": avg_price,
            }
        )

    latest_payload = None
    if latest:
        coords = TOWN_COORDS.get(latest.town)
        if coords:
            latest_payload = {
                "town": latest.town,
                "flat_type": latest.flat_type,
                "flat_model": latest.flat_model,
                "price": latest.predicted_price,
                "year": latest.year,
                "created_at": latest.created_at.isoformat(),
                "lat": coords[0],
                "lng": coords[1],
            }

    return jsonify({"towns": towns_payload, "latest": latest_payload})
