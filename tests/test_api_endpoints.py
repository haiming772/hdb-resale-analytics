# tests/test_api_endpoints.py
import json


def _valid_predict_payload():
    return {
        "floor_area_sqm": 90.0,
        "storey_mid": 10,
        "remaining_lease_years": 65.0,
        "year": 2024,
        "dist_mrt_km": 0.6,
        "dist_school_km": 0.8,
        "dist_supermarket_km": 0.5,
        "dist_health_km": 1.0,
        "town": "ANG MO KIO",
        "flat_type": "4 ROOM",
        "flat_model": "Model A",
    }


# ---------- Validity testing on /api/predict ----------

def test_api_predict_valid_request_returns_price(client):
    """Happy path: complete JSON payload should return success and a price."""
    payload = _valid_predict_payload()
    resp = client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert isinstance(data["predicted_price"], (int, float))
    assert data["predicted_price"] > 0


# ---------- Expected failure testing on /api/predict ----------

def test_api_predict_missing_required_field_returns_400(client):
    """
    Expected failure: request missing a required key
    should respond with 400 + helpful error message.
    """
    payload = _valid_predict_payload()
    payload.pop("flat_model")  # required by routes.py

    resp = client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert resp.status_code == 400
    data = resp.get_json()
    assert data["success"] is False
    assert "Missing keys" in data["error"]


def test_login_wrong_password_expected_failure(client):
    """
    Expected failure: login with wrong password should not authenticate user.
    """
    # First create a valid user via registration form
    resp_reg = client.post(
        "/register",
        data={
            "username": "tester2",
            "email": "tester2@example.com",
            "password": "goodpass",
            "confirm_password": "goodpass",
        },
        follow_redirects=True,
    )
    assert resp_reg.status_code == 200

    # Now try to login with wrong password
    resp_login = client.post(
        "/login",
        data={"email": "tester2@example.com", "password": "wrongpass"},
        follow_redirects=True,
    )
    # Should render login page again and not crash
    assert resp_login.status_code == 200
    assert b"Invalid email or password." in resp_login.data


# ---------- Consistency testing on /api/predict ----------

def test_api_predict_same_input_same_output(client):
    """Two calls with identical payload should give identical predictions."""
    payload = _valid_predict_payload()

    resp1 = client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json",
    )
    resp2 = client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json",
    )

    p1 = resp1.get_json()["predicted_price"]
    p2 = resp2.get_json()["predicted_price"]

    assert p1 == p2


# ---------- Unexpected failure testing ----------

def test_api_predict_unexpected_model_error_returns_500(monkeypatch, client):
    """
    Simulate an unexpected failure inside the ML model.
    The API should surface it as a 500 error rather than behaving randomly.
    """
    # predict_resale_price is imported into routes.py, so we patch that symbol
    def boom(**kwargs):
        raise RuntimeError("Simulated model crash")

    monkeypatch.setattr("application.routes.predict_resale_price", boom)

    payload = _valid_predict_payload()
    resp = client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json",
    )

    # Unhandled error should bubble up as HTTP 500
    assert resp.status_code == 500


# ---------- Auth-protected REST APIs ----------

def test_api_history_requires_login(client):
    """History endpoint should enforce authentication."""
    resp = client.get("/api/history")
    # Usually a redirect to /login; in some configs could be 401/403
    assert resp.status_code in (302, 401, 403)


def test_api_history_returns_entries_after_predictions(auth_client):
    """
    After making predictions while logged in, /api/history
    should return a non-empty JSON list.
    """
    payload = _valid_predict_payload()

    # make two predictions while logged in
    for _ in range(2):
        resp = auth_client.post(
            "/api/predict",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 200

    resp = auth_client.get("/api/history")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert "predicted_price" in data[0]


def test_api_map_data_returns_aggregated_view(auth_client):
    """
    /api/map-data should return town aggregates and latest prediction
    once some predictions exist.
    """
    payload = _valid_predict_payload()

    # at least one prediction so map has data
    resp_pred = auth_client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp_pred.status_code == 200

    resp = auth_client.get("/api/map-data")
    assert resp.status_code == 200

    data = resp.get_json()
    assert "towns" in data
    assert isinstance(data["towns"], list)

    latest = data.get("latest")
    if latest is not None:
        assert "town" in latest
        assert "price" in latest
        assert "lat" in latest
        assert "lng" in latest
