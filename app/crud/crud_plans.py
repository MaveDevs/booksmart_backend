from typing import List, Optional

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
