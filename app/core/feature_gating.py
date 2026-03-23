"""
Feature Gating Utilities - Centralized permission checks for plan features

This module helps determine what features are available to an establishment
based on its current subscription plan.
"""

from sqlalchemy.orm import Session

from app.models import Establishment, Subscription
from app.models.plan_features import FeatureKey
from app.crud.crud_plan_features import plan_has_feature


def get_active_subscription(db: Session, establishment_id: int) -> Subscription | None:
    """
    Get the active (non-expired) subscription for an establishment.
    Returns None if establishment has no active subscription.
    """
    from datetime import date
    
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.establecimiento_id == establishment_id,
            Subscription.estado == "ACTIVA",
        )
        .order_by(Subscription.fecha_fin.desc())
        .first()
    )

    # Verify subscription hasn't expired
    if subscription and subscription.fecha_fin and subscription.fecha_fin < date.today():
        return None

    return subscription


def establishment_has_feature(
    db: Session, establishment_id: int, feature_key: FeatureKey
) -> bool:
    """
    Check if an establishment (via its subscription plan) has a specific feature enabled.
    
    Returns:
        True if feature is enabled for the plan, False otherwise.
        Returns False if no active subscription exists.
    """
    subscription = get_active_subscription(db, establishment_id)
    if not subscription:
        return False

    return plan_has_feature(db, subscription.plan_id, feature_key)


def get_establishment_features(
    db: Session, establishment_id: int
) -> dict[str, bool]:
    """
    Get all features and their status for an establishment.
    
    Returns a dict: {feature_key: enabled_bool, ...}
    """
    subscription = get_active_subscription(db, establishment_id)
    if not subscription:
        # Establish cimiento sin suscripción: todas las features deshabilitadas
        return {feature.value: False for feature in FeatureKey}

    plan = subscription.plan
    features_dict = {}
    for feature in FeatureKey:
        has_it = plan_has_feature(db, plan.plan_id, feature)
        features_dict[feature.value] = has_it

    return features_dict


def assert_establishment_has_feature(
    db: Session, establishment_id: int, feature_key: FeatureKey
) -> None:
    """
    Assert that an establishment has a feature.
    Raises ValueError if not.
    
    Useful for guard clauses in endpoint/service logic.
    """
    if not establishment_has_feature(db, establishment_id, feature_key):
        raise ValueError(
            f"Establishment {establishment_id} does not have feature {feature_key.value}"
        )
