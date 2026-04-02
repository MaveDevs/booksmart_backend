from datetime import date
from math import asin, cos, radians, sin, sqrt
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Establishment, Plan, Subscription, User
from app.models.subscriptions import SubscriptionStatus
from app.schemas.establishments import EstablishmentCreate, EstablishmentUpdate


def get_establishment(db: Session, establishment_id: int) -> Optional[Establishment]:
    return (
        db.query(Establishment)
        .filter(Establishment.establecimiento_id == establishment_id)
        .first()
    )


def get_establishments(db: Session, skip: int = 0, limit: int = 100) -> List[Establishment]:
    return db.query(Establishment).offset(skip).limit(limit).all()


def get_establishments_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Establishment]:
    return (
        db.query(Establishment)
        .filter(Establishment.usuario_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def _haversine_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    earth_radius_km = 6371.0
    lat1 = radians(latitude_1)
    lon1 = radians(longitude_1)
    lat2 = radians(latitude_2)
    lon2 = radians(longitude_2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return earth_radius_km * c


def get_establishments_nearby(
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float = 10.0,
    skip: int = 0,
    limit: int = 100,
) -> List[dict]:
    establishments = db.query(Establishment).filter(Establishment.activo.is_(True)).all()
    today = date.today()
    ranked_establishments: List[dict] = []

    for establishment in establishments:
        if establishment.latitud is None or establishment.longitud is None:
            continue

        distance_km = _haversine_km(
            latitude,
            longitude,
            float(establishment.latitud),
            float(establishment.longitud),
        )

        if distance_km > radius_km:
            continue

        active_subscription = (
            db.query(Subscription)
            .join(Plan, Subscription.plan_id == Plan.plan_id)
            .filter(Subscription.establecimiento_id == establishment.establecimiento_id)
            .filter(Subscription.estado == SubscriptionStatus.ACTIVA)
            .filter((Subscription.fecha_fin.is_(None)) | (Subscription.fecha_fin >= today))
            .order_by(Subscription.fecha_inicio.desc(), Subscription.suscripcion_id.desc())
            .first()
        )

        subscription_active = active_subscription is not None
        subscription_plan_id = active_subscription.plan_id if active_subscription else None
        subscription_plan_name = (
            active_subscription.plan.nombre if active_subscription and active_subscription.plan else None
        )

        proximity_score = max(0.0, 1.0 - (distance_km / radius_km)) * 60.0
        subscription_score = 25.0 if subscription_active else 0.0
        premium_score = 10.0 if (subscription_plan_name or "").upper() == "PREMIUM" else 0.0
        ranking_score = round(proximity_score + subscription_score + premium_score, 4)

        ranked_establishments.append(
            {
                "establishment": establishment,
                "distance_km": round(distance_km, 3),
                "ranking_score": ranking_score,
                "subscription_active": subscription_active,
                "subscription_plan_id": subscription_plan_id,
                "subscription_plan_name": subscription_plan_name,
            }
        )

    ranked_establishments.sort(
        key=lambda item: (
            -item["ranking_score"],
            item["distance_km"],
            str(item["establishment"].nombre).lower(),
        )
    )

    return ranked_establishments[skip : skip + limit]


def create_establishment(db: Session, establishment: EstablishmentCreate) -> Establishment:
    # Verify usuario_id exists
    user = db.query(User).filter(User.usuario_id == establishment.usuario_id).first()
    if not user:
        raise ValueError(f"User with id {establishment.usuario_id} does not exist")
    
    db_establishment = Establishment(**establishment.model_dump())
    db.add(db_establishment)
    db.commit()
    db.refresh(db_establishment)
    return db_establishment

def update_establishment(db: Session, establishment_id: int, establishment: EstablishmentUpdate) -> Optional[Establishment]:
    db_establishment = get_establishment(db, establishment_id)
    if not db_establishment:
        return None
    
    update_data = establishment.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_establishment, field, value)
    
    db.commit()
    db.refresh(db_establishment)
    return db_establishment

def delete_establishment(db: Session, establishment_id: int) -> bool:
    db_establishment = get_establishment(db, establishment_id)
    if not db_establishment:
        return False
    
    db.delete(db_establishment)
    db.commit()
    return True