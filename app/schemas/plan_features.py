"""
Pydantic schemas for Plan Features
"""
from typing import Optional

from pydantic import BaseModel

from app.models.plan_features import FeatureKey


class PlanFeatureBase(BaseModel):
    plan_id: int
    feature_key: FeatureKey
    enabled: bool = True


class PlanFeatureCreate(PlanFeatureBase):
    pass


class PlanFeatureUpdate(BaseModel):
    plan_id: Optional[int] = None
    feature_key: Optional[FeatureKey] = None
    enabled: Optional[bool] = None


class PlanFeatureResponse(PlanFeatureBase):
    plan_feature_id: int

    class Config:
        from_attributes = True
