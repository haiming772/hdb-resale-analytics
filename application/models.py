# application/models.py

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from application import db


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    predictions = db.relationship(
        "PredictionEntry",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class PredictionEntry(db.Model):
    __tablename__ = "prediction_entry"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Model inputs
    town = db.Column(db.String(50), nullable=False)
    flat_type = db.Column(db.String(20), nullable=False)
    flat_model = db.Column(db.String(50), nullable=False)

    floor_area_sqm = db.Column(db.Float, nullable=False)
    storey_mid = db.Column(db.Integer, nullable=False)
    remaining_lease_years = db.Column(db.Float, nullable=False)

    year = db.Column(db.Integer, nullable=False)

    dist_mrt_km = db.Column(db.Float, nullable=False)
    dist_school_km = db.Column(db.Float, nullable=False)
    dist_supermarket_km = db.Column(db.Float, nullable=False)
    dist_health_km = db.Column(db.Float, nullable=False)

    # Model output
    predicted_price = db.Column(db.Float, nullable=False)

    # Optional owner
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user = db.relationship("User", back_populates="predictions")

    def __repr__(self) -> str:
        return f"<PredictionEntry {self.id} ${self.predicted_price:,.0f}>"
