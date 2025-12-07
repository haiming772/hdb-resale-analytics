# application/crud.py

from typing import Optional, List
from flask_login import current_user

from application import db
from application.models import PredictionEntry, User


def create_user(username: str, email: str, password: str) -> User:
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def get_user_by_email(email: str) -> Optional[User]:
    return User.query.filter_by(email=email).first()


def save_prediction(
    predicted_price: float,
    town: str,
    flat_type: str,
    flat_model: str,
    floor_area_sqm: float,
    storey_mid: int,
    remaining_lease_years: float,
    year: int,
    dist_mrt_km: float,
    dist_school_km: float,
    dist_supermarket_km: float,
    dist_health_km: float,
) -> PredictionEntry:
    user_id = current_user.id if current_user.is_authenticated else None

    entry = PredictionEntry(
        predicted_price=predicted_price,
        town=town,
        flat_type=flat_type,
        flat_model=flat_model,
        floor_area_sqm=floor_area_sqm,
        storey_mid=storey_mid,
        remaining_lease_years=remaining_lease_years,
        year=year,
        dist_mrt_km=dist_mrt_km,
        dist_school_km=dist_school_km,
        dist_supermarket_km=dist_supermarket_km,
        dist_health_km=dist_health_km,
        user_id=user_id,
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def get_user_predictions(limit: int = 50) -> List[PredictionEntry]:
    if not current_user.is_authenticated:
        return []
    return (
        PredictionEntry.query.filter_by(user_id=current_user.id)
        .order_by(PredictionEntry.created_at.desc())
        .limit(limit)
        .all()
    )
