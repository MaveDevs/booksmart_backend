from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.services import Service
from app.schemas.services import ServiceCreate, ServiceUpdate

def get_service(db: Session, service_id: int) -> Optional[Service]:
    return db.query(Service).filter(Service.servicio_id == service_id).first()

def get_services(db: Session, skip: int = 0, limit: int = 100) -> List[Service]:
    return db.query(Service).offset(skip).limit(limit).all()

def get_services_by_establishment(db: Session, establishment_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
    return db.query(Service).filter(Service.establecimiento_id == establishment_id).offset(skip).limit(limit).all()

def create_service(db: Session, service: ServiceCreate) -> Service:
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