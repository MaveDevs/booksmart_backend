from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Establishment, Worker, User
from app.schemas.workers import WorkerCreate, WorkerUpdate
from app.crud.crud_users import get_user_by_email
from app.core.security import get_password_hash


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
	
	usuario_id = None
	if worker.email:
		existing_user = get_user_by_email(db, worker.email)
		if existing_user:
			raise ValueError("Un usuario con este correo ya existe en el sistema.")
		
		new_user = User(
			nombre=worker.nombre,
			apellido=worker.apellido,
			correo=worker.email,
			contrasena_hash=get_password_hash("WorkerTemp123!"),
			rol_id=4,
			activo=True,
		)
		db.add(new_user)
		db.flush()
		usuario_id = new_user.usuario_id

	db_worker = Worker(**worker.model_dump())
	if usuario_id:
		db_worker.usuario_id = usuario_id
		
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
