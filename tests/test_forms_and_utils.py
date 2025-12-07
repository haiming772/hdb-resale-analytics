# tests/test_forms_and_utils.py

from application.forms import HDBPriceForm
from application.utils_geo import distance_band_to_km


def _valid_form_data():
    """Baseline valid payload for HDBPriceForm."""
    return {
        "town": "ANG MO KIO",
        "flat_type": "4 ROOM",
        "flat_model": "Model A",
        "floor_area_sqm": 90,
        "storey_mid": 8,
        "remaining_lease_years": 65,
        "year": 2024,
        "use_amenity_distances": True,
        "dist_mrt_band": "typical",
        "dist_school_band": "typical",
        "dist_supermarket_band": "typical",
        "dist_health_band": "typical",
    }


# ---------- Validity testing ----------

def test_hdb_price_form_valid(app):
    """Form with a full, valid payload should validate successfully."""
    with app.test_request_context("/hdb/predict", method="POST"):
        form = HDBPriceForm(data=_valid_form_data())
        assert form.validate() is True


# ---------- Range testing ----------

def test_floor_area_too_small_rejected(app):
    """Floor area below 10 sqm should fail range validation."""
    data = _valid_form_data()
    data["floor_area_sqm"] = 5  # below min 10

    with app.test_request_context("/hdb/predict", method="POST"):
        form = HDBPriceForm(data=data)
        assert form.validate() is False
        assert "floor_area_sqm" in form.errors


def test_floor_area_boundary_ok(app):
    """Floor area exactly at lower bound (10) should be accepted."""
    data = _valid_form_data()
    data["floor_area_sqm"] = 10  # boundary value

    with app.test_request_context("/hdb/predict", method="POST"):
        form = HDBPriceForm(data=data)
        assert form.validate() is True


def test_year_out_of_allowed_range_fails(app):
    """Year outside allowed 2017–2030 range should fail."""
    data = _valid_form_data()
    data["year"] = 2035  # above max 2030

    with app.test_request_context("/hdb/predict", method="POST"):
        form = HDBPriceForm(data=data)
        assert form.validate() is False
        assert "year" in form.errors


# ---------- Consistency testing (utility behaviour) ----------

def test_distance_band_typical_consistent_across_calls():
    """'typical' band for a given amenity should always give same km value."""
    v1 = distance_band_to_km("typical", "mrt")
    v2 = distance_band_to_km("typical", "mrt")
    assert v1 == v2
    assert isinstance(v1, float)
    assert v1 > 0
