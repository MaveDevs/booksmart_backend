from datetime import time
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Agenda, Establishment
from app.schemas.agendas import AgendaCreate, AgendaUpdate


def get_agenda(db: Session, agenda_id: int) -> Optional[Agenda]:
    return db.query(Agenda).filter(Agenda.agenda_id == agenda_id).first()


def get_agendas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    establecimiento_id: Optional[int] = None,
) -> List[Agenda]:
    query = db.query(Agenda)
    if establecimiento_id is not None:
        query = query.filter(Agenda.establecimiento_id == establecimiento_id)
    return query.offset(skip).limit(limit).all()


def create_agenda(db: Session, agenda: AgendaCreate) -> Agenda:
    # Verify establecimiento_id exists
    establishment = (
        db.query(Establishment)
        .filter(Establishment.establecimiento_id == agenda.establecimiento_id)
        .first()
    )
    if not establishment:
        raise ValueError(f"Establishment with id {agenda.establecimiento_id} does not exist")
    
    agenda_data = agenda.model_dump()
    db_agenda = Agenda(**agenda_data)  # type: ignore[arg-type]
    db.add(db_agenda)
    db.commit()
    db.refresh(db_agenda)
    return db_agenda


def create_agendas_bulk(
    db: Session, establecimiento_id: int, dias_semana: List[str], hora_inicio: time, hora_fin: time
) -> List[Agenda]:
    """Create multiple agendas for an establishment in one transaction."""
    created_agendas = []
    for dia in dias_semana:
        db_agenda = Agenda(
            establecimiento_id=establecimiento_id,
            dia_semana=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
        )
        db.add(db_agenda)
        created_agendas.append(db_agenda)
    
    db.commit()
    for agenda in created_agendas:
        db.refresh(agenda)
    return created_agendas


def update_agenda(db: Session, agenda_id: int, agenda: AgendaUpdate) -> Optional[Agenda]:
    db_agenda = get_agenda(db, agenda_id)
    if not db_agenda:
        return None

    update_data = agenda.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_agenda, field, value)

    db.commit()
    db.refresh(db_agenda)
    return db_agenda


def delete_agenda(db: Session, agenda_id: int) -> bool:
    db_agenda = get_agenda(db, agenda_id)
    if not db_agenda:
        return False

    db.delete(db_agenda)
    db.commit()
    return True
