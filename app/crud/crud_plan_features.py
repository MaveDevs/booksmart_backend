"""
CRUD operations for Plan Features
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Plan, PlanFeature
from app.models.plan_features import FeatureKey
from app.schemas.plan_features import PlanFeatureCreate, PlanFeatureUpdate


def get_plan_feature(db: Session, plan_feature_id: int) -> Optional[PlanFeature]:
    """Get a specific plan feature by ID"""
    return db.query(PlanFeature).filter(PlanFeature.plan_feature_id == plan_feature_id).first()


def get_plan_features(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    plan_id: Optional[int] = None,
) -> List[PlanFeature]:
    """Get all plan features, optionally filtered by plan_id"""
    query = db.query(PlanFeature)
    if plan_id is not None:
        query = query.filter(PlanFeature.plan_id == plan_id)
    return query.offset(skip).limit(limit).all()


def get_feature_by_plan_and_key(
    db: Session, plan_id: int, feature_key: FeatureKey
) -> Optional[PlanFeature]:
    """Get a specific feature for a plan by feature key"""
    return (
        db.query(PlanFeature)
        .filter(
            PlanFeature.plan_id == plan_id,
            PlanFeature.feature_key == feature_key,
        )
        .first()
    )


def plan_has_feature(db: Session, plan_id: int, feature_key: FeatureKey) -> bool:
    """Check if a plan has a specific feature enabled"""
    feature = get_feature_by_plan_and_key(db, plan_id, feature_key)
    return feature is not None and feature.enabled


def create_plan_feature(db: Session, plan_feature: PlanFeatureCreate) -> PlanFeature:
    """Create a new plan feature"""
    # Verify plan exists
    plan = db.query(Plan).filter(Plan.plan_id == plan_feature.plan_id).first()
    if not plan:
        raise ValueError(f"Plan with id {plan_feature.plan_id} does not exist")

    # Check if feature already exists for this plan
    existing = get_feature_by_plan_and_key(
        db, plan_feature.plan_id, plan_feature.feature_key
    )
    if existing:
        raise ValueError(
            f"Feature {plan_feature.feature_key} already exists for plan {plan_feature.plan_id}"
        )

    plan_feature_data = plan_feature.model_dump()
    db_plan_feature = PlanFeature(**plan_feature_data)  # type: ignore[arg-type]
    db.add(db_plan_feature)
    db.commit()
    db.refresh(db_plan_feature)
    return db_plan_feature


def update_plan_feature(
    db: Session,
    plan_feature_id: int,
    plan_feature: PlanFeatureUpdate,
) -> Optional[PlanFeature]:
    """Update a plan feature"""
    db_plan_feature = get_plan_feature(db, plan_feature_id)
    if not db_plan_feature:
        return None

    update_data = plan_feature.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_plan_feature, field, value)

    db.commit()
    db.refresh(db_plan_feature)
    return db_plan_feature


def delete_plan_feature(db: Session, plan_feature_id: int) -> bool:
    """Delete a plan feature"""
    db_plan_feature = get_plan_feature(db, plan_feature_id)
    if not db_plan_feature:
        return False

    db.delete(db_plan_feature)
    db.commit()
    return True


def seed_plan_features(db: Session, plan_id: int, feature_keys: List[FeatureKey]) -> List[PlanFeature]:
    """
    Seed multiple features for a plan.
    Used to initialize FREE vs PREMIUM plans.
    """
    created = []
    for feature_key in feature_keys:
        existing = get_feature_by_plan_and_key(db, plan_id, feature_key)
        if not existing:
            pf = PlanFeatureCreate(plan_id=plan_id, feature_key=feature_key, enabled=True)
            created.append(create_plan_feature(db, pf))
    return created
