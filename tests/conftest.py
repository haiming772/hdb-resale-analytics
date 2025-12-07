# tests/conftest.py
import os
import pytest

from application import create_app, db
from application.models import User


@pytest.fixture
def app():
    # Use in-memory DB for tests
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    app = create_app()
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,  # easier form + auth posts
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app, client):
    """Logged-in client for endpoints that require auth."""
    with app.app_context():
        user = User(username="tester", email="tester@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    # login via real form
    resp = client.post(
        "/login",
        data={"email": "tester@example.com", "password": "password123"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    return client
