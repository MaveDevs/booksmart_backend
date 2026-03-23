from typing import List, Optional, Dict, Any
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Plan
from app.schemas.plans import PlanCreate, PlanUpdate


def get_plan(db: Session, plan_id: int) -> Optional[Plan]:
    return db.query(Plan).filter(Plan.plan_id == plan_id).first()


def get_plans(db: Session, skip: int = 0, limit: int = 100) -> List[Plan]:
    return db.query(Plan).offset(skip).limit(limit).all()


def create_plan(db: Session, plan: PlanCreate) -> Plan:
    plan_data = plan.model_dump()
    db_plan = Plan(**plan_data)  # type: ignore[arg-type]
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def update_plan(db: Session, plan_id: int, plan: PlanUpdate) -> Optional[Plan]:
    db_plan = get_plan(db, plan_id)
    if not db_plan:
        return None

    update_data = plan.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_plan, field, value)

    db.commit()
    db.refresh(db_plan)
    return db_plan


def delete_plan(db: Session, plan_id: int) -> bool:
    db_plan = get_plan(db, plan_id)
    if not db_plan:
        return False

    db.delete(db_plan)
    db.commit()
    return True


def initialize_default_plans(db: Session) -> Dict[str, Any]:
    """
    Initialize default FREE and PREMIUM plans with their features.
    Idempotent - if plans already exist, just returns their IDs.
    """
    from app.crud import crud_plan_features
    from app.models.plan_features import FeatureKey

    result = {"created": False, "free_plan_id": None, "premium_plan_id": None}

    # Check if plans already exist
    free_plan = db.query(Plan).filter(Plan.nombre == "FREE").first()
    premium_plan = db.query(Plan).filter(Plan.nombre == "PREMIUM").first()

    # Create FREE plan if doesn't exist
    if not free_plan:
        free_plan = create_plan(
            db,
            PlanCreate(
                nombre="FREE",
                descripcion="Plan básico gratuito con características limitadas",
                precio=Decimal("0.00"),
                activo=True,
            ),
        )
        result["created"] = True
    result["free_plan_id"] = free_plan.plan_id

    # Create PREMIUM plan if doesn't exist
    if not premium_plan:
        premium_plan = create_plan(
            db,
            PlanCreate(
                nombre="PREMIUM",
                descripcion="Plan premium con automatizaciones y análisis avanzado",
                precio=Decimal("9.99"),
                activo=True,
            ),
        )
        result["created"] = True
    result["premium_plan_id"] = premium_plan.plan_id

    # Seed features for FREE plan
    free_features = [
        FeatureKey.AUTO_RESEÑA_PROMPT,
    ]
    crud_plan_features.seed_plan_features(db, free_plan.plan_id, free_features)

    # Seed features for PREMIUM plan
    premium_features = [
        FeatureKey.AUTO_REMINDERS,
        FeatureKey.AUTO_CONFIRMACION,
        FeatureKey.AUTO_RECOVERY,
        FeatureKey.AUTO_RESEÑA_PROMPT,
        FeatureKey.DESTACADO_LISTING,
        FeatureKey.CAMPAÑAS_VISIBILIDAD,
        FeatureKey.ANALYTICS_OCUPACION,
        FeatureKey.ANALYTICS_CLIENTES,
        FeatureKey.SUGERIR_PROMOS,
        FeatureKey.NOTIF_SMS,
        FeatureKey.NOTIF_EMAIL,
        FeatureKey.REPORTES_AVANZADOS,
    ]
    crud_plan_features.seed_plan_features(db, premium_plan.plan_id, premium_features)

    return result

