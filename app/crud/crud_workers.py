from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Establishment, Worker
from app.schemas.workers import WorkerCreate, WorkerUpdate


def get_worker(db: Session, worker_id: int) -> Optional[Worker]:
	return db.query(Worker).filter(Worker.trabajador_id == worker_id).first()


def get_workers(db: Session, skip: int = 0, limit: int = 100) -> List[Worker]:
	return db.query(Worker).offset(skip).limit(limit).all()


def get_workers_by_establishment(
	db: Session, establishment_id: int, skip: int = 0, limit: int = 100
) -> List[Worker]:
	return (
		db.query(Worker)
		.filter(Worker.establecimiento_id == establishment_id)
		.offset(skip)
		.limit(limit)
		.all()
	)


def create_worker(db: Session, worker: WorkerCreate) -> Worker:
	# Verify establecimiento_id exists
	establishment = (
		db.query(Establishment)
		.filter(Establishment.establecimiento_id == worker.establecimiento_id)
		.first()
	)
	if not establishment:
		raise ValueError(f"Establishment with id {worker.establecimiento_id} does not exist")
	
	db_worker = Worker(**worker.model_dump())
	db.add(db_worker)
	db.commit()
	db.refresh(db_worker)
	return db_worker


def update_worker(db: Session, worker_id: int, worker: WorkerUpdate) -> Optional[Worker]:
	db_worker = get_worker(db, worker_id)
	if not db_worker:
		return None
	
	update_data = worker.model_dump(exclude_unset=True)
	for field, value in update_data.items():
		setattr(db_worker, field, value)
	
	db.commit()
	db.refresh(db_worker)
	return db_worker


def delete_worker(db: Session, worker_id: int) -> bool:
	db_worker = get_worker(db, worker_id)
	if not db_worker:
		return False
	
	db.delete(db_worker)
	db.commit()
	return True
