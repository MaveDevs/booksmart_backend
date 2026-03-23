"""
Plan Features Admin Endpoints

Allows admins to:
- View and manage features for each plan
- Seed initial features for plans
- Enable/disable features
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_plan_features
from app.models import User
from app.models.plan_features import FeatureKey
from app.schemas.plan_features import PlanFeatureCreate, PlanFeatureResponse, PlanFeatureUpdate
from app.core.permissions import require_admin

router = APIRouter()


@router.get("/", response_model=List[PlanFeatureResponse])
def list_plan_features(
    plan_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: List plan features. Optionally filter by plan_id."""
    return crud_plan_features.get_plan_features(
        db, skip=skip, limit=limit, plan_id=plan_id
    )


@router.get("/{plan_feature_id}", response_model=PlanFeatureResponse)
def get_plan_feature(
    plan_feature_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: Get a specific plan feature."""
    feature = crud_plan_features.get_plan_feature(db, plan_feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Plan feature not found")
    return feature


@router.post("/", response_model=PlanFeatureResponse)
def create_plan_feature(
    plan_feature: PlanFeatureCreate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: Create a new plan feature."""
    try:
        return crud_plan_features.create_plan_feature(db, plan_feature)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{plan_feature_id}", response_model=PlanFeatureResponse)
def update_plan_feature(
    plan_feature_id: int,
    plan_feature: PlanFeatureUpdate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: Update a plan feature."""
    db_feature = crud_plan_features.update_plan_feature(db, plan_feature_id, plan_feature)
    if not db_feature:
        raise HTTPException(status_code=404, detail="Plan feature not found")
    return db_feature


@router.patch("/{plan_feature_id}", response_model=PlanFeatureResponse)
def patch_plan_feature(
    plan_feature_id: int,
    plan_feature: PlanFeatureUpdate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: Partially update a plan feature."""
    db_feature = crud_plan_features.update_plan_feature(db, plan_feature_id, plan_feature)
    if not db_feature:
        raise HTTPException(status_code=404, detail="Plan feature not found")
    return db_feature


@router.delete("/{plan_feature_id}")
def delete_plan_feature(
    plan_feature_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Admin: Delete a plan feature."""
    success = crud_plan_features.delete_plan_feature(db, plan_feature_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan feature not found")
    return {"message": "Plan feature deleted successfully"}


@router.post("/seed/{plan_id}")
def seed_plan_features_endpoint(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """
    Admin: Seed initial features for a plan.
    Used during plan setup (e.g., FREE vs PREMIUM).
    
    Define feature sets by plan_id in seeds list below.
    """
    # Define feature sets for each plan
    free_features = [
        FeatureKey.AUTO_RESEÑA_PROMPT,
        # Otras features básicas...
    ]
    
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
        FeatureKey.REPORTES_AVANZADOS,
    ]
    
    seed_map = {
        # Mapear plan_id a su feature set
        # 1: free_features,
        # 2: premium_features,
    }
    
    if plan_id not in seed_map:
        raise HTTPException(
            status_code=400,
            detail=f"No seed definition for plan_id {plan_id}. Update seeds in endpoint.",
        )
    
    features = seed_map[plan_id]
    created = crud_plan_features.seed_plan_features(db, plan_id, features)
    
    return {
        "message": f"Seeded {len(created)} features for plan {plan_id}",
        "features_created": [f.feature_key.value for f in created],
    }
