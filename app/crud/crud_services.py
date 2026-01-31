from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Establishment, Service
from app.schemas.services import ServiceCreate, ServiceUpdate


def get_service(db: Session, service_id: int) -> Optional[Service]:
    return db.query(Service).filter(Service.servicio_id == service_id).first()


def get_services(db: Session, skip: int = 0, limit: int = 100) -> List[Service]:
    return db.query(Service).offset(skip).limit(limit).all()


def get_services_by_establishment(
    db: Session, establishment_id: int, skip: int = 0, limit: int = 100
) -> List[Service]:
    return (
        db.query(Service)
        .filter(Service.establecimiento_id == establishment_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_service(db: Session, service: ServiceCreate) -> Service:
    # Verify establecimiento_id exists
    establishment = (
        db.query(Establishment)
        .filter(Establishment.establecimiento_id == service.establecimiento_id)
        .first()
    )
    if not establishment:
        raise ValueError(f"Establishment with id {service.establecimiento_id} does not exist")
    
    db_service = Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def update_service(db: Session, service_id: int, service: ServiceUpdate) -> Optional[Service]:
    db_service = get_service(db, service_id)
    if not db_service:
        return None
    
    update_data = service.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_service, field, value)
    
    db.commit()
    db.refresh(db_service)
    return db_service

def delete_service(db: Session, service_id: int) -> bool:
    db_service = get_service(db, service_id)
    if not db_service:
        return False
    
    db.delete(db_service)
    db.commit()
    return True